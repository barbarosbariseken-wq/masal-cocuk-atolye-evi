import numpy as np, wave, sys
SR = 44100
DUR = float(sys.argv[2])
BPM = 92; BEAT = 60 / BPM; E8 = BEAT / 2; BAR = BEAT * 4
N = int(SR * (DUR + 3))
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)

def hz(n):
    names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    acc = 1 if '#' in n else (-1 if len(n) == 3 and n[1] == 'b' else 0)
    return 440 * 2 ** ((names[n[0]] + acc + 12 * (int(n[-1]) + 1) - 69) / 12)

def add(sig, t, g=1.0, pan=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or i < 0: return
    s = sig[:j - i] * g
    L[i:j] += s * (1 - max(0, pan)); R[i:j] += s * (1 + min(0, pan))

def env_t(d): return np.arange(int(SR * d)) / SR

def musicbox(f, d=2.2):
    t = env_t(d)
    s = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * f * 4.0 * t) * np.exp(-t * 6) + 0.08 * np.sin(2 * np.pi * f * 6.8 * t) * np.exp(-t * 14)
    return s * np.exp(-t * 2.6) * np.minimum(1, t / 0.002)

def epiano(f, d=1.6):  # soft felt piano / rhodes-ish
    t = env_t(d)
    mod = np.sin(2 * np.pi * f * t) * 0.6 * np.exp(-t * 3)
    s = np.sin(2 * np.pi * f * t + mod) + 0.15 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 4)
    return s * np.exp(-t * 2.0) * np.minimum(1, t / 0.006)

def pad(freqs, d):
    t = env_t(d); s = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6):
            s += np.sin(2 * np.pi * (f + det) * t) + 0.2 * np.sin(2 * np.pi * 2 * (f + det) * t)
    a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.6)
    return s * a / (len(freqs) * 2)

def bass(f, d):
    t = env_t(d)
    return (np.sin(2 * np.pi * f * t) + 0.18 * np.sin(4 * np.pi * f * t)) * np.minimum(1, t / 0.015) * np.exp(-t * 1.6)

def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def brush():
    n = int(SR * 0.22); s = lp(rng.uniform(-1, 1, n), 5)
    return s * np.exp(-np.arange(n) / SR * 18) * np.minimum(1, np.arange(n) / (SR * 0.01))
def softkick():
    t = env_t(0.3); f = 80 * np.exp(-t * 20) + 48
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
def chime(f):
    t = env_t(3.0)
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.0 * t)) * np.exp(-t * 1.4)

CH = {'F': ['F3', 'A3', 'C4'], 'C': ['E3', 'G3', 'C4'], 'Dm': ['F3', 'A3', 'D4'], 'Bb': ['F3', 'Bb3', 'D4'], 'Gm': ['G3', 'Bb3', 'D4'], 'Am': ['E3', 'A3', 'C4']}
BS = {'F': 'F2', 'C': 'C2', 'Dm': 'D2', 'Bb': 'Bb1', 'Gm': 'G1', 'Am': 'A1'}
PROG = ['F', 'C', 'Dm', 'Bb', 'F', 'C', 'Bb', 'C']
MEL = ['C5 - A4 - C5 - A4 -', 'G4 A4 Bb4 - C5 - - -', 'D5 - D5 C5 A4 - F4 -', 'G4 - A4 Bb4 A4 - - -',
       'C5 - A4 - C5 - F5 -', 'E5 - D5 C5 G4 - - -', 'D5 - D5 C5 Bb4 A4 G4 -', 'A4 - G4 - E4 - - -']
MEL_B = ['F5 - E5 - D5 - C5 -', 'E5 - D5 - C5 - G4 -', 'F5 - E5 D5 C5 - A4 -', 'Bb4 - C5 D5 C5 - - -',
         'A4 C5 F5 - E5 D5 C5 -', 'G4 - C5 - E5 - D5 -', 'D5 C5 Bb4 A4 G4 - A4 Bb4', 'C5 - - - E4 - G4 -']

nb = int(np.ceil(DUR / BAR)) + 1
intro = 2
for b in range(nb):
    t0 = b * BAR
    last = b >= nb - 2
    if b < intro:
        for k, n in enumerate(['C5 - A4 - F4 - A4 -', 'G4 - C5 - E5 - - -'][b].split()):
            if n != '-': add(musicbox(hz(n)), t0 + k * E8, 0.30, 0.2)
        add(pad([hz(x) for x in CH[['F', 'C'][b]]], BAR), t0, 0.06)
        continue
    i = (b - intro) % 8; sec = ((b - intro) // 8) % 2
    ch = PROG[i] if not last else 'F'
    mel = (MEL if sec == 0 else MEL_B)[i] if not last else ('F5 - - - - - - -' if b == nb - 2 else '- - - - - - - -')
    for k, n in enumerate(mel.split()):
        if n != '-':
            add(musicbox(hz(n)), t0 + k * E8 + rng.normal(0, 0.003), 0.30, 0.2)
            if sec == 1: add(musicbox(hz(n) * 2), t0 + k * E8, 0.06, -0.3)  # sparkle octave
    # broken-chord piano in eighths
    notes = CH[ch]
    arp = [notes[0], notes[1], notes[2], notes[1], notes[0], notes[2], notes[1], notes[2]] if not last else [notes[0], notes[1], notes[2], '-', '-', '-', '-', '-']
    for k, n in enumerate(arp):
        if n != '-': add(epiano(hz(n)), t0 + k * E8, 0.085 if k % 2 else 0.11, -0.25)
    add(pad([hz(x) * 2 for x in CH[ch]], BAR + 0.3), t0, 0.045)
    add(bass(hz(BS[ch]), BEAT * 1.9), t0, 0.20)
    if not last:
        add(bass(hz(BS[ch]) * 1.5, BEAT * 1.9), t0 + 2 * BEAT, 0.15)
        add(softkick(), t0, 0.22); add(softkick(), t0 + 2.5 * BEAT, 0.18)
        for k in (1, 3): add(brush(), t0 + k * BEAT, 0.07, 0.15)
        for k in range(8):
            if k % 2: add(brush(), t0 + k * E8, 0.025, 0.35)
    if i == 7 and not last: add(chime(hz('F6')), t0 + 3.5 * BEAT, 0.05, 0.4)

n = int(SR * DUR); Ls, Rs = L[:n].copy(), R[:n].copy()
fi, fo = int(SR * 0.4), int(SR * 2.5)
e = np.ones(n); e[:fi] = np.linspace(0, 1, fi); e[-fo:] = np.linspace(1, 0, fo) ** 1.4
Ls *= e; Rs *= e
pk = max(abs(Ls).max(), abs(Rs).max()); Ls /= pk / 0.89; Rs /= pk / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([Ls, Rs], 1) * 32767).astype(np.int16).tobytes())
print('ok')
