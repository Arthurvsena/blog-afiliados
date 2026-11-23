"""Monta um vídeo do canal Segura Aí 3D (animação 3D desenhada por código, three.js).

Passos:
  1. narra o roteiro com a voz do Gemini (scripts/video_motion.narrar_gemini, a mesma da Nexus),
     numa chamada só, e corta o áudio nas pausas entre as cenas;
  2. calcula o tempo de cada palavra (legenda palavra por palavra e gatilhos das etiquetas);
  3. desenha os quadros (animacao/motor3d.html) no Chromium, quadro a quadro, a 30 fps;
  4. junta voz + efeitos + trilha própria (segura-ai/sons.py), trilha baixinha, e grava o MP4 1080x1920.

Uso:
  python3 segura-ai/montar.py segura-ai/roteiros/trocar-lampada.json --voz gemini:Fenrir --saida _segura
  python3 segura-ai/montar.py ... --sem-voz --folha     (prévia: um quadro de cada cena, sem gastar voz)
  python3 segura-ai/montar.py ... --quadros 2,8,15      (só alguns quadros em JPG)
"""
import argparse
import base64
import functools
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(AQUI))
FPS = 30
PAUSA = 0.22        # respiro entre as cenas
REBOBINAR = 0.65    # tempo extra do efeito de fita rebobinando
FINAL = 1.2
VOLUME_TRILHA = 0.10
GL = ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
      "--force-color-profile=srgb"]


def rodar(cmd):
    subprocess.run(cmd, check=True)


def duracao(arq):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(arq)]).decode().strip())


APARA = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
         "silenceremove=start_periods=1:start_threshold=-45dB,areverse")


def silencios(arq, limiar="-38dB", minimo=0.18):
    saida = subprocess.run(["ffmpeg", "-v", "info", "-i", str(arq), "-af", f"silencedetect=n={limiar}:d={minimo}", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    ini, res = None, []
    for linha in saida.splitlines():
        if "silence_start:" in linha:
            ini = float(linha.split("silence_start:")[1].split()[0])
        elif "silence_end:" in linha and ini is not None:
            res.append((ini, float(linha.split("silence_end:")[1].split()[0])))
            ini = None
    return res


def cortes_por_silencio(total, falas, sil):
    pesos = [len(f) + 8 for f in falas]
    soma, acc, cortes, ultimo = sum(pesos), 0, [], 0.0
    medio = total / len(falas)
    for i in range(len(falas) - 1):
        acc += pesos[i]
        esperado = total * acc / soma
        meios = [(a + b) / 2 for a, b in sil if (a + b) / 2 > ultimo + 0.4]
        perto = min(meios, key=lambda m: abs(m - esperado), default=None)
        corte = perto if perto is not None and abs(perto - esperado) < medio * 0.5 else esperado
        cortes.append(corte)
        ultimo = corte
    return cortes


def narrar(rot, voz, pasta, sem_voz):
    cenas = rot["cenas"]
    if sem_voz:
        for c in cenas:
            c["falaDur"] = max(1.2, len(c["fala"].split()) / 2.9)
        return None
    import video_motion as vm
    nome = voz.split(":", 1)[1] if ":" in voz else voz
    bruto, inteiro = pasta / "voz-bruta.wav", pasta / "voz-inteira.wav"
    texto = "\n\n".join(c["fala"] for c in cenas)
    vm.narrar_gemini(texto, bruto, nome, (rot.get("estilo_voz") or "") + ", com uma pausa curta entre cada parágrafo")
    rodar(["ffmpeg", "-y", "-v", "error", "-i", str(bruto), "-af", APARA, "-ar", "48000", "-ac", "1", str(inteiro)])
    total = duracao(inteiro)
    cortes = cortes_por_silencio(total, [c["fala"] for c in cenas], silencios(inteiro))
    limites = [0.0] + cortes + [total]
    partes = []
    for i, c in enumerate(cenas):
        wav, norm = pasta / f"voz{i:02d}.wav", pasta / f"voz{i:02d}n.wav"
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(inteiro), "-ss", f"{limites[i]:.3f}", "-to", f"{limites[i + 1]:.3f}", str(wav)])
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af", APARA, "-ar", "48000", "-ac", "1", str(norm)])
        c["falaDur"] = duracao(norm)
        partes.append(norm)
        print(f"  cena {i + 1}: {c['falaDur']:.2f}s", flush=True)
    linhas = []
    for i, p in enumerate(partes):
        linhas.append(f"file '{p}'")
        extra = FINAL if i == len(partes) - 1 else PAUSA + (REBOBINAR if cenas[i].get("rebobinar") else 0)
        s = pasta / f"pausa{i:02d}.wav"
        rodar(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{extra:.3f}", str(s)])
        linhas.append(f"file '{s}'")
    lista = pasta / "lista.txt"
    lista.write_text("\n".join(linhas))
    narracao = pasta / "narracao.wav"
    rodar(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(narracao)])
    return narracao


