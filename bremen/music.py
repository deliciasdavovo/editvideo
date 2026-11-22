"""Trilha sintetizada (violão de nylon Karplus-Strong + pad + cello), ambiente e efeitos — ancorados nos planos."""
import sys, numpy as np, wave, math
sys.argv = ['x', 'none']
import render as R

SR = 48000
T = R.T_END
N = int(T * SR) + SR
rng = np.random.default_rng(5)


def save(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(f'/home/user/editvideo/bremen/audio/{name}.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def ks(freq, dur, amp=0.08, bright=0.5):
    n = int(dur * SR)
    p = int(SR / freq)
    buf = rng.uniform(-1, 1, p)
    # passa-baixa inicial (nylon, macio)
    for _ in range(2):
        buf = (buf + np.roll(buf, 1)) / 2
    out = np.zeros(n)
    k = 0.5 + 0.495 * bright
    for i in range(n):
        out[i] = buf[i % p]
        j = i % p
        buf[j] = k * buf[j] + (1 - k) * buf[(j - 1) % p] if False else 0.996 * 0.5 * (buf[j] + buf[(j + 1) % p])
    env = np.minimum(1, np.arange(n) / (0.004 * SR))
    return out * env * amp


_ks_cache = {}


def pluck(freq, dur, amp):
    key = (round(freq, 2), round(dur, 2))
    if key not in _ks_cache:
        _ks_cache[key] = ks(freq, dur, 1.0)
    return _ks_cache[key] * amp


def note(name):
    names = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'Bb': 1, 'B': 2}
    n, o = name[:-1], int(name[-1])
    return 440 * 2 ** ((names[n] + (o - 4) * 12) / 12)


CH = {'Dm': ['D3', 'A3', 'D4', 'F4', 'A4', 'F4'], 'Bb': ['Bb2', 'F3', 'Bb3', 'D4', 'F4', 'D4'], 'F': ['F2', 'C3', 'F3', 'A3', 'C4', 'A3'],
      'C': ['C3', 'G3', 'C4', 'E4', 'G4', 'E4'], 'Gm': ['G2', 'D3', 'G3', 'Bb3', 'D4', 'Bb3'], 'A': ['A2', 'E3', 'A3', 'C4', 'E4', 'C4']}

mus = np.zeros(N)


def add(buf, x, t):
    i = int(t * SR)
    if i < 0:
        x = x[-i:]
        i = 0
    if i >= len(buf):
        return
    L = min(len(x), len(buf) - i)
    buf[i:i + L] += x[:L]


def arpeggio(t0, t1, prog, step, amp=0.08, skip=1):
    t = t0
    k = 0
    while t < t1:
        ch = prog[(k // 6) % len(prog)]
        nt = CH[ch][k % 6]
        if k % skip == 0:
            add(mus, pluck(note(nt), 2.2, amp * (1.0 if k % 6 == 0 else 0.8)), t)
        t += step
        k += 1


def pad(t0, t1, chords, amp=0.03, low=False):
    seg = (t1 - t0) / len(chords)
    for i, ch in enumerate(chords):
        a, b = t0 + i * seg, t0 + (i + 1) * seg
        n = int((b - a) * SR)
        tt = np.arange(n) / SR
        env = np.minimum(1, tt / 0.8) * np.minimum(1, (b - a - tt) / 0.8)
        x = np.zeros(n)
        for nt in CH[ch][:4]:
            f = note(nt) * (0.5 if low else 1)
            x += np.sin(2 * np.pi * f * tt) * 0.5 + np.sin(2 * np.pi * f * 2.002 * tt) * 0.12
        add(mus, x * env * amp / 4, a)


def cello(t0, t1, freq, amp=0.035):
    n = int((t1 - t0) * SR)
    tt = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * tt)
    ph = 2 * np.pi * freq * np.cumsum(vib) / SR
    x = sum(np.sin(ph * h) / h ** 1.3 for h in range(1, 7))
    env = np.minimum(1, tt / 1.2) * np.minimum(1, (t1 - t0 - tt) / 1.2)
    add(mus, x * env * amp, t0)


# --- roteiro musical por trecho
tB = R.tB01b
arpeggio(0.2, tB - 0.3, ['Dm', 'Bb'], 0.75, 0.07, skip=2)
cello(0.0, tB, note('D2'), 0.03)
arpeggio(tB, R.tB02, ['Dm', 'Gm', 'Dm', 'A'], 1.0, 0.06)
pad(tB, R.tB02, ['Dm', 'Gm', 'Dm', 'A'], 0.025)
arpeggio(R.tB02, R.tN04 - 1.5, ['F', 'C', 'Dm', 'Bb'], 0.6, 0.075)
pad(R.tB02, R.tN04 - 1.5, ['F', 'C', 'Dm', 'Bb'] * 3, 0.02)
arpeggio(R.tN04 - 1.5, R.tEeles, ['F', 'C'], 0.8, 0.07)
arpeggio(R.tEeles, R.tN05a, ['Dm', 'Bb', 'Gm', 'A'], 0.9, 0.06, skip=2)
cello(R.tEeles, R.tN05a + 1, note('D2'), 0.03)
arpeggio(R.tN05a, R.tN06, ['Dm', 'C', 'Bb', 'A', 'F', 'C'], 0.6, 0.07)
cello(R.tN06, R.tN07, note('A1'), 0.035)
arpeggio(R.tN06, R.tN07 - 0.3, ['Dm', 'A'], 0.7, 0.06, skip=2)
arpeggio(R.tN07, T - 2.2, ['F', 'Bb', 'F', 'C'], 1.2, 0.06)
pad(R.tN07, T - 0.6, ['F', 'Bb', 'C', 'F'], 0.03)
# acorde final resolvido (F), com fade curto
for i, nt in enumerate(['F2', 'C3', 'F3', 'A3', 'C4', 'F4']):
    add(mus, pluck(note(nt), 2.4, 0.07), T - 2.0 + i * 0.05)
fade = np.ones(N)
fs, fe = int((T - 0.7) * SR), int(T * SR)
fade[fs:fe] = np.linspace(1, 0, fe - fs)
fade[fe:] = 0
mus *= fade

# --- ambiente
amb = np.zeros(N)


def brown(n, k=0.02):
    w = rng.normal(0, 1, n)
    b = np.cumsum(w)
    b -= np.convolve(b, np.ones(2000) / 2000, 'same')
    return b / (np.abs(b).max() + 1e-9)


def region(t0, t1, x, fade=0.6):
    n = int((t1 - t0) * SR)
    y = x[:n] if len(x) >= n else np.pad(x, (0, n - len(x)))
    tt = np.arange(n) / SR
    env = np.minimum(1, tt / fade) * np.minimum(1, (t1 - t0 - tt) / fade)
    add(amb, y * env, t0)


wind = brown(N) * 0.5
crick = np.zeros(N)
for k in range(int(T * 1.3)):
    t = rng.uniform(0, T)
    n = int(0.05 * SR)
    tt = np.arange(n) / SR
    ch = np.sin(2 * np.pi * 4300 * tt) * (np.sin(2 * np.pi * 40 * tt) > 0) * np.exp(-tt * 30)
    add(crick, ch * 0.06, t)
fire_ = brown(N) * 0.25
for k in range(int(T * 6)):
    t = rng.uniform(0, T)
    n = int(0.01 * SR)
    add(fire_, rng.normal(0, 1, n) * np.exp(-np.arange(n) / 60) * rng.uniform(0.05, 0.25), t)

def sl(a, b):
    return slice(int(a * SR), int(b * SR))

for sh in R.SHOTS:
    nm = sh['f'].__name__
    a, b = sh['t0'], sh['t1']
    if nm in ('s01', 's19', 's24', 's26', 's26b', 's30', 's31'):
        region(a, b, fire_[sl(a, b)] * 0.5, 0.2)
    elif nm in ('s27', 's28'):
        region(a, b, fire_[sl(a, b)] * 0.15 + crick[sl(a, b)] * 0.5, 0.2)
    elif nm in ('s02', 's03', 's17', 's18', 's20', 's21', 's22', 's23', 's25', 's29'):
        region(a, b, crick[sl(a, b)] + wind[sl(a, b)] * 0.12, 0.2)
    elif nm in ('s04', 's05', 's06'):
        region(a, b, wind[sl(a, b)] * 0.35, 0.2)
    else:
        region(a, b, wind[sl(a, b)] * 0.15, 0.2)

# --- efeitos
sfx = np.zeros(N)


def tok(t, pitch=1.0, amp=0.35):
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    f = 520 * pitch * rng.uniform(0.94, 1.06)
    x = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.7 * tt)) * np.exp(-tt * 45)
    add(sfx, x * amp * rng.uniform(0.85, 1.0), t - 1.5 / 30)


