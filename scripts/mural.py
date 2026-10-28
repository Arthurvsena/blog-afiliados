"""Mural da equipe: como os agentes conversam entre si.

Cada mensagem é um pedido, aviso ou ideia de um agente para outro (ou para
"todos"), sempre ligada a uma das 4 metas: vendas, cliques, acessos, engajamento.

Uso:
  python3 scripts/mural.py listar [--para AGENTE]        # mensagens abertas
  python3 scripts/mural.py postar --de A --para B --meta cliques --assunto "..." --mensagem "..."
  python3 scripts/mural.py responder ID --de A --resposta "..."   # resolve a mensagem
Agentes: chefe, pesquisador, curador, redator, seo, vendas, designer,
atualizador, analista, todos.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ARQ = Path(__file__).resolve().parent.parent / "data" / "mural.json"
AGENTES = {"chefe", "pesquisador", "curador", "redator", "seo", "vendas", "designer", "atualizador", "analista", "todos"}
METAS = {"vendas", "cliques", "acessos", "engajamento"}


def carregar():
    return json.loads(ARQ.read_text(encoding="utf-8")) if ARQ.exists() else {"proximo_id": 1, "mensagens": []}


def salvar(d):
    # guarda abertas + as 80 resolvidas mais recentes
    abertas = [m for m in d["mensagens"] if m["status"] == "aberta"]
    resolvidas = [m for m in d["mensagens"] if m["status"] != "aberta"][-80:]
    d["mensagens"] = sorted(abertas + resolvidas, key=lambda m: m["id"])
    ARQ.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="acao", required=True)
    l = sub.add_parser("listar"); l.add_argument("--para")
    p = sub.add_parser("postar")
    for a in ("de", "para", "meta", "assunto", "mensagem"):
        p.add_argument("--" + a, required=True)
    r = sub.add_parser("responder"); r.add_argument("id", type=int); r.add_argument("--de", required=True); r.add_argument("--resposta", required=True)
    a = ap.parse_args()
    d = carregar()
    hoje = dt.date.today().isoformat()

    if a.acao == "listar":
        abertas = [m for m in d["mensagens"] if m["status"] == "aberta"
                   and (not a.para or m["para"] in (a.para, "todos"))]
        if not abertas:
            print("Nenhuma mensagem aberta.")
        for m in abertas:
            print(f"#{m['id']} [{m['meta']}] {m['de']} → {m['para']} ({m['data']}): {m['assunto']}\n    {m['mensagem']}")
        return

    if a.acao == "postar":
        if a.de not in AGENTES or a.para not in AGENTES:
            sys.exit(f"Agente inválido. Use: {', '.join(sorted(AGENTES))}")
        if a.meta not in METAS:
            sys.exit(f"Meta inválida. Use: {', '.join(sorted(METAS))}")
        m = {"id": d["proximo_id"], "data": hoje, "de": a.de, "para": a.para, "meta": a.meta,
             "assunto": a.assunto.strip(), "mensagem": a.mensagem.strip(), "status": "aberta"}
        d["mensagens"].append(m); d["proximo_id"] += 1
        salvar(d)
        print(f"Mensagem #{m['id']} postada para {a.para}.")
        return

    if a.acao == "responder":
        for m in d["mensagens"]:
            if m["id"] == a.id:
                m.update(status="resolvida", resposta=a.resposta.strip(), respondido_por=a.de, resolvida_em=hoje)
                salvar(d)
                print(f"Mensagem #{a.id} respondida e resolvida.")
                return
        sys.exit(f"Mensagem #{a.id} não encontrada.")


if __name__ == "__main__":
    main()
