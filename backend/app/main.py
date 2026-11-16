"""
Main FastAPI Application for Assistant Virtuel Educatif (Campus ESIC).
Serves:
- REST API for Chatbot, NLP, Knowledge Base, Analytics, IoT Borne Simulation, ENT SSO, GDPR
- Static web frontend files
"""

import os
import time
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .models.schemas import (
    ChatRequest, FeedbackRequest, KnowledgeItemCreate,
    KioskHeartbeatRequest, BadgeScanRequest, NotificationCreate, LoginRequest
)
from .services.chatbot_service import chatbot_service, FREQUENT_QUESTIONS_SUGGESTIONS
from .services.knowledge_service import knowledge_service
from .services.analytics_service import analytics_service
from .services.kiosk_service import kiosk_service
from .services.notification_service import notification_service
from .nlp.classifier import intent_classifier
from .nlp.ner import entity_extractor
from .nlp.sentiment import sentiment_analyzer
from .nlp.similarity import similarity_engine
from .database.db import get_connection

app = FastAPI(
    title="ESIC Campus Connected Virtual Assistant API",
    description="Assistant Virtuel Intelligent, Analytics & IoT Borne pour Campus ESIC (ESIS-2 / CPDIA-2)",
    version="1.0.0"
)

# Enable CORS for local testing and external deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

# ==============================================================================
# Authentication & Role Verification (Admin for Analytics & Knowledge Base)
# ==============================================================================

@app.post("/api/auth/login")
async def login_endpoint(req: LoginRequest):
    valid_admins = {
        "admin@esic.fr": "esic2026",
        "admin": "admin",
        "sophie.dubois@esic.fr": "esic2026"
    }
    if (req.username in valid_admins and valid_admins[req.username] == req.password) or (req.username == "admin" and req.password == "admin"):
        return {
            "status": "authenticated",
            "token": "esic_admin_token_2026",
            "user": {
                "name": "Sophie Dubois",
                "email": "sophie.dubois@esic.fr",
                "role": "Responsable Scolarité & Administrateur",
                "is_admin": True
            }
        }
    raise HTTPException(status_code=401, detail="Identifiants administrateur incorrects. Utilisez admin / admin ou admin@esic.fr / esic2026.")

# ==============================================================================
# Chatbot Endpoints (Sprint 1 & Sprint 2)
# ==============================================================================

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest, request: Request):
    # Use client IP if client_id is default
    client_ip = request.client.host if request.client else "unknown"
    client_id = req.client_id if req.client_id != "default_client" else client_ip

    result = chatbot_service.process_message(
        query=req.query,
        session_id=req.session_id,
        client_id=client_id,
        user_profile=req.user_profile,
        source=req.source,
        requested_lang=req.language
    )
    return result

@app.get("/api/chat/history/{session_id}")
async def get_history_endpoint(session_id: str):
    history = chatbot_service.get_session_history(session_id)
    return {"session_id": session_id, "messages": history}

@app.post("/api/chat/reset/{session_id}")
async def reset_session_endpoint(session_id: str):
    success = chatbot_service.reset_session(session_id)
    return {"session_id": session_id, "reset": success, "message": "Conversation réinitialisée avec succès."}

@app.get("/api/chat/suggestions")
async def get_suggestions_endpoint():
    return {"suggestions": FREQUENT_QUESTIONS_SUGGESTIONS}

@app.post("/api/feedback")
async def submit_feedback_endpoint(req: FeedbackRequest):
    row_id = analytics_service.record_feedback(
        interaction_id=req.interaction_id,
        session_id=req.session_id,
        rating=req.rating,
        comment=req.comment
    )
    return {"status": "ok", "feedback_id": row_id, "message": "Merci pour votre évaluation !"}

# ==============================================================================
# Analytics & Reports Endpoints (Sprint 2 - Epic 5)
# ==============================================================================

@app.get("/api/analytics/realtime")
async def get_realtime_analytics_endpoint():
    return analytics_service.get_realtime_metrics()

@app.get("/api/analytics/export")
async def export_analytics_endpoint():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interactions ORDER BY id DESC LIMIT 500")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"total_exported": len(rows), "interactions": rows}

# ==============================================================================
# Knowledge Base & Continuous Improvement (Sprint 1 & Sprint 2 - Epic 6)
# ==============================================================================

@app.get("/api/knowledge/summary")
async def get_knowledge_summary():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM knowledge_items ORDER BY id DESC")
    dynamic_items = [dict(r) for r in cur.fetchall()]
    conn.close()

    return {
        "schedules_count": len(knowledge_service.schedules),
        "procedures_count": len(knowledge_service.procedures),
        "contacts_count": len(knowledge_service.contacts),
        "faq_count": len(similarity_engine.questions),
        "dynamic_items_count": len(dynamic_items),
        "dynamic_items": dynamic_items
    }

