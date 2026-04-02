#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="sum-journey-mission-control"

if ! command -v wrangler >/dev/null 2>&1; then
  echo "[ERROR] Wrangler no está instalado."
  echo "Instala con: npm install -g wrangler"
  exit 1
fi

echo "[INFO] Verificando autenticación de Cloudflare..."
if ! wrangler whoami >/dev/null 2>&1; then
  echo "[INFO] No hay sesión activa. Ejecuta: wrangler login"
  wrangler login
fi

echo "[INFO] Cuenta vinculada."
wrangler whoami

echo "[INFO] Deploying ${PROJECT_NAME}..."
wrangler deploy

echo "[OK] Deploy completado."
echo "Revisa la URL workers.dev mostrada por Wrangler arriba."
