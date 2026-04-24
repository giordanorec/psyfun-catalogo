#!/usr/bin/env bash
# Encadeia consolidação → CSV → ranking → dashboard.
# (o download de imagens é opcional e pesado — rodar separado)
set -euo pipefail

ROOT="/home/grec/Documentos/psyfun-jogos-research"
cd "$ROOT"
PY="$ROOT/.venv/bin/python"

echo "=== 1/4 consolidate ==="
$PY scripts/consolidate.py

echo ""
echo "=== 2/4 csv ==="
$PY scripts/to_csv.py

echo ""
echo "=== 3/4 ranking TOP100/TOP25 ==="
$PY scripts/rank_top.py

echo ""
echo "=== 4/4 dashboard HTML ==="
$PY scripts/build_dashboard.py

echo ""
echo "=== done ==="
ls -la exports/
