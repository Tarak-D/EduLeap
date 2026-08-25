#!/bin/bash

echo "🚀 Starting EduLeap development environment..."

# Start infrastructure
docker-compose up -d postgres chroma

# Wait for services
sleep 3

# Setup DB
./scripts/setup_db.sh

# Start backend in background
cd backend
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
npm start

# Cleanup on exit
trap "kill $BACKEND_PID; docker-compose down" EXIT