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
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

# Cor e ícone de cada categoria (pode sobrescrever a cor no config.yaml com `cor:`)
VISUAL = {
    "fones-caixas-bluetooth": ("#6D4AFF", "fone"),
    "power-banks-carregadores": ("#F07800", "bateria"),
    "smartwatches-smartbands": ("#00927F", "relogio"),
    "acessorios-gamer": ("#D6336C", "controle"),
    "casa-inteligente": ("#2563EB", "casa"),
}
ICONES = {
    "fone": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="5" height="7" rx="2"/><rect x="16" y="14" width="5" height="7" rx="2"/>',
    "bateria": '<rect x="2" y="7" width="17" height="10" rx="2"/><path d="M22 11v2"/><path d="M11 9l-2 3h4l-2 3"/>',
    "relogio": '<rect x="6" y="6" width="12" height="12" rx="3"/><path d="M9 6l1-4h4l1 4M9 18l1 4h4l1-4"/><path d="M12 9.5V12l1.5 1.5"/>',
    "controle": '<path d="M7 8h10a5 5 0 0 1 4.9 6l-.6 3a2.5 2.5 0 0 1-4.3 1.2L15 16H9l-2 2.2A2.5 2.5 0 0 1 2.7 17l-.6-3A5 5 0 0 1 7 8z"/><path d="M8 11v3M6.5 12.5h3"/><circle cx="16" cy="12" r=".6"/><circle cx="17.5" cy="13.5" r=".6"/>',
    "casa": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M12 13a2.5 2.5 0 0 0-1.5 4.5V19h3v-1.5A2.5 2.5 0 0 0 12 13z"/>',
    "estrela": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
}


def icone(nome, classe="ico"):
    return (f'<svg class="{classe}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONES.get(nome, "")}</svg>')


def data_br(iso):
    try:
        d = dt.date.fromisoformat(str(iso)[:10])
    except ValueError:
        return str(iso)
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def preco_br(valor):
    try:
        v = float(str(valor).replace(",", "."))
    except ValueError:
        return ""
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def milhar(n):
    try:
        return f"{int(float(n)):,}".replace(",", ".")
    except ValueError:
        return ""


def estrelas(nota):
    try:
        n = float(nota)
    except (TypeError, ValueError):
        return ""
    pct = max(0, min(100, n / 5 * 100))
    return (f'<span class="estrelas" role="img" aria-label="Nota {str(n).replace(".", ",")} de 5">'
            f'<span class="estrelas-cheias" style="width:{pct:.0f}%"></span></span>')


def card_produto(p, ordem=None):
    destaques = "".join(f"<li>{html.escape(d)}</li>" for d in p["destaques"][:4])
    nota = ""
    if p.get("nota"):
        nota = (f'<p class="ficha-nota">{estrelas(p["nota"])} <strong>{html.escape(str(p["nota"]).replace(".", ","))}</strong>'
                f'{" · " + milhar(p["avaliacoes"]) + " avaliações" if p.get("avaliacoes") else ""}</p>')
    img = ""
    if (p.get("imagem_url") or "").startswith("http"):
        img = f'<div class="ficha-foto"><img src="{html.escape(p["imagem_url"])}" alt="{html.escape(p["nome"])}" loading="lazy" width="200" height="200"></div>'
    preco = preco_br(p.get("preco", ""))
    preco_html = (f'<p class="ficha-preco"><span>Referência</span> {preco}</p>'
                  f'<p class="ficha-obs">O preço muda com frequência. Confira o valor atual no anúncio.</p>') if preco else ""
    return f"""
<aside class="ficha" aria-label="{html.escape(p['nome'])}">
  {img}
  <div class="ficha-corpo">
    <p class="ficha-marca">{html.escape(p.get('marca', ''))}</p>
    <p class="ficha-nome">{html.escape(p['nome'])}</p>
    {nota}
    <ul class="ficha-destaques">{destaques}</ul>
    <div class="ficha-compra">
      {preco_html}
      <a class="btn-comprar" href="{html.escape(p['link_afiliado'])}" target="_blank" rel="sponsored nofollow noopener">Ver oferta no Mercado Livre</a>
    </div>
  </div>
</aside>"""


