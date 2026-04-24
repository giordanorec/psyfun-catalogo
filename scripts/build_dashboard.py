#!/usr/bin/env python3
"""
Gera exports/dashboard.html — v3: duas abas (Explorar / Rankings),
teclado completo, ícones visuais, multiselect chips, embed de vídeos.

Fonte: CONSOLIDADO.jsonl com campos opcionais:
  video_youtube_id, video_thumbnail, video_title (coletados por fetch_videos.py)
"""
import json
from pathlib import Path
import sys

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
SRC = ROOT / "exports" / "CONSOLIDADO.jsonl"
DST = ROOT / "exports" / "dashboard.html"


def main() -> int:
    if not SRC.exists():
        print(f"Falta: {SRC}", file=sys.stderr)
        return 1

    entries = []
    with SRC.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            e["imagens"] = ["../" + p for p in (e.get("imagens") or [])]
            entries.append(e)

    for e in entries:
        a = e.get("aderencia_psyfun", 0) or 0
        v = e.get("viabilidade_claude", 0) or 0
        d = e.get("dificuldade", 5) or 5
        e["score"] = round(a * 2 + v - d * 0.5, 2)

    data_json = json.dumps(entries, ensure_ascii=False)
    n_with_video = sum(1 for e in entries if e.get("video_youtube_id"))
    print(f"{len(entries)} jogos · {n_with_video} com vídeo", file=sys.stderr)

    html_content = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PsyFun — catálogo de jogos moddáveis</title>
<style>
:root {
  --bg: #0b0d12;
  --bg-soft: #151922;
  --bg-elev: #1c2130;
  --border: #2a3142;
  --fg: #e6e9ef;
  --fg-muted: #8b94a8;
  --accent: #ff9f43;
  --accent-2: #4ade80;
  --red: #f87171;
  --blue: #60a5fa;
  --violet: #a78bfa;
  --gold: #fbbf24;
}
* { box-sizing: border-box; }
html { font-size: 16px; }
body {
  margin: 0;
  font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--fg); line-height: 1.45;
  font-size: 15px;
}

header {
  padding: 14px 22px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 24px;
  background: var(--bg-soft);
  position: sticky; top: 0; z-index: 10;
}
header h1 { margin: 0; font-size: 19px; font-weight: 800; letter-spacing: .2px; flex-shrink: 0; }

nav.tabs {
  display: flex; gap: 4px;
  margin-left: 8px;
}
nav.tabs button {
  background: transparent; border: 0; color: var(--fg-muted);
  padding: 8px 16px; border-radius: 6px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all .15s;
}
nav.tabs button:hover { color: var(--fg); background: var(--bg-elev); }
nav.tabs button.active { color: var(--accent); background: var(--bg-elev); }

header .counters {
  color: var(--fg-muted); font-size: 14px;
  margin-left: auto;
  transition: color .25s;
}
header .counters strong { color: var(--accent); font-weight: 700; font-size: 16px; }
header .counters.pulse strong {
  color: #ffd166; text-shadow: 0 0 10px rgba(255,159,67,0.8);
}

.layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 0;
  min-height: calc(100vh - 62px);
}

aside {
  background: var(--bg-soft); border-right: 1px solid var(--border);
  padding: 20px;
  overflow-y: auto; max-height: calc(100vh - 62px);
  position: sticky; top: 62px;
}
aside h3 {
  font-size: 13px; text-transform: uppercase; letter-spacing: 1px;
  color: var(--fg-muted); margin: 22px 0 8px;
  display: flex; align-items: center; gap: 6px; font-weight: 700;
}
aside h3:first-of-type { margin-top: 0; }
.info-i {
  display: inline-flex; align-items: center; justify-content: center;
  width: 16px; height: 16px; border-radius: 50%;
  background: var(--bg-elev); color: var(--fg-muted);
  font-size: 10px; font-weight: 700; cursor: help; font-style: normal;
  transition: background .2s, color .2s;
}
.info-i:hover { background: var(--accent); color: #1a1000; }

input[type=search], select {
  width: 100%; padding: 10px 12px;
  background: var(--bg-elev);
  border: 1px solid var(--border); color: var(--fg);
  border-radius: 7px;
  font-size: 15px; outline: none;
}
input[type=search]:focus, select:focus { border-color: var(--accent); }

.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  padding: 5px 11px; border: 1px solid var(--border); background: transparent;
  color: var(--fg-muted); border-radius: 999px; cursor: pointer;
  font-size: 13px; user-select: none;
  transition: all .15s;
  white-space: nowrap;
}
.chip:hover { border-color: var(--accent); color: var(--fg); }
.chip.active {
  background: var(--accent); color: #1a1000;
  border-color: var(--accent); font-weight: 600;
}

.range-row {
  display: flex; align-items: center; gap: 10px; margin: 7px 0;
}
.range-row label {
  min-width: 130px; font-size: 13px; color: var(--fg-muted); cursor: help;
}
.range-row input[type=range] { flex: 1; accent-color: var(--accent); }
.range-row .val {
  min-width: 26px; text-align: right;
  font-size: 14px; color: var(--fg); font-weight: 600;
}

.toggle {
  display: flex; align-items: center; gap: 8px; margin: 10px 0;
  font-size: 14px; cursor: pointer;
}
.toggle input { accent-color: var(--accent); }

/* SIDEBAR Rankings subtabs */
nav.subtabs {
  display: flex; gap: 2px;
  background: var(--bg-elev); padding: 3px; border-radius: 7px;
  margin-bottom: 12px;
}
nav.subtabs button {
  flex: 1; background: transparent; border: 0;
  color: var(--fg-muted); padding: 8px 10px;
  border-radius: 5px;
  font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all .15s;
}
nav.subtabs button.active {
  background: var(--accent); color: #1a1000;
}

.weight-row {
  display: grid; grid-template-columns: 120px 1fr 32px;
  align-items: center; gap: 10px;
  margin: 7px 0; font-size: 13px;
}
.weight-row label { color: var(--fg); font-weight: 500; }
.weight-row input[type=range] { accent-color: var(--accent); }
.weight-row .wval {
  font-family: ui-monospace, monospace; color: var(--accent);
  font-weight: 700; text-align: right;
}

main { padding: 22px; overflow-y: auto; }
#stats {
  color: var(--fg-muted); font-size: 14px; margin-bottom: 14px;
  transition: color .25s;
}
#stats.pulse { color: var(--accent); }
#stats strong { color: var(--fg); }

#grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

/* ============ CARD ============ */
.card {
  background: var(--bg-soft); border: 1px solid var(--border);
  border-radius: 10px; overflow: hidden;
  display: flex; flex-direction: column;
  transition: border-color .15s, transform .12s, box-shadow .15s;
  cursor: pointer; position: relative;
  outline: none;
  animation: fadeIn .25s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 2px 8px rgba(255,159,67,0.15);
}
.card:focus-visible {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(255,159,67,0.5);
  transform: translateY(-2px);
}

