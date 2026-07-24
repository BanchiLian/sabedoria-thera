#!/usr/bin/env python3
"""
extrai-doc.py — Leitor do DOC do analista (briefing da tarefa).

O analista envia um .docx com o que ele quer ou não na landing: textos,
instruções e prints mostrando o que vai ser cada coisa. Este script lê o
.docx e gera:
  - doc-analista.json  → conteúdo na ORDEM do documento (parágrafos, títulos,
                         tabelas e marcadores de onde cada print aparece)
  - doc-analista-imgs/ → todos os prints/imagens embutidos no doc, numerados
                         na ordem em que aparecem no texto

Assim o implementador lê o JSON e abre cada print no ponto exato em que o
analista o colocou.

100% biblioteca padrão do Python — funciona em qualquer máquina, sem pip.

Uso:
  python3 scripts/extrai-doc.py "caminho/do/briefing.docx"
  python3 scripts/extrai-doc.py "briefing.docx" saida.json pasta-imgs/
"""
import json
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
    "v": "urn:schemas-microsoft-com:vml",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}


def q(prefix, tag):
    return f"{{{NS[prefix]}}}{tag}"


def carrega_rels(z):
    """Mapa rId -> alvo (word/media/imageN.png) das relações do documento."""
    rels = {}
    try:
        root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    except KeyError:
        return rels
    for r in root.findall(q("rel", "Relationship")):
        alvo = r.get("Target", "")
        if alvo.startswith("media/") or "/media/" in alvo:
            rels[r.get("Id")] = "word/" + alvo.lstrip("/") if not alvo.startswith("word/") else alvo
    return rels


def texto_do_paragrafo(p):
    """Concatena os <w:t> do parágrafo, respeitando quebras de linha."""
    partes = []
    for el in p.iter():
        if el.tag == q("w", "t"):
            partes.append(el.text or "")
        elif el.tag in (q("w", "br"), q("w", "cr")):
            partes.append("\n")
        elif el.tag == q("w", "tab"):
            partes.append("\t")
    return "".join(partes).strip()


def estilo_do_paragrafo(p):
    """Nome do estilo (Heading1, Title, ...) se houver."""
    ppr = p.find(q("w", "pPr"))
    if ppr is not None:
        st = ppr.find(q("w", "pStyle"))
        if st is not None:
            return st.get(q("w", "val"), "")
    return ""


def imagens_do_elemento(el):
    """rIds de imagens dentro do elemento (drawing moderno + VML antigo)."""
    rids = []
    for blip in el.iter(q("a", "blip")):
        rid = blip.get(q("r", "embed")) or blip.get(q("r", "link"))
        if rid:
            rids.append(rid)
    for imagedata in el.iter(q("v", "imagedata")):
        rid = imagedata.get(q("r", "id"))
        if rid:
            rids.append(rid)
    return rids


def hyperlinks_do_paragrafo(p, rels_all):
    urls = []
    for h in p.iter(q("w", "hyperlink")):
        rid = h.get(q("r", "id"))
        if rid and rid in rels_all:
            urls.append(rels_all[rid])
    return urls


def carrega_rels_completo(z):
    """Todas as relações (inclui hyperlinks externos)."""
    rels = {}
    try:
        root = ET.fromstring(z.read("word/_rels/document.xml.rels"))
    except KeyError:
        return rels
    for r in root.findall(q("rel", "Relationship")):
        rels[r.get("Id")] = r.get("Target", "")
    return rels


def extrai_tabela(tbl):
    linhas = []
    for tr in tbl.findall(q("w", "tr")):
        celulas = []
        for tc in tr.findall(q("w", "tc")):
            txt = " ".join(filter(None, (texto_do_paragrafo(p)
                                         for p in tc.iter(q("w", "p")))))
            celulas.append(txt)
        if any(celulas):
            linhas.append(celulas)
    return linhas


