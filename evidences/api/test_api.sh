#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# test_api.sh — TechHive 3.0
# Prueba los endpoints principales usando curl.
# Requiere servidor corriendo: cd backend && python manage.py runserver
#
# Uso:
#   bash evidences/api/test_api.sh
#   bash evidences/api/test_api.sh --tenant papeleria  # cambiar tenant
#
# Prerequisito:
#   - Servidor Django corriendo en localhost:8000
#   - /etc/hosts (o C:\Windows\System32\drivers\etc\hosts) con:
#       127.0.0.1 magic.techhive.local
#       127.0.0.1 papeleria.techhive.local
#   - Usuario staff existente (ajustar USER y PASS abajo)
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Configuración ─────────────────────────────────────────────────────────────
TENANT="${1:-magic}"
HOST="${TENANT}.techhive.local"
BASE="http://${HOST}:8000"
USER="admin"
PASS="admin123"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() { echo -e "${GREEN}  [PASS]${NC} $1"; }
fail() { echo -e "${RED}  [FAIL]${NC} $1"; }
section() { echo -e "\n${BLUE}══════════════════════════════════════${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}══════════════════════════════════════${NC}"; }

# ── 1. Autenticación ──────────────────────────────────────────────────────────
section "1. Autenticación (POST /api/token/)"

AUTH_RESPONSE=$(curl -s -X POST "${BASE}/api/token/" \
  -H "Host: ${HOST}" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USER}\", \"password\": \"${PASS}\"}")

TOKEN=$(echo "${AUTH_RESPONSE}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access',''))" 2>/dev/null || echo "")

if [ -n "$TOKEN" ]; then
  pass "Token obtenido (${#TOKEN} chars)"
else
  fail "No se pudo obtener token. Respuesta: ${AUTH_RESPONSE}"
  echo "Verifica que el servidor esté corriendo y las credenciales sean correctas."
  exit 1
fi

AUTH_HEADER="Authorization: Bearer ${TOKEN}"

# ── 2. Inventario ─────────────────────────────────────────────────────────────
section "2. Inventario (GET /api/inventory/products/)"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/inventory/products/" \
  -H "Host: ${HOST}" -H "${AUTH_HEADER}")

[ "$STATUS" = "200" ] && pass "Listado de productos OK (HTTP $STATUS)" \
                       || fail "Error HTTP $STATUS"

# ── 3. Ventas ─────────────────────────────────────────────────────────────────
section "3. Ventas (GET /api/sales/ventas/)"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/sales/ventas/" \
  -H "Host: ${HOST}" -H "${AUTH_HEADER}")

[ "$STATUS" = "200" ] && pass "Listado de ventas OK (HTTP $STATUS)" \
                       || fail "Error HTTP $STATUS"

# ── 4. Predicción ML ──────────────────────────────────────────────────────────
section "4. Predicción ML (GET /api/prediccion/?dias=3)"

PRED_RESPONSE=$(curl -s "${BASE}/api/prediccion/?dias=3" \
  -H "Host: ${HOST}" -H "${AUTH_HEADER}")

PRED_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/prediccion/?dias=3" \
  -H "Host: ${HOST}" -H "${AUTH_HEADER}")

if [ "$PRED_STATUS" = "200" ]; then
  pass "Predicción OK (HTTP 200)"
  echo "    Respuesta: $(echo ${PRED_RESPONSE} | python3 -c "import sys,json; d=json.load(sys.stdin); preds=d.get('predicciones',[]); print(f'tenant={d.get(\"tenant\")}, {len(preds)} días')" 2>/dev/null)"
elif [ "$PRED_STATUS" = "400" ]; then
  echo -e "  [WARN] HTTP 400 — probablemente historial insuficiente (normal en tenant nuevo)"
  echo "    Respuesta: ${PRED_RESPONSE}"
else
  fail "Error HTTP $PRED_STATUS: ${PRED_RESPONSE}"
fi

# ── 5. Chatbot staff ──────────────────────────────────────────────────────────
section "5. Chatbot staff (POST /api/chatbot/mensaje/)"

CHAT_RESPONSE=$(curl -s -X POST "${BASE}/api/chatbot/mensaje/" \
  -H "Host: ${HOST}" \
  -H "${AUTH_HEADER}" \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "cuanto vendimos hoy", "session_id": "test-session-001"}')

CHAT_INTENT=$(echo "${CHAT_RESPONSE}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('intent','?'))" 2>/dev/null || echo "error")

if echo "${CHAT_RESPONSE}" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
  pass "Respuesta válida del chatbot (intent: ${CHAT_INTENT})"
  echo "    Respuesta: $(echo ${CHAT_RESPONSE} | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('respuesta',''); print(r[:100]+'...' if len(r)>100 else r)" 2>/dev/null)"
else
  fail "Respuesta inválida del chatbot: ${CHAT_RESPONSE}"
fi

# ── 6. Balance de caja ────────────────────────────────────────────────────────
section "6. Balance de caja (GET /api/cash/balance/)"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/cash/balance/" \
  -H "Host: ${HOST}" -H "${AUTH_HEADER}")

[ "$STATUS" = "200" ] && pass "Balance de caja OK (HTTP $STATUS)" \
                       || fail "Error HTTP $STATUS"

# ── 7. Chatbot — intent ventas_por_periodo ────────────────────────────────────
section "7. Chatbot staff — ventas por período"

CHAT2=$(curl -s -X POST "${BASE}/api/chatbot/mensaje/" \
  -H "Host: ${HOST}" \
  -H "${AUTH_HEADER}" \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "ventas de enero", "session_id": "test-session-001"}')

INTENT2=$(echo "${CHAT2}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('intent','?'))" 2>/dev/null || echo "error")
[ "$INTENT2" = "ventas_por_periodo" ] && pass "Intent correcto: ventas_por_periodo" \
                                       || fail "Intent incorrecto: ${INTENT2} (esperado: ventas_por_periodo)"

# ── Resumen ───────────────────────────────────────────────────────────────────
section "Resumen"
echo "  Tenant probado: ${TENANT} (Host: ${HOST})"
echo "  Para probar otro tenant: bash test_api.sh papeleria"
echo ""
