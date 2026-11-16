"""
API Integration & Conversation Scenarios Tests.
Validates the 4 conversation types from the PDF (Page 8):
1. Question simple (horaires bibliothèque)
2. Question complexe avec entités (Data Science 2 examens Machine Learning)
3. Question ambiguë ("Comment faire ma demande ?")
4. Escalade vers humain ("C'est inadmissible, j'ai perdu mon stage...")
Also tests feedback, analytics, kiosks, and GDPR endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_conversation_1_simple_question():
    """Conversation 1: 'Bonjour, à quelle heure ouvre la bibliothèque ?'"""
    res = client.post("/api/chat", json={
        "query": "Bonjour, à quelle heure ouvre la bibliothèque ?",
        "session_id": "test_conv_1",
        "client_id": "client_c1"
    })
    assert res.status_code == 200
    data = res.json()
    assert "bibliothèque" in data["response"].lower()
    assert "8h-20h" in data["response"]
    assert "9h-17h" in data["response"]
    assert data["escalated"] is False

def test_conversation_2_complex_question_with_entities():
    """Conversation 2: 'Je suis en Data Science 2e année, quand sont mes examens de machine learning ?'"""
    res = client.post("/api/chat", json={
        "query": "Je suis en Data Science 2e année, quand sont mes examens de machine learning ?",
        "session_id": "test_conv_2",
        "client_id": "client_c2"
    })
    assert res.status_code == 200
    data = res.json()
    resp_text = data["response"]
    assert "Vendredi 15 mars" in resp_text
    assert "Amphi B" in resp_text
    assert "Semaine du 22 mars" in resp_text

def test_conversation_3_ambiguous_question():
    """Conversation 3: 'Comment faire ma demande ?'"""
    res = client.post("/api/chat", json={
        "query": "Comment faire ma demande ?",
        "session_id": "test_conv_3",
        "client_id": "client_c3"
    })
    assert res.status_code == 200
    data = res.json()
    resp_text = data["response"]
    assert "Demande de stage/alternance" in resp_text
    assert "Certificat de scolarité" in resp_text
    assert "Aide au logement" in resp_text
    assert "Bourse d'études" in resp_text

def test_conversation_4_escalation_to_human():
    """Conversation 4: 'C'est inadmissible, j'ai perdu mon stage à cause de votre retard !'"""
    res = client.post("/api/chat", json={
        "query": "C'est inadmissible, j'ai perdu mon stage à cause de votre retard !",
        "session_id": "test_conv_4",
        "client_id": "client_c4"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["escalated"] is True
    assert data["sentiment"] == "frustration"
    assert "Sophie Dubois" in data["response"]
    assert "sophie.dubois@esic.fr" in data["response"]
    assert "01.53.90.15.20" in data["response"]

def test_feedback_and_analytics():
    # Submit feedback
    f_res = client.post("/api/feedback", json={
        "session_id": "test_conv_1",
        "rating": 1,
        "comment": "Très rapide et clair !"
    })
    assert f_res.status_code == 200

    # Get realtime metrics
    a_res = client.get("/api/analytics/realtime")
    assert a_res.status_code == 200
    m = a_res.json()
    assert "metrics" in m
    assert m["metrics"]["total_questions_all_time"] > 0
    assert "top_10_questions" in m
    assert "category_distribution" in m

def test_kiosks_endpoints():
    res = client.get("/api/kiosks")
    assert res.status_code == 200
    kiosks = res.json()["kiosks"]
    assert len(kiosks) >= 4

    # Badge scan test
    b_res = client.post("/api/kiosks/badge-scan", json={"card_id": "CARD-EMMA-01"})
    assert b_res.status_code == 200
    assert b_res.json()["student"]["nom"] == "Rousseau"

def test_rgpd_export_and_delete():
    # Export
    exp_res = client.get("/api/rgpd/export/test_conv_1")
    assert exp_res.status_code == 200

    # Delete
    del_res = client.delete("/api/rgpd/delete/test_conv_1")
    assert del_res.status_code == 200
    assert "supprimées" in del_res.json()["message"]
