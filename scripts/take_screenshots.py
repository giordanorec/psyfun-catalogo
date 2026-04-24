#!/usr/bin/env python3
"""
Abre o dashboard.html local no Playwright e produz screenshots
anotados para o relatório técnico (v2: reflete as 5 melhorias UX).

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
  width: 36px; height: 36px;
  border-radius: 50%;
  background: #ff1744;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 18px;
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
  max-width: 320px;
  line-height: 1.3;
}
.callout-label::before {
  content: ""; position: absolute;
  width: 0; height: 0; border-style: solid;
}
.callout-label.right::before { left: -8px; top: 50%; margin-top: -5px;
  border-width: 5px 8px 5px 0; border-color: transparent #ff1744 transparent transparent; }
.callout-label.left::before  { right: -8px; top: 50%; margin-top: -5px;
  border-width: 5px 0 5px 8px; border-color: transparent transparent transparent #ff1744; }
.callout-label.top::before   { bottom: -8px; left: 20px;
  border-width: 8px 5px 0 5px; border-color: #ff1744 transparent transparent transparent; }
.callout-label.bottom::before { top: -8px; left: 20px;
  border-width: 0 5px 8px 5px; border-color: transparent transparent #ff1744 transparent; }

/* tooltip simulado estático (pra screenshot mostrando o hover) */
.fake-tooltip {
  position: absolute; z-index: 9997;
  background: #1f2937;
  color: #fff;
  padding: 7px 10px;
  font-family: ui-sans-serif, 'Inter', sans-serif;
  font-size: 12px;
  border-radius: 4px;
  border: 1px solid #374151;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  pointer-events: none;
  max-width: 320px;
  line-height: 1.4;
}
"""


def add_callouts(page, callouts):
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


def add_fake_tooltip(page, x, y, text):
    page.add_style_tag(content=CALLOUT_CSS)
    js = """({x, y, text}) => {
      const t = document.createElement('div');
      t.className = 'fake-tooltip';
      t.textContent = text;
      t.style.left = x + 'px';
      t.style.top = y + 'px';
      document.body.appendChild(t);
    }"""
    page.evaluate(js, {"x": x, "y": y, "text": text})


