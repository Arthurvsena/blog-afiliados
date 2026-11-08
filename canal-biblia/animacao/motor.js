/* ==========================================================================
   Motor de cenas da Bíblia Animada.
   Uma cena do roteiro descreve: cenário + hora + câmera + elementos + efeitos.
   Assim, uma história nova não precisa de código novo: só de um roteiro JSON.
   Catálogo completo (o que o roteirista pode usar): canal-biblia/CATALOGO.md
   Depende das funções de cenas.html (pessoa, camelo, glow, sky, duna, ...).
   ========================================================================== */

// ---------- paletas por hora do dia ----------
const HORAS = {
  por_do_sol: { ceu: [[0, "#2c1a45"], [0.35, "#8a3c5a"], [0.6, "#f08a4b"], [0.75, "#f8c76a"], [1, "#f8c76a"]], sol: { y: 1180, r: 150, cor: "#fff3cf", luz: "rgba(255,220,140,0.8)" },
                longe: "#7a3a44", perto: "#4a2233", chao: "#2a1626", sil: "#160d1c", tom: "rgba(255,170,90,0.0)" },
  dia:        { ceu: [[0, "#3f6fae"], [0.45, "#8fb9df"], [0.75, "#f1dfb8"], [1, "#f1dfb8"]], sol: { x: 830, y: 560, r: 80, cor: "#fffbe8", luz: "rgba(255,250,220,0.65)" },
                longe: "#a7865e", perto: "#7a5a3c", chao: "#4a3324", sil: "#1c1210", tom: "rgba(0,0,0,0)" },
  amanhecer:  { ceu: [[0, "#1b2240"], [0.4, "#6a4a7a"], [0.62, "#f2a07a"], [0.78, "#ffe0a8"], [1, "#ffe0a8"]], sol: { y: 1250, r: 130, cor: "#fff1d0", luz: "rgba(255,210,160,0.75)" },
                longe: "#6a4a6a", perto: "#3e2a44", chao: "#22152a", sil: "#140c1a", tom: "rgba(0,0,0,0)" },
  noite:      { ceu: [[0, "#04071a"], [0.5, "#0e1838"], [1, "#1c2a55"]], lua: { x: 780, y: 420, r: 70 },
                longe: "#1a2444", perto: "#101830", chao: "#070a16", sil: "#04060e", tom: "rgba(0,0,0,0)" },
  tempestade: { ceu: [[0, "#06080f"], [0.5, "#141a26"], [1, "#2a3240"]],
                longe: "#1a1f2a", perto: "#10141c", chao: "#080a10", sil: "#04050a", tom: "rgba(0,0,0,0)" },
};

const PLANOS = {
  fundo:  { chao: 1200, h: 210, escuro: 0.0 },
  meio:   { chao: 1380, h: 400, escuro: 0.0 },
  frente: { chao: 2000, h: 920, escuro: 0.5 },
};

// mistura duas cores hex (t = quanto da segunda)
function mix(a, b, t) {
  const p = h => [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
  const A = p(a), B = p(b);
  return "#" + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, "0")).join("");
}
// a túnica do herói usa as cores do roteiro (campo "heroi.cores")
function definirHeroi(h) { if (h && h.cores && h.cores.length) TUNICA.splice(0, TUNICA.length, ...h.cores); }

// ---------- fundos ----------
function estrelas(c, t, n = 140) {
  const r = rng(77); c.save();
  for (let i = 0; i < n; i++) { const x = r() * W, y = r() * 1100, s = 1 + r() * 2.2; c.globalAlpha = 0.35 + 0.65 * Math.abs(Math.sin(t * (0.5 + r()) + i)); c.fillStyle = "#fff"; c.beginPath(); c.arc(x, y, s, 0, 6.283); c.fill(); }
  c.restore();
}
function nuvens(c, t, cor, y0 = 300, n = 6, vel = 8) {
  const r = rng(31); c.save(); c.fillStyle = cor;
  for (let i = 0; i < n; i++) {
    const x = ((r() * (W + 600) + t * vel * (0.5 + r())) % (W + 600)) - 300, y = y0 + r() * 500, s = 120 + r() * 160;
    c.beginPath(); c.ellipse(x, y, s, s * 0.35, 0, 0, 6.283); c.ellipse(x + s * 0.5, y - s * 0.15, s * 0.6, s * 0.3, 0, 0, 6.283); c.ellipse(x - s * 0.5, y + s * 0.05, s * 0.55, s * 0.25, 0, 0, 6.283); c.fill();
  }
  c.restore();
}
function astro(c, pal) {
  if (pal.sol) { const sx = pal.sol.x || 540; glow(c, sx, pal.sol.y, pal.sol.r * 3.2, pal.sol.luz); c.fillStyle = pal.sol.cor; c.beginPath(); c.arc(sx, pal.sol.y, pal.sol.r, 0, 6.283); c.fill(); }
  if (pal.lua) { glow(c, pal.lua.x, pal.lua.y, 260, "rgba(170,195,255,0.45)"); c.fillStyle = "#e8eeff"; c.beginPath(); c.arc(pal.lua.x, pal.lua.y, pal.lua.r, 0, 6.283); c.fill(); c.fillStyle = "rgba(10,16,40,0.95)"; c.beginPath(); c.arc(pal.lua.x + 28, pal.lua.y - 12, pal.lua.r * 0.92, 0, 6.283); c.fill(); }
}
function predio(c, x, y, w, h, cor) { c.fillStyle = cor; c.fillRect(x, y - h, w, h); for (let i = 0; i < w; i += 30) c.fillRect(x + i, y - h - 18, 18, 18); }

