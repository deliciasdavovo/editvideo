"""Render do roteiro da Laís (v3)."""
import os, subprocess, sys, wave, math
import numpy as np
import shots3                       # aplica a linha do tempo nova antes do render
import render
from render import pluck, TMP, FPS
import shots

render.NAMES.update({'rival': 'Menino', 'pai': 'Pai'})
render.TITLE_T[:] = [1.1, 4.9]
DUR = shots3.DUR
B = {x['name']: x for x in shots3.TL['blocks']}


def build_audio(path):
    sr = 48000
    n = int((DUR + 0.2) * sr)
    tt = np.arange(n) / sr
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(render.HERE, 'audio3', 'narracao3.wav'), '-af',
                    'highpass=f=80,equalizer=f=300:t=q:w=1:g=-2.5,deesser=i=0.4,acompressor=ratio=3:threshold=-18dB:attack=10:release=120,aecho=0.8:0.6:15:0.08,aresample=48000',
                    '-ac', '1', f'{TMP}/voz3.wav'], check=True)
    vw = wave.open(f'{TMP}/voz3.wav'); v = np.frombuffer(vw.readframes(vw.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    voice = np.zeros(n); voice[:min(n, len(v))] = v[:n]
    chords = [[146.83, 174.61, 220.0, 293.66], [116.54, 146.83, 174.61, 233.08], [87.31, 130.81, 174.61, 220.0], [130.81, 164.81, 196.0, 261.63]]
    music = np.zeros(n)
    sparse = [(B['c04_narr']['e'], B['c06_ping']['s']), (B['c09_imp']['s'] - 1, B['c09_imp']['e'] + 2)]   # respiro / revelação
    t_ = 0.2; k = 0; seed = 3
    while t_ < DUR - 1.6:
        f0 = chords[(k // 4) % 4][k % 4]
        step = 1.5 if any(a < t_ < b for a, b in sparse) else 0.65
        p = pluck(sr, f0, 1.8, 0.08, seed); i = int(t_ * sr); music[i:i + len(p)] += p[:max(0, n - i)]
        t_ += step; k += 1; seed += 1
    for j, f0 in enumerate([146.83, 185.0, 220.0, 293.66]):   # ré maior: resolve
        p = pluck(sr, f0, 2.5, 0.07, 90 + j); i = int((DUR - 1.6 + j * 0.06) * sr); music[i:i + len(p)] += p[:max(0, n - i)]
    pad = np.zeros(n)
    for f0, a in [(73.42, 0.5), (146.83, 0.3), (220.0, 0.2)]:
        pad += a * np.sin(2 * np.pi * f0 * tt + 0.3 * np.sin(2 * np.pi * 0.17 * tt))
    pad *= 0.022
    d0, d1 = B['c06_ping']['s'] - 1, B['c09_imp']['s']
    drone = 0.03 * np.sin(2 * np.pi * 55 * tt) * np.clip(np.minimum((tt - d0) / 2, (d1 - tt) / 1.5), 0, 1)
    music += pad + drone
    music *= np.clip((DUR - tt) / 0.7, 0, 1)
    sfx = np.zeros(n); rng = np.random.default_rng(5)
    for s in shots3.SHOTS:
        if s['trans']:
            i = int(max(0, s['s'] - 0.05) * sr); L = int(0.5 * sr)
            noise = np.convolve(rng.normal(0, 1, L) * np.hanning(L) * 0.05, np.ones(30) / 30, mode='same')
            sfx[i:i + L] += noise[:max(0, n - i)]

    def plic(at, f0=1400, amp=0.12):
        i = int(at * sr); L = int(0.09 * sr); e = np.exp(-np.arange(L) / (0.015 * sr))
        sfx[i:i + L] += (amp * np.sin(2 * np.pi * f0 * np.arange(L) / sr) * e)[:max(0, n - i)]
    for s in shots3.SHOTS:
        if s['fn'] is shots3.c4_prepare:
            plic(s['s'] + 0.45, 1500, 0.06); plic(s['s'] + 0.95, 1650, 0.06)
        if s['fn'] is shots3.c9_hide:
            plic(s['s'] + 0.3, 420, 0.14); plic(s['s'] + 0.55, 380, 0.1)
        if s['fn'] is shots3.c5_seasons:
            d = s['e'] - s['s']
            for j in range(3):
                plic(s['s'] + j * d / 3, 900 + 80 * j, 0.05)
    env = np.abs(voice); g = np.zeros(n); cur = 0.0; hop = 48
    for i in range(0, n, hop):
        tgt = 1.0 if env[i:i + hop].max() > 0.02 else 0.0
        kk = hop / (0.04 * sr) if tgt > cur else hop / (0.3 * sr)
        cur += (tgt - cur) * min(1, kk); g[i:i + hop] = cur
    music *= (1 - 0.7 * g)
    mix = voice + music * 0.55 + sfx * 0.6
    mix = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    ow = wave.open(f'{TMP}/mix3.wav', 'wb'); ow.setnchannels(1); ow.setsampwidth(2); ow.setframerate(sr); ow.writeframes(mix.tobytes()); ow.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{TMP}/mix3.wav', '-af', 'alimiter=limit=0.8,loudnorm=I=-14:TP=-1.5',
                    '-ar', '48000', '-ac', '2', path], check=True)


if __name__ == '__main__':
    mode = sys.argv[1]
    NF = int(math.ceil(DUR * FPS))
    if mode == 'part':
        k, K = int(sys.argv[2]), int(sys.argv[3])
        render.render_part(NF * k // K, NF * (k + 1) // K, f'{TMP}/p3_{k}.mp4')
    elif mode == 'audio':
        build_audio(f'{TMP}/audio3.wav')
    elif mode == 'still':
        render.render_frame(float(sys.argv[2])).save(sys.argv[3])
    elif mode == 'list':
        for s in shots3.SHOTS:
            print(f"{s['s']:6.2f}-{s['e']:6.2f} {s['e'] - s['s']:5.2f} {s['label']}")
        for ck in render.CHUNKS:
            print(f"   {ck['s']:6.2f} {ck['who'][:5]} {ck['text']}")
