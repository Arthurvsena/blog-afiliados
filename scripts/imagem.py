"""Imagens reais para os posts (sem imagem gerada por IA).

Fontes permitidas (editorial/manual.md, seção Imagens):
  1. Foto do produto do catálogo (guia de compras)             -> comando "produto"
  2. Foto com licença livre do Wikimedia Commons / Openverse    -> comandos "buscar" e "baixar"
     (CC0, domínio público, CC BY ou CC BY-SA; nunca NC ou ND), sempre com crédito.
  3. Imagem de divulgação oficial (newsroom/press kit da empresa) -> comando "baixar"
     com --credito "Divulgação/Empresa".

Uso:
  python3 scripts/imagem.py buscar "galaxy smartphone" [--n 8]
  python3 scripts/imagem.py baixar URL --slug SLUG --credito "Autor/Wikimedia Commons" \
          --licenca "CC BY-SA 4.0" --fonte URL_DA_PAGINA [--posicao centro|topo|base]
  python3 scripts/imagem.py produto SLUG [--id ID_DO_PRODUTO]
  python3 scripts/imagem.py faltando        # lista posts sem imagem

O arquivo vai para content/imagens/SLUG.jpg (1600x840) e o bloco `imagem:` é
gravado no frontmatter do post.
"""
import argparse
import csv
import io
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
POSTS = RAIZ / "content" / "posts"
PASTA = RAIZ / "content" / "imagens"
UA = "TechBaratoBR/1.0 (https://github.com/Arthurvsena/blog-afiliados; portal de tecnologia)"
W, H = 1600, 840
LIVRES = re.compile(r"^(cc0|cc[- ]?by(?:[- ]sa)?(?:[- ][\d.]+)?|public domain|pd|domínio público)", re.I)
PROIBIDAS = re.compile(r"\b(nc|nd|non[- ]?commercial|no[- ]?deriv|fair use)\b", re.I)


def pegar(url, tipo="bin"):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        dados = r.read()
    return json.loads(dados) if tipo == "json" else dados


def limpar(html_txt):
    return re.sub(r"<[^>]+>", "", str(html_txt or "")).strip()


# ---------------- busca ----------------
def buscar_commons(q, n):
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search"
           f"&gsrsearch={urllib.parse.quote(q + ' filetype:bitmap')}&gsrnamespace=6&gsrlimit={n * 3}"
           "&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=1600")
    res = []
    for pg in (pegar(url, "json").get("query", {}).get("pages", {}) or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = limpar(meta.get("LicenseShortName", {}).get("value"))
        if not LIVRES.search(lic) or PROIBIDAS.search(lic) or ii.get("width", 0) < 1000:
            continue
        res.append({"fonte": "wikimedia", "titulo": pg.get("title", "").replace("File:", ""),
                    "licenca": lic, "autor": limpar(meta.get("Artist", {}).get("value"))[:80] or "Wikimedia Commons",
                    "url": "https://commons.wikimedia.org/wiki/Special:FilePath/"
                           + urllib.parse.quote(pg.get("title", "").replace("File:", "").replace(" ", "_")) + "?width=1920",
                    "pagina": ii.get("descriptionurl"),
                    "tamanho": f"{ii.get('width')}x{ii.get('height')}",
                    "descricao": limpar(meta.get("ImageDescription", {}).get("value"))[:160]})
    return res[:n]


def buscar_openverse(q, n):
    url = ("https://api.openverse.org/v1/images/?license_type=commercial,modification&mature=false"
           f"&page_size={n}&q={urllib.parse.quote(q)}")
    res = []
    for r in pegar(url, "json").get("results", []):
        lic = f"CC {r.get('license', '').upper()} {r.get('license_version', '')}".replace("CC CC0", "CC0").strip()
        if PROIBIDAS.search(lic) or (r.get("width") or 0) < 1000:
            continue
        res.append({"fonte": r.get("source", "openverse"), "titulo": r.get("title", ""), "licenca": lic,
                    "autor": r.get("creator") or r.get("source"), "url": r.get("url"),
                    "pagina": r.get("foreign_landing_url"), "tamanho": f"{r.get('width')}x{r.get('height')}",
                    "descricao": (r.get("title") or "")[:160]})
    return res


# ---------------- tratamento ----------------
def recortar(img, posicao="centro"):
    img = ImageOps.exif_transpose(img).convert("RGB")
    centro = {"centro": (0.5, 0.5), "topo": (0.5, 0.25), "base": (0.5, 0.75)}.get(posicao, (0.5, 0.5))
    return ImageOps.fit(img, (W, H), Image.LANCZOS, centering=centro)


def salvar(img, slug):
    PASTA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / f"{slug}.jpg"
    img.save(destino, "JPEG", quality=84, optimize=True, progressive=True)
    return destino


def gravar_frontmatter(slug, bloco):
    """Acrescenta (ou troca) só o bloco `imagem:` do frontmatter, sem reformatar o resto."""
    caminho = POSTS / f"{slug}.md"
    if not caminho.exists():
        sys.exit(f"Post {caminho} não existe.")
    texto = caminho.read_text(encoding="utf-8")
    _, fm, corpo = texto.split("---", 2)
    fm = re.sub(r"^imagem:\n(?:[ \t]+.*\n?)*", "", fm, flags=re.M).rstrip("\n") + "\n"
    fm += yaml.safe_dump({"imagem": bloco}, allow_unicode=True, sort_keys=False, width=1000)
    caminho.write_text(f"---{fm}---{corpo}", encoding="utf-8")


def foto_produto(url):
    """Foto do produto em estúdio: fundo claro com luz suave e sombra, sem montagem artificial."""
    for troca in (lambda u: re.sub(r"-[A-Z]\.(webp|jpg)$", r"-F.\1", u), lambda u: u):
        try:
            prod = Image.open(io.BytesIO(pegar(troca(url)))).convert("RGBA")
            break
        except Exception:
            prod = None
    if prod is None:
        sys.exit("Não consegui baixar a foto do produto.")
    # recorta o fundo branco do anúncio
    cinza = ImageOps.invert(prod.convert("L"))
    caixa = cinza.point(lambda v: 255 if v > 12 else 0).getbbox() or (0, 0, *prod.size)
    prod = prod.crop(caixa)
    alpha = ImageOps.invert(prod.convert("L")).point(lambda v: 255 if v > 10 else int(v * 25))
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))
    prod.putalpha(alpha)
    escala = min((H * 0.78) / prod.height, (W * 0.5) / prod.width)
    prod = prod.resize((max(1, int(prod.width * escala)), max(1, int(prod.height * escala))), Image.LANCZOS)
    fundo = Image.new("RGB", (W, H), "#e9ebef")
    luz = Image.new("L", (W, H), 0)
    ImageDraw.Draw(luz).ellipse((W * 0.18, -H * 0.4, W * 0.82, H * 1.0), fill=255)
    fundo = Image.composite(Image.new("RGB", (W, H), "#f7f8fa"), fundo, luz.filter(ImageFilter.GaussianBlur(160)))
    x, y = (W - prod.width) // 2, int(H * 0.5 - prod.height / 2)
    sombra = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sombra).ellipse((x + prod.width * 0.08, y + prod.height - 14, x + prod.width * 0.92, y + prod.height + 26), fill=120)
    fundo = Image.composite(Image.new("RGB", (W, H), "#b9bec8"), fundo, sombra.filter(ImageFilter.GaussianBlur(18)))
    fundo.paste(prod, (x, y), prod)
    return fundo


