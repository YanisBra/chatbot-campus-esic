"""
SQLite Database Layer for Persistence.
Stores:
- Chat interactions with timestamps & metrics
- Thumbs up/down feedback
- Custom and enriched knowledge items
- IoT Kiosk heartbeats and telemetry
- Proactive campus notifications
"""

import os
import sqlite3
import json
import time
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "campus_chatbot.sqlite3")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Interactions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        client_id TEXT NOT NULL,
        question_raw TEXT,
        question_anonymized TEXT NOT NULL,
        response_text TEXT NOT NULL,
        intent TEXT NOT NULL,
        intent_confidence REAL NOT NULL,
        entities_json TEXT,
        sentiment TEXT NOT NULL,
        urgency_score REAL NOT NULL,
        escalated INTEGER NOT NULL DEFAULT 0,
        latency_ms INTEGER NOT NULL DEFAULT 0,
        source TEXT NOT NULL DEFAULT 'web',
        language TEXT NOT NULL DEFAULT 'fr',
        user_profile TEXT,
        timestamp REAL NOT NULL
    );
    """)

    # Feedback table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interaction_id INTEGER,
        session_id TEXT,
        rating INTEGER NOT NULL, -- 1 for thumbs up, -1 for thumbs down
        comment TEXT,
        timestamp REAL NOT NULL,
        FOREIGN KEY (interaction_id) REFERENCES interactions (id)
    );
    """)

    # Dynamic Knowledge Base table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS knowledge_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        keywords TEXT,
        source TEXT NOT NULL DEFAULT 'admin',
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL
    );
    """)

    # Kiosk devices
    cur.execute("""
    CREATE TABLE IF NOT EXISTS kiosk_devices (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'online',
        last_heartbeat REAL NOT NULL,
        interactions_count INTEGER NOT NULL DEFAULT 0,
        battery_level INTEGER NOT NULL DEFAULT 100,
        active_mode TEXT NOT NULL DEFAULT 'visiteur'
    );
    """)

    # Proactive notifications
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'info',
        active INTEGER NOT NULL DEFAULT 1,
        created_at REAL NOT NULL
    );
    """)

    conn.commit()

    # Seed initial kiosks if table empty
    cur.execute("SELECT COUNT(*) FROM kiosk_devices")
    if cur.fetchone()[0] == 0:
        now = time.time()
        initial_kiosks = [
            ("BORNE-01", "Borne Accueil Principal", "Bâtiment A - Hall Central", "online", now, 142, 100, "visiteur"),
            ("BORNE-02", "Borne Bibliothèque", "Bâtiment C - Entrée BU", "online", now - 20, 98, 95, "etudiant"),
            ("BORNE-03", "Borne Restauration", "Bâtiment D - Hall Resto U", "online", now - 45, 115, 100, "visiteur"),
            ("BORNE-04", "Borne Laboratoires & IA", "Bâtiment B - Pôle Tech", "online", now - 10, 67, 98, "vocal")
        ]
        cur.executemany("""
        INSERT INTO kiosk_devices (id, name, location, status, last_heartbeat, interactions_count, battery_level, active_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, initial_kiosks)
        conn.commit()

    # Seed initial proactive notifications
    cur.execute("SELECT COUNT(*) FROM notifications")
    if cur.fetchone()[0] == 0:
        now = time.time()
        initial_notifs = [
            ("Période des examens S2", "Les examens écrits débutent le 15 mars en Amphi B. Consultez vos convocations sur l'ENT.", "examens", "warning", 1, now),
            ("Date limite conventions de stage", "Dernier délai pour déposer votre convention de stage auprès de Sophie Dubois : 15 mai.", "stages", "urgent", 1, now),
            ("Menu de la semaine au Resto U", "Menu à thème italien ce jeudi au bâtiment D (Repas étudiant 3,30€).", "services", "info", 1, now),
            ("Rentrée académique & Inscriptions", "Les formulaires de choix d'options sont disponibles sur l'ENT jusqu'au vendredi 18h.", "scolarite", "info", 1, now)
        ]
        cur.executemany("""
        INSERT INTO notifications (title, message, category, priority, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, initial_notifs)
        conn.commit()

    conn.close()

# Initialize immediately
init_db()
