"""Gera os vídeos do canal Nexus Tech (Shorts 9:16 e vídeos longos 16:9).

Entrada: um roteiro JSON em data/videos/roteiros/ (escrito pelo agente `roteirista`):
{
  "tipo": "short" | "longo",
  "slug": "2026-11-03-galaxy-preco",          # nome do arquivo de saída
  "post": "slug-do-post-no-blog",
  "titulo": "Título do vídeo no YouTube",
  "descricao": "Descrição completa (o produtor acrescenta links e créditos)",
  "tags": ["..."],
  "selo": "Celulares",                          # rótulo no topo (editoria ou subnicho)
  "resumo": "2 a 3 frases para o topo da descrição",
  "hashtags": ["iPhone", "Apple"],
  "capa_texto": "Texto da miniatura (só vídeo longo)",
  "capitulos_desc": ["0:00 Introdução", "0:25 Redmi Buds 6 Play"],
  "cenas": [
    {"fala": "texto narrado, com números por extenso",
     "tela": "texto curto na tela (opcional; padrão = a própria fala)",
     "imagem": "content/imagens/slug.jpg" | "produto:ID" | null,
     "capitulo": "nome do capítulo (só vídeos longos, opcional)"}
  ]
}

Uso:
  python3 scripts/video.py data/videos/roteiros/ARQ.json [--audio narracao.mp3] [--saida DIR]
  python3 scripts/video.py ROTEIRO.json --descricao   # só a descrição do YouTube
  python3 scripts/video.py --voz            # baixa a voz grátis (Piper pt-BR) se faltar

Narração: sem --audio, cada cena é narrada pela voz grátis (Piper). Com --audio
(ex.: um MP3 do ElevenLabs com o roteiro inteiro), o tempo de cada cena é
dividido pelo tamanho da fala. O vídeo final fica abaixo de 9,5 MB (limite do
envio pelo Chrome).
"""
import argparse
import csv
import io
import json
import math
import re
import subprocess
import sys
import tempfile
import urllib.request
import wave
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "site" / "fontes" / "InterTight.ttf"
VOZES = Path.home() / ".cache" / "nexus-vozes"
VOZ = "pt_BR-faber-medium"
VOZ_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR/faber/medium/"
LIMITE_MB = 9.3
ROXO, ROXO_CLARO, FUNDO, BRANCO = (124, 92, 255), (166, 147, 255), (5, 5, 7), (244, 244, 246)
UA = "NexusTech/1.0 (https://github.com/Arthurvsena/blog-afiliados)"


# ---------------- utilidades ----------------
def fonte(tam, peso=800):
    f = ImageFont.truetype(str(FONTE), tam)
    try:
        f.set_variation_by_axes([peso])
    except Exception:
        pass
    return f


def rodar(cmd, entrada=None):
    r = subprocess.run(cmd, input=entrada, capture_output=True)
    if r.returncode != 0:
        sys.exit(f"Falhou: {' '.join(map(str, cmd[:4]))}...\n{r.stderr.decode(errors='ignore')[-1500:]}")
    return r


def duracao(arq):
    r = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(arq)])
    return float(r.stdout.decode().strip())


def baixar_voz():
    VOZES.mkdir(parents=True, exist_ok=True)
    for ext in (".onnx", ".onnx.json"):
        destino = VOZES / f"{VOZ}{ext}"
        if not destino.exists() or destino.stat().st_size < 1000:
            req = urllib.request.Request(VOZ_URL + VOZ + ext, headers={"User-Agent": UA})
            destino.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return VOZES / f"{VOZ}.onnx"


def narrar_piper(texto, destino):
    modelo = baixar_voz()
    rodar([sys.executable, "-m", "piper", "-m", str(modelo), "-f", str(destino),
           "--length-scale", "0.88", "--sentence-silence", "0.15"], entrada=texto.encode("utf-8"))


def imagem_de(ref, catalogo):
    """Abre a imagem de uma cena: arquivo do repositório ou foto de produto do catálogo."""
    if not ref:
        return None, False
    if str(ref).startswith("produto:"):
        p = catalogo.get(ref.split(":", 1)[1])
        if not p or not p.get("imagem_url", "").startswith("http"):
            return None, False
        for url in (re.sub(r"-[A-Z]\.(webp|jpg)$", r"-F.\1", p["imagem_url"]), p["imagem_url"]):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                return Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert("RGB"), True
            except Exception:
                continue
        return None, False
    caminho = RAIZ / ref
    return (Image.open(caminho).convert("RGB"), False) if caminho.exists() else (None, False)


