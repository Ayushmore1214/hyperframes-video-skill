#!/usr/bin/env python3
"""
Synthesize the soundtrack for the Kubernetes intro: mechanical keystrokes, then a minimal
electronic score that builds through the fast cuts and opens up for the reveal.

All times are read from the timing JSON block in index.html, and the music ducks under each voiceover line.
Run:  python3 make_score.py   ->  audio/score.wav (length = TOTAL in index.html)
Needs numpy and scipy. Deterministic (fixed random seed), so reruns give the same file.
"""
import numpy as np
from pathlib import Path
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

import json, re
T = json.loads(re.search(r'<script id="timing" type="application/json">(.*?)</script>', Path("index.html").read_text(), re.S).group(1))
SR, TOTAL = 44100, T["TOTAL"]
N = int(SR * TOTAL)
rng = np.random.default_rng(7)
dry = np.zeros((2, N))
send = np.zeros((2, N))          # reverb bus
TYPE = {k: (v["text"], v["start"], v["rate"], v["enter"]) for k, v in T["typing"].items()}

def mf(m): return 440.0 * 2 ** ((m - 69) / 12)
NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
def nf(name):                     # "A2" -> Hz
    return mf(12 * (int(name[-1]) + 1) + NOTE[name[:-1]])

def tt(dur): return np.arange(int(dur * SR)) / SR
def lp(x, fc, order=2): return sosfilt(butter(order, min(fc, SR * 0.45) / (SR / 2), "low", output="sos"), x)
def hp(x, fc, order=2): return sosfilt(butter(order, fc / (SR / 2), "high", output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo / (SR / 2), hi / (SR / 2)], "band", output="sos"), x)
def saw(f, t, detune=0.0):
    ph = (f * (1 + detune) * t + rng.random()) % 1.0
    return 2 * ph - 1

def add(start, sig, gain=1.0, pan=0.0, rev=0.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    dry[0, i:i + len(sig)] += sig * l; dry[1, i:i + len(sig)] += sig * r
    if rev:
        send[0, i:i + len(sig)] += sig * l * rev; send[1, i:i + len(sig)] += sig * r * rev

def env(n, a, r, sustain=None):
    """attack a seconds, release r seconds at the end, flat in between"""
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na) ** 2
    if nr: e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e

# ---------------- instruments ----------------
def key(t0, enter=False):
    d = 0.09 if enter else 0.06; t = tt(d)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.0035)
    f = (150 if enter else 190) * (0.92 + 0.16 * rng.random())
    thock = np.sin(2 * np.pi * f * t) * np.exp(-t / (0.03 if enter else 0.018))
    add(t0 + rng.uniform(-0.006, 0.006), 0.55 * click + 0.7 * thock, 0.5 if enter else 0.33, rng.uniform(-0.25, 0.25), 0.06)

def kick(t0, g=0.9):
    t = tt(0.45); f = 45 + 75 * np.exp(-t / 0.045)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    s[:60] += np.linspace(0.6, 0, 60)
    add(t0, s, g)

def hat(t0, g=0.12, open_=False):
    t = tt(0.25 if open_ else 0.05)
    add(t0, hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / (0.08 if open_ else 0.014)), g, rng.uniform(-0.3, 0.3), 0.05)

def clap(t0, g=0.35):
    t = tt(0.3); n = bp(rng.standard_normal(len(t)), 900, 3200)
    e = np.exp(-t / 0.09)
    for k in (0.0, 0.011, 0.022): e[int(k * SR):int(k * SR) + 200] += 0.6
    add(t0, n * e + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05), g, 0, 0.25)

def impact(t0, size=1.0):
    t = tt(2.5 * size); f = 38 + 50 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.7 * size))
    noise = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t / (0.25 * size))
    add(t0, 0.9 * sub + 0.35 * noise, 0.8 * size ** 0.5, 0, 0.45)

def tick(t0, f=2400, g=0.1):
    t = tt(0.08); add(t0, np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012), g, rng.uniform(-0.5, 0.5), 0.2)

def riser(t0, dur, g=0.35, reverse=False):
    t = tt(dur); n = rng.standard_normal(len(t)); out = np.zeros_like(n); blk = 2048
    for b in range(0, len(n), blk):
        p = b / len(n); fc = 300 * (40 ** p)
        out[b:b + blk] = lp(n[b:b + blk], fc)
    e = (t / dur) ** 2.2
    add(t0, out * e * g if not reverse else out * e * g, 1.0, 0, 0.3)

def pad(t0, t1, notes, g=0.12, bright=1400, a=1.6, r=2.2):
    dur = t1 - t0 + r; t = tt(dur); s = np.zeros(len(t))
    for nm in notes:
        f = nf(nm)
        for dt in (-0.004, 0.0, 0.005):
            s += saw(f, t, dt)
    s = lp(s / (3 * len(notes)), bright) * env(len(t), a, r)
    add(t0, s, g * 3.2, 0, 0.55)
    add(t0 + 0.013, s, g * 1.2, 0.6, 0.3)          # a touch of width

