"""Mídia para os vídeos do canal: imagens oficiais de uma página e "prints" de notícias com o trecho destacado.

Uso (o roteirista roda antes de escrever as cenas):
  python3 scripts/midia.py imagens URL_OFICIAL [--n 8] [--baixar PASTA]
      Lista (e, com --baixar, salva para você olhar com Read) as imagens grandes de
      uma página oficial: og:image, twitter:image e <img> grandes. Use as boas no
      roteiro como "url:URL|Divulgação/Empresa".
  python3 scripts/midia.py videos URL_OFICIAL
      Lista os vídeos (.mp4/.webm) de uma página oficial: trailer do jogo na Steam, página do
      produto, press kit. Use no roteiro como "video:URL|Vídeo: Empresa|SEGUNDO_INICIAL".
  python3 scripts/midia.py estoque "termos em inglês" SAIDA.mp4
      Busca um vídeo grátis no Pexels (precisa do segredo PEXELS_API_KEY). Roteiro: "estoque:termos".
  Gravação de tela nossa de uma página: no roteiro, "tela:URL" (rola a página por 9 s).
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


def videos_da_pagina(url, n=12):
    """Vídeos de uma página oficial (og:video, <video>/<source>, links .mp4/.webm, trailers da Steam)."""
    pagina = pegar(url).decode("utf-8", "ignore")
    achados = re.findall(r'<meta[^>]+(?:property|name)=["\'](?:og:video(?::secure_url|:url)?|twitter:player:stream)["\'][^>]+content=["\']([^"\']+)', pagina, re.I)
    achados += re.findall(r'<(?:video|source)[^>]+src=["\']([^"\']+)', pagina, re.I)
    achados += re.findall(r'(https?:[^"\'\s<>]+?\.(?:mp4|webm)(?:\?[^"\'\s<>]*)?)', pagina.replace("\\/", "/"))
    achados += re.findall(r'data-(?:mp4|webm)(?:-hd)?-source=["\']([^"\']+)', pagina, re.I)
    vistos, saida = set(), []
    for a in achados:
        a = urllib.parse.urljoin(url, html.unescape(a))
        if a not in vistos and not re.search(r"(logo|icon|sprite|loading)", a, re.I):
            vistos.add(a); saida.append(a)
    # Steam: os trailers ficam numa API pública da loja
    m = re.search(r"store\.steampowered\.com/app/(\d+)", url)
    if m:
        try:
            dados = json.loads(pegar(f"https://store.steampowered.com/api/appdetails?appids={m.group(1)}&l=brazilian"))
            for mv in (dados.get(m.group(1), {}).get("data", {}).get("movies") or []):
                us = [(mv.get(ch) or {}).get("max") or (mv.get(ch) or {}).get("480") for ch in ("mp4", "webm")]
                us.append(mv.get("hls_h264"))  # a Steam nova só entrega HLS/DASH: o ffmpeg lê o trecho direto
                for u in us:
                    if u and u not in vistos:
                        vistos.add(u); saida.append(u)
        except Exception:
            pass
    return saida[:n]


def _escala(vertical):
    # vídeo em pé: o trecho deitado inteiro (o Remotion põe o fundo desfocado); deitado: 1920 de largura
    return "scale='min(1920,iw)':-2" if not vertical else "scale='min(1280,iw)':-2"


_HLS_DESLOC = {}


def _baixar_hls(url, inicio, dur, vertical):
    mestre = pegar(url).decode()
    variantes = re.findall(r"RESOLUTION=(\d+)x(\d+)[^\n]*\n([^\n#]+)", mestre)
    if variantes:
        alvo = 1280 if vertical else 1920
        w, h, rel = min(variantes, key=lambda v: abs(int(v[0]) - alvo))
        url = urllib.parse.urljoin(url, rel.strip())
    lista = pegar(url).decode()
    dados = b""
    m = re.search(r'#EXT-X-MAP:URI="([^"]+)"', lista)
    if m:
        dados += pegar(urllib.parse.urljoin(url, m.group(1)))
    t, primeiro = 0.0, None
    for dur_seg, seg in re.findall(r"#EXTINF:([\d.]+),?[^\n]*\n([^\n#]+)", lista):
        fim = t + float(dur_seg)
        if fim > inicio and t < inicio + dur:
            if primeiro is None:
                primeiro = t
            dados += pegar(urllib.parse.urljoin(url, seg.strip()))
        t = fim
    _HLS_DESLOC["v"] = max(0.0, inicio - (primeiro or 0.0))
    return dados


def recortar_video(url, destino, inicio=0.0, dur=8.0, vertical=True):
    """Baixa só o trecho (sem som), em H.264 leve para o Remotion."""
    import subprocess
    tmp = Path(destino).with_suffix(".orig")
    if re.search(r"\.m3u8(\?|$)", url):
        # streaming HLS (trailers da Steam): baixa só os pedaços do trecho e junta
        tmp.write_bytes(_baixar_hls(url, inicio, dur, vertical))
        origem, inicio = str(tmp), _HLS_DESLOC.get("v", 0.0)
    else:
        tmp.write_bytes(pegar(url, timeout=120))
        origem = str(tmp)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(inicio), "-i", origem, "-t", str(dur), "-an",
                    "-vf", _escala(vertical) + ",fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destino)], check=True)
    tmp.unlink(missing_ok=True)
    quadro(destino)
    return destino


def quadro(video):
    """Um quadro do trecho (fundo desfocado do vídeo em pé)."""
    import subprocess
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", str(video), "-frames:v", "1", "-vf", "scale=640:-2",
                    str(Path(video).with_name(Path(video).stem + "-quadro.jpg"))], check=False)


def gravar_tela(url, destino, segundos=12, vertical=True):
    """Gravação de tela NOSSA: abre a página e rola devagar (vale para tutorial e para mostrar página oficial)."""
    import subprocess, shutil, tempfile
    from playwright.sync_api import sync_playwright
    vp = {"width": 540, "height": 960} if vertical else {"width": 1280, "height": 720}
    limpar = """() => {
      for (const el of document.querySelectorAll('[class*="cookie" i],[id*="cookie" i],[class*="consent" i],[id*="consent" i],[class*="onetrust" i],[id*="onetrust" i],[class*="modal" i],[class*="popup" i],[aria-modal="true"]')) el.remove();
      for (const el of document.querySelectorAll('body *')) {
        const s = getComputedStyle(el);
        if ((s.position === 'fixed' || s.position === 'sticky') && el.offsetHeight * el.offsetWidth > innerWidth * innerHeight * 0.25) el.remove();
      }
      document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
    }"""
    pasta = Path(tempfile.mkdtemp())
    with sync_playwright() as p:
        nav = p.chromium.launch()
        ctx = nav.new_context(viewport=vp, user_agent=UA, locale="pt-BR", record_video_dir=str(pasta), record_video_size=vp)
        pg = ctx.new_page()
        pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        pg.wait_for_timeout(2500)
        for _ in range(3):  # banners que aparecem depois
            try:
                pg.evaluate(limpar)
            except Exception:
                pass
            pg.wait_for_timeout(400)
        for passo in range(int(segundos * 10)):
            pg.mouse.wheel(0, 10)
            pg.wait_for_timeout(100)
            if passo % 15 == 0:
                try:
                    pg.evaluate(limpar)
                except Exception:
                    pass
        ctx.close(); nav.close()
    bruto = next(pasta.glob("*.webm"))
    escala = "scale=1080:1920:flags=lanczos" if vertical else "scale=1920:1080:flags=lanczos"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "3.6", "-i", str(bruto), "-t", str(segundos), "-an",
                    "-vf", escala + ",fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                    str(destino)], check=True)
    shutil.rmtree(pasta, ignore_errors=True)
    quadro(destino)
    return destino


def estoque_video(termos, destino, vertical=True):
    """Vídeo grátis do Pexels (licença Pexels: uso livre, sem atribuição obrigatória; damos crédito mesmo assim)."""
    import os
    chave = os.environ.get("PEXELS_API_KEY", "").strip()
    if not chave:
        raise RuntimeError("sem PEXELS_API_KEY: use video: (oficial) ou tela: (gravação nossa)")
    req = urllib.request.Request("https://api.pexels.com/videos/search?per_page=5&orientation=" +
                                 ("portrait" if vertical else "landscape") + "&query=" + urllib.parse.quote(termos),
                                 headers={"Authorization": chave, "User-Agent": UA})
    dados = json.loads(urllib.request.urlopen(req, timeout=30).read())
    for v in dados.get("videos", []):
        arqs = sorted([f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and (f.get("width") or 0) <= 1920],
                      key=lambda f: -(f.get("width") or 0))
        if arqs:
            recortar_video(arqs[0]["link"], destino, 0, 8, vertical)
            return f"Vídeo: {v.get('user', {}).get('name', 'autor')}/Pexels"
    raise RuntimeError(f"nada no Pexels para '{termos}'")


def proporcao(arquivo):
    import subprocess
    try:
        saida = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                "-of", "csv=p=0", str(arquivo)], capture_output=True, text=True).stdout.strip()
        w, h = (int(x) for x in saida.split(",")[:2])
        return round(w / h, 3)
    except Exception:
        return 1.78


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
    a3 = sub.add_parser("videos"); a3.add_argument("url")
    a4 = sub.add_parser("estoque"); a4.add_argument("termos"); a4.add_argument("saida")
    a2 = sub.add_parser("manchete"); a2.add_argument("url"); a2.add_argument("trecho"); a2.add_argument("saida")
    a2.add_argument("--vertical", action="store_true")
    a = ap.parse_args()
    if a.cmd == "videos":
        urls = videos_da_pagina(a.url)
        print("\n".join(f"{i}. {u}" for i, u in enumerate(urls, 1)) or "Nenhum vídeo nessa página.")
        return
    if a.cmd == "estoque":
        print(estoque_video(a.termos, a.saida))
        return
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
