"""
Unified Knowledge Retrieval & Document Indexing Engine.
Indexes ALL campus documents:
- procedures_admin.yml (25 administrative procedures)
- services_campus.md (8 campus services: BU, Resto U, Médical, IT, Stages, etc.)
- reglement_campus.md (articles on attendance, exams, sanctions, plagiarism)
- emplois_du_temps.json (schedules and exams)
- contacts_annuaire.csv (staff & teacher directory)
- faq_historique.txt (300 Q&A pairs)
- dynamic knowledge items from SQLite

Uses TF-IDF + n-grams vector space indexing and Cosine Similarity with
intent & entity contextual re-ranking to find and link to the exact right document.
"""

import os
import json
import csv
import yaml
import re
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..database.db import get_connection

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge")

# French stop-words for document indexing
FRENCH_STOP_WORDS = [
    "alors", "au", "aucuns", "aussi", "autre", "avant", "avec", "avoir", "bon", "car", "ce", "cela",
    "ces", "ceux", "chaque", "ci", "comme", "comment", "dans", "des", "du", "elle", "en", "encore",
    "est", "et", "eu", "fait", "faites", "fois", "font", "hors", "ici", "il", "ils", "je", "juste",
    "la", "le", "les", "leur", "ma", "maintenant", "mais", "mes", "mien", "moins", "mon", "mot",
    "même", "ni", "nommés", "notre", "nous", "ou", "où", "par", "parce", "pas", "peut", "peu",
    "plupart", "pour", "pourquoi", "quand", "que", "quel", "quelle", "quelles", "quels", "qui",
    "sa", "sans", "ses", "seulement", "si", "sien", "son", "sont", "sous", "soyez", "sujet", "sur",
    "ta", "tandis", "tellement", "tels", "tes", "ton", "tous", "tout", "trop", "très", "tu", "voient",
    "vont", "votre", "vous", "vu", "ça", "étaient", "état", "étions", "été", "être"
]

def clean_for_indexing(text: str) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r"[^\w\s\u00C0-\u017F]", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t

class DocumentChunk:
    def __init__(self, doc_id: str, title: str, content: str, source_file: str, category: str, metadata: Dict[str, Any] = None):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.source_file = source_file
        self.category = category
        self.metadata = metadata or {}
        # Combined searchable text (title is repeated to give it higher natural weight)
        self.searchable_text = clean_for_indexing(f"{title} {title} {category} {content}")

