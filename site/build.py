"""Gera o site estático em _site/ a partir de content/posts/*.md.

Uso: python3 site/build.py
"""
import csv
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

RAIZ = Path(__file__).resolve().parent.parent
POSTS = RAIZ / "content" / "posts"
SAIDA = RAIZ / "_site"
TOKEN_PRODUTO = re.compile(r"\{\{\s*produto:([\w\-]+)\s*\}\}")


# ---------------- leitura ----------------
def config():
    return yaml.safe_load((RAIZ / "config.yaml").read_text(encoding="utf-8"))


def produtos():
    """Produtos ativos e com link de afiliado de verdade, por id."""
    itens = {}
    with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as f:
        for p in csv.DictReader(f):
            link = (p.get("link_afiliado") or "").strip()
            ativo = (p.get("ativo") or "").strip().lower() in ("sim", "s", "1", "true")
            if ativo and link.startswith("https://") and ("meli.la/" in link or "mercadolivre.com" in link):
                p["destaques"] = [d.strip() for d in (p.get("destaques") or "").split(";") if d.strip()]
                itens[p["id"].strip()] = p
    return itens


def ler_post(caminho: Path):
    texto = caminho.read_text(encoding="utf-8")
    partes = texto.split("---", 2)
    if len(partes) < 3 or partes[0].strip():
        raise ValueError("frontmatter ausente (o arquivo deve começar com ---)")
    meta = yaml.safe_load(partes[1]) or {}
    for k in ("publicado", "atualizado"):
        if isinstance(meta.get(k), (dt.date, dt.datetime)):
            meta[k] = meta[k].isoformat()[:10]
    return meta, partes[2].strip()


def posts():
    itens = []
    for c in sorted(POSTS.glob("*.md")):
        meta, corpo = ler_post(c)
        itens.append({**meta, "corpo": corpo, "arquivo": c})
    itens.sort(key=lambda p: str(p.get("publicado", "")), reverse=True)
    return itens


# ---------------- renderização ----------------
def preco_br(valor):
    try:
        v = float(str(valor).replace(",", "."))
    except ValueError:
        return ""
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def card_produto(p):
    destaques = "".join(f"<li>{html.escape(d)}</li>" for d in p["destaques"][:4])
    nota = ""
    if p.get("nota"):
        aval = f" · {int(float(p['avaliacoes'])):,} avaliações".replace(",", ".") if p.get("avaliacoes") else ""
        nota = f'<p class="nota">★ {html.escape(str(p["nota"]))}{aval}</p>'
    img = ""
    if (p.get("imagem_url") or "").startswith("http"):
        img = f'<img src="{html.escape(p["imagem_url"])}" alt="{html.escape(p["nome"])}" loading="lazy">'
    preco = preco_br(p.get("preco", ""))
    preco_html = f'<p class="preco">a partir de ~{preco} <small>(preço de referência, confira o atual)</small></p>' if preco else ""
    return f"""
<div class="produto">
  {img}
  <div class="produto-info">
    <p class="produto-nome">{html.escape(p['nome'])}</p>
    <p class="marca">{html.escape(p.get('marca', ''))}</p>
    {nota}
    <ul>{destaques}</ul>
    {preco_html}
    <a class="botao" href="{html.escape(p['link_afiliado'])}" target="_blank" rel="sponsored nofollow noopener">Ver preço no Mercado Livre</a>
  </div>
</div>"""


def corpo_html(corpo, catalogo):
    def troca(m):
        p = catalogo.get(m.group(1))
        return card_produto(p) if p else ""  # produto inativo some do post

    corpo = TOKEN_PRODUTO.sub(lambda m: "\n\n" + troca(m) + "\n\n", corpo)
    return markdown.markdown(corpo, extensions=["tables", "toc", "sane_lists", "attr_list"])


def json_ld(post, cfg, url):
    dados = [{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["titulo"],
        "description": post.get("descricao", ""),
        "datePublished": post.get("publicado"),
        "dateModified": post.get("atualizado") or post.get("publicado"),
        "author": {"@type": "Organization", "name": cfg["site"]["autor"]},
        "mainEntityOfPage": url,
    }]
    if post.get("faq"):
        dados.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": f["pergunta"],
                 "acceptedAnswer": {"@type": "Answer", "text": f["resposta"]}}
                for f in post["faq"]
            ],
        })
    return json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")