def whoosh(t, dur=0.5, amp=0.18):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    w = rng.normal(0, 1, n)
    for _ in range(3):
        w = np.convolve(w, np.ones(6) / 6, 'same')
    env = np.sin(np.pi * tt / dur) ** 2
    add(sfx, w * env * amp, t - 0.15)


def thud(t, amp=0.5):
    n = int(0.3 * SR)
    tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * 70 * tt * (1 - tt)) * np.exp(-tt * 14) + rng.normal(0, 0.2, n) * np.exp(-tt * 40)
    add(sfx, x * amp, t - 1.5 / 30)


def plic(t, amp=0.25):
    n = int(0.06 * SR)
    tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * (1800 - 9000 * tt) * tt) * np.exp(-tt * 70)
    add(sfx, x * amp, t - 1.5 / 30)


def scratch(t, amp=0.18):
    n = int(0.25 * SR)
    w = rng.normal(0, 1, n) * (np.sin(np.arange(n) / SR * 2 * np.pi * 30) > 0)
    add(sfx, w * np.exp(-np.arange(n) / SR * 8) * amp, t)


for sh in R.SHOTS:
    if sh['trans']:
        whoosh(sh['t0'] + 0.25, 0.55, 0.16)
    else:
        whoosh(sh['t0'], 0.3, 0.05)
thud(R.Wt('embora.') + 0.4, 0.4)
plic(R.tLat + 0.1)
plic(R.tN03b + 0.8 + 0.15, 0.3)  # gato erra o bote
for t_ in (R.Wt('cachorro', 1, 'n05a') + 0.5, R.Wt('gato', 1, 'n05a') + 0.45, R.Wt('galo.', 1, 'n05a') + 0.4):
    tok(t_, 0.9 + rng.uniform(0, 0.3))
thud(R.EV['concert']['t1'] + 0.1 + 0.8, 0.45)  # cadeira
scratch(R.tArr)
plic(R.tMord, 0.3)
thud(R.tCoice, 0.6)
tok(R.tCoice + 0.02, 0.7, 0.4)

save('music', mus)
save('amb', amb)
save('sfx', sfx)
print('ok', T)
