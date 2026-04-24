#!/usr/bin/env python3
"""
Gera exports/dashboard.html — single-file, zero-build, filtros facetados client-side.

v2 — melhorias UX:
- badges de plataforma visíveis (WEB/WIN/MAC/LIN/AND/iOS/SW/PS/XB/VR/ALL)
- descrição curta no próprio card (exemplo concreto truncado)
- tooltips descritivos em todos os controles da sidebar
- feedback visual no contador quando filtro muda (pulse laranja)
- card inteiro clicável + suporte a Enter/Space (teclado)
- indicador visual "clique pra ver detalhes" mais evidente

Lê CONSOLIDADO.jsonl e embarca dados como JSON inline.
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

    html_content = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
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
}
* { box-sizing: border-box; }
body {
  margin: 0; font-family: ui-sans-serif, -apple-system, "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--fg); line-height: 1.4;
}
header {
  padding: 18px 24px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  background: var(--bg-soft); position: sticky; top: 0; z-index: 10;
}
header h1 { margin: 0; font-size: 18px; font-weight: 700; letter-spacing: .2px; }
header .counters { color: var(--fg-muted); font-size: 13px; transition: color .25s; }
header .counters strong { color: var(--accent); font-weight: 700; }
header .counters.pulse strong { color: #ffd166; text-shadow: 0 0 8px rgba(255,159,67,0.8); }

.layout { display: grid; grid-template-columns: 340px 1fr; gap: 0; min-height: calc(100vh - 60px); }
aside {
  background: var(--bg-soft); border-right: 1px solid var(--border);
  padding: 20px; overflow-y: auto; max-height: calc(100vh - 60px); position: sticky; top: 60px;
}
aside h3 {
  font-size: 11px; text-transform: uppercase; letter-spacing: 1px;
  color: var(--fg-muted); margin: 20px 0 8px;
  display: flex; align-items: center; gap: 6px;
}
aside h3:first-of-type { margin-top: 0; }
.info-i {
  display: inline-flex; align-items: center; justify-content: center;
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--bg-elev); color: var(--fg-muted);
  font-size: 9px; font-weight: 700; cursor: help; font-style: normal;
  transition: background .2s, color .2s;
}
.info-i:hover { background: var(--accent); color: #1a1000; }

input[type=search], select {
  width: 100%; padding: 9px 11px; background: var(--bg-elev);
  border: 1px solid var(--border); color: var(--fg); border-radius: 6px;
  font-size: 14px; outline: none;
}
input[type=search]:focus, select:focus { border-color: var(--accent); }

.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip {
  padding: 4px 10px; border: 1px solid var(--border); background: transparent;
  color: var(--fg-muted); border-radius: 999px; cursor: pointer; font-size: 12px;
  user-select: none; transition: all .15s;
}
.chip:hover { border-color: var(--accent); color: var(--fg); }
.chip.active { background: var(--accent); color: #1a1000; border-color: var(--accent); font-weight: 600; }

.range-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.range-row label { min-width: 120px; font-size: 12px; color: var(--fg-muted); cursor: help; }
.range-row input[type=range] { flex: 1; accent-color: var(--accent); }
.range-row .val { min-width: 24px; text-align: right; font-size: 13px; color: var(--fg); }

.toggle { display: flex; align-items: center; gap: 8px; margin: 8px 0; font-size: 13px; cursor: pointer; }
.toggle input { accent-color: var(--accent); }

main { padding: 24px; overflow-y: auto; }
#stats {
  color: var(--fg-muted); font-size: 13px; margin-bottom: 14px;
  transition: color .25s;
}
#stats.pulse { color: var(--accent); }

#grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 14px;
}

/* ============ CARD ============ */
.card {
  background: var(--bg-soft); border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; display: flex; flex-direction: column;
  transition: border-color .15s, transform .12s, box-shadow .15s;
  cursor: pointer;
  position: relative;
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
  box-shadow: 0 0 0 3px rgba(255,159,67,0.4);
}
.card:active { transform: translateY(0); }
.card .cover {
  aspect-ratio: 16/9; background: var(--bg-elev) center/cover no-repeat;
  position: relative;
}
.card .cover.no-img {
  display: flex; align-items: center; justify-content: center;
  color: var(--fg-muted); font-size: 12px;
}
.card .cover .score-badge {
  position: absolute; top: 8px; right: 8px;
  background: rgba(255,159,67,.95); color: #1a1000;
  padding: 3px 8px; border-radius: 4px;
  font-weight: 700; font-size: 12px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
}
.card .cover .platforms {
  position: absolute; bottom: 8px; left: 8px;
  display: flex; flex-wrap: wrap; gap: 3px; max-width: 80%;
}

.pbadge {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 2px 6px; font-size: 9.5px; font-weight: 700;
  border-radius: 3px; font-family: 'JetBrains Mono', ui-monospace, monospace;
  letter-spacing: 0.3px; line-height: 1;
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
  padding: 11px 14px 8px; flex: 1;
  display: flex; flex-direction: column; gap: 5px;
}
.card .title {
  font-weight: 700; font-size: 15px;
  color: var(--fg);
  line-height: 1.2;
}
.card .sub {
  font-size: 11.5px; color: var(--fg-muted);
  display: flex; align-items: center; gap: 5px; flex-wrap: wrap;
}
.card .desc {
  font-size: 12px; color: #c7cbd3;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}
.card .dilemas { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.card .dilemas span {
  background: rgba(96,165,250,.18); color: var(--blue);
  padding: 1px 6px; border-radius: 3px;
  font-size: 10px; font-weight: 700;
  font-family: 'JetBrains Mono', ui-monospace, monospace;
}
.card .stats {
  display: flex; gap: 10px; font-size: 10.5px;
  color: var(--fg-muted); margin-top: auto; padding-top: 8px;
  border-top: 1px dashed var(--border);
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  letter-spacing: 0.2px;
}
.card .stats .sv { color: var(--fg); font-weight: 700; }
.card .footer {
  padding: 7px 14px;
  color: var(--accent); font-size: 11px; font-weight: 600;
  text-align: right;
  border-top: 1px solid var(--border);
  background: linear-gradient(to right, transparent 0%, rgba(255,159,67,0.04) 100%);
  transition: all .15s;
}
.card:hover .footer {
  background: linear-gradient(to right, rgba(255,159,67,0.08) 0%, rgba(255,159,67,0.16) 100%);
  color: #ffd166;
}

/* modal */
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.65);
  display: none; z-index: 20;
  animation: backdropIn .15s ease-out;
}
@keyframes backdropIn { from { opacity: 0; } to { opacity: 1; } }
.modal-backdrop.open { display: flex; align-items: center; justify-content: center; }
.modal {
  background: var(--bg-soft); border-radius: 12px;
  max-width: 900px; width: 90vw; max-height: 90vh;
  overflow-y: auto; border: 1px solid var(--border);
  animation: modalIn .2s ease-out;
}
@keyframes modalIn { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
.modal header {
  position: sticky; top: 0; padding: 14px 20px;
  border-bottom: 1px solid var(--border); background: var(--bg-soft);
}
.modal .body { padding: 20px; }
.modal .gallery {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 8px; margin: 16px 0;
}
.modal .gallery img { width: 100%; border-radius: 6px; }
.modal dl {
  display: grid; grid-template-columns: 170px 1fr;
  gap: 8px 16px; font-size: 14px;
}
.modal dt { color: var(--fg-muted); }
.modal dd { margin: 0; }
.modal .close {
  background: transparent; border: 0; color: var(--fg);
  font-size: 24px; cursor: pointer; line-height: 1;
}
.modal .links a { color: var(--blue); margin-right: 12px; }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  aside { position: static; max-height: none; }
}
</style>
</head>
<body>

<header>
  <h1>🎮 PsyFun — catálogo de jogos moddáveis</h1>
  <div class="counters" id="counters"><strong id="count-visible">0</strong> de <strong id="count-total">0</strong> jogos</div>
</header>

<div class="layout">
  <aside>
    <h3>Busca <i class="info-i" title="Procura no nome do jogo, gênero, engine, developer, observações e exemplo concreto. Atualiza a cada tecla.">i</i></h3>
    <input type="search" id="q" placeholder="nome, gênero, engine…" title="Digite termos para filtrar — atualização instantânea">

    <h3>Dilemas compatíveis <i class="info-i" title="Clique para ativar — filtra jogos que podem simular o dilema escolhido. Múltiplas seleções usam OR (qualquer um dos dilemas).">i</i></h3>
    <div class="chips" id="chips-dilemas"></div>

    <h3>Filtros numéricos <i class="info-i" title="Sliders cortam o catálogo em tempo real. Ajuste cada um e veja a lista à direita reagindo.">i</i></h3>
    <div class="range-row" title="Quão natural é enxertar mecânica cooperar/trair no jogo (1=alienígena, 5=já é PD-like)">
      <label>Aderência ≥</label>
      <input type="range" min="1" max="5" value="1" id="min-aderencia" aria-label="Aderência mínima à mecânica PsyFun">
      <span class="val" id="val-aderencia">1</span>
    </div>
    <div class="range-row" title="Quão bem Claude Code consegue fazer a modificação sozinho (1=precisa humano, 5=totalmente autônomo)">
      <label>Viabilidade Claude ≥</label>
      <input type="range" min="1" max="5" value="1" id="min-viabilidade" aria-label="Viabilidade mínima de execução com Claude Code">
      <span class="val" id="val-viabilidade">1</span>
    </div>
    <div class="range-row" title="Complexidade técnica de entender o jogo e acertar a mod (1=editor visual, 5=engenharia reversa)">
      <label>Dificuldade ≤</label>
      <input type="range" min="1" max="5" value="5" id="max-dificuldade" aria-label="Dificuldade máxima técnica">
      <span class="val" id="val-dificuldade">5</span>
    </div>
    <div class="range-row" title="Risco de violar termos de serviço (1=zero risco FOSS, 5=DMCA/banimento provável)">
      <label>Risco ToS ≤</label>
      <input type="range" min="1" max="5" value="5" id="max-risco" aria-label="Risco máximo de violação de ToS">
      <span class="val" id="val-risco">5</span>
    </div>

    <h3>Método de modificação <i class="info-i" title="Como a modificação é feita: SDK oficial, fork de código, hook em runtime, scripting interno, editor do próprio jogo, etc.">i</i></h3>
    <select id="sel-metodo" title="Filtra por método de modificação">
      <option value="">— qualquer —</option>
    </select>

    <h3>Status do código <i class="info-i" title="Se o jogo é open-source, source-available, tem SDK oficial, ou é totalmente fechado">i</i></h3>
    <select id="sel-status" title="Filtra por status do código fonte">
      <option value="">— qualquer —</option>
    </select>

    <h3>Esforço estimado <i class="info-i" title="Horas humanas-equivalentes para primeiro piloto rodando. XS &lt;10h, S 10–40h (1sem), M 40–160h (1mês), L 160–480h (3m), XL &gt;480h.">i</i></h3>
    <select id="sel-esforco" title="Filtra por faixa de esforço estimado">
      <option value="">— qualquer —</option>
      <option value="XS">XS (&lt;10h, dia)</option>
      <option value="S">S (10–40h, semana)</option>
      <option value="M">M (40–160h, mês)</option>
      <option value="L">L (160–480h, 3 meses)</option>
      <option value="XL">XL (&gt;480h)</option>
    </select>

    <h3>Opções <i class="info-i" title="Filtros de visualização extras">i</i></h3>
    <label class="toggle" title="Esconde jogos cuja imagem de capa não foi baixada"><input type="checkbox" id="only-with-img">Apenas com imagem</label>
    <label class="toggle" title="Mostra apenas os 100 jogos com maior score composto"><input type="checkbox" id="top100-only">Top 100 (por score)</label>
  </aside>

  <main>
    <div id="stats"></div>
    <div id="grid"></div>
  </main>
</div>

<div class="modal-backdrop" id="modal-backdrop" onclick="if(event.target===this)closeModal()">
  <div class="modal" id="modal"></div>
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
  PD: "Prisoner's Dilemma — cada um escolhe cooperar ou trair sem saber do outro; trair é dominante individualmente",
  PG: "Public Goods — N jogadores contribuem para pool compartilhado; free-rider maximiza payoff",
  SH: "Stag Hunt — cooperar rende mais mas exige que o outro coopere também (coordenação)",
  UG: "Ultimatum — A propõe divisão; B aceita ou rejeita (ambos perdem se rejeitar)",
  DG: "Dictator — A divide unilateralmente; B é passivo",
  SD: "Snowdrift / Chicken — trair só compensa se o outro cooperar",
  TG: "Trust Game — A investe quantia em B; B decide quanto devolver",
  CG: "Commons — recurso compartilhado esgotável (tragedy of commons)",
  CPG: "Coordination — escolhas simultâneas precisam coincidir",
  BG: "Bargaining — negociação multi-rodada"
};
const PLAT_MAP = {
  web: ['WEB', 'web'], windows: ['WIN', 'win'], mac: ['MAC', 'mac'], linux: ['LIN', 'lin'],
  android: ['AND', 'and'], ios: ['iOS', 'ios'], switch: ['SW', 'sw'],
  playstation: ['PS', 'ps'], xbox: ['XB', 'xb'], vr: ['VR', 'vr'],
  'cross-platform': ['ALL', 'all']
};
const PLAT_FULL = {
  web: 'Web', windows: 'Windows', mac: 'macOS', linux: 'Linux',
  android: 'Android', ios: 'iOS', switch: 'Nintendo Switch',
  playstation: 'PlayStation', xbox: 'Xbox', vr: 'VR',
  'cross-platform': 'Cross-platform (roda em várias)'
};

function uniq(arr){ return [...new Set(arr.filter(Boolean))].sort(); }

function platformBadges(entry) {
  const plats = (entry.plataforma || '').split('|').map(p => p.trim()).filter(Boolean);
  if (plats.length === 0) return '<span class="pbadge unk" title="Plataforma não informada">?</span>';
  return plats.slice(0, 6).map(p => {
    const [label, cls] = PLAT_MAP[p] || [p.slice(0, 3).toUpperCase(), 'unk'];
    const full = PLAT_FULL[p] || p;
    return `<span class="pbadge ${cls}" title="${full}">${label}</span>`;
  }).join('');
}

function shortDescription(entry) {
  // Prefere exemplo_concreto (descreve a modificação), cai em observacoes, cai em genero
  const candidates = [entry.exemplo_concreto, entry.observacoes, entry.raciocinio_dificuldade];
  for (const c of candidates) {
    if (c && c.length > 15) return escape(c);
  }
  return escape(entry.genero || 'Sem descrição disponível');
}

function populateSelects() {
  const sM = document.getElementById('sel-metodo');
  const sS = document.getElementById('sel-status');
  for (const m of uniq(DATA.map(e=>e.metodo_modificacao))) sM.insertAdjacentHTML('beforeend', `<option>${m}</option>`);
  for (const s of uniq(DATA.map(e=>e.status_codigo))) sS.insertAdjacentHTML('beforeend', `<option>${s}</option>`);
  const cd = document.getElementById('chips-dilemas');
  for (const d of DILEMAS) {
    cd.insertAdjacentHTML('beforeend',
      `<div class="chip" data-dil="${d}" title="${DILEMA_DESCR[d]}">${d}</div>`);
  }
}

const state = {
  q: '', dilemas: new Set(),
  minAderencia: 1, minViabilidade: 1, maxDificuldade: 5, maxRisco: 5,
  metodo: '', status: '', esforco: '',
  withImg: false, top100: false,
};

function sorted() {
  return [...DATA].sort((a,b) => (b.score||0) - (a.score||0));
}

function matches(e) {
  if (state.q) {
    const q = state.q.toLowerCase();
    const hay = [e.nome, e.genero, e.engine_tech, e.observacoes, e.dev_publisher, e.exemplo_concreto].filter(Boolean).join(' ').toLowerCase();
    if (!hay.includes(q)) return false;
  }
  if (state.dilemas.size > 0) {
    const d = (e.dilemas_compativeis||'').split('|').map(x=>x.trim());
    let any = false;
    for (const s of state.dilemas) if (d.includes(s)) { any = true; break; }
    if (!any) return false;
  }
  if ((e.aderencia_psyfun||0) < state.minAderencia) return false;
  if ((e.viabilidade_claude||0) < state.minViabilidade) return false;
  if ((e.dificuldade||5) > state.maxDificuldade) return false;
  if ((e.risco_tos||1) > state.maxRisco) return false;
  if (state.metodo && e.metodo_modificacao !== state.metodo) return false;
  if (state.status && e.status_codigo !== state.status) return false;
  if (state.esforco && e.esforco_horas !== state.esforco) return false;
  if (state.withImg && (!e.imagens || e.imagens.length === 0)) return false;
  return true;
}

let lastVisible = -1;

function pulseCounter() {
  const el = document.getElementById('counters');
  const st = document.getElementById('stats');
  el.classList.add('pulse');
  st.classList.add('pulse');
  setTimeout(() => { el.classList.remove('pulse'); st.classList.remove('pulse'); }, 350);
}

function render() {
  const sortedData = sorted();
  let filtered = sortedData.filter(matches);
  if (state.top100) filtered = filtered.slice(0, 100);

  document.getElementById('count-visible').textContent = filtered.length;
  document.getElementById('count-total').textContent = DATA.length;
  if (filtered.length !== lastVisible) {
    pulseCounter();
    lastVisible = filtered.length;
  }

  const grid = document.getElementById('grid');
  grid.innerHTML = '';
  const frag = document.createDocumentFragment();
  for (const e of filtered.slice(0, 400)) {
    frag.appendChild(card(e));
  }
  grid.appendChild(frag);

  document.getElementById('stats').textContent =
    filtered.length > 400
      ? `Exibindo 400 primeiros de ${filtered.length} resultados. Refine filtros pra ver mais.`
      : `${filtered.length} resultado${filtered.length===1?'':'s'}.`;
}

function card(e) {
  const div = document.createElement('div');
  div.className = 'card';
  div.setAttribute('role', 'button');
  div.setAttribute('tabindex', '0');
  div.setAttribute('aria-label', `${e.nome} — abrir detalhes`);
  const cover = (e.imagens && e.imagens[0]) ? `style="background-image:url('${e.imagens[0]}')"` : '';
  const noImg = (!e.imagens || e.imagens.length === 0) ? 'no-img' : '';
  const dils = (e.dilemas_compativeis||'').split('|').map(x=>x.trim()).filter(Boolean);
  div.innerHTML = `
    <div class="cover ${noImg}" ${cover}>
      ${noImg ? 'sem imagem' : ''}
      <div class="score-badge" title="Score composto (aderência×2 + viabilidade − dificuldade÷2 + bônus)">${(e.score||0).toFixed(1)}</div>
      <div class="platforms">${platformBadges(e)}</div>
    </div>
    <div class="body">
      <div class="title" title="${escape(e.nome)}">${escape(e.nome)}</div>
      <div class="sub" title="Gênero · Engine · Developer">
        ${escape(e.genero||'?')}
        ${e.engine_tech ? ' · ' + escape(e.engine_tech) : ''}
      </div>
      <div class="desc" title="Descrição/exemplo concreto da modificação">${shortDescription(e)}</div>
      ${dils.length ? `<div class="dilemas">${dils.map(d=>`<span title="${DILEMA_NAMES[d]||d}">${d}</span>`).join('')}</div>` : ''}
      <div class="stats">
        <span title="Aderência à mecânica PsyFun (1-5)">ader <span class="sv">${e.aderencia_psyfun||'?'}</span></span>
        <span title="Dificuldade técnica (1-5)">dif <span class="sv">${e.dificuldade||'?'}</span></span>
        <span title="Viabilidade Claude Code (1-5)">viab <span class="sv">${e.viabilidade_claude||'?'}</span></span>
        <span title="Esforço estimado">esf <span class="sv">${e.esforco_horas||'?'}</span></span>
      </div>
    </div>
    <div class="footer">clique ou pressione Enter para abrir detalhes →</div>
  `;
  const open = (ev) => { ev.stopPropagation(); openModal(e); };
  div.addEventListener('click', open);
  div.addEventListener('keydown', (ev) => {
    if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); open(ev); }
  });
  return div;
}

function escape(s) { return String(s||'').replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

function openModal(e) {
  const bg = document.getElementById('modal-backdrop');
  const dils = (e.dilemas_compativeis||'').split('|').map(x=>x.trim()).filter(Boolean);
  const imgs = e.imagens||[];
  const links = e.links||[];
  const plats = (e.plataforma||'').split('|').map(x=>x.trim()).filter(Boolean);
  document.getElementById('modal').innerHTML = `
    <header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h2 style="margin:0">${escape(e.nome)} <small style="color:var(--fg-muted);font-weight:400">(score ${(e.score||0).toFixed(2)})</small></h2>
        <button class="close" onclick="closeModal()" aria-label="Fechar">×</button>
      </div>
    </header>
    <div class="body">
      ${imgs.length ? `<div class="gallery">${imgs.map(i=>`<img src="${i}" alt="${escape(e.nome)}">`).join('')}</div>` : ''}
      <dl>
        <dt>ano/dev</dt><dd>${escape(e.ano_lancamento||'?')} · ${escape(e.dev_publisher||'?')}</dd>
        <dt>gênero</dt><dd>${escape(e.genero||'?')}</dd>
        <dt>engine/tech</dt><dd>${escape(e.engine_tech||'?')}</dd>
        <dt>plataformas</dt><dd>${plats.map(p=>`<span class="pbadge ${(PLAT_MAP[p]||['','unk'])[1]}" style="margin-right:4px" title="${PLAT_FULL[p]||p}">${(PLAT_MAP[p]||[p.slice(0,3).toUpperCase()])[0]}</span>`).join('')} ${escape(e.plataforma||'')}</dd>
        <dt>status código</dt><dd>${escape(e.status_codigo||'?')}</dd>
        <dt>método mod</dt><dd>${escape(e.metodo_modificacao||'?')}</dd>
        <dt>dificuldade</dt><dd>${e.dificuldade||'?'} — ${escape(e.raciocinio_dificuldade||'')}</dd>
        <dt>esforço</dt><dd>${escape(e.esforco_horas||'?')}</dd>
        <dt>viabilidade Claude</dt><dd>${e.viabilidade_claude||'?'}</dd>
        <dt>aderência PsyFun</dt><dd>${e.aderencia_psyfun||'?'}</dd>
        <dt>dilemas</dt><dd>${dils.map(d=>`<span style="background:var(--bg-elev);padding:2px 6px;margin-right:4px;border-radius:3px;font-size:12px" title="${DILEMA_DESCR[d]||''}">${d} — ${DILEMA_NAMES[d]||''}</span>`).join('')}</dd>
        <dt>exemplo concreto</dt><dd>${escape(e.exemplo_concreto||'-')}</dd>
        <dt>popularidade</dt><dd>${escape(e.popularidade||'-')}</dd>
        <dt>idade público</dt><dd>${escape(e.idade_publico||'-')}</dd>
        <dt>requisitos</dt><dd>${escape(e.requisitos_tecnicos||'-')}</dd>
        <dt>custo/licenças</dt><dd>${escape(e.custo_licencas||'-')}</dd>
        <dt>risco ToS</dt><dd>${e.risco_tos||'?'}</dd>
        <dt>observações</dt><dd>${escape(e.observacoes||'-')}</dd>
        <dt>fonte (agente)</dt><dd>${escape(e.fonte_agente||'?')}</dd>
        <dt>links</dt><dd class="links">${links.map(l=>{ try { return `<a href="${l}" target="_blank" rel="noopener">${new URL(l).hostname}</a>`; } catch(_) { return ''; } }).join('')}</dd>
      </dl>
    </div>
  `;
  bg.classList.add('open');
}
function closeModal() { document.getElementById('modal-backdrop').classList.remove('open'); }

document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') closeModal();
});

function bind() {
  const dq = (id, key, asInt) => {
    const el = document.getElementById(id);
    el.addEventListener('input', () => {
      state[key] = asInt ? parseInt(el.value) : el.value;
      if (asInt) document.getElementById('val-' + id.split('-')[1]).textContent = el.value;
      render();
    });
  };
  document.getElementById('q').addEventListener('input', e => { state.q = e.target.value; render(); });
  dq('min-aderencia', 'minAderencia', true);
  dq('min-viabilidade', 'minViabilidade', true);
  dq('max-dificuldade', 'maxDificuldade', true);
  dq('max-risco', 'maxRisco', true);
  document.getElementById('sel-metodo').addEventListener('change', e => { state.metodo = e.target.value; render(); });
  document.getElementById('sel-status').addEventListener('change', e => { state.status = e.target.value; render(); });
  document.getElementById('sel-esforco').addEventListener('change', e => { state.esforco = e.target.value; render(); });
  document.getElementById('only-with-img').addEventListener('change', e => { state.withImg = e.target.checked; render(); });
  document.getElementById('top100-only').addEventListener('change', e => { state.top100 = e.target.checked; render(); });
  document.querySelectorAll('.chip').forEach(c => {
    c.addEventListener('click', () => {
      c.classList.toggle('active');
      const d = c.dataset.dil;
      if (state.dilemas.has(d)) state.dilemas.delete(d); else state.dilemas.add(d);
      render();
    });
  });
}

populateSelects();
bind();
render();
</script>
</body>
</html>
"""
    html_content = html_content.replace("__DATA__", data_json)
    DST.write_text(html_content, encoding="utf-8")
    print(f"Escrito: {DST}  ({len(entries)} jogos embedded)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
