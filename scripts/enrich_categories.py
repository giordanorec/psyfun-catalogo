#!/usr/bin/env python3
"""
Adiciona taxonomia Steam-like ao CONSOLIDADO.jsonl:
  genero_tag (multi), visualizacao (multi), licenca, modo_jogo (multi),
  ritmo, duracao, tema (multi)

Heurística determinística baseada em keywords em nome + genero +
engine_tech + observacoes + raciocinio_dificuldade + exemplo_concreto.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from collections import Counter

CONS = Path("/home/grec/Documentos/psyfun-jogos-research/exports/CONSOLIDADO.jsonl")


def text_blob(e):
    parts = [
        e.get("nome"), e.get("genero"), e.get("engine_tech"),
        e.get("observacoes"), e.get("raciocinio_dificuldade"),
        e.get("exemplo_concreto"), e.get("dev_publisher"),
        e.get("status_codigo"), e.get("fonte_agente"),
    ]
    return " ".join(str(p or "").lower() for p in parts)


# ==================== GENERO TAG ====================
GENRE_RULES = [
    ("action", ["action game", "action-adventure", "beat-em-up", "hack and slash"]),
    ("shooter", ["shooter", "fps", "first-person shooter", "tps", "third-person shooter", "quake", "doom ", "halo", "counter-strike", "battle royale"]),
    ("fighting", ["fighting game", "fighting", "brawler", "street fighter", "smash bros"]),
    ("platformer", ["platformer", "platforming", "jump", "mario", "sonic", "celeste", "super tux", "hollow knight"]),
    ("puzzle", ["puzzle", "tetris", "sudoku", "match-3", "match 3", "bejeweled", "2048", "sokoban", "portal", "baba is you"]),
    ("strategy", ["strategy", "rts", "real-time strategy", "4x", "turn-based strategy", "civilization", "age of empires", "starcraft", "total war", "stellaris", "crusader kings", "europa universalis"]),
    ("rpg", ["rpg", "role-playing", "role playing", "jrpg", "wrpg", "action rpg", "arpg", "skyrim", "fallout", "witcher", "baldur's gate", "diablo", "path of exile"]),
    ("roguelike", ["roguelike", "roguelite", "rogue-lite", "nethack", "angband", "dcss", "dungeon crawl", "slay the spire", "binding of isaac", "hades", "cataclysm"]),
    ("sports", ["sports", "football", "soccer", "basketball", "baseball", "hockey", "tennis", "golf", "fifa", "nba 2k", "madden", "pes"]),
    ("racing", ["racing", "kart", "rally", "mario kart", "need for speed", "gran turismo", "forza", "trackmania"]),
    ("simulation", ["simulation", "sim", "truck simulator", "farming simulator", "flight sim", "ksp", "kerbal", "factorio", "rimworld", "cities:", "sim city", "stardew", "animal crossing"]),
    ("party", ["party game", "jackbox", "mario party", "overcooked", "fall guys", "gartic", "skribbl", "pictionary"]),
    ("horror", ["horror", "survival horror", "resident evil", "silent hill", "amnesia", "phasmophobia", "slender"]),
    ("survival", ["survival", "crafting survival", "minecraft", "terraria", "valheim", "ark:", "rust", "7 days to die", "don't starve"]),
    ("rhythm", ["rhythm", "music game", "beat saber", "guitar hero", "rock band", "stepmania", "osu"]),
    ("card", ["card game", "deckbuilder", "deck-builder", "tcg", "ccg", "hearthstone", "mtg", "magic the gathering", "solitaire", "poker", "uno"]),
    ("board", ["board game", "boardgame", "chess", "go game", "go board", "checkers", "risk", "monopoly", "catan", "scrabble", "clue"]),
    ("mmo", ["mmo", "mmorpg", "massively multiplayer", "world of warcraft", "final fantasy xiv", "eve online", "runescape"]),
    ("visual-novel", ["visual novel", "vn", "ren'py", "renpy", "dating sim", "otome"]),
    ("social-deduction", ["social deduction", "among us", "werewolf", "mafia", "town of salem", "secret hitler", "goose goose duck", "spyfall", "blood on the clocktower"]),
    ("tower-defense", ["tower defense", "tower-defense", "kingdom rush", "bloons", "mindustry"]),
    ("sandbox", ["sandbox", "minecraft", "roblox", "gmod", "garry's mod", "dreams", "terraria", "creative mode"]),
    ("educational", ["educational", "edutainment", "learning game", "serious game", "training"]),
    ("adventure", ["adventure", "point-and-click", "point and click", "monkey island", "myst", "zelda"]),
    ("casual", ["casual", "hypercasual", "hyper-casual", "candy crush", "flappy", "angry birds", "fruit ninja"]),
]


def classify_genero(blob):
    tags = []
    for tag, keys in GENRE_RULES:
        for k in keys:
            if k in blob:
                tags.append(tag)
                break
    return list(dict.fromkeys(tags))  # dedup preserve order


# ==================== VISUALIZAÇÃO ====================
VIS_RULES = [
    ("pixel-art", ["pixel", "8-bit", "16-bit", "retro pixel", "pico-8", "tic-80"]),
    ("3d", [" 3d ", "3d-", "-3d", "three.js", "babylonjs", "unity 3d", "unreal", "unreal engine"]),
    ("2d", [" 2d ", "2d-", "-2d", "2d platformer", "2d game", "sidescroll"]),
    ("isometric", ["isometric", "iso-view", "top-down iso"]),
    ("low-poly", ["low-poly", "low poly", "voxel"]),
    ("realistic", ["realistic", "photorealistic", "photo-realistic", "cryengine"]),
    ("text-only", ["text-only", "text adventure", "roguelike ascii", "ascii", "nethack", "twine", "ink"]),
    ("top-down", ["top-down", "top down"]),
    ("side-scroller", ["side-scroll", "sidescroll", "side-scrolling"]),
    ("first-person", ["first-person", "first person", "fps", "vr"]),
    ("third-person", ["third-person", "third person", "tps"]),
    ("vr", [" vr ", "vr-", "virtual reality", "quest", "vrchat", "vrchatworld"]),
]


def classify_vis(blob):
    tags = []
    for tag, keys in VIS_RULES:
        for k in keys:
            if k in blob:
                tags.append(tag)
                break
    # fallback: jogos FOSS web são quase sempre 2d
    if not tags and any(k in blob for k in ["phaser", "html5", "pygame", "construct", "gdevelop"]):
        tags.append("2d")
    return list(dict.fromkeys(tags))


# ==================== LICENÇA ====================
def classify_licenca(e, blob):
    status = e.get("status_codigo", "")
    custo = (e.get("custo_licencas") or "").lower()

    if status == "open-source":
        # tenta detectar copyleft
        if any(k in blob for k in ["gpl-3", "gpl 3", "gplv3", "agpl", "gpl-2", "copyleft"]):
            return "open-source-copyleft"
        if any(k in blob for k in ["mit license", " mit ", "mit,", "bsd", "apache", "zlib", "unlicense", "cc0", "cc-0"]):
            return "open-source-permissive"
        # default FOSS = permissive (mais comum)
        return "open-source-permissive"
    if status == "source-available":
        return "source-available"
    if status in ("sdk-oficial", "modding-community", "closed-only"):
        if any(k in custo for k in ["free", "gratuito", "grátis", "freeware", "0"]):
            return "freeware"
        return "proprietary-modable"
    if status == "creative-platform":
        return "proprietary-modable"
    return "unclear"


# ==================== MODO DE JOGO ====================
def classify_modo(blob):
    tags = []
    if any(k in blob for k in ["single-player", "single player", "solo", "singleplayer"]):
        tags.append("single")
    if any(k in blob for k in ["local multi", "local-multi", "couch co-op", "couch coop", "same screen", "split-screen", "split screen", "hotseat"]):
        tags.append("local-multi")
    if any(k in blob for k in ["online multi", "online-multi", "online multiplayer", "multiplayer online", "netcode", "dedicated server", "p2p"]):
        tags.append("online-multi")
    if any(k in blob for k in [" co-op", " coop", "cooperative", "co-operative"]):
        tags.append("coop")
    if any(k in blob for k in ["pvp", "player vs player", "player versus"]):
        tags.append("pvp")
    if "mmo" in blob or "massively multiplayer" in blob:
        tags.append("mmo")
    # default: se for single-player só OU zero detectado, single
    if not tags:
        tags.append("single")
    return list(dict.fromkeys(tags))


# ==================== RITMO ====================
def classify_ritmo(blob):
    if any(k in blob for k in ["turn-based", "turn based", "turn by turn", "tbs"]):
        return "turn-based"
    if any(k in blob for k in ["async", "asynchronous", "play by email", "pbem"]):
        return "async"
    if any(k in blob for k in ["tick-based", "tick based", "simulation tick"]):
        return "tick-based"
    if any(k in blob for k in ["action", "real-time", "realtime", "real time", "fps", "shooter", "fighting"]):
        return "action"
    # default real-time
    return "real-time"


# ==================== DURAÇÃO ====================
def classify_duracao(blob):
    if any(k in blob for k in ["endless", "infinite", "persistent world", "sandbox", "open-ended", "open ended", "mmo", "idle game", "clicker"]):
        return "endless"
    if any(k in blob for k in ["campaign", "story-driven", "story driven", "narrative", "single-player story", "plot-driven"]):
        return "campaign"
    if any(k in blob for k in ["session", "quick match", "short match", "round-based", "round based", "per round"]):
        return "session"
    # default
    return "session"


# ==================== TEMA ====================
TEMA_RULES = [
    ("fantasy", ["fantasy", "dragon", "wizard", "mage", "elf", "dwarf", "tolkien", "sword and sorcery"]),
    ("sci-fi", ["sci-fi", "science fiction", "scifi", "space ", "galaxy", "alien", "mars ", "cyberpunk", "futuristic"]),
    ("cyberpunk", ["cyberpunk", "cyber-punk", "neo-tokyo", "dystopian future"]),
    ("post-apocalyptic", ["post-apocalypse", "post apocalypse", "wasteland", "fallout", "mad max", "nuclear"]),
    ("modern", ["modern", "contemporary", "present-day", "present day"]),
    ("historical", ["historical", "medieval", "renaissance", "victorian", "napoleonic", "ww2", "wwii", "world war", "ancient"]),
    ("military", ["military", "war game", "combat", "army", "tactical shooter", "arma"]),
    ("horror", ["horror", "creepy", "scary", "zombie", "ghost", "lovecraft", "cosmic horror"]),
    ("abstract", ["abstract", "minimal", "geometric", "pattern", "color puzzle"]),
    ("cute", ["cute", "kawaii", "adorable", "animal crossing", "stardew", "cozy"]),
]


def classify_tema(blob):
    tags = []
    for tag, keys in TEMA_RULES:
        for k in keys:
            if k in blob:
                tags.append(tag)
                break
    return list(dict.fromkeys(tags))


# ==================== MAIN ====================
def main():
    entries = [json.loads(l) for l in CONS.read_text().splitlines() if l.strip()]

    stats = {
        "genero_tag": Counter(), "visualizacao": Counter(),
        "licenca": Counter(), "modo_jogo": Counter(),
        "ritmo": Counter(), "duracao": Counter(), "tema": Counter(),
    }

    for e in entries:
        blob = text_blob(e)

        g = classify_genero(blob)
        v = classify_vis(blob)
        lic = classify_licenca(e, blob)
        mm = classify_modo(blob)
        r = classify_ritmo(blob)
        d = classify_duracao(blob)
        t = classify_tema(blob)

        e["genero_tag"] = "|".join(g) if g else ""
        e["visualizacao"] = "|".join(v) if v else ""
        e["licenca"] = lic
        e["modo_jogo"] = "|".join(mm)
        e["ritmo"] = r
        e["duracao"] = d
        e["tema"] = "|".join(t) if t else ""

        for tag in g: stats["genero_tag"][tag] += 1
        for tag in v: stats["visualizacao"][tag] += 1
        stats["licenca"][lic] += 1
        for tag in mm: stats["modo_jogo"][tag] += 1
        stats["ritmo"][r] += 1
        stats["duracao"][d] += 1
        for tag in t: stats["tema"][tag] += 1

    CONS.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n")
    print(f"{len(entries)} jogos enriquecidos\n", file=sys.stderr)

    for k, c in stats.items():
        print(f"\n== {k.upper()} ==", file=sys.stderr)
        for tag, n in c.most_common(20):
            print(f"  {n:4d}  {tag}", file=sys.stderr)


if __name__ == "__main__":
    main()
