"""Pesquisa de palavras-chave com dados reais de busca (sem custo).

Fontes:
  - Autocompletar do Google Brasil: o que as pessoas digitam no Google.
  - Autocompletar da busca do Mercado Livre: o que quem vai comprar digita no ML.
    (Se o ML bloquear daqui, a tarefa do Chrome de segunda coleta pelo navegador
     e grava em data/palavras_ml.json, que este script também lê.)
  - Search Console (data/metricas.json): buscas que já trazem o blog no Google.

Para cada semente do config.yaml, expande com modificadores de compra e de
dúvida e com o alfabeto, como as ferramentas pagas fazem. Cada termo recebe:
  - fontes: onde apareceu (google, mercadolivre, search_console)
  - forca: quantas expansões diferentes sugeriram o termo e em que posição
    (sinal de popularidade; o autocompletar só sugere o que muita gente busca)
  - intencao: compra | comparacao | duvida | navegacao
  - tipo_post: lista | review | comparativo | guia (formato que melhor atende)
  - coberto_por: slug do post que já mira esse termo (se houver)

Uso: python3 scripts/palavras.py            # todos os subnichos
     python3 scripts/palavras.py fones-caixas-bluetooth
Saída: data/palavras.json
"""
import datetime as dt
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "site"))
from build import config, posts  # noqa: E402

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
MODIFICADORES = [
    "", "melhor", "melhores", "qual", "como escolher", "vale a pena", "barato", "custo beneficio",
    "até 100", "até 200", "até 300", "ou", "vs", "para", "com", "review", "é bom", "original",
]
ALFABETO = "abcdefghijlmnoprstuv"


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9$ ]+", " ", t)).strip()


def pegar(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9", **(headers or {})})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", "replace")


def google(q):
    url = "https://suggestqueries.google.com/complete/search?client=firefox&hl=pt-BR&gl=br&q=" + urllib.parse.quote(q)
    try:
        return json.loads(pegar(url))[1]
    except Exception:
        return []


ML_BLOQUEADO = False


def mercadolivre(q):
    global ML_BLOQUEADO
    if ML_BLOQUEADO:
        return []
    url = ("https://http2.mlstatic.com/resources/sites/MLB/autosuggest?showFilters=true&limit=10&api_version=2&q="
           + urllib.parse.quote(q))
    try:
        dados = json.loads(pegar(url, {"Origin": "https://www.mercadolivre.com.br",
                                       "Referer": "https://www.mercadolivre.com.br/"}))
        return [s["q"] for s in dados.get("suggested_queries", [])]
    except Exception:
        ML_BLOQUEADO = True  # bloqueado deste servidor: a tarefa do Chrome cobre
        return []


def intencao(t):
    if re.search(r"\b(vs|ou|versus|comparativo|diferenca)\b", t):
        return "comparacao", "comparativo"
    if re.search(r"\b(melhor|melhores|top|ranking|barat|custo beneficio|ate \d+|ate r)", t):
        return "compra", "lista"
    if re.search(r"\b(vale a pena|e bom|presta|review|analise|confiavel|original)\b", t):
        return "compra", "review"
    if re.search(r"\b(como|qual|quanto|quantos|porque|por que|o que|pode|funciona|precisa|diferenca)\b", t):
        return "duvida", "guia"
    return "navegacao", "lista"


def coletar(subnicho, sementes):
    termos = {}

    def anotar(lista, fonte, peso_base):
        for pos, s in enumerate(lista):
            n = norm(s)
            if len(n) < 4 or len(n.split()) > 9:
                continue
            item = termos.setdefault(n, {"termo": s.strip().lower(), "fontes": set(), "forca": 0.0})
            item["fontes"].add(fonte)
            item["forca"] += peso_base * (1 - pos / 12)

    for semente in sementes:
        consultas = [f"{m} {semente}".strip() if m in ("melhor", "melhores", "qual", "como escolher") else f"{semente} {m}".strip()
                     for m in MODIFICADORES]
        consultas += [f"{semente} {letra}" for letra in ALFABETO]
        for q in consultas:
            anotar(google(q), "google", 1.0)
            anotar(mercadolivre(q), "mercadolivre", 1.3)  # intenção de compra pesa mais
            time.sleep(0.25)

    # coleta do ML feita pelo Chrome (quando o servidor é bloqueado)
    ml_chrome = RAIZ / "data" / "palavras_ml.json"
    if ml_chrome.exists():
        extra = json.loads(ml_chrome.read_text(encoding="utf-8"))
        anotar(extra.get(subnicho, []), "mercadolivre", 1.3)

    # buscas reais que já trazem o blog (Search Console)
    met = RAIZ / "data" / "metricas.json"
    if met.exists():
        for sem in json.loads(met.read_text(encoding="utf-8")).get("semanas", [])[-4:]:
            for c in sem.get("consultas") or []:
                if any(norm(x) in norm(c.get("termo", "")) for x in sementes):
                    anotar([c["termo"]], "search_console", 2.0)
    return termos


def main():
    cfg = config()
    alvo = sys.argv[1:] or [s["slug"] for s in cfg["subnichos"]]
    arq = RAIZ / "data" / "palavras.json"
    saida = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    existentes = {norm(str(p.get("palavra_chave", ""))): p["slug"] for p in posts()}
    total_fontes = set()
    for s in cfg["subnichos"]:
        if s["slug"] not in alvo:
            continue
        termos = coletar(s["slug"], s["sementes"])
        lista = []
        for n, t in termos.items():
            intent, formato = intencao(n)
            lista.append({
                "termo": t["termo"], "fontes": sorted(t["fontes"]), "forca": round(t["forca"], 2),
                "intencao": intent, "tipo_post": formato,
                "coberto_por": existentes.get(n) or next((sl for k, sl in existentes.items() if k and k in n), None),
            })
            total_fontes |= t["fontes"]
        lista.sort(key=lambda x: (-len(x["fontes"]), -x["forca"]))
        saida[s["slug"]] = {"atualizado": dt.date.today().isoformat(), "termos": lista[:150]}
        print(f"{s['slug']}: {len(lista)} termos (top: {', '.join(x['termo'] for x in lista[:5])})")
    saida["_fontes_ultima_coleta"] = sorted(total_fontes)
    saida["_mercadolivre_bloqueado_no_servidor"] = ML_BLOQUEADO
    arq.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    if not total_fontes:
        print("ATENÇÃO: nenhuma fonte respondeu. Verifique a conexão.")
        sys.exit(1)


if __name__ == "__main__":
    main()
