FROM python:3.11-slim

WORKDIR /app

# Copy and install requirements first (caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app/ ./app/

# Copy ai_engine from root (build context must be root)
COPY ai_engine/ ./ai_engine/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]