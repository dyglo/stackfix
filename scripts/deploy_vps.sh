#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/relay"

if [ ! -f .env.relay ]; then
  echo "Missing relay/.env.relay. Create it from relay/.env.relay.example." >&2
  exit 1
fi

export $(grep -v '^#' .env.relay | xargs)

docker compose up -d --build