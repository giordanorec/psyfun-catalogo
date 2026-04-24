#!/usr/bin/env python3
"""
Gera 3 HTMLs e 3 PDFs estilo revista gamer:
- TOP100.html / TOP100.pdf  — densa, 2-3 jogos por página
- TOP25.html  / TOP25.pdf   — espaçosa, 1 jogo por página
- FINALISTAS.html / FINALISTAS.pdf — full-page por jogo, texto analítico do MD

Usa WeasyPrint. Imagens são referenciadas por path absoluto.
"""
from __future__ import annotations
import json
import re
import sys
import html as html_mod
from pathlib import Path
from datetime import datetime

import markdown  # noqa
from weasyprint import HTML, CSS

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
SRC = ROOT / "exports" / "CONSOLIDADO.jsonl"
FINAL_MD = ROOT / "exports" / "FINALISTAS.md"
RELATORIO_MD = ROOT / "exports" / "RELATORIO_TECNICO.md"
CSS_PATH = ROOT / "scripts" / "magazine.css"
OUT_HTML = ROOT / "exports" / "print"
OUT_PDF = ROOT / "exports" / "pdfs"
OUT_HTML.mkdir(parents=True, exist_ok=True)
OUT_PDF.mkdir(parents=True, exist_ok=True)

DILEMA_NAMES = {
    "PD": "Prisoner's Dilemma", "PG": "Public Goods", "SH": "Stag Hunt",
    "UG": "Ultimatum", "DG": "Dictator", "SD": "Snowdrift",
    "TG": "Trust", "CG": "Commons", "CPG": "Coordination", "BG": "Bargaining",
}


def h(s: str) -> str:
    return html_mod.escape(str(s or ""))


def resolve_img(path: str) -> str:
    """Path absoluto pra WeasyPrint resolver."""
    if not path:
        return ""
    p = path.replace("../", "")
    full = ROOT / p
    return f"file://{full.resolve()}"


def score(e: dict) -> float:
    a = e.get("aderencia_psyfun", 0) or 0
    v = e.get("viabilidade_claude", 0) or 0
    d = e.get("dificuldade", 5) or 5
    return a * 2 + v - d * 0.5


def load_entries() -> list[dict]:
    entries = [json.loads(l) for l in SRC.read_text().splitlines() if l.strip()]
    for e in entries:
        e["_score"] = score(e)
    entries.sort(key=lambda x: x["_score"], reverse=True)
    return entries


# ==================== COVER ====================
def cover_html(title: str, sub: str, tag: str, count: int) -> str:
    hoje = datetime.today().strftime("%B %Y").upper()
    return f"""
<div class="cover">
  <span class="cover-tag">{h(tag)}</span>
  <div class="cover-content">
    <div>
      <div class="cover-label">PSYFUN RESEARCH · {hoje}</div>
      <h1 class="cover-title">{h(title)}</h1>
      <p class="cover-sub">{h(sub)}</p>
    </div>
    <div class="cover-meta">
      <strong>{count}</strong> JOGOS ANALISADOS · MODS · DILEMAS SOCIAIS · PSYFUN · UFPE / UNIVASF
    </div>
    <div class="cover-footer">
      catálogo multi-agente · dashboard em psyfun-jogos-research/exports/dashboard.html
    </div>
  </div>
</div>"""


# ==================== TOC ====================
def toc_html(entries: list[dict], title: str = "RANKING") -> str:
    items = []
    for i, e in enumerate(entries, 1):
        items.append(
            f'<li><span class="nome">{h(e["nome"])}</span>'
            f'<span class="score">{e["_score"]:.2f}</span></li>'
        )
    return f"""
<div class="toc">
  <h2>{h(title)}</h2>
  <ol>
    {"".join(items)}
  </ol>
</div>"""


