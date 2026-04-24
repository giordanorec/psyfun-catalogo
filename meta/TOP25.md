# Top 25 finalistas — PsyFun

Pré-seleção para análise profunda.

---

### 1. Roblox Studio  _(score 15.10)_

- **Método**: `creative-mode-in-game` · **Dificuldade**: 1 · **Esforço**: `M` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|UG|DG|TG|CG|CPG
- **Engine/Tech**: Roblox · **Plataforma**: windows|mac|android|ios|switch|xbox|playstation · **Idade**: all-ages
- **Popularidade**: Roblox ~70M DAU
- **Raciocínio**: Luau (Lua variante); editor visual; pub infraestrutura hosted; docs massivas. Provavelmente cobrado por outro agente mas incluo pela relevância
- **Exemplo concreto**: Experiência custom em 1 semana; deploy zero. Publishable com 150M+ DAU
- **Obs**: Consolidador: pode duplicar com outro agent
- **Fonte**: `creative-platforms|sdk-aaa` · [link](https://create.roblox.com) · [link](https://create.roblox.com/docs) · [link](https://create.roblox.com/)

---
### 2. PICO-8  _(score 15.05)_

- **Método**: `creative-mode-in-game` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|SH|UG|DG|TG|CG|CPG|BG
- **Engine/Tech**: Lua fantasy console · **Plataforma**: windows|mac|linux|web · **Idade**: all-ages
- **Popularidade**: Itch.io 50k+ carts, comunidade gigantesca
- **Raciocínio**: Editor all-in-one, Lua simples, cart de 32k limitada — força minimalismo ideal pra dilema binário; 99% do workflow é Claude-friendly
- **Exemplo concreto**: Cartridge 2-jogadores local: cada um em split-screen pressiona botão A (cooperar) ou B (trair). Payoff visual em pixels. Template Slingshot-style em ~300 linhas Lua
- **Obs**: EXCELENTE pro piloto: limitação 32k força minimalismo coop/trair
- **Fonte**: `classic-reimpl` · [link](https://www.lexaloffle.com/pico-8.php)

---
### 3. Pyxel  _(score 15.02)_

- **Método**: `template-engine` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|SH|UG|DG|TG|CG|CPG|BG
- **Engine/Tech**: Python · **Plataforma**: windows|mac|linux|web · **Idade**: all-ages
- **Popularidade**: GitHub 15k+ stars
- **Raciocínio**: MIT, Python retro game engine, 16 cores, 256x256; Python = Claude friendly
- **Exemplo concreto**: Script Python ~200 linhas: 2p teclado compartilhado, cada rodada 2 botões. Logging via CSV
- **Obs**: Python nativo = ótimo pra Claude escrever do zero
- **Fonte**: `classic-reimpl` · [link](https://github.com/kitao/pyxel)

---
### 4. TIC-80  _(score 15.01)_

- **Método**: `creative-mode-in-game` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|SH|UG|DG|TG|CG|CPG|BG
- **Engine/Tech**: Lua/JS/Python/Fennel/Wren · **Plataforma**: windows|mac|linux|web|android|ios · **Idade**: all-ages
- **Popularidade**: GitHub 4k+ stars, 10k+ carts
- **Raciocínio**: MIT, open-source alternative to PICO-8, múltiplas linguagens; web export; editor all-in-one
- **Exemplo concreto**: Mesmo que PICO-8 mas grátis e open; cart 2p escolha binária
- **Obs**: MELHOR que PICO-8 pra pesquisa: open + grátis + multi-language
- **Fonte**: `classic-reimpl` · [link](https://tic80.com) · [link](https://github.com/nesbox/TIC-80)

---
### 5. Print-and-Play PG games (itch)  _(score 15.00)_

- **Método**: `template-engine` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PG|UG|DG
- **Engine/Tech**: papel + regras digitais · **Plataforma**: cross-platform · **Idade**: varies
- **Popularidade**: itch tag print-and-play ~3k jogos
- **Raciocínio**: Rules PDFs abertos, digitalização trivial
- **Exemplo concreto**: Public goods game P&P exata — digitalizar regras direto
- **Obs**: TOP PICK — P&P regras são especificação direta
- **Fonte**: `itch-source` · [link](https://itch.io/physical-games/tag-print-and-play)

---
### 6. Ren'Py Android template (VN engine)  _(score 15.00)_

- **Método**: `template-engine` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|UG|DG|TG|BG
- **Engine/Tech**: Ren'Py Python · **Plataforma**: android|ios|windows|linux|mac · **Idade**: varies
- **Popularidade**: usada em 1000s de VNs
- **Raciocínio**: Engine FOSS Ren'Py; scripting simples
- **Exemplo concreto**: VN engine permite criar Public Goods narrativo do zero — escolhas claras coop/trair com recompensas visuais
- **Obs**: Engine, nao jogo — mas potencialmente otima para pilotos
- **Fonte**: `mobile-foss` · [link](https://www.renpy.org) · [link](https://github.com/renpy/renpy)

---
### 7. Prisoner's Dilemma simulator (direct itch)  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD
- **Engine/Tech**: varies · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: ~20 entries 'prisoner dilemma'
- **Raciocínio**: Vários PD sims prontos no itch com source
- **Exemplo concreto**: Já é PD literal; só adicionar logging e polish
- **Obs**: TOP PICK direto
- **Fonte**: `itch-source` · [link](https://itch.io/games/tag-prisoners-dilemma)

---
### 8. PD visualizations (itch multi)  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|TG
- **Engine/Tech**: JS · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: nicho educational
- **Raciocínio**: Diversos visualizadores de PD/tournament no itch/web, todos FOSS
- **Exemplo concreto**: 
- **Obs**: 
- **Fonte**: `itch-source` · [link](https://itch.io/games/tag-prisoners-dilemma) · [link](https://axelrod.readthedocs.io/)

---
### 9. Stag Hunt direct FOSS  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: SH
- **Engine/Tech**: JS · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: nicho educational
- **Raciocínio**: 
- **Exemplo concreto**: Jogo já é SH literal
- **Obs**: 
- **Fonte**: `itch-source` · [link](https://itch.io/games/tag-stag-hunt)

---
### 10. Ultimatum Game sim (FOSS)  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: UG
- **Engine/Tech**: JS · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: nicho
- **Raciocínio**: 
- **Exemplo concreto**: 
- **Obs**: 
- **Fonte**: `itch-source` · [link](https://itch.io/games/tag-ultimatum)

---
### 11. Dictator Game direct FOSS  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: DG
- **Engine/Tech**: JS · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: nicho
- **Raciocínio**: 
- **Exemplo concreto**: 
- **Obs**: 
- **Fonte**: `itch-source` · [link](https://itch.io/games/tag-dictator)

---
### 12. Public Goods Game direct FOSS  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PG
- **Engine/Tech**: JS · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: nicho edu
- **Raciocínio**: 
- **Exemplo concreto**: 
- **Obs**: 
- **Fonte**: `itch-source` · [link](https://itch.io/games/tag-public-goods)

---
### 13. oTree Prisoner's Dilemma (sample)  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD
- **Engine/Tech**: Python/Django · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: parte do otree-core, usado em dezenas de papers
- **Raciocínio**: Sample app já implementado no otree_library. ~100 linhas. Claude adapta UI trivialmente.
- **Exemplo concreto**: Substituir botões Cooperate/Defect por pictogramas (caixa comum vs caixa própria) e mostrar payoffs visuais (frutas, moedas) sem números.
- **Obs**: Ponto de partida ideal. Payoff matrix editável em Constants.
- **Fonte**: `research-serious` · [link](https://github.com/oTree-org/otree_library) · [link](https://otree.readthedocs.io/en/latest/tutorial/prisoner.html)

---
### 14. oTree Public Goods Game  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PG
- **Engine/Tech**: Python/Django · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: sample oficial, referência em N papers
- **Raciocínio**: Sample oficial. Inputs de contribuição, multiplicador, redistribuição — tudo parametrizado.
- **Exemplo concreto**: Input slider de endowment para pool comum; visualizar como 'árvore compartilhada' que cresce com contribuição coletiva e frutifica para todos. Substitui número por animação.
- **Obs**: Linear VCM (Voluntary Contribution Mechanism) clássico. Fácil estender pra n rounds, punição, strangers vs partners.
- **Fonte**: `research-serious` · [link](https://github.com/oTree-org/otree_library/tree/master/public_goods)

---
### 15. oTree Ultimatum Game  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: UG
- **Engine/Tech**: Python/Django · **Plataforma**: web · **Idade**: 7+
- **Popularidade**: sample oficial
- **Raciocínio**: Proposer/responder two-page flow. Triviais de adaptar.
- **Exemplo concreto**: Pizza-slice divisor: proposer divide círculo em duas fatias; responder aceita/rejeita. Visual sem numeracia.
- **Obs**: Strategy method variant também incluído (responder pré-compromete thresholds).
- **Fonte**: `research-serious` · [link](https://github.com/oTree-org/otree_library/tree/master/ultimatum)

---
### 16. oTree Dictator Game  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: DG
- **Engine/Tech**: Python/Django · **Plataforma**: web · **Idade**: 7+
- **Popularidade**: sample oficial
- **Raciocínio**: App mais simples do oTree — 2 pages, 1 decisão.
- **Exemplo concreto**: Distribuir sementes entre o próprio saco e o saco do parceiro. Interface drag-and-drop, sem exibir números.
- **Obs**: Útil como baseline de altruísmo puro, controle para UG.
- **Fonte**: `research-serious` · [link](https://github.com/oTree-org/otree_library/tree/master/dictator)

---
### 17. oTree Trust Game (Berg-Dickhaut-McCabe)  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: TG
- **Engine/Tech**: Python/Django · **Plataforma**: web · **Idade**: all-ages
- **Popularidade**: sample oficial
- **Raciocínio**: App referência em otree_library. Investment multiplicado por 3, return decision pelo trustee.
- **Exemplo concreto**: Envio de 'energia' a aliado que amplifica 3x; aliado decide quanto devolver. Visual: feixe de luz que cresce ao atravessar o trustee.
- **Obs**: Também existe variant Trust with Punishment. Multi-round version disponível.
- **Fonte**: `research-serious` · [link](https://github.com/oTree-org/otree_library/tree/master/trust)

---
### 18. oTree Stag Hunt  _(score 15.00)_

- **Método**: `code-fork` · **Dificuldade**: 1 · **Esforço**: `XS` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: SH|CPG
- **Engine/Tech**: Python/Django · **Plataforma**: web · **Idade**: 7+
- **Popularidade**: sample comunitário
- **Raciocínio**: Matrix game com equilíbrio payoff-dominant vs risk-dominant. Simples.
- **Exemplo concreto**: Dois caçadores escolhem cervo (coop alto) ou lebre (sozinho seguro). Ícones animais, escolha por clique.
- **Obs**: Útil pra estudar coordenação vs cooperação.
- **Fonte**: `research-serious` · [link](https://github.com/oTree-org/otree_library)

---
### 19. Tabletop Simulator  _(score 14.90)_

- **Método**: `scripting-in-game` · **Dificuldade**: 2 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|UG|DG|TG|BG|CG|CPG
- **Engine/Tech**: Unity · **Plataforma**: windows|mac|linux · **Idade**: 10+
- **Popularidade**: Steam 87% 100k reviews, 5M+ copies
- **Raciocínio**: Lua scripting nativo in-game; tabelas, cards, dice; Workshop com 100k+ mods. Duplicata de party-multiplayer
- **Exemplo concreto**: Literalmente faz-se tabuleiros PD iterado, Ultimatum, Dictator em minutos. Duplicata — consolidador decide
- **Obs**: Duplicata — party-multiplayer já lista. Incluo pelo valor
- **Fonte**: `party-multiplayer|sdk-aaa|tabletop-digital` · [link](https://www.tabletopsimulator.com) · [link](https://api.tabletopsimulator.com) · [link](https://store.steampowered.com/app/286160)

---
### 20. Minetest  _(score 14.81)_

- **Método**: `mod-loader-oficial` · **Dificuldade**: 1 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|CG|SH|BG|TG
- **Engine/Tech**: C++ / Lua · **Plataforma**: windows|mac|linux|android · **Idade**: all-ages
- **Popularidade**: GitHub 10k+ stars, 2k+ mods
- **Raciocínio**: LGPLv2.1, Lua API enorme, servers públicos 100+ players, Minecraft-like mas MUITO mais mod-friendly que Minecraft
- **Exemplo concreto**: Mod Lua: chest compartilhado no spawn. Depositar recurso (PG) vs pegar (trair). Logs via Lua file IO
- **Obs**: CANDIDATO TOP: Lua fácil + multiplayer + 100% free
- **Fonte**: `classic-reimpl` · [link](https://www.minetest.net) · [link](https://github.com/minetest/minetest)

---
### 21. 0 A.D.  _(score 14.80)_

- **Método**: `mod-loader-oficial` · **Dificuldade**: 2 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|SH|CG|BG|PG
- **Engine/Tech**: Pyrogenesis (C++ / JS) · **Plataforma**: windows|mac|linux · **Idade**: 10+
- **Popularidade**: GitHub 2.8k+ stars, 500k+ downloads, lobby global ativo
- **Raciocínio**: GPL+CC, JavaScript mod API + XML data, multiplayer 8p lobby público; qualidade comercial
- **Exemplo concreto**: Mod JS em ingame market: alocar recursos pro tributo ao aliado (PG) vs tesouro pessoal (trair); logging fácil
- **Obs**: CANDIDATO TOP: qualidade AAA, JS mod, multiplayer real, grátis
- **Fonte**: `classic-reimpl|itch-source|party-multiplayer|tabletop-digital` · [link](https://play0ad.com) · [link](https://github.com/0ad/0ad) · [link](https://play0ad.com/)

---
### 22. Tabletop Simulator (Steam Workshop)  _(score 14.80)_

- **Método**: `scripting-in-game` · **Dificuldade**: 2 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD|PG|SH|UG|DG|SD|TG|CG|CPG|BG
- **Engine/Tech**: Unity / Lua · **Plataforma**: windows|mac|linux · **Idade**: all-ages
- **Popularidade**: 2M+ cópias, milhares de mods Workshop
- **Raciocínio**: Lua scripting oficial; milhares de mods abertos; Claude escreve direto.
- **Exemplo concreto**: Mesa custom com cartas coop/trair; Lua registra escolhas e envia para webhook.
- **Obs**: Provavelmente a plataforma mais direta pra protótipo tabletop de dilema.
- **Fonte**: `creative-platforms` · [link](https://steamcommunity.com/app/286160/workshop/)

---
### 23. Coup (FOSS clone)  _(score 14.80)_

- **Método**: `code-fork` · **Dificuldade**: 2 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: TG|PD
- **Engine/Tech**: Node + React · **Plataforma**: web · **Idade**: 13+
- **Popularidade**: Coup 1M+ cópias
- **Raciocínio**: Clones Coup existem.
- **Exemplo concreto**: Jogo de bluff/traição. Core é PD.
- **Obs**: Marca Indie Boards & Cards
- **Fonte**: `html5-web` · [link](https://github.com/topics/coup-game)

---
### 24. Spyfall (FOSS)  _(score 14.80)_

- **Método**: `code-fork` · **Dificuldade**: 2 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: TG|PD
- **Engine/Tech**: Node · **Plataforma**: web · **Idade**: 13+
- **Popularidade**: Spyfall 500k+ cópias
- **Raciocínio**: Clones FOSS.
- **Exemplo concreto**: Spy vs players.
- **Obs**: Social deduction
- **Fonte**: `html5-web` · [link](https://github.com/topics/spyfall)

---
### 25. Prisoner's Dilemma simulators (web)  _(score 14.80)_

- **Método**: `code-fork` · **Dificuldade**: 2 · **Esforço**: `S` · **Viab. Claude**: 5
- **Aderência PsyFun**: 5 · **Dilemas**: PD
- **Engine/Tech**: JS · **Plataforma**: web · **Idade**: 10+
- **Popularidade**: Nicky Case 15M+ visualizações
- **Raciocínio**: Nicky Case 'Evolution of Trust' é MIT.
- **Exemplo concreto**: Já é PD puro — base ideal pra comparar.
- **Obs**: Nicky Case trust é referência direta. Must-have!
- **Fonte**: `html5-web` · [link](https://github.com/ncase/trust) · [link](https://ncase.me/trust/)

---
