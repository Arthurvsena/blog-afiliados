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

OBRIGATORIOS = ["titulo", "slug", "descricao", "palavra_chave", "tipo", "publicado", "atualizado"]
TIPOS = {"lista": 3, "comparativo": 2, "review": 1, "guia": 0, "noticia": 0, "analise": 0, "tutorial": 0}
TIPOS_COMPRA = ("lista", "comparativo", "review", "guia")
# "cheiro de IA": expressões proibidas pela voz do autor (editorial/voz.md)
CLICHES = [r"no cen[aá]rio atual", r"[eé] importante ressaltar", r"revolucion[aá]ri", r"em suma",
           r"vale destacar que", r"mergulh", r"jornada", r"desbloque\w* (todo )?o potencial",
           r"seja voc[eê] um", r"n[aã]o [eé] apenas", r"no mundo (atual )?da tecnologia", r"inovador",
           r"experi[eê]ncia do usu[aá]rio", r"fique ligad", r"comente abaixo"]
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
    editorias = {e["slug"] for e in cfg.get("editorias") or []}
    if meta.get("subnicho") and meta["subnicho"] not in subnichos:
        erros.append(f"subnicho '{meta['subnicho']}' não existe no config.yaml")
    if meta.get("editoria") and meta["editoria"] not in editorias:
        erros.append(f"editoria '{meta['editoria']}' não existe no config.yaml")
    tipo = meta.get("tipo")
    if tipo and tipo not in TIPOS:
        erros.append(f"tipo '{tipo}' inválido (use {', '.join(TIPOS)})")
    compra = tipo in TIPOS_COMPRA
    if compra and not meta.get("subnicho"):
        erros.append("posts do guia de compras precisam de 'subnicho'")
    if not compra and not meta.get("editoria"):
        erros.append("notícias, análises e tutoriais precisam de 'editoria'")
    if tipo == "noticia":
        fontes = [f for f in (meta.get("fontes") or []) if isinstance(f, dict) and str(f.get("url", "")).startswith("http")]
        if not fontes:
            erros.append("notícia sem 'fontes' (lista com nome e url de onde veio a informação)")

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
    if tipo != "noticia" and re.search(r"R\$\s?\d", texto):
        avisos.append("o texto cita preço em R$: prefira faixas ('até R$ 200') a preços exatos")

    abre = len(re.findall(r"^:::\s*\w+", corpo, re.M))
    fecha = len(re.findall(r"^:::\s*$", corpo, re.M))
    if abre != fecha:
        erros.append(f"blocos ::: desbalanceados ({abre} abertos, {fecha} fechados)")
    for bloco in re.findall(r"^:::\s*(\w+)", corpo, re.M):
        if bloco not in ("pros", "contras", "veredito", "dica", "atencao"):
            erros.append(f"bloco ':::{bloco}' não existe (use pros, contras, veredito, dica ou atencao)")
    texto = re.sub(r"^:::.*$", "", texto, flags=re.M)

    palavras = len(re.findall(r"\w+", texto))
    rot = cfg["rotina"]
    minimo = rot.get("palavras_minimas_noticia", 400) if tipo in ("noticia", "tutorial") else rot["palavras_minimas"]
    if palavras < minimo:
        erros.append(f"{palavras} palavras (mínimo {minimo})")
    if len(re.findall(r"^## ", corpo, re.M)) < (2 if tipo == "noticia" else 3):
        erros.append("use mais subtítulos H2 (##): 2 em notícias, 3 nos outros")
    # voz do autor
    achados = [c for c in CLICHES if re.search(c, texto, re.I)]
    if achados:
        avisos.append("voz: expressões com cheiro de IA: " + ", ".join(re.search(c, texto, re.I).group(0) for c in achados))
    if texto.count("—") > 3:
        avisos.append(f"voz: {texto.count('—')} travessões (—); prefira ponto ou vírgula")
    if tipo == "noticia" and not re.search(r"\b(segundo|de acordo com|afirmou|informou|confirmou|anunciou|em comunicado)\b", texto, re.I):
        avisos.append("notícia sem atribuição no texto ('segundo a empresa', 'em comunicado'...)")
    if re.search(r"^# ", corpo, re.M):
        erros.append("não use H1 (#) no corpo: o título já é o H1")
    chave = str(meta.get("palavra_chave", "")).lower()
    primeiro = corpo.strip().split("\n\n")[0].lower()
    if chave and not all(p in primeiro for p in chave.split()[:3]):
        avisos.append("a palavra-chave não aparece no primeiro parágrafo")
    if not meta.get("faq") and tipo != "noticia":
        avisos.append("sem FAQ no frontmatter")
    # SEO: palavra-chave real e bem posicionada
    import json as _json, unicodedata as _ud
    _n = lambda t: re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", _ud.normalize("NFKD", str(t).lower()).encode("ascii", "ignore").decode())).strip()
    arq_pal = RAIZ / "data" / "palavras.json"
    if chave and compra and arq_pal.exists():
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
    if compra and not meta.get("palavras_secundarias"):
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
