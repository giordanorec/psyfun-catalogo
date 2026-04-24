#!/usr/bin/env python3
"""
Atribui `qualidade_producao` (1-5) + `raciocinio_qualidade` a cada jogo.

Interpretação da métrica:
  5 — AAA/premium: arte polida, gameplay refinado, produção comercial massiva
  4 — Indie polido: visualmente consistente, gameplay maduro, base sólida
  3 — Sólido: funcional com algum polish; open-source maduro ou AA
  2 — Funcional: serve, mas arte genérica / protótipo polido
  1 — Cru/protótipo: lógica OK mas sem arte/polish; frameworks de pesquisa

Heurística: combina fonte_agente (proxy mais forte), status_codigo,
popularidade textual, engine conhecida, gênero AAA-típico.

Uso:
    .venv/bin/python scripts/score_quality.py
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

CONS = Path("/home/grec/Documentos/psyfun-jogos-research/exports/CONSOLIDADO.jsonl")


LABELS = {
    1: "cru/protótipo",
    2: "funcional",
    3: "sólido",
    4: "indie polido",
    5: "AAA/premium",
}


def assess(e: dict) -> tuple[int, str]:
    score = 2.5
    reasons = []

    pop = (e.get("popularidade") or "").lower()
    status = e.get("status_codigo", "")
    fonte = e.get("fonte_agente", "") or ""
    genero = (e.get("genero") or "").lower()
    engine = (e.get("engine_tech") or "").lower()
    nome = (e.get("nome") or "").lower()

    # ---- popularidade (sinal mais forte de produção alta) ----
    if re.search(r"\b\d+\s*(million|m\b|mau|dau)", pop):
        score += 1.4
        reasons.append("milhões de usuários/jogadores")
    elif re.search(r"\b(massive|seminal|iconic|legend|classic|cult|goty|game of the year)\b", pop):
        score += 1.0
        reasons.append("produção icônica")
    elif re.search(r"metacritic[:\s]*\d*[89]\d|opencritic.*[89]\d", pop):
        score += 0.9
        reasons.append("Metacritic alto")
    elif re.search(r"steam[^0-9]*9[0-9]%|overwhelmingly positive", pop):
        score += 0.8
        reasons.append("Steam overwhelmingly positive")
    elif re.search(r"\b\d+\s*k\+?\s*(reviews|stars|players|downloads|installs)", pop):
        score += 0.5
    elif re.search(r"\baaa\b|\baa\b", pop):
        score += 0.8
        reasons.append("AAA/AA")

    # ---- status do código ----
    if status == "modding-community":
        score += 1.0  # jogos fechados com mod community = comerciais polidos
        reasons.append("jogo comercial com mod community")
    elif status == "sdk-oficial":
        score += 0.7
        reasons.append("SDK oficial do publisher")
    elif status == "creative-platform":
        score += 0.6
        reasons.append("plataforma comercial massiva")
    elif status == "source-available":
        score += 0.1
    elif status == "closed-only":
        score += 0.3
    # open-source neutro (pode ser qualquer nível)

    # ---- fonte agente (proxy do universo de onde veio) ----
    if "sdk-aaa" in fonte:
        score += 1.2
        reasons.append("AAA/indie premium")
    if "party-multiplayer" in fonte and "sdk-aaa" not in fonte:
        score += 0.5
    if "creative-platforms" in fonte:
        score += 0.6
    if "classic-reimpl" in fonte:
        score += 0.3  # reimpls de AAA antigos
    if "tabletop-digital" in fonte:
        score += 0.2
    if "engine-templates" in fonte:
        score -= 0.2  # templates são base, não jogo pronto
    if "open-source" in fonte and "classic-reimpl" not in fonte and "creative-platforms" not in fonte:
        score -= 0.4
    if "html5-web" in fonte and "party-multiplayer" not in fonte:
        score -= 0.6
        reasons.append("jogo web simples")
    if "itch-source" in fonte:
        score -= 0.7
        reasons.append("protótipo de jam")
    if "mobile-foss" in fonte:
        score -= 0.4
    if "research-serious" in fonte:
        score -= 1.2
        reasons.append("framework de pesquisa (sem arte)")
    if "reverse-gray" in fonte:
        score += 0.3

    # ---- engine conhecida ----
    if any(t in engine for t in ["unreal", "creation engine", "cryengine", "source engine", "id tech", "gamebryo"]):
        score += 0.4
    elif "unity" in engine and "research" not in fonte:
        score += 0.2
    elif any(t in engine for t in ["pico-8", "tic-80", "bitsy", "pixel vision", "quadplay"]):
        score -= 0.3  # fantasy consoles: intencionalmente minimalistas
        reasons.append("fantasy console minimalista")
    elif any(t in engine for t in ["twine", "ink", "inform"]):
        score -= 0.5
        reasons.append("engine narrativa")
    elif "ren'py" in engine or "renpy" in engine:
        score -= 0.1
    elif "phaser" in engine or "html5" in engine or "three" in engine:
        score -= 0.3

    # ---- nomes icônicos que sabemos serem top-tier ----
    aaa_names = [
        "minecraft", "cyberpunk 2077", "witcher 3", "red dead", "grand theft",
        "baldur's gate 3", "elden ring", "overcooked", "stardew valley",
        "hollow knight", "slay the spire", "among us", "fortnite", "roblox",
        "league of legends", "counter-strike", "team fortress", "dota", "portal",
        "half-life", "skyrim", "fallout", "bioshock", "dark souls",
        "valheim", "terraria", "factorio", "rimworld", "cities: skylines",
        "civilization", "paradox", "crusader kings", "europa universalis",
        "total war", "kerbal space", "no man's sky", "gta"
    ]
    if any(n in nome for n in aaa_names):
        score += 0.8
        if not any("AAA" in r or "comercial" in r for r in reasons):
            reasons.append("título reconhecido globalmente")

    # ---- clamp + round ----
    raw = score
    score = max(1, min(5, round(score)))
    label = LABELS[score]

    # compor raciocinio curto
    if reasons:
        rationale = f"{label} — {'; '.join(reasons[:2])}"
    else:
        rationale = f"{label} (heurística neutra, score bruto {raw:.1f})"
    return score, rationale


def main():
    entries = [json.loads(l) for l in CONS.read_text().splitlines() if l.strip()]
    dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for e in entries:
        q, rationale = assess(e)
        e["qualidade_producao"] = q
        e["raciocinio_qualidade"] = rationale
        dist[q] += 1
    CONS.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n")
    print(f"{len(entries)} jogos atualizados com qualidade_producao", file=sys.stderr)
    for k in range(5, 0, -1):
        print(f"  {k} {LABELS[k]:18s} {dist[k]}", file=sys.stderr)


if __name__ == "__main__":
    main()
