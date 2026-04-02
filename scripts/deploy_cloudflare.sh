#!/usr/bin/env bash
set -euo pipefail

if ! command -v wrangler >/dev/null 2>&1; then
  echo "Instala Wrangler primero: npm install -g wrangler"
  exit 1
fi

wrangler deploy