def produto_em_cartao(img, w, h):
    """Foto de produto (fundo branco) num cartão claro com sombra suave."""
    cartao = Image.new("RGB", (w, h), (236, 238, 243))
    luz = Image.new("L", (w, h), 0)
    ImageDraw.Draw(luz).ellipse((w * 0.1, -h * 0.3, w * 0.9, h * 0.9), fill=255)
    cartao = Image.composite(Image.new("RGB", (w, h), (250, 250, 252)), cartao, luz.filter(ImageFilter.GaussianBlur(w // 8)))
    cinza = ImageOps.invert(img.convert("L"))
    caixa = cinza.point(lambda v: 255 if v > 12 else 0).getbbox() or (0, 0, *img.size)
    prod = img.crop(caixa)
    esc = min(h * 0.78 / prod.height, w * 0.78 / prod.width)
    prod = prod.resize((max(1, int(prod.width * esc)), max(1, int(prod.height * esc))), Image.LANCZOS)
    mascara = ImageOps.invert(prod.convert("L")).point(lambda v: 255 if v > 10 else v * 25)
    cartao.paste(prod, ((w - prod.width) // 2, (h - prod.height) // 2), mascara)
    return cartao


def quebrar(texto, f, largura, d):
    linhas, atual = [], ""
    for p in texto.split():
        teste = (atual + " " + p).strip()
        if d.textlength(teste, font=f) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas


def pedacos(texto, max_palavras):
    """Divide a fala em pedaços curtos para a legenda (quebra em pontuação quando dá)."""
    palavras, saida, atual = texto.split(), [], []
    for p in palavras:
        atual.append(p)
        if len(atual) >= max_palavras or (len(atual) >= max_palavras // 2 and re.search(r"[.,:;!?]$", p)):
            saida.append(" ".join(atual)); atual = []
    if atual:
        saida.append(" ".join(atual))
    return saida or [texto]


# ---------------- quadros ----------------
class Quadro:
    def __init__(self, rot, tipo, selo):
        self.tipo = tipo
        self.W, self.H = (1080, 1920) if tipo == "short" else (1280, 720)
        self.selo = selo
        self.f_selo = fonte(34 if tipo == "short" else 22, 700)
        self.f_marca = fonte(38 if tipo == "short" else 24, 800)
        self.f_leg = fonte(76 if tipo == "short" else 46, 850)
        self.f_rod = fonte(30 if tipo == "short" else 20, 600)
        self.f_cap = fonte(30 if tipo == "short" else 22, 700)
        self.simbolo = self._simbolo(64 if tipo == "short" else 40)

    def _simbolo(self, s):
        im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        k = s / 64
        Q = lambda a, b: (a * k, b * k)
        d.rounded_rectangle((*Q(4, 4), *Q(60, 60)), radius=int(14 * k), fill=ROXO)
        d.line([Q(20, 46), Q(20, 18), Q(44, 46), Q(44, 18)], fill="white", width=max(2, int(6 * k)), joint="curve")
        for a, b, r, c in ((20, 18, 5, "white"), (44, 46, 5, "white"), (20, 46, 3.5, FUNDO), (44, 18, 3.5, FUNDO)):
            d.ellipse((*Q(a - r, b - r), *Q(a + r, b + r)), fill=c)
        return im

    def fundo_cena(self, img, eh_produto):
        """Prepara a imagem base da cena (maior que a tela, para o zoom lento)."""
        W, H = self.W, self.H
        area = (W, int(W * 1.05)) if self.tipo == "short" else (W, H)
        if img is None:
            base = Image.new("RGB", area, (16, 16, 21))
            d = ImageDraw.Draw(base)
            for i, r in enumerate((area[0] * 0.55, area[0] * 0.35)):
                cx, cy = area[0] * 0.75, area[1] * 0.35
                d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ROXO + ((90,) if i else (160,)), width=8)
        elif eh_produto:
            base = produto_em_cartao(img, *area)
        else:
            base = ImageOps.fit(img, area, Image.LANCZOS)
        return base.resize((int(area[0] * 1.12), int(area[1] * 1.12)), Image.LANCZOS)

    def desenhar(self, base, prog_cena, prog_total, legenda, capitulo, eh_titulo):
        W, H = self.W, self.H
        quadro = Image.new("RGB", (W, H), FUNDO)
        # zoom lento (Ken Burns) na imagem
        bw, bh = base.size
        z = 1.0 + 0.10 * prog_cena
        cw, ch = int(bw / 1.12 * (1.12 / z)), int(bh / 1.12 * (1.12 / z))
        x0, y0 = int((bw - cw) * (0.5 + 0.15 * (prog_cena - 0.5))), (bh - ch) // 2
        area_w, area_h = int(bw / 1.12), int(bh / 1.12)
        img = base.crop((x0, y0, x0 + cw, y0 + ch)).resize((area_w, area_h), Image.BILINEAR)
        if self.tipo == "short":
            topo = 180
            quadro.paste(img, (0, topo))
            grad = Image.linear_gradient("L").resize((W, 420))
            quadro.paste(Image.new("RGB", (W, 420), FUNDO), (0, topo + area_h - 420), grad)
        else:
            quadro.paste(img, (0, 0))
            grad = Image.linear_gradient("L").resize((W, H // 2))
            quadro.paste(Image.new("RGB", (W, H // 2), FUNDO), (0, H - H // 2), grad)
            topo_g = Image.linear_gradient("L").rotate(180).resize((W, 150)).point(lambda v: int(v * 0.85))
            quadro.paste(Image.new("RGB", (W, 150), FUNDO), (0, 0), topo_g)
        d = ImageDraw.Draw(quadro)
        # barra de progresso
        d.rectangle((0, 0, int(W * prog_total), 8 if self.tipo == "short" else 5), fill=ROXO)
        # marca + selo
        m = 48 if self.tipo == "short" else 28
        y = 60 if self.tipo == "short" else 22
        quadro.paste(self.simbolo, (m, y), self.simbolo)
        tx = m + self.simbolo.width + 14
        ty = y + (self.simbolo.height - self.f_marca.size) // 2 - 4
        d.text((tx, ty), "Nexus", font=self.f_marca, fill=BRANCO)
        d.text((tx + d.textlength("Nexus ", font=self.f_marca), ty), "Tech", font=self.f_marca, fill=ROXO_CLARO)
        if self.selo:
            sw = d.textlength(self.selo, font=self.f_selo) + 44
            sx = W - m - sw
            d.rounded_rectangle((sx, y + 6, sx + sw, y + self.simbolo.height - 6), radius=40, fill=(23, 23, 30), outline=(60, 60, 75), width=2)
            d.text((sx + 22, y + (self.simbolo.height - self.f_selo.size) // 2 - 2), self.selo, font=self.f_selo, fill=BRANCO)
        # capítulo (vídeo longo)
        if capitulo and self.tipo == "longo":
            cw2 = d.textlength(capitulo.upper(), font=self.f_cap) + 30
            d.rounded_rectangle((m, H - 250, m + cw2, H - 214), radius=6, fill=ROXO)
            d.text((m + 15, H - 248), capitulo.upper(), font=self.f_cap, fill="white")
        # legenda
        f = self.f_leg if not eh_titulo else fonte(self.f_leg.size + (14 if self.tipo == "short" else 8), 900)
        larg = W - 2 * m - (0 if self.tipo == "short" else 220)
        linhas = quebrar(legenda, f, larg, d)
        alt_l = int(f.size * 1.18)
        if self.tipo == "short":
            yb = 1370 if not eh_titulo else 1330
        else:
            yb = H - 190 if not capitulo else H - 196
            yb = yb - (len(linhas) - 1) * alt_l + (40 if not capitulo else 50)
        for i, ln in enumerate(linhas):
            lw = d.textlength(ln, font=f)
            lx = (W - lw) / 2 if self.tipo == "short" else m
            ly = yb + i * alt_l
            d.rounded_rectangle((lx - 18, ly - 6, lx + lw + 18, ly + f.size + 14), radius=14,
                                fill=ROXO if (eh_titulo and self.tipo == "short") else (12, 12, 16))
            d.text((lx, ly), ln, font=f, fill="white")
        # rodapé
        rod = "Link na bio · nexustechai.com.br" if self.tipo == "short" else "nexustechai.com.br · links na descrição"
        rw = d.textlength(rod, font=self.f_rod)
        ry = H - (150 if self.tipo == "short" else 46)
        d.text(((W - rw) / 2 if self.tipo == "short" else W - m - rw, ry), rod, font=self.f_rod, fill=(185, 185, 198))
        return quadro


# ---------------- montagem ----------------
def montar(rot, audio_externo=None, saida=None):
    tipo = rot.get("tipo", "short")
    fps = 30 if tipo == "short" else 24
    cenas = [c for c in rot["cenas"] if c.get("fala")]
    if not cenas:
        sys.exit("Roteiro sem cenas.")
    with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as fcsv:
        catalogo = {p["id"]: p for p in csv.DictReader(fcsv)}
    tmp = Path(tempfile.mkdtemp(prefix="video-"))
    folga = 0.25

    # 1) narração e tempo de cada cena
    if audio_externo:
        total_audio = duracao(audio_externo)
        pesos = [len(c["fala"]) for c in cenas]
        tempos = [total_audio * p / sum(pesos) for p in pesos]
        audio_final = Path(audio_externo)
        motor = "elevenlabs"
    else:
        tempos, partes = [], []
        for i, c in enumerate(cenas):
            wav = tmp / f"fala{i:02d}.wav"
            narrar_piper(c["fala"], wav)
            with wave.open(str(wav)) as w:
                tempos.append(w.getnframes() / w.getframerate() + folga)
            partes.append(wav)
        lista = tmp / "lista.txt"
        silencio = tmp / "silencio.wav"
        with wave.open(str(partes[0])) as w:
            taxa, canais, larg = w.getframerate(), w.getnchannels(), w.getsampwidth()
        with wave.open(str(silencio), "wb") as w:
            w.setnchannels(canais); w.setsampwidth(larg); w.setframerate(taxa)
            w.writeframes(b"\0" * int(taxa * folga) * larg * canais)
        lista.write_text("".join(f"file '{p}'\nfile '{silencio}'\n" for p in partes))
        audio_final = tmp / "narracao.wav"
        rodar(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), str(audio_final)])
        motor = "piper"
    total = sum(tempos)

    # 2) quadros
    q = Quadro(rot, tipo, rot.get("selo", ""))
    sem_audio = tmp / "sem_audio.mp4"
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{q.W}x{q.H}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(sem_audio)],
                           stdin=subprocess.PIPE)
    decorrido = 0.0
    capitulo = ""
    for i, (c, dur) in enumerate(zip(cenas, tempos)):
        img, eh_prod = imagem_de(c.get("imagem"), catalogo)
        base = q.fundo_cena(img, eh_prod)
        capitulo = c.get("capitulo") or capitulo
        tela = c.get("tela") or c["fala"]
        eh_titulo = i == 0
        trechos = [tela] if (eh_titulo or c.get("tela")) else pedacos(tela, 6 if tipo == "short" else 8)
        n = max(1, int(round(dur * fps)))
        cache = {}
        for k in range(n):
            t = k / n
            trecho = trechos[min(len(trechos) - 1, int(t * len(trechos)))]
            chave = (k // 2, trecho)  # metade dos quadros reaproveitados: zoom continua suave
            if chave not in cache:
                cache.clear()
                cache[chave] = q.desenhar(base, t, (decorrido + t * dur) / total, trecho, capitulo, eh_titulo).tobytes()
            enc.stdin.write(cache[chave])
        decorrido += dur
    enc.stdin.close()
    enc.wait()

    # 3) junta áudio e comprime até caber no limite
    saida = Path(saida or RAIZ / "_videos")
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / f"{rot['slug']}.mp4"
    kbps_audio = 96
    alvo_kbps = int(LIMITE_MB * 8 * 1024 / max(total, 1)) - kbps_audio
    alvo_kbps = max(250, min(alvo_kbps, 4500 if tipo == "short" else 2500))
    rodar(["ffmpeg", "-y", "-v", "error", "-i", str(sem_audio), "-i", str(audio_final),
           "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage",
           "-b:v", f"{alvo_kbps}k", "-maxrate", f"{int(alvo_kbps * 1.3)}k", "-bufsize", f"{alvo_kbps * 2}k",
           "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", f"{kbps_audio}k",
           "-movflags", "+faststart", "-shortest", str(destino)])
    mb = destino.stat().st_size / 1024 / 1024
    # capa (miniatura) do vídeo longo
    capa = None
    if tipo == "longo":
        img, eh_prod = imagem_de(cenas[0].get("imagem"), catalogo)
        capa = saida / f"{rot['slug']}-capa.jpg"
        q.desenhar(q.fundo_cena(img, eh_prod), 0.0, 0.0, rot.get("capa_texto") or cenas[0].get("tela") or rot["titulo"], "", True) \
            .resize((1280, 720)).save(capa, quality=90)
    return {"arquivo": str(destino), "mb": round(mb, 2), "segundos": round(total, 1), "voz": motor,
            "capa": str(capa) if capa else None}


def gerar_descricao(rot):
    """Descrição final do YouTube: resumo, link do post, produtos com link de afiliado, avisos e créditos."""
    import yaml
    with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as fcsv:
        catalogo = {p["id"]: p for p in csv.DictReader(fcsv)}
    post = RAIZ / "content" / "posts" / f"{rot.get('post', '')}.md"
    meta = yaml.safe_load(post.read_text(encoding="utf-8").split("---", 2)[1]) if post.exists() else {}
    refs = [str(r) for c in rot["cenas"] for r in ((c.get("imagens") or []) + ([c["imagem"]] if c.get("imagem") else []))]
    ids = list(dict.fromkeys([r.split(":", 1)[1] for r in refs if r.startswith("produto:")]
                             + [c["produto"] for c in rot["cenas"] if c.get("produto")] + (rot.get("produtos") or [])))
    ids = [i for i in ids if catalogo.get(i, {}).get("ativo") == "sim" and catalogo[i].get("link_afiliado")]
    linhas = [rot.get("resumo", "").strip(), ""]
    if meta:
        linhas.append(f"Matéria completa no blog: https://nexustechai.com.br/posts/{rot['post']}/"
                      f"?utm_source=youtube&utm_medium={rot.get('tipo', 'short')}&utm_campaign={rot['slug']}")
    else:
        linhas.append(f"Mais notícias e guias de tecnologia: https://nexustechai.com.br/"
                      f"?utm_source=youtube&utm_medium={rot.get('tipo', 'short')}&utm_campaign={rot['slug']}")
    serie = {"60s": "Nexus em 60s: a notícia de tecnologia do dia em menos de um minuto.",
             "historias": "Histórias Tech: como empresas e produtos de tecnologia subiram, caíram e o que isso ensina.",
             "lafora": "Lá Fora, Aqui: o que bombou lá fora, se chega ao Brasil e por quanto."}.get(rot.get("quadro"))
    if serie:
        linhas += ["", serie + " Inscreva-se: https://www.youtube.com/@TechNexusIA?sub_confirmation=1"]
    if ids:
        linhas += ["", "Produtos do vídeo (links de afiliado):"]
        linhas += [f"- {catalogo[i]['nome']}: {catalogo[i]['link_afiliado']}" for i in ids]
    if rot.get("capitulos_desc"):
        linhas += ["", "Capítulos:"] + rot["capitulos_desc"]
    if ids:
        linhas += ["", "Links de afiliado do Mercado Livre: se você comprar por eles, o canal ganha uma comissão,"
                   " sem custo extra para você. Preços mudam: confira o valor atual no link."]
    else:
        linhas.append("")
    fontes = list(dict.fromkeys([f["nome"] for f in (meta.get("fontes") or []) + (rot.get("fontes") or []) if f.get("nome")]))
    if fontes:
        linhas.append("Fontes: " + ", ".join(fontes) + ".")
    creditos = []
    img = meta.get("imagem") or {}
    if img.get("credito") and f"content/imagens/{img.get('arquivo')}" in refs:
        creditos.append(f"{img['credito']}" + (f" ({img['licenca']})" if img.get("licenca") and img["licenca"] != "Divulgação" else ""))
    creditos += list(dict.fromkeys(rot.get("creditos_extra") or []))
    if ids:
        creditos.append("fotos dos produtos: divulgação dos fabricantes")
    if creditos:
        linhas.append("Imagens: " + "; ".join(creditos) + ".")
    linhas.append("Narração com voz sintética.")
    # as 3 primeiras hashtags aparecem em cima do título: a mais buscada primeiro
    tags = [t.lstrip("#") for t in (rot.get("hashtags") or [])][:4]
    if rot.get("tipo", "short") == "short" and "shorts" not in [t.lower() for t in tags]:
        tags.append("shorts")
    if tags:
        linhas += ["", " ".join("#" + t for t in tags)]
    return "\n".join(l for l in linhas if l is not None).strip()[:4900]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro", nargs="?")
    ap.add_argument("--audio", help="narração pronta (ex.: ElevenLabs) com o roteiro inteiro")
    ap.add_argument("--saida", help="pasta de saída (padrão: _videos/)")
    ap.add_argument("--voz", action="store_true", help="só baixa a voz grátis")
    ap.add_argument("--descricao", action="store_true", help="só imprime a descrição final do YouTube")
    a = ap.parse_args()
    if a.voz:
        print(f"Voz pronta em {baixar_voz()}")
        return
    if not a.roteiro:
        ap.error("informe o roteiro")
    rot = json.loads(Path(a.roteiro).read_text(encoding="utf-8"))
    if a.descricao:
        print(gerar_descricao(rot))
        return
    res = montar(rot, a.audio, a.saida)
    desc = Path(res["arquivo"]).with_suffix(".txt")
    desc.write_text(gerar_descricao(rot), encoding="utf-8")
    res["descricao"] = str(desc)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
