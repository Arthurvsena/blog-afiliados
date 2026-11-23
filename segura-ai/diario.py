"""Produção diária do Segura Aí 3D (roda no GitHub Actions, workflow segura-diario.yml).

Pega o próximo roteiro "pronto" da fila (segura-ai/fila.json), monta o vídeo com montar.py e escreve,
ao lado do MP4, a legenda pronta para o TikTok. Marca na fila o que foi produzido. Se a voz falhar
(cota do Gemini), para e deixa para amanhã.

Uso: python3 segura-ai/diario.py [--saida _segura] [--quantos N] [--checar]
"""
import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

AQUI = Path(__file__).resolve().parent
FILA = AQUI / "fila.json"
CFG = yaml.safe_load((AQUI / "config.yaml").read_text(encoding="utf-8"))
HOJE = (dt.datetime.utcnow() - dt.timedelta(hours=3)).date().isoformat()
AMBIENTES = {"sala", "banheiro", "cozinha"}
OBJETOS = {"cadeira_plastico", "escada", "lampada", "interruptor", "quadro_disjuntores", "tomada", "benjamim", "chuveiro",
           "poca", "fogao", "panela", "botijao", "extintor", "caixa", "fio_no_chao", "bilhete"}
ACOES = {"parado", "andar", "subir", "esticar", "mexer", "choque", "cair", "escorregar", "deitado", "apontar", "comemorar", "pensar"}
CAMERAS = {"geral", "personagem", "rosto", "perto", "baixo", "cima", "parede"}


def ler_fila():
    return json.loads(FILA.read_text(encoding="utf-8"))


def salvar_fila(f):
    FILA.write_text(json.dumps(f, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def legenda_tiktok(rot):
    vistas, hs = set(), []
    for h in (rot.get("hashtags") or []) + CFG.get("hashtags_fixas", []):
        h = h.lstrip("#")
        if h.lower() not in vistas:
            vistas.add(h.lower()); hs.append(h)
    gancho = rot["titulo"]
    pede = f"Comenta {rot['comenta']} se já passou por isso 👇" if rot.get("comenta") else ""
    return "\n\n".join(x for x in [gancho, rot.get("descricao", ""), pede, "Salva pra lembrar e manda pra quem precisa ver 🦺",
                                    " ".join("#" + h for h in hs[:8])] if x)[:2150]


def checar_roteiro(rot):
    erros = []
    falas = [c.get("fala", "") for c in rot["cenas"]]
    palavras = sum(len(f.split()) for f in falas)
    if any(not f for f in falas):
        erros.append("cena sem fala")
    if palavras < 160:
        erros.append(f"{palavras} palavras: curto demais (o vídeo precisa passar de 60 s; mínimo 160 palavras)")
    if palavras > 290:
        erros.append(f"{palavras} palavras: longo demais (máximo 290)")
    for i, c in enumerate(rot["cenas"], 1):
        if c.get("ambiente", "sala") not in AMBIENTES:
            erros.append(f"cena {i}: ambiente {c.get('ambiente')} não existe")
        cam = (c.get("camera") or "geral").split(":")[0]
        if cam not in CAMERAS:
            erros.append(f"cena {i}: câmera {cam} não existe")
        ids = set()
        for o in c.get("objetos") or []:
            if o.get("tipo") not in OBJETOS:
                erros.append(f"cena {i}: objeto {o.get('tipo')} não existe")
            ids.add(o.get("id") or o.get("tipo"))
        p = c.get("personagem") or {}
        if p.get("acao", "parado") not in ACOES:
            erros.append(f"cena {i}: ação {p.get('acao')} não existe")
        if p.get("em_cima") and p["em_cima"] not in ids:
            erros.append(f"cena {i}: em_cima '{p['em_cima']}' não está nos objetos da cena")
    if not rot.get("fontes"):
        erros.append("faltam as fontes (norma, manual do fabricante, Corpo de Bombeiros...) que sustentam as dicas")
    if not rot["cenas"][-1].get("chamada"):
        erros.append("a última cena precisa da chamada (segue + comenta)")
    return erros, palavras


def checar():
    erros = 0
    for r in ler_fila()["roteiros"]:
        arq = AQUI / "roteiros" / f"{r['slug']}.json"
        if not arq.exists():
            print("FALTA", arq); erros += 1; continue
        e, n = checar_roteiro(json.loads(arq.read_text(encoding="utf-8")))
        for x in e:
            print(f"{r['slug']}: {x}")
        erros += len(e)
    print("OK" if not erros else f"{erros} problema(s)")
    return erros


def voz_da_vez(fila):
    vozes = (CFG.get("producao") or {}).get("vozes") or ["gemini:Fenrir"]
    usadas = [r.get("voz") for r in fila["roteiros"] if r.get("voz")]
    return min(vozes, key=lambda v: usadas.count(v))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", default="_segura")
    ap.add_argument("--quantos", type=int, default=int(CFG["producao"]["videos_por_dia"]))
    ap.add_argument("--checar", action="store_true")
    a = ap.parse_args()
    if a.checar:
        sys.exit(1 if checar() else 0)
    fila = ler_fila()
    prontos = [r for r in fila["roteiros"] if r.get("status") == "pronto"]
    saida = Path(a.saida); saida.mkdir(parents=True, exist_ok=True)
    feitos = 0
    for r in prontos[:a.quantos]:
        arq = AQUI / "roteiros" / f"{r['slug']}.json"
        rot = json.loads(arq.read_text(encoding="utf-8"))
        voz = voz_da_vez(fila)
        print(f"== {r['slug']} ({voz})", flush=True)
        try:
            subprocess.run([sys.executable, str(AQUI / "montar.py"), str(arq), "--voz", voz, "--saida", str(saida)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Falhou ao montar {r['slug']}: {e}. Fica para amanhã.", file=sys.stderr)
            break
        sufixo = "-" + voz.split(":")[-1].lower() if os.environ.get("GEMINI_API_KEY") else ""
        mp4 = saida / f"{r['slug']}{sufixo}.mp4"
        if mp4.exists() and sufixo:
            mp4.rename(saida / f"{r['slug']}.mp4")
            j = saida / f"{r['slug']}{sufixo}.json"
            if j.exists():
                j.rename(saida / f"{r['slug']}.json")
        (saida / f"{r['slug']}-tiktok.txt").write_text(legenda_tiktok(rot), encoding="utf-8")
        r.update({"status": "produzido", "produzido": HOJE, "release": f"segura-{HOJE}", "voz": voz})
        feitos += 1
    salvar_fila(fila)
    restantes = sum(1 for r in fila["roteiros"] if r.get("status") == "pronto")
    Path("_segura_restantes.txt").write_text(str(restantes))
    print(f"Produzidos hoje: {feitos}. Roteiros prontos na fila: {restantes}.")


if __name__ == "__main__":
    main()
