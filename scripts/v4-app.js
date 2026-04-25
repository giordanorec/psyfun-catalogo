// PsyFun v4 dashboard — vanilla JS, dados do <script id="data">
'use strict';

const DATA = JSON.parse(document.getElementById('data').textContent);

// ============================================================
// Constantes
// ============================================================
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
  web:'WEB', windows:'WIN', mac:'MAC', linux:'LIN',
  android:'AND', ios:'iOS', switch:'SW',
  playstation:'PS', xbox:'XB', vr:'VR', 'cross-platform':'ALL'
};
const PLAT_FULL = {
  web:'Web', windows:'Windows', mac:'macOS', linux:'Linux',
  android:'Android', ios:'iOS', switch:'Nintendo Switch',
  playstation:'PlayStation', xbox:'Xbox', vr:'VR',
  'cross-platform':'Cross-platform'
};
const ESF_NUM = { XS:1, S:2, M:3, L:4, XL:5 };
const ESF_LABEL = { XS:'XS · dia', S:'S · semana', M:'M · mês', L:'L · 3m', XL:'XL · +3m' };
const MODE_LABEL = {
  single:'solo', coop:'coop', 'local-multi':'local multi',
  'online-multi':'online multi', pvp:'PvP', mmo:'MMO'
};

// ============================================================
// Preprocessamento
// ============================================================
function popScore(entry) {
  const raw = (entry.popularidade || '').toLowerCase();
  if (!raw) return 0;
  let s = 0;
  const mm = raw.match(/(\d+(?:\.\d+)?)\s*m(\b|illion|au|on|\+)/);
  const km = raw.match(/(\d+(?:\.\d+)?)\s*k(\b|\+)/);
  const pct = raw.match(/(\d+)\s*%/);
  const stars = raw.match(/(\d+(?:\.\d+)?)\s*\/\s*5/);
  if (mm) s = Math.max(s, Math.min(5, Math.log10(parseFloat(mm[1]) * 1e6) / 1.4));
  else if (km) s = Math.max(s, Math.min(5, Math.log10(parseFloat(km[1]) * 1e3) / 1.4));
  if (pct) s = Math.max(s, parseInt(pct[1]) / 20);
  if (stars) s = Math.max(s, parseFloat(stars[1]));
  if (/dau|mau|million players|huge|massive|seminal/i.test(raw)) s = Math.max(s, 4);
  if (s === 0 && raw.length > 20) s = 1;
  return Math.round(s * 10) / 10;
}

DATA.forEach(e => {
  e.pop_score = popScore(e);
  e.esforco_num = ESF_NUM[e.esforco_horas] || 3;
  // Score composto: aderência*2 + viabilidade − dificuldade*0.5  (mesma fórmula do build_dashboard.py)
  if (e.score == null) {
    const a = e.aderencia_psyfun || 0;
    const v = e.viabilidade_claude || 0;
    const d = e.dificuldade || 5;
    e.score = Math.round((a * 2 + v - d * 0.5) * 100) / 100;
  }
});

const TOTAL = DATA.length;
const SCORE_MAX = DATA.reduce((m, e) => Math.max(m, e.score || 0), 0);

// ============================================================
// State
// ============================================================
const state = {
  panel: 'explorar',
  // explore
  q: '', dilemas: new Set(),
  minAderencia: 1, minViabilidade: 1, maxDificuldade: 5, maxRisco: 5,
  metodos: new Set(), statuses: new Set(), esforcos: new Set(),
  visualizacoes: new Set(), modos: new Set(), generos: new Set(), temas: new Set(),
  ritmo: '', duracao: '', licenca: '',
  withImg: false, withVideo: false,
  sortBy: 'score',
  // rankings
  rankSub: 'categoria',
  rankDim: 'aderencia',
  rankN: 25,
  weights: { aderencia: 3, viabilidade: 2, dificuldade: 1, tos: 2, popularidade: 1, qualidade: 1 },
};

// ============================================================
// Helpers
// ============================================================
function escape(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}

function uniq(arr) { return [...new Set(arr.filter(Boolean))].sort(); }

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

function multiMatch(value, set) {
  if (set.size === 0) return true;
  const vals = (value || '').split('|').map(x => x.trim()).filter(Boolean);
  return [...set].some(s => vals.includes(s));
}

function platCodes(plat) {
  return (plat || '').split('|')
    .map(p => p.trim())
    .filter(Boolean)
    .map(p => PLAT_MAP[p] || p.slice(0, 3).toUpperCase());
}

function shortDesc(e) {
  const cands = [e.exemplo_concreto, e.observacoes, e.raciocinio_dificuldade];
  for (const c of cands) if (c && c.length > 15) return escape(c);
  return escape(e.genero || 'Sem descrição');
}

// fallback gradient determinístico baseado no id
function fallbackGradient(id) {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = ((h << 5) - h + id.charCodeAt(i)) | 0;
  const h1 = Math.abs(h) % 360;
  const h2 = (h1 + 60 + (Math.abs(h >> 8) % 80)) % 360;
  return `linear-gradient(135deg,hsl(${h1} 35% 18%),hsl(${h2} 50% 32%) 60%,hsl(${(h2+30)%360} 70% 55%))`;
}

