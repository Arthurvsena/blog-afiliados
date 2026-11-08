"""Gera a identidade visual do canal (avatar e banner) no mesmo estilo 2D dos vídeos."""
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
JS = r"""
() => {
  const out = {};
  function base(c, w, h, solY) {
    const g = c.createLinearGradient(0, 0, 0, h);
    [[0, "#2c1a45"], [0.38, "#8a3c5a"], [0.62, "#f08a4b"], [0.78, "#f8c76a"], [1, "#f8c76a"]].forEach(([o, k]) => g.addColorStop(o, k));
    c.fillStyle = g; c.fillRect(0, 0, w, h);
    const r = c.createRadialGradient(w / 2, solY, 0, w / 2, solY, h * 0.6);
    r.addColorStop(0, "rgba(255,230,160,0.9)"); r.addColorStop(1, "rgba(255,230,160,0)");
    c.fillStyle = r; c.fillRect(0, 0, w, h);
  }
  // AVATAR 800x800
  let cv = document.createElement("canvas"); cv.width = 800; cv.height = 800; let c = cv.getContext("2d");
  base(c, 800, 800, 520);
  c.fillStyle = "#fff3cf"; c.beginPath(); c.arc(400, 520, 190, 0, 6.283); c.fill();
  c.fillStyle = "#7a3a44"; c.beginPath(); c.moveTo(0, 800); for (let x = 0; x <= 800; x += 10) c.lineTo(x, 600 + Math.sin(x * 0.008 + 1) * 25); c.lineTo(800, 800); c.fill();
  c.fillStyle = "#2a1626"; c.beginPath(); c.moveTo(0, 800); for (let x = 0; x <= 800; x += 10) c.lineTo(x, 660 + Math.sin(x * 0.012 + 3) * 18); c.lineTo(800, 800); c.fill();
  palmeira(c, 120, 690, 300, "#2a1626", 0); palmeira(c, 700, 700, 260, "#2a1626", 1);
  pessoa(c, 400, 700, 340, { tunica: "listras", bracoE: 2.55, bracoD: 2.5, olhar: 1 });
  out.avatar = cv.toDataURL("image/png");
  // BANNER 2560x1440 (área segura 1546x423 no centro)
  cv = document.createElement("canvas"); cv.width = 2560; cv.height = 1440; c = cv.getContext("2d");
  base(c, 2560, 1440, 900);
  c.fillStyle = "#fff3cf"; c.beginPath(); c.arc(1280, 930, 230, 0, 6.283); c.fill();
  const duna = (y0, amp, f, ph, cor) => { c.fillStyle = cor; c.beginPath(); c.moveTo(0, 1440); for (let x = 0; x <= 2560; x += 16) c.lineTo(x, y0 + Math.sin(x * f + ph) * amp); c.lineTo(2560, 1440); c.fill(); };
  duna(940, 40, 0.003, 1, "#7a3a44"); duna(1010, 30, 0.005, 3, "#4a2233");
  for (let i = 0; i < 3; i++) { camelo(c, 300 + i * 230, 1020, 190, i, "#160d1c"); }
  pessoa(c, 980, 1020, 180, { cabeca: "pano", cajado: true, bracoE: 0.2, bracoD: 0.1, cor: "#160d1c" });
  palmeira(c, 2250, 1030, 380, "#160d1c", 0); palmeira(c, 2420, 1040, 300, "#160d1c", 1);
  c.fillStyle = "#2a1626"; c.fillRect(0, 1015, 2560, 430);
  pessoa(c, 2000, 1020, 230, { tunica: "listras", bracoE: 2.5, bracoD: 2.55, olhar: -1 });
  c.textAlign = "center"; c.shadowColor = "rgba(0,0,0,0.5)"; c.shadowBlur = 30;
  c.font = "700 150px Poppins"; c.fillStyle = "#ffffff"; c.fillText("Bíblia Animada", 1280, 690);
  c.font = "700 54px Poppins"; c.fillStyle = "#ffe08a"; c.fillText("HISTÓRIAS DA BÍBLIA EM ANIMAÇÃO • UMA NOVA TODO DIA", 1280, 780);
  out.banner = cv.toDataURL("image/png");
  return out;
}
"""
with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page()
    pg.goto((AQUI.parent / "animacao" / "cenas.html").as_uri())
    pg.evaluate("() => window.pronto")
    res = pg.evaluate(JS)
    for nome, dados in res.items():
        (AQUI / f"{nome}.png").write_bytes(base64.b64decode(dados.split(",", 1)[1]))
        print(AQUI / f"{nome}.png")
    nav.close()
