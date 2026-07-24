codex exec --sandbox workspace-write --skip-git-repo-check "$(cat <<'EOF'
Construa uma landing page e depois se autoavalie. Trabalhe SÓ dentro de: viafibra/
site atual: https://viafibra.com.br/contrate/
Estrutura de referencia: https://viafibra.com.br/contrate/

LEIA nesta ordem, como fonte de verdade:
1. CLAUDE.md (raiz) — todas as regras: hierarquia, fidelidade visual, LGPD, logo/favicon, assinatura da agência e o "Checklist de aceite".
2. .claude/skills/estrutura-landing/SKILL.md — estrutura e qualidade.
3. viafibra/doc-analista/doc-analista.json — briefing do analista (AUTORIDADE MÁXIMA; a quantidade e a ordem das seções vêm DAQUI).
4. Os prints em viafibra/doc-analista/prints/ — abra e olhe cada um; cada print é uma seção. Respeite a posição de cards/badges (nunca sobre o rosto).
5. viafibra/template.json — escala/efeitos do template (h1/h2 não maiores que a escala dele; parallax onde ele usa).
6. viafibra/identidade.json — cores, fontes, fatos, links legais e logo_local/favicon_local.
7. viafibra/assets-analista/ e viafibra/identidade-visual/ — as imagens a usar.

CONSTRUA:
- viafibra/index.html: um único HTML autossuficiente (CSS/JS embutidos, sem recursos externos), copy PRÓPRIA, identidade do cliente.
- viafibra/enviar.php: disparo do form (honeypot + consentimento no servidor, sanitização, mail()).
- viafibra/politica-de-privacidade.html SÓ se identidade.json não tiver link de política; se tiver, aponte para o existente.

OBRIGATÓRIO (do CLAUDE.md): use o logo e o favicon reais de identidade-visual/ (nada de logo textual ou favicon genérico); img{max-width:100%;height:auto}; banner de cookies com Aceitar E Recusar reais + persistência; todo form com checkbox de consentimento + honeypot; um único CTA primário por seção; assinatura "Feito e Gerenciado por Assessoria de Marketing 360 Grupo IX" com link para https://grupoix.com.br no rodapé.

AUTORREVISÃO: percorra o "Checklist de aceite" do CLAUDE.md item a item (PASSOU/FALHOU com arquivo/linha). Sirva com python3 -m http.server e confirme HTTP 200; se houver google-chrome, tire um screenshot headless e confira proporção/sobreposição/logo. Corrija tudo que falhar e reavalie até passar. Ao final, imprima a tabela do checklist e o veredito.

Cliente: viafibra.
EOF
)"
