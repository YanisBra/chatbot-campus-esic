"""
Proactive Notification & Contextual Alert Service.
Delivers timely alerts: exam periods, registration deadlines, restaurant menus, security announcements.
"""

from typing import List, Dict, Any
from ..database.db import get_connection

class NotificationService:
    def get_active_notifications(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM notifications WHERE active = 1 ORDER BY priority DESC, id DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def create_notification(self, title: str, message: str, category: str, priority: str = "info") -> int:
        import time
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifications (title, message, category, priority, active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
        """, (title, message, category, priority, time.time()))
        nid = cur.lastrowid
        conn.commit()
        conn.close()
        return nid

notification_service = NotificationService()