def palavras(fala, inicio, dur):
    """Tempo de cada palavra, proporcional ao tamanho (a fala de cada cena já foi cortada certinha)."""
    ws = fala.split()
    pesos = [len(re.sub(r"\W", "", w)) + 2 for w in ws]
    soma, t, res = sum(pesos), inicio, []
    for w, p in zip(ws, pesos):
        d = dur * p / soma
        res.append({"w": w, "s": round(t, 3), "e": round(t + d, 3)})
        t += d
    return res


def linha_do_tempo(rot):
    t, cenas = 0.0, []
    n = len(rot["cenas"])
    for i, c in enumerate(rot["cenas"]):
        dur = c["falaDur"] + (FINAL if i == n - 1 else PAUSA + (REBOBINAR if c.get("rebobinar") else 0))
        cena = dict(c)
        cena.update({"start": round(t, 3), "dur": round(dur, 3), "palavras": palavras(c["fala"], t, c["falaDur"])})
        cenas.append(cena)
        t += dur
    return {"cenas": cenas, "total": round(t, 3), "placar_nome": rot.get("placar_nome", "PERIGO"), "rebobinar": REBOBINAR}


def _norm(s):
    s = unicodedata.normalize("NFD", (s or "").lower())
    return re.sub(r"[^a-z0-9]", "", "".join(ch for ch in s if unicodedata.category(ch) != "Mn"))


def palavra_t(c, alvo, padrao=0.5):
    if alvo is None or alvo == "":
        return c["start"] + c["falaDur"] * padrao
    if isinstance(alvo, (int, float)):
        return c["start"] + c["falaDur"] * alvo
    k = _norm(alvo)
    for w in c["palavras"]:
        if _norm(w["w"]).startswith(k):
            return w["s"]
    for w in c["palavras"]:
        if k in _norm(w["w"]):
            return w["s"]
    return c["start"] + c["falaDur"] * padrao


def eventos_sonoros(tl):
    ev, sil = [], []
    for c in tl["cenas"]:
        fim = c["start"] + c["dur"]
        if c.get("tag"):
            ev.append(("pop", c["start"] + 0.05, 0.7))
        for e in c.get("etiquetas") or []:
            tipo = e.get("tipo", "info")
            ev.append(({"ok": "ok", "erro": "erro"}.get(tipo, "pop"), palavra_t(c, e.get("em"), 0.1), 0.8))
        if c.get("placar"):
            t0 = palavra_t(c, c["placar"].get("em"), 0.5)
            ev += [("whoosh", t0 - 0.1, 0.8), ("plim", t0 + 0.15)]
        p = c.get("personagem") or {}
        acao = p.get("acao")
        tk = palavra_t(c, p.get("momento"), 0.45)
        if acao in ("cair", "escorregar"):
            ev.append(("rangido", tk - 1.0, 1.4))
            if any(o.get("tipo") == "cadeira_plastico" for o in c.get("objetos") or []):
                ev.append(("quebra", tk))
            ev += [("whoosh", tk + 0.1, 0.6), ("queda", tk + 0.55)]
        if acao == "choque":
            ev.append(("choque", tk))
        if c.get("rebobinar"):
            ev.append(("rebobinar", fim - REBOBINAR, 0.9))
            sil.append((fim - REBOBINAR, fim))
        if "confete" in (c.get("efeitos") or []):
            ev.append(("fanfarra", palavra_t(c, c.get("confete_em"), 0.15)))
        if c.get("chamada"):
            ev.append(("plim", c["start"] + 0.3))
    return ev, sil


class _Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def servidor():
    """O motor usa módulos JS (three.js): precisa de http://, não file://."""
    h = functools.partial(_Silencioso, directory=str(AQUI / "animacao"))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/motor3d.html"


