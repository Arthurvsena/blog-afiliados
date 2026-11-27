"""Banners das campanhas do agente de marketing (Black Friday, Natal, cupons, ofertas).

Lê uma campanha de data/campanhas.json, baixa as fotos reais dos produtos dela (imagem_url do
data/produtos.csv) e gera as peças em content/imagens/banners/ (o site publica em /img/banners/):

  ID-faixa.jpg    1600x300   faixa do topo do site (computador)
  ID-faixa-m.jpg  800x300    faixa do topo no celular
  ID-card.jpg     800x640    meio dos posts, coluna lateral e página /ofertas/
  ID-quadrado.jpg 1080x1080  redes sociais (WhatsApp, Instagram, X)

Uso: python3 scripts/banner.py ID_DA_CAMPANHA      (ou --todas para as ativas e as próximas)
Texto do banner sai dos campos da campanha: selo, titulo, chamada, cta. Nunca coloque preço nem
desconto que não esteja confirmado (cupom do dono ou página oficial do Mercado Livre).
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import random
import sys
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "video" / "public" / "InterTight.ttf"
SAIDA = RAIZ / "content" / "imagens" / "banners"
CACHE = Path("/tmp/nexus-banner-fotos")

# fundo (2 cores do degradê), destaque (pílula e botão), cor do texto no destaque, enfeite
TEMAS = {
    "black-friday": {"fundo": ((5, 5, 7), (22, 18, 40)), "destaque": (255, 214, 10), "no_destaque": (5, 5, 7),
                     "titulo": (255, 255, 255), "apoio": (205, 205, 215), "brilho": (124, 92, 255), "enfeite": "listras"},
    "natal": {"fundo": ((4, 38, 28), (12, 78, 54)), "destaque": (245, 196, 81), "no_destaque": (40, 12, 12),
              "titulo": (255, 255, 255), "apoio": (226, 236, 226), "brilho": (210, 32, 48), "enfeite": "neve"},
    "ano-novo": {"fundo": ((6, 6, 20), (30, 22, 60)), "destaque": (245, 196, 81), "no_destaque": (20, 12, 0),
                 "titulo": (255, 255, 255), "apoio": (215, 210, 230), "brilho": (245, 196, 81), "enfeite": "brilhos"},
    "cupom": {"fundo": ((30, 16, 90), (8, 6, 20)), "destaque": (61, 220, 151), "no_destaque": (4, 30, 18),
              "titulo": (255, 255, 255), "apoio": (214, 206, 255), "brilho": (124, 92, 255), "enfeite": "brilhos"},
    "oferta": {"fundo": ((5, 5, 7), (34, 22, 80)), "destaque": (124, 92, 255), "no_destaque": (255, 255, 255),
               "titulo": (255, 255, 255), "apoio": (200, 200, 214), "brilho": (124, 92, 255), "enfeite": "brilhos"},
}


def fonte(tam, peso=800):
    f = ImageFont.truetype(str(FONTE), int(tam))
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def catalogo():
    with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as f:
        return {p["id"].strip(): p for p in csv.DictReader(f)
                if (p.get("ativo") or "").strip().lower() == "sim" and (p.get("link_afiliado") or "").startswith("https://")}


def foto(url):
    """Foto do produto, recortada sem as bordas brancas (as fotos do Mercado Livre têm fundo branco)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    arq = CACHE / (hashlib.md5(url.encode()).hexdigest() + ".png")
    if not arq.exists():
        r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 NexusTech banner"})
        r.raise_for_status()
        Image.open(io.BytesIO(r.content)).convert("RGB").save(arq)
    im = Image.open(arq).convert("RGB")
    cinza = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 12 else 0)
    caixa = cinza.getbbox()
    return im.crop(caixa) if caixa else im


def degrade(w, h, c1, c2):
    base = Image.new("RGB", (w, h), c1)
    topo = Image.new("RGB", (w, h), c2)
    g = Image.linear_gradient("L")              # 256x256, de cima (0) para baixo (255)
    vert = g.resize((w, h))
    hor = g.rotate(90).transpose(Image.FLIP_LEFT_RIGHT).resize((w, h))
    masc = Image.blend(hor, vert, 0.3)   # degradê diagonal suave (da esquerda/topo para a direita/baixo)
    return Image.composite(topo, base, masc)


