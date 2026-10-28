"""Gera o site estático em _site/ a partir de content/posts/*.md.

Uso: python3 site/build.py
"""
import base64
import csv
import datetime as dt
import os
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
# Tokens de venda (agente Vendas): link no meio do texto e botão pequeno (cabe em tabela)
TOKEN_LINK = re.compile(r"\{\{\s*link:([\w\-]+)(?:\|([^}]+))?\s*\}\}")
TOKEN_BOTAO = re.compile(r"\{\{\s*botao:([\w\-]+)(?:\|([^}]+))?\s*\}\}")
TOKENS_VENDA = (TOKEN_PRODUTO, TOKEN_LINK, TOKEN_BOTAO)


# ---------------- leitura ----------------
def config():
    return yaml.safe_load((RAIZ / "config.yaml").read_text(encoding="utf-8"))


def marca():
    """Identidade visual mantida pelo agente Designer (design/marca.yaml)."""
    arq = RAIZ / "design" / "marca.yaml"
    return yaml.safe_load(arq.read_text(encoding="utf-8")) if arq.exists() else {}


def css_marca(m):
    """Variáveis CSS a partir do marca.yaml (sobrescrevem o style.css)."""
    linhas = [f"--{k.replace('_', '-')}: {v['hex']};" for k, v in (m.get("cores") or {}).items()]
    f = m.get("fontes") or {}
    if f.get("titulo"):
        linhas.append(f'--titulo: "{f["titulo"]["nome"]}", "Segoe UI", system-ui, sans-serif;')
    if f.get("texto"):
        linhas.append(f'--texto: "{f["texto"]["nome"]}", "Segoe UI", system-ui, sans-serif;')
    return ":root{" + "".join(linhas) + "}"


def fontes_url(m):
    f = m.get("fontes") or {}
    fams = [f[k]["google"] for k in ("titulo", "texto") if f.get(k, {}).get("google")]
    if not fams:
        return ""
    return "https://fonts.googleapis.com/css2?" + "&".join("family=" + x for x in fams) + "&display=swap"


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
CURTO = {
    "fones-caixas-bluetooth": "Fones e caixas",
    "power-banks-carregadores": "Power banks",
    "smartwatches-smartbands": "Smartwatches",
    "acessorios-gamer": "Gamer",
    "casa-inteligente": "Casa inteligente",
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


BLOCO = re.compile(r"^:::\s*(pros|contras|veredito|dica|atencao)\b[ \t]*(.*?)\n(.*?)^:::[ \t]*$", re.M | re.S)
TITULOS_BLOCO = {"pros": "Prós", "contras": "Contras", "veredito": "Veredito", "dica": "Dica", "atencao": "Atenção"}


def blocos(texto):
    """Componentes do Designer: :::pros, :::contras, :::veredito, :::dica, :::atencao."""
    def troca(m):
        tipo, titulo, miolo = m.group(1), m.group(2).strip() or TITULOS_BLOCO[m.group(1)], m.group(3)
        return (f'<div class="bloco bloco-{tipo}" markdown="1">\n<p class="bloco-titulo">{html.escape(titulo)}</p>\n\n'
                f'{miolo.strip()}\n\n</div>')
    return BLOCO.sub(troca, texto)


def pontuacao(p):
    """Ordem das vitrines: nota alta com muitas avaliações primeiro."""
    import math
    try:
        return float(p.get("nota") or 0) * math.log10(float(p.get("avaliacoes") or 0) + 10)
    except ValueError:
        return 0


def link_venda(p, texto=None, classe="link-oferta"):
    rotulo = html.escape(texto.strip() if texto else p["nome"])
    return (f'<a class="{classe}" href="{html.escape(p["link_afiliado"])}" target="_blank" '
            f'rel="sponsored nofollow noopener" data-produto="{html.escape(p["id"])}">{rotulo}</a>')


def renderizar(corpo, catalogo):
    """Devolve (html, sumario, ids de produtos usados)."""
    usados = [m.group(1) for t in TOKENS_VENDA for m in t.finditer(corpo) if m.group(1) in catalogo]
    usados = [m.group(1) for m in TOKEN_PRODUTO.finditer(corpo) if m.group(1) in catalogo] + usados
    corpo = TOKEN_LINK.sub(lambda m: link_venda(catalogo[m.group(1)], m.group(2)) if m.group(1) in catalogo
                           else (m.group(2) or ""), corpo)
    corpo = TOKEN_BOTAO.sub(lambda m: link_venda(catalogo[m.group(1)], m.group(2) or "Ver oferta", "btn-comprar btn-pequeno")
                            if m.group(1) in catalogo else "", corpo)

    def troca(m):
        p = catalogo.get(m.group(1))
        return card_produto(p) if p else ""  # produto inativo some do post

    texto = TOKEN_PRODUTO.sub(lambda m: "\n\n" + troca(m) + "\n\n", corpo)
    texto = blocos(texto)
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists", "attr_list", "md_in_html"],
                           extension_configs={"toc": {"toc_depth": "2"}})
    conteudo = md.convert(texto)
    conteudo = conteudo.replace("<table>", '<div class="tabela"><table>').replace("</table>", "</table></div>")
    conteudo = re.sub(r'(<div class="bloco bloco-pros">.*?</div>)\s*(<div class="bloco bloco-contras">.*?</div>)',
                      r'<div class="pros-contras">\1\2</div>', conteudo, flags=re.S)
    sumario = [{"id": t["id"], "nome": t["name"]} for t in md.toc_tokens]
    return conteudo, sumario, list(dict.fromkeys(usados))