const CENARIOS = {
  deserto(c, t, pal) {
    astro(c, pal);
    duna(c, 1260, 34, 0.004, 1 + t * 0.03, pal.longe);
    duna(c, 1340, 24, 0.006, 3 + t * 0.06, pal.perto);
    c.fillStyle = pal.chao; c.fillRect(0, 1375, W, H);
    palmeira(c, 960, 1380, 360, pal.perto, t);
  },
  campo(c, t, pal) {
    astro(c, pal);
    const verde = (a, b) => mix(a, b, 0.3);
    duna(c, 1240, 60, 0.003, 2, verde(pal.longe, "#3d6b3a"));
    duna(c, 1320, 40, 0.005, 5, verde(pal.perto, "#2c4f2a"));
    c.fillStyle = verde(pal.chao, "#1e3a1e"); c.fillRect(0, 1375, W, H);
    for (const [x, h] of [[120, 300], [930, 360]]) { c.fillStyle = verde(pal.perto, "#1e3a1e"); c.fillRect(x - 12, 1380 - h * 0.45, 24, h * 0.45); c.beginPath(); c.arc(x, 1380 - h * 0.6, h * 0.28, 0, 6.283); c.arc(x - h * 0.15, 1380 - h * 0.5, h * 0.2, 0, 6.283); c.arc(x + h * 0.16, 1380 - h * 0.5, h * 0.2, 0, 6.283); c.fill(); }
  },
  cidade(c, t, pal) {
    astro(c, pal);
    duna(c, 1300, 20, 0.004, 1, pal.longe);
    const cor = pal.perto;
    predio(c, 60, 1330, 180, 260, cor); predio(c, 260, 1330, 120, 380, cor); predio(c, 690, 1330, 140, 340, cor); predio(c, 850, 1330, 190, 240, cor);
    c.fillStyle = cor; c.fillRect(0, 1180, W, 160);
    for (let i = 0; i < W; i += 40) c.fillRect(i, 1158, 24, 24);
    c.fillStyle = pal.chao; c.beginPath(); c.moveTo(450, 1340); c.lineTo(450, 1240); c.quadraticCurveTo(540, 1160, 630, 1240); c.lineTo(630, 1340); c.fill();
    c.fillStyle = pal.chao; c.fillRect(0, 1338, W, H);
  },
  palacio(c, t) {
    c.fillStyle = grad(c, 0, 0, 0, H, [[0, "#2a1408"], [0.5, "#6b3a12"], [1, "#2a1408"]]); c.fillRect(0, 0, W, H);
    for (const cx of [110, 970]) { c.fillStyle = "#1b0d06"; c.fillRect(cx - 70, 200, 140, 1300); c.fillStyle = "#8a5a1c"; for (let i = 0; i < 6; i++) c.fillRect(cx - 70, 260 + i * 200, 140, 10); }
    glow(c, 540, 1000, 520, "rgba(255,170,70,0.45)");
    c.fillStyle = "#3a1e0c"; c.fillRect(0, 1380, W, H);
    c.fillStyle = "rgba(240,180,80,0.35)"; c.fillRect(0, 1380, W, 6);
  },
  templo(c, t, pal) {
    astro(c, pal);
    c.fillStyle = pal.longe; c.beginPath(); c.moveTo(160, 760); c.lineTo(540, 600); c.lineTo(920, 760); c.fill();
    c.fillRect(170, 760, 740, 40);
    for (let i = 0; i < 7; i++) { c.fillRect(200 + i * 108, 800, 46, 420); }
    c.fillStyle = pal.perto; c.fillRect(120, 1220, 840, 50); c.fillRect(70, 1270, 940, 50); c.fillRect(20, 1320, 1040, 60);
    c.fillStyle = pal.chao; c.fillRect(0, 1378, W, H);
  },
  prisao(c, t, pal) {
    c.fillStyle = grad(c, 0, 0, 0, H, [[0, "#0a1024"], [1, "#05070f"]]); c.fillRect(0, 0, W, H);
    for (let row = 0; row < 30; row++) for (let col = 0; col < 8; col++) { const x = col * 150 - (row % 2) * 75, y = 300 + row * 62; c.fillStyle = (row * 7 + col * 3) % 5 ? "#141c34" : "#18213d"; c.beginPath(); c.roundRect(x + 3, y + 3, 144, 56, 8); c.fill(); }
    c.fillStyle = "#cfe0ff"; c.fillRect(640, 560, 200, 150); glow(c, 740, 635, 260, "rgba(160,190,255,0.6)");
    c.fillStyle = "#0a0f20"; for (let i = 0; i < 4; i++) c.fillRect(660 + i * 50, 560, 14, 150);
    c.save(); c.globalCompositeOperation = "lighter"; c.fillStyle = grad(c, 0, 600, 0, 1450, [[0, "rgba(150,180,255,0.32)"], [1, "rgba(150,180,255,0.03)"]]);
    c.beginPath(); c.moveTo(640, 600); c.lineTo(840, 600); c.lineTo(620, 1400); c.lineTo(260, 1400); c.fill(); c.restore();
    c.fillStyle = "#070a16"; c.fillRect(0, 1378, W, H);
  },
  cova(c, t, pal) {
    c.fillStyle = "#0b0706"; c.fillRect(0, 0, W, H);
    c.fillStyle = grad(c, 0, 0, 0, 700, [[0, "#ffe6b0"], [1, "#e09a50"]]); c.beginPath(); c.ellipse(540, 330, 260, 150, 0, 0, 6.283); c.fill();
    glow(c, 540, 330, 500, "rgba(255,210,150,0.5)");
    c.save(); c.globalCompositeOperation = "lighter"; c.fillStyle = grad(c, 0, 350, 0, 1380, [[0, "rgba(255,210,150,0.35)"], [1, "rgba(255,210,150,0.03)"]]);
    c.beginPath(); c.moveTo(330, 380); c.lineTo(750, 380); c.lineTo(860, 1380); c.lineTo(220, 1380); c.fill(); c.restore();
    c.fillStyle = "#1a0f0b"; for (let i = 0; i < 9; i++) { const r = rng(i + 5); c.beginPath(); c.ellipse(r() * W, 500 + r() * 800, 90 + r() * 120, 60 + r() * 80, 0, 0, 6.283); c.fill(); }
    c.fillStyle = "#120a07"; c.fillRect(0, 1378, W, H);
  },
  mar(c, t, pal, cena) {
    astro(c, pal);
    const forte = cena.tempestade ? 1 : 0;
    const agua = cena.tempestade ? ["#1a2433", "#0c121c", "#05080e"] : [pal.longe, pal.perto, pal.chao];
    for (let k = 0; k < 3; k++) {
      c.fillStyle = agua[k]; c.beginPath(); c.moveTo(-20, H);
      const y0 = 1240 + k * 120, amp = (10 + k * 10) * (1 + forte * 3.5);
      for (let x = -20; x <= W + 20; x += 15) c.lineTo(x, y0 + Math.sin(x * 0.012 + t * (1.2 + k * 0.6) * (1 + forte)) * amp + Math.sin(x * 0.031 - t * 1.7) * amp * 0.4);
      c.lineTo(W + 20, H); c.fill();
    }
  },
  monte(c, t, pal) {
    astro(c, pal);
    glow(c, 540, 520, 420, "rgba(255,235,190,0.7)");
    c.fillStyle = pal.longe; c.beginPath(); c.moveTo(-50, 1380); c.lineTo(380, 700); c.lineTo(540, 520); c.lineTo(700, 720); c.lineTo(1130, 1380); c.fill();
    c.fillStyle = pal.perto; c.beginPath(); c.moveTo(-50, 1380); c.lineTo(200, 1060); c.lineTo(420, 1380); c.fill(); c.beginPath(); c.moveTo(640, 1380); c.lineTo(900, 1000); c.lineTo(1130, 1380); c.fill();
    c.fillStyle = pal.chao; c.fillRect(0, 1378, W, H);
  },
  jardim(c, t, pal) {
    astro(c, pal);
    duna(c, 1280, 40, 0.004, 2, mix(pal.longe, "#2f5a32", 0.35));
    c.fillStyle = mix(pal.chao, "#183a1c", 0.3); c.fillRect(0, 1375, W, H);
    for (const [x, h] of [[90, 420], [300, 300], [800, 340], [1000, 460]]) { c.fillStyle = mix(pal.perto, "#183a1c", 0.4); c.fillRect(x - 14, 1380 - h * 0.5, 28, h * 0.5); c.beginPath(); c.arc(x, 1380 - h * 0.62, h * 0.3, 0, 6.283); c.arc(x - h * 0.18, 1380 - h * 0.5, h * 0.22, 0, 6.283); c.arc(x + h * 0.18, 1380 - h * 0.5, h * 0.22, 0, 6.283); c.fill(); }
    c.save(); c.globalAlpha = 0.5; c.fillStyle = "#8fc0e0"; c.beginPath(); c.ellipse(540, 1520, 600, 40, 0, 0, 6.283); c.fill(); c.restore();
  },
  mar_aberto(c, t, pal, cena) {   // o mar dividido em duas paredes de água
    astro(c, pal);
    const ab = cena._k != null ? easeOut(seg(cena._k, cena.abre_em ?? 0.1, (cena.abre_em ?? 0.1) + 0.35)) : 1;
    c.fillStyle = pal.chao; c.fillRect(0, 1240, W, H);
    c.fillStyle = "#c9a46a"; c.beginPath(); c.moveTo(540 - 60 - ab * 160, 1240); c.lineTo(540 + 60 + ab * 160, 1240); c.lineTo(540 + 120 + ab * 420, H); c.lineTo(540 - 120 - ab * 420, H); c.fill();
    for (const s of [-1, 1]) {
      const borda = 540 + s * (60 + ab * 160), borda2 = 540 + s * (120 + ab * 420);
      c.fillStyle = grad(c, 0, 600, 0, H, [[0, "#3a7fb0"], [0.5, "#1d4f7a"], [1, "#0d2a44"]]);
      c.beginPath(); c.moveTo(s < 0 ? -20 : W + 20, 1240 - 700 * ab); c.lineTo(borda + s * Math.sin(t * 2) * 8, 1240 - 640 * ab);
      c.lineTo(borda2, H); c.lineTo(s < 0 ? -20 : W + 20, H); c.fill();
      c.strokeStyle = "rgba(220,240,255,0.55)"; c.lineWidth = 6; c.beginPath();
      for (let y = 1240 - 640 * ab; y < H; y += 30) c.lineTo(lerp(borda, borda2, (y - (1240 - 640 * ab)) / (H - (1240 - 640 * ab))) + s * Math.sin(y * 0.05 + t * 4) * 6, y);
      c.stroke();
    }
  },
  ventre(c, t) {   // dentro do grande peixe
    c.fillStyle = rgrad(c, 540, 1000, 50, 1100, [[0, "#5a1d1d"], [0.6, "#2a0b0d"], [1, "#0c0304"]]); c.fillRect(0, 0, W, H);
    c.strokeStyle = "rgba(255,150,140,0.12)"; c.lineWidth = 30;
    for (let i = 0; i < 9; i++) { c.beginPath(); c.ellipse(540, 1000, 300 + i * 90 + Math.sin(t * 1.5) * 10, 700 + i * 60, 0, 0, 6.283); c.stroke(); }
    c.fillStyle = "rgba(60,90,120,0.6)"; c.fillRect(0, 1420, W, 500);
  },
  ceu(c, t) {
    c.save(); c.translate(540, 1100); c.rotate(t * 0.05); c.globalCompositeOperation = "lighter";
    for (let i = 0; i < 18; i++) { c.rotate(Math.PI / 9); c.fillStyle = "rgba(255,230,170,0.07)"; c.beginPath(); c.moveTo(0, 0); c.lineTo(-90, -1600); c.lineTo(90, -1600); c.fill(); }
    c.restore();
    glow(c, 540, 1100, 650, "rgba(255,235,190,0.85)");
    nuvens(c, t, "rgba(255,240,220,0.35)", 1150, 7, 6);
    c.fillStyle = "rgba(255,240,225,0.55)"; for (let i = 0; i < 6; i++) { c.beginPath(); c.ellipse(i * 220, 1420, 260, 110, 0, 0, 6.283); c.fill(); }
  },
  interior(c, t) {
    c.fillStyle = grad(c, 0, 0, 0, H, [[0, "#1a0f0a"], [1, "#2e1a10"]]); c.fillRect(0, 0, W, H);
    c.fillStyle = "#24150d"; c.fillRect(0, 300, W, 1100);
    c.fillStyle = "#0d0806"; c.fillRect(700, 520, 220, 280); c.fillStyle = "#1f2a50"; c.fillRect(715, 535, 190, 250);
    glow(c, 300, 820, 380, "rgba(255,180,90,0.55)");
    c.fillStyle = "#ffd27a"; c.beginPath(); c.ellipse(300, 860, 12, 22 + Math.sin(t * 9) * 3, 0, 0, 6.283); c.fill();
    c.fillStyle = "#3a2214"; c.fillRect(270, 880, 60, 20);
    c.fillStyle = "#140c08"; c.fillRect(0, 1378, W, H);
  },
};

