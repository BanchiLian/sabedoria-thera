# Como usar o kit para criar uma landing page (Claude + Codex)

Guia para qualquer desenvolvedor. O kit já está pronto: `.claude/` (agentes +
skills), `scripts/` (3 coletores) e `CLAUDE.md` (o processo). Você só precisa
dos insumos do analista e seguir os 4 passos abaixo dentro do Claude Code.

> **Só tem o Codex, sem Claude?** Use o `PROMPT-CODEX.md` — mesmo resultado,
> num fluxo 100% Codex (os scripts rodam igual; o Codex constrói e se
> autoavalia contra o checklist do CLAUDE.md).

---

## 0. Pré-requisitos (uma vez por máquina)

```bash
pip install requests beautifulsoup4      # para os 2 scripts de scraping
# extrai-doc.py não precisa de nada (100% Python padrão)
```
- **Codex CLI** instalado e autenticado (o implementador delega a build a ele).
- **google-chrome** (opcional, recomendado): o revisor tira screenshots
  headless para conferir o visual. Sem ele, revisa só o código.

---

## 1. O que o analista te envia (vem no pedido)

1. **Link do template** — demo do Envato ou site-modelo escolhido.
2. **Link do site/e-commerce do cliente** (se existir).
3. **Doc (.docx)** — o que ele quer/não quer, com prints anotados.
4. **Assets** — pasta com imagens/banners.

> Os links vêm do pedido — os scripts não adivinham URLs, recebem por argumento.

---

## 2. Crie a pasta do cliente e extraia os insumos

Cada landing mora na SUA pasta (nome do cliente). A raiz guarda só o kit.

```bash
mkdir -p <cliente> && cd <cliente>

# coloque os assets e o .docx do analista aqui dentro:
#   <cliente>/assets-analista/...      <cliente>/doc-analista/briefing.docx

# 2.1 estrutura do template escolhido      -> template.json
python3 ../scripts/scrape-template.py "<url-do-template>"

# 2.2 identidade do cliente (cores/fontes/logo/fatos/legal) -> identidade.json
python3 ../scripts/scrape-cliente.py "<url-do-site-do-cliente>"

# 2.3 briefing do analista (texto na ordem + prints) -> doc-analista.json + prints
python3 ../scripts/extrai-doc.py "doc-analista/briefing.docx"

cd ..
```

Ao final você tem em `<cliente>/`: `template.json`, `identidade.json`,
`doc-analista/doc-analista.json` + os prints, e as pastas de assets.

---

## 3. Construir — chame o agente `implementador-codex`

No Claude Code, peça para rodar o agente **implementador-codex**. Cole este
prompt preenchendo o que está entre `< >`:

```
Use o agente implementador-codex para construir a landing page de <CLIENTE>.

Pasta do projeto: <cliente>/ (trabalhe sempre dentro dela).

Insumos já gerados (não regenere):
- <cliente>/doc-analista/doc-analista.json — briefing do analista, AUTORIDADE MÁXIMA.
- <cliente>/doc-analista/prints/ — prints anotados; cada print = uma seção.
  A QUANTIDADE e a ORDEM das seções vêm do doc do analista.
- <cliente>/template.json — estrutura/escala do template (inspiração, não cópia).
- <cliente>/identidade.json — cores, fontes, logo e fatos do cliente.
- <cliente>/assets-analista/ — imagens a usar na página.

Siga a skill .claude/skills/estrutura-landing/SKILL.md e as regras do CLAUDE.md.
Entregue <cliente>/index.html (único HTML autossuficiente) + <cliente>/enviar.php.
```

O implementador lê os prints, monta o prompt com a skill + os 3 JSONs, roda o
Codex e confere (arquivos criados, HTTP 200). Ele **não** conserta o resultado —
só reporta.

---

## 4. Revisar — chame o agente `revisor`

Depois que o implementador terminar, peça o agente **revisor**:

```
Use o agente revisor para revisar <cliente>/index.html contra a skill
estrutura-landing, o doc-analista.json e a identidade.json da pasta <cliente>/.
```

Ele avalia item por item com evidência (arquivo/linha), tira screenshot headless
e dá o veredito: **APROVADO** ou **CORREÇÕES NECESSÁRIAS: n itens**. Se houver
correções, mande de volta ao implementador/Codex e revise de novo.

---

## O que os agentes SEMPRE exigem (já embutido no kit)

- **Seções**: quantidade e ordem saem do doc do analista, não de número fixo.
- **Fidelidade visual**: h1 não passa da escala do template; parallax quando o
  template usa; cards flutuantes nunca cobrem o rosto em fotos;
  `img{max-width:100%;height:auto}` para não esticar imagem.
- **LGPD**: banner de cookies (Aceitar/Recusar reais, na identidade do cliente),
  link de política de privacidade (do site do cliente se houver, senão cria uma),
  e todo formulário com checkbox de consentimento + honeypot + `enviar.php`.
- **Assinatura da agência** no rodapé: "Feito e Gerenciado por Assessoria de
  Marketing 360 Grupo IX", link em "Grupo IX" → https://grupoix.com.br.
- **Autossuficiência**: um único HTML com CSS/JS embutidos, sem recursos externos.
- **Sem cópia**: copy própria; nunca reproduzir textos ou baixar imagens do
  template/site de origem.

---

## Sites institucionais longos (20+ seções)

Para site de marca (não landing de 1 produto), troque os agentes por
**implementador-site** / **revisor-site** e a skill por
`.claude/skills/estrutura-site/SKILL.md`. O resto do fluxo é igual.

---

## Referência rápida

| Passo | Comando / Agente | Saída |
|-------|------------------|-------|
| Template | `scrape-template.py <url>` | `template.json` |
| Cliente | `scrape-cliente.py <url>` | `identidade.json` |
| Doc | `extrai-doc.py <arquivo.docx>` | `doc-analista.json` + prints |
| Build | agente `implementador-codex` | `index.html` + `enviar.php` |
| Revisão | agente `revisor` | veredito com evidências |
