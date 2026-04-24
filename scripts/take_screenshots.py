#!/usr/bin/env python3
"""
Abre o dashboard.html local no Playwright e produz screenshots
anotados para o relatório técnico.

Cada screenshot tem callouts numerados (círculos vermelhos) com legendas
ao lado, injetados via DOM antes da captura. Os callouts são descritos
no texto do relatório usando os mesmos números.

Saídas em exports/screenshots/<nome>.png
"""
from __future__ import annotations
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path("/home/grec/Documentos/psyfun-jogos-research")
DASHBOARD = ROOT / "exports" / "dashboard.html"
OUT = ROOT / "exports" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


CALLOUT_CSS = """
.callout {
  position: absolute;
  z-index: 9999;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ff1744;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 18px;
  font-family: 'Inter', sans-serif;
  border: 3px solid #fff;
  box-shadow: 0 0 0 3px #ff1744, 0 4px 16px rgba(255,23,68,0.6), 0 2px 8px rgba(0,0,0,0.6);
  pointer-events: none;
}
.callout-label {
  position: absolute;
  z-index: 9998;
  background: #ff1744;
  color: #fff;
  padding: 6px 12px;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  font-weight: 600;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.6);
  pointer-events: none;
  max-width: 280px;
  line-height: 1.3;
}
.callout-label::before {
  content: "";
  position: absolute;
  width: 0; height: 0;
  border-style: solid;
}
/* label-right points left */
.callout-label.right::before { left: -8px; top: 50%; margin-top: -5px;
  border-width: 5px 8px 5px 0; border-color: transparent #ff1744 transparent transparent; }
.callout-label.left::before  { right: -8px; top: 50%; margin-top: -5px;
  border-width: 5px 0 5px 8px; border-color: transparent transparent transparent #ff1744; }
.callout-label.top::before   { bottom: -8px; left: 20px;
  border-width: 8px 5px 0 5px; border-color: #ff1744 transparent transparent transparent; }
.callout-label.bottom::before { top: -8px; left: 20px;
  border-width: 0 5px 8px 5px; border-color: transparent transparent #ff1744 transparent; }
"""


def add_callouts(page, callouts):
    """callouts = list of dict: {n:int, x:int, y:int, label:str, side:'right'|'left'|'top'|'bottom'}"""
    page.add_style_tag(content=CALLOUT_CSS)
    js = """(callouts) => {
      for (const c of callouts) {
        const dot = document.createElement('div');
        dot.className = 'callout';
        dot.textContent = String(c.n);
        dot.style.left = (c.x - 18) + 'px';
        dot.style.top = (c.y - 18) + 'px';
        document.body.appendChild(dot);

        const lbl = document.createElement('div');
        lbl.className = 'callout-label ' + (c.side || 'right');
        lbl.textContent = c.label;
        // posicionamento relativo ao dot
        if (c.side === 'right') {
          lbl.style.left = (c.x + 26) + 'px';
          lbl.style.top = (c.y - 13) + 'px';
        } else if (c.side === 'left') {
          lbl.style.right = (window.innerWidth - c.x + 26) + 'px';
          lbl.style.top = (c.y - 13) + 'px';
        } else if (c.side === 'top') {
          lbl.style.left = (c.x - 10) + 'px';
          lbl.style.top = (c.y - 60) + 'px';
        } else if (c.side === 'bottom') {
          lbl.style.left = (c.x - 10) + 'px';
          lbl.style.top = (c.y + 26) + 'px';
        }
        document.body.appendChild(lbl);
      }
    }"""
    page.evaluate(js, callouts)


