"""
Knowledge Service.
Loads and indexes:
- emplois_du_temps.json (200 slots)
- procedures_admin.yml (25 procedures)
- services_campus.md (campus services guide)
- contacts_annuaire.csv (150 contacts)
- reglement_campus.md (campus regulations)
- dynamic knowledge items from SQLite
"""

import os
import json
import csv
import yaml
import re
from typing import List, Dict, Any, Optional
from ..database.db import get_connection

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge")

# Stop-words to ignore in procedure search
COMMON_STOPWORDS = {
    "dans", "pour", "avec", "cette", "votre", "suis", "faire", "comment", "avoir",
    "peux", "rentrer", "salles", "études", "projet", "cours", "demande", "obtenir",
    "temps", "an", "mois", "jour", "cours", "mon", "ma", "mes", "les", "des", "une"
}

# Domain keyword mapping for procedures
PROCEDURE_INTENT_MAP = [
    (r"\b(badge|carte [ée]tudiante|paum[ée]|perdu(e)? mon badge|renouvellement carte)\b", "PROC-11"), # Carte étudiante
    (r"\b(pause|c[ée]sure|suspendre|ann[ée]e sabbatique)\b", "PROC-08"), # Césure
    (r"\b(tiers-temps|handicap|temps suppl[ée]mentaire|am[ée]nagement)\b", "PROC-06"), # Tiers-temps
    (r"\b(absence|certif(icat)? m[ée]dical|malade|pas l[àa]|justifi(er|catif))\b", "PROC-15"), # Absence
    (r"\b(convention( de)? stage|trouver un stage)\b", "PROC-01"), # Stage
    (r"\b(alternance|apprentissage|contrat pro)\b", "PROC-02"), # Alternance
    (r"\b(certificat de scolarit[ée]|attestation d'inscription)\b", "PROC-03"), # Certificat
    (r"\b(bourse|crous|aide financi[èe]re|fonds d'urgence)\b", "PROC-07"), # Bourse
    (r"\b(logement|chambre|r[ée]sidence|visale)\b", "PROC-12"), # Logement
    (r"\b(wifi|eduroam|vpn|connexion r[ée]seau)\b", "PROC-23"), # WiFi
    (r"\b(pc portable|pr[êe]t d'ordinateur|mat[ée]riel informatique)\b", "PROC-17"), # Prêt PC
    (r"\b(fablab|imprimante 3d|d[ée]coupe laser)\b", "PROC-18"), # FabLab
    (r"\b(box|r[ée]server (une )?salle (de travail|bu))\b", "PROC-19"), # Box BU
    (r"\b(rattrapage|contestation|contester une note)\b", "PROC-09"), # Contestation note
    (r"\b(harc[èe]lement|discrimination|cellule d'[ée]coute)\b", "PROC-22") # Signalement
]

class KnowledgeService:
    def __init__(self):
        self.schedules: List[Dict[str, Any]] = []
        self.procedures: List[Dict[str, Any]] = []
        self.services_text: str = ""
        self.contacts: List[Dict[str, Any]] = []
        self.reglement_text: str = ""
        self.load_all()

    def load_all(self):
        # Schedules
        sched_file = os.path.join(DATA_DIR, "emplois_du_temps.json")
        if os.path.exists(sched_file):
            with open(sched_file, "r", encoding="utf-8") as f:
                self.schedules = json.load(f)

        # Procedures
        proc_file = os.path.join(DATA_DIR, "procedures_admin.yml")
        if os.path.exists(proc_file):
            with open(proc_file, "r", encoding="utf-8") as f:
                self.procedures = yaml.safe_load(f) or []

        # Services
        srv_file = os.path.join(DATA_DIR, "services_campus.md")
        if os.path.exists(srv_file):
            with open(srv_file, "r", encoding="utf-8") as f:
                self.services_text = f.read()

        # Contacts
        cont_file = os.path.join(DATA_DIR, "contacts_annuaire.csv")
        if os.path.exists(cont_file):
            with open(cont_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.contacts = list(reader)

        # Rules
        reg_file = os.path.join(DATA_DIR, "reglement_campus.md")
        if os.path.exists(reg_file):
            with open(reg_file, "r", encoding="utf-8") as f:
                self.reglement_text = f.read()

    def search_schedule(self, formation: Optional[str] = None, annee: Optional[str] = None,
                        matiere: Optional[str] = None, is_exam: bool = False) -> List[Dict[str, Any]]:
        results = []
        for s in self.schedules:
            match = True
            if formation and formation.lower() not in s.get("formation", "").lower():
                if "data" in formation.lower() and "data" in s.get("formation", "").lower():
                    pass
                elif "cyber" in formation.lower() and "cyber" in s.get("formation", "").lower():
                    pass
                elif "dev" in formation.lower() and "dév" in s.get("formation", "").lower():
                    pass
                elif "ia" in formation.lower() and "intelligence" in s.get("formation", "").lower():
                    pass
                else:
                    match = False

            if annee and match:
                if "2" in annee and "2" not in s.get("annee", ""):
                    match = False
                elif "1" in annee and "1" not in s.get("annee", ""):
                    match = False

            if matiere and match:
                mat_lower = matiere.lower()
                if mat_lower not in s.get("matiere", "").lower():
                    match = False

            if is_exam and match:
                if "examen" not in s.get("type", "").lower() and "soutenance" not in s.get("type", "").lower():
                    match = False

            if match:
                results.append(s)
        return results

    def search_procedure(self, query: str) -> Optional[Dict[str, Any]]:
        q_lower = query.lower()

        # 1. High precision intent map
        for pattern, proc_id in PROCEDURE_INTENT_MAP:
            if re.search(pattern, q_lower):
                for p in self.procedures:
                    if p.get("id") == proc_id:
                        return p

        # 2. Weighted scoring search over title and description (ignoring common stopwords)
        q_tokens = [w for w in re.findall(r"\b[a-zA-Z\u00C0-\u017F]{4,}\b", q_lower) if w not in COMMON_STOPWORDS]
        best_proc = None
        best_score = 0

        for p in self.procedures:
            titre = p.get("titre", "").lower()
            desc = p.get("description", "").lower()
            cat = p.get("categorie", "").lower()

            score = 0
            for t in q_tokens:
                if t in titre:
                    score += 5
                elif t in desc or t in cat:
                    score += 2

            if score > best_score:
                best_score = score
                best_proc = p

        if best_proc and best_score >= 4:
            return best_proc

        return None

    def search_contact(self, name_or_service: str) -> List[Dict[str, Any]]:
        q_lower = name_or_service.lower()
        matches = []
        for c in self.contacts:
            full_name = f"{c.get('prenom', '')} {c.get('nom', '')}".lower()
            srv = c.get("service", "").lower()
            role = c.get("role", "").lower()
            if q_lower in full_name or full_name in q_lower or q_lower in srv or q_lower in role:
                matches.append(c)
        return matches

    def search_dynamic_knowledge(self, query: str) -> Optional[Dict[str, Any]]:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM knowledge_items ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        q_lower = query.lower()
        for r in rows:
            if r["question"].lower() in q_lower or q_lower in r["question"].lower():
                return dict(r)
            keywords = (r["keywords"] or "").lower().split(",")
            if any(k.strip() in q_lower for k in keywords if len(k.strip()) > 2):
                return dict(r)
        return None

knowledge_service = KnowledgeService()