// ============================================================
// Filtros / ordenação
// ============================================================
function matchesExplore(e) {
  if (state.q) {
    const q = state.q.toLowerCase();
    const hay = [e.nome, e.genero, e.engine_tech, e.observacoes,
                 e.dev_publisher, e.exemplo_concreto].filter(Boolean).join(' ').toLowerCase();
    if (!hay.includes(q)) return false;
  }
  if (state.dilemas.size > 0) {
    const d = (e.dilemas_compativeis || '').split('|').map(x => x.trim());
    if (![...state.dilemas].some(s => d.includes(s))) return false;
  }
  if ((e.aderencia_psyfun || 0) < state.minAderencia) return false;
  if ((e.viabilidade_claude || 0) < state.minViabilidade) return false;
  if ((e.dificuldade || 5) > state.maxDificuldade) return false;
  if ((e.risco_tos || 1) > state.maxRisco) return false;
  if (state.metodos.size > 0 && !state.metodos.has(e.metodo_modificacao)) return false;
  if (state.statuses.size > 0 && !state.statuses.has(e.status_codigo)) return false;
  if (state.esforcos.size > 0 && !state.esforcos.has(e.esforco_horas)) return false;
  if (!multiMatch(e.visualizacao, state.visualizacoes)) return false;
  if (!multiMatch(e.modo_jogo, state.modos)) return false;
  if (!multiMatch(e.genero_tag, state.generos)) return false;
  if (!multiMatch(e.tema, state.temas)) return false;
  if (state.ritmo && e.ritmo !== state.ritmo) return false;
  if (state.duracao && e.duracao !== state.duracao) return false;
  if (state.licenca && e.licenca !== state.licenca) return false;
  if (state.withImg && (!e.imagens || !e.imagens.length)) return false;
  if (state.withVideo && !e.video_youtube_id) return false;
  return true;
}

function sortKeyExplore(e) {
  const by = state.sortBy;
  switch (by) {
    case 'score':       return -(e.score || 0);
    case 'aderencia':   return -(e.aderencia_psyfun || 0);
    case 'viabilidade': return -(e.viabilidade_claude || 0);
    case 'popularidade':return -(e.pop_score || 0);
    case 'az':          return (e.nome || '').toLowerCase();
  }
  return 0;
}

function rankSortValue(e, dim) {
  switch (dim) {
    case 'score':        return -(e.score || 0);
    case 'aderencia':    return -(e.aderencia_psyfun || 0);
    case 'viabilidade':  return -(e.viabilidade_claude || 0);
    case 'dificuldade':  return (e.dificuldade || 5);
    case 'esforco':      return (e.esforco_num || 3);
    case 'tos':          return (e.risco_tos || 1);
    case 'popularidade': return -(e.pop_score || 0);
    case 'qualidade':    return -(e.qualidade_producao || 0);
  }
  return 0;
}

const RANK_LABEL = {
  score:       'Score composto ↓',
  aderencia:   'Aderência ↓',
  viabilidade: 'Viabilidade ↓',
  dificuldade: 'Dificuldade ↓',
  esforco:     'Esforço ↓',
  tos:         'Risco ToS ↓',
  popularidade:'Popularidade ↓',
  qualidade:   'Qualidade ↓'
};

function builderScore(e) {
  const w = state.weights;
  return (w.aderencia    * (e.aderencia_psyfun || 0))
       + (w.viabilidade  * (e.viabilidade_claude || 0))
       - (w.dificuldade  * ((e.dificuldade || 5) - 1))
       - (w.tos          * ((e.risco_tos || 1) - 1))
       + (w.popularidade * (e.pop_score || 0))
       + (w.qualidade    * (e.qualidade_producao || 0));
}

// ============================================================
// Render: cards
// ============================================================
const METRIC_DEFS = [
  { key:'qualidade_producao', gly:'🎨', label:'qualidade' },
  { key:'aderencia_psyfun',   gly:'🧠', label:'aderência' },
  { key:'viabilidade_claude', gly:'🤖', label:'viabilidade' },
  { key:'dificuldade',        gly:'⚙️', label:'dificuldade' },
];

function metricsHTML(e) {
  const cells = METRIC_DEFS.map(def => {
    const v = e[def.key];
    if (v == null) return '';
    const fillPct = Math.max(0, Math.min(100, (v / 5) * 100));
    return `<span class="metric" title="${def.label}: ${v} / 5">
      <span class="gly">${def.gly}</span>
      <span class="v">${v}</span>
      <span class="bar"><span class="bar-fill" style="width:${fillPct}%"></span></span>
    </span>`;
  });
  // esforço sempre presente, sem barra
  cells.push(`<span class="metric" title="esforço estimado">
    <span class="gly">⏱️</span>
    <span class="v">${escape(e.esforco_horas || '?')}</span>
  </span>`);
  // risco_tos só se ≥ 3 (warn)
  if ((e.risco_tos || 0) >= 3) {
    cells.push(`<span class="metric warn" title="risco ToS alto">
      <span class="gly">⚖️</span>
      <span class="v">${e.risco_tos}</span>
    </span>`);
  }
  return cells.join('');
}

function cardHTML(e) {
  const plats = platCodes(e.plataforma);
  const dilemas = (e.dilemas_compativeis || '').split('|').map(x => x.trim()).filter(Boolean);
  const cover = e.video_thumbnail || (e.imagens && e.imagens[0]) || '';
  const coverStyle = cover
    ? `background-image:url('${escape(cover)}')`
    : `background:${fallbackGradient(e.id)}`;
  const playBtn = e.video_youtube_id
    ? `<div class="play-btn"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>`
    : '';
  const dilemasHTML = dilemas.slice(0, 8).map(d => {
    const m = state.dilemas.has(d) ? 'match' : '';
    return `<span class="dilema ${m}" title="${escape(DILEMA_NAMES[d] || d)}">${d}</span>`;
  }).join('') + (dilemas.length > 8 ? `<span class="dilema">+${dilemas.length - 8}</span>` : '');

  return `<article class="card" tabindex="0" data-id="${escape(e.id)}" role="button" aria-label="${escape(e.nome)} — abrir detalhe">
    <div class="card-cover" data-video="${e.video_youtube_id ? 'true' : 'false'}">
      <div class="img-ph" style="${coverStyle}"></div>
      ${playBtn}
      <div class="score-badge">${(e.score || 0).toFixed(2)}</div>
      <div class="plat-row">${plats.slice(0, 5).map(p => `<span class="plat" data-p="${p}">${p}</span>`).join('')}</div>
    </div>
    <div class="card-body">
      <div class="card-meta">${escape(e.genero || '?')}${e.engine_tech ? ' · ' + escape(e.engine_tech) : ''}</div>
      <h3 class="card-title">${escape(e.nome)}</h3>
      <p class="card-desc">${shortDesc(e)}</p>
      <div class="metrics">${metricsHTML(e)}</div>
      <div class="dilemas-row">${dilemasHTML}</div>
      <div class="card-foot"><span>${e.video_youtube_id ? 'ver vídeo + detalhes' : 'ver detalhes'}</span><span class="arr">→</span></div>
    </div>
  </article>`;
}

