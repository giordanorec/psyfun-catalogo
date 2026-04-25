# HANDOFF — Redesign v4 via claude.ai/design

> Documento único e auto-suficiente pra uma sessão Claude Code (com Chrome
> ativo) operar claude.ai/design e gerar uma versão visualmente radical
> do dashboard PsyFun. Construído pra ser colado num `claude --chrome`.

---

## 1. O que você vai fazer (em alto nível)

1. Ler este brief + os 6 arquivos listados em §2 pra ter contexto total.
2. Abrir **https://claude.ai/design** no Chrome via `claude_in_chrome`
   (usuário já está logado).
3. Submeter o prompt de design montado em §5.
4. Iterar com variações até aprovar (máx 3 rodadas pra preservar tokens).
5. Exportar como **Handoff Bundle** (zip com HTML/CSS/React + DESIGN.md).
6. Salvar o bundle em `/home/grec/Projetos/psyfun-catalogo/handoff/v4-<timestamp>.zip`.
7. Avisar o Giordano que o bundle está pronto — ele vai redirecionar pra
   outra sessão (esta ou uma nova) implementar.

**NÃO implemente o código localmente aqui.** Seu papel nesta sessão é
**pilotar claude.ai/design** e trazer o handoff. Implementação é fase
separada.

---

## 2. Leia antes de qualquer ação

Ordem obrigatória, cada um por Read tool:

1. `/home/grec/Projetos/psyfun-catalogo/README.md`
   — visão de alto nível do catálogo e deployment.

2. `/home/grec/Projetos/psyfun-catalogo/meta/VOCABULARIO.md`
   — vocabulário controlado do domínio (dilemas, métodos, dificuldade).

3. `/home/grec/Projetos/psyfun-catalogo/meta/FINALISTAS.md` (primeiros 300 linhas só)
   — análise dos top 25 jogos. Dá tom + exemplos concretos.

4. `/home/grec/Documentos/claude-design-vault/README.md`
   — índice do vault de design.

5. `/home/grec/Documentos/claude-design-vault/handoff-templates/brief-template.md`
   — template de brief que vamos instanciar abaixo.

6. `/home/grec/Documentos/claude-design-vault/design-systems/README.md`
   + os específicos que vão guiar:
   - `design-systems/linear.md` (command-driven · dark produto)
   - `design-systems/stripe.md` (editorial autoritário)
   - `design-systems/arc-raycast.md` (backdrop blur · cinematic)
   - `design-systems/editorial-awwwards.md` (typography kinética)

7. `/home/grec/Documentos/claude-design-vault/principles/color.md`,
   `principles/spacing-and-rhythm.md`, `principles/motion.md`
   — regras universais.

Essa leitura leva ~5 min. Não pule.

---

## 3. Estado atual do site (o que existe hoje)

- Produção: **https://catalogpsyfun.vercel.app**
- Repo: **github.com/giordanorec/psyfun-catalogo**, branch `main`.
- Stack: **HTML + JS vanilla + CSS inline**, single file
  `public/index.html` (~1.5MB com JSON embedded).
- Dados: 1202 jogos em `public/data/CONSOLIDADO.jsonl`.
- Versão atual do dashboard (v3) tem:
  - Header sticky + duas abas **Explorar** / **Rankings**.
  - Sidebar esquerda (340px) com muitos filtros.
  - Grid responsivo de cards (min 340px).
  - Modal de detalhe com vídeo YouTube embedded, galeria, dl com todos
    campos.
  - Filtros: busca textual, 10 chips de dilemas, 4 sliders (aderência,
    viabilidade, dificuldade, risco ToS), chips multi pra método/status/
    esforço/gênero/visualização/modo/tema, selects pra ritmo/duração/
    licença, toggles "só com imagem" / "só com vídeo".
  - Rankings tem sub-abas "Categoria" (uma dimensão) e "Builder" (pesos).
  - Card mostra: cover + platform badges + score + nome + gênero +
    descrição 2 linhas + chips dilemas + métricas (🎨🧠🤖⚙️⏱️🔥⚖️).

Abra `https://catalogpsyfun.vercel.app` **no browser via claude_in_chrome**
e tire screenshot pra ver o estado atual antes de projetar a v4. Salve a
screenshot em `/tmp/psyfun-v3-current.png`.

---

## 4. Objetivo do redesign (v4)

**Um dashboard visualmente impactante de nível editorial internacional.**
O Giordano rejeitou explicitamente designs "genéricos / AI aesthetic".
Referências explícitas na conversa:

