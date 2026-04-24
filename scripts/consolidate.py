#!/usr/bin/env python3
"""
Consolida todos os agents/*.jsonl em um CONSOLIDADO.jsonl.

- Valida schema mínimo (id, nome, metodo_modificacao, dificuldade, aderencia_psyfun)
- Normaliza nome (lowercase, strip, remove punctuation) pra detectar duplicatas
- Em duplicata, mantém entrada com maior (aderencia_psyfun + viabilidade_claude - dificuldade)
- Atribui fonte_agente se faltando, baseado no nome do arquivo
- Escreve exports/CONSOLIDADO.jsonl + stats em stderr
"""
from __future__ import annotations
import json
import re
import sys
import unicodedata
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
AGENTS_DIR = ROOT / "agents"
OUT = ROOT / "exports" / "CONSOLIDADO.jsonl"
OUT.parent.mkdir(parents=True, exist_ok=True)


def normalize_name(n: str) -> str:
    """lowercase, remove acentos, remove punctuação e espaços extras."""
    if not n:
        return ""
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    n = n.lower()
    n = re.sub(r"[^a-z0-9]+", "", n)
    return n


def score(entry: dict) -> float:
    """Score de ranking (maior = melhor)."""
    a = entry.get("aderencia_psyfun", 0) or 0
    v = entry.get("viabilidade_claude", 0) or 0
    d = entry.get("dificuldade", 5) or 5
    return a * 2 + v - d * 0.5


REQUIRED = ["id", "nome", "metodo_modificacao", "dificuldade", "aderencia_psyfun"]


def load_agent_file(path: Path) -> tuple[list[dict], list[str]]:
    entries = []
    errors = []
    slug = path.stem
    with path.open() as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError as ex:
                errors.append(f"{slug}:{i} JSON erro: {ex}")
                continue
            missing = [k for k in REQUIRED if e.get(k) in (None, "")]
            if missing:
                errors.append(f"{slug}:{i} nome={e.get('nome','?')} faltam {missing}")
                continue
            e.setdefault("fonte_agente", slug)
            e.setdefault("imagens", [])
            e.setdefault("links", [])
            entries.append(e)
    return entries, errors


def main() -> int:
    files = sorted(AGENTS_DIR.glob("*.jsonl"))
    if not files:
        print("Nenhum *.jsonl em agents/", file=sys.stderr)
        return 1

    all_entries: list[dict] = []
    all_errors: list[str] = []
    per_agent_counts: dict[str, int] = {}

    for f in files:
        entries, errors = load_agent_file(f)
        all_entries.extend(entries)
        all_errors.extend(errors)
        per_agent_counts[f.stem] = len(entries)

    print(f"Agentes: {len(files)}", file=sys.stderr)
    for slug, c in sorted(per_agent_counts.items()):
        print(f"  {slug}: {c}", file=sys.stderr)
    print(f"Total bruto: {len(all_entries)}", file=sys.stderr)
    if all_errors:
        print(f"Erros de schema/parse: {len(all_errors)}", file=sys.stderr)
        for e in all_errors[:20]:
            print(f"  {e}", file=sys.stderr)

    # Dedup por nome normalizado
    bucket: dict[str, list[dict]] = defaultdict(list)
    for e in all_entries:
        key = normalize_name(e["nome"])
        if not key:
            continue
        bucket[key].append(e)

    dedup: list[dict] = []
    dup_count = 0
    for key, group in bucket.items():
        if len(group) == 1:
            dedup.append(group[0])
        else:
            dup_count += len(group) - 1
            best = max(group, key=score)
            # preserva fonte_agente de todas as origens
            best["fonte_agente"] = "|".join(sorted({x.get("fonte_agente", "") for x in group}))
            # mescla links
            seen_links = set()
            merged_links = []
            for x in group:
                for l in x.get("links", []) or []:
                    if l and l not in seen_links:
                        seen_links.add(l)
                        merged_links.append(l)
            best["links"] = merged_links
            dedup.append(best)

    print(f"Duplicatas removidas: {dup_count}", file=sys.stderr)
    print(f"Final pós-dedup: {len(dedup)}", file=sys.stderr)

    # ordena por score descendente
    dedup.sort(key=score, reverse=True)

    with OUT.open("w") as f:
        for e in dedup:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print(f"Escrito: {OUT}", file=sys.stderr)

    # Distribuição
    print("\nDistribuição aderencia_psyfun:", file=sys.stderr)
    dist: dict[int, int] = defaultdict(int)
    for e in dedup:
        dist[e.get("aderencia_psyfun", 0)] += 1
    for k in sorted(dist.keys(), reverse=True):
        print(f"  {k}: {dist[k]}", file=sys.stderr)

    print("\nDistribuição metodo_modificacao (top 10):", file=sys.stderr)
    mdist: dict[str, int] = defaultdict(int)
    for e in dedup:
        mdist[e.get("metodo_modificacao", "?")] += 1
    for k, v in sorted(mdist.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k}: {v}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
