"""Mídia para os vídeos do canal: imagens oficiais de uma página e "prints" de notícias com o trecho destacado.

Uso (o roteirista roda antes de escrever as cenas):
  python3 scripts/midia.py imagens URL_OFICIAL [--n 8] [--baixar PASTA]
      Lista (e, com --baixar, salva para você olhar com Read) as imagens grandes de
      uma página oficial: og:image, twitter:image e <img> grandes. Use as boas no
      roteiro como "url:URL|Divulgação/Empresa".
  python3 scripts/midia.py manchete URL "trecho exato da matéria" SAIDA.png [--vertical]
      Tira um print da matéria (título + o parágrafo com o trecho) e grava ao lado
      SAIDA.json com a posição do trecho, para o vídeo animar o marca-texto.

Direito de citação (Lei 9.610/98, art. 46, III): mostramos só o título e um trecho
curto, sempre com o nome do veículo na tela e na descrição.
"""
import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"


def pegar(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"})
    return urllib.request.urlopen(req, timeout=timeout).read()


def imagens_da_pagina(url, n=10):
    pagina = pegar(url).decode("utf-8", "ignore")
    achados = []
    for prop in ("og:image", "og:image:secure_url", "twitter:image"):
        for m in re.finditer(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % re.escape(prop), pagina, re.I):
            achados.append(m.group(1))
        for m in re.finditer(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % re.escape(prop), pagina, re.I):
            achados.append(m.group(1))
    for m in re.finditer(r'<img[^>]+>', pagina, re.I):
        tag = m.group(0)
        src = None
        srcset = re.search(r'srcset=["\']([^"\']+)', tag)
        if srcset:
            partes = [p.strip().split(" ") for p in srcset.group(1).split(",") if p.strip()]
            partes.sort(key=lambda p: int(re.sub(r"\D", "", p[1]) or 0) if len(p) > 1 else 0)
            src = partes[-1][0]
        src = src or (re.search(r'(?:data-src|src)=["\']([^"\']+)', tag) or [None, None])[1]
        if not src or src.startswith("data:") or re.search(r"(logo|icon|sprite|avatar|pixel|badge)", src, re.I):
            continue
        larg = re.search(r'width=["\']?(\d+)', tag)
        if larg and int(larg.group(1)) < 500:
            continue
        achados.append(src)
    vistos, saida = set(), []
    for a in achados:
        a = urllib.parse.urljoin(url, html.unescape(a))
        if a not in vistos and re.search(r"\.(jpe?g|png|webp)(\?|$)|/image|images?/", a, re.I):
            vistos.add(a)
            saida.append(a)
    return saida[:n]


def capturar_manchete(url, trecho, saida, vertical=True):
    """Print do título + trecho da matéria, com a posição do trecho (para o marca-texto animado)."""
    from playwright.sync_api import sync_playwright
    saida = Path(saida)
    vp = {"width": 430, "height": 932} if vertical else {"width": 1100, "height": 900}
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport=vp, device_scale_factor=2.5 if vertical else 1.5, user_agent=UA, locale="pt-BR")
        pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        pg.wait_for_timeout(2500)
        info = pg.evaluate("""(trecho) => {
          // tira banners de cookie, pop-ups e barras fixas
          for (const el of document.querySelectorAll('body *')) {
            const s = getComputedStyle(el);
            if ((s.position === 'fixed' || s.position === 'sticky') && el.offsetHeight < innerHeight) el.remove();
          }
          document.querySelectorAll('[class*="cookie" i],[id*="cookie" i],[class*="consent" i],[class*="popup" i],[class*="modal" i],iframe,ins,[class*="ad-" i],[id*="ad-" i]').forEach(e => e.remove());
          document.querySelectorAll('figure,picture,img,video,svg[class*="ad" i],aside,nav,[class*="share" i],[class*="social" i],[class*="publicidade" i],[class*="banner" i],[class*="related" i]').forEach(e => e.remove());
          for (const el of document.querySelectorAll('article *, main *')) {
            const t = (el.innerText || '').trim().toLowerCase();
            if (el.children.length === 0 && /^(continua após a publicidade|publicidade|anúncio)$/.test(t)) el.remove();
            const s = getComputedStyle(el);
            if (el.offsetHeight > 30 && !(el.innerText || '').trim() && s.backgroundColor !== 'rgba(0, 0, 0, 0)') el.remove();
          }
          for (const el of document.querySelectorAll('body *')) {
            const b = el.getBoundingClientRect();
            if (b.width > 0 && b.width < 90 && b.left > innerWidth * 0.82) el.remove();
          }
          document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
          const h1 = document.querySelector('article h1, main h1, h1');
          const norm = t => t.replace(/\\s+/g, ' ').trim().toLowerCase();
          const alvoTxt = norm(trecho);
          let alvo = null;
          for (const el of document.querySelectorAll('article p, main p, p, li, h2')) {
            if (norm(el.innerText || '').includes(alvoTxt.slice(0, 60))) { alvo = el; break; }
          }
          let faixa = null;
          if (alvo) {
            // destaca só o trecho dentro do parágrafo
            const r = document.createRange();
            const walker = document.createTreeWalker(alvo, NodeFilter.SHOW_TEXT);
            let texto = '', nos = [];
            while (walker.nextNode()) { nos.push([walker.currentNode, texto.length]); texto += walker.currentNode.textContent; }
            const i = texto.toLowerCase().replace(/\\s+/g, ' ').indexOf(alvoTxt.slice(0, 60));
            const box = alvo.getBoundingClientRect();
            faixa = {x: box.left, y: box.top + scrollY, w: box.width, h: box.height};
            if (i >= 0) {
              // posição aproximada pelo começo e fim do trecho
              const achar = pos => { for (let k = nos.length - 1; k >= 0; k--) if (nos[k][1] <= pos) return [nos[k][0], Math.min(pos - nos[k][1], nos[k][0].textContent.length)]; return [nos[0][0], 0]; };
              const [n1, o1] = achar(i), [n2, o2] = achar(Math.min(i + alvoTxt.length, texto.length - 1));
              try { r.setStart(n1, o1); r.setEnd(n2, o2); const rs = [...r.getClientRects()].map(q => ({x: q.left, y: q.top + scrollY, w: q.width, h: q.height})); if (rs.length) faixa.linhas = rs; } catch (e) {}
            }
          }
          const t = h1 ? h1.getBoundingClientRect() : null;
          return {titulo: t ? {x: t.left, y: t.top + scrollY, w: t.width, h: t.height} : null, faixa,
                  site: location.hostname.replace(/^www\\./, ''), largura: innerWidth};
        }""", trecho)
        if not info["titulo"] and not info["faixa"]:
            nav.close()
            raise SystemExit("Não achei o título nem o trecho na página.")
        topo = max(0, (info["titulo"] or info["faixa"])["y"] - 24)
        fim_alvo = info["faixa"]["y"] + info["faixa"]["h"] if info["faixa"] else topo + 500
        fim = min(fim_alvo + 40, topo + (1500 if vertical else 900))
        clip = {"x": 0, "y": topo, "width": info["largura"], "height": max(300, fim - topo)}
        pg.screenshot(path=str(saida), clip=clip, full_page=True)
        nav.close()
    rel = lambda r: {"x": r["x"] / clip["width"], "y": (r["y"] - topo) / clip["height"], "w": r["w"] / clip["width"], "h": r["h"] / clip["height"]}
    linhas = [rel(q) for q in (info["faixa"] or {}).get("linhas", [])] or ([rel(info["faixa"])] if info["faixa"] else [])
    meta = {"arquivo": saida.name, "site": info["site"], "url": url, "proporcao": clip["width"] / clip["height"],
            "titulo": rel(info["titulo"]) if info["titulo"] else None,
            "destaque": [q for q in linhas if 0 <= q["y"] <= 1]}
    saida.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False))
    return meta


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("imagens"); a1.add_argument("url"); a1.add_argument("--n", type=int, default=8); a1.add_argument("--baixar")
    a2 = sub.add_parser("manchete"); a2.add_argument("url"); a2.add_argument("trecho"); a2.add_argument("saida")
    a2.add_argument("--vertical", action="store_true")
    a = ap.parse_args()
    if a.cmd == "imagens":
        urls = imagens_da_pagina(a.url, a.n)
        if a.baixar:
            Path(a.baixar).mkdir(parents=True, exist_ok=True)
        for i, u in enumerate(urls, 1):
            print(f"{i}. {u}")
            if a.baixar:
                try:
                    Path(a.baixar, f"cand-{i:02d}.jpg").write_bytes(pegar(u))
                except Exception as e:
                    print(f"   (não baixou: {e})")
        if not urls:
            print("Nenhuma imagem grande encontrada nessa página.")
    else:
        print(json.dumps(capturar_manchete(a.url, a.trecho, a.saida, a.vertical), ensure_ascii=False))


if __name__ == "__main__":
    main()
