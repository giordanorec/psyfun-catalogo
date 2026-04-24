#!/usr/bin/env python3
"""Gera exports/TOP100.md (e TOP25.md) a partir do CONSOLIDADO.jsonl.

Score: (aderencia_psyfun * 2) + viabilidade_claude - (dificuldade * 0.5)
Empate: maior popularidade heuristicamente + menor esforço.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
SRC = ROOT / "exports" / "CONSOLIDADO.jsonl"
OUT100 = ROOT / "exports" / "TOP100.md"
OUT25 = ROOT / "exports" / "TOP25.md"


def base_score(e: dict) -> float:
    a = e.get("aderencia_psyfun", 0) or 0
    v = e.get("viabilidade_claude", 0) or 0
    d = e.get("dificuldade", 5) or 5
    return a * 2 + v - d * 0.5


# Heurística pra popularidade: extrai qualquer número seguido de 'k', 'M', '%', 'reviews'
POP_RE = re.compile(r"(\d+(?:\.\d+)?)\s*([kMm%]|reviews|copies|DAU|MAU|downloads)?", re.I)


def pop_bonus(e: dict) -> float:
    p = e.get("popularidade", "") or ""
    bonus = 0.0
    for match in POP_RE.finditer(p):
        n = float(match.group(1))
        suf = (match.group(2) or "").lower()
        if "m" in suf:
            n *= 1_000_000
        elif "k" in suf:
            n *= 1_000
        elif "%" in suf:
            n = n / 100 * 1_000  # % de review score ~0.01 de peso
        bonus += min(n / 1_000_000, 0.5)  # cap por ocorrência
    return min(bonus, 1.0)


def effort_bonus(e: dict) -> float:
    ef = (e.get("esforco_horas", "") or "").upper()
    return {"XS": 0.5, "S": 0.3, "M": 0.1, "L": -0.1, "XL": -0.3}.get(ef, 0.0)


def full_score(e: dict) -> float:
    return base_score(e) + pop_bonus(e) + effort_bonus(e)


def fmt_entry(i: int, e: dict) -> str:
    dil = e.get("dilemas_compativeis", "") or "-"
    links = e.get("links", []) or []
    link_md = " · ".join(f"[link]({l})" for l in links[:3]) if links else ""
    return (
        f"### {i}. {e['nome']}  "
        f"_(score {full_score(e):.2f})_\n\n"
        f"- **Método**: `{e.get('metodo_modificacao', '?')}` · "
        f"**Dificuldade**: {e.get('dificuldade', '?')} · "
        f"**Esforço**: `{e.get('esforco_horas', '?')}` · "
        f"**Viab. Claude**: {e.get('viabilidade_claude', '?')}\n"
        f"- **Aderência PsyFun**: {e.get('aderencia_psyfun', '?')} · "
        f"**Dilemas**: {dil}\n"
        f"- **Engine/Tech**: {e.get('engine_tech', '-')} · "
        f"**Plataforma**: {e.get('plataforma', '-')} · "
        f"**Idade**: {e.get('idade_publico', '-')}\n"
        f"- **Popularidade**: {e.get('popularidade', '-')}\n"
        f"- **Raciocínio**: {e.get('raciocinio_dificuldade', '-')}\n"
        f"- **Exemplo concreto**: {e.get('exemplo_concreto', '-')}\n"
        f"- **Obs**: {e.get('observacoes', '-')}\n"
        f"- **Fonte**: `{e.get('fonte_agente', '?')}` · {link_md}\n\n---\n"
    )


def main() -> int:
    if not SRC.exists():
        print(f"Falta: {SRC}", file=sys.stderr)
        return 1

    entries = []
    with SRC.open() as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    entries.sort(key=full_score, reverse=True)

    with OUT100.open("w") as f:
        f.write(f"# Top 100 jogos moddáveis — PsyFun\n\n")
        f.write(f"Gerado a partir de `CONSOLIDADO.jsonl` ({len(entries)} jogos total).\n\n")
        f.write(f"**Fórmula**: `aderencia*2 + viabilidade_claude - dificuldade*0.5 + bônus_popularidade + bônus_esforço`\n\n---\n\n")
        for i, e in enumerate(entries[:100], 1):
            f.write(fmt_entry(i, e))

    with OUT25.open("w") as f:
        f.write(f"# Top 25 finalistas — PsyFun\n\n")
        f.write(f"Pré-seleção para análise profunda.\n\n---\n\n")
        for i, e in enumerate(entries[:25], 1):
            f.write(fmt_entry(i, e))

    print(f"Escritos: {OUT100}, {OUT25}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