// ---------- elementos ----------
function corPlano(pal, plano, base) { return plano === "frente" ? "#0b060c" : plano === "fundo" ? pal.perto : (base || pal.sil); }

function asas(c, x, y, h, t) {
  c.save(); c.globalCompositeOperation = "lighter"; c.fillStyle = "rgba(255,245,220,0.55)";
  for (const s of [-1, 1]) { c.save(); c.translate(x + s * h * 0.06, y - h * 0.72); c.rotate(s * (0.5 + Math.sin(t * 2.4) * 0.12)); c.beginPath(); c.ellipse(s * h * 0.2, -h * 0.05, h * 0.26, h * 0.09, s * 0.4, 0, 6.283); c.fill(); c.restore(); }
  c.restore();
}

function leao(c, x, y, s, t, cor) {
  c.fillStyle = cor; c.strokeStyle = cor; c.lineWidth = s * 0.07; c.lineCap = "round";
  for (const lx of [-0.32, -0.2, 0.22, 0.34]) { c.beginPath(); c.moveTo(x + lx * s, y - s * 0.32); c.lineTo(x + lx * s + Math.sin(t * 3 + lx * 9) * 3, y); c.stroke(); }
  c.beginPath(); c.ellipse(x, y - s * 0.42, s * 0.42, s * 0.16, 0, 0, 6.283); c.fill();
  c.beginPath(); c.moveTo(x - s * 0.4, y - s * 0.45); c.quadraticCurveTo(x - s * 0.65, y - s * 0.6 + Math.sin(t * 2) * 8, x - s * 0.62, y - s * 0.3); c.stroke();
  c.beginPath(); c.arc(x + s * 0.42, y - s * 0.55, s * 0.2, 0, 6.283); c.fill();             // juba
  c.beginPath(); c.ellipse(x + s * 0.56, y - s * 0.52, s * 0.11, s * 0.08, 0, 0, 6.283); c.fill();
}
function ovelha(c, x, y, s, t) {
  c.fillStyle = "#e9e2d2"; c.strokeStyle = "#2a2020"; c.lineWidth = s * 0.07;
  for (const lx of [-0.2, -0.08, 0.1, 0.22]) { c.beginPath(); c.moveTo(x + lx * s, y - s * 0.25); c.lineTo(x + lx * s, y); c.stroke(); }
  for (const [ox, oy, r] of [[-0.18, -0.4, 0.17], [0, -0.45, 0.19], [0.17, -0.4, 0.17], [-0.08, -0.32, 0.17], [0.1, -0.32, 0.17]]) { c.beginPath(); c.arc(x + ox * s, y + oy * s, r * s, 0, 6.283); c.fill(); }
  c.fillStyle = "#2a2020"; c.beginPath(); c.ellipse(x + s * 0.34, y - s * 0.45 + Math.sin(t * 2 + x) * 2, s * 0.1, s * 0.08, 0.3, 0, 6.283); c.fill();
}
function porco(c, x, y, s, t, cor) {
  c.fillStyle = cor || "#3a2a2a"; c.strokeStyle = c.fillStyle; c.lineWidth = s * 0.07;
  for (const lx of [-0.2, -0.1, 0.14, 0.24]) { c.beginPath(); c.moveTo(x + lx * s, y - s * 0.2); c.lineTo(x + lx * s, y); c.stroke(); }
  c.beginPath(); c.ellipse(x, y - s * 0.33, s * 0.34, s * 0.17, 0, 0, 6.283); c.fill();
  c.beginPath(); c.ellipse(x + s * 0.36, y - s * 0.34 + Math.sin(t * 3 + x) * 2, s * 0.12, s * 0.1, 0, 0, 6.283); c.fill();
}
function peixeGrande(c, x, y, s, t, cor, boca = 0) {
  c.fillStyle = cor;
  c.beginPath(); c.ellipse(x, y, s * 0.6, s * 0.25, 0, 0, 6.283); c.fill();
  c.beginPath(); c.moveTo(x - s * 0.55, y); c.lineTo(x - s * 0.95, y - s * 0.28 + Math.sin(t * 3) * 10); c.lineTo(x - s * 0.9, y + s * 0.22 + Math.sin(t * 3) * 10); c.fill();
  if (boca > 0) { c.fillStyle = "#05070c"; c.beginPath(); c.moveTo(x + s * 0.62, y); c.lineTo(x + s * 0.3, y - s * 0.03); c.lineTo(x + s * 0.62, y + s * 0.18 * boca); c.fill(); }
  c.fillStyle = "rgba(255,255,255,0.7)"; c.beginPath(); c.arc(x + s * 0.4, y - s * 0.08, s * 0.025, 0, 6.283); c.fill();
}
function pomba(c, x, y, s, t) {
  c.fillStyle = "#fbf7ee"; glow(c, x, y, s * 1.4, "rgba(255,250,230,0.5)");
  c.beginPath(); c.ellipse(x, y, s * 0.3, s * 0.12, 0, 0, 6.283); c.fill();
  c.beginPath(); c.arc(x + s * 0.3, y - s * 0.08, s * 0.09, 0, 6.283); c.fill();
  const a = Math.sin(t * 9) * 0.8;
  for (const sg of [-1, 1]) { c.save(); c.translate(x, y - s * 0.05); c.rotate(-sg * 0.2 + a * sg * -0.5); c.beginPath(); c.ellipse(0, -s * 0.22, s * 0.12, s * 0.3, 0.3, 0, 6.283); c.fill(); c.restore(); }
}
function cobra(c, x, y, s, t, cor) {
  c.strokeStyle = cor; c.lineWidth = s * 0.08; c.lineCap = "round"; c.beginPath();
  for (let i = 0; i <= 30; i++) { const k = i / 30; const px = x - s * 0.6 + k * s * 1.2, py = y - Math.sin(k * 9 + t * 4) * s * 0.08 - (k > 0.85 ? (k - 0.85) * s * 2 : 0); i ? c.lineTo(px, py) : c.moveTo(px, py); }
  c.stroke(); c.fillStyle = cor; c.beginPath(); c.ellipse(x + s * 0.62, y - s * 0.32, s * 0.08, s * 0.05, 0, 0, 6.283); c.fill();
}
function barco(c, x, y, s, t, cor, tempestade) {
  const bal = Math.sin(t * (tempestade ? 2.4 : 1.2)) * (tempestade ? 0.14 : 0.04);
  c.save(); c.translate(x, y); c.rotate(bal); c.fillStyle = cor;
  c.beginPath(); c.moveTo(-s * 0.55, -s * 0.12); c.lineTo(s * 0.55, -s * 0.12); c.lineTo(s * 0.4, s * 0.08); c.lineTo(-s * 0.4, s * 0.08); c.fill();
  c.fillRect(-s * 0.015, -s * 0.75, s * 0.03, s * 0.65);
  c.beginPath(); c.moveTo(0, -s * 0.72); c.quadraticCurveTo(s * 0.32 + Math.sin(t * 3) * 6, -s * 0.45, 0, -s * 0.18); c.fill();
  c.restore();
}
function arca(c, x, y, s, cor) {
  c.fillStyle = cor;
  c.beginPath(); c.moveTo(x - s * 0.6, y - s * 0.25); c.lineTo(x + s * 0.6, y - s * 0.25); c.lineTo(x + s * 0.48, y); c.lineTo(x - s * 0.48, y); c.fill();
  c.fillRect(x - s * 0.4, y - s * 0.45, s * 0.8, s * 0.2);
  c.beginPath(); c.moveTo(x - s * 0.45, y - s * 0.45); c.lineTo(x, y - s * 0.6); c.lineTo(x + s * 0.45, y - s * 0.45); c.fill();
  c.fillStyle = "rgba(255,210,140,0.7)"; c.fillRect(x - s * 0.05, y - s * 0.4, s * 0.1, s * 0.08);
}
function fogo(c, x, y, s, t) {
  glow(c, x, y - s * 0.4, s * 1.4, "rgba(255,150,60,0.75)");
  for (let i = 0; i < 6; i++) {
    const ph = t * 8 + i * 1.7, hh = s * (0.6 + 0.25 * Math.sin(ph)), ww = s * (0.25 - i * 0.025);
    c.fillStyle = ["#ff6a2a", "#ff8c34", "#ffb347", "#ffd36a", "#fff0b0", "#ffffff"][i];
    c.beginPath(); c.moveTo(x - ww, y); c.quadraticCurveTo(x - ww * 0.8, y - hh * 0.6, x + Math.sin(ph) * ww * 0.3, y - hh); c.quadraticCurveTo(x + ww * 0.8, y - hh * 0.6, x + ww, y); c.fill();
  }
}
function tabuas(c, x, y, s) {
  glow(c, x, y - s * 0.4, s * 1.2, "rgba(255,240,200,0.7)");
  for (const dx of [-0.2, 0.2]) { c.fillStyle = "#cfc5b0"; c.beginPath(); c.roundRect(x + dx * s - s * 0.18, y - s * 0.75, s * 0.36, s * 0.7, [s * 0.18, s * 0.18, 6, 6]); c.fill(); c.fillStyle = "rgba(60,40,30,0.5)"; for (let k = 0; k < 5; k++) c.fillRect(x + dx * s - s * 0.12, y - s * 0.5 + k * s * 0.08, s * 0.24, s * 0.02); }
}
function cruz(c, x, y, s, cor) { c.fillStyle = cor; c.fillRect(x - s * 0.04, y - s, s * 0.08, s); c.fillRect(x - s * 0.3, y - s * 0.78, s * 0.6, s * 0.07); }
function tumulo(c, x, y, s, cor, aberto) {
  c.fillStyle = cor; c.beginPath(); c.moveTo(x - s * 0.7, y); c.quadraticCurveTo(x - s * 0.65, y - s * 0.7, x, y - s * 0.72); c.quadraticCurveTo(x + s * 0.65, y - s * 0.7, x + s * 0.7, y); c.fill();
  c.fillStyle = "#050305"; c.beginPath(); c.ellipse(x, y - s * 0.22, s * 0.2, s * 0.24, 0, Math.PI, 0); c.fillRect(x - s * 0.2, y - s * 0.22, s * 0.4, s * 0.22); c.fill();
  if (aberto) glow(c, x, y - s * 0.2, s * 0.6, "rgba(255,240,200,0.8)");
  c.fillStyle = cor; c.beginPath(); c.arc(x + (aberto ? s * 0.5 : 0), y - s * 0.24, s * 0.26, 0, 6.283); c.fill();
}
function muralha(c, x, y, s, cor, queda) {
  c.save(); c.fillStyle = cor;
  for (let i = -3; i <= 3; i++) {
    const bx = x + i * s * 0.32, q = queda > 0 ? easeOut(clamp(queda * 1.4 - Math.abs(i) * 0.08)) : 0;
    c.save(); c.translate(bx, y); c.rotate(q * (i % 2 ? 0.6 : -0.5)); c.translate(0, q * s * 0.3);
    c.fillRect(-s * 0.16, -s * 0.7, s * 0.32, s * 0.7); for (let k = 0; k < 3; k++) c.fillRect(-s * 0.16 + k * s * 0.12, -s * 0.78, s * 0.07, s * 0.08);
    c.restore();
  }
  c.restore();
  if (queda > 0.1 && queda < 1) poeira(c, 60, 12, queda * 6, [x - s, y - s * 0.6, s * 2, s * 0.6], "rgba(220,190,150,1)", 6, 40, 0.5 * (1 - queda));
}
function trono(c, x, y, s) { c.fillStyle = "#6a3d14"; c.fillRect(x - s * 0.3, y - s, s * 0.6, s); c.strokeStyle = "#e0a23c"; c.lineWidth = 8; c.strokeRect(x - s * 0.29, y - s * 0.99, s * 0.58, s * 0.98); }
function mesa(c, x, y, s, cor) {
  c.fillStyle = cor; c.fillRect(x - s * 0.7, y - s * 0.32, s * 1.4, s * 0.06); c.fillRect(x - s * 0.62, y - s * 0.3, s * 0.05, s * 0.3); c.fillRect(x + s * 0.57, y - s * 0.3, s * 0.05, s * 0.3);
  c.fillStyle = "#d9a85a"; c.beginPath(); c.ellipse(x - s * 0.2, y - s * 0.36, s * 0.12, s * 0.05, 0, 0, 6.283); c.fill();
  c.fillStyle = "#b8862e"; c.fillRect(x + s * 0.15, y - s * 0.48, s * 0.07, s * 0.14);
}
function cesto(c, x, y, s) {
  c.fillStyle = "#8a5a2a"; c.beginPath(); c.moveTo(x - s * 0.3, y - s * 0.3); c.lineTo(x + s * 0.3, y - s * 0.3); c.lineTo(x + s * 0.22, y); c.lineTo(x - s * 0.22, y); c.fill();
  c.fillStyle = "#e0b070"; for (let i = 0; i < 5; i++) { c.beginPath(); c.ellipse(x - s * 0.2 + i * s * 0.1, y - s * 0.33, s * 0.07, s * 0.05, 0, 0, 6.283); c.fill(); }
  c.fillStyle = "#9fb5c8"; c.beginPath(); c.ellipse(x + s * 0.05, y - s * 0.4, s * 0.16, s * 0.05, -0.2, 0, 6.283); c.fill();
  glow(c, x, y - s * 0.35, s * 0.6, "rgba(255,230,170,0.35)");
}
function estrelaGuia(c, x, y, s, t) {
  glow(c, x, y, s * 3, "rgba(255,250,220,0.9)");
  c.save(); c.translate(x, y); c.rotate(t * 0.2); c.fillStyle = "#fffbea";
  c.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, r = i % 2 ? s * 0.3 : s; c.lineTo(Math.cos(a) * r, Math.sin(a) * r); } c.fill(); c.restore();
}
function pedraFunda(c, x, y, s, t, ida, ax, ay) {
  if (ida <= 0 || ida >= 1) return;
  const px = lerp(x, ax ?? x + 500, ida), py = lerp(y, ay ?? y, ida) - Math.sin(ida * Math.PI) * 120;
  c.strokeStyle = "rgba(255,240,210,0.4)"; c.lineWidth = 4; c.beginPath(); c.moveTo(lerp(x, px, 0.6), lerp(y, py, 0.6) + 10); c.lineTo(px, py); c.stroke();
  c.fillStyle = "#d8d0c0"; c.beginPath(); c.arc(px, py, s * 0.05, 0, 6.283); c.fill();
}

