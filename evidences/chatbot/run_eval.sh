#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# run_eval.sh — TechHive 3.0 Chatbot
# Ejecuta el evaluador del router de intenciones y captura la salida.
# NO requiere base de datos ni servidor Django — solo Python 3.x.
#
# Uso:
#   bash evidences/chatbot/run_eval.sh
#   bash evidences/chatbot/run_eval.sh --save  # guarda salida en .txt
#
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

CHATBOT_DIR="backend/apps/chatbot"
SAVE_OUTPUT=false

if [[ "${1:-}" == "--save" ]]; then
  SAVE_OUTPUT=true
fi

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TechHive 3.0 — Evaluador de Chatbot                ${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"

# Verificar que el directorio existe
if [ ! -d "${CHATBOT_DIR}" ]; then
  echo "ERROR: No se encontró ${CHATBOT_DIR}"
  echo "Ejecutar desde la raíz del repositorio."
  exit 1
fi

# ── Evaluación STAFF ──────────────────────────────────────────────────────────
echo -e "\n${BLUE}[1/2] Evaluando router STAFF (63 casos)...${NC}"

if [ "$SAVE_OUTPUT" = true ]; then
  python "${CHATBOT_DIR}/evaluar_chatbot.py" --version "v1.2" --modo staff \
    | tee /tmp/eval_staff.txt
else
  python "${CHATBOT_DIR}/evaluar_chatbot.py" --version "v1.2" --modo staff
fi

echo -e "${GREEN}  ✓ Evaluación staff completada${NC}"

# ── Evaluación CLIENTE ────────────────────────────────────────────────────────
echo -e "\n${BLUE}[2/2] Evaluando router CLIENTE (60 casos)...${NC}"

if [ "$SAVE_OUTPUT" = true ]; then
  python "${CHATBOT_DIR}/evaluar_chatbot.py" --version "v1.1" --modo cliente \
    | tee /tmp/eval_cliente.txt
else
  python "${CHATBOT_DIR}/evaluar_chatbot.py" --version "v1.1" --modo cliente
fi

echo -e "${GREEN}  ✓ Evaluación cliente completada${NC}"

# ── Resumen ───────────────────────────────────────────────────────────────────
echo -e "\n${BLUE}══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Resumen esperado:${NC}"
echo -e "    Staff:   63/63 correctos — Accuracy 100.0% — Macro F1 100.0%"
echo -e "    Cliente: 60/60 correctos — Accuracy 100.0% — Macro F1 100.0%"
echo -e "${BLUE}══════════════════════════════════════════════════════${NC}"

if [ "$SAVE_OUTPUT" = true ]; then
  echo -e "\n  Salidas guardadas en:"
  echo -e "    /tmp/eval_staff.txt"
  echo -e "    /tmp/eval_cliente.txt"
fi

echo ""
