#!/usr/bin/env python3
"""
scrape-template.py — Coletor da ESTRUTURA do template/modelo escolhido.

O analista envia o link do template (demo do Envato, ThemeForest ou qualquer
site-modelo). Este script extrai a ESTRUTURA da landing escolhida para o
cliente: número/ordem de seções, hierarquia de títulos, navegação, CTAs,
paleta e fontes do template. Gera template.json.

Princípio: colhe PADRÕES de design e estrutura, NÃO conteúdo. Não baixa
imagens nem copia textos verbatim — a landing gerada usa copy e visuais
próprios (identidade do CLIENTE, ver scrape-cliente.py), apenas se inspira
na organização e no "clima" do template.

Uso:
  python3 scripts/scrape-template.py https://demo-do-template.com          # -> template.json
  python3 scripts/scrape-template.py https://demo-do-template.com saida.json

Requer: requests + beautifulsoup4
  pip install requests beautifulsoup4
"""
import json
import re
import sys
import urllib.parse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Faltam dependências. Rode: pip install requests beautifulsoup4")

MAX_ITEM = 160
MAX_LISTA = 40
MAX_IMGS = 40
MAX_CSS_BYTES = 600_000   # teto de CSS baixado (soma dos stylesheets)
UA = "Mozilla/5.0 (compatible; referencia-bot/1.0)"


def limpa(txt):
    return re.sub(r"\s+", " ", (txt or "").strip())[:MAX_ITEM]


def dedupe(seq):
    vistos, out = set(), []
    for x in seq:
        if x and x not in vistos:
            vistos.add(x)
            out.append(x)
    return out


def meta(soup, *nomes):
    for n in nomes:
        tag = (soup.find("meta", property=n) or
               soup.find("meta", attrs={"name": n}))
        if tag and tag.get("content"):
            return limpa(tag["content"])
    return ""


# ---- CSS: baixa os stylesheets ligados + junta o <style> inline -------------
def coleta_css(soup, base, session):
    partes = []
    # <style> inline
    for st in soup.find_all("style"):
        if st.string:
            partes.append(st.string)
    # <link rel=stylesheet>
    total = 0
    for link in soup.find_all("link", rel=True):
        rel = " ".join(link.get("rel")).lower()
        href = link.get("href")
        if "stylesheet" not in rel or not href:
            continue
        url = urllib.parse.urljoin(base, href)
        try:
            r = session.get(url, timeout=20)
            if r.ok and "css" in r.headers.get("content-type", "css"):
                partes.append(r.text)
                total += len(r.text)
        except requests.RequestException:
            continue
        if total >= MAX_CSS_BYTES:
            break
    return "\n".join(partes)


# ---- Paleta: cores mais usadas (ignora branco/preto/cinza puro comuns) ------
def extrai_paleta(*fontes):
    from collections import Counter
    texto = "\n".join(fontes)
    cores = Counter()
    # hex de 6 dígitos
    for h in re.findall(r"#([0-9a-fA-F]{6})\b", texto):
        cores[("#" + h.lower())] += 1
    # hex de 3 dígitos -> normaliza p/ 6
    for h in re.findall(r"#([0-9a-fA-F]{3})\b", texto):
        cores["#" + "".join(c * 2 for c in h.lower())] += 1
    # rgb/rgba
    for m in re.findall(r"rgba?\(([^)]+)\)", texto):
        nums = re.findall(r"\d+", m)[:3]
        if len(nums) == 3:
            cores["#%02x%02x%02x" % tuple(int(n) for n in nums)] += 1

    def cinza_ou_extremo(hex6):
        r = int(hex6[1:3], 16); g = int(hex6[3:5], 16); b = int(hex6[5:7], 16)
        if max(r, g, b) - min(r, g, b) < 12:      # cinza/branco/preto
            return True
        return False

    coloridas = [(c, n) for c, n in cores.most_common(60) if not cinza_ou_extremo(c)]
    neutras = [(c, n) for c, n in cores.most_common(60) if cinza_ou_extremo(c)]
    return {
        "cores_marca": [c for c, _ in coloridas[:10]],
        "neutros": [c for c, _ in neutras[:6]],
    }


