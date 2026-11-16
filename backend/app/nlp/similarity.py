"""
Semantic Question Similarity & FAQ Matching Module.
Computes cosine similarity between user query and historical FAQ questions.
Applies thresholds:
- Score > 0.7: Direct confident match
- Score 0.5 - 0.7: Suggested clarification / ambiguous match
- Score < 0.5: Fallback
"""

import os
import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

FAQ_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "knowledge", "faq_historique.txt")

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\u00C0-\u017F]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

class SimilarityEngine:
    def __init__(self, faq_path: str = None):
        self.faq_path = faq_path or FAQ_FILE
        self.questions: List[str] = []
        self.answers: List[str] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.faq_matrix = None
        self.load_faq()

    def load_faq(self):
        if not os.path.exists(self.faq_path):
            return

        with open(self.faq_path, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = content.split("---")
        q_list, a_list = [], []
        for block in blocks:
            lines = [line.strip() for line in block.strip().splitlines() if line.strip()]
            q_line, a_line = None, None
            for l in lines:
                if l.startswith("Q:"):
                    q_line = l[2:].strip()
                elif l.startswith("R:"):
                    a_line = l[2:].strip()
            if q_line and a_line:
                q_list.append(q_line)
                a_list.append(a_line)

        self.questions = q_list
        self.answers = a_list

        if self.questions:
            corpus = [clean_text(q) for q in self.questions]
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
            self.faq_matrix = self.vectorizer.fit_transform(corpus)

    def find_best_match(self, query: str) -> Dict[str, Any]:
        """Find the best matching question and return answer, similarity score and confidence status."""
        if not self.questions or not self.vectorizer or self.faq_matrix is None:
            return {
                "matched_question": None,
                "answer": None,
                "score": 0.0,
                "status": "fallback"
            }

        cleaned = clean_text(query)
        query_vec = self.vectorizer.transform([cleaned])
        scores = cosine_similarity(query_vec, self.faq_matrix)[0]

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score >= 0.65:
            status = "direct_match"
        elif best_score >= 0.40:
            status = "ambiguous"
        else:
            status = "fallback"

        # Also find top 3 suggestions
        top_indices = np.argsort(scores)[::-1][:3]
        suggestions = [
            {"question": self.questions[i], "score": float(scores[i])}
            for i in top_indices if scores[i] >= 0.30 and i != best_idx
        ]

        return {
            "matched_question": self.questions[best_idx],
            "answer": self.answers[best_idx],
            "score": round(best_score, 3),
            "status": status,
            "suggestions": suggestions
        }

similarity_engine = SimilarityEngine()