// ============================================================
// Render: ranked list
// ============================================================
function rankedHTML(e, idx) {
  const dilemas = (e.dilemas_compativeis || '').split('|').map(x => x.trim()).filter(Boolean);
  const dilemasHTML = dilemas.slice(0, 6).map(d => `<span class="dilema">${d}</span>`).join('');
  const scoreVal = state.rankSub === 'builder'
    ? (e._bscore || 0).toFixed(1)
    : (e.score || 0).toFixed(1);
  const scoreLabel = state.rankSub === 'builder'
    ? `score custom`
    : `score · aderência ${e.aderencia_psyfun || '?'}/5`;
  return `<div class="ranked-row" tabindex="0" data-id="${escape(e.id)}" role="button" aria-label="${escape(e.nome)}">
    <div class="rank">${String(idx + 1).padStart(2, '0')}</div>
    <div class="info">
      <div class="meta">${escape(e.genero || '?')}${e.engine_tech ? ' · ' + escape(e.engine_tech) : ''}</div>
      <h3>${escape(e.nome)}</h3>
      <p class="desc">${shortDesc(e)}</p>
    </div>
    <div class="score-col">
      <div><div class="big">${scoreVal}</div><div class="lbl">${scoreLabel}</div></div>
      <div class="dilemas-row">${dilemasHTML}</div>
    </div>
  </div>`;
}

// ============================================================
// Counters / summary bar
// ============================================================
function updateCounters(visible) {
  document.getElementById('counterFiltered').textContent = visible.toLocaleString('pt-BR');
  document.getElementById('counterTotal').textContent = TOTAL.toLocaleString('pt-BR');
  document.getElementById('heroCounterPill').innerHTML =
    `${visible.toLocaleString('pt-BR')} após filtros<em>· ${Math.round(visible / TOTAL * 100)}%</em>`;
  document.getElementById('catalogHeading').innerHTML =
    `<span class="n">${visible.toLocaleString('pt-BR')}</span> jogos`;
}

function updateSummaryBar(visible) {
  const parts = [];
  parts.push(`<strong>${visible.toLocaleString('pt-BR')} resultados</strong>`);
  if (state.dilemas.size) parts.push(`<span>${[...state.dilemas].join(' + ')} ativos</span>`);
  if (state.minAderencia > 1)   parts.push(`<span>Aderência ≥ ${state.minAderencia}</span>`);
  if (state.minViabilidade > 1) parts.push(`<span>Viabilidade ≥ ${state.minViabilidade}</span>`);
  if (state.maxDificuldade < 5) parts.push(`<span>Dificuldade ≤ ${state.maxDificuldade}</span>`);
  if (state.maxRisco < 5)       parts.push(`<span>Risco ToS ≤ ${state.maxRisco}</span>`);
  if (state.esforcos.size)      parts.push(`<span>Esforço ${[...state.esforcos].join(' / ')}</span>`);
  if (state.statuses.size)      parts.push(`<span>${[...state.statuses].join(' / ')}</span>`);
  if (state.q)                  parts.push(`<span>Busca: "${escape(state.q)}"</span>`);
  if (state.withImg)            parts.push(`<span>Com imagem</span>`);
  if (state.withVideo)          parts.push(`<span>Com vídeo</span>`);
  const inner = parts.join('<span class="sep">·</span>');
  document.getElementById('summaryBar').innerHTML =
    `${inner}<button class="clear" type="button" id="clearAllBtn"><span class="x"></span>Limpar tudo</button>`;
  document.getElementById('clearAllBtn').addEventListener('click', clearAllFilters);
}

function clearAllFilters() {
  state.q = '';
  state.dilemas.clear();
  state.minAderencia = 1; state.minViabilidade = 1;
  state.maxDificuldade = 5; state.maxRisco = 5;
  state.metodos.clear(); state.statuses.clear(); state.esforcos.clear();
  state.visualizacoes.clear(); state.modos.clear(); state.generos.clear(); state.temas.clear();
  state.ritmo = ''; state.duracao = ''; state.licenca = '';
  state.withImg = false; state.withVideo = false;
  // reset UI
  document.querySelectorAll('.sidebar .chip[aria-pressed="true"]').forEach(c => c.setAttribute('aria-pressed','false'));
  document.querySelectorAll('.sidebar [role="checkbox"][aria-checked="true"]').forEach(c => c.setAttribute('aria-checked','false'));
  document.getElementById('searchBoxInput').value = '';
  // sliders back to limits
  setSlider('aderencia',   1, 5, 1);
  setSlider('viabilidade', 1, 5, 1);
  setSlider('dificuldade', 5, 5, 5);
  setSlider('tos',         5, 5, 5);
  // selects
  ['ritmo','duracao','licenca'].forEach(k => setSelectValue(k, ''));
  render();
}

