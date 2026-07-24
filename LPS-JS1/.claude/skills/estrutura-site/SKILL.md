---
name: estrutura-site
description: Estrutura obrigatória de um SITE institucional/de marca de página longa (one-page) com 20+ seções, regras de conversão, técnicas e o checklist de avaliação. Use ao construir ou revisar o site do projeto (diferente de estrutura-landing, que é para 1 produto).
---

# Estrutura de Site (one-page, 20+ seções)

Gabarito de um **site de marca/institucional** de página única e longa. Enquanto
`estrutura-landing` foca UM produto e UMA conversão, aqui o objetivo é apresentar
a marca inteira: quem é, o que faz, provas, portfólio e vários caminhos de contato.

## Regra de ouro
- **Mínimo de 20 seções** (`<section>`), cada uma com um `id` e um `<h2>` claro.
- Navegação fixa translúcida com âncoras para as seções principais e **rolagem
  suave** (`scroll-behavior:smooth` + `scroll-padding-top`).
- UMA ação primária de conversão repetida (ex.: "Fale conosco" / WhatsApp / agendar),
  com o MESMO texto/estilo, ao longo da página.
- Copy própria e honesta (sem inventar números, prêmios ou clientes). Se usar
  logos/depoimentos ilustrativos, deixe claro que são ilustrativos.

## As seções (ordem sugerida — adapte ao segmento, mantendo ≥20)
1. **Nav fixa translúcida** — logo + âncoras + CTA primário compacto.
2. **Herói** — headline de posicionamento (1 frase), subheadline, CTA primário
   acima da dobra, visual/mockup da marca.
3. **Prova social (faixa)** — logos de clientes/parceiros ou selos (ilustrativos ok).
4. **Proposta de valor** — o que a marca resolve, em 1 bloco forte.
5. **Serviços/Soluções** — grade de 3–6 cards (ícone + título + linha).
6. **Diferenciais** — por que escolher a marca (3–4 pontos).
7. **Como funciona / Processo** — passos numerados (3–5).
8. **Portfólio / Cases** — grade de trabalhos/projetos.
9. **Case em destaque** — 1 case aprofundado (desafio → solução → resultado).
10. **Números / Métricas** — contadores/estatísticas (plausíveis, honestos).
11. **Depoimentos** — 3+ citações (nome + contexto; ilustrativos se for o caso).
12. **Sobre / Quem somos** — história e propósito da marca.
13. **Time** — pessoas-chave (ou cultura/valores, se sem fotos).
14. **Tecnologias / Ferramentas** — stack, métodos ou parceiros técnicos.
15. **Planos / Pacotes** — ofertas ou modelos de trabalho (se aplicável).
16. **Integrações / Parcerias** — ecossistema, marcas parceiras.
17. **Conteúdo / Blog** — 3 posts/recursos recentes (ou newsletter).
18. **Perguntas frequentes (FAQ)** — 5–8 em `<details>/<summary>`.
19. **CTA final / Contato** — formulário simples OU WhatsApp/agenda, foco na ação.
20. **Rodapé completo** — navegação secundária, contato, redes sociais, aviso legal.

Passou de 20? Ótimo — pode desdobrar (ex.: "Depoimentos em vídeo", "Prêmios",
"Perguntas por segmento", "Mapa/onde estamos", "Vagas/carreira").

## Conversão / UX
- CTA primário claro no herói, no meio (após serviços/cases) e no CTA final.
- Botão flutuante de contato (WhatsApp/topo) sempre visível é recomendado.
- Reveal on scroll sutil (IntersectionObserver + CSS), respeitando
  `prefers-reduced-motion`. Nada de parallax pesado que trave o scroll.
- Hierarquia visual consistente: 1 `<h1>` (herói), `<h2>` por seção.

## Técnico / Acessibilidade / Performance
- HTML5 semântico (`header/nav/main/section/footer`, headings em ordem).
- Responsivo: 360px → 1 coluna, 1440px → multi-coluna; **sem rolagem horizontal**.
- Sem recursos de terceiros (a menos que a spec permita explicitamente): CSS/JS
  embutidos, imagens locais ou data URI, ícones em SVG inline.
- Acessível: contraste AA, foco visível, `alt` em imagens, `lang`, `<title>` e
  `<meta description>`, âncoras funcionais, skip-link.
- Performance: imagens dimensionadas (sem layout shift), nada de bibliotecas
  pesadas desnecessárias; a página deve carregar e rolar fluida.

## Checklist de qualidade (para o revisor)
- [ ] ≥ 20 `<section>`, cada uma com `id` e `<h2>`.
- [ ] Ordem coerente (herói no topo, rodapé no fim; provas antes do CTA final).
- [ ] Nav fixa translúcida com âncoras que levam às seções (rolagem suave).
- [ ] UM CTA primário repetido (mesmo texto/estilo) em ≥3 pontos.
- [ ] Botão flutuante de contato presente (ou justificativa).
- [ ] Prova social + portfólio/cases + depoimentos + FAQ presentes.
- [ ] 1 único `<h1>`; `<h2>` por seção; hierarquia correta.
- [ ] Responsivo (mobile 1 coluna, sem rolagem horizontal).
- [ ] Sem recursos de terceiros não autorizados; carrega HTTP 200 sem erros.
- [ ] Acessibilidade: alt, foco, contraste, lang, title/description, skip-link.
- [ ] Reveal on scroll com `prefers-reduced-motion` respeitado.
- [ ] Copy honesta (nada de dados/prêmios/clientes inventados; ilustrativos rotulados).
- [ ] Identidade visual do cliente aplicada (paleta e tom corretos).