.card .cover {
  aspect-ratio: 16/9;
  background: var(--bg-elev) center/cover no-repeat;
  position: relative;
}
.card .cover.no-img {
  display: flex; align-items: center; justify-content: center;
  color: var(--fg-muted); font-size: 13px;
}
.card .cover.has-video::before {
  content: "▶";
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 54px; height: 54px;
  background: rgba(255,0,0,0.85); color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; padding-left: 4px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.6);
  z-index: 1;
  transition: transform .15s;
}
.card:hover .cover.has-video::before {
  transform: translate(-50%, -50%) scale(1.1);
  background: rgba(255,30,30,0.95);
}
.card .cover .score-badge {
  position: absolute; top: 8px; right: 8px;
  background: rgba(255,159,67,.95); color: #1a1000;
  padding: 3px 9px; border-radius: 5px;
  font-weight: 700; font-size: 14px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  z-index: 2;
}
.card .cover .platforms {
  position: absolute; bottom: 8px; left: 8px;
  display: flex; flex-wrap: wrap; gap: 3px; max-width: 80%;
  z-index: 2;
}

.pbadge {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 2px 7px; font-size: 10.5px; font-weight: 700;
  border-radius: 3px;
  font-family: ui-monospace, 'JetBrains Mono', monospace;
  letter-spacing: 0.3px; line-height: 1.15;
  box-shadow: 0 1px 3px rgba(0,0,0,0.4);
}
.pbadge.web { background: #1e40af; color: #fff; }
.pbadge.win { background: #0078d4; color: #fff; }
.pbadge.mac { background: #555; color: #fff; }
.pbadge.lin { background: #1a1a1a; color: #ff9f43; }
.pbadge.and { background: #3ddc84; color: #0a3318; }
.pbadge.ios { background: #e5e5ea; color: #000; }
.pbadge.sw  { background: #e60012; color: #fff; }
.pbadge.ps  { background: #0070cc; color: #fff; }
.pbadge.xb  { background: #107c10; color: #fff; }
.pbadge.vr  { background: #7c3aed; color: #fff; }
.pbadge.all { background: #ff9f43; color: #1a1000; }
.pbadge.unk { background: #333; color: #888; }

.card .body {
  padding: 12px 15px 10px; flex: 1;
  display: flex; flex-direction: column; gap: 6px;
}
.card .title {
  font-weight: 700; font-size: 17px;
  color: var(--fg); line-height: 1.2;
}
.card .sub {
  font-size: 12.5px; color: var(--fg-muted);
}
.card .desc {
  font-size: 13px; color: #c7cbd3; line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 2px;
}

.card .metrics {
  display: flex; flex-wrap: wrap; gap: 6px;
  margin-top: 4px;
}
.metric {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 8px;
  background: var(--bg-elev);
  border-radius: 4px;
  font-size: 12px;
  font-family: ui-monospace, monospace;
  font-weight: 600;
}
.metric .ico { font-size: 13px; }
.metric .v { color: var(--fg); font-weight: 700; }
.metric.ader { border-left: 2px solid var(--accent-2); }
.metric.ader .v { color: var(--accent-2); }
.metric.dif { border-left: 2px solid var(--red); }
.metric.dif .v { color: var(--red); }
.metric.viab { border-left: 2px solid var(--blue); }
.metric.viab .v { color: var(--blue); }
.metric.esf { border-left: 2px solid var(--accent); }
.metric.esf .v { color: var(--accent); }
.metric.pop { border-left: 2px solid var(--gold); }
.metric.pop .v { color: var(--gold); }
.metric.tos { border-left: 2px solid var(--violet); }
.metric.tos .v { color: var(--violet); }
.metric.qual { border-left: 2px solid #ec4899; }
.metric.qual .v { color: #ec4899; }

.card .dilemas { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 2px; }
.card .dilemas span {
  background: rgba(96,165,250,.18); color: var(--blue);
  padding: 2px 7px; border-radius: 3px;
  font-size: 11px; font-weight: 700;
  font-family: ui-monospace, monospace;
}

.card .footer {
  padding: 8px 15px;
  color: var(--accent); font-size: 12px; font-weight: 600;
  text-align: right;
  border-top: 1px solid var(--border);
  background: linear-gradient(to right, transparent 0%, rgba(255,159,67,0.04) 100%);
  transition: all .15s;
}
.card:hover .footer {
  background: linear-gradient(to right, rgba(255,159,67,0.08) 0%, rgba(255,159,67,0.18) 100%);
  color: #ffd166;
}

/* ============ MODAL ============ */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.75);
  display: none; z-index: 20;
  align-items: flex-start; justify-content: center;
  padding: 40px 20px;
  overflow-y: auto;
}
.modal-backdrop.open { display: flex; animation: backdropIn .15s ease-out; }
@keyframes backdropIn { from { opacity: 0; } to { opacity: 1; } }

.modal {
  background: var(--bg-soft); border-radius: 12px;
  max-width: 960px; width: 100%; max-height: calc(100vh - 80px);
  overflow-y: auto; border: 1px solid var(--border);
  animation: modalIn .2s ease-out;
}
@keyframes modalIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

.modal header {
  position: sticky; top: 0; padding: 14px 22px;
  border-bottom: 1px solid var(--border); background: var(--bg-soft);
  display: flex; justify-content: space-between; align-items: center;
  gap: 16px; z-index: 2;
}
.modal header h2 { margin: 0; font-size: 20px; }
.modal header .nav-hint {
  font-size: 12px; color: var(--fg-muted);
  font-family: ui-monospace, monospace;
}
.modal header .nav-hint kbd {
  background: var(--bg-elev); border: 1px solid var(--border);
  padding: 2px 6px; border-radius: 3px; font-size: 11px;
  margin: 0 2px;
}

.modal .body { padding: 22px; }
.modal .video-container {
  position: relative; width: 100%;
  aspect-ratio: 16/9;
  background: #000; border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}
.modal .video-container iframe {
  position: absolute; inset: 0;
  width: 100%; height: 100%; border: 0;
}

.modal .gallery {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 8px; margin: 16px 0;
}
.modal .gallery img { width: 100%; border-radius: 6px; }

.modal dl {
  display: grid; grid-template-columns: 170px 1fr;
  gap: 10px 18px; font-size: 14px;
}
.modal dt { color: var(--fg-muted); font-weight: 500; }
.modal dd { margin: 0; color: var(--fg); }
.modal .close {
  background: transparent; border: 0; color: var(--fg);
  font-size: 28px; cursor: pointer; line-height: 1;
  padding: 0 8px;
}
.modal .links a { color: var(--blue); margin-right: 14px; }

/* ============ RANKINGS subtabs ============ */
.sidebar-rankings .rank-meta {
  padding: 10px 12px;
  background: var(--bg-elev);
  border-left: 3px solid var(--accent);
  border-radius: 4px;
  font-size: 13px; line-height: 1.5;
  margin-bottom: 14px;
  color: var(--fg-muted);
}
.sidebar-rankings .rank-meta strong { color: var(--fg); }

/* ============ BREADCRUMBS ============ */
.mode-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px;
  background: var(--bg-elev);
  border-left: 3px solid var(--accent);
  border-radius: 4px;
  font-size: 12px;
  margin-right: 10px;
  color: var(--fg);
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  aside { position: static; max-height: none; }
  header { flex-wrap: wrap; gap: 10px; }
  header .counters { margin-left: 0; width: 100%; order: 3; }
}
</style>
</head>
<body>

<header>
  <h1>🎮 PsyFun</h1>
  <nav class="tabs">
    <button class="active" data-tab="explore" title="Filtra o catálogo por critérios (busca, dilemas, dificuldade, etc)">🔍 Explorar</button>
    <button data-tab="rankings" title="Ordena os jogos por uma dimensão específica ou combinação ponderada">🏆 Rankings</button>
  </nav>
  <div class="counters" id="counters"><strong id="count-visible">0</strong> / <strong id="count-total">0</strong></div>
</header>

<div class="layout">

  <!-- ====== SIDEBAR: EXPLORE ====== -->
  <aside class="sidebar-explore" id="sidebar-explore">
    <h3>Busca <i class="info-i" title="Procura em nome, gênero, engine, developer, observações, descrição">i</i></h3>
    <input type="search" id="q" placeholder="nome, gênero, engine…">

    <h3>Dilemas compatíveis <i class="info-i" title="Mostra apenas jogos que podem simular ao menos um dos dilemas selecionados (operador OR)">i</i></h3>
    <div class="chips" id="chips-dilemas"></div>

    <h3>Filtros numéricos <i class="info-i" title="Sliders cortam o catálogo em tempo real. Todos combinados em AND.">i</i></h3>
    <div class="range-row" title="Quão natural é enxertar cooperar/trair no jogo (1=alienígena, 5=já é PD-like)">
      <label>🧠 Aderência ≥</label>
      <input type="range" min="1" max="5" value="1" id="min-aderencia">
      <span class="val" id="val-aderencia">1</span>
    </div>
    <div class="range-row" title="Quão bem Claude Code consegue fazer a modificação sozinho (1=humano necessário, 5=autônomo)">
      <label>🤖 Viabilidade ≥</label>
      <input type="range" min="1" max="5" value="1" id="min-viabilidade">
      <span class="val" id="val-viabilidade">1</span>
    </div>
    <div class="range-row" title="Complexidade técnica (1=editor visual, 5=reverse engineering)">
      <label>⚙️ Dificuldade ≤</label>
      <input type="range" min="1" max="5" value="5" id="max-dificuldade">
      <span class="val" id="val-dificuldade">5</span>
    </div>
    <div class="range-row" title="Risco de violar termos de serviço (1=zero, 5=DMCA/banimento)">
      <label>⚖️ Risco ToS ≤</label>
      <input type="range" min="1" max="5" value="5" id="max-risco">
      <span class="val" id="val-risco">5</span>
    </div>

    <h3>Método de modificação <i class="info-i" title="Marque quantos quiser — operador OR">i</i></h3>
    <div class="chips" id="chips-metodo"></div>

    <h3>Status do código <i class="info-i" title="Open-source, source-available, SDK oficial, etc — OR entre selecionados">i</i></h3>
    <div class="chips" id="chips-status"></div>

    <h3>Esforço estimado <i class="info-i" title="Horas humanas-equivalentes para primeiro piloto">i</i></h3>
    <div class="chips" id="chips-esforco"></div>

    <h3>Gênero <i class="info-i" title="Tags de gênero típicas (action, RPG, strategy...) — múltiplos valores = OR">i</i></h3>
    <div class="chips" id="chips-genero"></div>

    <h3>Visualização <i class="info-i" title="2D, 3D, isométrico, pixel art, first-person, etc — múltiplos valores = OR">i</i></h3>
    <div class="chips" id="chips-visualizacao"></div>

    <h3>Modo de jogo <i class="info-i" title="Single-player, coop, PvP, multiplayer local ou online, MMO">i</i></h3>
    <div class="chips" id="chips-modo"></div>

    <h3>Ritmo <i class="info-i" title="Real-time, turn-based, async, tick-based — escolha um">i</i></h3>
    <select id="sel-ritmo">
      <option value="">— qualquer —</option>
    </select>

    <h3>Duração <i class="info-i" title="Session (partida rápida), campaign (narrativa), endless (mundo persistente / sandbox)">i</i></h3>
    <select id="sel-duracao">
      <option value="">— qualquer —</option>
    </select>

    <h3>Licença <i class="info-i" title="Tipo de licença/disponibilidade do código">i</i></h3>
    <select id="sel-licenca">
      <option value="">— qualquer —</option>
    </select>

    <h3>Tema <i class="info-i" title="Fantasy, sci-fi, militar, horror, etc — múltiplos valores = OR">i</i></h3>
    <div class="chips" id="chips-tema"></div>

    <h3>Opções</h3>
    <label class="toggle" title="Esconde jogos sem capa baixada"><input type="checkbox" id="only-with-img">Apenas com imagem</label>
    <label class="toggle" title="Mostra apenas jogos com vídeo de gameplay coletado"><input type="checkbox" id="only-with-video">Apenas com vídeo</label>
  </aside>

  <!-- ====== SIDEBAR: RANKINGS ====== -->
  <aside class="sidebar-rankings" id="sidebar-rankings" hidden>
    <nav class="subtabs">
      <button class="active" data-sub="single" title="Ordena por uma dimensão única">Categoria</button>
      <button data-sub="builder" title="Combine pesos pra criar seu ranking custom">Builder</button>
    </nav>

    <!-- Sub: categoria única -->
    <div id="sub-single">
      <div class="rank-meta">
        <strong>Modo "Categoria"</strong>: escolha uma dimensão e veja os top N.
        Sem filtros complexos — ranking puro.
      </div>

      <h3>Ordenar por</h3>
      <select id="rank-by" title="Dimensão pra ordenar o ranking">
        <option value="score">⭐ Score composto (default)</option>
        <option value="aderencia_psyfun">🧠 Aderência PsyFun</option>
        <option value="viabilidade_claude">🤖 Viabilidade Claude</option>
        <option value="-dificuldade">⚙️ Menor dificuldade</option>
        <option value="esforco">⏱️ Menor esforço</option>
        <option value="-risco_tos">⚖️ Menor risco ToS</option>
        <option value="popularidade">🔥 Popularidade</option>
        <option value="qualidade_producao">🎨 Qualidade de produção</option>
      </select>

      <h3>Mostrar top</h3>
      <select id="rank-n" title="Quantos jogos no topo">
        <option value="10">Top 10</option>
        <option value="25" selected>Top 25</option>
        <option value="50">Top 50</option>
        <option value="100">Top 100</option>
      </select>

      <h3>Filtros mínimos <i class="info-i" title="Opcional — pode deixar tudo desativado">i</i></h3>
      <label class="toggle"><input type="checkbox" id="r-only-img">Só com imagem</label>
      <label class="toggle"><input type="checkbox" id="r-only-video">Só com vídeo</label>
      <h3 style="margin-top:12px">Dilemas (opcional)</h3>
      <div class="chips" id="r-chips-dilemas"></div>
    </div>

    <!-- Sub: builder -->
    <div id="sub-builder" hidden>
      <div class="rank-meta">
        <strong>Modo "Builder"</strong>: ajuste os pesos e veja o ranking custom.
        Fórmula: <code>soma(peso × valor)</code> para cada jogo.
      </div>

      <h3>Pesos (0–5)</h3>
      <div class="weight-row" title="Peso da aderência PsyFun (1-5 do jogo × peso)">
        <label>🧠 Aderência</label>
        <input type="range" min="0" max="5" value="3" id="w-aderencia">
        <span class="wval" id="wval-aderencia">3</span>
      </div>
      <div class="weight-row" title="Peso da viabilidade Claude">
        <label>🤖 Viabilidade</label>
        <input type="range" min="0" max="5" value="2" id="w-viabilidade">
        <span class="wval" id="wval-viabilidade">2</span>
      </div>
      <div class="weight-row" title="Peso de (6 - dificuldade) — valoriza menor dificuldade">
        <label>⚙️ Facilidade</label>
        <input type="range" min="0" max="5" value="1" id="w-facilidade">
        <span class="wval" id="wval-facilidade">1</span>
      </div>
      <div class="weight-row" title="Peso de (6 - risco_tos)">
        <label>⚖️ Segurança</label>
        <input type="range" min="0" max="5" value="1" id="w-seguranca">
        <span class="wval" id="wval-seguranca">1</span>
      </div>
      <div class="weight-row" title="Peso da popularidade (reviews/DAU normalizado)">
        <label>🔥 Popularidade</label>
        <input type="range" min="0" max="5" value="1" id="w-popularidade">
        <span class="wval" id="wval-popularidade">1</span>
      </div>
      <div class="weight-row" title="Peso da qualidade de produção — quanto assets/polish o jogo já entrega prontos">
        <label>🎨 Qualidade</label>
        <input type="range" min="0" max="5" value="2" id="w-qualidade">
        <span class="wval" id="wval-qualidade">2</span>
      </div>

      <h3>Mostrar top</h3>
      <select id="builder-n">
        <option value="10">Top 10</option>
        <option value="25" selected>Top 25</option>
        <option value="50">Top 50</option>
        <option value="100">Top 100</option>
      </select>
    </div>
  </aside>

  <main>
    <div id="stats"></div>
    <div id="grid"></div>
  </main>
</div>

<div class="modal-backdrop" id="modal-backdrop" onclick="if(event.target===this)closeModal()">
  <div class="modal" id="modal" role="dialog" aria-modal="true"></div>
</div>

<script id="data" type="application/json">__DATA__</script>
<script>
const DATA = JSON.parse(document.getElementById('data').textContent);
const DILEMAS = ['PD','PG','SH','UG','DG','SD','TG','CG','CPG','BG'];
const DILEMA_NAMES = {
  PD:"Prisoner's Dilemma", PG:"Public Goods", SH:"Stag Hunt",
  UG:"Ultimatum", DG:"Dictator", SD:"Snowdrift",
  TG:"Trust", CG:"Commons", CPG:"Coordination", BG:"Bargaining"
};
const DILEMA_DESCR = {
  PD:"Prisoner's Dilemma — cooperar vs trair; trair é dominante individualmente",
  PG:"Public Goods — contribuir pro pool comum ou ficar só com o seu",
  SH:"Stag Hunt — cooperar rende mais mas exige coordenação",
  UG:"Ultimatum — A propõe; B aceita ou rejeita (ambos perdem)",
  DG:"Dictator — A divide sem B poder reagir",
  SD:"Snowdrift — trair só vale se o outro cooperar",
  TG:"Trust Game — A investe em B; B decide quanto devolver",
  CG:"Commons — recurso compartilhado esgotável",
  CPG:"Coordination — escolhas simultâneas precisam coincidir",
  BG:"Bargaining — negociação multi-rodada"
};
const PLAT_MAP = {
  web: ['WEB','web'], windows: ['WIN','win'], mac: ['MAC','mac'], linux: ['LIN','lin'],
  android: ['AND','and'], ios: ['iOS','ios'], switch: ['SW','sw'],
  playstation: ['PS','ps'], xbox: ['XB','xb'], vr: ['VR','vr'],
  'cross-platform': ['ALL','all']
};
const PLAT_FULL = {
  web:'Web', windows:'Windows', mac:'macOS', linux:'Linux',
  android:'Android', ios:'iOS', switch:'Nintendo Switch',
  playstation:'PlayStation', xbox:'Xbox', vr:'VR',
  'cross-platform':'Cross-platform'
};

// heurística popularidade 0-5 a partir de strings livres
function popScore(entry) {
  const raw = (entry.popularidade || '').toLowerCase();
  if (!raw) return 0;
  let s = 0;
  const mm = raw.match(/(\d+(?:\.\d+)?)\s*m(\b|illion|au|on|\+)/);
  const km = raw.match(/(\d+(?:\.\d+)?)\s*k(\b|\+)/);
  const pct = raw.match(/(\d+)\s*%/);
  const stars = raw.match(/(\d+(?:\.\d+)?)\s*\/\s*5/);
  if (mm) s = Math.max(s, Math.min(5, Math.log10(parseFloat(mm[1]) * 1e6)/1.4));
  else if (km) s = Math.max(s, Math.min(5, Math.log10(parseFloat(km[1]) * 1e3)/1.4));
  if (pct) s = Math.max(s, parseInt(pct[1]) / 20);
  if (stars) s = Math.max(s, parseFloat(stars[1]));
  if (/dau|mau|million players|huge|massive|seminal/i.test(raw)) s = Math.max(s, 4);
  if (s === 0 && raw.length > 20) s = 1;
  return Math.round(s * 10) / 10;
}
for (const e of DATA) {
  e.pop_score = popScore(e);
  e.esforco_num = {XS:1,S:2,M:3,L:4,XL:5}[e.esforco_horas] || 3;
}

function uniq(arr){ return [...new Set(arr.filter(Boolean))].sort(); }

function platformBadges(entry) {
  const plats = (entry.plataforma||'').split('|').map(p=>p.trim()).filter(Boolean);
  if (!plats.length) return '<span class="pbadge unk" title="não informada">?</span>';
  return plats.slice(0,6).map(p => {
    const [label, cls] = PLAT_MAP[p] || [p.slice(0,3).toUpperCase(), 'unk'];
    const full = PLAT_FULL[p] || p;
    return `<span class="pbadge ${cls}" title="${full}">${label}</span>`;
  }).join('');
}

function shortDesc(e) {
  const cands = [e.exemplo_concreto, e.observacoes, e.raciocinio_dificuldade];
  for (const c of cands) if (c && c.length > 15) return escape(c);
  return escape(e.genero || 'Sem descrição');
}

function metricsRow(e) {
  const pop = e.pop_score || 0;
  const popStars = pop >= 1 ? '⭐'.repeat(Math.round(pop)) : '';
  const q = e.qualidade_producao || 0;
  const qualStars = q >= 1 ? '🎨'.repeat(q) : '';
  const qualLabel = e.raciocinio_qualidade || '';
  return `
    <span class="metric qual" title="Qualidade de produção: ${escape(qualLabel)}">
      <span class="ico">🎨</span><span class="v">${qualStars || '?'}</span>
    </span>
    <span class="metric ader" title="Aderência à mecânica PsyFun (1-5) — quão natural é enxertar coop/trair">
      <span class="ico">🧠</span><span class="v">${e.aderencia_psyfun||'?'}</span>
    </span>
    <span class="metric viab" title="Viabilidade Claude Code (1-5)">
      <span class="ico">🤖</span><span class="v">${e.viabilidade_claude||'?'}</span>
    </span>
    <span class="metric dif" title="Dificuldade técnica (1-5)">
      <span class="ico">⚙️</span><span class="v">${e.dificuldade||'?'}</span>
    </span>
    <span class="metric esf" title="Esforço estimado">
      <span class="ico">⏱️</span><span class="v">${e.esforco_horas||'?'}</span>
    </span>
    ${pop >= 1 ? `<span class="metric pop" title="Popularidade: ${escape(e.popularidade||'')}"><span class="ico">🔥</span><span class="v">${popStars}</span></span>` : ''}
    ${e.risco_tos && e.risco_tos >= 3 ? `<span class="metric tos" title="Risco ToS (alto)"><span class="ico">⚖️</span><span class="v">${e.risco_tos}</span></span>` : ''}
  `;
}

// ==================== STATE ====================
const state = {
  tab: 'explore',
  // Explore
  q: '', dilemas: new Set(),
  minAderencia: 1, minViabilidade: 1, maxDificuldade: 5, maxRisco: 5,
  metodos: new Set(), statuses: new Set(), esforcos: new Set(),
  generos: new Set(), visualizacoes: new Set(), modos: new Set(),
  temas: new Set(),
  ritmo: '', duracao: '', licenca: '',
  withImg: false, withVideo: false,
  // Rankings
  rankSub: 'single',
  rankBy: 'score', rankN: 25,
  rDilemas: new Set(), rOnlyImg: false, rOnlyVideo: false,
  weights: { aderencia: 3, viabilidade: 2, facilidade: 1, seguranca: 1, popularidade: 1, qualidade: 2 },
  builderN: 25,
};

// ==================== POPULAR CONTROLES ====================
function multiValues(field) {
  const s = new Set();
  for (const e of DATA) {
    const v = e[field];
    if (!v) continue;
    for (const x of String(v).split('|')) {
      const t = x.trim();
      if (t) s.add(t);
    }
  }
  return [...s].sort();
}
function singleValues(field) { return uniq(DATA.map(e => e[field])); }

function populateControls() {
  const cd = document.getElementById('chips-dilemas');
  const rcd = document.getElementById('r-chips-dilemas');
  for (const d of DILEMAS) {
    const html = `<div class="chip" data-dil="${d}" title="${DILEMA_DESCR[d]}">${d}</div>`;
    cd.insertAdjacentHTML('beforeend', html);
    rcd.insertAdjacentHTML('beforeend', html);
  }
  const cm = document.getElementById('chips-metodo');
  for (const m of uniq(DATA.map(e=>e.metodo_modificacao))) {
    cm.insertAdjacentHTML('beforeend', `<div class="chip" data-met="${m}" title="${m}">${m.replace(/-/g,' ')}</div>`);
  }
  const cs = document.getElementById('chips-status');
  for (const s of uniq(DATA.map(e=>e.status_codigo))) {
    cs.insertAdjacentHTML('beforeend', `<div class="chip" data-sta="${s}" title="${s}">${s.replace(/-/g,' ')}</div>`);
  }
  const ce = document.getElementById('chips-esforco');
  for (const x of ['XS','S','M','L','XL']) {
    const lbl = {XS:'XS · dia',S:'S · semana',M:'M · mês',L:'L · 3 meses',XL:'XL · +3m'}[x];
    ce.insertAdjacentHTML('beforeend', `<div class="chip" data-esf="${x}" title="${lbl}">${x}</div>`);
  }

  // Novos filtros Steam-like
  const cg = document.getElementById('chips-genero');
  for (const g of multiValues('genero_tag')) {
    cg.insertAdjacentHTML('beforeend', `<div class="chip" data-gen="${g}" title="${g}">${g.replace(/-/g,' ')}</div>`);
  }
  const cv = document.getElementById('chips-visualizacao');
  for (const v of multiValues('visualizacao')) {
    cv.insertAdjacentHTML('beforeend', `<div class="chip" data-vis="${v}" title="${v}">${v.replace(/-/g,' ')}</div>`);
  }
  const cmd = document.getElementById('chips-modo');
  const MODE_LABEL = {single:'solo',coop:'coop','local-multi':'local multi','online-multi':'online multi',pvp:'PvP',mmo:'MMO'};
  for (const m of multiValues('modo_jogo')) {
    cmd.insertAdjacentHTML('beforeend', `<div class="chip" data-mod="${m}" title="${m}">${MODE_LABEL[m]||m}</div>`);
  }
  const ct = document.getElementById('chips-tema');
  for (const t of multiValues('tema')) {
    ct.insertAdjacentHTML('beforeend', `<div class="chip" data-tem="${t}" title="${t}">${t.replace(/-/g,' ')}</div>`);
  }
  const sr = document.getElementById('sel-ritmo');
  for (const v of singleValues('ritmo')) if (v) sr.insertAdjacentHTML('beforeend', `<option value="${v}">${v.replace(/-/g,' ')}</option>`);
  const sd = document.getElementById('sel-duracao');
  for (const v of singleValues('duracao')) if (v) sd.insertAdjacentHTML('beforeend', `<option value="${v}">${v.replace(/-/g,' ')}</option>`);
  const sl = document.getElementById('sel-licenca');
  for (const v of singleValues('licenca')) if (v) sl.insertAdjacentHTML('beforeend', `<option value="${v}">${v.replace(/-/g,' ')}</option>`);
}

function multiMatch(entryField, set) {
  if (set.size === 0) return true;
  const vals = (entryField || '').split('|').map(x=>x.trim()).filter(Boolean);
  return [...set].some(s => vals.includes(s));
}

// ==================== FILTRO / ORDENAÇÃO ====================
function matchesExplore(e) {
  if (state.q) {
    const q = state.q.toLowerCase();
    const hay = [e.nome, e.genero, e.engine_tech, e.observacoes, e.dev_publisher, e.exemplo_concreto].filter(Boolean).join(' ').toLowerCase();
    if (!hay.includes(q)) return false;
  }
  if (state.dilemas.size > 0) {
    const d = (e.dilemas_compativeis||'').split('|').map(x=>x.trim());
    if (![...state.dilemas].some(s => d.includes(s))) return false;
  }
  if ((e.aderencia_psyfun||0) < state.minAderencia) return false;
  if ((e.viabilidade_claude||0) < state.minViabilidade) return false;
  if ((e.dificuldade||5) > state.maxDificuldade) return false;
  if ((e.risco_tos||1) > state.maxRisco) return false;
  if (state.metodos.size > 0 && !state.metodos.has(e.metodo_modificacao)) return false;
  if (state.statuses.size > 0 && !state.statuses.has(e.status_codigo)) return false;
  if (state.esforcos.size > 0 && !state.esforcos.has(e.esforco_horas)) return false;
  if (!multiMatch(e.genero_tag, state.generos)) return false;
  if (!multiMatch(e.visualizacao, state.visualizacoes)) return false;
  if (!multiMatch(e.modo_jogo, state.modos)) return false;
  if (!multiMatch(e.tema, state.temas)) return false;
  if (state.ritmo && e.ritmo !== state.ritmo) return false;
  if (state.duracao && e.duracao !== state.duracao) return false;
  if (state.licenca && e.licenca !== state.licenca) return false;
  if (state.withImg && (!e.imagens || !e.imagens.length)) return false;
  if (state.withVideo && !e.video_youtube_id) return false;
  return true;
}

function matchesRankSingle(e) {
  if (state.rDilemas.size > 0) {
    const d = (e.dilemas_compativeis||'').split('|').map(x=>x.trim());
    if (![...state.rDilemas].some(s => d.includes(s))) return false;
  }
  if (state.rOnlyImg && (!e.imagens || !e.imagens.length)) return false;
  if (state.rOnlyVideo && !e.video_youtube_id) return false;
  return true;
}

function sortKey(e, by) {
  switch (by) {
    case 'score':             return -(e.score || 0);
    case 'aderencia_psyfun':  return -(e.aderencia_psyfun || 0);
    case 'viabilidade_claude':return -(e.viabilidade_claude || 0);
    case '-dificuldade':      return (e.dificuldade || 5);
    case 'esforco':           return (e.esforco_num || 3);
    case '-risco_tos':        return (e.risco_tos || 1);
    case 'popularidade':      return -(e.pop_score || 0);
    case 'qualidade_producao':return -(e.qualidade_producao || 0);
  }
  return 0;
}

function builderScore(e) {
  const w = state.weights;
  return (w.aderencia * (e.aderencia_psyfun || 0))
       + (w.viabilidade * (e.viabilidade_claude || 0))
       + (w.facilidade * (6 - (e.dificuldade || 5)))
       + (w.seguranca * (6 - (e.risco_tos || 1)))
       + (w.popularidade * (e.pop_score || 0))
       + (w.qualidade * (e.qualidade_producao || 0));
}

// ==================== RENDER ====================
let lastVisible = -1;

function pulseCounter() {
  const el = document.getElementById('counters');
  const st = document.getElementById('stats');
  el.classList.add('pulse'); st.classList.add('pulse');
  setTimeout(() => { el.classList.remove('pulse'); st.classList.remove('pulse'); }, 350);
}

function render() {
  let list = [...DATA];
  let hint = '';
  if (state.tab === 'explore') {
    list = list.filter(matchesExplore).sort((a,b) => (b.score||0) - (a.score||0));
    hint = `<span class="mode-badge">🔍 Explorar</span>filtrando · ordenado por score`;
  } else if (state.rankSub === 'single') {
    list = list.filter(matchesRankSingle).sort((a,b) => sortKey(a, state.rankBy) - sortKey(b, state.rankBy));
    list = list.slice(0, state.rankN);
    const labels = {
      score:'score composto', aderencia_psyfun:'aderência PsyFun',
      viabilidade_claude:'viabilidade Claude', '-dificuldade':'menor dificuldade',
      esforco:'menor esforço', '-risco_tos':'menor risco ToS',
      popularidade:'popularidade', qualidade_producao:'qualidade de produção'
    };
    hint = `<span class="mode-badge">🏆 Top ${state.rankN}</span>ordenado por <strong>${labels[state.rankBy]}</strong>`;
  } else {
    for (const e of list) e._bscore = builderScore(e);
    list.sort((a,b) => b._bscore - a._bscore);
    list = list.slice(0, state.builderN);
    const w = state.weights;
    hint = `<span class="mode-badge">🏆 Builder · Top ${state.builderN}</span>pesos: 🧠${w.aderencia} · 🤖${w.viabilidade} · ⚙️${w.facilidade} · ⚖️${w.seguranca} · 🔥${w.popularidade} · 🎨${w.qualidade}`;
  }

  document.getElementById('count-visible').textContent = list.length;
  document.getElementById('count-total').textContent = DATA.length;
  if (list.length !== lastVisible) { pulseCounter(); lastVisible = list.length; }

  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  const frag = document.createDocumentFragment();
  for (const e of list.slice(0, 500)) frag.appendChild(card(e));
  grid.appendChild(frag);

  const showing = list.length > 500 ? `exibindo 500 primeiros de ${list.length}` : `${list.length} resultado${list.length===1?'':'s'}`;
  document.getElementById('stats').innerHTML = `${hint} · ${showing}`;

  // guarda lista atual pra navegação modal
  window._filteredList = list;
}

// ==================== CARD ====================
function card(e) {
  const div = document.createElement('div');
  div.className = 'card';
  div.setAttribute('role', 'button');
  div.setAttribute('tabindex', '0');
  div.setAttribute('aria-label', `${e.nome} — abrir detalhes`);
  div.dataset.id = e.id;

  const thumb = e.video_thumbnail || (e.imagens && e.imagens[0]) || '';
  const cover = thumb ? `style="background-image:url('${thumb}')"` : '';
  const noImg = thumb ? '' : 'no-img';
  const hasVideo = e.video_youtube_id ? 'has-video' : '';
  const dils = (e.dilemas_compativeis||'').split('|').map(x=>x.trim()).filter(Boolean);

  div.innerHTML = `
    <div class="cover ${noImg} ${hasVideo}" ${cover}>
      ${noImg ? 'sem imagem' : ''}
      <div class="score-badge" title="Score composto">${(e.score||0).toFixed(1)}</div>
      <div class="platforms">${platformBadges(e)}</div>
    </div>
    <div class="body">
      <div class="title">${escape(e.nome)}</div>
      <div class="sub">${escape(e.genero||'?')}${e.engine_tech ? ' · ' + escape(e.engine_tech) : ''}</div>
      <div class="desc">${shortDesc(e)}</div>
      <div class="metrics">${metricsRow(e)}</div>
      ${dils.length ? `<div class="dilemas">${dils.map(d=>`<span title="${DILEMA_NAMES[d]||d}">${d}</span>`).join('')}</div>` : ''}
    </div>
    <div class="footer">${e.video_youtube_id ? '▶ ver vídeo + detalhes' : 'clique ou Enter →'}</div>
  `;
  const open = (ev) => { if (ev) ev.stopPropagation(); openModal(e); };
  div.addEventListener('click', open);
  return div;
}

function escape(s) { return String(s||'').replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

// ==================== MODAL ====================
let modalIndex = 0;

function openModal(e) {
  modalIndex = (window._filteredList || []).findIndex(x => x.id === e.id);
  renderModal(e);
  document.getElementById('modal-backdrop').classList.add('open');
}

function openNext() {
  const list = window._filteredList || [];
  if (!list.length) return;
  modalIndex = (modalIndex + 1) % list.length;
  renderModal(list[modalIndex]);
}
function openPrev() {
  const list = window._filteredList || [];
  if (!list.length) return;
  modalIndex = (modalIndex - 1 + list.length) % list.length;
  renderModal(list[modalIndex]);
}

function renderModal(e) {
  const dils = (e.dilemas_compativeis||'').split('|').map(x=>x.trim()).filter(Boolean);
  const imgs = e.imagens||[];
  const links = e.links||[];
  const plats = (e.plataforma||'').split('|').map(x=>x.trim()).filter(Boolean);
  document.getElementById('modal').innerHTML = `
    <header>
      <div>
        <h2>${escape(e.nome)} <small style="color:var(--fg-muted);font-weight:400;font-size:14px">· score ${(e.score||0).toFixed(2)}</small></h2>
        <div class="nav-hint"><kbd>←</kbd><kbd>→</kbd> navegar · <kbd>Esc</kbd> fechar</div>
      </div>
      <button class="close" onclick="closeModal()" aria-label="Fechar">×</button>
    </header>
    <div class="body">
      ${e.video_youtube_id ? `
        <div class="video-container">
          <iframe src="https://www.youtube.com/embed/${e.video_youtube_id}?autoplay=0&rel=0" allow="encrypted-media" allowfullscreen></iframe>
        </div>
        ${e.video_title ? `<div style="font-size:12px;color:var(--fg-muted);margin-top:-8px;margin-bottom:16px">🎬 ${escape(e.video_title)}</div>` : ''}
      ` : ''}
      ${imgs.length ? `<div class="gallery">${imgs.map(i=>`<img src="${i}" alt="${escape(e.nome)}" loading="lazy">`).join('')}</div>` : ''}
      <dl>
        <dt>ano/dev</dt><dd>${escape(e.ano_lancamento||'?')} · ${escape(e.dev_publisher||'?')}</dd>
        <dt>gênero</dt><dd>${escape(e.genero||'?')}</dd>
        <dt>engine/tech</dt><dd>${escape(e.engine_tech||'?')}</dd>
        <dt>plataformas</dt><dd>${plats.map(p=>`<span class="pbadge ${(PLAT_MAP[p]||['','unk'])[1]}" style="margin-right:4px" title="${PLAT_FULL[p]||p}">${(PLAT_MAP[p]||[p.slice(0,3).toUpperCase()])[0]}</span>`).join('')} <span style="color:var(--fg-muted)">${escape(e.plataforma||'')}</span></dd>
        <dt>status código</dt><dd>${escape(e.status_codigo||'?')}</dd>
        <dt>método mod</dt><dd>${escape(e.metodo_modificacao||'?')}</dd>
        <dt>🧠 aderência</dt><dd>${e.aderencia_psyfun||'?'} / 5</dd>
        <dt>🤖 viabilidade</dt><dd>${e.viabilidade_claude||'?'} / 5</dd>
        <dt>⚙️ dificuldade</dt><dd>${e.dificuldade||'?'} / 5 — ${escape(e.raciocinio_dificuldade||'')}</dd>
        <dt>⏱️ esforço</dt><dd>${escape(e.esforco_horas||'?')}</dd>
        <dt>⚖️ risco ToS</dt><dd>${e.risco_tos||'?'} / 5</dd>
        <dt>🎨 qualidade</dt><dd>${e.qualidade_producao ? '🎨'.repeat(e.qualidade_producao) + ' · ' : ''}${escape(e.raciocinio_qualidade||'-')}</dd>
        <dt>🔥 popularidade</dt><dd>${e.pop_score >= 1 ? '⭐'.repeat(Math.round(e.pop_score)) + ' · ' : ''}${escape(e.popularidade||'-')}</dd>
        <dt>dilemas</dt><dd>${dils.map(d=>`<span style="background:var(--bg-elev);padding:3px 8px;margin-right:5px;border-radius:4px;font-size:12px" title="${DILEMA_DESCR[d]||''}">${d} — ${DILEMA_NAMES[d]||''}</span>`).join('')}</dd>
        <dt>exemplo concreto</dt><dd>${escape(e.exemplo_concreto||'-')}</dd>
        <dt>idade público</dt><dd>${escape(e.idade_publico||'-')}</dd>
        <dt>requisitos</dt><dd>${escape(e.requisitos_tecnicos||'-')}</dd>
        <dt>custo/licenças</dt><dd>${escape(e.custo_licencas||'-')}</dd>
        <dt>observações</dt><dd>${escape(e.observacoes||'-')}</dd>
        <dt>fonte (agente)</dt><dd>${escape(e.fonte_agente||'?')}</dd>
        <dt>links</dt><dd class="links">${links.map(l=>{ try { return `<a href="${l}" target="_blank" rel="noopener">${new URL(l).hostname}</a>`; } catch(_) { return ''; } }).join('')}</dd>
      </dl>
    </div>
  `;
  // restaura scroll topo do modal
  document.getElementById('modal').scrollTop = 0;
}
function closeModal() { document.getElementById('modal-backdrop').classList.remove('open'); }
function modalIsOpen() { return document.getElementById('modal-backdrop').classList.contains('open'); }

// ==================== KEYBOARD NAV ====================
function colsPerRow() {
  const grid = document.getElementById('grid');
  const cs = getComputedStyle(grid);
  const gtc = cs.gridTemplateColumns;
  return gtc.split(' ').length;
}

let focusedIdx = 0;
function focusCard(idx) {
  const cards = [...document.querySelectorAll('.card')];
  if (!cards.length) return;
  focusedIdx = Math.max(0, Math.min(idx, cards.length - 1));
  const c = cards[focusedIdx];
  c.focus();
  c.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
}

document.addEventListener('keydown', (ev) => {
  // dentro de input, não capturamos setas
  const tag = document.activeElement?.tagName;
  const typing = tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT';
  if (typing && ev.key !== 'Escape') return;

  if (ev.key === 'Escape') { closeModal(); return; }

  if (modalIsOpen()) {
    if (ev.key === 'ArrowRight') { ev.preventDefault(); openNext(); }
    else if (ev.key === 'ArrowLeft') { ev.preventDefault(); openPrev(); }
    return;
  }

  const cards = [...document.querySelectorAll('.card')];
  if (!cards.length) return;
  const cols = Math.max(1, colsPerRow());
  if (ev.key === 'ArrowRight') { ev.preventDefault(); focusCard(focusedIdx + 1); }
  else if (ev.key === 'ArrowLeft') { ev.preventDefault(); focusCard(focusedIdx - 1); }
  else if (ev.key === 'ArrowDown') { ev.preventDefault(); focusCard(focusedIdx + cols); }
  else if (ev.key === 'ArrowUp') { ev.preventDefault(); focusCard(focusedIdx - cols); }
  else if (ev.key === 'Enter' || ev.key === ' ') {
    if (document.activeElement?.classList.contains('card')) {
      ev.preventDefault();
      document.activeElement.click();
    }
  }
});

// ==================== BINDING ====================
function bindExplore() {
  document.getElementById('q').addEventListener('input', e => { state.q = e.target.value; render(); });
  const dq = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('input', () => {
      state[key] = parseInt(el.value);
      document.getElementById('val-' + id.split('-')[1]).textContent = el.value;
      render();
    });
  };
  dq('min-aderencia', 'minAderencia');
  dq('min-viabilidade', 'minViabilidade');
  dq('max-dificuldade', 'maxDificuldade');
  dq('max-risco', 'maxRisco');

  document.getElementById('only-with-img').addEventListener('change', e => { state.withImg = e.target.checked; render(); });
  document.getElementById('only-with-video').addEventListener('change', e => { state.withVideo = e.target.checked; render(); });

  document.querySelectorAll('#chips-dilemas .chip').forEach(c => {
    c.addEventListener('click', () => {
      c.classList.toggle('active');
      const d = c.dataset.dil;
      state.dilemas.has(d) ? state.dilemas.delete(d) : state.dilemas.add(d);
      render();
    });
  });
  const chipToggler = (selector, set) => {
    document.querySelectorAll(selector).forEach(c => {
      c.addEventListener('click', () => {
        c.classList.toggle('active');
        const v = c.dataset.met || c.dataset.sta || c.dataset.esf;
        set.has(v) ? set.delete(v) : set.add(v);
        render();
      });
    });
  };
  chipToggler('#chips-metodo .chip', state.metodos);
  chipToggler('#chips-status .chip', state.statuses);
  chipToggler('#chips-esforco .chip', state.esforcos);

  // Novos filtros Steam-like
  const toggleSet = (selector, set, attr) => {
    document.querySelectorAll(selector).forEach(c => {
      c.addEventListener('click', () => {
        c.classList.toggle('active');
        const v = c.dataset[attr];
        set.has(v) ? set.delete(v) : set.add(v);
        render();
      });
    });
  };
  toggleSet('#chips-genero .chip', state.generos, 'gen');
  toggleSet('#chips-visualizacao .chip', state.visualizacoes, 'vis');
  toggleSet('#chips-modo .chip', state.modos, 'mod');
  toggleSet('#chips-tema .chip', state.temas, 'tem');

  document.getElementById('sel-ritmo').addEventListener('change', e => { state.ritmo = e.target.value; render(); });
  document.getElementById('sel-duracao').addEventListener('change', e => { state.duracao = e.target.value; render(); });
  document.getElementById('sel-licenca').addEventListener('change', e => { state.licenca = e.target.value; render(); });
}

function bindRankings() {
  document.getElementById('rank-by').addEventListener('change', e => { state.rankBy = e.target.value; render(); });
  document.getElementById('rank-n').addEventListener('change', e => { state.rankN = parseInt(e.target.value); render(); });
  document.getElementById('r-only-img').addEventListener('change', e => { state.rOnlyImg = e.target.checked; render(); });
  document.getElementById('r-only-video').addEventListener('change', e => { state.rOnlyVideo = e.target.checked; render(); });
  document.querySelectorAll('#r-chips-dilemas .chip').forEach(c => {
    c.addEventListener('click', () => {
      c.classList.toggle('active');
      const d = c.dataset.dil;
      state.rDilemas.has(d) ? state.rDilemas.delete(d) : state.rDilemas.add(d);
      render();
    });
  });

  const wq = (id, key) => {
    const el = document.getElementById(id);
    el.addEventListener('input', () => {
      state.weights[key] = parseInt(el.value);
      document.getElementById('wval-' + key).textContent = el.value;
      render();
    });
  };
  wq('w-aderencia','aderencia');
  wq('w-viabilidade','viabilidade');
  wq('w-facilidade','facilidade');
  wq('w-seguranca','seguranca');
  wq('w-popularidade','popularidade');
  wq('w-qualidade','qualidade');
  document.getElementById('builder-n').addEventListener('change', e => { state.builderN = parseInt(e.target.value); render(); });
}

function bindTabs() {
  document.querySelectorAll('nav.tabs button').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('nav.tabs button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      state.tab = b.dataset.tab;
      document.getElementById('sidebar-explore').hidden = state.tab !== 'explore';
      document.getElementById('sidebar-rankings').hidden = state.tab !== 'rankings';
      render();
    });
  });
  document.querySelectorAll('nav.subtabs button').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('nav.subtabs button').forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      state.rankSub = b.dataset.sub;
      document.getElementById('sub-single').hidden = state.rankSub !== 'single';
      document.getElementById('sub-builder').hidden = state.rankSub !== 'builder';
      render();
    });
  });
}

populateControls();
bindExplore();
bindRankings();
bindTabs();
render();
</script>
</body>
</html>
"""
    html_content = html_content.replace("__DATA__", data_json)
    DST.write_text(html_content, encoding="utf-8")
    print(f"Escrito: {DST}  ({len(entries)} jogos, {n_with_video} com vídeo)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
