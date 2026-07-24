# Processo de Landing Page da agência (kit reutilizável)

Este é um PADRÃO para qualquer projeto: copie `.claude/`, `scripts/` e este
CLAUDE.md para a pasta do projeto novo e siga o pipeline. Nada aqui é
específico de um cliente.

## Como a tarefa chega (do analista, via pedido do dev)
O dev SEMPRE informa no pedido:
1. **Link do template** — demo do Envato ou site-modelo escolhido para o cliente
2. **Link do site/e-commerce do cliente** (quando existir)
3. **Doc (.docx)** — o que ele quer ou não, com prints anotados
4. **Assets** — imagens/banners numa pasta (ex.: `assets-analista/`)

Os links vêm do PEDIDO — os scripts não adivinham URLs; recebem por argumento.

## Organização das pastas
A RAIZ guarda só o kit reutilizável: `.claude/`, `scripts/`, `CLAUDE.md`.
**Cada landing gerada mora na sua própria subpasta** (nome do cliente), com
todos os seus insumos e entregáveis dentro. Ex.: `sonifarma/`.

```
LPS-JS1/
├── .claude/  scripts/  CLAUDE.md        ← kit (não mexer por cliente)
└── sonifarma/                            ← um projeto por pasta
    ├── assets-analista/  doc-analista/   ← insumos do analista
    ├── template.json  identidade.json  doc-analista/doc-analista.json
    └── index.html  enviar.php  (politica-de-privacidade.html)  ← entrega
```

## Pipeline (3 scripts → 2 agentes)

### Passo 1 — Extrair os insumos (rode DE DENTRO da pasta do cliente)
```bash
mkdir -p <cliente> && cd <cliente>      # tudo do projeto fica aqui dentro

# Estrutura da landing escolhida (template Envato/modelo) -> template.json
python ../scripts/scrape-template.py <url-do-template>

# Identidade do cliente: cores, fontes, logo, fatos, legal -> identidade.json
python ../scripts/scrape-cliente.py <url-do-site-ou-ecommerce-do-cliente>

# Briefing do analista: texto na ordem + prints extraídos
#   -> doc-analista.json + doc-analista-imgs/
python ../scripts/extrai-doc.py "caminho/do/briefing.docx"
```
No Windows deste ambiente, use `python` (Python 3.14.6); o comando `python3` não
está disponível. Dependências: `python -m pip install requests beautifulsoup4`
(o extrai-doc.py é 100% stdlib).

### Passo 2 — Implementar (agente `implementador-codex`)
Delega a construção ao Codex CLI usando os 3 JSONs + a skill
`.claude/skills/estrutura-landing/SKILL.md` como fonte de verdade.
Ele não escreve código — orquestra o Codex e confere.

### Passo 3 — Revisar (agente `revisor`)
Claude revisa contra a skill + o doc do analista, item por item, com
evidência (arquivo/linha). Veredito: APROVADO ou CORREÇÕES NECESSÁRIAS.

Para sites institucionais longos (20+ seções): use `implementador-site` /
`revisor-site` com a skill `estrutura-site`.

## Dois modos de rodar o pipeline
- **Modo Claude+Codex** (padrão): Claude Code orquestra os agentes
  `implementador-codex` (que chama o Codex) e `revisor`. Guia: `PROMPT.md`.
- **Modo Codex-only** (quem não tem Claude): os 3 scripts rodam igual
  (só precisam de `python`); o próprio **Codex** constrói E faz o
  autorreview contra o checklist abaixo, num único fluxo. Guia:
  `PROMPT-CODEX.md`.

As REGRAS desta CLAUDE.md valem para os dois modos — ela é a fonte única de
verdade. No modo Codex-only, o Codex deve LER este arquivo inteiro + a skill.

## Hierarquia de autoridade
1. **Doc do analista** (doc-analista.json + prints) — manda em tudo.
   A QUANTIDADE DE SEÇÕES da landing sempre vem do doc do analista
   (cada bloco/print dele = uma seção), não de um número fixo da skill.
2. **Template** (template.json) — dá a estrutura/ordem de seções
3. **Identidade do cliente** (identidade.json) — dá cores, fontes, fatos
4. **Assets do analista** — são as imagens a usar na página

## Logo e favicon do cliente (obrigatório)
O `scrape-cliente.py` BAIXA o logo e o favicon reais do cliente para
`<cliente>/identidade-visual/` e registra os caminhos em `identidade.json >
identidade_visual > logo_local / favicon_local`. A landing DEVE usar esses
arquivos — nunca recriar um logo textual nem inventar um favicon genérico.
Se `logo_local` vier vazio (site sem logo detectável), avise no relatório e
peça o logo ao analista; não invente. (Exceção consciente à regra de não
baixar imagens do site: logo e favicon SÃO a identidade da marca.)

