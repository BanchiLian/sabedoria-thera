#!/usr/bin/env python3
"""
scrape-cliente.py — Coletor de IDENTIDADE + FATOS do site/e-commerce do cliente.

Dado o site ou e-commerce EXISTENTE do cliente, extrai tudo que o implementador
precisa para manter a identidade da marca na nova landing:
  - IDENTIDADE VISUAL: paleta real (lida do CSS), fontes, logo, favicon
  - FATOS: nome do produto, preço, ficha técnica, avaliações (schema.org)
  - CONTATO: e-mails, telefones, WhatsApp, redes sociais
Gera identidade.json.

Princípio: colhe fatos e identidade, não conteúdo criativo. NÃO baixa imagens
nem copia textos de marketing verbatim — a landing gerada usa copy própria.

Uso:
  python3 scripts/scrape-cliente.py https://loja-do-cliente.com           # -> identidade.json
  python3 scripts/scrape-cliente.py https://loja-do-cliente.com saida.json

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

MAX_ITEM = 160          # corta itens de texto (evita copiar parágrafos longos)
MAX_LISTA = 25          # máximo de bullets coletados
MAX_IMGS = 30
MAX_CSS_BYTES = 600_000
UA = "Mozilla/5.0 (compatible; identidade-bot/1.0)"


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
    for st in soup.find_all("style"):
        if st.string:
            partes.append(st.string)
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


# ---- Paleta: cores mais usadas (separa cores de marca dos neutros) ----------
def extrai_paleta(*fontes):
    from collections import Counter
    texto = "\n".join(fontes)
    cores = Counter()
    for h in re.findall(r"#([0-9a-fA-F]{6})\b", texto):
        cores[("#" + h.lower())] += 1
    for h in re.findall(r"#([0-9a-fA-F]{3})\b", texto):
        cores["#" + "".join(c * 2 for c in h.lower())] += 1
    for m in re.findall(r"rgba?\(([^)]+)\)", texto):
        nums = re.findall(r"\d+", m)[:3]
        if len(nums) == 3:
            cores["#%02x%02x%02x" % tuple(int(n) for n in nums)] += 1

    def cinza_ou_extremo(hex6):
        r = int(hex6[1:3], 16); g = int(hex6[3:5], 16); b = int(hex6[5:7], 16)
        return max(r, g, b) - min(r, g, b) < 12   # cinza/branco/preto

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


# ---- Fatos de produto (schema.org) -------------------------------------------
def coleta_json_ld(soup):
    achados = []
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        blocos = data if isinstance(data, list) else data.get("@graph", [data])
        for b in blocos if isinstance(blocos, list) else [blocos]:
            if isinstance(b, dict):
                achados.append(b)
    return achados


def extrai_produto(blocos):
    for b in blocos:
        t = b.get("@type", "")
        t = " ".join(t) if isinstance(t, list) else str(t)
        if "Product" in t:
            oferta = b.get("offers", {})
            if isinstance(oferta, list):
                oferta = oferta[0] if oferta else {}
            aval = b.get("aggregateRating", {}) or {}
            return {
                "nome": limpa(str(b.get("name", ""))),
                "marca": limpa(str((b.get("brand") or {}).get("name", "")
                                   if isinstance(b.get("brand"), dict)
                                   else b.get("brand", ""))),
                "descricao": limpa(str(b.get("description", ""))),
                "preco": oferta.get("price", ""),
                "moeda": oferta.get("priceCurrency", ""),
                "disponibilidade": limpa(str(oferta.get("availability", ""))),
                "avaliacao": aval.get("ratingValue", ""),
                "qtd_avaliacoes": aval.get("reviewCount", "") or aval.get("ratingCount", ""),
            }
    return {}


REDES = {
    "instagram": r"instagram\.com",
    "facebook": r"facebook\.com|fb\.com|fb\.me",
    "youtube": r"youtube\.com|youtu\.be",
    "tiktok": r"tiktok\.com",
    "twitter": r"twitter\.com|x\.com",
    "linkedin": r"linkedin\.com",
    "pinterest": r"pinterest\.",
    "telegram": r"t\.me|telegram\.me",
    "whatsapp": r"wa\.me|api\.whatsapp\.com",
}
LIXO_SOCIAL = re.compile(
    r"/tr[/?]|/sharer|share\.php|/share[/?]|intent/|/plugins/|/dialog/"
    r"|noscript|pageview", re.I)


def coleta_redes(soup):
    achados = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href.startswith("http") or LIXO_SOCIAL.search(href):
            continue
        host = urllib.parse.urlparse(href).netloc.lower()
        for nome, padrao in REDES.items():
            if re.search(padrao, host) and nome not in achados:
                achados[nome] = href
    return achados


def coleta_legal(soup, base):
    """Links de política de privacidade / termos / cookies do site do cliente.
    Se existirem, a landing APONTA para eles; se não, cria-se uma política
    própria conforme a LGPD."""
    achados = {}
    PADROES = {
        "politica_privacidade": r"privacidade|privacy",
        "termos_de_uso": r"termos|terms",
        "politica_cookies": r"cookie",
    }
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        blob = (href + " " + a.get_text()).lower()
        for chave, pad in PADROES.items():
            if chave not in achados and re.search(pad, blob):
                achados[chave] = urllib.parse.urljoin(base, href)
    return achados


# atributos onde sites com lazy-load escondem a imagem real (o src costuma
# ser um placeholder base64 de 1px — Magento/Amasty, WordPress, etc.)
LAZY_ATTRS = ("data-amsrc", "data-src", "data-original", "data-lazy",
              "data-lazy-src", "data-echo", "src")


def _src_real(im):
    """Melhor URL de imagem de um <img>, pulando placeholders data:."""
    for attr in LAZY_ATTRS:
        v = (im.get(attr) or "").strip()
        if v and not v.startswith("data:"):
            return v
    # srcset: pega a primeira URL
    ss = im.get("data-srcset") or im.get("srcset") or ""
    if ss:
        primeira = ss.split(",")[0].strip().split(" ")[0]
        if primeira and not primeira.startswith("data:"):
            return primeira
    return ""


def coleta_logo(soup, base):
    candidatos = []
    for im in soup.find_all("img"):
        src = _src_real(im)
        if not src:
            continue
        blob = " ".join([src, im.get("alt", ""),
                         " ".join(im.get("class") or [])]).lower()
        # "logo" no src/alt/class OU caminho típico de logo (/media/logo/, /logo/)
        if "logo" in blob or re.search(r"/logo[/.]", src.lower()):
            candidatos.append(urllib.parse.urljoin(base, src))
    favicons = []
    for link in soup.find_all("link", rel=True):
        rel = " ".join(link.get("rel")).lower()
        if "icon" in rel and link.get("href"):
            favicons.append(urllib.parse.urljoin(base, link["href"]))
    return {
        "logo_candidatos": dedupe(candidatos)[:5],
        "og_imagem": meta(soup, "og:image"),
        "favicons": dedupe(favicons)[:3],
        "theme_color": meta(soup, "theme-color"),
    }


def baixa_identidade(candidatos, favicons, session, base, pasta="identidade-visual"):
    """Baixa o LOGO e o FAVICON do cliente (exceção à regra de não baixar
    imagens de origem: logo/favicon SÃO a identidade da marca, devem ser
    usados na landing, não recriados). Retorna os caminhos locais."""
    import os
    os.makedirs(pasta, exist_ok=True)
    out = {"logo_local": "", "favicon_local": ""}

    def baixa(url, nome_base):
        try:
            r = session.get(urllib.parse.urljoin(base, url), timeout=20)
            if not r.ok or not r.content:
                return ""
        except requests.RequestException:
            return ""
        ct = r.headers.get("content-type", "").lower()
        ext = (".svg" if "svg" in ct or url.lower().endswith(".svg")
               else ".png" if "png" in ct
               else ".jpg" if "jpeg" in ct or "jpg" in ct
               else ".webp" if "webp" in ct
               else ".ico" if "icon" in ct or url.lower().endswith(".ico")
               else os.path.splitext(urllib.parse.urlparse(url).path)[1] or ".png")
        caminho = os.path.join(pasta, nome_base + ext)
        with open(caminho, "wb") as f:
            f.write(r.content)
        return caminho

    if candidatos:
        out["logo_local"] = baixa(candidatos[0], "logo")
    if favicons:
        out["favicon_local"] = baixa(favicons[0], "favicon")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python3 scrape-cliente.py <url-do-cliente> [saida.json]")
    url = sys.argv[1]
    if not url.startswith("http"):
        url = "https://" + url
    saida = sys.argv[2] if len(sys.argv) > 2 else "identidade.json"

    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    css = coleta_css(soup, url, session)
    blocos_ld = coleta_json_ld(soup)

    # estrutura: hierarquia de títulos (os TÓPICOS da página)
    titulos = [{"nivel": h.name, "texto": limpa(h.get_text())}
               for h in soup.find_all(["h1", "h2", "h3"])
               if limpa(h.get_text())]

    # listas (frequentemente = ficha técnica / benefícios) — fatos curtos
    bullets = []
    for li in soup.find_all("li"):
        t = limpa(li.get_text())
        if 3 < len(t) <= MAX_ITEM and not li.find("a"):  # ignora menus
            bullets.append(t)
        if len(bullets) >= MAX_LISTA:
            break

    # preços visíveis (R$)
    precos = sorted(set(re.findall(r"R\$\s?\d[\d.,]*", resp.text)))[:10]

    # imagens: só metadados (src/alt/dimensão) — NÃO baixamos as de conteúdo
    imgs = []
    for im in soup.find_all("img"):
        src = _src_real(im)
        if src:
            imgs.append({
                "url": urllib.parse.urljoin(url, src),
                "alt": limpa(im.get("alt", "")),
                "w": im.get("width", ""), "h": im.get("height", ""),
            })
        if len(imgs) >= MAX_IMGS:
            break

    # LOGO e FAVICON: estes SIM baixamos — são a identidade da marca
    visual = coleta_logo(soup, url)
    arquivos = baixa_identidade(visual["logo_candidatos"], visual["favicons"],
                                session, url)

    texto = resp.text
    contato = {
        "emails": sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", texto)))[:5],
        "telefones": sorted(set(re.findall(r"\(?\d{2}\)?\s?9?\d{4}[-\s]?\d{4}", texto)))[:5],
        "whatsapp": sorted(set(re.findall(r"(?:wa\.me|api\.whatsapp\.com)[^\"'\s]+", texto)))[:3],
    }

    identidade = {
        "fonte": url,
        "aviso": "IDENTIDADE e FATOS do cliente para a nova landing. Cores, "
                 "fontes, LOGO e FAVICON daqui SÃO a identidade a usar — o logo "
                 "e o favicon foram BAIXADOS para identidade-visual/ e devem ser "
                 "usados na página (não recrie logo textual nem favicon genérico). "
                 "Os fatos INSPIRAM copy própria — nunca reproduza textos de "
                 "marketing verbatim nem baixe as imagens de CONTEÚDO do site.",
        "meta": {
            "title": limpa(soup.title.get_text() if soup.title else ""),
            "descricao": meta(soup, "og:description", "description"),
            "og_titulo": meta(soup, "og:title"),
            "og_imagem": meta(soup, "og:image"),
        },
        "identidade_visual": {
            **visual,
            **arquivos,
            "paleta": extrai_paleta(resp.text, css),
            "fontes": extrai_fontes(soup, css),
        },
        "produto": extrai_produto(blocos_ld),
        "precos_detectados": precos,
        "topicos_da_pagina": titulos,
        "possiveis_beneficios_ou_ficha": bullets,
        "imagens_referencia": imgs,
        "redes_sociais": coleta_redes(soup),
        "contato": contato,
        "legal": coleta_legal(soup, url),
    }

    with open(saida, "w", encoding="utf-8") as f:
        json.dump(identidade, f, ensure_ascii=False, indent=2)

    p = identidade["produto"]
    pal = identidade["identidade_visual"]["paleta"]
    fonts = identidade["identidade_visual"]["fontes"]["font_families"]
    print(f"✅ Identidade do cliente salva em {saida}")
    print(f"   Título:  {identidade['meta']['title'] or '—'}")
    print(f"   Paleta:  {', '.join(pal['cores_marca'][:6]) or '—'}")
    print(f"   Fontes:  {', '.join(fonts[:4]) or '—'}")
    iv = identidade["identidade_visual"]
    print(f"   Logo:    {iv.get('logo_local') or 'NÃO baixado — verifique manualmente'}")
    print(f"   Favicon: {iv.get('favicon_local') or 'NÃO baixado'}")
    print(f"   Produto: {p.get('nome') or '(sem schema.org Product)'}")
    print(f"   Preço:   {p.get('preco') or (precos[0] if precos else '—')} {p.get('moeda', '')}")
    redes = identidade["redes_sociais"]
    print(f"   Redes:   {', '.join(redes) if redes else '—'}")
    legal = identidade["legal"]
    print(f"   Legal:   {legal.get('politica_privacidade') or 'SEM política — criar conforme LGPD'}")


if __name__ == "__main__":
    main()