// ============================================================
// Render principal (cards + counters + summary)
// ============================================================
let _filteredList = [];

function render() {
  const list = DATA.filter(matchesExplore).sort((a, b) => {
    const av = sortKeyExplore(a), bv = sortKeyExplore(b);
    if (av < bv) return -1;
    if (av > bv) return 1;
    return 0;
  });
  _filteredList = list;
  const slice = list.slice(0, 500); // cap render

  document.getElementById('cardGrid').innerHTML = slice.map(cardHTML).join('') ||
    `<p style="grid-column:1/-1;color:var(--fg-muted);font-family:var(--font-mono);font-size:13px;padding:48px;text-align:center">Nenhum jogo bate os filtros. Tente afrouxar.</p>`;

  updateCounters(list.length);
  updateSummaryBar(list.length);
}

// ============================================================
// Render: rankings
// ============================================================
function renderRankCategoria() {
  const list = [...DATA].sort((a, b) => rankSortValue(a, state.rankDim) - rankSortValue(b, state.rankDim))
                        .slice(0, state.rankN);
  document.getElementById('rankedList').innerHTML = list.map(rankedHTML).join('');
  document.getElementById('rkBread2').textContent = RANK_LABEL[state.rankDim];
  document.getElementById('rkBread3').textContent = `Top ${state.rankN}`;
}

function renderRankBuilder() {
  const list = [...DATA];
  list.forEach(e => { e._bscore = builderScore(e); });
  list.sort((a, b) => b._bscore - a._bscore);
  const slice = list.slice(0, state.rankN);
  document.getElementById('builderList').innerHTML = slice.map(rankedHTML).join('');
  // formula
  const w = state.weights;
  const fmt = (v, sign) => `<span class="${sign}">${sign==='pos'?'+':'−'} ${v}</span>`;
  document.getElementById('builderFormula').innerHTML =
    `<b>score</b> = `
    + `<span class="pos">🧠×${w.aderencia}</span> `
    + `<span class="pos">+ 🤖×${w.viabilidade}</span> `
    + `<span class="neg">− ⚙️×${w.dificuldade}</span> `
    + `<span class="neg">− ⚖️×${w.tos}</span> `
    + `<span class="pos">+ 🔥×${w.popularidade}</span> `
    + `<span class="pos">+ 🎨×${w.qualidade}</span>`;
  document.getElementById('builderHeading').innerHTML =
    `<span class="n">${slice.length}</span> resultados <span class="muted-tag">peso custom</span>`;
}

// ============================================================
// Modal
// ============================================================
let _modalIdx = -1;
let _modalScope = []; // lista visível no contexto (filtered ou ranked)

function openModal(id, scope) {
  const e = DATA.find(x => x.id === id);
  if (!e) return;
  _modalScope = scope || _filteredList;
  _modalIdx = _modalScope.findIndex(x => x.id === id);
  if (_modalIdx < 0) { _modalScope = [e]; _modalIdx = 0; }
  renderModalContent(e);
  document.getElementById('modalBackdrop').setAttribute('data-open', 'true');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalBackdrop').setAttribute('data-open', 'false');
  document.body.style.overflow = '';
  // pause iframe by removing src
  const iframe = document.querySelector('.modal-video iframe');
  if (iframe) iframe.src = '';
}

function modalIsOpen() {
  return document.getElementById('modalBackdrop').getAttribute('data-open') === 'true';
}

function modalNav(delta) {
  if (!_modalScope.length) return;
  _modalIdx = (_modalIdx + delta + _modalScope.length) % _modalScope.length;
  renderModalContent(_modalScope[_modalIdx]);
  document.getElementById('modal').scrollTop = 0;
}

function scaleHTML(v, max) {
  v = v || 0; max = max || 5;
  return `<span class="scale">${Array.from({length: max}, (_, i) =>
    `<span class="b ${i < v ? 'on' : ''}"></span>`).join('')}</span> ${v} / ${max}`;
}

