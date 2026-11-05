"""Trilha sonora própria do canal (gerada por código: 100% nossa, sem direitos de terceiros
e sem reivindicação do Content ID).

Estilos (um por quadro):
  pulso    -> "Nexus em 60s": pad escuro + pulso eletrônico e arpejo (ritmo de notícia)
  cinema   -> "Histórias Tech": piano lento + cordas (clima de documentário)
  ambiente -> "Lá Fora, Aqui": pad suave + arpejo leve (explicador); troca de trilha a cada bloco

Uso: python3 scripts/trilha.py SAIDA.wav SEGUNDOS ESTILO [--semente texto] [--cortes 30,75,120]
Cada semente (o slug do vídeo) dá tom, progressão e andamento diferentes: nenhum vídeo repete a trilha.
"""
import argparse
import hashlib
import wave
from pathlib import Path

import numpy as np

TAXA = 44100
# progressões (graus da escala menor natural), escolhidas pela semente
PROGRESSOES = [[0, 5, 2, 6], [0, 3, 5, 4], [0, 6, 5, 6], [0, 5, 3, 4], [0, 2, 5, 4], [5, 3, 0, 4]]
MENOR = [0, 2, 3, 5, 7, 8, 10]


def _hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def _acorde(tonica, grau):
    notas = []
    for passo in (0, 2, 4):
        g = grau + passo
        notas.append(tonica + MENOR[g % 7] + 12 * (g // 7))
    return notas


def _env(n, ataque, queda):
    e = np.ones(n)
    a, q = min(n, int(ataque * TAXA)), min(n, int(queda * TAXA))
    if a:
        e[:a] = np.linspace(0, 1, a)
    if q:
        e[-q:] *= np.linspace(1, 0, q)
    return e


def _pad(freqs, dur):
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    s = np.zeros(n)
    for f in freqs:
        for desafino in (-0.15, 0.0, 0.17):  # coro: 3 osciladores levemente desafinados
            fase = 2 * np.pi * (f + desafino) * t
            s += np.sin(fase) + 0.25 * np.sin(2 * fase) + 0.1 * np.sin(3 * fase)
    return s * _env(n, dur * 0.35, dur * 0.35) / (len(freqs) * 3)


def _piano(f, dur):
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    s = sum(np.sin(2 * np.pi * f * h * t) * (0.6 ** (h - 1)) for h in (1, 2, 3, 4))
    return s * np.exp(-t * 2.2) * _env(n, 0.004, 0.08)


def _pluck(f, dur):
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)
    return s * np.exp(-t * 9) * _env(n, 0.002, 0.03)


def _bumbo(dur=0.35):
    n = int(dur * TAXA)
    t = np.arange(n) / TAXA
    f = 110 * np.exp(-t * 18) + 42
    return np.sin(2 * np.pi * np.cumsum(f) / TAXA) * np.exp(-t * 9)


def _baixo_passa(s, corte):
    # filtro passa-baixa de 1 polo (suaviza, deixa a trilha "atrás" da voz)
    a = np.exp(-2 * np.pi * corte / TAXA)
    try:
        from scipy.signal import lfilter
        return lfilter([1 - a], [1, -a], s)
    except ImportError:
        pass
    y = np.empty_like(s)
    acc = 0.0
    for i in range(0, len(s), 4096):
        bloco = s[i:i + 4096]
        out = np.empty_like(bloco)
        for j, x in enumerate(bloco):
            acc = (1 - a) * x + a * acc
            out[j] = acc
        y[i:i + 4096] = out
    return y


def _eco(s, atraso=0.32, ganho=0.35, vezes=4):
    y = s.copy()
    d = int(atraso * TAXA)
    for k in range(1, vezes + 1):
        if d * k < len(s):
            y[d * k:] += s[:-d * k] * (ganho ** k)
    return y


def secao(dur, estilo, semente):
    rng = np.random.default_rng(int(hashlib.md5(semente.encode()).hexdigest()[:8], 16))
    tonica = 45 + int(rng.integers(0, 8))  # de A2 a E3
    prog = PROGRESSOES[int(rng.integers(0, len(PROGRESSOES)))]
    bpm = {"pulso": rng.uniform(96, 112), "cinema": rng.uniform(60, 70), "ambiente": rng.uniform(80, 92)}[estilo]
    batida = 60 / bpm
    compasso = batida * 4 * (2 if estilo == "cinema" else 1)
    n = int(dur * TAXA)
    mix = np.zeros(n + TAXA * 12)
    t0, i = 0.0, 0
    while t0 < dur:
        notas = _acorde(tonica, prog[i % len(prog)])
        p = int(t0 * TAXA)
        pad = _pad([_hz(m + 12) for m in notas] + [_hz(notas[0])], compasso * 1.15)
        mix[p:p + len(pad)] += pad * (0.55 if estilo != "cinema" else 0.45)
        if estilo == "cinema":
            for b, m in enumerate([notas[0] + 24, notas[1] + 24, notas[2] + 24, notas[1] + 24, notas[0] + 36, notas[2] + 24]):
                q = p + int(b * compasso / 6 * TAXA)
                nota = _piano(_hz(m), compasso / 6 * 2.5)
                mix[q:q + len(nota)] += nota * 0.22
        else:
            passos = 8 if estilo == "pulso" else 4
            for b in range(passos):
                q = p + int(b * compasso / passos * TAXA)
                m = notas[b % 3] + (24 if estilo == "pulso" else 36)
                nota = _pluck(_hz(m), compasso / passos * 0.9)
                mix[q:q + len(nota)] += nota * (0.16 if estilo == "pulso" else 0.1)
            if estilo == "pulso":
                for b in range(4):
                    q = p + int(b * batida * TAXA)
                    k = _bumbo()
                    mix[q:q + len(k)] += k * 0.5
        t0 += compasso
        i += 1
    mix = mix[:n]
    if estilo != "pulso":
        mix = _eco(mix, atraso=batida * 0.75, ganho=0.3)
    mix = _baixo_passa(mix, 2600 if estilo == "pulso" else 1900)
    return mix * _env(n, 1.5, 2.5)


def gerar(saida, dur, estilo="ambiente", semente="nexus", cortes=None):
    """Gera a trilha; em `cortes` (segundos) troca de trilha com transição suave (vídeos longos)."""
    pontos = [0.0] + [c for c in (cortes or []) if 5 < c < dur - 5] + [dur]
    partes = []
    for j in range(len(pontos) - 1):
        d = pontos[j + 1] - pontos[j] + (1.5 if j < len(pontos) - 2 else 0)
        partes.append(secao(d, estilo, f"{semente}-{j}"))
    total = np.zeros(int(dur * TAXA) + TAXA * 2)
    for j, s in enumerate(partes):
        p = int(pontos[j] * TAXA)
        total[p:p + len(s)] += s[:len(total) - p]
    total = total[:int(dur * TAXA)]
    total /= max(1e-6, np.max(np.abs(total))) / 0.8
    dados = (np.clip(total, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(saida), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(TAXA)
        w.writeframes(dados.tobytes())
    return Path(saida)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("saida"); ap.add_argument("segundos", type=float)
    ap.add_argument("estilo", choices=["pulso", "cinema", "ambiente"])
    ap.add_argument("--semente", default="nexus"); ap.add_argument("--cortes", default="")
    a = ap.parse_args()
    cortes = [float(x) for x in a.cortes.split(",") if x.strip()]
    print(gerar(a.saida, a.segundos, a.estilo, a.semente, cortes))