// desenha um personagem humano de qualquer variante
function personagem(c, el, x, y, h, cor, t, k) {
  const v = el.variante || "homem";
  const heroi = el.tipo === "heroi";
  const pose = el.pose || "em_pe";
  const braco = el.levanta_bracos_em != null ? lerp(0.15, 2.5, easeOut(seg(k, el.levanta_bracos_em, el.levanta_bracos_em + 0.2))) : null;
  const o = { olhar: el.olhar || 1, cor, barba: v === "idoso" || v === "rei" || el.barba, cajado: v === "idoso" || v === "pastor" || el.cajado,
              cabeca: v === "farao" ? "nemes" : (v === "mulher" || v === "idoso" || v === "pastor" || v === "sacerdote" || el.pano) ? "pano" : "nua",
              colar: v === "farao" || el.colar, bracoE: 0.15, bracoD: 0.15 + Math.sin(t * 1.5 + x) * 0.04, inclina: el.inclina || 0 };
  if (heroi) { o.tunica = el.veste === "branca" ? "branca" : "listras"; }
  if (v === "jesus") { o.tunica = "branca"; o.barba = true; glow(c, x, y - h * 0.6, h * 1.1, "rgba(255,240,205,0.6)"); }
  if (v === "anjo") { o.tunica = "branca"; asas(c, x, y, h, t); glow(c, x, y - h * 0.6, h * 0.9, "rgba(255,245,215,0.55)"); }
  if (v === "crianca") h *= 0.62;
  if (pose === "bracos_erguidos") { o.bracoE = 2.6; o.bracoD = 2.5 + Math.sin(t * 2) * 0.05; }
  if (pose === "apontando") { o.bracoD = 1.45; }
  if (pose === "orando") { o.bracoD = 1.9; o.bracoE = 1.8; o.inclina = 0.03 * o.olhar; }
  if (pose === "abraco") { o.bracoD = 1.45; o.bracoE = 1.35; }
  if (pose === "andando") { o.bracoD = Math.sin(t * 6) * 0.35; o.bracoE = -Math.sin(t * 6) * 0.35; o.inclina = Math.sin(t * 6) * 0.02; }
  if (braco != null) { o.bracoE = braco; o.bracoD = braco + 0.05; }
  if (el.braco_d != null) o.bracoD = el.braco_d;
  if (el.braco_e != null) o.bracoE = el.braco_e;
  if (heroi && el.brilho !== false) glow(c, x, y - h * 0.55, h * 0.8, "rgba(255,225,160,0.32)");
  if (pose === "sentado") { sentado(c, x, y, h * 1.05, heroi, o.olhar); return; }
  if (pose === "ajoelhado_costas") { ajoelhadoCostas(c, x, y, h, cor, 1); return; }
  if (pose === "caido") { c.save(); c.translate(x, y); c.rotate(-Math.PI / 2 * (o.olhar)); c.translate(-x, -y); pessoa(c, x, y + h * 0.12, h, o); c.restore(); return; }
  if (pose === "ajoelhado") { // de joelhos, de perfil: corpo mais baixo e mãos postas
    o.bracoD = 1.9; o.bracoE = 1.8;
    c.save(); c.translate(x, y); c.scale(1, 0.72); c.translate(-x, -y); pessoa(c, x, y, h, o); c.restore(); return;
  }
  if (v === "soldado" || v === "gigante") { o.cajado = false; o.lanca = true; }
  pessoa(c, x, y, h, o);
  const hr = h * 0.072, hy = y - h + hr;
  if (v === "rei" || el.coroa) { c.fillStyle = "#f0bf4c"; c.beginPath(); c.moveTo(x - hr, hy - hr * 0.7); for (let i = 0; i <= 4; i++) c.lineTo(x - hr + i * hr * 0.5, hy - hr * (i % 2 ? 1.0 : 1.7)); c.lineTo(x + hr, hy - hr * 0.7); c.fill(); glow(c, x, hy - hr, hr * 3, "rgba(255,210,100,0.4)"); }
  if (v === "soldado" || v === "gigante") {
    c.fillStyle = cor; c.beginPath(); c.arc(x, hy - hr * 0.1, hr * 1.2, Math.PI, 0); c.fill(); c.fillRect(x - hr * 0.1, hy - hr * 2.0, hr * 0.2, hr * 0.9);
    c.beginPath(); c.ellipse(x + (o.olhar) * h * 0.13, y - h * 0.5, h * 0.09, h * 0.17, 0, 0, 6.283); c.fill();   // escudo
    if (v === "gigante") { c.fillStyle = "rgba(200,190,170,0.35)"; c.beginPath(); c.ellipse(x + o.olhar * h * 0.13, y - h * 0.5, h * 0.06, h * 0.12, 0, 0, 6.283); c.fill(); }
  }
  if (v === "sacerdote") { c.fillStyle = "rgba(220,200,140,0.7)"; c.fillRect(x - h * 0.08, y - h * 0.72, h * 0.16, h * 0.12); }
}

