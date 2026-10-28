"""Checagem de qualidade dos posts. Os agentes rodam isto antes de terminar.

Uso:
  python3 scripts/verificar.py                      # verifica todos os posts
  python3 scripts/verificar.py content/posts/x.md   # verifica um post
Sai com código 1 se algum post tiver ERRO.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "site"))
from build import TOKEN_BOTAO, TOKEN_LINK, TOKEN_PRODUTO, TOKENS_VENDA, config, ler_post, produtos  # noqa: E402

OBRIGATORIOS = ["titulo", "slug", "descricao", "palavra_chave", "subnicho", "tipo", "publicado", "atualizado"]
TIPOS = {"lista": 3, "comparativo": 2, "review": 1, "guia": 0}
PROIBIDOS = [
    r"mercadolivre\.com", r"mercadolibre\.com", r"meli\.la", r"\bcomo uma? (?:modelo de )?ia\b",
    r"\beu testei\b", r"\btestamos pessoalmente\b", r"lorem ipsum",
]


def verificar(caminho: Path, cfg, catalogo, slugs_vistos):
    erros, avisos = [], []
    try:
        meta, corpo = ler_post(caminho)
    except Exception as e:  # noqa: BLE001
        return [f"não consegui ler: {e}"], []

    for campo in OBRIGATORIOS:
        if not meta.get(campo):
            erros.append(f"campo '{campo}' faltando no frontmatter")
    slug = meta.get("slug", "")
    if slug and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        erros.append("slug deve ter só letras minúsculas sem acento, números e hífens")
    if slug and caminho.stem != slug:
        erros.append(f"nome do arquivo deve ser {slug}.md")
    if slug in slugs_vistos:
        erros.append("slug repetido em outro post")
    slugs_vistos.add(slug)

    subnichos = {s["slug"] for s in cfg["subnichos"]}
    if meta.get("subnicho") and meta["subnicho"] not in subnichos:
        erros.append(f"subnicho '{meta['subnicho']}' não existe no config.yaml")
    tipo = meta.get("tipo")
    if tipo and tipo not in TIPOS:
        erros.append(f"tipo '{tipo}' inválido (use {', '.join(TIPOS)})")

    titulo = str(meta.get("titulo", ""))
    if len(titulo) > 65:
        avisos.append(f"título com {len(titulo)} caracteres (ideal até 60)")
    desc = str(meta.get("descricao", ""))
    if desc and not 100 <= len(desc) <= 160:
        avisos.append(f"descrição com {len(desc)} caracteres (ideal 120–155)")

    usados = TOKEN_PRODUTO.findall(corpo)
    for t in TOKENS_VENDA:
        for m in t.finditer(corpo):
            if m.group(1) not in catalogo:
                erros.append(f"produto '{m.group(1)}' não existe ou não está ativo com link no CSV")
    if tipo in TIPOS and len(set(usados)) < TIPOS[tipo]:
        erros.append(f"post do tipo {tipo} precisa de {TIPOS[tipo]}+ produtos, tem {len(set(usados))}")
    # vendas: chamadas de compra suficientes
    ctas = sum(len(t.findall(corpo)) for t in TOKENS_VENDA)
    links_texto = len(TOKEN_LINK.findall(corpo))
    if tipo in ("lista", "comparativo", "review"):
        if links_texto == 0:
            avisos.append("vendas: nenhum {{link:ID}} no texto; cite o produto com link onde o leitor decide")
        if ctas < len(set(usados)) * 2:
            avisos.append(f"vendas: só {ctas} chamadas de compra para {len(set(usados))} produtos (ideal: 2+ por produto)")
    elif tipo == "guia" and ctas == 0 and any(p.get("subnicho") == meta.get("subnicho") for p in catalogo.values()):
        avisos.append("vendas: guia sem nenhuma chamada de compra, mas há produtos da categoria no catálogo")

    texto = corpo
    for t in TOKENS_VENDA:
        texto = t.sub("", texto)
    for padrao in PROIBIDOS:
        if re.search(padrao, texto, re.I):
            erros.append(f"texto proibido encontrado: /{padrao}/ (links de compra só via {{{{produto:ID}}}})")
    if re.search(r"R\$\s?\d", texto):
        avisos.append("o texto cita preço em R$: prefira faixas ('até R$ 200') a preços exatos")

    abre = len(re.findall(r"^:::\s*\w+", corpo, re.M))
    fecha = len(re.findall(r"^:::\s*$", corpo, re.M))
    if abre != fecha:
        erros.append(f"blocos ::: desbalanceados ({abre} abertos, {fecha} fechados)")
    for tipo in re.findall(r"^:::\s*(\w+)", corpo, re.M):
        if tipo not in ("pros", "contras", "veredito", "dica", "atencao"):
            erros.append(f"bloco ':::{tipo}' não existe (use pros, contras, veredito, dica ou atencao)")
    texto = re.sub(r"^:::.*$", "", texto, flags=re.M)

    palavras = len(re.findall(r"\w+", texto))
    minimo = cfg["rotina"]["palavras_minimas"]
    if palavras < minimo:
        erros.append(f"{palavras} palavras (mínimo {minimo})")
    if len(re.findall(r"^## ", corpo, re.M)) < 3:
        erros.append("use pelo menos 3 subtítulos H2 (##)")
    if re.search(r"^# ", corpo, re.M):
        erros.append("não use H1 (#) no corpo: o título já é o H1")
    chave = str(meta.get("palavra_chave", "")).lower()
    primeiro = corpo.strip().split("\n\n")[0].lower()
    if chave and not all(p in primeiro for p in chave.split()[:3]):
        avisos.append("a palavra-chave não aparece no primeiro parágrafo")
    if not meta.get("faq"):
        avisos.append("sem FAQ no frontmatter")
    # SEO: palavra-chave real e bem posicionada
    import json as _json, unicodedata as _ud
    _n = lambda t: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", _ud.normalize("NFKD", str(t).lower()).encode("ascii", "ignore").decode())).strip()
    arq_pal = RAIZ / "data" / "palavras.json"
    if chave and arq_pal.exists():
        pal = _json.loads(arq_pal.read_text(encoding="utf-8"))
        reais = {_n(x["termo"]) for k, v in pal.items() if isinstance(v, dict) for x in v.get("termos", [])}
        if reais and _n(chave) not in reais:
            avisos.append("seo: a palavra_chave não está em data/palavras.json (use um termo real de busca)")
    if chave:
        nucleo = [w for w in _n(chave).split() if len(w) > 2][:3]
        if not all(w in _n(titulo) for w in nucleo):
            avisos.append("seo: a palavra-chave não aparece no título")
        if not all(w in _n(meta.get("descricao", "")) for w in nucleo):
            avisos.append("seo: a palavra-chave não aparece na descrição")
        h2s = " ".join(re.findall(r"^## (.+)$", corpo, re.M))
        if not any(w in _n(h2s) for w in nucleo):
            avisos.append("seo: nenhum H2 usa a palavra-chave")
    if not meta.get("palavras_secundarias"):
        avisos.append("seo: sem palavras_secundarias no frontmatter")
    if not meta.get("capa_frase"):
        avisos.append("sem capa_frase: o post ainda não passou pelo designer")
    if tipo in ("lista", "comparativo") and "|" not in corpo:
        avisos.append("lista/comparativo sem tabela comparativa")
    return erros, avisos


def main():
    cfg, catalogo = config(), produtos()
    alvos = [Path(a) for a in sys.argv[1:]] or sorted((RAIZ / "content" / "posts").glob("*.md"))
    vistos, falhou = set(), False
    if not alvos:
        print("Nenhum post para verificar.")
    for c in alvos:
        erros, avisos = verificar(c, cfg, catalogo, vistos)
        status = "ERRO" if erros else "OK"
        print(f"[{status}] {c.name}")
        for e in erros:
            print(f"   ✗ {e}")
        for a in avisos:
            print(f"   ! {a}")
        falhou |= bool(erros)
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
