"""Vídeos com motion (Remotion) para o canal Nexus Tech.

Mesmo roteiro de scripts/video.py, com campos extras por cena:
  "tipo": "gancho" | "fato" | "numero" | "produto" | "cta"   (padrão: fato; 1ª cena = gancho; última = cta)
  "imagens": ["content/imagens/x.jpg", "produto:ID", "busca:termos em inglês"]  (várias fotos por cena)
  "destaque": "R$ 21.999"   (cena numero: o número que sobe na tela)
  "rotulo": "na versão de 256 GB"  (legenda curta do número)
  "produto": "ID"           (cena produto: cartão animado do produto do catálogo)

Uso:
  python3 scripts/video_motion.py data/videos/roteiros/ARQ.json [--audio narracao.mp3] [--saida DIR]

Etapas: baixa as fotos (busca:* vem do Wikimedia Commons, só licença livre, com
crédito), narra com a voz grátis por trechos (tempo exato de cada legenda) ou
usa o áudio pronto do ElevenLabs, renderiza no Remotion (pasta video/) e
comprime para menos de 9,3 MB. Se o Remotion falhar, use scripts/video.py.
"""
import argparse
import csv
import io
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import video as base  # noqa: E402
from PIL import Image, ImageOps  # noqa: E402

RAIZ = base.RAIZ
PROJ = RAIZ / "video"
PUBLICO = PROJ / "public"
UA = base.UA


def chrome():
    if os.environ.get("CHROME_PATH"):
        return os.environ["CHROME_PATH"]
    for padrao in ("/opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell",
                   str(Path.home() / ".cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell")):
        achados = sorted(Path("/").glob(padrao.lstrip("/")))
        if achados:
            return str(achados[-1])
    return None  # o Remotion baixa o próprio navegador


def pegar(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=40).read()


def salvar_img(img, destino, produto=False):
    img = ImageOps.exif_transpose(img).convert("RGB")
    lim = 1400 if not produto else 1000
    img.thumbnail((lim, lim), Image.LANCZOS)
    img.save(destino, quality=88)


def busca_commons(termos, usados):
    """Foto livre do Commons (sem NC/ND), com crédito. Devolve (bytes, credito) ou (None, None)."""
    sys.path.insert(0, str(RAIZ / "scripts"))
    import imagem  # noqa
    import time
    achados = []
    for tentativa in range(4):
        try:
            achados = imagem.buscar_commons(termos, 6)
            break
        except Exception as e:
            print(f"(Commons: {e}; nova tentativa)", file=sys.stderr)
            time.sleep(5 * (tentativa + 1))
    if not achados:
        try:
            achados = [a for a in imagem.buscar_openverse(termos, 8) if a.get("url")]
        except Exception as e:
            print(f"(Openverse: {e})", file=sys.stderr)
    for a in achados:
        a["url"] = a["url"].replace("width=1920", "width=1280")
    for a in achados:
        if a["url"] in usados:
            continue
        try:
            dados = pegar(a["url"])
            usados.add(a["url"])
            origem = "Wikimedia Commons" if a.get("fonte") == "wikimedia" else (a.get("fonte") or "Openverse")
            return dados, f"{a['autor']}/{origem} ({a['licenca']})"
        except Exception:
            continue
    return None, None


def preparar_imagens(rot, pasta, catalogo, creditos):
    usados = set()
    cache = {}
    for i, c in enumerate(rot["cenas"]):
        refs = c.get("imagens") or ([c["imagem"]] if c.get("imagem") else [])
        saida = []
        for j, ref in enumerate(refs):
            ref = str(ref)
            if ref in cache:
                saida.append(cache[ref]); continue
            nome = f"c{i:02d}-{j}.jpg"
            destino = pasta / nome
            item = None
            try:
                if ref.startswith("produto:"):
                    img, _ = base.imagem_de(ref, catalogo)
                    if img:
                        salvar_img(img, destino, True)
                        item = {"src": f"run/{pasta.name}/{nome}", "produto": True}
                elif ref.startswith("busca:"):
                    dados, cred = busca_commons(ref.split(":", 1)[1].strip(), usados)
                    if dados:
                        salvar_img(Image.open(io.BytesIO(dados)), destino)
                        item = {"src": f"run/{pasta.name}/{nome}", "produto": False}
                        creditos.append(cred)
                else:
                    arq = RAIZ / ref
                    if arq.exists():
                        salvar_img(Image.open(arq), destino)
                        item = {"src": f"run/{pasta.name}/{nome}", "produto": False}
            except Exception as e:
                print(f"(imagem {ref} falhou: {e})", file=sys.stderr)
            if item:
                cache[ref] = item
                saida.append(item)
        c["_imagens"] = saida


def tokens(fala):
    """Fala com marcação {o que aparece|o que se fala}: ex. "{R$ 21.999|vinte e um mil, novecentos e noventa e nove reais}".
    Devolve [(na_tela, falado)]."""
    saida = []
    for m in re.finditer(r"\{([^|{}]+)\|([^{}]+)\}([.,:;!?]*)|(\S+)", fala):
        if m.group(4):
            saida.append((m.group(4), m.group(4)))
        else:
            pont = m.group(3) or ""
            saida.append((m.group(1).strip() + pont, m.group(2).strip() + pont))
    return saida


