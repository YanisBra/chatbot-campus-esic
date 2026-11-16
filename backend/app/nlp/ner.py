"""
Named Entity Recognition (NER) Module for Campus Assistant.
Extracts:
- FORMATION ("Data Science", "Cybersécurité", "Développement Web", "Intelligence Artificielle", "Réseaux & Cloud")
- DATE (explicit dates e.g. "15 mars", "vendredi 15 mars", and relative dates "demain", "lundi prochain", "semaine prochaine")
- SERVICE ("scolarité", "bibliothèque", "resto U", "bureau des stages", "service médical", "bde", "informatique")
- PERSONNE ("Sophie Dubois", "Joel Banka", "Claire Martin", "Alexandre Petit", "Sophie Leroy", teachers, delegates)
- LIEU ("salle 201", "bâtiment A", "amphi B", "laboratoire IA", "campus", "resto u", "bu")
"""

import re
from typing import Dict, List, Any

# Campus formations
FORMATIONS_PATTERNS = [
    (r"\bdata\s*science\b", "Data Science"),
    (r"\bcybers[ée]curit[ée]\b|\bcyber\b", "Cybersécurité"),
    (r"\bd[ée]veloppement(\s*web)?\b|\bdev\s*web\b", "Développement Web"),
    (r"\bintelligence\s*artificielle\b|\bia\b", "Intelligence Artificielle"),
    (r"\br[ée]seaux?(\s*(et|&)?\s*cloud)?\b|\bcloud\b", "Réseaux & Cloud"),
    (r"\bmachine\s*learning\b|\bml\b", "Data Science - Machine Learning"),
    (r"\bdeep\s*learning\b|\bdl\b", "Data Science - Deep Learning")
]

# Campus services
SERVICES_PATTERNS = [
    (r"\bscolarit[ée]\b|\bsecr[ée]tariat\b", "Scolarité"),
    (r"\bbiblioth[èe]que\b|\bbu\b|\blearning\s*center\b", "Bibliothèque"),
    (r"\bresto\s*u\b|\brestaurant\s*universitaire\b|\bcaf[ée]t[ée]ria\b|\bcafet\b|\bcrous\b", "Resto U / Restauration"),
    (r"\bbureau\s*des\s*stages\b|\bstages?\b|\balternance\b", "Bureau des Stages"),
    (r"\bservice\s*m[ée]dical\b|\binfirmerie\b|\bm[ée]decin\b|\bpsy(chologue)?\b", "Service Médical"),
    (r"\bsupport(\s*it)?\b|\bservice\s*informatique\b|\bhelpdesk\b", "Support Informatique"),
    (r"\bbde\b|\bvie\s*[ée]tudiante\b|\bassociation\b", "BDE & Vie Étudiante"),
    (r"\bwelcome\s*desk\b|\binternational\b|\berasmus\b", "Service International")
]

# Known people from ESIC campus
PERSONNES_PATTERNS = [
    (r"\bsophie\s*dubois\b|\bmme\s*dubois\b", "Sophie Dubois (Responsable Scolarité)"),
    (r"\bjoel\s*banka\b|\bm\.?\s*banka\b", "Joel Banka (Directeur Pédagogique)"),
    (r"\bclaire\s*martin\b|\bmme\s*martin\b", "Claire Martin (Pôle Data Science)"),
    (r"\balexandre\s*petit\b|\bm\.?\s*petit\b", "Alexandre Petit (Pôle Cyber)"),
    (r"\bsophie\s*leroy\b|\bmme\s*leroy\b", "Sophie Leroy (Relations Entreprises)"),
    (r"\bemma\s*rousseau\b", "Emma Rousseau (Déléguée Étudiante)"),
    (r"\bmarc\s*bernard\b", "Marc Bernard (Responsable BU)"),
    (r"\bh[ée]l[èe]ne\s*durand\b|\bdr\s*durand\b", "Hélène Durand (Médecin)")
]

# Campus locations
LIEUX_PATTERNS = [
    (r"\bamphi\s*[ab]\b|\bamphi\s*turing\b|\bamphith[ée]?[aâ]tre\s*[ab]?\b", lambda m: "Amphi B" if "b" in m.group(0).lower() else ("Amphi A" if "a" in m.group(0).lower() else m.group(0))),
    (r"\bsalle\s*\d{3}\b|\bsalle\s*b-\d{3}\b", lambda m: m.group(0).title()),
    (r"\bb[âa]timent\s*[a-d]\b|\bb[âa]t\s*[a-d]\b", lambda m: m.group(0).title()),
    (r"\blaboratoire\s*ia\b|\blab\s*ia\b", "Laboratoire IA"),
    (r"\blaboratoire\s*r[ée]seau\b|\blab\s*r[ée]seau\b", "Laboratoire Réseau"),
    (r"\bfablab\b", "FabLab"),
    (r"\bfoyer\b", "Foyer Étudiant"),
    (r"\bcampus\b", "Campus ESIC")
]

# Date patterns (relative & explicit)
DATES_PATTERNS = [
    (r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)\s+prochain\b", lambda m: m.group(0)),
    (r"\bsemaine\s+prochaine\b|\bla\s+semaine\s+prochaine\b", "Semaine prochaine"),
    (r"\bsemaine\s+du\s+\d{1,2}\s+(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)\b", lambda m: m.group(0)),
    (r"\b(demain|aujourd'hui|hier|ce\s+matin|cet\s+apr[èe]s-midi|ce\s+soir)\b", lambda m: m.group(0)),
    (r"\b(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche)?\s*\d{1,2}\s+(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)(\s+\d{4})?\b", lambda m: m.group(0)),
    (r"\b15\s+mars\b|\bvendredi\s+15\s+mars\b", "Vendredi 15 mars")
]

class EntityExtractor:
    """Rule-based and regex-driven campus named entity extractor."""

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities: Dict[str, List[str]] = {
            "FORMATION": [],
            "DATE": [],
            "SERVICE": [],
            "PERSONNE": [],
            "LIEU": []
        }
        if not text:
            return entities

        # 1. Formations
        for pattern, label in FORMATIONS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if label not in entities["FORMATION"]:
                    entities["FORMATION"].append(label)

        # 2. Services
        for pattern, label in SERVICES_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if label not in entities["SERVICE"]:
                    entities["SERVICE"].append(label)

        # 3. Personnes
        for pattern, label in PERSONNES_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if label not in entities["PERSONNE"]:
                    entities["PERSONNE"].append(label)

        # 4. Lieux
        for pattern, repl in LIEUX_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for m in matches:
                val = repl(m) if callable(repl) else repl
                if val not in entities["LIEU"]:
                    entities["LIEU"].append(val)

        # 5. Dates
        for pattern, repl in DATES_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for m in matches:
                val = repl(m) if callable(repl) else repl
                if val not in entities["DATE"]:
                    entities["DATE"].append(val)

        return entities

    def evaluate_sample(self, text: str) -> List[Dict[str, Any]]:
        """Return a structured list of detected entities with start/end spans if available."""
        res = []
        extracted = self.extract_entities(text)
        for cat, items in extracted.items():
            for it in items:
                res.append({"type": cat, "value": it})
        return res

entity_extractor = EntityExtractor()
