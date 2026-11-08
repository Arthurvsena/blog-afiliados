"""Produção diária da Bíblia Animada (roda no GitHub Actions, workflow biblia-diario.yml).

Pega os próximos roteiros "pronto" da fila (canal-biblia/fila.json), monta cada vídeo com
montar.py e escreve, ao lado de cada MP4, os textos prontos para YouTube, TikTok e Instagram.
Marca na fila o que foi produzido. Se a voz falhar (cota do Gemini), para e deixa o resto para amanhã.

Uso: python3 canal-biblia/diario.py [--saida _biblia] [--quantos N] [--checar]
"""
import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import yaml

AQUI = Path(__file__).resolve().parent
FILA = AQUI / "fila.json"
CFG = yaml.safe_load((AQUI / "config.yaml").read_text(encoding="utf-8"))
HOJE = (dt.datetime.utcnow() - dt.timedelta(hours=3)).date().isoformat()


def ler_fila():
    return json.loads(FILA.read_text(encoding="utf-8"))


def salvar_fila(f):
    FILA.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def tags(rot):
    vistas, res = set(), []
    for t in (rot.get("hashtags") or []) + CFG.get("hashtags_fixas", []):
        t = t.lstrip("#")
        if t.lower() not in vistas:
            vistas.add(t.lower())
            res.append(t)
    return res


def textos(rot):
    """Título e legendas de cada rede (indicação só entra quando houver link)."""
    vers = next((c for c in rot["cenas"] if c.get("versiculo")), None)
    citacao = f"\"{vers['fala']}\" ({vers['texto_tela']})" if vers else ""
    ind = CFG.get("indicacao") or {}
    chamada = ind.get("chamada") if ind.get("link") else ""
    hs = tags(rot)
    titulo = rot["titulo"] if len(rot["titulo"]) <= 95 else rot["titulo"][:92].rsplit(" ", 1)[0] + "…"
    youtube = "\n\n".join(x for x in [
        rot["titulo"],
        f"{rot['referencia']} em menos de 1 minuto, em animação.",
        citacao,
        chamada,
        f"Inscreva-se na {CFG['canal']['nome']}: uma nova história da Bíblia todo dia. 🙏",
        " ".join("#" + h for h in hs[:8]),
    ] if x)
    tiktok = f"{rot['titulo']} 🙏 ({rot['referencia']})\n\n{citacao}\n\n" + ("Link na bio 📖\n\n" if chamada else "") + \
             " ".join("#" + h for h in hs[:7])
    instagram = f"{rot['titulo']} 🙏\n\n{rot['referencia']}\n{citacao}\n\n" + (f"{chamada}\n\n" if chamada else "") + \
                f"Siga a {CFG['canal']['nome']} para uma história nova todo dia.\n\n" + " ".join("#" + h for h in hs)
    return titulo, youtube, tiktok[:2150], instagram


def checar():
    """Confere todos os roteiros da fila: arquivo existe, cenas têm fala e o último é o versículo."""
    erros = 0
    for h in ler_fila()["historias"]:
        arq = AQUI / "roteiros" / f"{h['slug']}.json"
        if not arq.exists():
            print("FALTA", arq); erros += 1; continue
        rot = json.loads(arq.read_text(encoding="utf-8"))
        palavras = sum(len(c["fala"].split()) for c in rot["cenas"])
        problemas = [c for c in rot["cenas"] if not c.get("fala")]
        if problemas or not (rot["cenas"][-1].get("versiculo") or rot["cenas"][-1].get("id") == "versiculo"):
            print("ROTEIRO INCOMPLETO", h["slug"]); erros += 1
        if not 55 <= palavras <= 150:
            print(f"AVISO {h['slug']}: {palavras} palavras (ideal 70 a 130)")
    print("OK" if not erros else f"{erros} problema(s)")
    return erros


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default="_biblia")
    ap.add_argument("--quantos", type=int, default=CFG["producao"]["videos_por_dia"])
    ap.add_argument("--checar", action="store_true")
    a = ap.parse_args()
    if a.checar:
        sys.exit(1 if checar() else 0)
    saida = Path(a.saida); saida.mkdir(parents=True, exist_ok=True)
    fila = ler_fila()
    pendentes = [h for h in fila["historias"] if h["status"] == "pronto"]
    vozes = CFG["producao"]["vozes"]
    feitos = sum(1 for h in fila["historias"] if h["status"] != "pronto")
    for i, h in enumerate(pendentes[:a.quantos]):
        roteiro = AQUI / "roteiros" / f"{h['slug']}.json"
        voz = vozes[(feitos + i) % len(vozes)]
        print(f"== {h['slug']} ({voz})", flush=True)
        r = subprocess.run([sys.executable, str(AQUI / "montar.py"), str(roteiro), "--voz", voz, "--saida", str(saida)])
        mp4 = saida / f"{h['slug']}-{voz.split(':')[-1].lower()}.mp4"
        if r.returncode != 0 or not mp4.exists():
            print(f"FALHOU {h['slug']}: deixo para a próxima rodada (provável cota do Gemini)")
            break
        final = saida / f"{h['slug']}.mp4"
        mp4.rename(final)
        mp4.with_suffix(".json").unlink(missing_ok=True)
        rot = json.loads(roteiro.read_text(encoding="utf-8"))
        titulo, yt, tk, ig = textos(rot)
        (saida / f"{h['slug']}-youtube.txt").write_text(yt, encoding="utf-8")
        (saida / f"{h['slug']}-tiktok.txt").write_text(tk, encoding="utf-8")
        (saida / f"{h['slug']}-instagram.txt").write_text(ig, encoding="utf-8")
        (saida / f"{h['slug']}.json").write_text(json.dumps({"slug": h["slug"], "titulo": titulo, "referencia": rot["referencia"],
                                                             "voz": voz, "produzido": HOJE, "release": f"biblia-{HOJE}"},
                                                            ensure_ascii=False, indent=1), encoding="utf-8")
        h.update({"status": "produzido", "produzido": HOJE, "release": f"biblia-{HOJE}", "voz": voz})
        salvar_fila(fila)
    restantes = sum(1 for h in fila["historias"] if h["status"] == "pronto")
    print(f"Roteiros prontos na fila: {restantes}")
    Path("_biblia_restantes.txt").write_text(str(restantes))


if __name__ == "__main__":
    main()
