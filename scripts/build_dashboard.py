#!/usr/bin/env python3
"""
Gera exports/dashboard.html — single-file, zero-build, filtros facetados client-side.

Lê CONSOLIDADO.jsonl e embarca dados como JSON inline.

Filtros:
- busca textual (nome, gênero, observações)
- chips por dilema compatível (PD, PG, SH, UG, DG, SD, TG, CG)
- slider dificuldade (1-5)
- slider aderência PsyFun (1-5)
- slider viabilidade Claude (1-5)
- select método_modificação
- select status_código
- select esforço
- toggle "apenas com imagens"
- toggle "risco ToS ≤ 2"

Visualização: grid de cards com imagem, nome, score, badges de dilemas, método, score,
link para detalhes expansíveis.
"""
import json
import html
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
            # Ajusta paths de imagens pra serem relativos ao dashboard.html (em exports/)
            e["imagens"] = ["../" + p for p in (e.get("imagens") or [])]
            entries.append(e)

    # score
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
header .counters { color: var(--fg-muted); font-size: 13px; }
header .counters strong { color: var(--accent); font-weight: 700; }

.layout { display: grid; grid-template-columns: 320px 1fr; gap: 0; min-height: calc(100vh - 60px); }
aside {
  background: var(--bg-soft); border-right: 1px solid var(--border);
  padding: 20px; overflow-y: auto; max-height: calc(100vh - 60px); position: sticky; top: 60px;
}
aside h3 { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--fg-muted); margin: 20px 0 8px; }
aside h3:first-child { margin-top: 0; }

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
  user-select: none;
}
.chip.active { background: var(--accent); color: #1a1000; border-color: var(--accent); font-weight: 600; }

.range-row { display: flex; align-items: center; gap: 10px; margin: 6px 0; }
.range-row label { min-width: 120px; font-size: 12px; color: var(--fg-muted); }
.range-row input[type=range] { flex: 1; accent-color: var(--accent); }
.range-row .val { min-width: 24px; text-align: right; font-size: 13px; color: var(--fg); }

.toggle { display: flex; align-items: center; gap: 8px; margin: 8px 0; font-size: 13px; }
.toggle input { accent-color: var(--accent); }

main { padding: 24px; overflow-y: auto; }
#stats { color: var(--fg-muted); font-size: 13px; margin-bottom: 14px; }

#grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }
.card {
  background: var(--bg-soft); border: 1px solid var(--border); border-radius: 8px;
  overflow: hidden; display: flex; flex-direction: column; transition: border-color .15s, transform .05s;
}
.card:hover { border-color: var(--accent); }
.card .cover { aspect-ratio: 16/9; background: var(--bg-elev) center/cover no-repeat; position: relative; }
.card .cover.no-img { display: flex; align-items: center; justify-content: center; color: var(--fg-muted); font-size: 12px; }
.card .cover .score-badge {
  position: absolute; top: 8px; right: 8px; background: rgba(255,159,67,.95); color: #1a1000;
  padding: 3px 8px; border-radius: 4px; font-weight: 700; font-size: 12px;
}
.card .body { padding: 10px 12px; flex: 1; display: flex; flex-direction: column; }
.card .title { font-weight: 600; margin-bottom: 4px; }
.card .sub { font-size: 11px; color: var(--fg-muted); margin-bottom: 6px; }
.card .dilemas { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.card .dilemas span {
  background: var(--bg-elev); color: var(--blue); padding: 1px 6px; border-radius: 3px;
  font-size: 10px; font-weight: 600;
}
.card .meta { font-size: 11px; color: var(--fg-muted); margin-top: auto; padding-top: 6px; }
.card button.expand {
  background: transparent; border: 0; color: var(--accent); padding: 6px 12px;
  font-size: 12px; cursor: pointer; border-top: 1px solid var(--border);
}

/* modal */
.modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,.65); display: none; z-index: 20; }
.modal-backdrop.open { display: flex; align-items: center; justify-content: center; }
.modal {
  background: var(--bg-soft); border-radius: 10px; max-width: 900px; width: 90vw; max-height: 90vh;
  overflow-y: auto; border: 1px solid var(--border);
}
.modal header { position: sticky; top: 0; padding: 14px 20px; border-bottom: 1px solid var(--border); background: var(--bg-soft); }
.modal .body { padding: 20px; }
.modal .gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px; margin: 16px 0; }
.modal .gallery img { width: 100%; border-radius: 6px; }
.modal dl { display: grid; grid-template-columns: 170px 1fr; gap: 8px 16px; font-size: 14px; }
.modal dt { color: var(--fg-muted); }
.modal dd { margin: 0; }
.modal .close { background: transparent; border: 0; color: var(--fg); font-size: 24px; cursor: pointer; }
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
  <div class="counters"><strong id="count-visible">0</strong> de <strong id="count-total">0</strong> jogos</div>