def falado(fala):
    return " ".join(f for _, f in tokens(fala))


def grupos_de(fala, n=4):
    """Trechos de 2 a 5 itens, quebrando na pontuação: cada um vira um bloco de legenda."""
    saida, atual = [], []
    for tk in tokens(fala):
        atual.append(tk)
        peso = sum(len(f.split()) for _, f in atual)
        if len(atual) >= n or peso >= n + 2 or (len(atual) >= 2 and re.search(r"[.,:;!?]$", tk[1])):
            saida.append(atual); atual = []
    if atual:
        if saida and len(atual) == 1:
            saida[-1] += atual
        else:
            saida.append(atual)
    return saida


def sfx(pasta):
    """Efeitos sonoros sintetizados (sem direitos autorais): whoosh e ding."""
    pasta.mkdir(parents=True, exist_ok=True)
    whoosh, ding = pasta / "whoosh.wav", pasta / "ding.wav"
    if not whoosh.exists():
        base.rodar(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.6",
                    "-af", "highpass=f=400,lowpass=f=6000,afade=t=in:d=0.18,afade=t=out:st=0.2:d=0.25,volume=0.8", str(whoosh)])
    if not ding.exists():
        base.rodar(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "sine=f=1318:d=0.5", "-f", "lavfi", "-i", "sine=f=1976:d=0.5",
                    "-filter_complex", "amix=inputs=2,afade=t=out:st=0.05:d=0.45,volume=0.5", str(ding)])
    return whoosh, ding


