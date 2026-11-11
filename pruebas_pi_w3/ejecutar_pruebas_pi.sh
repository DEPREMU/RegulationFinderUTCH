#!/usr/bin/env bash
# Run from repository root with: bash pruebas_pi_w3/ejecutar_pruebas_pi.sh
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
DATA='data/real/week3-prepared'
MODEL='artifacts/training/week3-real-model.json'
RESULTS="pi_resultados/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$RESULTS"

if [[ ! -f "$MODEL" || ! -f "$DATA/metadata.json" ]]; then
  echo 'ERROR: frozen Week 3 dataset/model not found. Update local project; do not retrain.' >&2
  exit 2
fi
if [[ "$(uname -s)" != 'Linux' ]]; then
  echo 'ERROR: this script is intended for Linux on Raspberry Pi.' >&2
  exit 2
fi
if ! command -v uv >/dev/null 2>&1; then
  echo 'ERROR: uv is not installed or is not in PATH.' >&2
  exit 2
fi

BOARD="$(tr -d '\0' < /proc/device-tree/model 2>/dev/null || true)"
if [[ -z "$BOARD" ]]; then BOARD="Unknown board; verify manually"; fi
{
  echo "UTC: $(date -u +%FT%TZ)"
  echo "Board: $BOARD"
  echo "Git commit: $(git rev-parse HEAD 2>/dev/null || echo unknown)"
  echo '--- uname ---'; uname -a
  echo '--- OS ---'; cat /etc/os-release
  echo '--- CPU ---'; lscpu
  echo '--- RAM ---'; free -h
  echo '--- Python ---'; python3 --version
  echo '--- model sha256 ---'; sha256sum "$MODEL"
  echo '--- data sha256 ---'; sha256sum "$DATA/metadata.json" "$DATA/articles.json" "$DATA/training.json"
  echo '--- uv version ---'; uv --version
  echo '--- power / throttle (if available) ---'
  if command -v vcgencmd >/dev/null 2>&1; then vcgencmd get_throttled || true; vcgencmd measure_temp || true; fi
} > "$RESULTS/hardware_y_versiones.txt" 2>&1

step() {
  local label="$1"
  shift
  printf 'Ejecutando %-24s ... ' "$label"
  if "$@" > "$RESULTS/${label}.log" 2>&1; then
    echo 'OK'
  else
    echo "ERROR: revisa $RESULTS/${label}.log"
    exit 1
  fi
}

step 01_instalacion uv sync --frozen
step 02_ruff uv run --frozen ruff check src/regulation_finder scripts tests
step 03_formato uv run --frozen ruff format --check src/regulation_finder scripts tests
step 04_pytest uv run --frozen pytest
step 05_validacion uv run --frozen regulation-finder --data "$DATA" --model "$MODEL" validate
step 06_busqueda uv run --frozen regulation-finder --data "$DATA" --model "$MODEL" --min-topic-probability 0.35 --min-lexical-score 0.25 search '¿Cuál es la calificación mínima para aprobar?'
step 07_funcionales uv run --frozen python pruebas_pi_w3/pruebas_funcionales_pi.py --data "$DATA" --model "$MODEL" --topic-threshold 0.35 --lexical-threshold 0.25 --output "$RESULTS/funcionales"

for n in 1 2 3; do
  step "08_medicion_${n}" uv run --frozen regulation-finder --data "$DATA" --model "$MODEL" --min-topic-probability 0.35 --min-lexical-score 0.25 measure --iterations 100 --hardware-label "$BOARD"
  cp "$RESULTS/08_medicion_${n}.log" "$RESULTS/medicion_${n}.json"
done

{
  echo 'STATUS: automatic checks finished. Review each log and JSON.'
  echo 'NOTE: these are development smoke and Raspberry Pi performance checks.'
  echo 'NOTE: no final independent evaluation was rerun.'
  echo 'MANUAL PENDING: web interface and full fresh-start checklist (see README).'
} > "$RESULTS/ESTADO.txt"
echo "Pruebas automáticas completas. Evidencia: $RESULTS"
