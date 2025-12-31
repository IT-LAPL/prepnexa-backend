#!/bin/bash
set -e

echo "📥 Pulling latest code..."
git pull origin main

echo "🛑 Stopping containers..."
docker-compose down

echo "🔨 Building images..."
docker-compose build

echo "🚀 Starting containers..."
docker-compose up -d

echo "✅ Deployment completed successfully"
