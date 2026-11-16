"""
NLP Unit and Performance Tests.
Verifies:
- Intent classifier accuracy > 85%
- Entity extractor detection on all target categories
- Sentiment analyzer and escalation logic
- Semantic similarity engine
"""

import pytest
from backend.app.nlp.classifier import intent_classifier
from backend.app.nlp.ner import entity_extractor
from backend.app.nlp.sentiment import sentiment_analyzer
from backend.app.nlp.similarity import similarity_engine

def test_intent_classifier_accuracy():
    """Verify that intent classifier achieves >85% accuracy on test set."""
    res = intent_classifier.train()
    assert res["accuracy"] >= 0.85, f"Expected accuracy >= 0.85, got {res['accuracy']}"
    assert res["num_classes"] == 15, f"Expected 15 classes, got {res['num_classes']}"

def test_intent_predictions_key_categories():
    intent1, conf1 = intent_classifier.predict("À quelle heure ouvre la bibliothèque ?")
    assert intent1 in ["service_campus", "emploi_du_temps"]

    intent2, conf2 = intent_classifier.predict("Comment obtenir une convention de stage ?")
    assert intent2 == "procedure_admin"

    intent3, conf3 = intent_classifier.predict("Quel est l'email de Sophie Dubois ?")
    assert intent3 == "contact"

    intent4, conf4 = intent_classifier.predict("Combien d'absences injustifiées sont tolérées ?")
    assert intent4 == "reglement"

def test_entity_extraction_page_8_sample():
    """Conversation 2 from PDF: 'Je suis en Data Science 2e année, quand sont mes examens de machine learning ?'"""
    text = "Je suis en Data Science 2e année, quand sont mes examens de machine learning ?"
    entities = entity_extractor.extract_entities(text)
    assert any("Data Science" in f for f in entities["FORMATION"])

    # Test date and places
    text2 = "Examen écrit vendredi 15 mars en Amphi B à 14h"
    entities2 = entity_extractor.extract_entities(text2)
    assert any("15 mars" in d for d in entities2["DATE"])
    assert any("Amphi B" in l for l in entities2["LIEU"])

def test_sentiment_escalation():
    """Conversation 4 from PDF: 'C'est inadmissible, j'ai perdu mon stage à cause de votre retard !'"""
    text = "C'est inadmissible, j'ai perdu mon stage à cause de votre retard !"
    res = sentiment_analyzer.analyze(text)
    assert res["sentiment"] == "frustration"
    assert res["escalade_humaine"] is True
    assert res["escalade_contact"] is not None
    assert "Sophie Dubois" in res["escalade_contact"]["contact_name"]

def test_sentiment_urgency():
    text = "Urgence médicale, quelqu'un a fait un malaise grave !"
    res = sentiment_analyzer.analyze(text)
    assert res["sentiment"] == "urgent"
    assert res["score_urgence"] >= 0.7
    assert res["escalade_humaine"] is True

def test_sentiment_satisfaction():
    text = "Merci beaucoup, c'est parfait !"
    res = sentiment_analyzer.analyze(text)
    assert res["sentiment"] == "satisfaction"
    assert res["escalade_humaine"] is False

def test_semantic_similarity_thresholds():
    # Direct match > 0.70
    res = similarity_engine.find_best_match("À quelle heure ouvre la bibliothèque ?")
    assert res["score"] >= 0.70
    assert res["status"] == "direct_match"

    # Out of domain query -> low score
    res_low = similarity_engine.find_best_match("Quelle est la vitesse de la lumière dans le vide ?")
    assert res_low["score"] < 0.50
    assert res_low["status"] == "fallback"
