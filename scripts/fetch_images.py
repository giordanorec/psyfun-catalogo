#!/usr/bin/env python3
"""
Baixa imagens pra cada jogo em CONSOLIDADO.jsonl.

Estratégia de fontes (ordem de preferência):
1. URL Steam Store (apps/<id>) -> https://cdn.cloudflare.steamstatic.com/steam/apps/<id>/header.jpg
2. URL itch.io -> scrape OG:image
3. URL GitHub -> scrape repo OG:image + README images
4. URL Wikipedia -> scrape infobox image
5. Fallback: Google Images / DuckDuckGo Images

Cada jogo recebe até 4 imagens em images/<id>/<n>.{jpg,png,webp}.
JSONL é reescrito com campo `imagens: [...paths...]`.

Rodar com concorrência via asyncio + aiohttp.

Uso:
    python3 fetch_images.py [--limit N] [--concurrency C] [--skip-done]
"""
from __future__ import annotations
import argparse
import asyncio
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, quote

try:
    import aiohttp
except ImportError:
    print("pip install aiohttp", file=sys.stderr)
    sys.exit(1)

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
CONS = ROOT / "exports" / "CONSOLIDADO.jsonl"
IMAGES = ROOT / "images"
IMAGES.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/121 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept": "text/html,image/*,*/*;q=0.8"}
TIMEOUT = aiohttp.ClientTimeout(total=20, connect=8)


STEAM_APPID = re.compile(r"store\.steampowered\.com/app/(\d+)")
OG_IMG = re.compile(r'<meta[^>]*(?:property|name)=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', re.I)
TWITTER_IMG = re.compile(r'<meta[^>]*name=["\']twitter:image[^"\']*["\'][^>]*content=["\']([^"\']+)["\']', re.I)
ITCH_COVER = re.compile(r'<img[^>]*class=["\']game_cover[^"\']*["\'][^>]*src=["\']([^"\']+)["\']', re.I)
README_IMG_RE = re.compile(r'!\[[^\]]*\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp))\)', re.I)


def pick_url_type(url: str) -> str:
    """Classifica URL pra escolher estratégia."""
    p = urlparse(url)
    h = p.netloc.lower()
    if "steampowered.com" in h or "steamcommunity.com" in h:
        return "steam"
    if "itch.io" in h:
        return "itch"
    if "github.com" in h:
        return "github"
    if "wikipedia.org" in h:
        return "wikipedia"
    if "nexusmods.com" in h:
        return "nexus"
    if "mod.io" in h:
        return "modio"
    if "roblox.com" in h:
        return "roblox"
    return "other"


async def fetch_text(session, url: str) -> str | None:
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True) as r:
            if r.status != 200 or "html" not in r.headers.get("Content-Type", ""):
                return None
            return await r.text(errors="ignore")
    except Exception:
        return None


async def fetch_bin(session, url: str) -> bytes | None:
    try:
        async with session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True) as r:
            if r.status != 200:
                return None
            ct = r.headers.get("Content-Type", "")
            if "image" not in ct:
                return None
            data = await r.read()
            if len(data) < 2000:  # muito pequeno, provavelmente favicon
                return None
            if len(data) > 8 * 1024 * 1024:  # >8MB, ignora
                return None
            return data
    except Exception:
        return None


def guess_ext(data: bytes, url: str) -> str:
    if data.startswith(b"\x89PNG"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"GIF8"):
        return "gif"
    if data.startswith(b"RIFF") and b"WEBP" in data[:20]:
        return "webp"
    ext = Path(urlparse(url).path).suffix.lstrip(".").lower()
    return ext if ext in ("jpg", "jpeg", "png", "gif", "webp") else "jpg"


