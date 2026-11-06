"""Vídeos com motion (Remotion) para o canal Nexus Tech.

Mesmo roteiro de scripts/video.py, com campos extras por cena:
  "tipo": "gancho" | "fato" | "numero" | "produto" | "cta"   (padrão: fato; 1ª cena = gancho; última = cta)
  "imagens": ["content/imagens/x.jpg", "produto:ID", "url:https://...jpg|Divulgação/Apple", "busca:termos"]
  "icone": "chip" | "calendario" | ...  (cena info: ícone animado no lugar da foto)
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


VOZ_PADRAO = "kokoro:pm_alex"
VELOCIDADE = 1.12
VELOCIDADE_GOOGLE = 1.1
KOKORO_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"


def pronunciar(texto):
    """Troca nomes em inglês pela grafia que a voz grátis lê com sotaque brasileiro (data/videos/pronuncia.json)."""
    arq = RAIZ / "data" / "videos" / "pronuncia.json"
    if not arq.exists():
        return texto
    dic = {k: v for k, v in json.loads(arq.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    for k in sorted(dic, key=len, reverse=True):
        texto = re.sub(r"(?<![\w-])" + re.escape(k) + r"(?![\w-])", dic[k], texto, flags=re.I)
    return texto


def sintetizador(voz):
    """'google:Charon' (Google Chirp 3 HD pt-BR, precisa de GOOGLE_TTS_KEY; outras: Puck, Fenrir, Orus, Kore, Aoede...),
    'kokoro:pm_alex' | 'kokoro:pm_santa' | 'kokoro:pf_dora' ou 'piper:cadu' | 'piper:jeff' (grátis, sem chave)."""
    motor, nome = (voz.split(":", 1) + [""])[:2]
    if motor == "google":
        chave = os.environ.get("GOOGLE_TTS_KEY")
        if not chave:
            print("(GOOGLE_TTS_KEY não definida: usando a voz grátis Kokoro)", file=sys.stderr)
            return sintetizador("kokoro:pm_alex")
        import base64

        def falar(texto, destino):
            corpo = json.dumps({"input": {"text": texto},
                                "voice": {"languageCode": "pt-BR", "name": f"pt-BR-Chirp3-HD-{nome or 'Charon'}"},
                                "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000,
                                                "speakingRate": VELOCIDADE_GOOGLE}}).encode()
            req = urllib.request.Request("https://texttospeech.googleapis.com/v1/text:synthesize",
                                         data=corpo, headers={"Content-Type": "application/json", "X-Goog-Api-Key": chave})
            resp = json.loads(urllib.request.urlopen(req, timeout=60).read())
            Path(destino).write_bytes(base64.b64decode(resp["audioContent"]))
        return falar
    cache = Path.home() / ".cache" / "nexus-vozes"
    cache.mkdir(parents=True, exist_ok=True)
    if motor == "kokoro":
        for arq in ("kokoro-v1.0.onnx", "voices-v1.0.bin"):
            if not (cache / arq).exists():
                (cache / arq).write_bytes(pegar(KOKORO_URL + arq))
        import soundfile as sf
        from kokoro_onnx import Kokoro
        k = Kokoro(str(cache / "kokoro-v1.0.onnx"), str(cache / "voices-v1.0.bin"))

        def falar(texto, destino):
            som, taxa = k.create(pronunciar(texto), voice=nome or "pm_alex", speed=VELOCIDADE, lang="pt-br")
            sf.write(str(destino), som, taxa, subtype="PCM_16")
        return falar
    # piper
    nome = nome or "cadu"
    modelo = cache / f"pt_BR-{nome}-medium.onnx"
    for ext in (".onnx", ".onnx.json"):
        arq = cache / f"pt_BR-{nome}-medium{ext}"
        if not arq.exists():
            arq.write_bytes(pegar(f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR/{nome}/medium/pt_BR-{nome}-medium{ext}"))
    from piper import PiperVoice, SynthesisConfig
    v = PiperVoice.load(str(modelo))
    cfg = SynthesisConfig(length_scale=0.9)

    def falar(texto, destino):
        with wave.open(str(destino), "wb") as wf:
            v.synthesize_wav(pronunciar(texto), wf, syn_config=cfg)
    return falar


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
                elif ref.startswith("url:"):
                    url, _, cred = ref[4:].partition("|")
                    salvar_img(Image.open(io.BytesIO(pegar(url.strip()))), destino)
                    item = {"src": f"run/{pasta.name}/{nome}", "produto": False}
                    creditos.append(cred.strip() or "Divulgação")
                elif ref.startswith(("video:", "tela:", "estoque:")):
                    # trecho de VÍDEO: oficial (trailer/b-roll do fabricante ou do jogo), gravação de tela nossa
                    # ou banco gratuito (Pexels). Nunca vídeo de outro canal/emissora (editorial/manual_youtube.md).
                    import midia
                    nome = f"c{i:02d}-{j}.mp4"
                    destino = pasta / nome
                    tipo_ref, _, resto = ref.partition(":")
                    partes = [x.strip() for x in resto.split("|")]
                    alvo, cred = partes[0], (partes[1] if len(partes) > 1 else "")
                    inicio = float(partes[2]) if len(partes) > 2 and partes[2] else 0.0
                    if tipo_ref == "video":
                        midia.recortar_video(alvo, destino, inicio, 12, vertical=rot.get("tipo", "short") == "short")
                    elif tipo_ref == "tela":
                        midia.gravar_tela(alvo, destino, segundos=12, vertical=rot.get("tipo", "short") == "short")
                        cred = cred or "Gravação de tela: Nexus Tech"
                    else:
                        cred = midia.estoque_video(alvo, destino, vertical=rot.get("tipo", "short") == "short") or cred
                    prop = midia.proporcao(destino)
                    item = {"src": f"run/{pasta.name}/{nome}", "produto": False, "video": True, "prop": prop,
                            "credito": cred}
                    if cred:
                        creditos.append(cred)
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


def preparar_manchetes(rot, pasta, creditos, vertical):
    """Cenas 'manchete': print da matéria com o trecho destacado (scripts/midia.py)."""
    import midia
    for i, c in enumerate(rot["cenas"]):
        if c.get("tipo") != "manchete":
            continue
        m = c.get("manchete") or {}
        try:
            meta = midia.capturar_manchete(m["url"], m.get("trecho", ""), pasta / f"manchete{i:02d}.png", vertical)
            c["_manchete"] = {"src": f"run/{pasta.name}/{meta['arquivo']}", "proporcao": meta["proporcao"],
                              "destaque": meta["destaque"], "site": meta["site"]}
            creditos.append(f"Reprodução: {meta['site']}")
        except BaseException as e:  # sem print: a cena vira um fato comum
            print(f"(manchete {m.get('url')} falhou: {e})", file=sys.stderr)
            c["tipo"] = "citacao" if m.get("trecho") else "fato"
            c.setdefault("tela", m.get("trecho") or c["fala"])
            c.setdefault("autor", m.get("site", ""))


ENTRADAS = ["zoom", "slide", "subida", "glitch", "cortina", "giro", "desfoque"]


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
    """Blocos de legenda de leitura natural: quebra na pontuação ou perto de ~18 letras,
    nunca terminando num artigo/preposição solto ("o", "no", "de")."""
    soltas = {"o", "a", "os", "as", "um", "uma", "no", "na", "nos", "nas", "de", "do", "da", "dos", "das",
              "e", "em", "que", "uns", "umas", "pra", "para", "com", "por", "ao", "à", "se", "seu", "sua", "mais"}
    lista = tokens(fala)
    saida, atual = [], []
    for i, tk in enumerate(lista):
        atual.append(tk)
        letras = sum(len(f) for _, f in atual)
        ultima = re.sub(r"\W", "", tk[1].lower())
        pontuou = re.search(r"[.,:;!?]$", tk[1])
        cheio = len(atual) >= n + 1 or letras >= 18
        if (pontuou and len(atual) >= 2) or (cheio and ultima not in soltas) or len(atual) >= n + 3:
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


# Os 3 quadros fixos do canal (editorial/manual_youtube.md)
QUADROS = {
    "60s": {"nome": "Nexus em 60s", "trilha": "pulso", "legenda": "palavra",
            "estilo": "apresentador brasileiro de um canal dark de tecnologia, sotaque do Brasil (paulista), ritmo rápido de Shorts "
                      "(cerca de 175 palavras por minuto), direto, seguro, com humor seco e leve ironia no comentário final, "
                      "pronunciando nomes em inglês do jeito que os brasileiros falam"},
    "historias": {"nome": "Histórias Tech", "trilha": "cinema", "legenda": "frase",
                  "estilo": "narrador brasileiro de documentário, sotaque do Brasil, voz grave, calma e cinematográfica, ritmo pausado "
                            "(cerca de 145 palavras por minuto), com pausas dramáticas nas viradas da história, "
                            "pronunciando nomes em inglês do jeito que os brasileiros falam"},
    "tutorial": {"nome": "Nexus Ensina", "trilha": "ambiente", "legenda": "palavra", "vinheta": True,
                 "estilo": "professor brasileiro de tecnologia explicando um passo a passo para quem não entende do assunto, "
                           "sotaque do Brasil (paulista), calmo, claro e simpático, ritmo de cerca de 150 palavras por minuto, "
                           "pausas curtas entre os passos, pronunciando nomes em inglês do jeito que os brasileiros falam"},
    "lafora": {"nome": "Lá Fora, Aqui", "trilha": "ambiente", "legenda": "palavra", "vinheta": True,
               "estilo": "apresentador brasileiro de um canal de tecnologia que explica novidades de fora para o público do Brasil, "
                         "sotaque do Brasil (paulista), tom de conversa natural e curioso, ritmo de cerca de 155 palavras por minuto, "
                         "pronunciando nomes em inglês do jeito que os brasileiros falam"},
}
ESTILO_PADRAO = ("apresentador brasileiro de um canal de tecnologia no YouTube, sotaque do Brasil (paulista), "
                 "ritmo rápido de Shorts, animado e natural, pronunciando nomes em inglês do jeito que os brasileiros falam")


def narrar_gemini(texto, destino, voz="Charon", estilo=None):
    """Voz do Gemini (Google AI Studio, cota grátis, sem cartão). Uma chamada por vídeo. Precisa de GEMINI_API_KEY."""
    import base64
    corpo = json.dumps({
        "model": os.environ.get("GEMINI_TTS_MODELO", "gemini-3.8-flash-tts"),
        "input": [{"type": "user_input", "content": [{"type": "text", "text": texto, "annotations": [{
            "type": "speech_metadata",
            "style": estilo or ESTILO_PADRAO}]}]}],
        "response_format": {"type": "audio"},
        "generation_config": {"speech_config": [{"voice": voz}]},
    }).encode()
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions", data=corpo,
                                 headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    import time
    for tentativa in range(4):
        try:
            resp = json.loads(urllib.request.urlopen(req, timeout=180).read())
            break
        except urllib.error.HTTPError as e:
            if e.code != 429 or tentativa == 3:
                raise
            time.sleep(35 * (tentativa + 1))  # cota por minuto do plano grátis
    audios = [c for st in resp.get("steps", []) if st.get("type") == "model_output"
              for c in st.get("content", []) if c.get("type") == "audio"]
    if not audios:
        raise RuntimeError(f"Gemini não devolveu áudio: {str(resp)[:300]}")
    Path(destino).write_bytes(base64.b64decode(audios[-1]["data"]))


def escolher_voz_ab():
    """Teste A/B de vozes: escolhe a voz mais atrasada em relação ao peso em data/videos/vozes.json."""
    arq, uso_arq = RAIZ / "data" / "videos" / "vozes.json", RAIZ / "data" / "videos" / "uso_vozes.json"
    if not arq.exists():
        return None
    pesos = json.loads(arq.read_text(encoding="utf-8")).get("vozes") or {}
    pesos = {k: float(v) for k, v in pesos.items() if float(v) > 0}
    if not pesos:
        return None
    uso = json.loads(uso_arq.read_text(encoding="utf-8")) if uso_arq.exists() else {"videos": []}
    contagem = {k: 0 for k in pesos}
    for u in uso.get("videos", []):
        if u.get("voz") in contagem:
            contagem[u["voz"]] += 1
    total = sum(contagem.values()) + 1
    soma = sum(pesos.values())
    return max(pesos, key=lambda k: pesos[k] / soma - contagem[k] / total)


def registrar_voz(slug, voz):
    uso_arq = RAIZ / "data" / "videos" / "uso_vozes.json"
    uso = json.loads(uso_arq.read_text(encoding="utf-8")) if uso_arq.exists() else {"videos": []}
    uso["videos"] = [u for u in uso["videos"] if u.get("slug") != slug] + [{"slug": slug, "voz": voz}]
    uso_arq.write_text(json.dumps(uso, ensure_ascii=False, indent=1), encoding="utf-8")


def voz_config():
    try:
        import yaml
        return (yaml.safe_load((RAIZ / "config.yaml").read_text(encoding="utf-8")).get("video") or {}).get("voz") or VOZ_PADRAO
    except Exception:
        return VOZ_PADRAO


def finalizar(origem, destino, trilha=None):
    """Grava num arquivo temporário e só renomeia no fim: um vídeo interrompido nunca vira um .mp4 quebrado."""
    destino = Path(destino)
    parcial = destino.with_name(destino.stem + ".parcial.mp4")
    _finalizar(origem, parcial, trilha)
    os.replace(parcial, destino)


def _finalizar(origem, destino, trilha=None):
    """Versão final em ALTA qualidade para o YouTube (sem limite de tamanho): H.264 CRF 18,
    áudio AAC 192 kbps com volume padronizado. O envio é feito pelo seletor de arquivos do
    Windows (veja a skill canal-diario), então não precisa caber em 10 MB."""
    video = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", "60", "-bf", "2"]
    audio = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(destino)]
    if trilha:
        # trilha ~22 dB abaixo da voz e "abaixando" sozinha quando a voz fala (sidechain)
        filtro = ("[0:a]asplit=2[voz][chave];[1:a]aresample=48000,volume=0.16[m];"
                  "[m][chave]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=350[md];"
                  "[voz][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(origem), "-i", str(trilha), "-filter_complex", filtro,
                    "-map", "0:v", "-map", "[a]"] + video + audio)
    else:
        base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(origem)] + video +
                   ["-af", "loudnorm=I=-14:TP=-1.5:LRA=11"] + audio)


def comprimir(origem, destino, segundos, tipo="short", alvo_mb=9.2):
    """Comprime para ficar abaixo de alvo_mb (2 passadas). Também serve para vídeos já prontos."""
    kbps_a = 96 if tipo == "short" else 64
    for tentativa in range(3):
        v = int(alvo_mb * (0.93 ** tentativa) * 8192 / max(segundos, 1)) - kbps_a
        v = max(220, min(v, 6000 if tipo == "short" else 3000))
        log = Path("/tmp") / f"x264-{Path(destino).stem}"
        base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(origem), "-c:v", "libx264", "-preset", "slow", "-b:v", f"{v}k",
                    "-pass", "1", "-passlogfile", str(log), "-an", "-f", "null", "/dev/null"])
        base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(origem), "-c:v", "libx264", "-preset", "slow", "-b:v", f"{v}k",
                    "-pass", "2", "-passlogfile", str(log), "-pix_fmt", "yuv420p",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", f"{kbps_a}k",
                    "-movflags", "+faststart", str(destino)])
        if Path(destino).stat().st_size <= 9.5 * 1024 * 1024:
            return
    raise SystemExit(f"Não consegui deixar {destino} abaixo de 9,5 MB.")


def montar(rot, audio_externo=None, saida=None, voz_escolhida=None):
    voz_escolhida = voz_escolhida or escolher_voz_ab() or voz_config()
    if voz_escolhida.startswith("google") and not os.environ.get("GOOGLE_TTS_KEY"):
        voz_escolhida = "gemini:Charon" if os.environ.get("GEMINI_API_KEY") else VOZ_PADRAO
    if voz_escolhida.startswith("gemini") and not audio_externo:
        if not os.environ.get("GEMINI_API_KEY"):
            voz_escolhida = VOZ_PADRAO
        else:
            try:
                arq = Path("/tmp") / f"gemini-{rot['slug']}.wav"
                texto = "\n\n".join(falado(c["fala"]) for c in rot["cenas"] if c.get("fala"))
                narrar_gemini(texto, arq, voz_escolhida.split(":", 1)[1] if ":" in voz_escolhida else "Charon",
                              QUADROS.get(rot.get("quadro"), {}).get("estilo"))
                audio_externo = str(arq)
            except Exception as e:
                print(f"(Gemini falhou: {e}; usando a voz grátis)", file=sys.stderr)
                voz_escolhida = VOZ_PADRAO
    tipo = rot.get("tipo", "short")
    quadro = QUADROS.get(rot.get("quadro"), {})
    n_passo = 0
    for c in rot["cenas"]:
        if c.get("tipo") == "passo":
            n_passo += 1
            c.setdefault("numero_passo", n_passo)
    if quadro:
        rot["selo"] = quadro["nome"] + (f" #{rot['numero']}" if rot.get("numero") else "")
    fps = 30
    largura, altura = (1080, 1920) if tipo == "short" else (1920, 1080)
    cenas = [c for c in rot["cenas"] if c.get("fala")]
    rot["cenas"] = cenas
    with open(RAIZ / "data" / "produtos.csv", encoding="utf-8") as f:
        catalogo = {p["id"]: p for p in csv.DictReader(f)}
    pasta = PUBLICO / "run" / rot["slug"]
    shutil.rmtree(pasta, ignore_errors=True)
    pasta.mkdir(parents=True)
    creditos = []
    preparar_imagens(rot, pasta, catalogo, creditos)
    preparar_manchetes(rot, pasta, creditos, tipo == "short")
    for c in cenas:  # proporção de cada foto (o vídeo em pé mostra foto deitada inteira, sem cortar)
        for x in c.get("_imagens", []):
            if x.get("video"):
                continue
            try:
                with Image.open(PUBLICO / x["src"]) as im:
                    x["prop"] = round(im.width / im.height, 3)
            except Exception:
                pass
    sfx(PUBLICO / "sfx")

    # narração por trechos
    folga = 0.18
    n_leg = 9 if quadro.get("legenda") == "frase" else (4 if tipo == "short" else 6)
    trechos_por_cena = [grupos_de(c["fala"], n_leg) for c in cenas]
    if audio_externo:
        total = base.duracao(audio_externo)
        txt = lambda g: " ".join(f for _, f in g)
        soma = sum(len(txt(g)) for gs in trechos_por_cena for g in gs)
        tempos_trechos = [[total * len(txt(g)) / soma for g in gs] for gs in trechos_por_cena]
        audio = pasta / ("narracao" + Path(audio_externo).suffix)
        shutil.copy(audio_externo, audio)
        voz = voz_escolhida if voz_escolhida.startswith("gemini") else "elevenlabs"
    else:
        falar = sintetizador(voz_escolhida)
        wavs, tempos_trechos = [], []
        for ci, gs in enumerate(trechos_por_cena):
            # uma síntese por cena (entonação natural); o tempo de cada trecho sai do tamanho do texto
            arq = pasta / f"c{ci:02d}.wav"
            falar(" ".join(f for g in gs for _, f in g), arq)
            with wave.open(str(arq)) as w:
                d = w.getnframes() / w.getframerate()
            pausa = 0.28
            wavs.append((arq, pausa))
            tam = [len(" ".join(f for _, f in g)) + 3 for g in gs]
            tempos_trechos.append([d * x / sum(tam) for x in tam[:-1]] + [d * tam[-1] / sum(tam) + pausa])
        with wave.open(str(wavs[0][0])) as w:
            taxa, can, lg = w.getframerate(), w.getnchannels(), w.getsampwidth()
        audio = pasta / "narracao.wav"
        with wave.open(str(audio), "wb") as out:
            out.setnchannels(can); out.setsampwidth(lg); out.setframerate(taxa)
            for arq, pausa in wavs:
                with wave.open(str(arq)) as w:
                    out.writeframes(w.readframes(w.getnframes()))
                out.writeframes(b"\0" * int(taxa * pausa) * lg * can)
        voz = voz_escolhida

    # cenas em quadros
    props_cenas, sons, t = [], [], 0.0
    n = len(cenas)
    for ci, (c, gs, tt) in enumerate(zip(cenas, trechos_por_cena, tempos_trechos)):
        ini = round(t * fps)
        palavras, tg = [], t
        for gi, (g, dg) in enumerate(zip(gs, tt)):
            fala_d = dg - (0.28 if (gi == len(gs) - 1 and not audio_externo) else 0)
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
                "rotulo": c.get("rotulo", ""), "icone": c.get("icone", ""), "itens": c.get("itens", []),
                "titulo_lista": c.get("titulo_lista", ""), "autor": c.get("autor", ""), "layout": c.get("layout", ""),
                "entrada": c.get("entrada") or ENTRADAS[(ci * 3) % len(ENTRADAS)], "manchete": c.get("_manchete"), "capitulo": c.get("capitulo", ""), "fonte": c.get("fonte", ""), "numero_passo": c.get("numero_passo"), "imagens": c.get("_imagens", []), "palavras": palavras}
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
    # vinheta curta (2,5 s) DEPOIS do gancho, nunca no início: abre um silêncio na narração e empurra o resto
    vinheta = None
    if quadro.get("vinheta") and len(props_cenas) > 2:
        V = 75
        corte = props_cenas[1]["ini"]
        audio_v = pasta / ("narracao-v" + audio.suffix)
        base.rodar(["ffmpeg", "-y", "-v", "error", "-i", str(audio), "-filter_complex",
                    f"[0:a]atrim=0:{corte / fps:.3f},asetpts=PTS-STARTPTS[a];[0:a]atrim={corte / fps:.3f},asetpts=PTS-STARTPTS[b];"
                    f"anullsrc=r=44100:cl=mono,atrim=0:{V / fps:.3f}[s];[a]aresample=44100,aformat=channel_layouts=mono[a2];"
                    f"[b]aresample=44100,aformat=channel_layouts=mono[b2];[a2][s][b2]concat=n=3:v=0:a=1[o]",
                    "-map", "[o]", str(audio_v)])
        audio = audio_v
        for c in props_cenas[1:]:
            c["ini"] += V
            for w in c["palavras"]:
                w["ini"] += V; w["fim"] += V
        for q in sons:
            if q["ini"] >= corte - 6:
                q["ini"] += V
        sons.append({"ini": corte, "src": "sfx/whoosh.wav", "vol": 0.3})
        vinheta = {"ini": corte, "dur": V, "titulo": quadro["nome"]}
        duracao += V
    # cenas gráficas ganham de fundo a foto mais próxima, desfocada (contexto visual sem repetir a mesma tela)
    fotos = [(i, x["src"]) for i, c in enumerate(props_cenas) for x in c["imagens"] if not x.get("produto") and not x.get("video")]
    graficas = {"info", "data", "comparativo", "manchete", "lista", "barras", "linha", "citacao"}
    for i, c in enumerate(props_cenas):
        if c["tipo"] in graficas and c["imagens"] and not c["imagens"][0].get("produto") and not c["imagens"][0].get("video"):
            c["fundo"] = c["imagens"][0]["src"]  # cena gráfica com foto própria: a foto vira o fundo desfocado
        elif not c["imagens"] and fotos:
            c["fundo"] = min(fotos, key=lambda q: (abs(q[0] - i), q[0]))[1]
    # pedido de inscrição animado: no fim (Short) e também a ~30% do vídeo (longo)
    inscrever = []
    cta = next((c for c in props_cenas if c["tipo"] == "cta"), props_cenas[-1])
    inscrever.append({"ini": cta["ini"] + 6})
    if tipo == "longo":
        meio = next((c for c in props_cenas if c["ini"] > duracao * 0.3), None)
        if meio:
            inscrever.insert(0, {"ini": meio["ini"] + 10})
    for q in inscrever:
        sons.append({"ini": q["ini"] + 32, "src": "sfx/ding.wav", "vol": 0.2})
    props = {"tipo": tipo, "fps": fps, "largura": largura, "altura": altura, "duracao": duracao, "selo": rot.get("selo", ""),
             "audio": f"run/{rot['slug']}/{audio.name}", "cenas": props_cenas, "sons": sons, "inscrever": inscrever,
             "vinheta": vinheta, "legenda": quadro.get("legenda", "palavra")}
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

    # versão final em alta qualidade (o envio pelo Chrome vai em partes de 9 MB)
    saida = Path(saida or RAIZ / "_videos")
    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / f"{rot['slug']}.mp4"
    total = duracao / fps
    trilha = None
    try:
        import trilha as gerador_trilha
        cortes = [c["ini"] / fps for c in props_cenas if c.get("capitulo")][1:] if tipo == "longo" else []
        trilha = gerador_trilha.gerar(pasta / "trilha.wav", duracao / fps + 1, quadro.get("trilha", "pulso" if tipo == "short" else "ambiente"),
                                      rot["slug"], cortes)
    except Exception as e:
        print(f"(trilha não gerada: {e})", file=sys.stderr)
    finalizar(bruto, destino, trilha)

    capa = None
    if tipo == "longo":
        # 2 miniaturas (A e B) para o "Testar e comparar" do YouTube Studio
        fotos_capa = [x for c in props_cenas for x in c["imagens"] if not x.get("produto") and not x.get("video")]
        idx = int(rot.get("capa_cena", -1))
        escolhida = (props_cenas[idx]["imagens"][0] if 0 <= idx < len(props_cenas) and props_cenas[idx]["imagens"] else None) \
            or (max(fotos_capa, key=lambda x: x.get("prop", 1)) if fotos_capa else None) \
            or next((x for c in props_cenas for x in c["imagens"] if not x.get("video")), None)
        if escolhida:
            import capa as gerador_capa
            capa, _ = gerador_capa.gerar(PUBLICO / escolhida["src"], saida / rot["slug"], rot.get("capa_texto") or rot["titulo"],
                                         quadro.get("nome", ""), rot.get("capa_texto_b"))
    rot["creditos_extra"] = creditos
    # capítulos da descrição com os tempos REAIS da narração (a estimativa do roteiro erra e o YouTube
    # ignora capítulos que passam do fim do vídeo); precisa começar em 0:00 e ter blocos de 10 s ou mais
    caps = [(c["ini"] / fps, c["capitulo"]) for c in props_cenas if c.get("capitulo")]
    if tipo == "longo" and caps:
        if caps[0][0] > 1:
            caps.insert(0, (0, "Introdução"))
        lista = []
        for seg, nome in caps:
            seg = 0 if not lista else int(seg)
            if lista and seg - lista[-1][0] < 10:
                continue
            lista.append((seg, nome))
        rot["capitulos_desc"] = [f"{s // 60}:{s % 60:02d} {n}" for s, n in lista]
    if not rot["slug"].startswith("amostra"):
        registrar_voz(rot["slug"], voz)
    return {"arquivo": str(destino), "mb": round(destino.stat().st_size / 1024 / 1024, 2), "segundos": round(total, 1),
            "voz": voz, "capa": str(capa) if capa else None, "creditos": creditos}


def checar(rot):
    """Regras mínimas de qualidade do roteiro, por quadro (editorial/manual_youtube.md). Devolve 0 se passou."""
    cenas = rot.get("cenas") or []
    tipos = [c.get("tipo", "fato") for c in cenas]
    fotos = {str(r) for c in cenas for r in (c.get("imagens") or []) if r}
    problemas = []
    q = rot.get("quadro")
    if q not in QUADROS:
        problemas.append(f"campo 'quadro' ausente ou inválido ({q!r}): use 60s, historias, lafora ou tutorial")
    longo = rot.get("tipo") == "longo"
    if (q in ("lafora", "tutorial")) != longo and q in QUADROS:
        problemas.append("'lafora' e 'tutorial' são sempre vídeo longo; '60s' e 'historias' são sempre Shorts")
    clipes = {str(r) for c in cenas for r in (c.get("imagens") or []) if str(r).startswith(("video:", "tela:", "estoque:"))}
    minimo_clipes = 4 if longo else 1
    if len(clipes) < minimo_clipes:
        problemas.append(f"só {len(clipes)} trecho(s) de vídeo (mínimo {minimo_clipes}): use 'video:' (trailer/b-roll oficial), "
                         "'tela:' (gravação de tela nossa) ou 'estoque:' (Pexels). Só foto e animação fazem a pessoa pular")
    if q == "tutorial" and sum(1 for t in tipos if t == "passo") < 3:
        problemas.append("tutorial precisa de pelo menos 3 cenas 'passo'")
    palavras = sum(len(falado(c.get("fala", "")).split()) for c in cenas)
    faixa = {"60s": (75, 165), "historias": (140, 225), "lafora": (700, 1300), "tutorial": (600, 1300)}.get(q, (60, 2000))
    if not faixa[0] <= palavras <= faixa[1]:
        problemas.append(f"{palavras} palavras faladas; o quadro pede de {faixa[0]} a {faixa[1]}")
    minimo_tipos = {"60s": 4, "historias": 4, "lafora": 7, "tutorial": 6}.get(q, 5)
    if len(set(tipos)) < minimo_tipos:
        problemas.append(f"pouca variedade de cenas: {sorted(set(tipos))} (mínimo {minimo_tipos} tipos diferentes)")
    for i in range(len(tipos) - 2):
        if tipos[i] == tipos[i + 1] == tipos[i + 2]:
            problemas.append(f"3 cenas seguidas do tipo '{tipos[i]}' (cenas {i + 1} a {i + 3})")
            break
    minimo_fotos = 8 if longo else 4
    if len(fotos) < minimo_fotos:
        problemas.append(f"só {len(fotos)} fotos diferentes (mínimo {minimo_fotos}); use imagens oficiais do produto/jogo/empresa")
    if len(rot.get("fontes") or []) < 2 and not rot.get("post"):
        problemas.append("menos de 2 fontes no roteiro")
    if q in ("60s", "lafora") and "manchete" not in tipos and (rot.get("fontes") or rot.get("post")):
        problemas.append("falta uma cena 'manchete' (print da notícia com o trecho destacado)")
    if q == "historias" and not ({"data", "linha"} & set(tipos)):
        problemas.append("Histórias Tech precisa de ano na tela: cena 'data' ou 'linha'")
    if q == "historias" and not rot.get("numero"):
        problemas.append("Histórias Tech precisa do campo 'numero' (episódio #N)")
    if longo and not any(c.get("capitulo") for c in cenas):
        problemas.append("vídeo longo sem 'capitulo' nas cenas que abrem cada bloco")
    ultima = (cenas[-1].get("fala", "") if cenas else "").lower()
    if longo and not re.search(r"inscrev", ultima):
        problemas.append("a última fala do vídeo longo não pede para se inscrever no canal")
    if not longo and re.search(r"inscrev", " ".join(c.get("fala", "") for c in cenas[:2]).lower()):
        problemas.append("Short não pede inscrição no começo (o botão animado aparece sozinho no fim)")
    # embalagem: título, resumo, hashtags e capa (editorial/manual_youtube.md, seção 7)
    import unicodedata
    sem_acento = lambda x: unicodedata.normalize("NFKD", x or "").encode("ascii", "ignore").decode().lower()
    titulo = rot.get("titulo", "")
    nucleo = re.sub(r"\s*#shorts\s*$", "", titulo, flags=re.I)
    if len(nucleo) > 60:
        problemas.append(f"título com {len(nucleo)} caracteres (máximo 60, sem contar o #shorts)")
    if not longo and not titulo.lower().endswith("#shorts"):
        problemas.append("título de Short tem que terminar com #shorts")
    pc = rot.get("palavra_chave", "")
    if not pc:
        problemas.append("falta 'palavra_chave' (o termo que as pessoas buscam, ex.: 'ocarina of time switch 2')")
    else:
        tem = lambda texto, ate: all(re.search(r"\b" + re.escape(w) + r"\b", sem_acento(texto)[:ate]) for w in sem_acento(pc).split())
        if not tem(nucleo, max(45, len(pc) + 15)):
            problemas.append(f"a palavra-chave '{pc}' tem que estar no começo do título")
        if not tem(rot.get("resumo", ""), 160):
            problemas.append("a 1ª frase do 'resumo' tem que ter a palavra-chave")
    if not 3 <= len(rot.get("hashtags") or []) <= 5:
        problemas.append("use de 3 a 5 hashtags (a mais buscada primeiro)")
    if longo:
        ct = rot.get("capa_texto", "")
        if not ct or len(ct.split()) > 4:
            problemas.append("'capa_texto' obrigatório no longo, com no máximo 4 palavras")
        elif sem_acento(ct) in sem_acento(titulo):
            problemas.append("'capa_texto' não pode repetir o título: a capa completa o título")
    for p in problemas:
        print("PROBLEMA:", p)
    print("OK" if not problemas else f"{len(problemas)} problema(s)")
    return 1 if problemas else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro", nargs="?")
    ap.add_argument("--pronuncia", help="mostra como a voz grátis vai ler um texto")
    ap.add_argument("--audio", help="narração pronta (ElevenLabs) com o roteiro inteiro")
    ap.add_argument("--voz", help=f"voz grátis (padrão {VOZ_PADRAO}); ex.: kokoro:pm_santa, piper:cadu")
    ap.add_argument("--saida")
    ap.add_argument("--manter", action="store_true", help="não apaga a pasta temporária em video/public/run/")
    ap.add_argument("--fala", action="store_true", help="só imprime o texto falado inteiro (para o ElevenLabs)")
    ap.add_argument("--comprimir", help="(reserva antiga) comprime um .mp4 para menos de 9,5 MB; não use para publicar")
    ap.add_argument("--checar", action="store_true", help="confere se o roteiro tem variedade, fotos, fontes e pedido de inscrição")
    a = ap.parse_args()
    if a.comprimir:
        arq = Path(a.comprimir)
        tmp = arq.with_suffix(".tmp.mp4")
        comprimir(arq, tmp, base.duracao(arq), "longo" if base.duracao(arq) > 70 else "short")
        os.replace(tmp, arq)
        print(f"{arq}: {arq.stat().st_size / 1024 / 1024:.2f} MB")
        return
    if a.pronuncia:
        print(pronunciar(a.pronuncia))
        try:
            from kokoro_onnx.tokenizer import Tokenizer
            print(Tokenizer().phonemize(pronunciar(a.pronuncia), "pt-br"))
        except Exception:
            pass
        return
    rot = json.loads(Path(a.roteiro).read_text(encoding="utf-8"))
    if a.checar:
        sys.exit(checar(rot))
    if a.fala:
        print(" ".join(falado(c["fala"]) for c in rot["cenas"] if c.get("fala")))
        return
    res = montar(rot, a.audio, a.saida, a.voz)
    desc = Path(res["arquivo"]).with_suffix(".txt")
    desc.write_text(base.gerar_descricao(rot), encoding="utf-8")
    res["descricao"] = str(desc)
    # resumo para a publicação (a PARTE B lê este arquivo)
    resumo = {k: rot.get(k) for k in ("slug", "tipo", "quadro", "numero", "post", "titulo", "hashtags")}
    resumo.update({"voz": res.get("voz"), "segundos": res.get("segundos") or res.get("duracao")})
    Path(res["arquivo"]).with_suffix(".json").write_text(json.dumps(resumo, ensure_ascii=False, indent=1), encoding="utf-8")
    if not a.manter:
        shutil.rmtree(PUBLICO / "run" / rot["slug"], ignore_errors=True)
    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