class KnowledgeEngine:
    def __init__(self):
        self.documents: List[DocumentChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.doc_matrix = None
        self.schedules: List[Dict[str, Any]] = []
        self.procedures: List[Dict[str, Any]] = []
        self.contacts: List[Dict[str, Any]] = []
        self.load_and_index_all()

    def load_and_index_all(self):
        chunks: List[DocumentChunk] = []

        # 1. Index 25 Procedures (procedures_admin.yml)
        proc_file = os.path.join(DATA_DIR, "procedures_admin.yml")
        if os.path.exists(proc_file):
            try:
                with open(proc_file, "r", encoding="utf-8") as f:
                    procs = yaml.safe_load(f) or []
                self.procedures = procs
                for p in procs:
                    etapes_text = " ".join(p.get("etapes", []))
                    docs_text = " ".join(p.get("documents_requis", []))
                    full_content = (
                        f"{p.get('description', '')} "
                        f"Étapes: {etapes_text}. "
                        f"Délai: {p.get('delai', '')}. "
                        f"Contact: {p.get('contact', '')}. "
                        f"Documents: {docs_text}."
                    )
                    chunks.append(DocumentChunk(
                        doc_id=p.get("id", f"PROC-{len(chunks)}"),
                        title=p.get("titre", ""),
                        content=full_content,
                        source_file="procedures_admin.yml",
                        category="procedure_admin",
                        metadata=p
                    ))
            except Exception as e:
                print(f"Error loading procedures: {e}")

        # 2. Index Services Sections (services_campus.md)
        srv_file = os.path.join(DATA_DIR, "services_campus.md")
        if os.path.exists(srv_file):
            try:
                with open(srv_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # Split by markdown headers "## "
                sections = re.split(r"\n##\s+", content)
                for s in sections[1:]: # skip intro
                    lines = s.strip().splitlines()
                    title = lines[0].strip() if lines else "Service Campus"
                    sec_body = "\n".join(lines[1:]).strip()
                    chunks.append(DocumentChunk(
                        doc_id=f"SRV-{len(chunks)}",
                        title=title,
                        content=sec_body,
                        source_file="services_campus.md",
                        category="service_campus",
                        metadata={"raw_markdown": s}
                    ))
            except Exception as e:
                print(f"Error loading services: {e}")

        # 3. Index Campus Regulations (reglement_campus.md)
        reg_file = os.path.join(DATA_DIR, "reglement_campus.md")
        if os.path.exists(reg_file):
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    content = f.read()
                articles = re.split(r"\n##\s+", content)
                for a in articles[1:]:
                    lines = a.strip().splitlines()
                    title = lines[0].strip() if lines else "Règlement Intérieur"
                    body = "\n".join(lines[1:]).strip()
                    chunks.append(DocumentChunk(
                        doc_id=f"REG-{len(chunks)}",
                        title=title,
                        content=body,
                        source_file="reglement_campus.md",
                        category="reglement",
                        metadata={"article": title}
                    ))
            except Exception as e:
                print(f"Error loading reglement: {e}")

        # 4. Index Historical FAQ (faq_historique.txt)
        faq_file = os.path.join(DATA_DIR, "faq_historique.txt")
        if os.path.exists(faq_file):
            try:
                with open(faq_file, "r", encoding="utf-8") as f:
                    content = f.read()
                blocks = content.split("---")
                for idx, b in enumerate(blocks):
                    lines = [l.strip() for l in b.strip().splitlines() if l.strip()]
                    q_line, a_line = None, None
                    for l in lines:
                        if l.startswith("Q:"):
                            q_line = l[2:].strip()
                        elif l.startswith("R:"):
                            a_line = l[2:].strip()
                    if q_line and a_line:
                        chunks.append(DocumentChunk(
                            doc_id=f"FAQ-{idx}",
                            title=q_line,
                            content=a_line,
                            source_file="faq_historique.txt",
                            category="faq",
                            metadata={"question": q_line, "answer": a_line}
                        ))
            except Exception as e:
                print(f"Error loading FAQ: {e}")

        # 5. Index Schedules & Courses (emplois_du_temps.json)
        sched_file = os.path.join(DATA_DIR, "emplois_du_temps.json")
        if os.path.exists(sched_file):
            try:
                with open(sched_file, "r", encoding="utf-8") as f:
                    scheds = json.load(f)
                self.schedules = scheds

                # A. Group regular courses by formation and year to index complete course schedules
                courses_by_formation: Dict[tuple, List[Dict[str, Any]]] = {}
                for s in scheds:
                    stype = s.get("type", "").lower()
                    if "examen" not in stype and "soutenance" not in stype:
                        key = (s.get("formation"), s.get("annee"))
                        if key not in courses_by_formation:
                            courses_by_formation[key] = []
                        exists = any(
                            c["matiere"] == s.get("matiere") and c["date"] == s.get("date")
                            for c in courses_by_formation[key]
                        )
                        if not exists and len(courses_by_formation[key]) < 8:
                            courses_by_formation[key].append(s)

                for (form, yr), clist in courses_by_formation.items():
                    if not form or not yr:
                        continue
                    course_lines = [
                        f"• **{c.get('matiere')}** ({c.get('type')}) : {c.get('date')} {c.get('horaire')}, {c.get('salle')} (Enseignant : {c.get('enseignant')})"
                        for c in clist
                    ]
                    full_course_text = f"Emploi du temps et prochains cours pour {form} {yr} :\n\n" + "\n".join(course_lines)
                    chunks.append(DocumentChunk(
                        doc_id=f"EDT-COURS-{form}-{yr}",
                        title=f"Emploi du temps et prochains cours - {form} {yr}",
                        content=full_course_text,
                        source_file="emplois_du_temps.json",
                        category="emploi_du_temps",
                        metadata={"type": "cours_schedule", "formation": form, "annee": yr, "courses": clist}
                    ))

                # B. Index Exams from schedules
                for s in scheds:
                    if "examen" in s.get("type", "").lower() or "soutenance" in s.get("type", "").lower():
                        c_text = f"Formation: {s.get('formation')} {s.get('annee')}. Matière: {s.get('matiere')}. Type: {s.get('type')}. Date: {s.get('date')} {s.get('horaire')}. Salle: {s.get('salle')}. Enseignant: {s.get('enseignant')}."
                        chunks.append(DocumentChunk(
                            doc_id=s.get("id", f"EDT-{len(chunks)}"),
                            title=f"Examen {s.get('matiere')} - {s.get('formation')} {s.get('annee')}",
                            content=c_text,
                            source_file="emplois_du_temps.json",
                            category="emploi_du_temps",
                            metadata=s
                        ))
            except Exception as e:
                print(f"Error loading schedules: {e}")

        # 6. Index Contacts (contacts_annuaire.csv)
        cont_file = os.path.join(DATA_DIR, "contacts_annuaire.csv")
        if os.path.exists(cont_file):
            try:
                with open(cont_file, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    all_c = list(reader)
                    self.contacts = all_c
                    for idx, c in enumerate(all_c):
                        if idx < 40:
                            full_name = f"{c.get('prenom', '')} {c.get('nom', '')}"
                            c_text = f"{full_name} est {c.get('role')} au service {c.get('service')}. Email: {c.get('email')}, Téléphone: {c.get('telephone')}, Bureau: {c.get('bureau')}."
                            chunks.append(DocumentChunk(
                                doc_id=f"CONT-{idx}",
                                title=f"Contact {full_name}",
                                content=c_text,
                                source_file="contacts_annuaire.csv",
                                category="contact",
                                metadata=c
                            ))
            except Exception as e:
                print(f"Error loading contacts: {e}")

        # 7. Index Dynamic Knowledge items from SQLite
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM knowledge_items ORDER BY id DESC")
            dyn_rows = cur.fetchall()
            conn.close()
            for r in dyn_rows:
                chunks.append(DocumentChunk(
                    doc_id=f"DYN-{r['id']}",
                    title=r["question"],
                    content=r["answer"],
                    source_file="base_dynamique_sqlite",
                    category=r["category"],
                    metadata={"keywords": r["keywords"]}
                ))
        except Exception:
            pass

        self.documents = chunks

        # Fit Combined (Word + Subword Char_wb) Vectorizer over all document chunks
        if self.documents:
            from sklearn.pipeline import FeatureUnion
            corpus = [doc.searchable_text for doc in self.documents]
            self.vectorizer = FeatureUnion([
                ('word', TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words=FRENCH_STOP_WORDS, min_df=1)),
                ('char', TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True, min_df=1))
            ])
            self.doc_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, intent: Optional[str] = None, entities: Optional[Dict[str, List[str]]] = None, top_k: int = 3) -> Dict[str, Any]:
        """Search the unified document index using query vector similarity."""
        if not self.documents or not self.vectorizer or self.doc_matrix is None:
            return {"best_match": None, "score": 0.0, "status": "empty"}

        cleaned_query = clean_for_indexing(query)
        q_vec = self.vectorizer.transform([cleaned_query])
        raw_scores = cosine_similarity(q_vec, self.doc_matrix)[0].copy()

        # If entities are explicitly extracted, give targeted boost
        if entities:
            for i, doc in enumerate(self.documents):
                for p in entities.get("PERSONNE", []):
                    if p.lower() in doc.content.lower() or p.lower() in doc.title.lower():
                        raw_scores[i] += 0.15

        best_idx = int(np.argmax(raw_scores))
        best_score = float(raw_scores[best_idx])
        best_doc = self.documents[best_idx]

        # Top candidates for suggestions
        sorted_indices = np.argsort(raw_scores)[::-1][:top_k]
        top_candidates = [
            {
                "title": self.documents[idx].title,
                "category": self.documents[idx].category,
                "source": self.documents[idx].source_file,
                "score": round(float(raw_scores[idx]), 3)
            }
            for idx in sorted_indices if idx != best_idx and raw_scores[idx] >= 0.10
        ]

        # Format user response based on document type
        formatted_response = self._format_doc_response(best_doc)

        status = "confident" if best_score >= 0.11 else "low_confidence"

        return {
            "best_match": best_doc,
            "formatted_response": formatted_response,
            "score": round(best_score, 3),
            "status": status,
            "source_document": best_doc.source_file,
            "document_title": best_doc.title,
            "top_candidates": top_candidates
        }

    def _format_doc_response(self, doc: DocumentChunk) -> str:
        """Format the document into a structured, readable markdown response."""
        meta = doc.metadata

        # Procedure response
        if doc.source_file == "procedures_admin.yml":
            etapes = meta.get("etapes", [])
            etapes_md = "\n".join([f"{i+1}. {step}" for i, step in enumerate(etapes)])
            docs_md = ", ".join(meta.get("documents_requis", [])) or "Aucun document spécifique"
            return (
                f"📋 **{doc.title}**\n\n"
                f"{meta.get('description', '')}\n\n"
                f"**Étapes de la démarche :**\n{etapes_md}\n\n"
                f"⏱️ **Délai moyen de traitement** : {meta.get('delai', 'Sous 48h')}\n"
                f"👤 **Service référent** : {meta.get('contact', 'scolarite@esic.fr')}\n"
                f"📄 **Documents requis** : {docs_md}"
            )

        # Services response (BU, Resto U, Scolarité, Helpdesk, etc.)
        if doc.source_file == "services_campus.md":
            # If scolarité
            if "scolarité" in doc.title.lower() or "scolarite" in doc.title.lower():
                return (
                    "🏢 **Service Scolarité et Accueil Pédagogique (Bâtiment A, Bureau 102)** :\n\n"
                    "• **Horaires d'ouverture** : Du Lundi au Vendredi de 08h30 à 17h30 (fermé le samedi et dimanche)\n"
                    "• **Permanence téléphonique** : 01.53.90.15.20 (09h00 - 17h00)\n"
                    "• **Responsable** : Mme Sophie Dubois (`sophie.dubois@esic.fr`)\n"
                    "• **Missions** : Inscriptions pédagogiques, certificats de scolarité, conventions de stage, relevés de notes, gestion des plannings et examens."
                )
            # If library
            if "bibliothèque" in doc.title.lower() or "bu" in doc.title.lower():
                return (
                    "Bonjour ! 📚 **Bibliothèque Universitaire & Espace Numérique (Bâtiment C)** :\n\n"
                    "- **Lundi à vendredi** : 08h00 - 20h00\n"
                    "- **Samedi** : 09h00 - 17h00\n"
                    "- **Dimanche** : Fermée\n\n"
                    "**Services** : 15 000 ouvrages en libre accès, 12 box de travail insonorisés, 50 postes informatiques équipés.\n"
                    "📧 Contact : `bibliotheque@esic.fr` | ☎️ 01.53.90.15.40\n\n"
                    "Puis-je vous aider avec autre chose ?"
                )
            # If Resto U
            if "restauration" in doc.title.lower() or "resto" in doc.title.lower():
                return (
                    "🍽️ **Restauration Universitaire (Bâtiment D)** :\n\n"
                    "- **Resto U (Déjeuner)** : 11h30 - 14h00\n"
                    "- **Cafétéria** : 07h45 - 18h00 (boissons, viennoiseries, micro-ondes en accès libre)\n"
                    "- **Tarifs** : 3,30 € le menu complet (1,00 € pour les étudiants boursiers Crous)\n"
                    "- **Paiement** : Carte étudiante Izly sans contact ou Carte Bancaire."
                )
            return f"🏢 **{doc.title}**\n\n{doc.content}"

        # Regulations response
        if doc.source_file == "reglement_campus.md":
            return (
                f"📜 **{doc.title} - Règlement Intérieur Campus ESIC**\n\n"
                f"{doc.content}"
            )

        # Timetable / Exam schedule response
        if doc.source_file == "emplois_du_temps.json":
            if meta.get("type") == "cours_schedule":
                return (
                    f"📅 **{doc.title}**\n\n"
                    f"{doc.content}\n\n"
                    "💡 *Retrouvez votre planning détaillé et les mises à jour de salle en temps réel sur l'ENT (rubrique Emploi du Temps).*"
                )
            return (
                f"📅 **{doc.title}**\n\n"
                f"• **Formation** : {meta.get('formation')} ({meta.get('annee')})\n"
                f"• **Type** : {meta.get('type')}\n"
                f"• **Date & Horaire** : {meta.get('date')}, {meta.get('horaire')}\n"
                f"• **Lieu** : {meta.get('salle')}\n"
                f"• **Enseignant** : {meta.get('enseignant')}"
            )

        # Contact directory response
        if doc.source_file == "contacts_annuaire.csv":
            return (
                f"👤 **{meta.get('prenom')} {meta.get('nom')}** - {meta.get('role')}\n"
                f"🏢 **Service** : {meta.get('service')}\n"
                f"📧 **Email** : {meta.get('email')}\n"
                f"☎️ **Téléphone** : {meta.get('telephone')}\n"
                f"📍 **Bureau** : {meta.get('bureau')}\n"
                f"🕒 **Disponibilité** : {meta.get('disponibilite')}"
            )

        # Default / FAQ
        if "bibliothèque" in doc.title.lower() or "bu" in doc.title.lower():
            return (
                "Bonjour ! 📚 La bibliothèque est ouverte :\n"
                "- Lundi à vendredi : 8h-20h\n"
                "- Samedi : 9h-17h\n"
                "- Fermée le dimanche\n\n"
                "Puis-je vous aider avec autre chose ?"
            )
        return doc.content

# Global engine singleton
knowledge_engine = KnowledgeEngine()
knowledge_service = knowledge_engine
