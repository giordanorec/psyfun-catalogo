#!/usr/bin/env python3
"""Build public/index.html (dashboard PsyFun v4.1) — chassis HTML enxuto +
CSS local (scripts/v4-styles.css) + dataset CONSOLIDADO.jsonl embedded
+ scripts/v4-app.js.

Roda: python scripts/build_v4.py

A revisão pós-feedback (v4.1) descartou o hero monumental editorial e a
serif display gigante. Resultado: cards são protagonistas, tipografia
comedida estilo plataforma de games (Steam/itch.io).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "public" / "data" / "CONSOLIDADO.jsonl"
APP_JS = ROOT / "scripts" / "v4-app.js"
CSS = ROOT / "scripts" / "v4-styles.css"
OUT = ROOT / "public" / "index.html"


def load_data(path: Path) -> list[dict]:
    games = []
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            games.append(json.loads(line))
        except json.JSONDecodeError as e:
            sys.exit(f"ERRO: JSON inválido em CONSOLIDADO.jsonl:{ln} — {e}")
    return games


def fmt_br(n: int) -> str:
    """1202 → '1.202' (pt-BR)."""
    return f"{n:,}".replace(",", ".")


def build_html(styles: str, data: list[dict], app_js: str) -> str:
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    n_total = fmt_br(len(data))

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PsyFun · Catálogo de jogos moddáveis para pesquisa em dilemas sociais</title>
<meta name="description" content="Catálogo curado de {len(data)} jogos moddáveis pra pesquisa em dilemas sociais. PsyFun Lab · CIn/UFPE × LDAPP/UNIVASF.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>{styles}</style>
</head>
<body>

<!-- ============================================================
     Header
     ============================================================ -->
<header class="app-header">
  <button class="mobile-menu" aria-label="Abrir filtros" id="mobileMenuBtn">
    <span class="lines"><span></span><span></span><span></span></span>
  </button>
  <a class="brand" href="#">
    <span class="brand-mark">PsyFun</span>
    <span class="brand-tag">v4 · catálogo</span>
  </a>
  <nav class="app-tabs" role="tablist" aria-label="Modos do dashboard">
    <button class="app-tab" role="tab" aria-current="true" data-tab="explorar">Explorar</button>
    <button class="app-tab" role="tab" data-tab="rankings">Rankings</button>
    <button class="app-tab" role="tab" data-tab="sobre">Sobre</button>
  </nav>
  <button class="cmd-trigger" id="cmdTrigger" aria-label="Abrir command palette">
    <span class="ico"></span>
    <span class="label">Buscar, filtrar, executar comando…</span>
    <span class="kbd-group"><span class="kbd">⌘</span><span class="kbd">K</span></span>
  </button>
  <div class="counter">
    <b><span id="counterFiltered">{n_total}</span><em> / <span id="counterTotal">{n_total}</span></em></b>
    <span>jogos filtrados</span>
  </div>
</header>

<!-- ============================================================
     Panel: Explorar
     ============================================================ -->
<section class="panel" data-active="true" data-panel="explorar">
<div class="app-body">

  <aside class="sidebar" id="sidebar" aria-label="Filtros">

    <div class="filter-section">
      <label class="filter-label">Busca textual</label>
      <div class="search-input">
        <span class="ico"></span>
        <input type="text" id="searchBoxInput" placeholder="nome, engine, tema…" aria-label="Busca textual">
      </div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Dilemas compatíveis <span class="count">· 10</span></label>
      <div class="chip-grid" id="dilemaChips">
        <button class="chip" type="button" aria-pressed="false" data-d="PD"  title="Prisoner's Dilemma">PD</button>
        <button class="chip" type="button" aria-pressed="false" data-d="PG"  title="Public Goods">PG</button>
        <button class="chip" type="button" aria-pressed="false" data-d="SH"  title="Stag Hunt">SH</button>
        <button class="chip" type="button" aria-pressed="false" data-d="UG"  title="Ultimatum">UG</button>
        <button class="chip" type="button" aria-pressed="false" data-d="DG"  title="Dictator">DG</button>
        <button class="chip" type="button" aria-pressed="false" data-d="SD"  title="Snowdrift">SD</button>
        <button class="chip" type="button" aria-pressed="false" data-d="TG"  title="Trust Game">TG</button>
        <button class="chip" type="button" aria-pressed="false" data-d="CG"  title="Commons">CG</button>
        <button class="chip" type="button" aria-pressed="false" data-d="CPG" title="Coordination">CPG</button>
        <button class="chip" type="button" aria-pressed="false" data-d="BG"  title="Bargaining">BG</button>
      </div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Thresholds</label>
      <div class="slider-group">
        <div class="slider" data-slider="aderencia">
          <span class="slider-label">Aderência ≥</span><span class="slider-value">1 / 5</span>
          <div class="slider-track"><div class="slider-fill" style="width:0%"></div><div class="slider-thumb" style="left:0%"></div></div>
        </div>
        <div class="slider" data-slider="viabilidade">
          <span class="slider-label">Viabilidade ≥</span><span class="slider-value">1 / 5</span>
          <div class="slider-track"><div class="slider-fill" style="width:0%"></div><div class="slider-thumb" style="left:0%"></div></div>
        </div>
        <div class="slider" data-slider="dificuldade">
          <span class="slider-label">Dificuldade ≤</span><span class="slider-value">5 / 5</span>
          <div class="slider-track"><div class="slider-fill" style="width:100%"></div><div class="slider-thumb" style="left:100%"></div></div>
        </div>
        <div class="slider" data-slider="tos">
          <span class="slider-label">Risco ToS ≤</span><span class="slider-value">5 / 5</span>
          <div class="slider-track"><div class="slider-fill" style="width:100%"></div><div class="slider-thumb" style="left:100%"></div></div>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Método de modificação</label>
      <div class="chip-grid" id="chipsMetodo"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Status do código</label>
      <div class="chip-grid" id="chipsStatus"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Esforço estimado</label>
      <div class="chip-grid" id="chipsEsforco"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Visualização</label>
      <div class="chip-grid" id="chipsVisualizacao"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Modo de jogo</label>
      <div class="chip-grid" id="chipsModo"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Gênero</label>
      <div class="chip-grid" id="chipsGenero"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Tema</label>
      <div class="chip-grid" id="chipsTema"></div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Ritmo · Duração · Licença</label>
      <div class="select-stack">
        <button type="button" class="select" data-select="ritmo" data-value="">
          <span>Ritmo</span><span class="select-value">qualquer</span>
        </button>
        <button type="button" class="select" data-select="duracao" data-value="">
          <span>Duração</span><span class="select-value">qualquer</span>
        </button>
        <button type="button" class="select" data-select="licenca" data-value="">
          <span>Licença</span><span class="select-value">qualquer</span>
        </button>
      </div>
    </div>

    <div class="filter-section">
      <label class="filter-label">Flags</label>
      <div role="checkbox" aria-checked="false" class="toggle-row" tabindex="0" data-toggle="img">
        <span>Só com imagem</span>
        <span class="toggle"></span>
      </div>
      <div role="checkbox" aria-checked="false" class="toggle-row" tabindex="0" data-toggle="video">
        <span>Só com vídeo</span>
        <span class="toggle"></span>
      </div>
    </div>

  </aside>

  <main class="main">

    <!-- status bar enxuta no topo (substitui o hero) -->
    <div class="status-bar" id="summaryBar"></div>

    <section class="catalog">
      <div class="catalog-head">
        <h2 id="catalogHeading"><span class="n">{n_total}</span> jogos</h2>
        <div class="sort-row">
          <span class="lbl">Ordenar</span>
          <button data-sort="score"        aria-current="true">Score ↓</button>
          <button data-sort="aderencia"    aria-current="false">Aderência</button>
          <button data-sort="viabilidade"  aria-current="false">Viabilidade</button>
          <button data-sort="popularidade" aria-current="false">Popularidade</button>
          <button data-sort="az"           aria-current="false">A–Z</button>
        </div>
      </div>
      <div class="card-grid" id="cardGrid"></div>
    </section>

  </main>
</div>
</section>

<!-- ============================================================
     Panel: Rankings
     ============================================================ -->
<section class="panel" data-panel="rankings">
  <div class="rankings-head">
    <p class="breadcrumb">
      <b>Rankings</b><span class="sep">·</span><span id="rkBread1">Categoria</span><span class="sep">·</span><span id="rkBread2">Aderência ↓</span><span class="sep">·</span><span id="rkBread3">Top 25</span>
    </p>
    <h1 class="rankings-h1">Top jogos do catálogo, ordenados por <em>dimensão escolhida</em>.</h1>
    <div class="rankings-controls">
      <div class="segmented" role="tablist">
        <button role="tab" aria-current="true"  data-rktab="categoria">Categoria</button>
        <button role="tab" aria-current="false" data-rktab="builder">Builder</button>
      </div>
      <div class="sort-row">
        <span class="lbl">Top</span>
        <button data-topn="10"  aria-current="false">10</button>
        <button data-topn="25"  aria-current="true">25</button>
        <button data-topn="50"  aria-current="false">50</button>
        <button data-topn="100" aria-current="false">100</button>
      </div>
    </div>
  </div>

  <div class="rk-sub" data-rksub="categoria">
    <div class="dim-grid" id="dimGrid">
      <button class="dim" type="button" aria-pressed="false" data-dim="score"><span class="gly">★</span><span class="name">Score composto</span><span class="sub">soma ponderada padrão</span></button>
      <button class="dim" type="button" aria-pressed="true"  data-dim="aderencia"><span class="gly">🧠</span><span class="name">Aderência PsyFun</span><span class="sub">fit com paradigmas · maior é melhor</span></button>
      <button class="dim" type="button" aria-pressed="false" data-dim="viabilidade"><span class="gly">🤖</span><span class="name">Viabilidade Claude</span><span class="sub">facilidade de mod por LLM</span></button>
      <button class="dim" type="button" aria-pressed="false" data-dim="dificuldade"><span class="gly">⚙️</span><span class="name">Dificuldade ↓</span><span class="sub">menor é melhor</span></button>
      <button class="dim" type="button" aria-pressed="false" data-dim="esforco"><span class="gly">⏱️</span><span class="name">Esforço ↓</span><span class="sub">XS &gt; S &gt; M &gt; L &gt; XL</span></button>
      <button class="dim" type="button" aria-pressed="false" data-dim="tos"><span class="gly">⚖️</span><span class="name">Risco ToS ↓</span><span class="sub">menor é mais seguro</span></button>
      <button class="dim" type="button" aria-pressed="false" data-dim="popularidade"><span class="gly">🔥</span><span class="name">Popularidade</span><span class="sub">tração orgânica</span></button>
      <button class="dim" type="button" aria-pressed="false" data-dim="qualidade"><span class="gly">🎨</span><span class="name">Qualidade produção</span><span class="sub">polish, arte, UX</span></button>
    </div>
    <div class="ranked-list" id="rankedList"></div>
  </div>

  <div class="rk-sub" data-rksub="builder" style="display:none">
    <div class="builder">
      <aside class="builder-panel">
        <h3>Builder de score</h3>
        <p class="lead">Atribua peso 0–5 a cada dimensão. A fórmula gera um ranking custom em tempo real.</p>
        <div class="weight-stack" id="weightStack">
          <div class="weight" data-w="aderencia"><span class="gly">🧠</span><span class="name">Aderência PsyFun<em>+ peso</em></span><span class="v">3</span>
            <div class="slider-track"><div class="slider-fill" style="width:60%"></div><div class="slider-thumb" style="left:60%"></div></div>
          </div>
          <div class="weight" data-w="viabilidade"><span class="gly">🤖</span><span class="name">Viabilidade Claude<em>+ peso</em></span><span class="v">2</span>
            <div class="slider-track"><div class="slider-fill" style="width:40%"></div><div class="slider-thumb" style="left:40%"></div></div>
          </div>
          <div class="weight" data-w="dificuldade"><span class="gly">⚙️</span><span class="name">Dificuldade<em>− peso (inverso)</em></span><span class="v">1</span>
            <div class="slider-track"><div class="slider-fill" style="width:20%"></div><div class="slider-thumb" style="left:20%"></div></div>
          </div>
          <div class="weight" data-w="tos"><span class="gly">⚖️</span><span class="name">Risco ToS<em>− peso (inverso)</em></span><span class="v">2</span>
            <div class="slider-track"><div class="slider-fill" style="width:40%"></div><div class="slider-thumb" style="left:40%"></div></div>
          </div>
          <div class="weight" data-w="popularidade"><span class="gly">🔥</span><span class="name">Popularidade<em>+ peso</em></span><span class="v">1</span>
            <div class="slider-track"><div class="slider-fill" style="width:20%"></div><div class="slider-thumb" style="left:20%"></div></div>
          </div>
          <div class="weight" data-w="qualidade"><span class="gly">🎨</span><span class="name">Qualidade<em>+ peso</em></span><span class="v">1</span>
            <div class="slider-track"><div class="slider-fill" style="width:20%"></div><div class="slider-thumb" style="left:20%"></div></div>
          </div>
        </div>
        <div class="formula" id="builderFormula">
          <span class="lbl">Fórmula resultante</span>
          <b>score</b> = <span class="pos">🧠×3</span> + <span class="pos">🤖×2</span> <span class="neg">− ⚙️×1</span> <span class="neg">− ⚖️×2</span> + <span class="pos">🔥×1</span> + <span class="pos">🎨×1</span>
        </div>
      </aside>
      <div class="builder-results">
        <div class="catalog-head" style="margin-bottom:18px">
          <h2 id="builderHeading"><span class="n">25</span> resultados <span class="muted-tag">peso custom</span></h2>
        </div>
        <div class="ranked-list" id="builderList" style="padding:0"></div>
      </div>
    </div>
  </div>
</section>

<!-- ============================================================
     Panel: Sobre
     ============================================================ -->
<section class="panel" data-panel="sobre">
  <div class="sobre">
    <p class="breadcrumb"><b>Sobre</b><span class="sep">·</span>Metodologia</p>
    <h1>PsyFun v4 indexa jogos moddáveis pelo <em>fit empírico</em> com paradigmas de dilemas sociais.</h1>
    <p>
      Curadoria do <strong style="color:var(--fg)">PsyFun Lab</strong> — CIn/UFPE × LDAPP/UNIVASF · 2026.
      Cada um dos {n_total} jogos é avaliado em 8 dimensões (qualidade · aderência · viabilidade · dificuldade · esforço · ToS · popularidade · score composto)
      por revisores treinados, com checagem cruzada via Claude Code para reprodutibilidade.
    </p>
    <div class="meta-block">
      <strong>vocabulário controlado:</strong> <a href="https://github.com/giordanorec/psyfun-catalogo/blob/main/meta/VOCABULARIO.md" target="_blank" rel="noopener">meta/VOCABULARIO.md</a><br>
      <strong>repo:</strong> <a href="https://github.com/giordanorec/psyfun-catalogo" target="_blank" rel="noopener">github.com/giordanorec/psyfun-catalogo</a><br>
      <strong>contato:</strong> <a href="mailto:grec@cin.ufpe.br">grec@cin.ufpe.br</a>
    </div>
  </div>
</section>

<!-- ============================================================
     Modal de detalhe
     ============================================================ -->
<div class="modal-backdrop" id="modalBackdrop" role="dialog" aria-modal="true" aria-labelledby="modalTitle">
  <div class="modal" id="modal">
    <div class="modal-header">
      <div class="nav">
        <button type="button" aria-label="Jogo anterior" id="modalPrev">←</button>
        <button type="button" aria-label="Próximo jogo" id="modalNext">→</button>
        <span class="pos">Jogo <b id="modalPos">1</b> de <b id="modalTotal">1</b></span>
      </div>
      <button class="modal-close" type="button" id="modalClose">Fechar <span class="kbd">esc</span></button>
    </div>

    <div class="modal-video">
      <div class="placeholder"><span>—</span></div>
    </div>

    <div class="modal-body">
      <div>
        <p class="modal-meta" id="modalMeta"></p>
        <h2 class="modal-h1" id="modalTitle"></h2>
        <div class="modal-plat-row" id="modalPlatRow"></div>
        <p class="modal-desc" id="modalDesc"></p>
        <blockquote class="modal-quote" id="modalQuote">
          <span class="lbl">Exemplo concreto</span>
          <span id="modalQuoteText"></span>
        </blockquote>
      </div>
      <dl class="dl" id="modalDL"></dl>
    </div>

    <div class="modal-gallery" id="modalGallery"></div>
    <div class="modal-links" id="modalLinks"></div>

    <div class="modal-footer">
      <span><span class="kbd">←</span><span class="kbd">→</span> navegar</span>
      <span><span class="kbd">↵</span> abrir link externo</span>
      <span><span class="kbd">esc</span> fechar</span>
    </div>
  </div>
</div>

<!-- ============================================================
     Command Palette ⌘K
     ============================================================ -->
<div class="palette-backdrop" id="paletteBackdrop" role="dialog" aria-modal="true" aria-label="Command palette">
  <div class="palette">
    <div class="palette-search">
      <span class="ico"></span>
      <input type="text" id="paletteInput" placeholder="Buscar jogos, executar comandos…" autocomplete="off">
      <span class="kbd">esc</span>
    </div>
    <div class="palette-body" id="paletteBody"></div>
    <div class="palette-foot">
      <span><span class="kbd">↑</span><span class="kbd">↓</span> navegar</span>
      <span><span class="kbd">↵</span> selecionar</span>
      <span><span class="kbd">⌘</span><span class="kbd">K</span> alternar</span>
      <span><span class="kbd">esc</span> fechar</span>
    </div>
  </div>
</div>

<!-- ============================================================
     Dataset embedded
     ============================================================ -->
<script id="data" type="application/json">{data_json}</script>

<!-- ============================================================
     App
     ============================================================ -->
<script>{app_js}</script>

</body>
</html>
"""


def main() -> None:
    if not DATA.exists():
        sys.exit(f"ERRO: {DATA} não encontrado.")
    if not APP_JS.exists():
        sys.exit(f"ERRO: {APP_JS} não encontrado.")
    if not CSS.exists():
        sys.exit(f"ERRO: {CSS} não encontrado.")

    print(f"→ lendo CSS local: {CSS.relative_to(ROOT)}")
    styles = CSS.read_text(encoding="utf-8")
    print(f"  CSS: {len(styles):,} chars")

    print(f"→ lendo dataset: {DATA.relative_to(ROOT)}")
    data = load_data(DATA)
    print(f"  jogos: {fmt_br(len(data))}")

    print(f"→ lendo app js: {APP_JS.relative_to(ROOT)}")
    app_js = APP_JS.read_text(encoding="utf-8")
    print(f"  JS: {len(app_js):,} chars")

    html = build_html(styles, data, app_js)
    OUT.write_text(html, encoding="utf-8")
    print(f"→ escrito: {OUT.relative_to(ROOT)}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