# ==================== CARD ====================
def game_card(rank: int, e: dict, big: bool = False) -> str:
    imgs = e.get("imagens") or []
    cover_url = resolve_img(imgs[0]) if imgs else ""
    cover_style = f'style="background-image:url({cover_url})"' if cover_url else ""
    cover_class = "" if cover_url else "no-img"

    dilemas_raw = (e.get("dilemas_compativeis") or "").split("|")
    dilemas = [d.strip() for d in dilemas_raw if d.strip()]
    dilema_html = "".join(f'<span class="dilema" title="{DILEMA_NAMES.get(d,"")}">{d}</span>' for d in dilemas)

    badges = []
    if e.get("aderencia_psyfun") == 5 and e.get("viabilidade_claude") == 5:
        badges.append('<span class="game-badge editor-pick">EDITOR\'S PICK</span>')
    if e.get("esforco_horas") == "XS":
        badges.append('<span class="game-badge premium">QUICK START</span>')
    if rank <= 10:
        badges.append(f'<span class="game-badge">TOP {rank}</span>')
    badges_html = "".join(badges)

    example = h(e.get("exemplo_concreto") or "Não informado")
    reasoning = h(e.get("raciocinio_dificuldade") or "")
    popularidade = h(e.get("popularidade") or "-")

    meta_parts = []
    if e.get("ano_lancamento"): meta_parts.append(f"<strong>{e['ano_lancamento']}</strong>")
    if e.get("dev_publisher"): meta_parts.append(h(e["dev_publisher"]))
    if e.get("engine_tech"): meta_parts.append(h(e["engine_tech"]))
    if e.get("plataforma"): meta_parts.append(h(e["plataforma"].replace("|", " · ")))
    meta_line = " · ".join(meta_parts)

    links_html = ""
    for link in (e.get("links") or [])[:3]:
        try:
            from urllib.parse import urlparse
            dom = urlparse(link).hostname or link
            links_html += f'<a href="{h(link)}">{h(dom)}</a>'
        except Exception:
            pass

    big_cls = " big" if big else ""
    return f"""
<div class="game{big_cls}" data-nome="#{rank} {h(e['nome'])}">
  <div class="game-cover {cover_class}" {cover_style}>
    <div class="game-rank">#{rank:02d}</div>
    <div class="game-score">{e['_score']:.2f}</div>
    <div class="game-badges">{badges_html}</div>
  </div>
  <div class="game-body">
    <div class="game-name">{h(e['nome'])}</div>
    <div class="game-meta">{meta_line}</div>
    <div class="game-stats">
      <div class="stat"><div class="stat-label">Aderência</div><div class="stat-val aderencia">{e.get('aderencia_psyfun','?')}</div></div>
      <div class="stat"><div class="stat-label">Dificuldade</div><div class="stat-val dificuldade">{e.get('dificuldade','?')}</div></div>
      <div class="stat"><div class="stat-label">Viabilidade</div><div class="stat-val viabilidade">{e.get('viabilidade_claude','?')}</div></div>
      <div class="stat"><div class="stat-label">Esforço</div><div class="stat-val esforco">{h(e.get('esforco_horas','?'))}</div></div>
    </div>
    <div class="game-dilemas">{dilema_html}</div>
    <div class="game-example">{example}</div>
    { f'<div class="game-reasoning">{reasoning}</div>' if reasoning else ''}
    <div class="game-meta" style="margin-top:2mm"><strong>MÉTODO:</strong> {h(e.get('metodo_modificacao','-'))} · <strong>STATUS:</strong> {h(e.get('status_codigo','-'))} · <strong>TOS:</strong> {e.get('risco_tos','?')}/5</div>
    <div class="game-meta" style="margin-top:1mm"><strong>POP:</strong> {popularidade}</div>
    { f'<div class="game-links">{links_html}</div>' if links_html else '' }
  </div>
</div>"""


# ==================== FINALISTAS PAGE (baseada em markdown) ====================
def finalista_section(rank: int, e: dict, md_section: str) -> str:
    """Gera seção full-page do finalista — imagem de fundo + texto do MD."""
    imgs = e.get("imagens") or []
    cover_url = resolve_img(imgs[0]) if imgs else ""
    cover_style = f'style="background-image:url({cover_url})"' if cover_url else 'style="background:#1c2130"'

    tagline = e.get("exemplo_concreto") or ""

    # Converte o MD section pra HTML (remove cabeçalho principal, já está na hero)
    body_md = re.sub(r"^##\s+\d+\.\s+.*?\n", "", md_section, count=1, flags=re.M)
    body_html = markdown.markdown(body_md, extensions=["tables", "fenced_code"])

    return f"""
<div class="finalista" data-nome="#{rank:02d} {h(e['nome'])}">
  <div class="hero" {cover_style}>
    <div class="rank-huge">#{rank:02d}</div>
    <div class="hero-text">
      <div class="title-huge">{h(e['nome'])}</div>
      <div class="tagline">{h(tagline[:140])}</div>
    </div>
  </div>
  <div class="body">
    {body_html}
  </div>
</div>"""


# ==================== BUILDERS ====================
def build_top100(entries: list[dict]) -> Path:
    top = entries[:100]
    body = [cover_html("TOP 100", "Os 100 jogos melhor posicionados para virar instrumento de pesquisa em dilemas sociais.", "RANKING COMPLETO", len(entries))]
    body.append(toc_html(top, "TOP 100 — RANKING"))
    body.append('<h1 class="section new-page">Ranking · #1–#100</h1>')
    for i, e in enumerate(top, 1):
        body.append(game_card(i, e, big=(i <= 10)))
    return emit_html(body, "TOP100.html")


