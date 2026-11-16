#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "🚀 Démarrage de l'Assistant Virtuel ESIC Campus Connecté"
echo "=========================================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur : python3 n'est pas installé."
    exit 1
fi

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel venv..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r backend/requirements.txt
fi

# Generate datasets if missing
if [ ! -f "backend/data/knowledge/emplois_du_temps.json" ]; then
    echo "📑 Génération des jeux de données d'entraînement et de connaissances..."
    ./venv/bin/python3 generate_datasets.py
fi

# Run tests before launch
echo "🧪 Exécution des tests unitaires et de sécurité..."
PYTHONPATH=. ./venv/bin/pytest backend/tests/ -q

echo "✅ Tous les tests sont validés avec succès !"
echo "🌐 Lancement du serveur sur http://127.0.0.1:8000"
echo "Documentation interactive Swagger : http://127.0.0.1:8000/docs"
echo "=========================================================="

export PYTHONPATH=.
./venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