</header>

<div class="layout">
  <aside>
    <h3>Busca</h3>
    <input type="search" id="q" placeholder="nome, gênero, engine…">

    <h3>Dilemas compatíveis</h3>
    <div class="chips" id="chips-dilemas"></div>

    <h3>Filtros numéricos</h3>
    <div class="range-row">
      <label>Aderência ≥</label>
      <input type="range" min="1" max="5" value="1" id="min-aderencia">
      <span class="val" id="val-aderencia">1</span>
    </div>
    <div class="range-row">
      <label>Viabilidade Claude ≥</label>
      <input type="range" min="1" max="5" value="1" id="min-viabilidade">
      <span class="val" id="val-viabilidade">1</span>
    </div>
    <div class="range-row">
      <label>Dificuldade ≤</label>
      <input type="range" min="1" max="5" value="5" id="max-dificuldade">
      <span class="val" id="val-dificuldade">5</span>
    </div>
    <div class="range-row">
      <label>Risco ToS ≤</label>
      <input type="range" min="1" max="5" value="5" id="max-risco">
      <span class="val" id="val-risco">5</span>
    </div>

    <h3>Método de modificação</h3>
    <select id="sel-metodo">
      <option value="">— qualquer —</option>
    </select>

    <h3>Status do código</h3>
    <select id="sel-status">
      <option value="">— qualquer —</option>
    </select>

    <h3>Esforço</h3>
    <select id="sel-esforco">
      <option value="">— qualquer —</option>
      <option value="XS">XS (&lt;10h)</option>
      <option value="S">S (10–40h)</option>
      <option value="M">M (40–160h)</option>
      <option value="L">L (160–480h)</option>
      <option value="XL">XL (&gt;480h)</option>
    </select>

    <h3>Opções</h3>
    <label class="toggle"><input type="checkbox" id="only-with-img">Apenas com imagem</label>
    <label class="toggle"><input type="checkbox" id="top100-only">Top 100 (por score)</label>
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
const DILEMA_NAMES = {PD:"Prisoner's Dilemma", PG:"Public Goods", SH:"Stag Hunt", UG:"Ultimatum", DG:"Dictator", SD:"Snowdrift", TG:"Trust", CG:"Commons", CPG:"Coordination", BG:"Bargaining"};

function uniq(arr){ return [...new Set(arr.filter(Boolean))].sort(); }

