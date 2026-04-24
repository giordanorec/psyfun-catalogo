#!/usr/bin/env bash
# Watcher dos subagents assíncronos do Claude Code (tool Agent).
#
# Os subagents gravam stream-json em /tmp/claude-*/<sessao>/tasks/<id>.output.
# Este script:
#   1. Detecta as task outputs do Giordano
#   2. Abre tmux tiled com 1 painel por agente rodando
#   3. Cada painel mostra só linhas "stream_event" -> text_delta (live typing) +
#      tool calls resumidos (read/write/bash/websearch)
#
# Uso:
#   scripts/watch_subagents.sh            # abre tmux
#   scripts/watch_subagents.sh --stop     # mata session

set -euo pipefail

SESSION="psyfun-subagents"
TASKS_DIR="$(ls -td /tmp/claude-*/-home-grec/*/tasks 2>/dev/null | head -1 || true)"

if [[ "${1:-}" == "--stop" ]]; then
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    exit 0
fi

if [[ -z "$TASKS_DIR" ]]; then
    echo "Não achei diretório de tasks. Os subagents já terminaram?" >&2
    exit 1
fi

echo "Tasks dir: $TASKS_DIR"
FILES=($(ls -t "$TASKS_DIR"/*.output 2>/dev/null))
if [[ ${#FILES[@]} -eq 0 ]]; then
    echo "Sem .output ativos." >&2
    exit 1
fi

# Pretty-printer: tail + parse stream-json -> mostra só o que é útil
PRETTY_PY='
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line or line[0] not in "{[":
        continue
    try:
        ev = json.loads(line)
    except:
        continue
    t = ev.get("type")
    if t == "stream_event":
        inner = ev.get("event", {}) or {}
        et = inner.get("type")
        if et == "content_block_delta":
            d = inner.get("delta", {}) or {}
            if d.get("type") == "text_delta":
                sys.stdout.write(d.get("text", ""))
                sys.stdout.flush()
        elif et == "content_block_start":
            b = inner.get("content_block", {}) or {}
            if b.get("type") == "tool_use":
                print(f"\n\x1b[33m>> {b.get(\"name\", \"?\")}\x1b[0m", flush=True)
    elif t == "user":
        m = ev.get("message", {}) or {}
        for c in m.get("content", []) or []:
            if isinstance(c, dict) and c.get("type") == "tool_result":
                r = c.get("content", "")
                if isinstance(r, list):
                    r = " ".join(x.get("text","") for x in r if isinstance(x, dict))
                preview = str(r)[:120].replace("\n", " ")
                color = "31" if c.get("is_error") else "32"
                print(f"\x1b[{color}m<< {preview}\x1b[0m", flush=True)
    elif t == "result":
        sub = ev.get("subtype", "?")
        dur = ev.get("duration_ms", 0)
        print(f"\n\x1b[35m=== DONE {sub} {dur/1000:.1f}s ===\x1b[0m", flush=True)
'

if tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux kill-session -t "$SESSION"
fi

FIRST="${FILES[0]}"
tmux new-session -d -s "$SESSION" "tail -F '$FIRST' | python3 -c '$PRETTY_PY'; read"
tmux select-pane -t "$SESSION" -T "$(basename $FIRST .output | cut -c1-8)"

for ((i=1; i<${#FILES[@]}; i++)); do
    F="${FILES[$i]}"
    tmux split-window -t "$SESSION" "tail -F '$F' | python3 -c '$PRETTY_PY'; read"
    tmux select-pane -t "$SESSION" -T "$(basename $F .output | cut -c1-8)"
    tmux select-layout -t "$SESSION" tiled >/dev/null
done

tmux set -t "$SESSION" pane-border-status top >/dev/null
tmux set -t "$SESSION" pane-border-format ' #{pane_title} ' >/dev/null
tmux select-layout -t "$SESSION" tiled >/dev/null

if command -v tilix >/dev/null; then
    tilix -e "tmux attach -t $SESSION" >/dev/null 2>&1 &
    disown
    echo "Tilix aberto com $SESSION. ${#FILES[@]} painéis."
else
    echo "Tilix não encontrado. Attach manualmente:  tmux attach -t $SESSION"
fi
