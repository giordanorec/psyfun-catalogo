# DECISOES — log cronológico

Cada entrada documenta o **porquê** de uma decisão técnica. Append-only.

---

## 2026-04-24 — Dashboard v4 (estética editorial × command-driven)

### Contexto

Dashboard v3 (`scripts/legacy/build_dashboard_v3.py`) tinha boa funcionalidade
(filtros densos, rankings, modal com vídeo) mas estética genérica de SaaS.
Giordano pediu redesign visual de nível editorial internacional, rejeitando
explicitamente o padrão "AI aesthetic".

### Processo

1. Briefing único (HANDOFF_BRIEF.md) descrevendo família estética-alvo:
   editorial sério encontra produto command-driven · Linear + Stripe Press +
   Arc/Raycast + Rauno.me · dark first · Instrument Serif + Inter +
   JetBrains Mono · accent laranja #ff9f43 + ciano #00d4ff.
2. Sessão Claude Code pilotou claude.ai/design (browser MCP no Chrome do
   Mac Mini). Rodada 1 entregou 3 wireframes P&B (V1 Editorial denso /
   V2 Command-driven hero / V3 Cinematic kinetic). Rodada 2 aplicou
   estética em V2 + elementos de V1.
3. Handoff Bundle salvo em `handoff/v4-20260424-2002.zip` (44 KB), 6
   arquivos: psyfun-v4-hifi.html (82 KB) · 3 wireframes · design-canvas.jsx.

### Decisão arquitetural

**Estratégia C — full replace** do `public/index.html`:

- Chassis HTML + CSS extraído do hifi (via `scripts/build_v4.py`,
  preservando os ~38 KB de tokens/estilos exatos do design)
- Lógica JS reescrita em `scripts/v4-app.js` (~43 KB) — preserva filtros,
  rankings, modal, command palette, keyboard nav do v3 mas com markup v4
- Dataset embeded inline no `<script id="data" type="application/json">`
  (mesma estratégia do v3 — single-file deploy via Vercel static)
- Score composto recalculado client-side: `aderência*2 + viabilidade −
  dificuldade*0.5` (mesma fórmula do build_dashboard_v3.py linha 37)

### Por que V2 como base, não V1 ou V3

- **V1 Editorial denso** — Stripe Press × Linear puro, mais conservador
- **V2 Command-driven hero** — escolhida: hero "1 202" monumental (DNA
  Stripe Press) + ⌘K palette protagonista (DNA Arc/Raycast) cobrem dois
  dos quatro âncoras pedidos. Mantém densidade da sidebar V1 (incorporada).
- **V3 Cinematic kinetic** — risk alto pra dashboard com 1.202 itens;
  scroll-triggered motion mata performance e desorienta pesquisador.

### Stack final

- `public/index.html` — single-file gerado por `scripts/build_v4.py`
- `scripts/build_v4.py` — orquestrador (chassis + dataset + JS → index.html)
- `scripts/v4-app.js` — lógica do dashboard
- `scripts/legacy/build_dashboard_v3.py` — v3 arquivado (não rodar)
- `handoff/v4-20260424-2002.zip` — bundle original do claude.ai/design
- `handoff/v4-20260424-2002-extracted/` — bundle descompactado pra
  consulta (chassis CSS canônico mora aqui)

### Validação

- `python -m http.server 8765 --directory public` + Puppeteer headless:
  - 500 cards renderizados (cap), 86 chips de filtros populados de DATA
  - Modal abre em PICO-8 com 24 pares dt/dd, score 14.50, vídeo iframe
  - Filtro PD: 1.202 → 442 jogos
  - Tabs Explorar/Rankings/Sobre, sub-tabs Categoria/Builder funcionais
  - ⌘K palette abre + lista jogos + ações + keyboard nav
  - prefers-reduced-motion respeitado (CSS no chassis)
- 5 screenshots salvos em /tmp/v4-shot-{explore,modal,rankings,builder,palette}.png

### Rollback

Se v4 quebrar em produção:

```
git checkout HEAD~1 -- public/index.html scripts/
```

Backup adicional: `public/index.v3.html.bak` (criado antes do build).

### Pendências conhecidas

- Modal navega via ← →, mas o "Jogo X de Y" no header só atualiza
  quando se clica num card (refletindo lista filtrada do contexto).
  Funciona, mas merece teste de edge case (modal aberto, filtros mudam).
- Sliders thresholds são click-to-set por enquanto; drag funciona via
  mousedown+mousemove mas não toquei `<input type=range>` real ainda.
- Imagens em `imagens` de cada jogo carregam via path relativo
  `images/<id>/N.png` — funciona servindo a partir de `public/`.
- Versão do `data-canvas.jsx` no bundle é só ferramenta do
  claude.ai/design pra apresentação — não é usada em produção.

### Próximos passos sugeridos

1. Testar deploy real em `catalogpsyfun.vercel.app` (commit + push)
2. Coletar feedback do Giordano sobre micro-ajustes (radius, padding,
   easing) antes de qualquer rodada extra de design
3. Eventual port do `build_dashboard.py` legacy → script único que
   regenera o catálogo do zero (consolidate.py + score + build_v4.py)