def shot(page, name):
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=False)
    print(f"  {name}.png ({path.stat().st_size // 1024} KB)", flush=True)
    return path


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": 1600, "height": 1000},
            device_scale_factor=2,  # retina
        )
        page = ctx.new_page()
        page.goto(f"file://{DASHBOARD.resolve()}")
        page.wait_for_selector(".card", timeout=15000)
        page.wait_for_timeout(400)  # settle

        # --------- 1. Overview ---------
        print("1/6 overview …", flush=True)
        add_callouts(page, [
            {"n": 1, "x": 700, "y": 30,  "label": "Contador de resultados: filtrados / total", "side": "bottom"},
            {"n": 2, "x": 165, "y": 130, "label": "Busca textual (nome, gênero, engine, obs)",  "side": "right"},
            {"n": 3, "x": 165, "y": 195, "label": "Chips de dilemas: toggles OR-somáveis",      "side": "right"},
            {"n": 4, "x": 165, "y": 370, "label": "Sliders de aderência, viabilidade, dificuldade, ToS", "side": "right"},
            {"n": 5, "x": 165, "y": 600, "label": "Selects de método, status, esforço",          "side": "right"},
            {"n": 6, "x": 900, "y": 250, "label": "Card de jogo — cover + score + chips",        "side": "right"},
        ])
        shot(page, "01_overview")
        page.evaluate("() => document.querySelectorAll('.callout,.callout-label').forEach(e=>e.remove())")

        # --------- 2. Sidebar zoom ---------
        print("2/6 sidebar …", flush=True)
        page.set_viewport_size({"width": 400, "height": 1000})
        page.wait_for_timeout(300)
        add_callouts(page, [
            {"n": 1, "x": 195, "y": 130, "label": "Busca full-text",                      "side": "bottom"},
            {"n": 2, "x": 195, "y": 210, "label": "PD, PG, SH, UG, DG, SD, TG, CG, CPG, BG", "side": "bottom"},
            {"n": 3, "x": 195, "y": 380, "label": "Sliders operam OR sobre o catálogo",      "side": "bottom"},
            {"n": 4, "x": 195, "y": 770, "label": "Filtros de enum: método / status / esforço", "side": "top"},
            {"n": 5, "x": 195, "y": 925, "label": "Toggles: só com imagem / só top 100",         "side": "top"},
        ])
        shot(page, "02_sidebar")
        page.evaluate("() => document.querySelectorAll('.callout,.callout-label').forEach(e=>e.remove())")
        page.set_viewport_size({"width": 1600, "height": 1000})
        page.wait_for_timeout(300)

        # --------- 3. Card detalhado ---------
        print("3/6 card …", flush=True)
        # card é um .card no grid. Escolhe o primeiro e zooma.
        page.evaluate("""() => {
            document.body.style.background = '#0b0d12';
            const q = document.querySelector('main');
            q.scrollTop = 0;
        }""")
        page.wait_for_timeout(300)
        add_callouts(page, [
            {"n": 1, "x": 550, "y": 130,  "label": "Rank (implícito na ordem do grid)", "side": "right"},
            {"n": 2, "x": 780, "y": 175,  "label": "Score badge (laranja)", "side": "left"},
            {"n": 3, "x": 550, "y": 340,  "label": "Nome + meta (gênero · engine · plataforma)", "side": "right"},
            {"n": 4, "x": 550, "y": 395,  "label": "Chips de dilemas compatíveis (azul)", "side": "right"},
            {"n": 5, "x": 550, "y": 430,  "label": "Stats: ader · dif · viab · esforço", "side": "right"},
            {"n": 6, "x": 550, "y": 480,  "label": "Botão para abrir modal de detalhes", "side": "right"},
        ])
        shot(page, "03_card")
        page.evaluate("() => document.querySelectorAll('.callout,.callout-label').forEach(e=>e.remove())")

        # --------- 4. Modal aberto ---------
        print("4/6 modal …", flush=True)
        page.evaluate("() => document.querySelector('.card .expand').click()")
        page.wait_for_timeout(600)
        add_callouts(page, [
            {"n": 1, "x": 800, "y": 130, "label": "Título + score no header do modal", "side": "bottom"},
            {"n": 2, "x": 800, "y": 280, "label": "Galeria de imagens (grid responsivo)", "side": "right"},
            {"n": 3, "x": 800, "y": 560, "label": "Definition list com todos os campos",  "side": "right"},
            {"n": 4, "x": 800, "y": 880, "label": "Links clicáveis (site oficial, docs, repo)", "side": "right"},
        ])
        shot(page, "04_modal")
        page.evaluate("() => document.querySelectorAll('.callout,.callout-label').forEach(e=>e.remove())")
        page.evaluate("() => document.querySelector('.modal-backdrop').classList.remove('open')")
        page.wait_for_timeout(400)

        # --------- 5. Filtro aplicado: só dilema PD + aderência 4+ ---------
        print("5/6 filtro aplicado …", flush=True)
        page.evaluate("""() => {
            // simula click no chip PD
            const chip = [...document.querySelectorAll('.chip')].find(c => c.dataset.dil === 'PD');
            chip && chip.click();
            // aderência mínima = 4
            const r = document.getElementById('min-aderencia');
            r.value = 4; r.dispatchEvent(new Event('input', {bubbles:true}));
        }""")
        page.wait_for_timeout(500)
        add_callouts(page, [
            {"n": 1, "x": 95, "y": 210,  "label": "Chip PD ativo (laranja)",        "side": "right"},
            {"n": 2, "x": 165, "y": 370, "label": "Aderência ≥ 4 aplicado",          "side": "right"},
            {"n": 3, "x": 700, "y": 30,  "label": "Contador reduziu de 1202 para filtrados", "side": "bottom"},
            {"n": 4, "x": 900, "y": 260, "label": "Grid refaz — só jogos que casam PD com aderência alta", "side": "right"},
        ])
        shot(page, "05_filtro")
        page.evaluate("() => document.querySelectorAll('.callout,.callout-label').forEach(e=>e.remove())")

        # --------- 6. Mobile ---------
        print("6/6 mobile …", flush=True)
        page.set_viewport_size({"width": 400, "height": 900})
        # limpa filtros
        page.evaluate("""() => {
            document.querySelectorAll('.chip.active').forEach(c => c.click());
            const r = document.getElementById('min-aderencia');
            r.value = 1; r.dispatchEvent(new Event('input', {bubbles:true}));
        }""")
        page.wait_for_timeout(400)
        add_callouts(page, [
            {"n": 1, "x": 200, "y": 90,  "label": "Layout mobile: sidebar empilha no topo", "side": "bottom"},
            {"n": 2, "x": 200, "y": 420, "label": "Grid single-column, cards mantém cover + stats", "side": "top"},
        ])
        shot(page, "06_mobile")

        browser.close()
        print("\nTodas as 6 screenshots salvas em", OUT)


if __name__ == "__main__":
    main()