def build_top25(entries: list[dict]) -> Path:
    top = entries[:25]
    body = [cover_html("TOP 25", "Pré-seleção final: 25 candidatos para análise profunda.", "FINALISTAS", len(entries))]
    body.append(toc_html(top, "TOP 25 — FINALISTAS"))
    body.append('<h1 class="section new-page">Finalistas · #1–#25</h1>')
    for i, e in enumerate(top, 1):
        body.append(game_card(i, e, big=True))
    return emit_html(body, "TOP25.html")


def build_finalistas(entries: list[dict]) -> Path:
    top = entries[:25]
    md = FINAL_MD.read_text()

    # Separa preâmbulo + 25 seções + fechamento
    sections = re.split(r"(?=^##\s+\d+\.\s+)", md, flags=re.M)
    # sections[0] = preâmbulo
    # sections[1..25] = jogos 1..25
    # Procurar fechamento (## Próximos passos)
    preambulo = sections[0]
    game_sections = []
    closing = ""
    for s in sections[1:]:
        if re.match(r"^##\s+\d+\.", s):
            game_sections.append(s)
        else:
            closing += s

    # Detecta seção de fechamento dentro da última entrada de jogo (se necessário)
    if game_sections and "Próximos passos" in game_sections[-1]:
        m = re.search(r"(.*?)(##\s+Próximos.*)", game_sections[-1], re.S)
        if m:
            game_sections[-1] = m.group(1)
            closing = m.group(2) + closing

    body = [cover_html("FINALISTAS", "Análise profunda dos 25 jogos mais promissores. Plano concreto de modificação, mapeamento de dilemas, trade-offs e próximas ações.", "ANÁLISE EDITORIAL", len(entries))]

    # Preâmbulo como intro
    preamble_html = markdown.markdown(preambulo, extensions=["tables", "fenced_code"])
    body.append(f'<div class="closing">{preamble_html}</div>')

    body.append(toc_html(top, "25 FINALISTAS"))

    for i, e in enumerate(top, 1):
        section_md = game_sections[i - 1] if i - 1 < len(game_sections) else ""
        body.append(finalista_section(i, e, section_md))

    if closing:
        closing_html = markdown.markdown(closing, extensions=["tables", "fenced_code"])
        body.append(f'<div class="closing">{closing_html}</div>')

    return emit_html(body, "FINALISTAS.html")


def build_relatorio() -> Path:
    """Constrói RELATORIO.html a partir do RELATORIO_TECNICO.md."""
    md = RELATORIO_MD.read_text()
    # Remove título principal h1 (usamos capa custom) - a 1ª linha "# ..."
    md_body = re.sub(r"^#\s+[^\n]+\n", "", md, count=1)

    body_html = markdown.markdown(
        md_body,
        extensions=["tables", "fenced_code", "toc", "attr_list"],
    )

    # Capa do relatório
    cover = cover_html(
        "RELATÓRIO TÉCNICO",
        "Construção do catálogo PsyFun de jogos moddáveis — arquitetura, execução, resultados e próximos passos.",
        "DOCUMENTAÇÃO",
        1202,
    )

    body = [
        cover,
        f'<div class="report-body"><div class="report-content">{body_html}</div></div>',
    ]
    return emit_html(body, "RELATORIO.html")


def emit_html(parts: list[str], filename: str) -> Path:
    doc = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>PsyFun · {filename}</title>
  <link rel="stylesheet" href="file://{CSS_PATH.resolve()}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
{''.join(parts)}
</body>
</html>"""
    path = OUT_HTML / filename
    path.write_text(doc, encoding="utf-8")
    print(f"HTML: {path}", file=sys.stderr)
    return path


def render_pdf(html_path: Path) -> Path:
    pdf_name = html_path.stem + ".pdf"
    pdf_path = OUT_PDF / pdf_name
    print(f"  rendering PDF → {pdf_path}", file=sys.stderr)
    HTML(filename=str(html_path), base_url=str(ROOT)).write_pdf(
        str(pdf_path),
        stylesheets=[CSS(filename=str(CSS_PATH))],
    )
    print(f"  OK ({pdf_path.stat().st_size // 1024} KB)", file=sys.stderr)
    return pdf_path


def main():
    print("Loading entries...", file=sys.stderr)
    entries = load_entries()
    print(f"  {len(entries)} entries", file=sys.stderr)

    print("\n=== TOP100 ===", file=sys.stderr)
    html = build_top100(entries)
    render_pdf(html)

    print("\n=== TOP25 ===", file=sys.stderr)
    html = build_top25(entries)
    render_pdf(html)

    print("\n=== FINALISTAS ===", file=sys.stderr)
    html = build_finalistas(entries)
    render_pdf(html)

    print("\n=== RELATORIO ===", file=sys.stderr)
    html = build_relatorio()
    render_pdf(html)

    print("\nDone. Outputs:", file=sys.stderr)
    for p in sorted(OUT_PDF.glob("*.pdf")):
        print(f"  {p}  ({p.stat().st_size // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
