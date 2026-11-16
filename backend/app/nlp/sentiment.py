"""
Sentiment and Urgency Detection Module.
Detects emotional state:
- 'satisfaction'
- 'frustration'
- 'urgent'
- 'neutre'
Calculates an urgency score (0.0 to 1.0) and indicates if human escalation or emergency is needed.
"""

import re
from typing import Dict, Any

FRUSTRATION_KEYWORDS = [
    r"\binadmissible\b", r"\bhonteux\b", r"\bscandale\b", r"\bscandaleux\b",
    r"\bfurieux\b", r"\ben col[èe]re\b", r"\bperdu mon stage\b", r"\bretard\b",
    r"\bplainte\b", r"\bmarre\b", r"\bne marche jamais\b", r"\bincapables?\b",
    r"\bnul\b", r"\bpire\b", r"\bincomp[ée]tents?\b", r"\bcatastroph(e|ique)\b",
    r"\bm[ée]content\b", r"\barnaque\b", r"\baberrant\b", r"\bintol[ée]rable\b",
    r"\bn'importe quoi\b", r"\bpersonne ne (me )?r[ée]pond\b", r"\bpersonne ne d[ée]croche\b",
    r"\bça tra[îi]ne\b"
]

URGENT_KEYWORDS = [
    r"\burgent\b", r"\burgence\b", r"\bimm[ée]diat(ement)?\b", r"\bvital\b",
    r"\bmalaise\b", r"\bblesse(r|ment)?\b", r"\bfeu\b", r"\bsecours\b",
    r"\bau secours\b", r"\baidez-moi vite\b", r"\btout de suite\b", r"\bgrave\b",
    r"\bdanger\b", r"\bsam[u|u]\b", r"\bpompiers?\b", r"\b[ée]vanoui(e)?\b",
    r"\binconscient(e)?\b"
]

SATISFACTION_KEYWORDS = [
    r"\bmerci\b", r"\bparfait\b", r"\bsuper\b", r"\bexcellent\b",
    r"\btop\b", r"\bg[ée]nial\b", r"\bformidable\b", r"\btr[èe]s bien\b",
    r"\bimpeccable\b", r"\bravis?\b", r"\bbravo\b", r"\bmerci beaucoup\b"
]

HUMAN_ESCALATION_TEMPLATE = {
    "type": "scolarite",
    "contact_name": "Sophie Dubois",
    "contact_role": "Responsable Scolarité",
    "email": "sophie.dubois@esic.fr",
    "telephone": "01.53.90.15.20",
    "disponibilite": "9h à 17h",
    "message": (
        "Je comprends votre frustration et je suis désolé pour cette situation. "
        "Cette situation nécessite une attention personnalisée.\n\n"
        "🎯 Je vous mets en relation avec Sophie Dubois (Responsable Scolarité) :\n"
        "📧 sophie.dubois@esic.fr | ☎️ 01.53.90.15.20\n"
        "Elle est généralement disponible aujourd'hui de 9h à 17h.\n"
        "Puis-je faire autre chose pour vous aider ?"
    )
}

EMERGENCY_TEMPLATE = {
    "type": "medical_urgence",
    "contact_name": "Service Médical & Sécurité Campus",
    "email": "sante-etudiants@esic.fr",
    "telephone": "01.53.90.15.15",
    "disponibilite": "24h/24",
    "message": (
        "🚨 **ALERTE URGENCE CAMPUS**\n\n"
        "Pour toute situation d'urgence vitale, malaise ou accident sur le campus :\n\n"
        "• **SAMU** : Composez immédiatement le **15** (ou **112** sur mobile)\n"
        "• **Pompiers** : Composez le **18**\n"
        "• **Service Médical & Sécurité Campus ESIC** : **01.53.90.15.15** (Bâtiment B, Bureau 012)\n"
        "• **Accueil Central** : Bâtiment A - Rez-de-chaussée (défibrillateur disponible dans le hall)\n\n"
        "Restez auprès de la personne jusqu'à l'arrivée des secours."
    )
}

class SentimentAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "sentiment": "neutre",
                "score_urgence": 0.0,
                "escalade_humaine": False,
                "escalade_contact": None
            }

        text_lower = text.lower()

        # Check urgent first
        urgent_matches = [kw for kw in URGENT_KEYWORDS if re.search(kw, text_lower)]
        if urgent_matches:
            return {
                "sentiment": "urgent",
                "score_urgence": min(0.99, 0.8 + 0.1 * len(urgent_matches)),
                "escalade_humaine": True,
                "escalade_contact": EMERGENCY_TEMPLATE,
                "raison": "Détection de situation urgente ou critique"
            }

        # Check frustration
        frustration_matches = [kw for kw in FRUSTRATION_KEYWORDS if re.search(kw, text_lower)]
        exclamation_count = text.count("!")
        if frustration_matches or exclamation_count >= 3:
            urgency_score = min(0.9, 0.6 + 0.1 * len(frustration_matches) + 0.05 * exclamation_count)
            return {
                "sentiment": "frustration",
                "score_urgence": urgency_score,
                "escalade_humaine": True,
                "escalade_contact": HUMAN_ESCALATION_TEMPLATE,
                "raison": "Détection d'insatisfaction ou réclamation critique"
            }

        # Check satisfaction
        satisfaction_matches = [kw for kw in SATISFACTION_KEYWORDS if re.search(kw, text_lower)]
        if satisfaction_matches:
            return {
                "sentiment": "satisfaction",
                "score_urgence": 0.1,
                "escalade_humaine": False,
                "escalade_contact": None,
                "raison": "Message positif de remerciement ou satisfaction"
            }

        # Neutral fallback
        return {
            "sentiment": "neutre",
            "score_urgence": 0.2,
            "escalade_humaine": False,
            "escalade_contact": None,
            "raison": "Requête informative standard"
        }

sentiment_analyzer = SentimentAnalyzer()
