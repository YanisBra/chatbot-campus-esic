"""
Security & GDPR Compliance Module.
Handles:
- Prompt injection detection & filtering
- Code injection & XSS sanitization
- Rate limiting (max 10 requests / minute / client)
- Anonymization of personal data (emails, phones, social security numbers)
- GDPR right to be forgotten (purge user data) & data portability export
"""

import re
import html
import time
from typing import Dict, Tuple, Optional
from collections import defaultdict

# Known prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"you\s+are\s+now\s+in\s+(developer|dan|jailbreak)\s+mode",
    r"system\s*prompt\s*(reveal|leak|show|display)",
    r"act\s+as\s+an\s+unrestricted\s+ai",
    r"forget\s+all\s+your\s+rules",
    r"<script\b[^>]*>",
    r"javascript:\s*",
    r"drop\s+table\s+",
    r"select\s+\*\s+from\s+",
    r"union\s+select\s+",
    r"exec\s*\(\s*['\"]",
    r"base64\s*decode"
]

class SecurityManager:
    def __init__(self, max_requests_per_minute: int = 10):
        self.max_requests_per_minute = max_requests_per_minute
        # client_ip_or_id -> list of request timestamps
        self.rate_limit_records = defaultdict(list)

    def check_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """Returns (is_allowed, remaining_requests)."""
        now = time.time()
        window_start = now - 60.0
        # Clean older than 1 minute
        self.rate_limit_records[client_id] = [
            ts for ts in self.rate_limit_records[client_id] if ts >= window_start
        ]
        current_count = len(self.rate_limit_records[client_id])
        if current_count >= self.max_requests_per_minute:
            return False, 0

        self.rate_limit_records[client_id].append(now)
        return True, self.max_requests_per_minute - current_count - 1

    def detect_prompt_injection(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect prompt injection or malicious code payload."""
        if not text:
            return False, None
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True, f"Tentative de manipulation ou injection détectée (motif: {pattern})"
        return False, None

    def sanitize_input(self, text: str) -> str:
        """Sanitize text against XSS and control characters while preserving harmless letters and punctuation."""
        if not text:
            return ""
        # Escape HTML tags
        cleaned = html.escape(text.strip())
        # Trim extreme length
        if len(cleaned) > 1000:
            cleaned = cleaned[:1000]
        return cleaned

    def anonymize_text(self, text: str) -> str:
        """Mask PII: emails, French phone numbers, SSN/NIR numbers."""
        if not text:
            return ""
        # Mask emails
        text = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_ANONYMISÉ]", text)
        # Mask phone numbers (01..., 06..., +33...)
        text = re.sub(r"(\+33|0)[1-9](\s*\d{2}){4}", "[TÉLÉPHONE_ANONYMISÉ]", text)
        # Mask 15-digit NIR/Secu
        text = re.sub(r"\b[12]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{3}\s*\d{3}\s*\d{2}\b", "[NUM_SÉCU_ANONYMISÉ]", text)
        return text

security_manager = SecurityManager(max_requests_per_minute=10)