def main():
    if len(sys.argv) < 2:
        sys.exit('Uso: python3 extrai-doc.py "briefing.docx" [saida.json] [pasta-imgs/]')
    caminho = sys.argv[1]
    if not os.path.isfile(caminho):
        sys.exit(f"Arquivo não encontrado: {caminho}")
    saida = sys.argv[2] if len(sys.argv) > 2 else "doc-analista.json"
    pasta_imgs = sys.argv[3] if len(sys.argv) > 3 else "doc-analista-imgs"

    z = zipfile.ZipFile(caminho)
    rels_media = carrega_rels(z)
    rels_all = carrega_rels_completo(z)
    root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(q("w", "body"))
    if body is None:
        sys.exit("Documento sem corpo — .docx inválido?")

    os.makedirs(pasta_imgs, exist_ok=True)

    conteudo = []          # blocos na ordem do documento
    img_seq = 0
    rid_para_arquivo = {}  # rId já extraído -> nome do arquivo salvo

    def salva_imagem(rid):
        nonlocal img_seq
        if rid in rid_para_arquivo:
            return rid_para_arquivo[rid]
        alvo = rels_media.get(rid)
        if not alvo:
            return None
        try:
            dados = z.read(alvo)
        except KeyError:
            return None
        img_seq += 1
        ext = os.path.splitext(alvo)[1] or ".png"
        nome = f"print-{img_seq:02d}{ext}"
        with open(os.path.join(pasta_imgs, nome), "wb") as f:
            f.write(dados)
        rid_para_arquivo[rid] = nome
        return nome

    for el in body:
        if el.tag == q("w", "p"):
            texto = texto_do_paragrafo(el)
            estilo = estilo_do_paragrafo(el)
            links = hyperlinks_do_paragrafo(el, rels_all)
            rids = imagens_do_elemento(el)

            if texto:
                bloco = {"tipo": "texto", "texto": texto}
                if re.match(r"(?i)heading|t[ií]tulo|title", estilo):
                    nivel = re.sub(r"\D", "", estilo) or "1"
                    bloco = {"tipo": "titulo", "nivel": int(nivel), "texto": texto}
                if links:
                    bloco["links"] = links
                conteudo.append(bloco)
            elif links:
                conteudo.append({"tipo": "texto", "texto": "", "links": links})

            for rid in rids:
                nome = salva_imagem(rid)
                if nome:
                    conteudo.append({"tipo": "print",
                                     "arquivo": f"{pasta_imgs}/{nome}"})
        elif el.tag == q("w", "tbl"):
            linhas = extrai_tabela(el)
            if linhas:
                conteudo.append({"tipo": "tabela", "linhas": linhas})
            for rid in imagens_do_elemento(el):
                nome = salva_imagem(rid)
                if nome:
                    conteudo.append({"tipo": "print",
                                     "arquivo": f"{pasta_imgs}/{nome}"})

    # imagens no zip que nenhum rId referenciou (raro, mas não perdemos nada)
    referenciadas = set(rels_media.get(r) for r in rid_para_arquivo)
    for info in z.namelist():
        if info.startswith("word/media/") and info not in referenciadas:
            dados = z.read(info)
            img_seq += 1
            ext = os.path.splitext(info)[1] or ".png"
            nome = f"print-{img_seq:02d}-extra{ext}"
            with open(os.path.join(pasta_imgs, nome), "wb") as f:
                f.write(dados)
            conteudo.append({"tipo": "print", "arquivo": f"{pasta_imgs}/{nome}",
                             "obs": "imagem no doc sem posição detectada"})

    doc = {
        "fonte": os.path.basename(caminho),
        "aviso": "Briefing do ANALISTA na ordem original do documento. Os "
                 "blocos 'print' apontam para as imagens extraídas — abra "
                 "cada uma para entender o que o analista quer naquele ponto.",
        "resumo": {
            "blocos_texto": sum(1 for b in conteudo if b["tipo"] == "texto"),
            "titulos": sum(1 for b in conteudo if b["tipo"] == "titulo"),
            "tabelas": sum(1 for b in conteudo if b["tipo"] == "tabela"),
            "prints": sum(1 for b in conteudo if b["tipo"] == "print"),
        },
        "conteudo": conteudo,
    }

    with open(saida, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    r = doc["resumo"]
    print(f"✅ Doc do analista extraído para {saida}")
    print(f"   Textos:  {r['blocos_texto']} · Títulos: {r['titulos']} · "
          f"Tabelas: {r['tabelas']}")
    print(f"   Prints:  {r['prints']} salvos em {pasta_imgs}/")


if __name__ == "__main__":
    main()
