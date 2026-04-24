#!/usr/bin/env python3
"""
Busca 1 video do YouTube por jogo via yt-dlp.

Atualiza CONSOLIDADO.jsonl adicionando campos:
  - video_youtube_id (str)
  - video_thumbnail (str — URL pública sem download)
  - video_title (str)

Roda em paralelo via ThreadPoolExecutor.

Uso:
    python3 fetch_videos.py [--limit N] [--concurrency C] [--skip-done]
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
CONS = ROOT / "exports" / "CONSOLIDADO.jsonl"
YTDLP = ROOT / ".venv" / "bin" / "yt-dlp"


def score(e):
    a = e.get("aderencia_psyfun", 0) or 0
    v = e.get("viabilidade_claude", 0) or 0
    d = e.get("dificuldade", 5) or 5
    return a * 2 + v - d * 0.5


def search_one(name, hint=""):
    """Roda yt-dlp ytsearch1; retorna (id, title) ou (None, None)."""
    query = f"{name} {hint}".strip()
    try:
        r = subprocess.run(
            [str(YTDLP), "--flat-playlist", "-j",
             "--default-search", "ytsearch1",
             "--skip-download", "--no-warnings",
             query],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0 or not r.stdout.strip():
            return None, None
        d = json.loads(r.stdout.strip().splitlines()[0])
        vid = d.get("id")
        title = (d.get("title") or "")[:120]
        # rejeita curtos, conversas só
        dur = d.get("duration") or 0
        if dur and dur < 30:
            return None, None
        return vid, title
    except Exception:
        return None, None


def query_hint_for(entry):
    """Decide o sufixo de busca pra reduzir ruído."""
    g = (entry.get("genero", "") or "").lower()
    if "framework" in g or "engine" in g:
        return "demo"
    return "gameplay"


def main(limit, concurrency, skip_done):
    entries = [json.loads(l) for l in CONS.read_text().splitlines() if l.strip()]
    entries.sort(key=score, reverse=True)

    if limit:
        targets = entries[:limit]
    else:
        targets = entries

    if skip_done:
        pending = [e for e in targets if not e.get("video_youtube_id")]
    else:
        pending = targets

    print(f"Total: {len(entries)} · Alvo: {len(targets)} · Pendentes: {len(pending)}", file=sys.stderr)

    results = {}

    def work(e):
        hint = query_hint_for(e)
        vid, title = search_one(e["nome"], hint)
        if vid:
            return e["id"], vid, title
        return e["id"], None, None

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(work, e): e for e in pending}
        done = 0
        found = 0
        for fut in as_completed(futures):
            eid, vid, title = fut.result()
            done += 1
            if vid:
                results[eid] = {"id": vid, "title": title}
                found += 1
            if done % 25 == 0:
                print(f"  {done}/{len(pending)} · {found} encontrados", file=sys.stderr)

    print(f"Achou video pra {len(results)}/{len(pending)}", file=sys.stderr)

    # aplica no JSONL
    for e in entries:
        if e["id"] in results:
            v = results[e["id"]]
            e["video_youtube_id"] = v["id"]
            e["video_thumbnail"] = f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg"
            e["video_title"] = v["title"]
    CONS.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n")
    print(f"CONSOLIDADO.jsonl atualizado", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--concurrency", type=int, default=15)
    ap.add_argument("--skip-done", action="store_true")
    args = ap.parse_args()
    main(args.limit, args.concurrency, args.skip_done)
