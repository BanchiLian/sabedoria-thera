---
name: estrutura-landing
description: Estrutura obrigatória de uma landing page de produto em 8 seções, com regras de conversão, técnicas e o checklist de avaliação. Use ao construir ou revisar a landing do projeto.
---

# Estrutura de landing page — 8 seções (fonte única de verdade)

Toda landing deste projeto segue esta ordem. Quem constrói obedece;
quem revisa cobra pelo checklist do fim.

## As 8 seções (ordem obrigatória)

1. **Herói (above the fold)**
   - Headline focada em UM benefício principal (o que o cliente ganha, não
     o que o produto é).
   - Subheadline de 1 linha esclarecendo/reforçando.
   - CTA primário (botão) visível sem rolar.
   - Um visual do produto (nesta fase: recriado em CSS/SVG ou placeholder
     elegante — sem imagens de URL externa).

2. **Prova social / confiança**
   - Faixa logo abaixo do herói: selos, números ("+10 mil clientes"),
     nota de avaliação, ou logos. Reduz desconfiança cedo.

3. **Problema / dor**
   - Nomeia a dor do público em 2–4 pontos. O cliente precisa pensar
     "é exatamente o meu caso".

4. **Solução / benefícios**
   - Como o produto resolve cada dor. Grade de 3–4 benefícios
     (ícone + título curto + 1 linha). Benefício, não característica técnica.

5. **Como funciona (passos)**
   - 3 a 4 passos numerados. Tira o medo do "como eu uso isso?".

6. **Depoimentos / provas**
   - Depoimentos de clientes (nesta fase, fictícios e claramente ilustrativos)
     ou antes/depois. Rosto/nome/contexto aumentam credibilidade.

7. **Oferta / preço**
   - A oferta clara: o que inclui, preço, garantia. CTA primário de novo.
     Se houver, elemento de urgência honesto (estoque/prazo real).

8. **FAQ + CTA final**
   - 4–6 perguntas que quebram as últimas objeções, e um CTA final
     fechando a página.

## Regras de conversão

- **UM CTA primário, repetido.** O mesmo texto e cor de ação nas seções
  1, 7 e 8. Não competir com vários botões primários diferentes.
- **Hierarquia de leitura:** headline > subheadline > corpo. Uma ideia
  por seção.
- **Texto de benefício:** fale do resultado para o cliente. Nada de
  "lorem ipsum" — escreva copy real e plausível.
- **Fricção mínima:** o CTA pede o próximo passo, não "tudo de uma vez".

## Regras técnicas

- Um único arquivo `index.html` autossuficiente (CSS e JS embutidos).
- **Nenhum recurso de terceiros** (sem CDN, Google Fonts, imagens de URL).
  Fontes: stack de sistema. Visuais: CSS/SVG/placeholder.
- **Responsivo:** funciona a 360px e a 1440px; grades viram 1 coluna no
  mobile; nada de rolagem horizontal.
- **Acessível:** HTML semântico (header/section/footer), contraste AA,
  `alt` em imagens, foco visível, botões são `<button>`/`<a>` reais.
- Paleta enxuta: 1 cor primária (a do CTA) + 1 de apoio + neutros.

## Honestidade (produto de saúde/fito — OBRIGATÓRIO)

Se o produto for suplemento/fitoterápico ou similar:
- **Não invente alegações médicas** ("cura", "trata doença X"). Use
  linguagem de bem-estar, não terapêutica.
- Depoimentos fictícios devem ser plausíveis, nunca atribuídos a médicos
  reais ou prometendo resultados garantidos de saúde.
- Incluir aviso do tipo "não substitui orientação profissional" quando
  fizer sentido. No Brasil, alegações de suplemento são reguladas (ANVISA)
  — a copy não deve prometer efeito de medicamento.

## Checklist de qualidade (para o revisor)

- [ ] As 8 seções existem, na ordem correta?
- [ ] Herói: headline de benefício + subheadline + CTA acima da dobra?
- [ ] Há faixa de prova social logo após o herói?
- [ ] Seção de dor com pontos concretos (2–4)?
- [ ] Benefícios em grade (3–4), focados em resultado, não característica?
- [ ] "Como funciona" com 3–4 passos numerados?
- [ ] Depoimentos presentes (fictícios, plausíveis)?
- [ ] Oferta com preço/garantia + CTA?
- [ ] FAQ (4–6) + CTA final?
- [ ] UM CTA primário repetido (mesmo texto/cor) nas seções 1, 7 e 8?
- [ ] Zero recursos externos? Responsivo (mobile 1 coluna)? Semântico?
- [ ] Nenhuma alegação médica indevida (se produto de saúde)?