function renderModalContent(e) {
  const plats = (e.plataforma || '').split('|').map(x => x.trim()).filter(Boolean);
  const platBadges = plats.map(p => {
    const code = PLAT_MAP[p] || p.slice(0, 3).toUpperCase();
    return `<span class="plat" data-p="${code}" title="${escape(PLAT_FULL[p] || p)}">${code}</span>`;
  }).join('');
  const dilemas = (e.dilemas_compativeis || '').split('|').map(x => x.trim()).filter(Boolean);
  const dilemaPills = dilemas.map(d =>
    `<span class="dilema match" title="${escape(DILEMA_DESCR[d] || d)}">${d}</span>`).join('');
  const links = (e.links || []).filter(Boolean);
  const imgs = (e.imagens || []).filter(Boolean);

  // header
  document.getElementById('modalPos').textContent = String(_modalIdx + 1);
  document.getElementById('modalTotal').textContent = String(_modalScope.length);
  document.getElementById('modalTitle').textContent = e.nome || '';

  // video
  const videoBox = document.querySelector('.modal-video');
  if (e.video_youtube_id) {
    videoBox.innerHTML = `<iframe src="https://www.youtube.com/embed/${escape(e.video_youtube_id)}?rel=0" allow="encrypted-media" allowfullscreen></iframe>`;
  } else if (imgs.length) {
    videoBox.innerHTML = `<div class="placeholder" style="background-image:url('${escape(imgs[0])}');background-size:cover;background-position:center;width:100%;height:100%;opacity:.7"></div>`;
  } else {
    videoBox.innerHTML = `<div class="placeholder"><span>sem mídia disponível</span></div>`;
  }

  // body
  document.getElementById('modalMeta').innerHTML =
    `${escape(e.genero || '?')}${e.engine_tech ? ' · ' + escape(e.engine_tech) : ''}${e.ano_lancamento ? ' · ' + escape(e.ano_lancamento) : ''}`;
  document.getElementById('modalPlatRow').innerHTML = platBadges;
  document.getElementById('modalDesc').textContent = e.observacoes || e.raciocinio_dificuldade || e.exemplo_concreto || e.genero || '';

  const quote = e.exemplo_concreto;
  document.getElementById('modalQuote').style.display = quote ? '' : 'none';
  if (quote) {
    document.getElementById('modalQuoteText').textContent = quote;
  }

  // dl
  document.getElementById('modalDL').innerHTML = `
    <dt>id</dt><dd>${escape(e.id || '')}</dd>
    <dt>dev/publisher</dt><dd>${escape(e.dev_publisher || '?')}</dd>
    <dt>plataforma</dt><dd>${escape(e.plataforma || '?')}</dd>
    <dt>score</dt><dd><b>${(e.score || 0).toFixed(2)}</b></dd>
    <dt>aderência</dt><dd>${scaleHTML(e.aderencia_psyfun, 5)}</dd>
    <dt>viabilidade</dt><dd>${scaleHTML(e.viabilidade_claude, 5)}</dd>
    <dt>dificuldade</dt><dd>${scaleHTML(e.dificuldade, 5)}</dd>
    <dt>esforço</dt><dd>${escape(e.esforco_horas || '?')} · ${escape(ESF_LABEL[e.esforco_horas] || '')}</dd>
    <dt>risco ToS</dt><dd>${scaleHTML(e.risco_tos, 5)}</dd>
    <dt>qualidade</dt><dd>${e.qualidade_producao ? '🎨'.repeat(e.qualidade_producao) : '—'} ${e.raciocinio_qualidade ? '· ' + escape(e.raciocinio_qualidade) : ''}</dd>
    <dt>popularidade</dt><dd>${e.pop_score >= 1 ? '⭐'.repeat(Math.round(e.pop_score)) + ' · ' : ''}${escape(e.popularidade || '—')}</dd>
    <dt>método mod</dt><dd>${escape(e.metodo_modificacao || '?')}</dd>
    <dt>status código</dt><dd>${escape(e.status_codigo || '?')}</dd>
    <dt>visualização</dt><dd>${escape(e.visualizacao || '—')}</dd>
    <dt>modo</dt><dd>${escape(e.modo_jogo || '—')}</dd>
    <dt>tema</dt><dd>${escape(e.tema || '—')}</dd>
    <dt>ritmo · duração</dt><dd>${escape(e.ritmo || '—')} · ${escape(e.duracao || '—')}</dd>
    <dt>licença</dt><dd>${escape(e.licenca || '—')}</dd>
    <dt>idade público</dt><dd>${escape(e.idade_publico || '—')}</dd>
    <dt>requisitos</dt><dd>${escape(e.requisitos_tecnicos || '—')}</dd>
    <dt>custo</dt><dd>${escape(e.custo_licencas || '—')}</dd>
    <dt>raciocínio</dt><dd>${escape(e.raciocinio_dificuldade || '—')}</dd>
    <dt>fonte (agente)</dt><dd>${escape(e.fonte_agente || '?')}</dd>
    <dt>dilemas</dt><dd style="display:flex;flex-wrap:wrap;gap:4px">${dilemaPills}</dd>
  `;

  // gallery
  document.getElementById('modalGallery').innerHTML = imgs.length
    ? imgs.slice(0, 6).map(i => `<div class="shot" style="background-image:url('${escape(i)}')"></div>`).join('')
    : '';
  document.getElementById('modalGallery').style.display = imgs.length ? '' : 'none';

  // links
  const linksHTML = links.map(l => {
    let host = l;
    try { host = new URL(l).hostname.replace(/^www\./, ''); } catch (_) {}
    return `<a class="modal-link" href="${escape(l)}" target="_blank" rel="noopener">${escape(host)} <span class="arr">↗</span></a>`;
  }).join('');
  const linksEl = document.getElementById('modalLinks');
  linksEl.innerHTML = linksHTML;
  linksEl.style.display = linksHTML ? '' : 'none';
}

// ============================================================
// Command palette
// ============================================================
const paletteBackdrop = () => document.getElementById('paletteBackdrop');
const paletteInput = () => document.getElementById('paletteInput');

function openPalette() {
  paletteBackdrop().setAttribute('data-open', 'true');
  setTimeout(() => paletteInput().focus(), 50);
  refreshPalette('');
}
function closePalette() {
  paletteBackdrop().setAttribute('data-open', 'false');
  paletteInput().value = '';
}
function paletteIsOpen() {
  return paletteBackdrop().getAttribute('data-open') === 'true';
}