def brilho(img, centro, raio, cor, forca=140):
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    x, y = centro
    d.ellipse((x - raio, y - raio, x + raio, y + raio), fill=cor + (forca,))
    img.alpha_composite(camada.filter(ImageFilter.GaussianBlur(raio * 0.55)))


def enfeitar(img, tema, semente):
    w, h = img.size
    rnd = random.Random(semente)
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    tipo = TEMAS[tema]["enfeite"]
    if tipo == "listras":   # faixas diagonais discretas, clima de etiqueta de oferta
        passo = max(28, h // 7)
        for x in range(-h, w + h, passo * 2):
            d.polygon([(x, 0), (x + passo, 0), (x + passo - h, h), (x - h, h)], fill=(255, 255, 255, 9))
    elif tipo == "neve":
        for _ in range(int(w * h / 5200)):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(1.2, 3.6) * h / 600
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rnd.randint(60, 170)))
    else:
        for _ in range(int(w * h / 26000)):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(2, 6) * h / 600
            cor = TEMAS[tema]["destaque"]
            d.line((x - r * 2, y, x + r * 2, y), fill=cor + (110,), width=max(1, int(r / 2)))
            d.line((x, y - r * 2, x, y + r * 2), fill=cor + (110,), width=max(1, int(r / 2)))
    img.alpha_composite(camada)


def quebrar(d, texto, f, largura):
    linhas, atual = [], ""
    for p in texto.split():
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) <= largura or not atual:
            atual = t
        else:
            linhas.append(atual)
            atual = p
    return linhas + ([atual] if atual else [])


def caber(d, texto, largura, altura, maximo, minimo, linhas_max=3, peso=850):
    for tam in range(int(maximo), int(minimo) - 1, -2):
        f = fonte(tam, peso)
        ls = quebrar(d, texto, f, largura)
        if len(ls) <= linhas_max and len(ls) * tam * 1.05 <= altura and all(d.textlength(l, font=f) <= largura for l in ls):
            return f, ls, tam
    f = fonte(minimo, peso)
    return f, quebrar(d, texto, f, largura)[:linhas_max], minimo


def pilula(d, x, y, texto, tam, cor, cor_texto):
    f = fonte(tam, 800)
    larg = d.textlength(texto, font=f)
    alt = tam * 1.55
    d.rounded_rectangle((x, y, x + larg + tam * 1.3, y + alt), radius=alt / 2, fill=cor)
    d.text((x + tam * 0.65, y + alt / 2), texto, font=f, fill=cor_texto, anchor="lm")
    return x + larg + tam * 1.3, y + alt