# ---------------- comandos ----------------
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar"); b.add_argument("termos"); b.add_argument("--n", type=int, default=8)
    d = sub.add_parser("baixar"); d.add_argument("url"); d.add_argument("--slug", required=True)
    d.add_argument("--credito", required=True); d.add_argument("--licenca", default="Divulgação")
    d.add_argument("--fonte", required=True); d.add_argument("--posicao", default="centro")
    pr = sub.add_parser("produto"); pr.add_argument("slug"); pr.add_argument("--id")
    sub.add_parser("faltando")
    a = ap.parse_args()

    if a.cmd == "buscar":
        achados = []
        for f in (buscar_commons, buscar_openverse):
            try:
                achados += f(a.termos, a.n)
            except Exception as e:
                print(f"(fonte indisponível: {f.__name__}: {e})", file=sys.stderr)
        if not achados:
            print("Nenhuma imagem livre encontrada. Tente termos em inglês e mais genéricos.")
        for i, r in enumerate(achados, 1):
            print(f"{i}. [{r['licenca']}] {r['titulo']} ({r['tamanho']}) por {r['autor']}\n   {r['descricao']}\n   url: {r['url']}\n   pagina: {r['pagina']}")
        return

    if a.cmd == "baixar":
        if PROIBIDAS.search(a.licenca):
            sys.exit("Licença não permitida (NC/ND). Escolha outra imagem.")
        img = recortar(Image.open(io.BytesIO(pegar(a.url))), a.posicao)
        salvar(img, a.slug)
        gravar_frontmatter(a.slug, {"arquivo": f"{a.slug}.jpg", "credito": a.credito,
                                     "licenca": a.licenca, "fonte": a.fonte})
        print(f"Imagem salva em content/imagens/{a.slug}.jpg e registrada no post.")
        return

    if a.cmd == "produto":
        meta = yaml.safe_load((POSTS / f"{a.slug}.md").read_text(encoding="utf-8").split("---", 2)[1])
        with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as f:
            catalogo = {p["id"]: p for p in csv.DictReader(f)}
        corpo = (POSTS / f"{a.slug}.md").read_text(encoding="utf-8")
        ids = [a.id] if a.id else (meta.get("produtos") or re.findall(r"\{\{\s*(?:produto|link|botao):([\w\-]+)", corpo))
        ids = [i for i in ids if i in catalogo and catalogo[i].get("imagem_url", "").startswith("http")]
        if not ids:
            sys.exit("Nenhum produto com foto citado no post. Use 'buscar' para uma foto livre.")
        p = catalogo[ids[0]]
        salvar(foto_produto(p["imagem_url"]), a.slug)
        gravar_frontmatter(a.slug, {"arquivo": f"{a.slug}.jpg", "credito": f"{p.get('marca') or 'Fabricante'}/Divulgação",
                                     "licenca": "Divulgação", "fonte": p.get("url_produto") or ""})
        print(f"Foto do produto {p['nome']} salva em content/imagens/{a.slug}.jpg.")
        return

    if a.cmd == "faltando":
        for c in sorted(POSTS.glob("*.md")):
            meta = yaml.safe_load(c.read_text(encoding="utf-8").split("---", 2)[1]) or {}
            if not (meta.get("imagem") or {}).get("arquivo"):
                print(f"{c.stem}  ({meta.get('tipo')}, {meta.get('editoria') or meta.get('subnicho')})")


if __name__ == "__main__":
    main()
