"""Marca no escritório quem está trabalhando agora e o que cada agente fez.

  python3 scripts/escritorio.py trabalhando AGENTE [AGENTE...] "o que está fazendo"
  python3 scripts/escritorio.py feito AGENTE "o que fez"   [--se-trabalhando]
  python3 scripts/escritorio.py erro AGENTE "o que deu errado"
  python3 scripts/escritorio.py parado AGENTE "motivo"

"trabalhando" grava data/ao_vivo.json (o escritório lê esse arquivo do GitHub e anima o agente; vale por
3 horas). As rotinas do GitHub Actions já aparecem sozinhas como trabalhando: use isto nas tarefas do Chrome,
com commit e push logo em seguida. "feito/erro/parado" gravam o resultado em data/escritorio.json e tiram o
agente de ao_vivo.json.
"""
import datetime as dt
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
VIVO = RAIZ / "data" / "ao_vivo.json"
ESC = RAIZ / "data" / "escritorio.json"


def agora():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=-3)))


def ler(arq, padrao):
    try:
        return json.loads(arq.read_text(encoding="utf-8"))
    except Exception:
        return padrao


def gravar(arq, dados):
    arq.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(args):
    if len(args) < 3:
        print(__doc__); return 1
    acao, se_trab = args[0], "--se-trabalhando" in args
    args = [a for a in args[1:] if a != "--se-trabalhando"]
    texto, agentes = args[-1], args[:-1]
    vivo = ler(VIVO, {"agentes": {}})
    if acao == "trabalhando":
        for a in agentes:
            vivo["agentes"][a] = {"desde": agora().isoformat(timespec="seconds"), "tarefa": texto}
        gravar(VIVO, vivo); return 0
    esc = ler(ESC, {"agentes": {}, "historico": []})
    status = {"feito": "ok", "erro": "erro", "parado": "ocioso"}.get(acao)
    if not status:
        print(__doc__); return 1
    for a in agentes:
        if se_trab and a not in vivo["agentes"] and esc.get("agentes", {}).get(a, {}).get("status") == "ok":
            continue
        esc.setdefault("agentes", {})[a] = {"status": status, "tarefa": texto}
        if status != "ocioso":
            esc.setdefault("historico", []).append({"data": agora().date().isoformat(), "agente": a, "texto": texto})
        vivo["agentes"].pop(a, None)
    esc["historico"] = esc.get("historico", [])[-60:]
    gravar(ESC, esc); gravar(VIVO, vivo)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