def pluck(t0, nm, g=0.1, pan=0.0):
    t = tt(0.6); f = nf(nm)
    s = lp(saw(f, t) + 0.5 * saw(f * 2, t), 900 + 3000 * 1) * np.exp(-t / 0.13)
    add(t0, s, g, pan, 0.4)

def bass(t0, nm, dur, g=0.3):
    t = tt(dur); f = nf(nm)
    s = lp(saw(f, t), 260) + 0.8 * np.sin(2 * np.pi * f * t)
    add(t0, s * env(len(t), 0.005, min(0.08, dur * 0.5)), g)

def bell(t0, nm, g=0.18):
    t = tt(4.0); f = nf(nm)
    s = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / d) for m, a, d in ((1, 1, 1.6), (2.76, 0.35, 0.6), (5.4, 0.15, 0.25)))
    add(t0, s, g, 0, 0.7)

def tone(t0, nm, dur, g=0.1, shape="sine"):
    t = tt(dur); f = nf(nm)
    s = np.sin(2 * np.pi * f * t) if shape == "sine" else lp(saw(f, t), 1200)
    add(t0, s * env(len(t), 0.02, dur * 0.5), g, 0, 0.3)

# ---------------- arrangement (all times come from index.html) ----------------
F, C, D, SV, FO, W2, OS, M = T["fast"], T["cluster"], T["cmds"], T["service"], T["failover"], T["words2"], T["os"], T["mosaic"]
beat = 0.5
for name, (txt, st, rate, ent) in TYPE.items():
    for i, ch in enumerate(txt): key(st + i * rate)
    key(ent, enter=True)
# cold open: near silence, a low swell, a heartbeat under each app, rising into the push-through
CO = T["cold"]
t = tt(TOTAL - 0.3); dr = (np.sin(2 * np.pi * 55 * t) + 0.35 * lp(saw(55, t), 220)) * env(len(t), 3.0, 1.5)
add(0.3, dr, 0.16)
pad(0.6, CO["push"], ["A2", "E3", "B3"], 0.07, 900, 2.5, 1.2)
for key in ("msg", "pay", "song"):
    kick(CO[key], 0.35); kick(CO[key] + 0.28, 0.22); tone(CO[key] + 0.05, {"msg": "E5", "pay": "G5", "song": "B5"}[key], 2.0, 0.035)
riser(CO["push"] - 1.6, 1.7, 0.35)
impact(CO["push"] + 0.1, 1.2)
pad(CO["push"] + 0.2, T["flash"], ["F2", "C3", "A3", "E4"], 0.1, 1600, 0.8, 1.2)
bell(CO["l2"] + 0.3, "E6", 0.07)

# fast cuts: pulse at 120 bpm
impact(T["flash"], 1.0); riser(T["flash"] - 0.5, 0.45, 0.25)
for k in range(int((C["in"] - T["flash"]) / beat)):
    b0 = T["flash"] + k * beat
    kick(b0, 0.7); hat(b0 + beat / 2, 0.1)
    bass(b0, "A1", 0.22, 0.26); bass(b0 + beat / 2, "A1", 0.2, 0.18)
for tc in (F["pull"], F["pods"], F["check"], F["words"]): tick(tc, 1800, 0.12); hat(tc, 0.18, True)
for tw in F["stamps"]: clap(tw, 0.28); kick(tw, 0.5)
riser(C["in"] - 0.8, 0.8, 0.3)

# cluster: cinematic pads and a soft arpeggio
seg = (C["out"] - C["in"]) / 4
names = [["A2", "C3", "E3", "A3"], ["F2", "A2", "C3", "F3"], ["C3", "E3", "G3", "C4"], ["G2", "B2", "D3", "G3"]]
arp = [["A4", "C5", "E5", "C5"], ["F4", "A4", "C5", "A4"], ["C5", "E5", "G5", "E5"], ["G4", "B4", "D5", "B4"]]
for i, ns in enumerate(names): pad(C["in"] + i * seg - 0.2, C["in"] + (i + 1) * seg, ns, 0.1)
k = 0; tk = C["in"] + 2.0
while tk < C["out"] - 0.3:
    ci = min(3, int((tk - C["in"]) / seg))
    pluck(tk, arp[ci][k % 4], 0.045 + 0.02 * (k % 4 == 0), (-0.4, 0.4)[k % 2]); k += 1; tk += 0.25
for tl_ in (C["l1"], C["l2"], C["l3"]): impact(tl_, 0.4)
tone(C["crash"], "A#4", 0.5, 0.05, "saw"); tone(C["restart"], "E5", 0.6, 0.06)
for j in range(6): tick(C["scale"] + 0.15 + j * 0.14, 3000, 0.05)
tone(C["die"], "D#3", 0.9, 0.06, "saw"); tone(C["die"], "A2", 0.9, 0.06, "saw")
impact(C["auto"], 1.1); bell(C["auto"], "A5", 0.12)

