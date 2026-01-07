#!/usr/bin/env bash
set -euo pipefail

ENV_MODE="dev"
# Optional first arg selects environment: 'dev' (default) or 'prod'
if [[ "${1:-}" == "prod" || "${1:-}" == "dev" ]]; then
  ENV_MODE="$1"
  shift || true
fi

if [[ "$ENV_MODE" == "prod" ]]; then
  COMPOSE_FILE="dev/docker-compose.prod.yml"
else
  COMPOSE_FILE="dev/docker-compose.yml"
fi

# choose command: prefer `docker compose` if available, fall back to `docker-compose`
if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD=(docker compose -f "$COMPOSE_FILE")
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD=(docker-compose -f "$COMPOSE_FILE")
else
  echo "ERROR: neither 'docker compose' nor 'docker-compose' is available" >&2
  exit 1
fi

usage() {
  cat <<-USAGE
Usage: $0 [dev|prod] <command>

Environment (optional):
  dev           Use development compose (default)
  prod          Use production compose (dev/docker-compose.prod.yml)

Commands:
  up            Build and run (foreground)
  upd           Build and run detached (background)
  logs          Follow logs for all services
  down          Stop and remove containers
  rebuild-worker  Rebuild and run only the worker service in background
  worker-shell  Run an interactive shell in the worker container
  help          Show this help

Examples:
  $0 up
  $0 prod up
  $0 prod upd
USAGE
}

case ${1:-help} in
  up)
    "${COMPOSE_CMD[@]}" up --build
    ;;

  upd)
    "${COMPOSE_CMD[@]}" up -d --build
    ;;

  logs)
    "${COMPOSE_CMD[@]}" logs -f
    ;;

  down)
    "${COMPOSE_CMD[@]}" down
    ;;

  rebuild-worker)
    "${COMPOSE_CMD[@]}" up -d --build worker
    ;;

  worker-shell)
    # runs a temporary container with an interactive shell
    # if worker isn't running this will create a one-off container
    "${COMPOSE_CMD[@]}" run --rm worker bash
    ;;

  help|--help|-h)
    usage
    ;;

  *)
    echo "Unknown command: ${1:-}" >&2
    usage
    exit 2
    ;;

esac