def cartao_foto(img, im, caixa, raio, sombra=True, inclinar=0):
    """Foto do produto num cartão branco arredondado (as fotos do ML ficam limpas assim)."""
    x0, y0, x1, y1 = [int(v) for v in caixa]
    w, h = x1 - x0, y1 - y0
    cart = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(cart).rounded_rectangle((0, 0, w - 1, h - 1), radius=raio, fill=(255, 255, 255, 255))
    margem = int(min(w, h) * 0.1)
    p = ImageOps.contain(im, (w - 2 * margem, h - 2 * margem), Image.LANCZOS)
    cart.paste(p, ((w - p.width) // 2, (h - p.height) // 2))
    if inclinar:
        cart = cart.rotate(inclinar, resample=Image.BICUBIC, expand=True)
    if sombra:
        s = Image.new("RGBA", img.size, (0, 0, 0, 0))
        m = cart.split()[3].point(lambda v: 150 if v else 0)
        s.paste((0, 0, 0, 255), (x0 + int(h * 0.03), y0 + int(h * 0.06)), m)
        img.alpha_composite(s.filter(ImageFilter.GaussianBlur(max(4, h // 18))))
    img.alpha_composite(cart, (x0, y0))


def logo(d, x, y, s, nome=True):
    roxo = (124, 92, 255)
    d.rounded_rectangle((x, y, x + s, y + s), radius=s * 0.24, fill=roxo)
    k = s / 64
    d.line([(x + 20 * k, y + 46 * k), (x + 20 * k, y + 18 * k), (x + 44 * k, y + 46 * k), (x + 44 * k, y + 18 * k)],
           fill="white", width=max(2, int(6 * k)), joint="curve")
    if nome:
        f = fonte(s * 0.58, 750)
        d.text((x + s * 1.25, y + s / 2), "Nexus", font=f, fill="white", anchor="lm")
        d.text((x + s * 1.25 + d.textlength("Nexus ", font=f), y + s / 2), "Tech", font=f, fill=(166, 147, 255), anchor="lm")


def fotos_da(camp, cat, n):
    ims = []
    for pid in camp.get("produtos") or []:
        p = cat.get(pid)
        if p and (p.get("imagem_url") or "").startswith("http"):
            try:
                ims.append(foto(p["imagem_url"]))
            except Exception as e:
                print(f"  sem foto de {pid}: {e}", file=sys.stderr)
        if len(ims) == n:
            break
    return ims


def textos(camp):
    t = camp.get("banner") or {}
    return (t.get("selo") or camp.get("nome", "").upper(), t.get("titulo") or camp.get("titulo", ""),
            t.get("chamada") or camp.get("chamada", ""), t.get("cta") or "Ver ofertas")


def fundo(w, h, tema, semente):
    T = TEMAS[tema]
    img = degrade(w, h, *T["fundo"]).convert("RGBA")
    enfeitar(img, tema, semente)
    return img


def faixa(camp, cat, w, h, compacta=False):
    tema = camp.get("tema", "oferta")
    T = TEMAS[tema]
    img = fundo(w, h, tema, camp["id"] + str(w))
    selo, titulo, chamada, cta = textos(camp)
    n_fotos = 2 if compacta else 4
    ims = fotos_da(camp, cat, n_fotos)
    area_fotos = int(w * (0.40 if compacta else 0.44)) if ims else 0
    brilho(img, (w - area_fotos // 2, h // 2), int(h * 0.75), T["brilho"], 110)
    # fotos em leque à direita (com folga para a inclinação não cortar nas bordas)
    if ims:
        lado = int(h * (0.62 if compacta else 0.64))
        passo = (area_fotos - lado * 1.15) / max(1, len(ims) - 1) if len(ims) > 1 else 0
        x0 = w - area_fotos - int(h * 0.02)
        for i, im in enumerate(ims):
            ang = (i - (len(ims) - 1) / 2) * 4
            y = (h - lado) / 2 - h * 0.02 + (abs(i - (len(ims) - 1) / 2) * h * 0.03)
            cartao_foto(img, im, (x0 + i * passo, y, x0 + i * passo + lado, y + lado), int(lado * 0.12), inclinar=ang)
    d = ImageDraw.Draw(img)
    m = int(h * 0.11)
    larg_txt = w - area_fotos - m * 2.4
    _, yb = pilula(d, m, m * 0.8, selo, h * (0.075 if compacta else 0.065), T["destaque"], T["no_destaque"])
    alt_cta = h * (0.06 if compacta else 0.07) * 1.55
    y_cta = h - m * 0.8 - alt_cta
    sobra = y_cta - yb - h * 0.06   # espaço entre o selo e o botão
    f, ls, tam = caber(d, titulo, larg_txt, sobra * (0.95 if compacta else 0.72), h * (0.2 if compacta else 0.17), h * 0.09, 2)
    y = yb + h * 0.035
    for l in ls:
        d.text((m, y), l, font=f, fill=T["titulo"])
        y += tam * 1.04
    if chamada and not compacta:
        f2, ls2, t2 = caber(d, chamada, larg_txt, h * 0.09, h * 0.07, h * 0.05, 1, 500)
        if ls2 and y + t2 * 1.1 <= y_cta - h * 0.03:
            d.text((m, y + h * 0.015), ls2[0], font=f2, fill=T["apoio"])
    pilula(d, m, y_cta, cta + "  →", h * (0.06 if compacta else 0.07), T["titulo"], (5, 5, 7))
    return img.convert("RGB")


def card(camp, cat, w=800, h=640):
    tema = camp.get("tema", "oferta")
    T = TEMAS[tema]
    img = fundo(w, h, tema, camp["id"] + "card")
    selo, titulo, chamada, cta = textos(camp)
    ims = fotos_da(camp, cat, 3)
    brilho(img, (w // 2, int(h * 0.72)), int(w * 0.42), T["brilho"], 120)
    d = ImageDraw.Draw(img)
    m = int(w * 0.07)
    logo(d, m, m * 0.85, w * 0.05)
    _, yb = pilula(d, m, m * 0.85 + w * 0.075, selo, w * 0.03, T["destaque"], T["no_destaque"])
    f, ls, tam = caber(d, titulo, w - 2 * m, h * 0.26, w * 0.085, w * 0.05, 2)
    y = yb + h * 0.03
    for l in ls:
        d.text((m, y), l, font=f, fill=T["titulo"])
        y += tam * 1.04
    if chamada:
        f2, ls2, t2 = caber(d, chamada, w - 2 * m, h * 0.1, w * 0.036, w * 0.028, 2, 500)
        for l in ls2[:2]:
            d.text((m, y + 4), l, font=f2, fill=T["apoio"])
            y += t2 * 1.2
    if ims:
        lado = int(min(h - y - h * 0.2, w * 0.3))
        total = len(ims) * lado + (len(ims) - 1) * lado * 0.12
        x = (w - total) / 2
        yf = y + h * 0.04
        for i, im in enumerate(ims):
            ang = (i - (len(ims) - 1) / 2) * -4
            cartao_foto(img, im, (x, yf, x + lado, yf + lado), int(lado * 0.12), inclinar=ang)
            x += lado * 1.12
    pilula(d, m, h - m - w * 0.06, cta + "  →", w * 0.034, T["destaque"], T["no_destaque"])
    return img.convert("RGB")


def quadrado(camp, cat, s=1080):
    tema = camp.get("tema", "oferta")
    T = TEMAS[tema]
    img = fundo(s, s, tema, camp["id"] + "quad")
    selo, titulo, chamada, cta = textos(camp)
    ims = fotos_da(camp, cat, 4)
    brilho(img, (s // 2, int(s * 0.68)), int(s * 0.4), T["brilho"], 120)
    d = ImageDraw.Draw(img)
    m = int(s * 0.07)
    logo(d, m, m, s * 0.055)
    _, yb = pilula(d, m, m + s * 0.1, selo, s * 0.03, T["destaque"], T["no_destaque"])
    f, ls, tam = caber(d, titulo, s - 2 * m, s * 0.25, s * 0.09, s * 0.055, 3)
    y = yb + s * 0.025
    for l in ls:
        d.text((m, y), l, font=f, fill=T["titulo"])
        y += tam * 1.04
    if ims:
        cols = 2
        lado = int(min((s - 2 * m - s * 0.04) / cols, (s - y - s * 0.2) / math.ceil(len(ims) / cols)))
        for i, im in enumerate(ims):
            linha, col = divmod(i, cols)
            n_lin = min(cols, len(ims) - linha * cols)
            x = (s - (n_lin * lado + (n_lin - 1) * s * 0.03)) / 2 + col * (lado + s * 0.03)
            yy = y + s * 0.03 + linha * (lado + s * 0.025)
            cartao_foto(img, im, (x, yy, x + lado, yy + lado), int(lado * 0.1))
    f3 = fonte(s * 0.03, 600)
    d.text((s / 2, s - m * 0.9), "nexustechai.com.br/ofertas", font=f3, fill=T["apoio"], anchor="ms")
    return img.convert("RGB")


def gerar(camp, cat):
    SAIDA.mkdir(parents=True, exist_ok=True)
    pecas = {
        "faixa": faixa(camp, cat, 1600, 300),
        "faixa-m": faixa(camp, cat, 800, 300, compacta=True),
        "card": card(camp, cat),
        "quadrado": quadrado(camp, cat),
    }
    saida = {}
    for nome, im in pecas.items():
        arq = SAIDA / f"{camp['id']}-{nome}.jpg"
        im.save(arq, quality=86, optimize=True, progressive=True)
        saida[nome] = f"banners/{arq.name}"
    return saida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--todas", action="store_true", help="todas as campanhas ativas e as que começam nos próximos 7 dias")
    a = ap.parse_args()
    caminho = RAIZ / "data" / "campanhas.json"
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    hoje = dt.date.today().isoformat()
    limite = (dt.date.today() + dt.timedelta(days=7)).isoformat()
    cat = catalogo()
    feitas = 0
    for c in dados.get("campanhas", []):
        quer = c["id"] in a.ids or (a.todas and c.get("ativo", True) and c.get("fim", "9999") >= hoje and c.get("inicio", "") <= limite)
        if not quer:
            continue
        faltam = [p for p in c.get("produtos", []) if p not in cat]
        if faltam:
            print(f"{c['id']}: produtos fora do catálogo ativo (ignorados): {', '.join(faltam)}")
        c["banners"] = gerar(c, cat)
        print(f"{c['id']}: {', '.join(c['banners'].values())}")
        feitas += 1
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not feitas:
        print("Nenhuma campanha para gerar.")


if __name__ == "__main__":
    main()