# ---- Fontes: font-family do CSS + Google Fonts ------------------------------
def extrai_fontes(soup, css):
    familias = []
    for fam in re.findall(r"font-family\s*:\s*([^;{}]+)", css):
        primeira = fam.split(",")[0].strip().strip("'\"")
        if primeira and not primeira.lower().startswith(("var(", "inherit")):
            familias.append(primeira)
    google = []
    for link in soup.find_all("link", href=True):
        if "fonts.googleapis.com" in link["href"] or "fonts.gstatic" in link["href"]:
            google.append(link["href"])
    return {"font_families": dedupe(familias)[:8], "google_fonts": dedupe(google)[:4]}


# ---- Design tokens: escala tipográfica, efeitos, raios ----------------------
def extrai_design_tokens(css):
    """Detalhes visuais que o implementador precisa replicar: tamanho de
    títulos, parallax (background-attachment: fixed), raios de borda."""
    def font_sizes_de(seletor):
        tamanhos = []
        # regra cujo bloco de seletores contém o alvo (h1, h2, body...)
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            sel, corpo = m.group(1), m.group(2)
            if not re.search(rf"(^|[,\s]){seletor}(\s*[,{{.:\[]|$)", sel.strip()):
                continue
            for fs in re.findall(r"font-size\s*:\s*([^;}]+)", corpo):
                tamanhos.append(fs.strip())
        return dedupe(tamanhos)[:4]

    parallax = len(re.findall(r"background-attachment\s*:\s*fixed", css))
    raios = [r.strip() for r in re.findall(r"border-radius\s*:\s*([^;}]+)", css)]
    from collections import Counter
    raios_comuns = [r for r, _ in Counter(raios).most_common(5)]
    return {
        "font_size_h1": font_sizes_de("h1"),
        "font_size_h2": font_sizes_de("h2"),
        "font_size_body": font_sizes_de("body"),
        "parallax_background_fixed": parallax > 0,
        "ocorrencias_background_fixed": parallax,
        "border_radius_comuns": raios_comuns,
        "obs": "Replique a ESCALA dos títulos e os efeitos (ex.: parallax) do "
               "template. Se parallax_background_fixed=true, alguma seção usa "
               "background-attachment: fixed — normalmente faixas de CTA.",
    }


# ---- Estrutura: seções, headings, nav, CTAs ---------------------------------
def estrutura(soup):
    secoes = soup.find_all("section")
    # blocos de layout comuns além de <section>
    blocos = soup.find_all(["section", "header", "footer", "main", "article"])
    topicos = [{"nivel": h.name, "texto": limpa(h.get_text())}
               for h in soup.find_all(["h1", "h2", "h3"]) if limpa(h.get_text())]
    # navegação: links do primeiro <nav>
    nav_itens = []
    nav = soup.find("nav")
    if nav:
        nav_itens = dedupe([limpa(a.get_text()) for a in nav.find_all("a")
                            if limpa(a.get_text())])[:15]
    # CTAs: textos de <a>/<button> curtos e "acionáveis"
    ctas = []
    for el in soup.find_all(["a", "button"]):
        t = limpa(el.get_text())
        if 2 <= len(t) <= 40 and re.search(
                r"comec|começ|assin|compr|test|grát|gratis|free|demo|fal|"
                r"contat|saiba|agend|cadastr|inscre|quero|pedir|orça|sign|"
                r"get|start|buy|try", t, re.I):
            ctas.append(t)
    return {
        "n_secoes_tag": len(secoes),
        "n_blocos_layout": len(blocos),
        "topicos_da_pagina": topicos[:MAX_LISTA],
        "navegacao": nav_itens,
        "ctas_detectados": dedupe(ctas)[:15],
    }


