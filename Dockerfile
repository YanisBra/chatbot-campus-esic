FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend code, data, and frontend
COPY backend /app/backend
COPY frontend /app/frontend
COPY generate_datasets.py /app/generate_datasets.py
COPY pytest.ini /app/pytest.ini

# Ensure datasets are generated and NLP models trained
RUN python generate_datasets.py && \
    python -c "from backend.app.nlp.classifier import intent_classifier; intent_classifier.train()"

EXPOSE 8000

ENV PORT=8000
ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