function populateSelects() {
  const sM = document.getElementById('sel-metodo');
  const sS = document.getElementById('sel-status');
  for (const m of uniq(DATA.map(e=>e.metodo_modificacao))) sM.insertAdjacentHTML('beforeend', `<option>${m}</option>`);
  for (const s of uniq(DATA.map(e=>e.status_codigo))) sS.insertAdjacentHTML('beforeend', `<option>${s}</option>`);
  const cd = document.getElementById('chips-dilemas');
  for (const d of DILEMAS) cd.insertAdjacentHTML('beforeend', `<div class="chip" data-dil="${d}" title="${DILEMA_NAMES[d]}">${d}</div>`);
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

function render() {
  const sortedData = sorted();
  let filtered = sortedData.filter(matches);
  if (state.top100) filtered = filtered.slice(0, 100);

  document.getElementById('count-visible').textContent = filtered.length;
  document.getElementById('count-total').textContent = DATA.length;

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
  const cover = (e.imagens && e.imagens[0]) ? `style="background-image:url('${e.imagens[0]}')"` : '';
  const noImg = (!e.imagens || e.imagens.length === 0) ? 'no-img' : '';
  const dils = (e.dilemas_compativeis||'').split('|').map(x=>x.trim()).filter(Boolean);
  div.innerHTML = `
    <div class="cover ${noImg}" ${cover}>
      ${noImg ? 'sem imagem' : ''}
      <div class="score-badge">${(e.score||0).toFixed(1)}</div>
    </div>
    <div class="body">
      <div class="title">${escape(e.nome)}</div>
      <div class="sub">${escape(e.genero||'?')} · ${escape(e.engine_tech||'?')} · ${escape(e.plataforma||'')}</div>
      <div class="dilemas">${dils.map(d=>`<span>${d}</span>`).join('')}</div>
      <div class="meta">ader ${e.aderencia_psyfun||'?'} · dif ${e.dificuldade||'?'} · viab ${e.viabilidade_claude||'?'} · esf ${e.esforco_horas||'?'}</div>
    </div>
    <button class="expand">ver detalhes →</button>
  `;
  div.querySelector('.expand').addEventListener('click', () => openModal(e));
  return div;
}

function escape(s) { return String(s||'').replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

function openModal(e) {
  const bg = document.getElementById('modal-backdrop');
  const dils = (e.dilemas_compativeis||'').split('|').map(x=>x.trim()).filter(Boolean);
  const imgs = e.imagens||[];
  const links = e.links||[];
  document.getElementById('modal').innerHTML = `
    <header>
      <div style="display:flex;justify-content:space-between;align-items:center">
        <h2 style="margin:0">${escape(e.nome)} <small style="color:var(--fg-muted);font-weight:400">(score ${(e.score||0).toFixed(2)})</small></h2>
        <button class="close" onclick="closeModal()">×</button>
      </div>
    </header>
    <div class="body">
      ${imgs.length ? `<div class="gallery">${imgs.map(i=>`<img src="${i}">`).join('')}</div>` : ''}
      <dl>
        <dt>ano/dev</dt><dd>${escape(e.ano_lancamento||'?')} · ${escape(e.dev_publisher||'?')}</dd>
        <dt>gênero</dt><dd>${escape(e.genero||'?')}</dd>
        <dt>engine/tech</dt><dd>${escape(e.engine_tech||'?')}</dd>
        <dt>plataforma</dt><dd>${escape(e.plataforma||'?')}</dd>
        <dt>status código</dt><dd>${escape(e.status_codigo||'?')}</dd>
        <dt>método mod</dt><dd>${escape(e.metodo_modificacao||'?')}</dd>
        <dt>dificuldade</dt><dd>${e.dificuldade||'?'} — ${escape(e.raciocinio_dificuldade||'')}</dd>
        <dt>esforço</dt><dd>${escape(e.esforco_horas||'?')}</dd>
        <dt>viabilidade Claude</dt><dd>${e.viabilidade_claude||'?'}</dd>
        <dt>aderência PsyFun</dt><dd>${e.aderencia_psyfun||'?'}</dd>
        <dt>dilemas</dt><dd>${dils.map(d=>`<span style="background:var(--bg-elev);padding:2px 6px;margin-right:4px;border-radius:3px;font-size:12px">${d} — ${DILEMA_NAMES[d]||''}</span>`).join('')}</dd>
        <dt>exemplo concreto</dt><dd>${escape(e.exemplo_concreto||'-')}</dd>
        <dt>popularidade</dt><dd>${escape(e.popularidade||'-')}</dd>
        <dt>idade público</dt><dd>${escape(e.idade_publico||'-')}</dd>
        <dt>requisitos</dt><dd>${escape(e.requisitos_tecnicos||'-')}</dd>
        <dt>custo/licenças</dt><dd>${escape(e.custo_licencas||'-')}</dd>
        <dt>risco ToS</dt><dd>${e.risco_tos||'?'}</dd>
        <dt>observações</dt><dd>${escape(e.observacoes||'-')}</dd>
        <dt>fonte (agente)</dt><dd>${escape(e.fonte_agente||'?')}</dd>
        <dt>links</dt><dd class="links">${links.map(l=>`<a href="${l}" target="_blank" rel="noopener">${new URL(l).hostname}</a>`).join('')}</dd>
      </dl>
    </div>
  `;
  bg.classList.add('open');
}
function closeModal() { document.getElementById('modal-backdrop').classList.remove('open'); }

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