def coleta_redes(soup):
    REDES = {
        "instagram": r"instagram\.com", "facebook": r"facebook\.com|fb\.com",
        "youtube": r"youtube\.com|youtu\.be", "tiktok": r"tiktok\.com",
        "twitter": r"twitter\.com|x\.com", "linkedin": r"linkedin\.com",
        "pinterest": r"pinterest\.", "telegram": r"t\.me",
        "whatsapp": r"wa\.me|api\.whatsapp\.com",
    }
    lixo = re.compile(r"/tr[/?]|/sharer|share\.php|intent/|/plugins/|/dialog/", re.I)
    out = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href.startswith("http") or lixo.search(href):
            continue
        host = urllib.parse.urlparse(href).netloc.lower()
        for nome, pad in REDES.items():
            if re.search(pad, host) and nome not in out:
                out[nome] = href
    return out


def coleta_logo(soup, base):
    cand = []
    for im in soup.find_all("img"):
        src = im.get("src") or im.get("data-src") or ""
        if not src or src.startswith("data:"):
            continue
        blob = " ".join([src, im.get("alt", ""), " ".join(im.get("class") or [])]).lower()
        if "logo" in blob:
            cand.append(urllib.parse.urljoin(base, src))
    fav = []
    for link in soup.find_all("link", rel=True):
        if "icon" in " ".join(link.get("rel")).lower() and link.get("href"):
            fav.append(urllib.parse.urljoin(base, link["href"]))
    return {"logo_candidatos": dedupe(cand)[:5], "favicons": dedupe(fav)[:3],
            "theme_color": meta(soup, "theme-color")}


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 scrape-template.py <url-do-template> [saida.json]")
    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url
    saida = sys.argv[2] if len(sys.argv) > 2 else "template.json"

    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    css = coleta_css(soup, url, session)

    imgs = []
    for im in soup.find_all("img"):
        src = im.get("src") or im.get("data-src") or ""
        if src and not src.startswith("data:"):
            imgs.append({"url": urllib.parse.urljoin(url, src),
                         "alt": limpa(im.get("alt", "")),
                         "w": im.get("width", ""), "h": im.get("height", "")})
        if len(imgs) >= MAX_IMGS:
            break

    est = estrutura(soup)
    referencia = {
        "fonte": url,
        "aviso": "ESTRUTURA do template escolhido, para INSPIRAR uma landing "
                 "ORIGINAL. Não copie textos nem baixe as imagens do template; "
                 "recrie com a identidade do CLIENTE (identidade.json). Aqui "
                 "saem só padrões (ordem de seções, nav, CTAs, paleta, fontes).",
        "meta": {
            "title": limpa(soup.title.get_text() if soup.title else ""),
            "descricao": meta(soup, "og:description", "description"),
            "og_titulo": meta(soup, "og:title"),
            "og_imagem": meta(soup, "og:image"),
        },
        "identidade_visual": {
            **coleta_logo(soup, url),
            "paleta": extrai_paleta(resp.text, css),
            "fontes": extrai_fontes(soup, css),
        },
        "design_tokens": extrai_design_tokens(css),
        "estrutura": est,
        "redes_sociais": coleta_redes(soup),
        "imagens_referencia": imgs,
    }

    with open(saida, "w", encoding="utf-8") as f:
        json.dump(referencia, f, ensure_ascii=False, indent=2)

    print(f"✅ Estrutura do template salva em {saida}")
    print(f"   Título:  {referencia['meta']['title'] or '—'}")
    print(f"   Seções:  {est['n_secoes_tag']} <section> · {est['n_blocos_layout']} blocos · "
          f"{len(est['topicos_da_pagina'])} títulos")
    pal = referencia['identidade_visual']['paleta']
    print(f"   Paleta:  {', '.join(pal['cores_marca'][:6]) or '—'}")
    fonts = referencia['identidade_visual']['fontes']['font_families']
    print(f"   Fontes:  {', '.join(fonts[:4]) or '—'}")
    print(f"   Nav:     {', '.join(est['navegacao'][:8]) or '—'}")
    dt = referencia['design_tokens']
    print(f"   H1:      {', '.join(dt['font_size_h1']) or '—'} · "
          f"Parallax: {'SIM' if dt['parallax_background_fixed'] else 'não'}")


if __name__ == "__main__":
    main()
