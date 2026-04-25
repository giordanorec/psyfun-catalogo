# Catálogo PsyFun — jogos moddáveis pra pesquisa em dilemas sociais

> Catálogo de 1202 jogos que podem ser modificados pra virar instrumentos de
> pesquisa em psicologia experimental. Foco: **dilemas sociais** (Prisoner's
> Dilemma, Public Goods, Stag Hunt, Ultimatum, Dictator, Snowdrift, Trust,
> Commons, Coordination, Bargaining). Construído pelo grupo PsyFun (UFPE /
> UNIVASF).

**[Acesse o dashboard →](https://catalogopsyfun.vercel.app)**

## O que é

Cada jogo do catálogo é avaliado segundo:

- **Método de modificação**: SDK oficial, mod loader, fork de código, template
  de engine, runtime hook, scripting nativo, engenharia reversa, etc.
- **Dificuldade** (1–5): quão técnico é entender o jogo e acertar a modificação.
- **Esforço** (XS a XL): horas de trabalho pra primeiro piloto rodando.
- **Viabilidade Claude** (1–5): o quanto um agente AI (Claude Code) consegue
  fazer sozinho sem expertise humana específica.
- **Aderência PsyFun** (1–5): quão natural é enxertar mecânica binária
  cooperar/trair no jogo.
- **Dilemas compatíveis**: lista de dilemas teóricos que o jogo suporta.
- **Risco ToS**: 1 = open-source puro; 5 = DMCA/banimento provável.

Vocabulário controlado completo em [meta/VOCABULARIO.md](meta/VOCABULARIO.md).

## Estrutura do repo

```
public/              # servido pelo Vercel (catalogopsyfun.vercel.app)
├── index.html       # dashboard facetado (filtros, busca, galeria)
├── images/          # ~1310 imagens de ~680 jogos
├── pdfs/            # TOP100.pdf, TOP25.pdf, FINALISTAS.pdf, RELATORIO.pdf
├── screenshots/     # 6 screenshots anotadas (usadas no RELATORIO.pdf)
└── data/            # CATALOGO.csv + CONSOLIDADO.jsonl (fonte canônica)

meta/                # documentos explicativos e análises
├── VOCABULARIO.md   # valores aceitos em cada coluna
├── SCHEMA.json      # JSON schema
├── SPEC_AGENTE.md   # briefing passado aos agentes de pesquisa
├── TOP100.md        # ranking por score composto
├── TOP25.md         # finalistas enxutos
├── FINALISTAS.md    # análise profunda dos 25 (1610 linhas)
└── RELATORIO_TECNICO.md  # relatório de construção do catálogo (1190 linhas)

scripts/             # pipeline de construção (reprodutibilidade)
├── consolidate.py   # merge + dedup dos JSONLs parciais
├── to_csv.py        # JSONL → CSV
├── rank_top.py      # score composto + corte top 100 / 25
├── fetch_images.py  # downloader (Steam, itch, GitHub, Wikipedia, DDG)
├── fetch_images_fallback.py
├── build_v4.py      # gera public/index.html (dashboard v4 — atual)
├── v4-app.js        # lógica JS do dashboard v4 (vanilla)
├── legacy/build_dashboard_v3.py  # v3 arquivado — não rodar
├── build_pdfs.py        # gera os 4 PDFs magazine-style (WeasyPrint)
├── take_screenshots.py  # screenshots anotadas do dashboard via Playwright
└── magazine.css         # CSS print gamer
```

### Regerar o dashboard

```bash
python scripts/build_v4.py
```

Lê `public/data/CONSOLIDADO.jsonl` + chassis em `handoff/v4-*/` + lógica em
`scripts/v4-app.js`, escreve `public/index.html`. Vercel serve direto de
`public/`.

## Como foi construído

1. **12 agentes paralelos** varreram 12 fontes distintas:
   `sdk-aaa`, `open-source`, `creative-platforms`, `engine-templates`,
   `html5-web`, `itch-source`, `classic-reimpl`, `research-serious`,
   `mobile-foss`, `party-multiplayer`, `reverse-gray`, `tabletop-digital`.
2. Cada agente produziu um `agents/<slug>.jsonl` (uma entrada por linha).
3. Consolidação: merge + dedup por nome normalizado → **1202 únicos**.
4. Ranking composto: `aderencia*2 + viabilidade − dificuldade*0.5 + bônus_pop + bônus_esforço`.
5. Download de imagens: 1ª passagem por links diretos (Steam/itch/GitHub) +
   fallback (Wikipedia/Steam search/DDG). Cobertura final: 679/1202 (57%).
6. Dashboard HTML facetado + 3 PDFs magazine-style.

## Licença

Este repositório (metadados, scripts, textos) é [CC BY 4.0](LICENSE).

Todas as imagens e citações de jogos são propriedade dos respectivos
publishers/desenvolvedores e foram usadas em **fair use** para fins de
catálogo editorial de pesquisa acadêmica. Se você é titular de algum
direito e quer que uma imagem seja removida, abra uma
[issue](https://github.com/giordanorec/psyfun-catalogo/issues/new).

## Próximos passos

- Rodar 2 pilotos em paralelo nos próximos 2-3 sprints:
  (a) **oTree Prisoner's Dilemma** — gold-standard metodológico.
  (b) **Pyxel custom** — valida pipeline visual próprio.
- Expandir cobertura de imagens via IGDB API + mobygames scraping.
- Abrir catálogo pra contribuições externas (fork → PR com novos jogos).

## Contato

PsyFun — LDAPP/UNIVASF × CIn/UFPE
Giordano Cabral · [grec@cin.ufpe.br](mailto:grec@cin.ufpe.br)
Guilherme Cabral · UNIVASF · LDAPP