function refreshPalette(q) {
  q = (q || '').toLowerCase().trim();
  let games;
  if (q) {
    games = DATA.filter(e => (e.nome || '').toLowerCase().includes(q)
        || (e.genero || '').toLowerCase().includes(q)
        || (e.engine_tech || '').toLowerCase().includes(q)).slice(0, 8);
  } else {
    games = [..._filteredList].slice(0, 6);
  }

  const gameRows = games.map(e => `
    <div class="palette-row" role="option" data-act="open" data-game="${escape(e.id)}">
      <span class="ico score">${(e.score || 0).toFixed(1)}</span>
      <span class="label">${escape(e.nome)} <em>${escape(e.genero || '')}${e.visualizacao ? ' · ' + escape(e.visualizacao) : ''}</em></span>
      <span class="hint">abrir detalhe</span>
      <span class="kbd">↵</span>
    </div>`).join('');

  const actions = [
    { ico:'→', label:'Ir para <em style="color:var(--accent)">Rankings</em>', hint:'nav', act:'goto-rankings' },
    { ico:'★', label:'Ir para <em style="color:var(--accent)">Builder</em>', hint:'nav', act:'goto-builder' },
    { ico:'×', label:'Limpar todos os filtros', hint:'reset', act:'reset' },
  ];
  const actionRows = actions.map(a => `
    <div class="palette-row" role="option" data-act="${a.act}">
      <span class="ico">${a.ico}</span>
      <span class="label">${a.label}</span>
      <span class="hint">${a.hint}</span>
      <span class="kbd">↵</span>
    </div>`).join('');

  const body = document.getElementById('paletteBody');
  body.innerHTML = `
    ${games.length ? `<div class="palette-group-h">Jogos · ${games.length}</div>${gameRows}` : ''}
    <div class="palette-group-h">Ações · ${actions.length}</div>
    ${actionRows}
  `;
  setPaletteSelected(0);
}

function paletteRows() {
  return [...document.querySelectorAll('.palette-row')].filter(r => r.offsetParent !== null);
}
function setPaletteSelected(idx) {
  const rows = paletteRows();
  if (!rows.length) return;
  idx = Math.max(0, Math.min(idx, rows.length - 1));
  rows.forEach((r, i) => r.setAttribute('aria-selected', i === idx ? 'true' : 'false'));
  rows[idx].scrollIntoView({ block: 'nearest' });
}
function selectedPaletteIdx() {
  return paletteRows().findIndex(r => r.getAttribute('aria-selected') === 'true');
}

function paletteAct(row) {
  const act = row.dataset.act;
  if (act === 'open') {
    const id = row.dataset.game;
    closePalette();
    openModal(id);
  } else if (act === 'goto-rankings') {
    closePalette();
    switchPanel('rankings');
    switchRankSub('categoria');
  } else if (act === 'goto-builder') {
    closePalette();
    switchPanel('rankings');
    switchRankSub('builder');
  } else if (act === 'reset') {
    closePalette();
    clearAllFilters();
  }
}

// ============================================================
// Sidebar setup (chips, sliders, selects, toggles)
// ============================================================
function setSlider(key, val, max, displayVal) {
  // val: numeric, max: numeric (5), displayVal: shown in slider-value
  const slider = document.querySelector(`[data-slider="${key}"]`);
  if (!slider) return;
  const pct = ((val - 1) / (max - 1)) * 100;
  slider.querySelector('.slider-fill').style.width = pct + '%';
  slider.querySelector('.slider-thumb').style.left = pct + '%';
  slider.querySelector('.slider-value').textContent = `${displayVal != null ? displayVal : val} / ${max}`;
}

function setSelectValue(key, val) {
  const sel = document.querySelector(`[data-select="${key}"]`);
  if (!sel) return;
  sel.querySelector('.select-value').textContent = val || 'qualquer';
  sel.dataset.value = val;
}

function buildChipGrid(containerId, items, attr, set, labelFn) {
  const c = document.getElementById(containerId);
  if (!c) return;
  c.innerHTML = items.map(v =>
    `<button class="chip chip-sm" type="button" aria-pressed="false" data-${attr}="${escape(v)}" title="${escape(v)}">${escape((labelFn || (x => x))(v))}</button>`
  ).join('');
  c.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const cur = chip.getAttribute('aria-pressed') === 'true';
      chip.setAttribute('aria-pressed', cur ? 'false' : 'true');
      const v = chip.dataset[attr];
      if (cur) set.delete(v); else set.add(v);
      render();
    });
  });
}

function buildSelect(key, options) {
  const sel = document.querySelector(`[data-select="${key}"]`);
  if (!sel) return;
  // we keep it as button + popover. Popover is a hidden <ul>
  let pop = sel.querySelector('.select-pop');
  if (!pop) {
    pop = document.createElement('ul');
    pop.className = 'select-pop';
    pop.setAttribute('role', 'listbox');
    sel.appendChild(pop);
  }
  pop.innerHTML = `<li role="option" data-v="">qualquer</li>` +
    options.map(o => `<li role="option" data-v="${escape(o)}">${escape(o)}</li>`).join('');
  pop.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', e => {
      e.stopPropagation();
      const v = li.dataset.v;
      state[key] = v;
      setSelectValue(key, v);
      pop.classList.remove('open');
      render();
    });
  });
  sel.addEventListener('click', e => {
    e.stopPropagation();
    document.querySelectorAll('.select-pop.open').forEach(p => { if (p !== pop) p.classList.remove('open'); });
    pop.classList.toggle('open');
  });
}

document.addEventListener('click', () => {
  document.querySelectorAll('.select-pop.open').forEach(p => p.classList.remove('open'));
});

// Slider drag interactions (value stored in state[key])
function wireSlider(key, stateKey, min, max, isMax) {
  const slider = document.querySelector(`[data-slider="${key}"]`);
  if (!slider) return;
  const update = (clientX) => {
    const rect = slider.querySelector('.slider-track').getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const val = Math.round(min + pct * (max - min));
    state[stateKey] = val;
    setSlider(key, val, max);
    render();
  };
  let dragging = false;
  slider.querySelector('.slider-track').addEventListener('mousedown', e => {
    dragging = true; update(e.clientX);
    e.preventDefault();
  });
  document.addEventListener('mousemove', e => { if (dragging) update(e.clientX); });
  document.addEventListener('mouseup', () => { dragging = false; });
  // touch
  slider.querySelector('.slider-track').addEventListener('touchstart', e => {
    if (!e.touches.length) return;
    dragging = true; update(e.touches[0].clientX); e.preventDefault();
  }, { passive: false });
  document.addEventListener('touchmove', e => {
    if (dragging && e.touches.length) update(e.touches[0].clientX);
  }, { passive: true });
  document.addEventListener('touchend', () => { dragging = false; });
}