function multidao(c, el, x, y, h, cor, t) {
  const n = el.n || 9, r = rng(n * 13 + Math.round(x));
  for (let i = 0; i < n; i++) {
    const px = x - (n - 1) * h * 0.14 + i * h * 0.28 + (r() - 0.5) * h * 0.1, hh = h * (0.85 + r() * 0.25);
    if (el.pose === "ajoelhado_costas") ajoelhadoCostas(c, px, y + (i % 2) * h * 0.08, hh * 0.6, cor, 1);
    else personagem(c, { tipo: "pessoa", variante: el.variante || (r() > 0.5 ? "mulher" : "homem"), olhar: el.olhar || (r() > 0.5 ? 1 : -1), pose: el.pose === "bracos_erguidos" ? "bracos_erguidos" : "em_pe" }, px, y + (i % 2) * h * 0.05, hh, cor, t + i, 0);
  }
}

// posição animada de um elemento no instante k (0..1 da cena)
function posicao(el, k, base) {
  const ap = el.aparece_em || 0;
  if (k < ap) return null;
  let x = el.x ?? 540, y = base.chao + (el.dy || 0), alfa = 1;
  const ent = easeOut(seg(k, ap, ap + 0.18));
  if (el.entra === "esquerda") x = lerp(-300, x, ent);
  else if (el.entra === "direita") x = lerp(W + 300, x, ent);
  else if (el.entra === "baixo") y = lerp(y + 500, y, ent);
  else if (el.entra === "cima") y = lerp(-200, y, ent);
  else if (ap > 0 || el.entra === "fade") alfa = ent;
  if (el.anda_ate != null) x = lerp(x, el.anda_ate, ease(seg(k, Math.max(ap, el.anda_de || ap), el.anda_fim || 1)));
  if (el.sobe != null) y -= el.sobe * ease(seg(k, el.sobe_de || ap, el.sobe_fim || 1));
  if (el.some_em != null) alfa *= 1 - seg(k, el.some_em, el.some_em + 0.12);
  return { x, y, alfa };
}

