# Vocabulário controlado — catálogo PsyFun de jogos moddáveis

Use **exatamente** os valores abaixo. Qualquer valor fora → coloque em `observacoes`.

## `plataforma` (multivalor, separar por `|`)
`web` · `windows` · `mac` · `linux` · `android` · `ios` · `switch` · `playstation` · `xbox` · `vr` · `cross-platform`

## `status_codigo`
- `open-source` — código fonte aberto, licença permissiva ou copyleft
- `source-available` — código disponível mas licença restritiva (no commercial use, no redistribution)
- `sdk-oficial` — código fechado, mas fabricante provê SDK/API pública robusta pra modificar
- `modding-community` — código fechado, mas comunidade ativa desenvolveu ferramentas de mod (unofficial)
- `creative-platform` — jogo é plataforma pra criação de experiências dentro dele (Roblox, UEFN, Dreams)
- `closed-only` — código fechado, sem SDK, sem modding oficial — só via engenharia reversa

## `metodo_modificacao`
- `sdk-oficial` — fabricante provê SDK/editor (Skyrim Creation Kit, Source SDK, Riot DDragon)
- `mod-loader-oficial` — fabricante suporta mod loader (Forge, Fabric, Bukkit, RimWorld mods)
- `creative-mode-in-game` — editor dentro do próprio jogo (Roblox Studio, UEFN, Dreams, LittleBigPlanet)
- `code-fork` — fork de repo open-source e modificação direta
- `template-engine` — usar template/asset-pack como base em engine própria (Unity Asset Store, Unreal Marketplace, Construct/GDevelop templates)
- `runtime-hook` — injeção em runtime (DLL injection, ASM patching, memory editing — BepInEx, MelonLoader, Cheat Engine)
- `save-editor` — manipular save files (modificação indireta)
- `asset-swap` — trocar arquivos de asset (não muda lógica, só aparência)
- `scripting-in-game` — scripting suportado pelo jogo (Lua em Screeps/Gmod/Skyrim Papyrus, Python em Factorio via mod)
- `packet-intercept` — interceptação de rede ou proxy (risco ToS alto)
- `private-server` — rodar servidor próprio, cliente original vai contra ele
- `engenharia-reversa` — decompilação/debug do binário
- `api-publica` — jogo expõe API oficial pra consumo externo (Riot API, Discord Activities, Steam API)

## `dilemas_compativeis` (multivalor, separar por `|`)
- `PD` — Prisoner's Dilemma
- `PG` — Public Goods Game
- `SH` — Stag Hunt (cooperação coordenada)
- `UG` — Ultimatum Game
- `DG` — Dictator Game
- `SD` — Snowdrift / Chicken
- `TG` — Trust Game (investment game)
- `CG` — Commons (tragedy of commons / CPR)
- `CPG` — Coordination Game (pure coord, sem dilema)
- `BG` — Bargaining Game (negociação multi-round)

## `dificuldade` (1–5, só técnica/cognitiva)
- 1 — **muito fácil**: editor visual + docs oficiais + templates prontos prontos pra rodar (Roblox Studio, Unity Asset complete, Construct templates)
- 2 — **fácil**: código aberto limpo + linguagem mainstream + docs OK (Phaser game com source bem estruturado, Godot projects, Bukkit plugin)
- 3 — **médio**: SDK parcial / código complexo / precisa entender arquitetura (Minecraft Forge, UEFN scripting, OpenRA fork)
- 4 — **difícil**: modding hack / reverse partial / sem docs (DLL injection, BepInEx, Skyrim Papyrus profundo, packet analysis leve)
- 5 — **muito difícil**: engenharia reversa completa, memória, ASM, ou jogo sem nenhum ponto de entrada documentado

## `esforco_horas` (enum, estimativa bruta)
- `XS` — <10h
- `S` — 10–40h (~1 semana)
- `M` — 40–160h (~1 mês)
- `L` — 160–480h (~3 meses)
- `XL` — >480h

## `viabilidade_claude` (1–5)
Quão viável é Claude Code executar a modificação (com sub-agentes) sem intervenção humana não-trivial:
- 5 — totalmente viável, Claude edita código + testa + deploya sozinho
- 4 — viável com usuário rodando comandos locais (build/run/teste manual)
- 3 — parcialmente viável; Claude escreve patch mas usuário precisa expertise específica pra validar
- 2 — difícil; requer conhecimento de domínio humano (arte, level design, sound design) que Claude não faz bem
- 1 — inviável sem humano (eg. jogo que exige arte original, rede neural custom-treinada, hardware específico)

## `aderencia_psyfun` (1–5)
Quão natural é enxertar mecânica cooperar/trair no jogo (ref: Slingshot Challenge, Star Mines):
- 5 — jogo já tem dilema-like nativo (Among Us traidor/cooperador, Overcooked forced coop, Keep Talking & Nobody Explodes)
- 4 — jogo tem ação binária clara que mapeia pra coop/trair (tiro em alvo vs tiro cooperativo, rota A vs rota B)
- 3 — precisa enxertar mecânica mas jogo é neutro (sandbox, puzzle multi-player simples)
- 2 — mecânica de base é alheia mas dá pra mod forçar (racing, fighting — precisa mudar bastante)
- 1 — mecânica hostil ao dilema (single-player sem outro jogador, horror, narrative walking sim)

## `risco_tos` (1–5)
- 1 — zero risco: open-source, licença permite mod sem reservas
- 2 — baixo: SDK oficial + ToS claros permitindo uso pesquisa
- 3 — médio: modding community tolerado mas não oficial, pode haver cease-and-desist
- 4 — alto: packet intercept / private server / reverse engineering contra ToS
- 5 — crítico: DMCA likely, banimento de conta likely, uso legal questionável

## `idade_publico`
- `all-ages` · `7+` · `10+` · `12+` · `13+` · `16+` · `18+` · `mature`

## Campos livres
- `raciocinio_dificuldade`: texto curto (1-3 frases) justificando o score
- `exemplo_concreto`: 1-2 frases descrevendo *que modificação específica* poderia simular *qual dilema*. Ex: "Em Overcooked, modificar mecânica de serving pra que jogador A possa entregar prato pro pool comum (cooperar) ou pro seu próprio balcão (trair) simula Public Goods."
- `popularidade`: notação livre mas objetiva. Ex: "Steam 98% 450k reviews", "Roblox 150M DAU", "Metacritic 88", "YouTube 50M views"
- `observacoes`: qualquer nuance não coberta acima