// Builder slider (0-5 weights)
function wireBuilderSlider(key) {
  const w = document.querySelector(`.weight[data-w="${key}"]`);
  if (!w) return;
  const update = (clientX) => {
    const rect = w.querySelector('.slider-track').getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const val = Math.round(pct * 5);
    state.weights[key] = val;
    w.querySelector('.slider-fill').style.width = (val / 5 * 100) + '%';
    w.querySelector('.slider-thumb').style.left = (val / 5 * 100) + '%';
    w.querySelector('.v').textContent = val;
    if (state.rankSub === 'builder') renderRankBuilder();
  };
  let dragging = false;
  w.querySelector('.slider-track').addEventListener('mousedown', e => { dragging = true; update(e.clientX); e.preventDefault(); });
  document.addEventListener('mousemove', e => { if (dragging) update(e.clientX); });
  document.addEventListener('mouseup', () => { dragging = false; });
}

// ============================================================
// Tabs / panels / sub-tabs
// ============================================================
function switchPanel(target) {
  state.panel = target;
  document.querySelectorAll('.app-tab').forEach(b =>
    b.setAttribute('aria-current', b.dataset.tab === target ? 'true' : 'false'));
  document.querySelectorAll('.panel').forEach(p =>
    p.setAttribute('data-active', p.dataset.panel === target ? 'true' : 'false'));
  if (target === 'rankings') {
    if (state.rankSub === 'categoria') renderRankCategoria();
    else renderRankBuilder();
  }
  window.scrollTo({ top: 0, behavior: 'instant' });
}

function switchRankSub(target) {
  state.rankSub = target;
  document.querySelectorAll('[data-rktab]').forEach(b =>
    b.setAttribute('aria-current', b.dataset.rktab === target ? 'true' : 'false'));
  document.querySelectorAll('[data-rksub]').forEach(s =>
    s.style.display = s.dataset.rksub === target ? '' : 'none');
  document.getElementById('rkBread1').textContent =
    target === 'categoria' ? 'Categoria' : 'Builder';
  if (target === 'categoria') renderRankCategoria();
  else renderRankBuilder();
}

// ============================================================
// Init
// ============================================================
function initSidebar() {
  // search input
  document.getElementById('searchBoxInput').addEventListener('input', e => {
    state.q = e.target.value; render();
  });

  // dilema chips (fixed list)
  document.querySelectorAll('#dilemaChips .chip').forEach(c => {
    c.addEventListener('click', () => {
      const cur = c.getAttribute('aria-pressed') === 'true';
      c.setAttribute('aria-pressed', cur ? 'false' : 'true');
      const d = c.dataset.d;
      if (cur) state.dilemas.delete(d); else state.dilemas.add(d);
      render();
    });
  });

  // sliders
  wireSlider('aderencia',   'minAderencia',   1, 5);
  wireSlider('viabilidade', 'minViabilidade', 1, 5);
  wireSlider('dificuldade', 'maxDificuldade', 1, 5, true);
  wireSlider('tos',         'maxRisco',       1, 5, true);
  // initial values
  setSlider('aderencia',   state.minAderencia,   5);
  setSlider('viabilidade', state.minViabilidade, 5);
  setSlider('dificuldade', state.maxDificuldade, 5);
  setSlider('tos',         state.maxRisco,       5);

  // dynamic chips from data
  buildChipGrid('chipsMetodo',       uniq(DATA.map(e => e.metodo_modificacao)), 'met', state.metodos, x => x.replace(/-/g,' '));
  buildChipGrid('chipsStatus',       uniq(DATA.map(e => e.status_codigo)),      'sta', state.statuses, x => x.replace(/-/g,' '));
  buildChipGrid('chipsEsforco',      ['XS','S','M','L','XL'],                   'esf', state.esforcos, x => ESF_LABEL[x] || x);
  buildChipGrid('chipsVisualizacao', multiValues('visualizacao'),               'vis', state.visualizacoes, x => x.replace(/-/g,' '));
  buildChipGrid('chipsModo',         multiValues('modo_jogo'),                  'mod', state.modos, x => MODE_LABEL[x] || x);
  buildChipGrid('chipsGenero',       multiValues('genero_tag'),                 'gen', state.generos, x => x.replace(/-/g,' '));
  buildChipGrid('chipsTema',         multiValues('tema'),                       'tem', state.temas, x => x.replace(/-/g,' '));

  // selects
  buildSelect('ritmo',   uniq(DATA.map(e => e.ritmo)));
  buildSelect('duracao', uniq(DATA.map(e => e.duracao)));
  buildSelect('licenca', uniq(DATA.map(e => e.licenca)));

  // toggles
  document.querySelectorAll('[role="checkbox"][data-toggle]').forEach(t => {
    const flip = () => {
      const cur = t.getAttribute('aria-checked') === 'true';
      t.setAttribute('aria-checked', cur ? 'false' : 'true');
      const k = t.dataset.toggle;
      if (k === 'img')   state.withImg = !cur;
      if (k === 'video') state.withVideo = !cur;
      render();
    };
    t.addEventListener('click', flip);
    t.addEventListener('keydown', e => {
      if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); }
    });
  });
}

function initSortRow() {
  document.querySelectorAll('[data-sort]').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('[data-sort]').forEach(x =>
        x.setAttribute('aria-current', x === b ? 'true' : 'false'));
      state.sortBy = b.dataset.sort;
      render();
    });
  });
}