async def img_urls_steam(session, url: str) -> list[str]:
    urls = []
    m = STEAM_APPID.search(url)
    if m:
        appid = m.group(1)
        urls.append(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg")
        urls.append(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg")
        urls.append(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/library_hero.jpg")
        urls.append(f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/page_bg_raw.jpg")
    return urls


async def img_urls_from_html(html: str | None) -> list[str]:
    if not html:
        return []
    urls = []
    for rx in (OG_IMG, TWITTER_IMG, ITCH_COVER):
        for m in rx.finditer(html):
            u = m.group(1).strip()
            if u.startswith("//"):
                u = "https:" + u
            if u and u not in urls:
                urls.append(u)
    # Imagens em README / corpo
    for m in README_IMG_RE.finditer(html[:50000]):
        u = m.group(1).strip()
        if u and u.startswith("http") and u not in urls:
            urls.append(u)
    return urls[:6]


async def candidate_urls(session, links: list[str]) -> list[str]:
    """Gera lista ordenada de candidatas de URLs de imagem a partir dos links do jogo."""
    cands: list[str] = []
    for url in links[:5]:
        kind = pick_url_type(url)
        if kind == "steam":
            cands.extend(await img_urls_steam(session, url))
        elif kind in ("itch", "github", "wikipedia", "nexus", "modio", "roblox", "other"):
            html = await fetch_text(session, url)
            cands.extend(await img_urls_from_html(html))
    # dedup preservando ordem
    seen = set()
    out = []
    for u in cands:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


async def process_entry(session, entry: dict, max_imgs: int) -> list[str]:
    id_ = entry["id"]
    game_dir = IMAGES / id_
    game_dir.mkdir(exist_ok=True)
    existing = sorted(game_dir.glob("*"))
    if len(existing) >= max_imgs:
        return [str(p.relative_to(ROOT)) for p in existing[:max_imgs]]

    candidates = await candidate_urls(session, entry.get("links", []) or [])
    saved: list[Path] = list(existing)
    for img_url in candidates:
        if len(saved) >= max_imgs:
            break
        data = await fetch_bin(session, img_url)
        if not data:
            continue
        ext = guess_ext(data, img_url)
        idx = len(saved) + 1
        dst = game_dir / f"{idx}.{ext}"
        dst.write_bytes(data)
        saved.append(dst)

    return [str(p.relative_to(ROOT)) for p in saved]


async def main(limit: int | None, concurrency: int, max_imgs: int, skip_done: bool):
    entries = [json.loads(l) for l in CONS.read_text().splitlines() if l.strip()]
    if limit:
        entries = entries[:limit]
    if skip_done:
        entries = [e for e in entries if not (IMAGES / e["id"]).exists() or not list((IMAGES / e["id"]).iterdir())]

    sem = asyncio.Semaphore(concurrency)
    results: list[tuple[str, list[str]]] = []

    async with aiohttp.ClientSession() as session:
        async def worker(e):
            async with sem:
                paths = await process_entry(session, e, max_imgs)
                results.append((e["id"], paths))
                if len(results) % 20 == 0:
                    print(f"  {len(results)}/{len(entries)}", file=sys.stderr)

        await asyncio.gather(*(worker(e) for e in entries))

    # update CONSOLIDADO.jsonl com os paths
    id_to_paths = dict(results)
    all_entries = [json.loads(l) for l in CONS.read_text().splitlines() if l.strip()]
    for e in all_entries:
        if e["id"] in id_to_paths:
            e["imagens"] = id_to_paths[e["id"]]
    CONS.write_text("\n".join(json.dumps(e, ensure_ascii=False) for e in all_entries) + "\n")

    # estatísticas
    total_imgs = sum(len(p) for _, p in results)
    with_any = sum(1 for _, p in results if p)
    print(f"Processados: {len(results)} · Com pelo menos 1 imagem: {with_any} · Total imagens: {total_imgs}", file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--concurrency", type=int, default=20)
    ap.add_argument("--max-imgs", type=int, default=3)
    ap.add_argument("--skip-done", action="store_true")
    args = ap.parse_args()
    asyncio.run(main(args.limit, args.concurrency, args.max_imgs, args.skip_done))