@app.post("/api/knowledge/items")
async def add_knowledge_item(req: KnowledgeItemCreate):
    conn = get_connection()
    cur = conn.cursor()
    now = time.time()
    cur.execute("""
        INSERT INTO knowledge_items (category, question, answer, keywords, source, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'admin', ?, ?)
    """, (req.category, req.question, req.answer, req.keywords or "", now, now))
    item_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"status": "ok", "item_id": item_id, "message": "Fiche ajoutée à la base de connaissances avec succès."}

@app.delete("/api/knowledge/items/{item_id}")
async def delete_knowledge_item(item_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM knowledge_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"Fiche {item_id} supprimée."}

# ==============================================================================
# IoT Borne Simulation & Monitoring (Sprint 3 - Epic 7)
# ==============================================================================

@app.get("/api/kiosks")
async def get_kiosks_endpoint():
    kiosks = kiosk_service.get_all_kiosks()
    return {"kiosks": kiosks}

@app.post("/api/kiosks/heartbeat")
async def kiosk_heartbeat_endpoint(req: KioskHeartbeatRequest):
    return kiosk_service.send_heartbeat(req.kiosk_id, req.battery, req.mode)

@app.post("/api/kiosks/badge-scan")
async def kiosk_badge_scan_endpoint(req: BadgeScanRequest):
    student = kiosk_service.simulate_student_card_scan(req.card_id)
    return {"scanned": True, "student": student}

# ==============================================================================
# Proactive Notifications & ENT SSO (Sprint 3 - Epic 8)
# ==============================================================================

@app.get("/api/notifications")
async def get_notifications_endpoint():
    return {"notifications": notification_service.get_active_notifications()}

@app.post("/api/notifications")
async def create_notification_endpoint(req: NotificationCreate):
    nid = notification_service.create_notification(req.title, req.message, req.category, req.priority)
    return {"status": "ok", "notification_id": nid}

@app.get("/api/ent/profiles")
async def get_ent_mock_profiles():
    return {
        "profiles": [
            {
                "id": "emma_rousseau",
                "name": "Emma Rousseau",
                "role": "Étudiante 2e année",
                "formation": "Data Science",
                "annee": "2e année",
                "student_id": "ESIC-2024-DS-042",
                "email": "emma.rousseau@esic.fr",
                "avatar": "👩‍🎓",
                "description": "Persona Principal : 20 ans, Data Science 2"
            },
            {
                "id": "carlos_martinez",
                "name": "Carlos Martinez",
                "role": "Étudiant Erasmus",
                "formation": "Data Science",
                "annee": "Erasmus (2e année)",
                "student_id": "ESIC-2024-INT-109",
                "email": "carlos.martinez@esic.fr",
                "avatar": "👨‍🎓",
                "description": "Persona Secondaire : 23 ans, International / Erasmus"
            },
            {
                "id": "sophie_dubois",
                "name": "Sophie Dubois",
                "role": "Responsable Scolarité",
                "formation": "Personnel Administratif",
                "annee": "Staff",
                "student_id": "STAFF-ESIC-007",
                "email": "sophie.dubois@esic.fr",
                "avatar": "👩‍💼",
                "description": "Persona Tertiaire : 42 ans, Responsable Scolarité"
            },
            {
                "id": "jean_moreau",
                "name": "Jean Moreau",
                "role": "Visiteur / Prospect",
                "formation": "Visiteur Lycéen",
                "annee": "Terminale",
                "student_id": "VISITEUR-2026",
                "email": "jean.moreau@gmail.com",
                "avatar": "🧑",
                "description": "Persona Quaternaire : 18 ans, lycéen curieux"
            }
        ]
    }

# ==============================================================================
# RGPD & Data Privacy Endpoints (PDF Page 11)
# ==============================================================================

@app.delete("/api/rgpd/delete/{client_or_session_id}")
async def rgpd_delete_data(client_or_session_id: str):
    """Right to be forgotten: removes all logs matching session or client ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM interactions
        WHERE session_id = ? OR client_id = ?
    """, (client_or_session_id, client_or_session_id))
    cur.execute("""
        DELETE FROM feedback
        WHERE session_id = ?
    """, (client_or_session_id,))
    conn.commit()
    conn.close()
    chatbot_service.reset_session(client_or_session_id)
    return {"status": "ok", "message": "Toutes vos données et conversations ont été définitivement supprimées conformément au RGPD."}

@app.get("/api/rgpd/export/{session_id}")
async def rgpd_export_data(session_id: str):
    """Data portability: export all data related to the session in JSON format."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM interactions WHERE session_id = ? ORDER BY timestamp ASC", (session_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"session_id": session_id, "export_timestamp": time.time(), "interactions": rows}

# ==============================================================================
# Health Check & Static Files
# ==============================================================================

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ESIC Campus Assistant",
        "version": "1.0.0",
        "timestamp": time.time(),
        "models": {
            "intent_classifier": "ready",
            "entity_extractor": "ready",
            "similarity_engine": "ready",
            "sentiment_analyzer": "ready"
        }
    }

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "ESIC Campus Virtual Assistant API is running. Open /docs for Swagger UI."}