def clear_overlays(page):
    page.evaluate("""() => {
      document.querySelectorAll('.callout,.callout-label,.fake-tooltip').forEach(e => e.remove());
    }""")


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
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.goto(f"file://{DASHBOARD.resolve()}")
        page.wait_for_selector(".card", timeout=15000)
        page.wait_for_timeout(500)

        # --------- 1. Overview ---------
        print("1/6 overview …", flush=True)
        add_callouts(page, [
            {"n": 1, "x": 750, "y": 30,  "label": "Contador pulsa em laranja quando filtros alteram resultado", "side": "bottom"},
            {"n": 2, "x": 175, "y": 135, "label": "Busca full-text (nome, gênero, engine, dev, descrição)", "side": "right"},
            {"n": 3, "x": 175, "y": 210, "label": "Chips de dilemas com tooltip explicando o dilema ao passar o mouse", "side": "right"},
            {"n": 4, "x": 175, "y": 390, "label": "Sliders numéricos com tooltip explicando cada métrica", "side": "right"},
            {"n": 5, "x": 175, "y": 630, "label": "Selects com opções em linguagem humana (S = 10–40h, ~1 semana)", "side": "right"},
            {"n": 6, "x": 980, "y": 250, "label": "Card com cover, badges de plataforma, descrição e footer clicável", "side": "right"},
        ])
        shot(page, "01_overview")
        clear_overlays(page)

        # --------- 2. Sidebar + tooltip info simulado ---------
        print("2/6 sidebar …", flush=True)
        page.set_viewport_size({"width": 420, "height": 1000})
        page.wait_for_timeout(300)
        add_fake_tooltip(page, 110, 255,
            "Clique para ativar — filtra jogos que podem simular o dilema escolhido. "
            "Múltiplas seleções usam OR (qualquer um dos dilemas).")
        add_callouts(page, [
            {"n": 1, "x": 195, "y": 135, "label": "Ícone (i) → tooltip descreve o grupo de filtros", "side": "right"},
            {"n": 2, "x": 195, "y": 230, "label": "Hover em cada chip mostra o nome completo do dilema", "side": "right"},
            {"n": 3, "x": 50,  "y": 255, "label": "Tooltip nativo do browser (acima) ao passar mouse no chip", "side": "left"},
            {"n": 4, "x": 195, "y": 420, "label": "Cada slider também tem tooltip no hover sobre o label ou o input", "side": "right"},
            {"n": 5, "x": 195, "y": 930, "label": "Toggles com hint explicando quando usar", "side": "top"},
        ])
        shot(page, "02_sidebar")
        clear_overlays(page)
        page.set_viewport_size({"width": 1600, "height": 1000})
        page.wait_for_timeout(300)

        # --------- 3. Card detalhado (novas camadas) ---------
        print("3/6 card …", flush=True)
        # Scroll para o topo
        page.evaluate("() => { document.querySelector('main').scrollTop = 0; }")
        page.wait_for_timeout(300)
        add_callouts(page, [
            {"n": 1, "x": 900, "y": 180, "label": "Cover image (do próprio jogo, 16:9)", "side": "right"},
            {"n": 2, "x": 1110, "y": 155, "label": "Score composto no canto superior direito", "side": "left"},
            {"n": 3, "x": 740, "y": 300, "label": "NOVO: badges de plataforma (WEB/WIN/MAC/LIN/AND/iOS/SW/PS/XB/VR/ALL)", "side": "right"},
            {"n": 4, "x": 740, "y": 370, "label": "Título do jogo + gênero/engine", "side": "right"},
            {"n": 5, "x": 740, "y": 430, "label": "NOVO: descrição curta (2 linhas, do exemplo concreto)", "side": "right"},
            {"n": 6, "x": 740, "y": 490, "label": "Chips dos dilemas que o jogo suporta", "side": "right"},
            {"n": 7, "x": 740, "y": 525, "label": "Stats compactos em monospace", "side": "right"},
            {"n": 8, "x": 740, "y": 560, "label": "NOVO: footer clicável (card inteiro também é clicável + Enter)", "side": "right"},
        ])
        shot(page, "03_card")
        clear_overlays(page)

        # --------- 4. Modal aberto ---------
        print("4/6 modal …", flush=True)
        page.evaluate("() => document.querySelector('.card').click()")
        page.wait_for_timeout(600)
        add_callouts(page, [
            {"n": 1, "x": 850, "y": 145, "label": "Header com nome + score; fecha com × ou tecla Esc", "side": "bottom"},
            {"n": 2, "x": 850, "y": 330, "label": "Galeria de imagens (grid responsivo)", "side": "right"},
            {"n": 3, "x": 850, "y": 620, "label": "Todos os campos do schema: plataforma agora com badges também", "side": "right"},
            {"n": 4, "x": 850, "y": 900, "label": "Links clicáveis abrindo em nova aba", "side": "right"},
        ])
        shot(page, "04_modal")
        clear_overlays(page)
        page.evaluate("() => document.querySelector('.modal-backdrop').classList.remove('open')")
        page.wait_for_timeout(400)

        # --------- 5. Filtro aplicado + pulse ---------
        print("5/6 filtro aplicado …", flush=True)
        page.evaluate("""() => {
            const chip = [...document.querySelectorAll('.chip')].find(c => c.dataset.dil === 'PD');
            chip && chip.click();
            const r = document.getElementById('min-aderencia');
            r.value = 4; r.dispatchEvent(new Event('input', {bubbles:true}));
            // força pulse visível
            document.getElementById('counters').classList.add('pulse');
            document.getElementById('stats').classList.add('pulse');
        }""")
        page.wait_for_timeout(300)
        add_callouts(page, [
            {"n": 1, "x": 100, "y": 220, "label": "Chip PD ativo (laranja)", "side": "right"},
            {"n": 2, "x": 175, "y": 390, "label": "Aderência ≥ 4 aplicado", "side": "right"},
            {"n": 3, "x": 750, "y": 30,  "label": "Contador pulsa em amarelo-claro quando o número muda", "side": "bottom"},
            {"n": 4, "x": 980, "y": 260, "label": "Grid atualiza em tempo real — cards novos fazem fade-in", "side": "right"},
        ])
        shot(page, "05_filtro")
        clear_overlays(page)
        page.evaluate("""() => {
            document.getElementById('counters').classList.remove('pulse');
            document.getElementById('stats').classList.remove('pulse');
        }""")

        # --------- 6. Mobile ---------
        print("6/6 mobile …", flush=True)
        page.set_viewport_size({"width": 400, "height": 900})
        page.evaluate("""() => {
            document.querySelectorAll('.chip.active').forEach(c => c.click());
            const r = document.getElementById('min-aderencia');
            r.value = 1; r.dispatchEvent(new Event('input', {bubbles:true}));
        }""")
        page.wait_for_timeout(400)
        add_callouts(page, [
            {"n": 1, "x": 200, "y": 90,  "label": "Sidebar empilha no topo em viewport < 900px", "side": "bottom"},
            {"n": 2, "x": 200, "y": 430, "label": "Cards mantém platform badges + descrição em coluna única", "side": "top"},
        ])
        shot(page, "06_mobile")

        browser.close()
        print("\nTodas as 6 screenshots salvas em", OUT)


if __name__ == "__main__":
    main()