function initTabs() {
  document.querySelectorAll('.app-tab').forEach(b => {
    b.addEventListener('click', () => switchPanel(b.dataset.tab));
  });
  document.querySelectorAll('[data-rktab]').forEach(b => {
    b.addEventListener('click', () => switchRankSub(b.dataset.rktab));
  });
  document.querySelectorAll('[data-topn]').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('[data-topn]').forEach(x =>
        x.setAttribute('aria-current', x === b ? 'true' : 'false'));
      state.rankN = parseInt(b.dataset.topn);
      if (state.rankSub === 'categoria') renderRankCategoria();
      else renderRankBuilder();
    });
  });
  document.querySelectorAll('#dimGrid .dim').forEach(b => {
    b.addEventListener('click', () => {
      document.querySelectorAll('#dimGrid .dim').forEach(x =>
        x.setAttribute('aria-pressed', x === b ? 'true' : 'false'));
      state.rankDim = b.dataset.dim;
      renderRankCategoria();
    });
  });
  // builder weight sliders
  ['aderencia','viabilidade','dificuldade','tos','popularidade','qualidade'].forEach(wireBuilderSlider);
}

function initModal() {
  document.getElementById('modalClose').addEventListener('click', closeModal);
  document.getElementById('modalPrev').addEventListener('click', () => modalNav(-1));
  document.getElementById('modalNext').addEventListener('click', () => modalNav(+1));
  document.getElementById('modalBackdrop').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });
}

function initPalette() {
  document.getElementById('cmdTrigger').addEventListener('click', openPalette);
  paletteBackdrop().addEventListener('click', e => {
    if (e.target === e.currentTarget) closePalette();
  });
  paletteInput().addEventListener('input', () => refreshPalette(paletteInput().value));
  // delegated row click
  document.getElementById('paletteBody').addEventListener('click', e => {
    const row = e.target.closest('.palette-row');
    if (row) paletteAct(row);
  });
}

function initMobileMenu() {
  const sb = document.getElementById('sidebar');
  document.getElementById('mobileMenuBtn').addEventListener('click', () => {
    const open = sb.getAttribute('data-open') === 'true';
    sb.setAttribute('data-open', open ? 'false' : 'true');
  });
}

function initCardClicks() {
  document.getElementById('cardGrid').addEventListener('click', e => {
    const card = e.target.closest('.card');
    if (card) openModal(card.dataset.id, _filteredList);
  });
  document.getElementById('rankedList').addEventListener('click', e => {
    const row = e.target.closest('.ranked-row');
    if (row) openModal(row.dataset.id, _modalScopeForRank());
  });
  document.getElementById('builderList').addEventListener('click', e => {
    const row = e.target.closest('.ranked-row');
    if (row) openModal(row.dataset.id, _modalScopeForRank());
  });
}

function _modalScopeForRank() {
  if (state.rankSub === 'categoria') {
    return [...DATA].sort((a,b) => rankSortValue(a,state.rankDim) - rankSortValue(b,state.rankDim))
                    .slice(0, state.rankN);
  }
  return [...DATA].map(e => (e._bscore = builderScore(e), e)).sort((a,b) => b._bscore - a._bscore).slice(0, state.rankN);
}

function initKeyboard() {
  document.addEventListener('keydown', e => {
    const tag = document.activeElement?.tagName;
    const typing = tag === 'INPUT' || tag === 'TEXTAREA';

    // ⌘K / Ctrl+K — palette toggle
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      paletteIsOpen() ? closePalette() : openPalette();
      return;
    }

    // / — focus search (when not typing)
    if (e.key === '/' && !typing && !modalIsOpen() && !paletteIsOpen()) {
      e.preventDefault();
      document.getElementById('searchBoxInput').focus();
      return;
    }

    // Esc — close overlays
    if (e.key === 'Escape') {
      if (paletteIsOpen()) { closePalette(); return; }
      if (modalIsOpen())   { closeModal();   return; }
    }

    // Modal nav
    if (modalIsOpen()) {
      if (e.key === 'ArrowLeft')  { e.preventDefault(); modalNav(-1); }
      if (e.key === 'ArrowRight') { e.preventDefault(); modalNav(+1); }
      return;
    }

    // Palette nav
    if (paletteIsOpen()) {
      const rows = paletteRows();
      let idx = selectedPaletteIdx();
      if (e.key === 'ArrowDown') { e.preventDefault(); setPaletteSelected(idx + 1); }
      if (e.key === 'ArrowUp')   { e.preventDefault(); setPaletteSelected(idx - 1); }
      if (e.key === 'Enter')     { e.preventDefault(); rows[Math.max(idx, 0)]?.click(); }
      return;
    }

    // Card grid arrow nav
    if (typing) return;
    const grid = document.getElementById('cardGrid');
    if (grid && grid.contains(document.activeElement) && document.activeElement.classList.contains('card')) {
      const cards = [...grid.querySelectorAll('.card')];
      const cur = cards.indexOf(document.activeElement);
      const cols = Math.max(1, Math.floor(grid.getBoundingClientRect().width / 380));
      let target = cur;
      if (e.key === 'ArrowRight') target = Math.min(cur + 1, cards.length - 1);
      if (e.key === 'ArrowLeft')  target = Math.max(cur - 1, 0);
      if (e.key === 'ArrowDown')  target = Math.min(cur + cols, cards.length - 1);
      if (e.key === 'ArrowUp')    target = Math.max(cur - cols, 0);
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault(); document.activeElement.click(); return;
      }
      if (target !== cur) {
        e.preventDefault(); cards[target].focus();
      }
    }
  });
}

// ============================================================
// Boot
// ============================================================
initSidebar();
initSortRow();
initTabs();
initModal();
initPalette();
initMobileMenu();
initCardClicks();
initKeyboard();
render();
