"""
Multilingual Module for Campus Assistant.
Detects language (French, English, Spanish) and handles translations/localized campus answers.
Primary language is French (default). Spanish and English are detected through strict, unambiguous markers.
"""

import re
from typing import Dict, Any

# Unambiguous English markers (strictly English)
EN_MARKERS = [
    r"\bwhen\s+is\b", r"\bwhat\s+is\b", r"\bwhere\s+is\b", r"\bhow\s+to\b",
    r"\bcan\s+i\b", r"\bcan\s+you\b", r"\bhello\b", r"\bhi\s+there\b",
    r"\blibrary\b", r"\bopening\s+hours\b", r"\bschedule\b",
    r"\bwho\s+is\b", r"\bplease\b", r"\bthank\s+you\b", r"\bthanks\b",
    r"\bwhere\s+can\s+i\b", r"\bexchange\s+student\b", r"\baccommodation\b"
]

# Unambiguous Spanish markers (strictly Spanish, NO common words like 'que' or 'de')
ES_MARKERS = [
    r"\bcu[aá]ndo\b", r"\bd[oó]nde\b", r"\bc[oó]mo\b",
    r"\bhorario(s)?\b", r"\bbiblioteca\b", r"\bhola\b", r"\bgracias\b",
    r"\bestudiante(s)?\b", r"\bpor\s+favor\b", r"\bbuenos\s+d[ií]as\b",
    r"¿", r"\bbuenas\s+tardes\b", r"\bprofesores?\b"
]

# Common French markers
FR_MARKERS = [
    r"\bc'est\b", r"\bqu'est-ce\b", r"\bqu'on\b", r"\bj'ai\b", r"\bj'peux\b",
    r"\bje\b", r"\btu\b", r"\bil\b", r"\bnous\b", r"\bvous\b", r"\bils\b",
    r"\best\b", r"\bsont\b", r"\bavoir\b", r"\bfaire\b", r"\bquelle\b",
    r"\bquel\b", r"\bcomment\b", r"\bpourquoi\b", r"\boù\b", r"\bquand\b",
    r"\bdans\b", r"\bpour\b", r"\bavec\b", r"\bsur\b", r"\bmon\b", r"\bma\b",
    r"\bmes\b", r"\bton\b", r"\bta\b", r"\btes\b", r"\bson\b", r"\bsa\b",
    r"\bses\b", r"\bnotre\b", r"\bvotre\b", r"\bleur\b", r"\bpas\b",
    r"\bplus\b", r"\btrès\b", r"\bmême\b", r"\baussi\b", r"\bmerci\b",
    r"\bbonjour\b", r"\bsalut\b", r"\bça\b", r"\bce\b", r"\bcette\b",
    r"\bces\b", r"\bun\b", r"\bune\b", r"\bdes\b", r"\bdu\b", r"\bau\b",
    r"\baux\b", r"\bqui\b", r"\bque\b", r"\bquoi\b", r"\bdont\b"
]

LOCALIZED_RESPONSES = {
    "en": {
        "welcome": "Hello! I am your ESIC Virtual Campus Assistant. How can I help you today?",
        "fallback": "I'm sorry, I couldn't find a direct answer to your question. You can contact student affairs at sophie.dubois@esic.fr or phone +33 1 53 90 15 20.",
        "library_hours": "The ESIC university library is open Monday to Friday from 8:00 AM to 8:00 PM, and Saturday from 9:00 AM to 5:00 PM. Closed on Sundays.",
        "resto_u": "The campus restaurant (Building D) is open for lunch from 11:30 AM to 2:00 PM. Student meal is €3.30 (or €1.00 for scholarship students).",
        "contacts": "Student Affairs office is in Building A, Room 102. Contact: Sophie Dubois (sophie.dubois@esic.fr | +33 1 53 90 15 20).",
        "international_office": "The International Welcome Desk is in Building A, Room 308 (open Mon-Fri 9:30 AM - 4:30 PM). Contact: international@esic.fr.",
        "disambiguation": "I can help you! Could you please clarify your request:\n- Internship / Apprenticeship contract\n- Student certificate\n- Housing assistance\n- Scholarship\nor something else?"
    },
    "es": {
        "welcome": "¡Hola! Soy tu Asistente Virtual del Campus ESIC. ¿En qué puedo ayudarte hoy?",
        "fallback": "Lo siento, no encontré una respuesta directa. Puedes comunicarte con secretaría en sophie.dubois@esic.fr o al +33 1 53 90 15 20.",
        "library_hours": "La biblioteca universitaria abre de lunes a viernes de 8:00 a 20:00 y sábados de 9:00 a 17:00. Cerrada los domingos.",
        "resto_u": "El restaurante universitario (Edificio D) abre de 11:30 a 14:00. El menú para estudiantes cuesta 3,30 € (1,00 € para becarios).",
        "contacts": "La oficina de secretaría está en el Edificio A, despacho 102. Contacto: Sophie Dubois (sophie.dubois@esic.fr | +33 1 53 90 15 20).",
        "international_office": "El Welcome Desk Internacional está en el Edificio A, despacho 308 (L-V 9:30 - 16:30). Email: international@esic.fr.",
        "disambiguation": "¡Puedo ayudarte! ¿Podrías especificar qué tipo de solicitud necesitas:\n- Convenio de prácticas / alternancia\n- Certificado de estudios\n- Ayuda para alojamiento\n- Beca de estudios\n¿u otra cosa?"
    }
}

class MultilingualService:
    def detect_language(self, text: str) -> str:
        """Detect language: 'fr' (default), 'en', or 'es'."""
        if not text:
            return "fr"
        t = text.lower()

        fr_score = sum(1 for p in FR_MARKERS if re.search(p, t))
        en_score = sum(1 for p in EN_MARKERS if re.search(p, t))
        es_score = sum(1 for p in ES_MARKERS if re.search(p, t))

        # If clear French markers are present, keep French
        if fr_score >= 1 and fr_score >= en_score and fr_score >= es_score:
            return "fr"

        if en_score >= 2 or (en_score >= 1 and fr_score == 0):
            return "en"
        if es_score >= 2 or (es_score >= 1 and fr_score == 0):
            return "es"

        return "fr"

    def get_localized_response(self, lang: str, key: str) -> str:
        if lang in LOCALIZED_RESPONSES and key in LOCALIZED_RESPONSES[lang]:
            return LOCALIZED_RESPONSES[lang][key]
        return ""

multilingual_service = MultilingualService()
