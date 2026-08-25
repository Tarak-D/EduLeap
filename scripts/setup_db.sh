#!/bin/bash
set -e

echo "🗄️  Setting up EduLeap database..."

# Wait for postgres
until pg_isready -h localhost -p 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Run migrations (using SQLAlchemy create_all for MVP)
cd backend
python -c "from app.core.database import engine, Base; Base.metadata.create_all(bind=engine)"
echo "✅ Database tables created!"

# Seed knowledge base
cd ../ai_engine/rag
python ingest.py
echo "✅ Knowledge base seeded!"