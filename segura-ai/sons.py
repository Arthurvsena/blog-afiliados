"""Efeitos sonoros e trilha do Segura Aí 3D, gerados por código (nada de áudio de terceiros).

gerar(eventos, duracao, destino_efeitos, destino_trilha, semente)
  eventos: lista de (tipo, segundo). Tipos: plim, pop, erro, ok, queda, quebra, choque, rebobinar,
  fanfarra, whoosh, rangido.
"""
import wave

import numpy as np

SR = 44100


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(d, a=0.005, r=None):
    t = _t(d)
    return np.minimum(1, t / a) * np.exp(-t / (r if r else d / 4))


def _seno(f, d):
    return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, (int(d * SR),))) / SR)


def plim(rng):
    return np.concatenate([(np.sin(2 * np.pi * f * _t(0.18)) * _env(0.18, r=0.06) +
                            0.3 * np.sin(4 * np.pi * f * _t(0.18)) * _env(0.18, r=0.03)) for f in (1318.5, 1760)]) * 0.5


def pop(rng):
    return _seno(np.linspace(500, 1100, int(0.12 * SR)), 0.12) * _env(0.12, r=0.035) * 0.35


def ok(rng):
    return np.concatenate([_seno(f, 0.1) * _env(0.1, r=0.05) for f in (880, 1320)]) * 0.35


def erro(rng):
    t = _t(0.35)
    s = np.sign(np.sin(2 * np.pi * 155 * t)) + 0.5 * np.sign(np.sin(2 * np.pi * 160 * t))
    return s * np.minimum(1, (0.35 - t) / 0.05) * np.minimum(1, t / 0.01) * 0.12


def whoosh(rng, d=0.35):
    n = np.convolve(rng.normal(0, 1, int(d * SR)), np.ones(40) / 40, 'same')
    return n * np.sin(np.pi * _t(d) / d) ** 2 * 1.2


def quebra(rng):
    d = 0.35
    n = rng.normal(0, 1, int(d * SR)) * _env(d, a=0.001, r=0.04)
    for c in (0.0, 0.05, 0.11):
        i = int(c * SR)
        n[i:i + 300] += rng.normal(0, 3, 300) * np.exp(-np.arange(300) / 60)
    return n * 0.35


def queda(rng):
    d = 0.6
    t = _t(d)
    baque = _seno(np.linspace(140, 45, len(t)), d) * _env(d, a=0.002, r=0.1) + rng.normal(0, 0.3, len(t)) * _env(d, a=0.001, r=0.02)
    boing = _seno(260 + 90 * np.sin(2 * np.pi * 14 * t) * np.exp(-t / 0.25), d) * _env(d, r=0.18) * 0.5
    return baque * 0.9 + boing


def choque(rng):
    d = 0.9
    t = _t(d)
    zum = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.15 + rng.normal(0, 0.25, len(t)) * (np.sin(2 * np.pi * 30 * t) > 0)
    return zum * np.minimum(1, (d - t) / 0.1) * 0.5


def rebobinar(rng, d=0.6):
    t = _t(d)
    f = 900 + 700 * np.sin(2 * np.pi * 9 * t)
    s = 0.1 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) + rng.normal(0, 0.25, len(t))
    return s * np.sin(np.pi * t / d) * 0.5


def rangido(rng, d=1.4):
    t = _t(d)
    return _seno(180 + 40 * np.sin(2 * np.pi * 6 * t), d) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * t)) * 0.06


def fanfarra(rng):
    out = np.zeros(int(0.8 * SR))
    for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        s = (np.sin(2 * np.pi * f * _t(0.4)) + 0.4 * np.sin(4 * np.pi * f * _t(0.4))) * _env(0.4, r=0.15) * 0.25
        a = int(i * 0.09 * SR)
        out[a:a + len(s)] += s
    return out


SONS = {"plim": plim, "pop": pop, "ok": ok, "erro": erro, "whoosh": whoosh, "quebra": quebra, "queda": queda,
        "choque": choque, "rebobinar": rebobinar, "rangido": rangido, "fanfarra": fanfarra}


def _pluck(f, d, g, rng):
    n = int(SR / f)
    buf = rng.uniform(-1, 1, n)
    out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]
        buf[i % n] = 0.5 * (buf[i % n] + buf[(i + 1) % n]) * 0.996
    return out * g


def trilha(duracao, rng, bpm=112):
    """Loop leve de violão sintético + baixo + chimbal (C-G-Am-F)."""
    N = int(duracao * SR)
    beat = 60 / bpm
    acordes = [(261.6, 329.6, 392.0), (196.0, 246.9, 293.7), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6)]
    baixo = [130.8, 98.0, 110.0, 87.3]
    cache, mus = {}, np.zeros(N)

    def P(f, d, g):
        k = (round(f, 1), d, g)
        if k not in cache:
            cache[k] = _pluck(f, d, g, rng)
        return cache[k]

    def add(s, at):
        a = int(at * SR)
        e = min(N, a + len(s))
        if e > a:
            mus[a:e] += s[:e - a]

    for b in range(int(duracao / beat) + 1):
        t0, ci = b * beat, (b // 4) % 4
        add(P(baixo[ci], 0.5, 0.35), t0)
        add(P(acordes[ci][[0, 2, 1, 2][b % 4]] * 2, 0.3, 0.12), t0 + beat / 2)
        if b % 2 == 0:
            add(P(acordes[ci][2] * 2, 0.25, 0.09), t0 + beat * 0.75)
    hat = rng.normal(0, 1, 1500) * np.exp(-np.arange(1500) / 250) * 0.04
    for b in range(int(duracao / beat * 2) + 1):
        add(hat, b * beat / 2)
    return mus


def _wav(nome, x):
    x = np.clip(x, -1, 1)
    w = wave.open(str(nome), 'w')
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
    w.close()


def gerar(eventos, duracao, destino_efeitos, destino_trilha, semente=7, silencios=()):
    rng = np.random.default_rng(semente)
    N = int((duracao + 0.5) * SR)
    fx = np.zeros(N)
    for tipo, quando, *ganho in eventos:
        if tipo not in SONS:
            continue
        s = SONS[tipo](rng)
        i = max(0, int(quando * SR))
        j = min(N, i + len(s))
        if j > i:
            fx[i:j] += s[:j - i] * (ganho[0] if ganho else 1.0)
    _wav(destino_efeitos, fx * 0.8)
    mus = trilha(duracao + 0.5, rng)
    tt = np.arange(N) / SR
    g = np.ones(N)
    for a, b in silencios:   # trilha quase some no rebobinar
        g[(tt > a) & (tt < b)] = 0.15
    g[tt > duracao - 0.4] = 0.0
    g = np.convolve(g, np.ones(2000) / 2000, 'same')
    _wav(destino_trilha, mus * g)