- **Linear** (dark, motion respeita o olho, keyboard-first)
- **Stripe Press** (serif display + sans body, hierarquia quieta)
- **Arc/Raycast** (backdrop-filter blur, gradient accent)
- **Sites premiados do Awwwards 2026** (typography-first, motion
  cinematográfico discreto)
- **Apple HIG** (materialidade, elevação via Z, respiração)

**Família estética a pedir no prompt do Claude Design:**

> "Editorial sério encontra command-driven. Dark-first. Display serif
> moderna (Instrument Serif ou Fraunces) nos títulos gigantes; Inter
> nas UI; JetBrains Mono em metadados/números. Accent único vibrante
> (escolha: laranja #ff9f43 do brand atual, ou arrisque um verde neon
> #4ade80 + segundo accent ciano #00d4ff). Backdrop-filter blur agressivo
> em modals. Motion 180-260ms com ease-out-back. Tipografia gigante no
> hero (72-120pt). Respiração generosa (space-24 entre seções)."

---

## 5. Prompt completo pra colar no claude.ai/design

Depois de abrir a aba "Design" em claude.ai, cole **isto**:

```
Vou projetar a v4 do dashboard do catálogo PsyFun — 1202 jogos
moddáveis pra pesquisa em dilemas sociais.

Stack atual: HTML + JS vanilla (single file). Usuário: pesquisadores
adultos universitários. Viewport: desktop 1440px primário, mobile 390px
secundário.

ESTÉTICA-ALVO: editorial sério encontra produto command-driven. Dark
first. Display SERIF moderna (Instrument Serif ou Fraunces) nos títulos
gigantes; Inter pra UI; JetBrains Mono pra metadados/números/badges.
Accent laranja vibrante #ff9f43 + secundário ciano #00d4ff. Backdrop-
filter blur agressivo (24-30px) em modals e surfaces flutuantes. Motion
180-260ms com ease-out-back. Tipografia gigante no hero (80-120pt).
Respiração generosa (96px entre seções). Inspirações: Linear + Stripe
Press + Arc/Raycast + Rauno.me.

SEÇÕES NECESSÁRIAS:

1. HEADER sticky:
   - Logo "PsyFun" em serif display
   - Nav tabs "Explorar" / "Rankings"
   - Busca global (command palette estilo cmd+K)
   - Counter "X / Y jogos"

2. SIDEBAR esquerda colapsável (320-360px), com filtros:
   - Busca textual
   - Chips toggle pra 10 dilemas (PD, PG, SH, UG, DG, SD, TG, CG, CPG, BG)
   - Sliders: aderência ≥, viabilidade ≥, dificuldade ≤, risco ToS ≤
   - Multi-chip pra método mod, status código, esforço (XS/S/M/L/XL),
     gênero, visualização (2d/3d/pixel-art), modo (single/coop/mmo/pvp),
     tema
   - Selects: ritmo, duração, licença
   - Toggles: só com imagem, só com vídeo

3. MAIN: grid responsivo de cards (min 340px). Cada card:
   - Cover image 16:9 OU thumbnail YouTube (quando jogo tem vídeo, com
     play button vermelho sobreposto)
   - Score badge laranja canto superior direito (15.10 formato)
   - Platform badges coloridos canto inferior esquerdo (WEB/WIN/MAC/LIN/
     AND/iOS/SW/PS/XB/VR/ALL, cada um com cor distinta)
   - Título (serif ou sans bold)
   - Meta linha (gênero · engine)
   - Descrição 2 linhas com ellipsis
   - Linha de métricas: 🎨 qualidade (estrelas), 🧠 aderência (1-5),
     🤖 viabilidade, ⚙️ dificuldade, ⏱️ esforço, 🔥 popularidade
     (estrelas), ⚖️ ToS (se ≥3)
   - Chips de dilemas compatíveis
   - Footer sutil "clique pra detalhes"

4. MODAL de detalhe (ao clicar em card):
   - Iframe YouTube gigante no topo (quando jogo tem video_youtube_id)
   - Galeria de imagens grid abaixo
   - Definition list com todos os metadados do jogo
   - Links externos no final
   - Navegação teclado: ← → trocam de jogo, Esc fecha
   - Backdrop-filter blur(30px) no fundo

5. MODO RANKINGS (segunda aba):
   - Sub-aba "Categoria": escolha UMA dimensão (score / aderência /
     viabilidade / menor dificuldade / menor esforço / menor ToS /
     popularidade / qualidade) + top N (10/25/50/100)
   - Sub-aba "Builder": sliders de peso 0-5 pra cada dimensão (🧠 🤖 ⚙️
     ⚖️ 🔥 🎨), gera ranking custom
   - Breadcrumb mostrando modo ativo

RESTRIÇÕES:
- Mobile-first responsivo (breakpoint 900px)
- Navegação por teclado obrigatória (setas entre cards, Enter abre, Esc
  fecha)
- WCAG AA em todo texto
- Respeitar prefers-reduced-motion
- Bundle CSS ≤ 50KB, JS inline OK (o modelo atual embeda 1.5MB JSON)
- Single-page HTML + CSS + JS vanilla (sem React/Tailwind deps)

QUERO 3 VARIAÇÕES:

V1 "Editorial denso" — tipografia Instrument Serif 48pt nos nomes de
jogos, grid apertado, muito espaço entre seções, paleta escura quase
preta, accent laranja único. Vibe Stripe Press × Linear.

V2 "Command-driven hero" — hero gigante com counter animado "1202",
command palette estilo Arc/Raycast (cmd+K overlay full-screen), cards
com glass-morphism leve. Vibe Arc × Raycast.

V3 "Cinematic kinetic" — scroll-triggered reveals, tipografia variable
morphing no hover, imagens hero full-bleed com duotone, motion
expressiva. Vibe Awwwards 2026 × Rauno.me.

Pra cada V, entregue HTML + CSS standalone que eu possa abrir no browser
pra validar. Após eu escolher uma, exporte como Handoff Bundle completo.
```

**Anexe também** ao iniciar a conversa:
- `/tmp/psyfun-v3-current.png` (screenshot que você tirou em §3)
- Dados de amostra: copie as **primeiras 3 linhas** de
  `/home/grec/Projetos/psyfun-catalogo/public/data/CONSOLIDADO.jsonl`
  pra dar ao Claude Design exemplos reais de jogos.

---

## 6. Workflow no claude.ai/design

### Rodada 1 — wireframes
Depois do prompt acima, peça: "mostre primeiro os 3 wireframes em preto-
e-branco (só estrutura, sem tipografia ou cor). Quero validar hierarquia
antes de aplicar estilo."

### Rodada 2 — estilo
"Escolho V[1/2/3]. Agora aplique a estética completa."

### Rodada 3 — refinar
Ajustes pontuais específicos (ex: "card radius 12px não 6px").

### Export
"Exporte como Handoff Bundle completo, incluindo DESIGN.md, index.html
standalone, src/ se usar componentes, styles/tokens.css, assets/."

### Save
Baixe o zip. Salve em `/home/grec/Projetos/psyfun-catalogo/handoff/v4-$(date +%Y%m%d-%H%M).zip`.

Crie a pasta `handoff/` se não existir.

---

## 7. Entrega

Após salvar o bundle, rode:

```bash
mkdir -p /home/grec/Projetos/psyfun-catalogo/handoff
mv ~/Downloads/claude-design-*.zip /home/grec/Projetos/psyfun-catalogo/handoff/v4-$(date +%Y%m%d-%H%M).zip
ls -la /home/grec/Projetos/psyfun-catalogo/handoff/
```

Escreva no chat: "Handoff bundle v4 salvo em `handoff/v4-YYYYMMDD-HHMM.zip`.
Claude Code pode implementar agora."

Aí esta sessão do Giordano (ou outra) pega o bundle e segue
`meta/handoff-templates/implementation-template.md` (no vault).

---

## 8. O que NÃO fazer

- **Não edite** `public/index.html` nesta sessão. Seu papel é gerar o
  handoff, não implementar.
- **Não crie branch nem commit**. Implementação vira novo commit
  separado, gerenciado pela sessão de implementação.
- **Não exporte PDF** do Claude Design. Só Handoff Bundle.
- **Não perca tempo** com refinamento de fontes micro — Claude Code
  ajusta depois. Foque em hierarquia, layout, personalidade visual.
- **Não aceite gradient rainbow, motion infinito, lottie pesado, ou
  qualquer generic AI aesthetic**. Se Claude Design propor, rejeite e
  peça de novo.

---

## 9. Permissions pra Claude in Chrome

Este brief assume que `mcp__claude_in_chrome__*` tools estão disponíveis.
Se não estiverem, interrompa e avise o Giordano — talvez precise
reconectar a extensão com `/chrome` → "Reconnect".

Sites que precisam estar permitidos:
- `claude.ai` (específico `claude.ai/design`)
- `catalogpsyfun.vercel.app`

---

*Fim do brief. Boa sorte. O critério de sucesso é simples: bundle
salvo em `handoff/v4-*.zip` contendo design que o Giordano olhe e diga
"agora sim".*
