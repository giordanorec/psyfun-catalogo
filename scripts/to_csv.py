#!/usr/bin/env python3
"""CONSOLIDADO.jsonl -> CATALOGO.csv (RFC 4180)."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
SRC = ROOT / "exports" / "CONSOLIDADO.jsonl"
DST = ROOT / "exports" / "CATALOGO.csv"

COLUMNS = [
    "id", "nome", "ano_lancamento", "dev_publisher", "plataforma", "genero",
    "engine_tech", "status_codigo", "metodo_modificacao",
    "dificuldade", "esforco_horas", "viabilidade_claude", "raciocinio_dificuldade",
    "dilemas_compativeis", "aderencia_psyfun", "exemplo_concreto",
    "popularidade", "idade_publico", "requisitos_tecnicos", "custo_licencas",
    "risco_tos", "links", "imagens", "observacoes", "fonte_agente",
]


def flat(val):
    if isinstance(val, list):
        return " | ".join(str(x) for x in val)
    if val is None:
        return ""
    return str(val)


def main() -> int:
    if not SRC.exists():
        print(f"Falta: {SRC}", file=sys.stderr)
        return 1

    rows = []
    with SRC.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            rows.append({c: flat(e.get(c, "")) for c in COLUMNS})

    with DST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"Escrito: {DST}  ({len(rows)} linhas)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