def renderizar(corpo, catalogo):
    """Devolve (html, sumario, ids de produtos usados)."""
    usados = [pid for pid in TOKEN_PRODUTO.findall(corpo) if pid in catalogo]

    def troca(m):
        p = catalogo.get(m.group(1))
        return card_produto(p) if p else ""  # produto inativo some do post

    texto = TOKEN_PRODUTO.sub(lambda m: "\n\n" + troca(m) + "\n\n", corpo)
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list"],
                           extension_configs={"toc": {"toc_depth": "2"}})
    conteudo = md.convert(texto)
    conteudo = conteudo.replace("<table>", '<div class="tabela"><table>').replace("</table>", "</table></div>")
    sumario = [{"id": t["id"], "nome": t["name"]} for t in md.toc_tokens]
    return conteudo, sumario, list(dict.fromkeys(usados))


def minutos_leitura(corpo):
    return max(1, round(len(re.findall(r"\w+", TOKEN_PRODUTO.sub("", corpo))) / 200))


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

    cats = {}
    for s in cfg["subnichos"]:
        cor, ico = VISUAL.get(s["slug"], ("#2950FF", "estrela"))
        cats[s["slug"]] = {
            "slug": s["slug"], "nome": s["nome"], "cor": s.get("cor", cor),
            "icone": icone(ico), "descricao": s.get("descricao", ""),
            "total": sum(1 for p in lista if p.get("subnicho") == s["slug"]),
        }
    subnichos = {k: v["nome"] for k, v in cats.items()}
    for p in lista:
        p["cat"] = cats.get(p.get("subnicho"), {"nome": "", "cor": "#2950FF", "slug": "", "icone": ""})
        p["data_txt"] = data_br(p.get("atualizado") or p.get("publicado"))
        p["minutos"] = minutos_leitura(p["corpo"])

    env = Environment(loader=FileSystemLoader(RAIZ / "site" / "templates"), autoescape=True)
    env.filters["data_br"] = data_br
    glob = dict(site=cfg["site"], subnichos=subnichos, cats=cats, b=caminho_base,
                ano=dt.date.today().year)

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    (SAIDA / "posts").mkdir(parents=True)
    shutil.copytree(RAIZ / "site" / "static", SAIDA / "static")

    urls = [base + "/"]
    for p in lista:
        url = f"{base}/posts/{p['slug']}/"
        conteudo, sumario, usados = renderizar(p["corpo"], catalogo)
        rapida = [catalogo[i] for i in usados] if p.get("tipo") in ("lista", "comparativo") else []
        relacionados = [q for q in lista if q.get("subnicho") == p.get("subnicho") and q["slug"] != p["slug"]][:3]
        if len(relacionados) < 3:
            relacionados += [q for q in lista if q["slug"] != p["slug"] and q not in relacionados][:3 - len(relacionados)]
        pagina = env.get_template("post.html").render(
            **glob, post=p, conteudo=conteudo, sumario=sumario, rapida=rapida, url=url,
            json_ld=json_ld(p, cfg, url), relacionados=relacionados, tem_produto=bool(usados),
            preco_br=preco_br,
        )
        destino = SAIDA / "posts" / p["slug"]
        destino.mkdir(parents=True)
        (destino / "index.html").write_text(pagina, encoding="utf-8")
        urls.append(url)

    (SAIDA / "index.html").write_text(
        env.get_template("inicio.html").render(**glob, posts=lista, url=base + "/"), encoding="utf-8")

    for slug, cat in cats.items():
        dest = SAIDA / "categoria" / slug
        dest.mkdir(parents=True)
        url = f"{base}/categoria/{slug}/"
        (dest / "index.html").write_text(
            env.get_template("categoria.html").render(
                **glob, cat=cat, posts=[p for p in lista if p.get("subnicho") == slug], url=url),
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