def montar(rot, audio_externo=None, saida=None):
    tipo = rot.get("tipo", "short")
    fps = 30
    largura, altura = (1080, 1920) if tipo == "short" else (1280, 720)
    cenas = [c for c in rot["cenas"] if c.get("fala")]
    rot["cenas"] = cenas
    with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as f:
        catalogo = {p["id"]: p for p in csv.DictReader(f)}
    pasta = PUBLICO / "run" / rot["slug"]
    shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True)
    creditos = []
    preparar_imagens(rot, pasta, catalogo, creditos)
    sfx(PUBLICO / "sfx")

    # narração por trechos
    folga = 0.18
    trechos_por_cena = [grupos_de(c["fala"], 4 if tipo == "short" else 6) for c in cenas]
    if audio_externo:
        total = base.duracao(audio_externo)
        txt = lambda g: " ".join(f for _, f in g)
        soma = sum(len(txt(g)) for gs in trechos_por_cena for g in gs)
        tempos_trechos = [[total * len(txt(g)) / soma for g in gs] for gs in trechos_por_cena]
        audio = pasta / ("narracao" + Path(audio_externo).suffix)
        shutil.copy(audio_externo, audio)
        voz = "elevenlabs"
    else:
        from piper import PiperVoice, SynthesisConfig
        v = PiperVoice.load(str(base.baixar_voz()))
        cfg = SynthesisConfig(length_scale=0.86)
        wavs, tempos_trechos = [], []
        for ci, gs in enumerate(trechos_por_cena):
            tt = []
            for gi, g in enumerate(gs):
                arq = pasta / f"t{ci:02d}-{gi:02d}.wav"
                with wave.open(str(arq), "wb") as wf:
                    v.synthesize_wav(" ".join(f for _, f in g), wf, syn_config=cfg)
                with wave.open(str(arq)) as w:
                    d = w.getnframes() / w.getframerate()
                pausa = folga + (0.22 if gi == len(gs) - 1 else 0.0)
                wavs.append((arq, pausa))
                tt.append(d + pausa)
            tempos_trechos.append(tt)
        # junta com pausas
        with wave.open(str(wavs[0][0])) as w:
            taxa, can, lg = w.getframerate(), w.getnchannels(), w.getsampwidth()
        audio = pasta / "narracao.wav"
        with wave.open(str(audio), "wb") as out:
            out.setnchannels(can); out.setsampwidth(lg); out.setframerate(taxa)
            for arq, pausa in wavs:
                with wave.open(str(arq)) as w:
                    out.writeframes(w.readframes(w.getnframes()))
                out.writeframes(b"\0" * int(taxa * pausa) * lg * can)
        voz = "piper"

    # cenas em quadros
    props_cenas, sons, t = [], [], 0.0
    n = len(cenas)
    for ci, (c, gs, tt) in enumerate(zip(cenas, trechos_por_cena, tempos_trechos)):
        ini = round(t * fps)
        palavras, tg = [], t
        for gi, (g, dg) in enumerate(zip(gs, tt)):
            fala_d = dg - (folga if not audio_externo else 0)
            pesos = [len(f) + 2 for _, f in g]
            tw = tg
            for (tela_p, _), peso in zip(g, pesos):
                dw = fala_d * peso / sum(pesos)
                palavras.append({"t": re.sub(r"[,;:]$", "", tela_p), "ini": round(tw * fps), "fim": round((tw + dw) * fps), "g": f"{ci}-{gi}"})
                tw += dw
            tg += dg
        t = tg
        dur = max(round(t * fps) - ini, 20)
        tipo_c = c.get("tipo") or ("gancho" if ci == 0 else "cta" if ci == n - 1 else "fato")
        cena = {"ini": ini, "dur": dur, "tipo": tipo_c, "tela": c.get("tela") or " ".join(t for t, _ in tokens(c["fala"])), "destaque": c.get("destaque", ""),
                "rotulo": c.get("rotulo", ""), "capitulo": c.get("capitulo", ""), "imagens": c.get("_imagens", []), "palavras": palavras}
        if tipo_c == "produto":
            pid = c.get("produto") or next((r.split(":", 1)[1] for r in (c.get("imagens") or []) if str(r).startswith("produto:")), "")
            p = catalogo.get(pid, {})
            img = next((x["src"] for x in cena["imagens"] if x.get("produto")), None)
            cena["produto"] = {"nome": p.get("nome", ""), "imagem": img,
                               "destaques": [d.strip() for d in (p.get("destaques") or "").split(";") if d.strip()][:4]}
        props_cenas.append(cena)
        if ci > 0:
            sons.append({"ini": max(0, ini - 4), "src": "sfx/whoosh.wav", "vol": 0.22})
        if tipo_c == "numero":
            sons.append({"ini": ini + 24, "src": "sfx/ding.wav", "vol": 0.25})
    duracao = round(t * fps) + 20
    props = {"tipo": tipo, "fps": fps, "largura": largura, "altura": altura, "duracao": duracao, "selo": rot.get("selo", ""),
             "audio": f"run/{rot['slug']}/{audio.name}", "cenas": props_cenas, "sons": sons}
    arq_props = pasta / "props.json"
    arq_props.write_text(json.dumps(props, ensure_ascii=False))

    # render
    if not (PROJ / "node_modules").exists():
        subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=PROJ, check=True)
    bruto = pasta / "bruto.mp4"
    env = dict(os.environ)
    if chrome():
        env["CHROME_PATH"] = chrome()
    r = subprocess.run(["node", "render.mjs", str(arq_props), str(bruto)], cwd=PROJ, env=env)
    if r.returncode != 0 or not bruto.exists():
        sys.exit("Render do Remotion falhou (use scripts/video.py como reserva).")

    # comprime para caber no envio pelo Chrome
    saida = Path(saida or RAIZ / "_videos")
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / f"{rot['slug']}.mp4"
    total = duracao / fps
    kbps_a = 128
    alvo = max(400, min(int(base.LIMITE_MB * 8 * 1024 / total) - kbps_a, 6000 if tipo == "short" else 3000))
    base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(bruto), "-c:v", "libx264", "-preset", "medium",
                "-b:v", f"{alvo}k", "-maxrate", f"{int(alvo * 1.25)}k", "-bufsize", f"{alvo * 2}k", "-pix_fmt", "yuv420p",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", f"{kbps_a}k", "-movflags", "+faststart", str(destino)])
    if destino.stat().st_size > 9.6 * 1024 * 1024:
        alvo = int(alvo * 0.8)
        base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(bruto), "-c:v", "libx264", "-preset", "medium", "-b:v", f"{alvo}k",
                    "-maxrate", f"{alvo}k", "-bufsize", f"{alvo * 2}k", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                    "-movflags", "+faststart", str(destino) + ".tmp.mp4"])
        os.replace(str(destino) + ".tmp.mp4", destino)

    capa = None
    if tipo == "longo":
        primeira = next((x for c in props_cenas for x in c["imagens"]), None)
        q = base.Quadro(rot, "longo", rot.get("selo", ""))
        img = Image.open(PUBLICO / primeira["src"]).convert("RGB") if primeira else None
        capa = saida / f"{rot['slug']}-capa.jpg"
        q.desenhar(q.fundo_cena(img, bool(primeira and primeira.get("produto"))), 0.0, 0.0,
                   rot.get("capa_texto") or rot["titulo"], "", True).save(capa, quality=90)
    rot["creditos_extra"] = creditos
    return {"arquivo": str(destino), "mb": round(destino.stat().st_size / 1024 / 1024, 2), "segundos": round(total, 1),
            "voz": voz, "capa": str(capa) if capa else None, "creditos": creditos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--audio")
    ap.add_argument("--saida")
    ap.add_argument("--manter", action="store_true", help="não apaga a pasta temporária em video/public/run/")
    ap.add_argument("--fala", action="store_true", help="só imprime o texto falado inteiro (para o ElevenLabs)")
    a = ap.parse_args()
    rot = json.loads(Path(a.roteiro).read_text(encoding="utf-8"))
    if a.fala:
        print(" ".join(falado(c["fala"]) for c in rot["cenas"] if c.get("fala")))
        return
    res = montar(rot, a.audio, a.saida)
    desc = Path(res["arquivo"]).with_suffix(".txt")
    desc.write_text(base.gerar_descricao(rot), encoding="utf-8")
    res["descricao"] = str(desc)
    if not a.manter:
        shutil.rmtree(PUBLICO / "run" / rot["slug"], ignore_errors=True)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
