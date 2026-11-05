"""Miniaturas (capas) do canal no padrão do manual: um elemento principal grande, fundo escuro com
brilho violeta, no máximo 3 a 4 palavras que NÃO repetem o título, legível no tamanho de celular.
Gera 2 versões (A e B) para o "Testar e comparar" do YouTube Studio.

Uso: python3 scripts/capa.py IMAGEM SAIDA_BASE "TEXTO DA CAPA" [--selo "LÁ FORA, AQUI"] [--texto-b "OUTRO TEXTO"]
     -> SAIDA_BASE-capa.jpg (A) e SAIDA_BASE-capa-b.jpg (B), 1280x720
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "video" / "public" / "InterTight.ttf"
W, H = 1280, 720
ROXO, ROXO2, FUNDO = (124, 92, 255), (166, 147, 255), (5, 5, 7)
AMARELO = (255, 214, 10)


def fonte(tam, peso=900):
    f = ImageFont.truetype(str(FONTE), tam)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def quebrar(texto, f, largura, d):
    linhas, atual = [], ""
    for p in texto.split(" "):
        t = (atual + " " + p).strip()
        if d.textlength(t, font=f) <= largura or not atual:
            atual = t
        else:
            linhas.append(atual); atual = p
    return linhas + ([atual] if atual else [])


def caber(texto, largura, altura_max, d, maximo=170, minimo=70):
    texto = texto.replace("R$ ", "R$\u00a0").replace("US$ ", "US$\u00a0")  # moeda nunca se separa do número
    for tam in range(maximo, minimo - 1, -6):
        f = fonte(tam)
        linhas = quebrar(texto.upper(), f, largura, d)
        if len(linhas) <= 3 and len(linhas) * tam * 1.02 <= altura_max:
            return f, linhas, tam
    f = fonte(minimo)
    return f, quebrar(texto.upper(), f, largura, d), minimo


def logo(d, x, y, s=54):
    d.rounded_rectangle((x, y, x + s, y + s), radius=s * 0.24, fill=ROXO)
    k = s / 64
    pts = [(x + 20 * k, y + 46 * k), (x + 20 * k, y + 18 * k), (x + 44 * k, y + 46 * k), (x + 44 * k, y + 18 * k)]
    d.line(pts, fill="white", width=max(3, int(6 * k)), joint="curve")


def texto_destacado(d, linhas, f, tam, x, y, cor_destaque):
    """Última palavra (ou a que tem número) com fundo de cor: o olho bate nela primeiro."""
    todas = " ".join(linhas).split(" ")
    alvo = next((p for p in todas if any(ch.isdigit() for ch in p)), todas[-1])
    for i, linha in enumerate(linhas):
        cx = x
        for p in linha.split(" "):
            larg = d.textlength(p, font=f)
            if p == alvo:
                d.rounded_rectangle((cx - 12, y + i * tam * 1.02 + tam * 0.06, cx + larg + 12, y + (i + 1) * tam * 1.02 - tam * 0.02),
                                    radius=14, fill=cor_destaque)
                cor = FUNDO if cor_destaque == AMARELO else (255, 255, 255)
            else:
                cor = (255, 255, 255)
            d.text((cx + 4, y + i * tam * 1.02 + 6), p, font=f, fill=(0, 0, 0))  # sombra
            d.text((cx, y + i * tam * 1.02), p, font=f, fill=cor)
            cx += larg + d.textlength(" ", font=f)


def brilho(img, caixa, cor=ROXO, raio=60):
    camada = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(camada).rounded_rectangle(caixa, radius=28, fill=cor + (230,))
    img.alpha_composite(camada.filter(ImageFilter.GaussianBlur(raio)))


def versao_a(foto, texto, selo):
    """Texto grande à esquerda, foto em destaque à direita com brilho violeta."""
    img = Image.new("RGBA", (W, H), FUNDO + (255,))
    fundo = ImageOps.fit(foto, (W, H)).filter(ImageFilter.GaussianBlur(28))
    fundo = Image.blend(fundo, Image.new("RGB", (W, H), FUNDO), 0.72)
    img.paste(fundo, (0, 0))
    caixa = (560, 70, 1240, 650)
    brilho(img, caixa)
    painel = ImageOps.fit(foto, (caixa[2] - caixa[0], caixa[3] - caixa[1]))
    mascara = Image.new("L", painel.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, *painel.size), radius=28, fill=255)
    img.paste(painel, caixa[:2], mascara)
    d = ImageDraw.Draw(img)
    f, linhas, tam = caber(texto, 560, 470, d)
    y = (H - len(linhas) * tam * 1.02) / 2 + 20
    texto_destacado(d, linhas, f, tam, 48, y, ROXO)
    logo(d, 48, 40)
    if selo:
        d.text((116, 50), selo.upper(), font=fonte(30, 800), fill=ROXO2)
    return img.convert("RGB")


def versao_b(foto, texto, selo):
    """Foto ocupando tudo, escurecida embaixo, texto enorme embaixo com destaque amarelo."""
    img = ImageOps.fit(foto, (W, H)).convert("RGBA")
    grad = Image.new("L", (1, H))
    for yy in range(H):
        grad.putpixel((0, yy), int(235 * max(0, (yy / H - 0.25) / 0.75) ** 1.2))
    sombra = Image.new("RGBA", (W, H), FUNDO + (255,))
    sombra.putalpha(grad.resize((W, H)))
    img.alpha_composite(sombra)
    d = ImageDraw.Draw(img)
    f, linhas, tam = caber(texto, W - 120, 330, d, maximo=180)
    y = H - 48 - len(linhas) * tam * 1.02
    texto_destacado(d, linhas, f, tam, 60, y, AMARELO)
    # moldura violeta fina: identidade do canal
    d.rectangle((0, 0, W - 1, H - 1), outline=ROXO, width=10)
    logo(d, W - 100, 36)
    if selo:
        larg = d.textlength(selo.upper(), font=fonte(30, 800))
        d.rounded_rectangle((36, 36, 36 + larg + 36, 86), radius=25, fill=ROXO)
        d.text((54, 42), selo.upper(), font=fonte(30, 800), fill="white")
    return img.convert("RGB")


def gerar(imagem, base, texto, selo="", texto_b=None):
    foto = ImageOps.exif_transpose(Image.open(imagem)).convert("RGB")
    a = Path(f"{base}-capa.jpg")
    b = Path(f"{base}-capa-b.jpg")
    versao_a(foto, texto, selo).save(a, quality=90)
    versao_b(foto, texto_b or texto, selo).save(b, quality=90)
    return a, b


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("imagem"); ap.add_argument("base"); ap.add_argument("texto")
    ap.add_argument("--selo", default=""); ap.add_argument("--texto-b")
    x = ap.parse_args()
    print(*gerar(x.imagem, x.base, x.texto, x.selo, x.texto_b))