# commands, service, failover: energy builds
prog = ["A1", "F1", "C2", "G1"]
k = 0; b0 = D["in"]
while b0 < W2["out"] - 0.25:
    kick(b0, 0.8)
    if b0 >= SV["in"] and k % 2 == 1: clap(b0, 0.28)
    root = prog[int((b0 - D["in"]) / 2.0) % 4]
    bass(b0, root, 0.22, 0.3); bass(b0 + beat / 2, root, 0.2, 0.24)
    hat(b0 + beat / 2, 0.09); 
    if b0 >= SV["in"]: hat(b0 + beat / 4, 0.06); hat(b0 + 3 * beat / 4, 0.06)
    k += 1; b0 += beat
for i in range(int((W2["out"] - D["in"]) / 2.0)):
    r0 = prog[i % 4]; pad(D["in"] + i * 2.0, D["in"] + i * 2.0 + 2.0, [r0[:-1] + "3", {"A": "C4", "F": "A3", "C": "E3", "G": "B3"}[r0[0]]], 0.04, 2200, 0.3, 0.8)
for j in range(30): tick(SV["in"] + 0.5 + j * 0.085 + 0.5, 2600 + 400 * (j % 6), 0.04)
tone(FO["die"], "D#3", 0.6, 0.08, "saw"); tone(FO["die"] + 0.3, "D#3", 0.6, 0.08, "saw")
for j in range(12): tick(FO["checks"] + j * 0.05, 3200, 0.04)
riser(W2["out"] - 4.0, 4.0, 0.4)
for j in range(24): clap(W2["in"] + (W2["out"] - W2["in"]) * (1 - (1 - j / 24) ** 1.6), 0.08 + 0.12 * j / 24)
for tw in W2["stamps"]: impact(tw, 0.4)

# open source: the beat drops away, a hopeful pad and a rising arpeggio
impact(OS["in"], 0.9); hat(OS["in"], 0.2, True)
pad(OS["in"], OS["out"], ["D3", "F#3", "A3", "E4"], 0.1, 1900, 0.6, 1.5)
k = 0; tk = OS["in"] + 0.5
while tk < OS["out"] - 0.2:
    pluck(tk, ["D5", "F#5", "A5", "E5", "A5", "F#5"][k % 6], 0.04 + 0.015 * min(1, (tk - OS["in"]) / 4), (-0.35, 0.35)[k % 2]); k += 1; tk += 0.25
for j in range(10): tick(OS["ticker"] + j * 0.12, 2800 + 150 * j, 0.03)
riser(M["in"] - 0.3, M["fly"] + M["flyDur"] + 0.5 - (M["in"] - 0.3), 0.38)

# mosaic assembles, then the reveal opens up and breathes
impact(M["logo"], 1.8); hat(M["logo"], 0.25, True)
for j in range(16): tick(M["shine"] + 0.1 + j * 0.05, 3400 + 80 * j, 0.03)
pad(M["logo"], M["title"] + 0.5, ["F2", "A2", "C3", "E3", "G3"], 0.12, 1800, 0.3, 2.5)
pad(M["title"] - 0.3, M["out"], ["C3", "E3", "G3", "D4"], 0.11, 2000, 1.2, 2.5)
for j, nm in enumerate(["E5", "A5", "G5", "C6", "E6"]): tone(M["logo"] + 0.4 + j * 0.9, nm, 3.0, 0.03)
bell(M["title"], "A5", 0.15); bell(M["title"], "E6", 0.07)
pad(T["final"]["in"] - 0.4, T["final"]["fade"], ["A2", "E3", "B3", "C4"], 0.08, 1400, 1.5, 1.8)
bell(T["final"]["in"] + 0.2, "E5", 0.08)

# duck the music under the voiceover (about -8 dB, with short ramps)
duck = np.ones(N)
for _id, st, ln in T["vo"]:
    a0, a1 = int((st - 0.15) * SR), int((st + ln + 0.25) * SR)
    duck[a0:a1] = np.minimum(duck[a0:a1], 0.4)
duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), mode="same")
dry *= duck; send *= duck

# ---------------- mix ----------------
ir_t = tt(2.8)
ir = np.stack([lp(rng.standard_normal(len(ir_t)), 5000) * np.exp(-ir_t / 0.75) for _ in range(2)]) * 0.05
wet = np.stack([fftconvolve(send[c], ir[c])[:N] for c in range(2)])
mix = dry + wet
fade = np.ones(N); a, b = int(T["final"]["fade"] * SR), int((TOTAL - 0.1) * SR)
fade[a:b] = np.linspace(1, 0, b - a) ** 1.5; fade[b:] = 0
mix *= fade
mix = np.tanh(1.2 * mix / np.max(np.abs(mix))) / np.tanh(1.2) * 0.89
Path("audio").mkdir(exist_ok=True)
wavfile.write("audio/score.wav", SR, (mix.T * 32767).astype(np.int16))
print("wrote audio/score.wav", mix.shape[1] / SR, "s")