def desenhar(tl, destino_video, quadros=None):
    from playwright.sync_api import sync_playwright
    n = int(tl["total"] * FPS)
    srv, url = servidor()
    with sync_playwright() as p:
        nav = p.chromium.launch(args=GL)
        pg = nav.new_page(viewport={"width": 1080, "height": 1920})
        pg.on("pageerror", lambda e: print("[motor] erro:", e, file=sys.stderr))
        pg.goto(url)
        pg.wait_for_function("window.pronto === true", timeout=120000)
        pg.evaluate("tl => { window.TIMELINE = tl; }", tl)
        if quadros:
            Path(destino_video).mkdir(parents=True, exist_ok=True)
            for s in quadros:
                dados = pg.evaluate("t => quadroJpeg(t, 0.92)", s)
                (Path(destino_video) / f"quadro-{s:06.2f}.jpg").write_bytes(base64.b64decode(dados.split(",", 1)[1]))
            nav.close(); srv.shutdown()
            return
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", str(destino_video)],
                              stdin=subprocess.PIPE)
        for i in range(n):
            dados = pg.evaluate("t => quadroJpeg(t, 0.92)", i / FPS)
            ff.stdin.write(base64.b64decode(dados.split(",", 1)[1]))
            if i % 300 == 0:
                print(f"  quadro {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait()
        nav.close(); srv.shutdown()


def finalizar(video_mudo, narracao, tl, slug, destino, pasta):
    import sons
    efeitos, trilha = pasta / "efeitos.wav", pasta / "trilha.wav"
    ev, sil = eventos_sonoros(tl)
    sons.gerar(ev, tl["total"], efeitos, trilha, semente=sum(map(ord, slug)), silencios=sil)
    v = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p"]
    a = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(destino)]
    if narracao:
        filtro = (f"[1:a]aresample=48000,asplit=2[voz][chave];[3:a]aresample=48000,volume={VOLUME_TRILHA}[m];"
                  "[m][chave]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[md];"
                  "[2:a]aresample=48000,volume=0.8[fx];"
                  "[voz][fx][md]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo), "-i", str(narracao), "-i", str(efeitos), "-i", str(trilha),
               "-filter_complex", filtro, "-map", "0:v", "-map", "[a]"] + v + a)
    else:
        filtro = f"[1:a]volume=0.8[fx];[2:a]volume={VOLUME_TRILHA * 2}[m];[fx][m]amix=inputs=2:normalize=0[a]"
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo), "-i", str(efeitos), "-i", str(trilha),
               "-filter_complex", filtro, "-map", "0:v", "-map", "[a]"] + v + a)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--voz", default="gemini:Fenrir")
    ap.add_argument("--saida", default="_segura")
    ap.add_argument("--sem-voz", action="store_true")
    ap.add_argument("--quadros", default="")
    ap.add_argument("--folha", action="store_true", help="uma imagem com 2 quadros de cada cena (conferir antes de gastar voz)")
    a = ap.parse_args()
    rot = json.loads(Path(a.roteiro).read_text(encoding="utf-8"))
    saida = Path(a.saida); saida.mkdir(parents=True, exist_ok=True)
    pasta = Path(tempfile.mkdtemp(prefix=f"segura-{rot['slug']}-"))
    sem_voz = a.sem_voz or a.folha or not os.environ.get("GEMINI_API_KEY")
    if sem_voz and not (a.sem_voz or a.folha):
        print("(GEMINI_API_KEY não definida: prévia sem narração)", file=sys.stderr)
    print(f"Narrando ({'estimado' if sem_voz else a.voz})...", flush=True)
    narracao = narrar(rot, a.voz, pasta, sem_voz)
    tl = linha_do_tempo(rot)
    print(f"Duração total: {tl['total']:.1f}s", flush=True)
    if a.folha:
        tempos = []
        for c in tl["cenas"]:
            tempos += [c["start"] + c["dur"] * 0.25, c["start"] + c["dur"] * 0.8]
        tmp = Path(tempfile.mkdtemp())
        desenhar(tl, tmp, tempos)
        destino = saida / f"{rot['slug']}-folha.jpg"
        col = min(8, len(tempos))
        rodar(["ffmpeg", "-y", "-v", "error", "-pattern_type", "glob", "-i", str(tmp / "quadro-*.jpg"),
               "-vf", f"scale=216:384,tile={col}x{(len(tempos) + col - 1) // col}:padding=4", "-frames:v", "1", str(destino)])
        print(f"Folha: {destino}")
        return
    if a.quadros:
        desenhar(tl, saida, [float(x) for x in a.quadros.split(",")])
        return
    sufixo = "" if sem_voz else "-" + a.voz.split(":")[-1].lower()
    mudo = pasta / "mudo.mp4"
    print("Desenhando os quadros...", flush=True)
    desenhar(tl, mudo)
    destino = saida / f"{rot['slug']}{sufixo}.mp4"
    print("Juntando voz, efeitos e trilha...", flush=True)
    finalizar(mudo, narracao, tl, rot["slug"], destino, pasta)
    (saida / f"{rot['slug']}{sufixo}.json").write_text(json.dumps({"titulo": rot["titulo"], "descricao": rot.get("descricao", ""),
                                                                     "voz": None if sem_voz else a.voz, "linha_do_tempo": tl},
                                                                    ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Pronto: {destino} ({duracao(destino):.1f}s)")


if __name__ == "__main__":
    main()
