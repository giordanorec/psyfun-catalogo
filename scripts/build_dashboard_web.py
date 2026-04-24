#!/usr/bin/env python3
"""
Gera public/index.html do repo psyfun-catalogo — paths /images/, /data/, etc.

Diferente de build_dashboard.py (que gera exports/dashboard.html com paths ../).

NÃO usa regex frágil: carrega CONSOLIDADO, ajusta paths uma vez, renderiza template.
"""
import json
from pathlib import Path
import re
import sys

SRC_JSONL = Path("/home/grec/Documentos/psyfun-jogos-research/exports/CONSOLIDADO.jsonl")
SRC_TEMPLATE = Path("/home/grec/Documentos/psyfun-jogos-research/exports/dashboard.html")
DST = Path("/home/grec/Projetos/psyfun-catalogo/public/index.html")


def main():
    entries = [json.loads(l) for l in SRC_JSONL.read_text().splitlines() if l.strip()]
    for e in entries:
        # paths absolutos servidos pelo Vercel
        e["imagens"] = [
            p.replace("../images/", "/images/").replace("images/", "/images/") if not p.startswith("/") else p
            for p in (e.get("imagens") or [])
        ]
        a = e.get("aderencia_psyfun", 0) or 0
        v = e.get("viabilidade_claude", 0) or 0
        d = e.get("dificuldade", 5) or 5
        e["score"] = round(a * 2 + v - d * 0.5, 2)

    # Lê template renderizado — tem __DATA__ como anchor no primeiro build,
    # mas aqui ele já foi substituído. Então vou substituir a TAG inteira:
    # <script id="data" type="application/json">...</script>
    template = SRC_TEMPLATE.read_text()

    new_data = json.dumps(entries, ensure_ascii=False)
    # Dentro de <script>, apenas `</script>` ou `<!--` podem fechar parsing.
    # Proteger `</` em geral via `<\/` é suficiente e não polui o JSON (JavaScript aceita).
    new_data_safe = new_data.replace("</", "<\\/")

    # Substituição via split — zero regex
    marker_open = '<script id="data" type="application/json">'
    marker_close = "</script>"
    i = template.find(marker_open)
    if i < 0:
        print("marker not found", file=sys.stderr)
        return 1
    j = template.find(marker_close, i)
    if j < 0:
        print("marker close not found", file=sys.stderr)
        return 1
    patched = template[: i + len(marker_open)] + new_data_safe + template[j:]

    DST.write_text(patched, encoding="utf-8")

    # Validação: extrai o script id=data e parseia
    i2 = patched.find(marker_open) + len(marker_open)
    j2 = patched.find(marker_close, i2)
    blob = patched[i2:j2]
    # revert proteção pra validar
    validatable = blob.replace("<\\/", "</")
    try:
        parsed = json.loads(validatable)
        print(f"OK: {len(parsed)} entradas · JSON válido · {DST.stat().st_size:,} bytes", file=sys.stderr)
    except Exception as e:
        print(f"FAIL: JSON inválido: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