function desenharElemento(c, el, k, u, d, pal, cena) {
  const plano = PLANOS[el.plano || "meio"];
  const p = posicao(el, k, plano); if (!p || p.alfa <= 0) return;
  const h = plano.h * (el.escala || 1);
  const cor = el.cor || corPlano(pal, el.plano || "meio");
  const t = u;
  c.save(); c.globalAlpha *= p.alfa;
  if (el.treme) c.translate(Math.sin(u * 40) * 4, 0);
  if (el.cai_em != null && k > el.cai_em) { const q = easeOut(seg(k, el.cai_em, el.cai_em + 0.18)); c.translate(p.x, p.y); c.rotate(q * Math.PI / 2 * (el.olhar || 1)); c.translate(-p.x, -p.y); }
  switch (el.tipo) {
    case "heroi": case "pessoa": personagem(c, el, p.x, p.y, h, el.tipo === "heroi" ? (el.cor || pal.sil) : cor, t, k); break;
    case "multidao": multidao(c, el, p.x, p.y, h, cor, t); break;
    case "gigante": personagem(c, Object.assign({ variante: "gigante" }, el), p.x, p.y, h * 2.0, cor, t, k); break;
    case "camelo": camelo(c, p.x, p.y, h * 0.55, u * 5, cor); break;
    case "ovelha": { const n = el.n || 1; for (let i = 0; i < n; i++) ovelha(c, p.x + (i - (n - 1) / 2) * h * 0.42 + (i % 2) * 14, p.y + (i % 3) * 8, h * 0.32, t + i); break; }
    case "leao": leao(c, p.x, p.y, h * 0.75, t, cor); break;
    case "peixe_grande": peixeGrande(c, p.x, p.y - h * 0.4, h * 1.4, t, el.cor || "#0d1a2a", seg(k, el.boca_em ?? 2, (el.boca_em ?? 2) + 0.15)); break;
    case "pomba": pomba(c, p.x, p.y - (el.altura ?? 900), h * 0.35, t); break;
    case "porco": { const n = el.n || 1; for (let i = 0; i < n; i++) porco(c, p.x + (i - (n - 1) / 2) * h * 0.4, p.y + (i % 2) * 10, h * 0.32, t + i, el.cor); break; }
    case "cobra": cobra(c, p.x, p.y, h * 0.5, t, cor); break;
    case "barco": barco(c, p.x, p.y - 40, h * 0.9, t, cor, cena.tempestade); break;
    case "arca": arca(c, p.x, p.y, h * 2.2, cor); break;
    case "fogo": fogo(c, p.x, p.y, h * 0.45, t); break;
    case "tabuas": tabuas(c, p.x, p.y - (el.altura ?? 0), h * 0.5); break;
    case "cruz": cruz(c, p.x, p.y, h * 1.3, cor); break;
    case "tumulo": tumulo(c, p.x, p.y, h * 0.9, cor, el.aberto_em != null ? k > el.aberto_em : el.aberto); break;
    case "muralha": muralha(c, p.x, p.y, h * 0.9, cor, el.cai_em != null ? seg(k, el.cai_em, el.cai_em + 0.3) : 0); break;
    case "trono": trono(c, p.x, p.y, h * 0.9); break;
    case "mesa": mesa(c, p.x, p.y, h * 0.8, cor); break;
    case "cesto": cesto(c, p.x, p.y, h * 0.4); break;
    case "estrela": estrelaGuia(c, p.x, el.altura != null ? p.y - el.altura : 360, 40, t); break;
    case "palmeira": palmeira(c, p.x, p.y, h * 0.95, cor, t); break;
    case "pedra": pedraFunda(c, p.x, p.y - h * 0.7, h, t, seg(k, el.lanca_em ?? 0.4, (el.lanca_em ?? 0.4) + 0.14), el.alvo_x, el.alvo_y); break;
    case "luz": glow(c, p.x, p.y - (el.altura ?? 600), h * 1.5, "rgba(255,240,200,0.75)"); break;
  }
  c.restore();
}