def build():
    cfg = config()
    base = cfg["site"]["url_base"].rstrip("/")
    caminho_base = "/" + base.split("://", 1)[-1].split("/", 1)[1] if base.count("/") > 2 else ""
    catalogo = produtos()
    lista = posts()
    subnichos = {s["slug"]: s["nome"] for s in cfg["subnichos"]}

    env = Environment(loader=FileSystemLoader(RAIZ / "site" / "templates"), autoescape=True)
    glob = dict(site=cfg["site"], subnichos=subnichos, b=caminho_base,
                ano=dt.date.today().year)

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    (SAIDA / "posts").mkdir(parents=True)
    shutil.copytree(RAIZ / "site" / "static", SAIDA / "static")

    urls = [base + "/"]
    for p in lista:
        url = f"{base}/posts/{p['slug']}/"
        relacionados = [q for q in lista if q["subnicho"] == p.get("subnicho") and q["slug"] != p["slug"]][:3]
        pagina = env.get_template("post.html").render(
            **glob, post=p, conteudo=corpo_html(p["corpo"], catalogo), url=url,
            json_ld=json_ld(p, cfg, url), relacionados=relacionados,
            tem_produto=bool(TOKEN_PRODUTO.search(p["corpo"])),
        )
        destino = SAIDA / "posts" / p["slug"]
        destino.mkdir(parents=True)
        (destino / "index.html").write_text(pagina, encoding="utf-8")
        urls.append(url)

    (SAIDA / "index.html").write_text(
        env.get_template("lista.html").render(**glob, titulo_pagina=None, posts=lista, url=base + "/"),
        encoding="utf-8")

    for slug, nome in subnichos.items():
        dest = SAIDA / "categoria" / slug
        dest.mkdir(parents=True)
        url = f"{base}/categoria/{slug}/"
        (dest / "index.html").write_text(
            env.get_template("lista.html").render(
                **glob, titulo_pagina=nome, posts=[p for p in lista if p.get("subnicho") == slug], url=url),
            encoding="utf-8")
        urls.append(url)

    for nome in ("sobre", "privacidade"):
        dest = SAIDA / nome
        dest.mkdir()
        url = f"{base}/{nome}/"
        (dest / "index.html").write_text(env.get_template(f"{nome}.html").render(**glob, url=url), encoding="utf-8")
        urls.append(url)

    # escritório em pixel art (fora do sitemap, noindex)
    escritorio = json.loads((RAIZ / "data" / "escritorio.json").read_text(encoding="utf-8")) \
        if (RAIZ / "data" / "escritorio.json").exists() else {}
    pautas = json.loads((RAIZ / "data" / "pautas.json").read_text(encoding="utf-8")) \
        if (RAIZ / "data" / "pautas.json").exists() else []
    semana = (dt.date.today() - dt.timedelta(days=7)).isoformat()
    escritorio["metricas"] = {
        "posts": len(lista),
        "posts_7d": sum(1 for p in lista if str(p.get("publicado", "")) >= semana),
        "fila": sum(1 for p in pautas if p.get("status") == "pendente"),
        "produtos": len(catalogo),
        "meta_dia": cfg["rotina"]["posts_novos_por_dia"],
    }
    dest = SAIDA / "escritorio"
    dest.mkdir()
    (dest / "index.html").write_text(
        env.get_template("escritorio.html").render(
            **glob, dados_json=json.dumps(escritorio, ensure_ascii=False).replace("</", "<\\/")),
        encoding="utf-8")

    # sitemap e robots
    datas = {f"{base}/posts/{p['slug']}/": p.get("atualizado") or p.get("publicado") for p in lista}
    linhas = "".join(
        f"<url><loc>{u}</loc>" + (f"<lastmod>{datas[u]}</lastmod>" if datas.get(u) else "") + "</url>"
        for u in urls)
    (SAIDA / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{linhas}</urlset>',
        encoding="utf-8")
    (SAIDA / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
    (SAIDA / ".nojekyll").write_text("")
    print(f"Site gerado em _site/ com {len(lista)} posts e {len(catalogo)} produtos ativos.")


if __name__ == "__main__":
    build()
