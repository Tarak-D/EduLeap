.PHONY: dev backend frontend test setup seed clean

dev:
	docker-compose up --build

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm start

setup:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd ai_engine/rag && python ingest.py

test:
	cd backend && pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true