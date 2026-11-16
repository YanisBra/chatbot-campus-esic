"""
Intent Classification Module.
Trains and serves a TF-IDF + LogisticRegression/SGD classifier
over the 15 campus intent classes with >85% precision.
"""

import os
import json
import re
import pickle
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

MODEL_FILE = os.path.join(os.path.dirname(__file__), "intent_model.pkl")
TRAIN_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "nlp", "intentions_training.json")

def preprocess_text(text: str) -> str:
    """Normalize text: lowercasing, whitespace cleanup, keeping punctuation marks relevant to questions."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

class IntentClassifier:
    def __init__(self):
        self.pipeline: Pipeline = None
        self.classes = []
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(MODEL_FILE):
            try:
                with open(MODEL_FILE, "rb") as f:
                    saved = pickle.load(f)
                    self.pipeline = saved["pipeline"]
                    self.classes = saved["classes"]
                return
            except Exception:
                pass
        self.train()

    def train(self, data_path: str = None) -> Dict[str, Any]:
        path = data_path or TRAIN_DATA_FILE
        if not os.path.exists(path):
            raise FileNotFoundError(f"Training file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = [preprocess_text(item["text"]) for item in data]
        labels = [item["intent"] for item in data]

        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )

        pipe = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                min_df=1,
                max_df=0.95
            )),
            ("clf", LogisticRegression(
                C=2.0,
                max_iter=1000,
                random_state=42,
                class_weight="balanced"
            ))
        ])

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        self.pipeline = pipe
        self.classes = list(pipe.classes_)

        # Save model
        with open(MODEL_FILE, "wb") as f:
            pickle.dump({"pipeline": pipe, "classes": self.classes}, f)

        return {
            "accuracy": accuracy,
            "report": report,
            "num_samples": len(texts),
            "num_classes": len(self.classes)
        }

    def predict(self, text: str) -> Tuple[str, float]:
        """Predict intent label and confidence score (0.0 to 1.0)."""
        clean = preprocess_text(text)
        if not self.pipeline:
            return ("information_generale", 0.5)

        probs = self.pipeline.predict_proba([clean])[0]
        max_idx = probs.argmax()
        intent = self.pipeline.classes_[max_idx]
        confidence = float(probs[max_idx])
        return intent, confidence

    def predict_top_k(self, text: str, k: int = 3):
        """Predict top k intents with probabilities."""
        clean = preprocess_text(text)
        if not self.pipeline:
            return []
        probs = self.pipeline.predict_proba([clean])[0]
        scored = sorted(zip(self.pipeline.classes_, probs), key=lambda x: x[1], reverse=True)
        return [{"intent": cat, "confidence": float(score)} for cat, score in scored[:k]]

# Global singleton
intent_classifier = IntentClassifier()