// ---------- efeitos ----------
function efeitos(c, cena, u, k) {
  const ef = cena.efeitos || [];
  if (ef.includes("luz_divina")) {
    c.save(); c.globalCompositeOperation = "lighter"; const a = 0.6 + 0.4 * Math.sin(u * 1.5);
    c.fillStyle = grad(c, 0, 0, 0, 1400, [[0, `rgba(255,240,200,${0.45 * a})`], [1, "rgba(255,240,200,0.02)"]]);
    c.beginPath(); c.moveTo(380, -50); c.lineTo(700, -50); c.lineTo(800, 1400); c.lineTo(280, 1400); c.fill(); c.restore();
  }
  if (ef.includes("chuva") || cena.tempestade) {
    c.save(); c.strokeStyle = "rgba(190,210,240,0.35)"; c.lineWidth = 2; const r = rng(3);
    for (let i = 0; i < 160; i++) { const x = (r() * W + u * 300) % W, y = (r() * H + u * 1900 * (0.8 + r() * 0.4)) % H; c.beginPath(); c.moveTo(x, y); c.lineTo(x - 12, y + 44); c.stroke(); }
    c.restore();
  }
  if (ef.includes("raios") || cena.tempestade) {
    const f = Math.max(0, Math.sin(u * 2.3) ** 40);
    if (f > 0.05) { c.fillStyle = `rgba(220,230,255,${0.35 * f})`; c.fillRect(0, 0, W, H); c.strokeStyle = `rgba(240,245,255,${f})`; c.lineWidth = 6; c.beginPath(); let x = 300 + (Math.floor(u / 2.7) % 3) * 230, y = 0; c.moveTo(x, y); while (y < 1100) { x += (rng(Math.floor(y) + Math.floor(u))() - 0.5) * 120; y += 90; c.lineTo(x, y); } c.stroke(); }
  }
  if (ef.includes("arco_iris")) {
    const a = easeOut(seg(k, 0.15, 0.6)); c.save(); c.globalAlpha = 0.55 * a; c.lineWidth = 34;
    ["#e04a4a", "#f29a3a", "#f2d54a", "#5ab45a", "#4a8ad8", "#7a5ac8"].forEach((cor, i) => { c.strokeStyle = cor; c.beginPath(); c.arc(540, 1500, 900 - i * 34, Math.PI, 0); c.stroke(); });
    c.restore();
  }
  if (ef.includes("fogo_do_ceu")) { for (let i = 0; i < 6; i++) { const q = (u * 0.8 + i * 0.37) % 1; fogo(c, 200 + i * 130, lerp(-100, 1380, q), 40, u + i); } }
  if (ef.includes("brasas")) poeira(c, 50, 8, u, [0, 400, W, 1200], "rgba(255,160,80,1)", 3, 50, 0.6);
  poeira(c, 28, 17, u, [0, 300, W, 1300], "rgba(255,225,180,1)", 2.4, 16, ef.includes("sem_poeira") ? 0 : 0.35);
}

