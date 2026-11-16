"""
IoT Interactive Kiosk Service.
Manages:
- Kiosk devices telemetry, heartbeat & status
- Kiosk interactions logging (source='borne_iot')
- Kiosk modes: Visiteur, Étudiant, Vocal, Accessibilité, Démo
- Virtual badge / student card authentication
"""

import time
from typing import List, Dict, Any, Optional
from ..database.db import get_connection

class KioskService:
    def get_all_kiosks(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM kiosk_devices ORDER BY id ASC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        now = time.time()
        for k in rows:
            # Check if alive (heartbeat in last 60 seconds)
            if now - k["last_heartbeat"] > 90:
                k["status"] = "warning"
            elif now - k["last_heartbeat"] > 180:
                k["status"] = "offline"
            else:
                k["status"] = "online"
        return rows

    def send_heartbeat(self, kiosk_id: str, battery: int = 100, mode: str = "visiteur") -> Dict[str, Any]:
        conn = get_connection()
        cur = conn.cursor()
        now = time.time()
        cur.execute("""
            UPDATE kiosk_devices
            SET last_heartbeat = ?, battery_level = ?, active_mode = ?, status = 'online'
            WHERE id = ?
        """, (now, battery, mode, kiosk_id))
        conn.commit()
        conn.close()
        return {"status": "ok", "kiosk_id": kiosk_id, "timestamp": now}

    def record_kiosk_interaction(self, kiosk_id: str) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE kiosk_devices
            SET interactions_count = interactions_count + 1, last_heartbeat = ?
            WHERE id = ?
        """, (time.time(), kiosk_id))
        conn.commit()
        conn.close()

    def simulate_student_card_scan(self, student_card_id: str) -> Optional[Dict[str, Any]]:
        """Simulate scanning a physical NFC/RFID student badge on kiosk."""
        simulated_students = {
            "CARD-EMMA-01": {
                "nom": "Rousseau",
                "prenom": "Emma",
                "formation": "Data Science",
                "annee": "2e année",
                "etudiant_id": "ESIC-2024-DS-042",
                "photo": "/assets/emma.png",
                "email": "emma.rousseau@esic.fr"
            },
            "CARD-CARLOS-02": {
                "nom": "Martinez",
                "prenom": "Carlos",
                "formation": "Data Science",
                "annee": "Erasmus (2e année)",
                "etudiant_id": "ESIC-2024-INT-109",
                "photo": "/assets/carlos.png",
                "email": "carlos.martinez@esic.fr",
                "langue": "en"
            },
            "CARD-JEAN-03": {
                "nom": "Moreau",
                "prenom": "Jean",
                "formation": "Visiteur / Prospect Lycéen",
                "annee": "Terminale STI2D",
                "etudiant_id": "VISITEUR-2026",
                "photo": "/assets/jean.png",
                "email": "jean.moreau@gmail.com"
            }
        }
        return simulated_students.get(student_card_id, {
            "nom": "Étudiant",
            "prenom": "Campus",
            "formation": "Data Science",
            "annee": "2e année",
            "etudiant_id": student_card_id,
            "email": "etudiant@esic.fr"
        })

kiosk_service = KioskService()
