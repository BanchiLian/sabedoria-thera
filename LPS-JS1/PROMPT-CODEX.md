# Como usar o kit SÓ com o Codex (sem Claude)

Fluxo para quem tem apenas o **Codex CLI**. Os 3 scripts Python rodam igual
(não dependem de Claude); o próprio Codex **constrói E se autoavalia** contra o
checklist do `CLAUDE.md`, num único passo. Nada aqui precisa do Claude Code.

> Se você tem o Claude Code, use o `PROMPT.md` (fluxo com os agentes
> implementador-codex + revisor). Este arquivo é só para o modo Codex-only.

---

## 0. Pré-requisitos (uma vez por máquina)

```bash
pip install requests beautifulsoup4      # para os 2 scripts de scraping
# extrai-doc.py não precisa de nada (100% Python padrão)
codex --version                          # Codex CLI instalado e autenticado
# google-chrome (opcional): deixa o Codex conferir o visual por screenshot
```

---

## 1. Insumos (vêm no pedido do analista)

1. Link do **template** (Envato/modelo). 2. Link do **site do cliente**.
3. **Doc .docx** com prints. 4. Pasta de **assets**.

---

## 2. Crie a pasta do cliente e extraia os insumos

```bash
mkdir -p <cliente> && cd <cliente>

# coloque aqui dentro: <cliente>/assets-analista/  e  <cliente>/doc-analista/briefing.docx

python3 ../scripts/scrape-template.py "<url-do-template>"      # -> template.json
python3 ../scripts/scrape-cliente.py  "<url-do-site-cliente>"  # -> identidade.json
python3 ../scripts/extrai-doc.py "doc-analista/briefing.docx"  # -> doc-analista.json + prints

cd ..
```

---

## 3. Construir + autorrevisar com o Codex (um comando)

Rode a partir da RAIZ do kit. O Codex lê as regras, os insumos e os prints,
constrói e se autoavalia:

```bash
codex exec --sandbox workspace-write --skip-git-repo-check "$(cat <<'EOF'
Você vai construir uma landing page e depois se autoavaliar. Trabalhe apenas
dentro da pasta do cliente: <cliente>/

PASSO A — LEIA como fonte de verdade (na ordem):
1. CLAUDE.md (raiz) — todas as regras: hierarquia, fidelidade visual, LGPD,
   assinatura da agência e o "Checklist de aceite".
2. .claude/skills/estrutura-landing/SKILL.md — estrutura e qualidade.
3. <cliente>/doc-analista/doc-analista.json — briefing do analista (AUTORIDADE
   MÁXIMA). A quantidade e a ordem das seções vêm DAQUI.
4. Os prints em <cliente>/doc-analista/prints/ — abra e olhe cada um; cada
   print corresponde a uma seção. Respeite posição de cards/badges.
5. <cliente>/template.json — estrutura/escala/efeitos do template (inspiração).
6. <cliente>/identidade.json — cores, fontes, logo, fatos e links legais.
7. <cliente>/assets-analista/ — as imagens a usar.

PASSO B — CONSTRUA:
- <cliente>/index.html: um único HTML autossuficiente (CSS/JS embutidos, sem
  recursos externos), copy própria, identidade do cliente.
- <cliente>/enviar.php: disparo do formulário (honeypot + consentimento no
  servidor, sanitização, mail()).
- <cliente>/politica-de-privacidade.html SOMENTE se identidade.json não tiver
  link de política de privacidade; se tiver, aponte para o link existente.
Regras obrigatórias (do CLAUDE.md): seções pelo doc; h1/h2 não maiores que a
escala do template; parallax quando o template usa; img{max-width:100%;
height:auto}; cards nunca sobre o rosto; banner de cookies com Aceitar/Recusar
reais; form com consentimento + honeypot; assinatura "Feito e Gerenciado por
Assessoria de Marketing 360 Grupo IX" com link para https://grupoix.com.br.

PASSO C — AUTORREVISÃO:
Percorra o "Checklist de aceite" do CLAUDE.md item a item, marcando
PASSOU/FALHOU com evidência (arquivo/linha). Sirva a página
(python3 -m http.server) e confirme HTTP 200; se houver google-chrome, tire um
screenshot headless e confira proporção/sobreposição/alinhamento. CORRIJA tudo
que falhar e reavalie até todos os itens passarem. No final, imprima a tabela
do checklist e o veredito.

Cliente: <CLIENTE>.
EOF
)"
```

Substitua `<cliente>` (pasta) e `<CLIENTE>` (nome) antes de rodar.

Se preferir interativo, abra `codex` na raiz e cole o mesmo texto do PASSO A ao
PASSO C.

> ⏱️ **Dê tempo ao Codex.** Ler as regras + skill + doc + prints, construir a
> página inteira e ainda se autoavaliar leva vários minutos (pode passar de
> 15–20 min). Não interrompa cedo. Se usar `timeout`, deixe folgado; no modo
> interativo, só aguarde. Se ficar longo demais, rode em duas etapas: peça
> primeiro a construção (PASSOS A+B) e, num segundo comando, a autorrevisão
> (PASSO C) — o Codex relê os arquivos já gravados.

---

## 4. Confira a entrega

```bash
cd <cliente> && python3 -m http.server 8000    # abra http://localhost:8000
```

Entregáveis em `<cliente>/`: `index.html`, `enviar.php` e, quando criada,
`politica-de-privacidade.html`. Ajuste o e-mail de destino no topo do
`enviar.php` antes de subir para o servidor.

---

## Diferença para o modo Claude

| | Claude+Codex (`PROMPT.md`) | Codex-only (este arquivo) |
|---|---|---|
| Scripts (insumos) | igual | igual |
| Constrói | agente implementador-codex → Codex | Codex direto |
| Revisa | agente revisor (Claude), independente | Codex se autoavalia pelo checklist |
| Fonte das regras | CLAUDE.md + skill + agentes | CLAUDE.md + skill (Codex lê) |

O autorreview do Codex é do mesmo construtor — menos independente que o revisor
Claude. Recomendação: rode o comando, e se puder, passe o olho na página final.