def minutos_leitura(corpo):
    for t in TOKENS_VENDA:
        corpo = t.sub("", corpo)
    return max(1, round(len(re.findall(r"\w+", corpo)) / 200))


def cifrar(texto, senha, iteracoes=250_000):
    """AES-256-GCM com chave derivada da senha (PBKDF2-SHA256). Aberto no navegador via WebCrypto."""
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    sal, iv = os.urandom(16), os.urandom(12)
    chave = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sal, iterations=iteracoes).derive(senha.encode())
    dados = AESGCM(chave).encrypt(iv, texto.encode("utf-8"), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"sal": b(sal), "iv": b(iv), "iter": iteracoes, "dados": b(dados)}


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
        **({"image": post["capa"]} if post.get("capa") else {}),
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


def capa_png(post, cat, cfg, destino):
    """Capa 1200x630 para WhatsApp, redes e Google (og:image). Opcional: precisa do Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return False
    fontes = RAIZ / "site" / "fontes"
    try:
        def fonte(arq, tam, peso):
            f = ImageFont.truetype(str(fontes / arq), tam)
            try:
                eixos = {a["name"].decode() if isinstance(a["name"], bytes) else a["name"]: a for a in f.get_variation_axes()}
                f.set_variation_by_axes([peso if "eight" in n else (48 if "ptical" in n or "opsz" in n.lower() else 100)
                                         for n in eixos])
            except Exception:
                pass
            return f
        cor = cat.get("cor", "#2950FF")
        W, H = 1200, 630
        img = Image.new("RGB", (W, H), "#050507")
        d = ImageDraw.Draw(img)
        for r, a in ((520, 18), (380, 34), (240, 60)):  # halo da categoria
            halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(halo).ellipse((W - 260 - r, 120 - r, W - 260 + r, 120 + r), fill=cor + f"{a:02x}")
            img.paste(halo, (0, 0), halo)
        d.rectangle((0, H - 10, W, H), fill="#7C5CFF")
        # símbolo da marca (etiqueta + raio)
        x0, y0, k = 72, 64, 1.1
        P = lambda pts: [(x0 + a * k, y0 + b * k) for a, b in pts]
        d.polygon(P([(20, 6), (58, 6), (60, 10), (60, 54), (58, 58), (20, 58), (4, 32)]), fill="#7C5CFF")
        d.ellipse((x0 + 13 * k, y0 + 28 * k, x0 + 21 * k, y0 + 36 * k), fill="#050507")
        d.polygon(P([(44, 12), (29, 35), (38.5, 35), (34.5, 52), (50, 28.5), (40.2, 28.5)]), fill="#FFFFFF")
        d.text((x0 + 84, y0 + 12), cfg["site"]["nome"], font=fonte("InterTight.ttf", 38, 700), fill="#FFFFFF")
        f_cat = fonte("InterTight.ttf", 26, 500)
        larg = d.textlength(cat.get("nome", ""), font=f_cat)
        d.rounded_rectangle((72, 196, 72 + 52 + larg + 22, 244), radius=24, fill="#101015", outline="#25252F", width=2)
        d.ellipse((94, 214, 106, 226), fill=cor)
        d.text((120, 204), cat.get("nome", ""), font=f_cat, fill="#F4F4F6")
        frase = str(post.get("capa_frase") or post["titulo"])
        tam = 76 if len(frase) < 48 else 62
        f_tit = fonte("InterTight.ttf", tam, 700)
        linhas, atual = [], ""
        for palavra in frase.split():
            teste = (atual + " " + palavra).strip()
            if d.textlength(teste, font=f_tit) > W - 200 and atual:
                linhas.append(atual); atual = palavra
            else:
                atual = teste
        linhas.append(atual)
        y = 290
        for ln in linhas[:3]:
            d.text((72, y), ln, font=f_tit, fill="#FFFFFF")
            y += int(tam * 1.12)
        destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(destino, optimize=True)
        return True
    except Exception as e:  # capa nunca derruba a publicação
        print(f"capa não gerada para {post.get('slug')}: {e}")
        return False


def build():
    cfg = config()
    m = marca()
    VISUAL.update({k: (v["hex"], v.get("icone", VISUAL.get(k, ("", "estrela"))[1]))
                   for k, v in (m.get("categorias") or {}).items()})
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
            "curto": s.get("curto") or CURTO.get(s["slug"], s["nome"]),
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
                ano=dt.date.today().year, css_marca=css_marca(m), fontes_url=fontes_url(m), base=base,
                link_venda=link_venda)

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    (SAIDA / "posts").mkdir(parents=True)
    shutil.copytree(RAIZ / "site" / "static", SAIDA / "static")

    urls = [base + "/"]
    for p in lista:
        url = f"{base}/posts/{p['slug']}/"
        conteudo, sumario, usados = renderizar(p["corpo"], catalogo)
        rapida = [catalogo[i] for i in usados] if p.get("tipo") in ("lista", "comparativo") else []
        da_cat = sorted([x for x in catalogo.values() if x.get("subnicho") == p.get("subnicho")], key=pontuacao, reverse=True)
        recomendados = [x for x in da_cat if x["id"] not in usados][:3]
        principal = catalogo[usados[0]] if usados else (da_cat[0] if da_cat else None)
        relacionados = [q for q in lista if q.get("subnicho") == p.get("subnicho") and q["slug"] != p["slug"]][:3]
        if len(relacionados) < 3:
            relacionados += [q for q in lista if q["slug"] != p["slug"] and q not in relacionados][:3 - len(relacionados)]
        tem_capa = capa_png(p, p["cat"], cfg, SAIDA / "capas" / f"{p['slug']}.png")
        p["capa"] = f"{base}/capas/{p['slug']}.png" if tem_capa else ""
        pagina = env.get_template("post.html").render(
            **glob, post=p, conteudo=conteudo, sumario=sumario, rapida=rapida, url=url,
            json_ld=json_ld(p, cfg, url), relacionados=relacionados,
            tem_produto=bool(usados or recomendados), recomendados=recomendados, principal=principal,
            preco_br=preco_br, milhar=milhar, estrelas=estrelas,
        )
        destino = SAIDA / "posts" / p["slug"]
        destino.mkdir(parents=True)
        (destino / "index.html").write_text(pagina, encoding="utf-8")
        urls.append(url)

    capa_png({"titulo": "Eletrônico bom, sem pagar a mais.", "slug": "inicio"},
             {"nome": "Guias de compra", "cor": "#7C5CFF"}, cfg, SAIDA / "capas" / "inicio.png")
    (SAIDA / "index.html").write_text(
        env.get_template("inicio.html").render(
            **glob, posts=lista, url=base + "/", produto=next(iter(sorted(catalogo.values(), key=pontuacao, reverse=True)), None),
            achados=sorted(catalogo.values(), key=pontuacao, reverse=True)[:6],
            total_produtos=len(catalogo), preco_br=preco_br, milhar=milhar, estrelas=estrelas),
        encoding="utf-8")

    for slug, cat in cats.items():
        dest = SAIDA / "categoria" / slug
        dest.mkdir(parents=True)
        url = f"{base}/categoria/{slug}/"
        (dest / "index.html").write_text(
            env.get_template("categoria.html").render(
                **glob, cat=cat, posts=[p for p in lista if p.get("subnicho") == slug], url=url,
                achados=sorted([x for x in catalogo.values() if x.get("subnicho") == slug], key=pontuacao, reverse=True)[:6],
                preco_br=preco_br, milhar=milhar, estrelas=estrelas),
            encoding="utf-8")
        urls.append(url)

    dest = SAIDA / "marca"
    dest.mkdir()
    (dest / "index.html").write_text(
        env.get_template("marca.html").render(**glob, marca=m, url=f"{base}/marca/",
                                              exemplo=next(iter(cats.values()))),
        encoding="utf-8")

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
    est = RAIZ / "data" / "estrategia.md"
    if est.exists():
        escritorio["estrategia_html"] = markdown.markdown(est.read_text(encoding="utf-8"), extensions=["tables"])
    mur = RAIZ / "data" / "mural.json"
    if mur.exists():
        msgs = json.loads(mur.read_text(encoding="utf-8")).get("mensagens", [])
        escritorio["mural"] = [m for m in msgs if m.get("status") == "aberta"] + \
            [m for m in msgs if m.get("status") != "aberta"][-12:][::-1]
    met = RAIZ / "data" / "metricas.json"
    if met.exists():
        hist = json.loads(met.read_text(encoding="utf-8")).get("semanas", [])
        if hist:
            escritorio["metricas"]["semana"] = hist[-1]
    # O escritório é privado: só é publicado criptografado com a senha do dono
    # (secret ESCRITORIO_SENHA no GitHub). Sem senha configurada, não é publicado.
    senha = os.environ.get("ESCRITORIO_SENHA", "").strip()
    if senha:
        html_claro = env.get_template("escritorio.html").render(
            **glob, dados_json=json.dumps(escritorio, ensure_ascii=False).replace("</", "<\\/"))
        dest = SAIDA / "escritorio"
        dest.mkdir()
        (dest / "index.html").write_text(
            env.get_template("cadeado.html").render(cofre=json.dumps(cifrar(html_claro, senha))), encoding="utf-8")
    else:
        print("Escritório não publicado: defina o secret ESCRITORIO_SENHA para publicá-lo com senha.")

    # sitemap e robots
    datas = {f"{base}/posts/{p['slug']}/": p.get("atualizado") or p.get("publicado") for p in lista}
    linhas = "".join(
        f"<url><loc>{u}</loc>" + (f"<lastmod>{datas[u]}</lastmod>" if datas.get(u) else "") + "</url>"
        for u in urls)
    (SAIDA / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{linhas}</urlset>',
        encoding="utf-8")
    (SAIDA / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nDisallow: {caminho_base}/escritorio/\nDisallow: {caminho_base}/marca/\nSitemap: {base}/sitemap.xml\n",
        encoding="utf-8")
    (SAIDA / ".nojekyll").write_text("")
    print(f"Site gerado em _site/ com {len(lista)} posts e {len(catalogo)} produtos ativos.")


if __name__ == "__main__":
    build()
