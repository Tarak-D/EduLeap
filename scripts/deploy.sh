#!/bin/bash

echo "🚀 Deploying EduLeap..."

# Build and push
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d

echo "✅ Deployed! Check http://localhost:3000"