// ---------- câmera ----------
function camera(c, cena, k) {
  const tipo = cena.camera || "aproxima", p = ease(k);
  const foco = cena.foco || [540, 1150];
  let s = 1, dx = 0, dy = 0;
  if (tipo === "aproxima") s = lerp(1.0, 1.14, p);
  if (tipo === "afasta") s = lerp(1.18, 1.0, p);
  if (tipo === "zoom_forte") s = lerp(1.0, 1.45, p);
  if (tipo === "desce") { s = 1.12; dy = lerp(260, -60, p); }
  if (tipo === "sobe") { s = 1.12; dy = lerp(-120, 220, p); }
  if (tipo === "direita") { s = 1.15; dx = lerp(110, -110, p); }
  if (tipo === "esquerda") { s = 1.15; dx = lerp(-110, 110, p); }
  if (cena.tremor) { dx += Math.sin(k * 300) * 6; dy += Math.cos(k * 260) * 6; }
  c.translate(foco[0], foco[1]); c.scale(s, s); c.translate(-foco[0] + dx, -foco[1] + dy);
}

// ---------- texto na tela (contador ou rótulo) ----------
function textoTela(c, cena, k) {
  const tt = cena.texto_tela; if (!tt || cena.versiculo) return;
  const m = /^(\d+)\s+(.*)$/.exec(tt);
  const a = easeOut(seg(k, 0.05, 0.2));
  c.save(); c.globalAlpha = a; c.font = "700 66px Poppins"; c.textAlign = "center";
  c.shadowColor = "rgba(0,0,0,0.6)"; c.shadowBlur = 20; c.fillStyle = "rgba(255,244,220,0.96)";
  const txt = m && cena.contar !== false ? `${Math.max(1, Math.round(+m[1] * clamp(seg(k, 0.05, 0.55))))} ${m[2]}` : tt;
  c.fillText(txt, 540, 330); c.restore();
}

// ---------- versículo final ----------
function quebraLinhas(c, texto, max) {
  const ws = texto.split(/\s+/), linhas = [[]];
  ws.forEach(w => { const l = linhas[linhas.length - 1]; if (c.measureText([...l, w].join(" ")).width > max && l.length) linhas.push([w]); else l.push(w); });
  return linhas.map(l => l.join(" "));
}
function versiculo(c, cena, u) {
  const ativo = (cena.falaDur || cena.dur) * 0.8;
  c.save(); c.font = "italic 600 86px Lora";
  const linhas = quebraLinhas(c, `“${cena.fala.replace(/[“”"]/g, "")}”`, 900);
  const total = linhas.join(" ").split(" ").length; let idx = 0;
  const y0 = 760 - (linhas.length - 1) * 56;
  const fundoA = clamp(u / 0.4);
  c.save(); c.globalAlpha = 0.45 * fundoA; c.fillStyle = "#120a18";
  c.beginPath(); c.roundRect(60, y0 - 110, 960, linhas.length * 112 + 150, 40); c.fill(); c.restore();
  linhas.forEach((ln, li) => {
    const largura = c.measureText(ln).width; let x = 540 - largura / 2;
    ln.split(" ").forEach(w => {
      const ap = clamp((u - (idx / total) * ativo) / 0.35);
      c.save(); c.globalAlpha = ap; c.textAlign = "left"; c.shadowColor = "rgba(0,0,0,0.65)"; c.shadowBlur = 24;
      c.fillStyle = "#fff4dc"; c.fillText(w, x, y0 + li * 112 + (1 - ap) * 20); c.restore();
      x += c.measureText(w + " ").width; idx++;
    });
  });
  const ref = clamp((u - ativo * 0.9) / 0.5);
  c.globalAlpha = ref; c.font = "700 54px Poppins"; c.fillStyle = "#ffd96a"; c.textAlign = "center"; c.shadowColor = "rgba(0,0,0,0.8)"; c.shadowBlur = 16;
  c.fillText((cena.texto_tela || "").toUpperCase(), 540, y0 + linhas.length * 112 + 40);
  c.restore();
}

// ---------- cena completa ----------
function cenaComposta(c, u, d, cena) {
  const k = clamp(u / d);
  const hora = cena.tempestade ? "tempestade" : (cena.hora || "por_do_sol");
  const pal = HORAS[hora] || HORAS.por_do_sol;
  sky(c, pal.ceu);
  if (hora === "noite") estrelas(c, u);
  if (cena.tempestade) nuvens(c, u, "rgba(40,48,64,0.85)", 150, 9, 30);
  c.save();
  camera(c, cena, k);
  cena._k = k;
  (CENARIOS[cena.cenario] || CENARIOS.deserto)(c, u, pal, cena);
  const ordem = { fundo: 0, meio: 1, frente: 2 };
  const els = (cena.elementos || []).slice().sort((a, b) => (ordem[a.plano || "meio"] - ordem[b.plano || "meio"]));
  els.filter(e => (e.plano || "meio") !== "frente").forEach(el => desenharElemento(c, el, k, u, d, pal, cena));
  efeitos(c, cena, u, k);
  c.restore();
  els.filter(e => e.plano === "frente").forEach(el => desenharElemento(c, el, k, u, d, pal, cena));
  textoTela(c, cena, k);
  if (cena.versiculo) versiculo(c, cena, u);
}
