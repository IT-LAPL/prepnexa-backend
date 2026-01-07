#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="dev/docker-compose.prod.yml"

# choose command: prefer `docker compose` if available, fall back to `docker-compose`
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
	COMPOSE=(docker compose -f "$COMPOSE_FILE")
elif command -v docker-compose >/dev/null 2>&1; then
	COMPOSE=(docker-compose -f "$COMPOSE_FILE")
else
	echo "ERROR: neither 'docker compose' nor 'docker-compose' is available" >&2
	exit 1
fi

echo "📥 Pulling latest code..."
git pull origin main

echo "🛑 Stopping containers..."
"${COMPOSE[@]}" down || true

echo "🔨 Building images..."
"${COMPOSE[@]}" build

echo "🚀 Starting containers..."
"${COMPOSE[@]}" up -d

echo "✅ Deployment completed successfully"
