"""Monta um vídeo do canal Histórias da Bíblia (animação 2D desenhada por código).

Passos:
  1. narra cada cena com a voz do Gemini (a mesma função da Nexus: scripts/video_motion.narrar_gemini);
  2. usa a duração real de cada narração para montar a linha do tempo;
  3. desenha os quadros (animacao/cenas.html) no Chromium, quadro a quadro, a 30 fps;
  4. junta voz + trilha própria (scripts/trilha.py, estilo "cinema") e grava o MP4 1080x1920.

Uso:
  python3 canal-biblia/montar.py canal-biblia/roteiros/jose-do-egito.json --voz gemini:Orus --saida _biblia
  python3 canal-biblia/montar.py ... --sem-voz        (prévia muda, com tempos estimados)
  python3 canal-biblia/montar.py ... --quadros 2,8,15 (só salva alguns quadros em PNG, para conferir)
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "scripts"))
FPS = 30
PAUSA = 0.32          # respiro entre as cenas
FINAL = 1.6           # segura o versículo na tela no fim


def rodar(cmd):
    subprocess.run(cmd, check=True)


def duracao(arq):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(arq)]).decode().strip())


def narrar(rot, voz, pasta, sem_voz):
    """Uma narração por cena (entonação natural e tempo exato de cada cena)."""
    cenas = rot["cenas"]
    if sem_voz:
        for c in cenas:
            c["falaDur"] = max(1.6, len(c["fala"].split()) / 2.55)
        return None
    import video_motion as vm
    nome = voz.split(":", 1)[1] if ":" in voz else voz
    partes = []
    for i, c in enumerate(cenas):
        wav = pasta / f"voz{i:02d}.wav"
        vm.narrar_gemini(c["fala"], wav, nome, rot.get("estilo_voz"))
        norm = pasta / f"voz{i:02d}n.wav"
        # tira o silêncio das pontas e padroniza (48 kHz mono)
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af",
               "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
               "-ar", "48000", "-ac", "1", str(norm)])
        c["falaDur"] = duracao(norm)
        partes.append(norm)
        print(f"  cena {i + 1}: {c['falaDur']:.2f}s", flush=True)
    # junta tudo com as pausas
    lista = pasta / "lista.txt"
    silencio = pasta / "pausa.wav"
    final = pasta / "final.wav"
    rodar(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(PAUSA), str(silencio)])
    rodar(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", str(FINAL), str(final)])
    linhas = []
    for i, p in enumerate(partes):
        linhas.append(f"file '{p}'")
        linhas.append(f"file '{final if i == len(partes) - 1 else silencio}'")
    lista.write_text("\n".join(linhas))
    narracao = pasta / "narracao.wav"
    rodar(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lista), "-c", "copy", str(narracao)])
    return narracao


def linha_do_tempo(rot):
    t, cenas = 0.0, []
    for i, c in enumerate(rot["cenas"]):
        dur = c["falaDur"] + (FINAL if i == len(rot["cenas"]) - 1 else PAUSA)
        cenas.append({"id": c["id"], "fala": c["fala"], "falaDur": c["falaDur"], "start": t, "dur": dur,
                      "texto_tela": c.get("texto_tela", "")})
        t += dur
    return {"cenas": cenas, "total": t}


def desenhar(tl, destino_video, quadros=None):
    from playwright.sync_api import sync_playwright
    n = int(tl["total"] * FPS)
    with sync_playwright() as p:
        nav = p.chromium.launch(args=["--disable-gpu", "--force-color-profile=srgb"])
        pg = nav.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto((AQUI / "animacao" / "cenas.html").as_uri())
        pg.evaluate("tl => { window.TIMELINE = tl; }", tl)
        pg.evaluate("() => window.pronto")
        if quadros:
            for s in quadros:
                dados = pg.evaluate("t => quadroJpeg(t, 0.92)", s)
                Path(destino_video).mkdir(parents=True, exist_ok=True)
                (Path(destino_video) / f"quadro-{s:05.1f}.jpg").write_bytes(base64.b64decode(dados.split(",", 1)[1]))
            nav.close()
            return
        ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", str(destino_video)],
                              stdin=subprocess.PIPE)
        for i in range(n):
            dados = pg.evaluate("t => quadroJpeg(t, 0.93)", i / FPS)
            ff.stdin.write(base64.b64decode(dados.split(",", 1)[1]))
            if i % 150 == 0:
                print(f"  quadro {i}/{n}", flush=True)
        ff.stdin.close()
        ff.wait()
        nav.close()


def finalizar(video_mudo, narracao, total, slug, destino):
    trilha = Path(tempfile.gettempdir()) / f"trilha-{slug}.wav"
    try:
        import trilha as tr
        tr.gerar(str(trilha), total + 0.5, "cinema", slug)
    except Exception as e:
        print(f"(sem trilha: {e})", file=sys.stderr)
        trilha = None
    v = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p"]
    a = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(destino)]
    if narracao and trilha:
        # mesma mixagem da Nexus: trilha baixa que abaixa sozinha quando a voz fala
        filtro = ("[1:a]asplit=2[voz][chave];[2:a]aresample=48000,volume=0.20[m];"
                  "[m][chave]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[md];"
                  "[voz][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo), "-i", str(narracao), "-i", str(trilha),
               "-filter_complex", filtro, "-map", "0:v", "-map", "[a]"] + v + a)
    elif narracao:
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo), "-i", str(narracao), "-map", "0:v", "-map", "1:a",
               "-af", "loudnorm=I=-14:TP=-1.5:LRA=11"] + v + a)
    elif trilha:
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo), "-i", str(trilha), "-map", "0:v", "-map", "1:a",
               "-af", "volume=0.5"] + v + a)
    else:
        rodar(["ffmpeg", "-y", "-v", "error", "-i", str(video_mudo)] + v + [str(destino)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--voz", default="gemini:Orus")
    ap.add_argument("--saida", default="_biblia")
    ap.add_argument("--sem-voz", action="store_true")
    ap.add_argument("--quadros", default="")
    a = ap.parse_args()
    rot = json.loads(Path(a.roteiro).read_text(encoding="utf-8"))
    saida = Path(a.saida); saida.mkdir(parents=True, exist_ok=True)
    pasta = Path(tempfile.mkdtemp(prefix=f"biblia-{rot['slug']}-"))
    sem_voz = a.sem_voz or not os.environ.get("GEMINI_API_KEY")
    if sem_voz and not a.sem_voz:
        print("(GEMINI_API_KEY não definida: prévia sem narração)", file=sys.stderr)
    print(f"Narrando ({'estimado' if sem_voz else a.voz})...", flush=True)
    narracao = narrar(rot, a.voz, pasta, sem_voz)
    tl = linha_do_tempo(rot)
    print(f"Duração total: {tl['total']:.1f}s", flush=True)
    if a.quadros:
        desenhar(tl, saida, [float(x) for x in a.quadros.split(",")])
        return
    sufixo = "" if sem_voz else "-" + a.voz.split(":")[-1].lower()
    mudo = pasta / "mudo.mp4"
    print("Desenhando os quadros...", flush=True)
    desenhar(tl, mudo)
    destino = saida / f"{rot['slug']}{sufixo}.mp4"
    print("Juntando voz e trilha...", flush=True)
    finalizar(mudo, narracao, tl["total"], rot["slug"], destino)
    (saida / f"{rot['slug']}{sufixo}.json").write_text(json.dumps({"titulo": rot["titulo"], "descricao": rot["descricao"],
                                                                     "voz": None if sem_voz else a.voz, "linha_do_tempo": tl},
                                                                    ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Pronto: {destino} ({duracao(destino):.1f}s)")


if __name__ == "__main__":
    main()
