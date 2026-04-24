#!/usr/bin/env python3
"""Segunda passagem de imagens.

Pra cada jogo em CONSOLIDADO.jsonl que ainda não tem imagens em disk,
tenta:
  1. Wikipedia search + OG:image
  2. Steam search pelo nome + primeira capsule/header
  3. DuckDuckGo HTML image (fallback final; scraping moderado)

Atualiza CONSOLIDADO.jsonl com paths novos.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus, urlparse

import aiohttp

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
CONS = ROOT / "exports" / "CONSOLIDADO.jsonl"
IMAGES = ROOT / "images"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"}
TIMEOUT = aiohttp.ClientTimeout(total=20, connect=8)

OG_IMG = re.compile(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', re.I)
TWITTER_IMG = re.compile(r'<meta[^>]*name=["\']twitter:image[^"\']*["\'][^>]*content=["\']([^"\']+)["\']', re.I)
STEAM_LINK = re.compile(r'href=["\']https?://store\.steampowered\.com/app/(\d+)')
IMG_ANY = re.compile(r'<img[^>]+src=["\']([^"\']+\.(?:jpg|jpeg|png|webp))["\']', re.I)


async def fetch_text(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True) as r:
            if r.status != 200:
                return None
            return await r.text(errors="ignore")
    except Exception:
        return None


async def fetch_bin(session, url):
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True) as r:
            if r.status != 200:
                return None
            if "image" not in r.headers.get("Content-Type", ""):
                return None
            data = await r.read()
            if len(data) < 2000 or len(data) > 8 * 1024 * 1024:
                return None
            return data
    except Exception:
        return None


def guess_ext(data, url):
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"RIFF") and b"WEBP" in data[:20]:
        return "webp"
    if data.startswith(b"GIF8"):
        return "gif"
    ext = Path(urlparse(url).path).suffix.lstrip(".").lower()
    return ext if ext in ("jpg", "jpeg", "png", "gif", "webp") else "jpg"


async def wikipedia_og(session, name):
    # Tenta Wikipedia EN e PT
    for lang in ("en", "pt"):
        url = f"https://{lang}.wikipedia.org/wiki/Special:Search?search={quote_plus(name)}&go=Go"
        html = await fetch_text(session, url)
        if not html:
            continue
        m = OG_IMG.search(html)
        if m:
            img = m.group(1)
            if img.startswith("//"):
                img = "https:" + img
            # Ignora placeholder da Wikipedia
            if "Wikipedia-logo" in img or "search-right" in img:
                continue
            return img
    return None


async def steam_search(session, name):
    url = f"https://store.steampowered.com/search/?term={quote_plus(name)}"
    html = await fetch_text(session, url)
    if not html:
        return None
    m = STEAM_LINK.search(html)
    if not m:
        return None
    appid = m.group(1)
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"


async def duckduckgo_img(session, name):
    # fallback: extrai primeiro img em DuckDuckGo Lite search results (não-API, precário)
    q = f"{name} game screenshot"
    url = f"https://duckduckgo.com/?q={quote_plus(q)}&ia=images"
    html = await fetch_text(session, url)
    if not html:
        return None
    for m in IMG_ANY.finditer(html):
        img = m.group(1)
        if img.startswith("http") and "duckduckgo.com" not in img:
            return img
    return None


async def process(session, entry, max_imgs):
    id_ = entry["id"]
    game_dir = IMAGES / id_
    game_dir.mkdir(exist_ok=True)
    existing = sorted(game_dir.glob("*"))
    if len(existing) >= max_imgs:
        return [str(p.relative_to(ROOT)) for p in existing[:max_imgs]]

    name = entry.get("nome", "")
    if not name:
        return [str(p.relative_to(ROOT)) for p in existing]

    saved = list(existing)

    for strat in (wikipedia_og, steam_search, duckduckgo_img):
        if len(saved) >= max_imgs:
            break
        try:
            img_url = await strat(session, name)
        except Exception:
            continue
        if not img_url:
            continue
        data = await fetch_bin(session, img_url)
        if not data:
            continue
        ext = guess_ext(data, img_url)
        idx = len(saved) + 1
        dst = game_dir / f"{idx}.{ext}"
        dst.write_bytes(data)
        saved.append(dst)

    return [str(p.relative_to(ROOT)) for p in saved]


async def main(concurrency, max_imgs, limit):
    entries = [json.loads(l) for l in CONS.read_text().splitlines() if l.strip()]
    # only those without images OR with fewer than max_imgs on disk
    pending = []
    for e in entries:
        d = IMAGES / e["id"]
        existing = list(d.glob("*")) if d.exists() else []
        if len(existing) < max_imgs:
            pending.append(e)
    if limit:
        pending = pending[:limit]

    print(f"Pendentes: {len(pending)}/{len(entries)}", file=sys.stderr)

    sem = asyncio.Semaphore(concurrency)
    results = []

    async with aiohttp.ClientSession() as session:
        async def w(e):
            async with sem:
                paths = await process(session, e, max_imgs)
                results.append((e["id"], paths))
                if len(results) % 30 == 0:
                    print(f"  {len(results)}/{len(pending)}", file=sys.stderr)

        await asyncio.gather(*(w(e) for e in pending))

    id_paths = dict(results)
    for e in entries:
        if e["id"] in id_paths:
            e["imagens"] = id_paths[e["id"]]
    CONS.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n")

    total = sum(len(p) for _, p in results)
    with_any = sum(1 for _, p in results if p)
    print(f"Fallback: {with_any}/{len(pending)} agora com imagem · {total} imagens baixadas no fallback", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=12)
    ap.add_argument("--max-imgs", type=int, default=2)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    asyncio.run(main(args.concurrency, args.max_imgs, args.limit))