## Regras invioláveis
- Nunca copiar textos verbatim nem baixar imagens de CONTEÚDO do template ou do
  site de origem (logo e favicon do cliente são a exceção — ver acima)
- A landing final é um único HTML autossuficiente (CSS/JS embutidos, sem recursos externos)
- Copy própria, identidade do CLIENTE
- **Assinatura da agência no rodapé (SEMPRE)**: o copyright de toda página
  traz, além do © do cliente, o crédito
  `Feito e Gerenciado por Assessoria de Marketing 360 Grupo IX` com hiperlink
  em "Grupo IX" (ou na frase) para https://grupoix.com.br
  (target="_blank" rel="noopener").

## Fidelidade visual (obrigatório)
1. **Escala tipográfica**: use os font-sizes de `template.json` >
   `design_tokens` como TETO. O h1 da landing não pode passar do h1 do
   template (ex.: template 63px → clamp com máximo ~63px, nunca 70+).
   Título gigante é o erro mais comum. Vale o mesmo para h2.
2. **Efeitos**: se `design_tokens.parallax_background_fixed` = true, as
   faixas de CTA com imagem de fundo usam `background-attachment: fixed`
   (com fallback `scroll` em telas touch/mobile via media query).
3. **Elementos flutuantes**: olhe o PRINT da seção e posicione cada
   card/badge como na referência (ex.: sobre a metade INFERIOR da foto).
   Card flutuante cobrindo o rosto de uma pessoa em foto é ERRO.
4. **Imagens fluidas**: o reset base DEVE ter `img{max-width:100%;height:auto}`.
   `<img>` com atributos width/height + largura fluida SEM `height:auto`
   estica a imagem (o atributo height vira altura fixa e mata o aspect-ratio).

## LGPD, cookies e formulários (obrigatório em TODA landing)
1. **Política de privacidade**: se o site original do cliente tiver
   (identidade.json > `politica_privacidade`), aponte o link para lá (footer,
   banner de cookies e formulário). Se NÃO tiver, crie
   `politica-de-privacidade.html` com base nas infos do cliente, conforme a
   LGPD (Lei 13.709/2018): dados coletados, finalidade (incl. marketing),
   base legal, compartilhamento, direitos do titular, contato do controlador.
2. **Banner de cookies**: sempre presente, na identidade visual do cliente,
   informando o uso de cookies/dados para marketing e análise (exigência
   LGPD + Google Consent Mode). Botões **Sim/Aceitar** e **Não/Recusar**
   (recusa real, não só fechar), link para a política, escolha persistida
   (localStorage) e reexibido só se não houver escolha.
3. **Formulários** — todo form da landing tem:
   - Checkbox obrigatório "Li e concordo com a Política de Privacidade"
     ANTES do botão de envio (consentimento LGPD);
   - **Honeypot** anti-bot (campo oculto que, se preenchido, descarta o envio);
   - Arquivo **PHP de disparo** junto da entrega (`enviar.php`): valida
     honeypot + consentimento no servidor, sanitiza os campos e dispara
     e-mail via mail(); o front tenta o POST ao PHP e segue o fluxo
     combinado (ex.: abrir WhatsApp) mesmo se o PHP não estiver hospedado.

## Checklist de aceite (o revisor cobra; no modo Codex-only, o Codex se autoavalia)
Cada item PASSOU/FALHOU com evidência. Se algo FALHOU, corrija e reavalie.

1. Nº e ordem das seções = doc do analista (não a skill).
2. Todos os itens exigidos no doc do analista presentes (leia os prints).
3. Identidade do cliente: paleta e fontes de `identidade.json`.
3b. Logo e favicon = os arquivos de `identidade-visual/` (logo_local/
    favicon_local), não recriados. FALHA se a página usar logo textual ou
    favicon genérico havendo arquivo baixado.
4. h1/h2 ≤ escala do template (`template.json > design_tokens`).
5. Parallax onde o template usa; sem esticar imagens (`height:auto`).
6. Cards flutuantes conforme o print (nunca sobre o rosto).
7. Um único CTA primário por seção (sem dois botões primários competindo).
8. Banner de cookies com Aceitar E Recusar reais + persistência localStorage.
9. Link de política de privacidade (do cliente ou criada) no footer, banner e form.
10. Form: checkbox de consentimento (required) + honeypot + `enviar.php`.
11. Assinatura "Feito e Gerenciado por Assessoria de Marketing 360 Grupo IX"
    com link para https://grupoix.com.br no rodapé.
12. Autossuficiente: um HTML, CSS/JS embutidos, sem recursos externos.
13. Funcional: serve HTTP 200; se houver `google-chrome`, tire um screenshot
    headless e OLHE a página (proporção/sobreposição/alinhamento).
