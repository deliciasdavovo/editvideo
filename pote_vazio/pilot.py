"""Plano-piloto: sobre o ombro do imperador, Ping responde (sincronia labial, choro, foco)."""
import math, subprocess, wave, os, random
import numpy as np
import skia
import paperlib as pl
import characters as ch
import scenes as sc
from scenes import W, H
from style_frames import palace_crowd, draw_char

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'frames')
AUD = os.path.join(HERE, 'audio')
OFFSET = 0.40            # corta o silêncio inicial do áudio
DUR = 5.0

# ------------------------------------------------ áudio: envelope para abrir a boca
w = wave.open(os.path.join(AUD, 'ping_b5.wav'))
SR = w.getframerate()
X = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def rms_at(t):
    i = int((t + OFFSET) * SR)
    seg = X[max(0, i - 600):i + 600]
    return float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0


RMAX = max(rms_at(k / 100) for k in range(500))

# palavras em tempo do ÁUDIO, distribuídas nos trechos de fala do silencedetect
# (0,58–1,97 / 2,12–2,885 / 3,25–5,11); depois convertidas para tempo do clipe
_W = [('Eu', .58, .72), ('cuidei', .72, 1.12), ('da', 1.12, 1.24), ('sua', 1.24, 1.46), ('semente', 1.46, 1.97),
      ('todo', 2.12, 2.45), ('dia', 2.45, 2.885), ('mas', 3.25, 3.62), ('ela', 3.62, 4.05), ('não', 4.05, 4.45),
      ('nasceu', 4.45, 5.11)]
WORDS = [(w_, a - OFFSET, b - OFFSET) for (w_, a, b) in _W]
STRESS = [x - OFFSET for x in (1.0, 1.7, 2.5, 4.2, 4.85)]   # cuiDEI, seMENte, DIa, NÃO, nasCEU
BLINKS = [1.62, 2.55, 4.78]


def viseme(t):
    for w_, a, b in WORDS:
        if a <= t < b:
            letters = [ch_ for ch_ in w_.lower() if ch_.isalpha()]
            k = min(len(letters) - 1, int((t - a) / (b - a) * len(letters)))
            for j in range(k, -1, -1):
                L = letters[j]
                if L in 'aáàã':
                    return 'A'
                if L in 'eéêií':
                    return 'E'
                if L in 'oóôõ':
                    return 'O'
                if L in 'uú':
                    return 'U'
                if L in 'mbp':
                    return 'M'
            return 'E'
    return None


def ease(x):
    x = max(0, min(1, x))
    return x * x * (3 - 2 * x)


def nod_at(t):
    v = 0
    for s in STRESS:
        d = t - s
        if -0.12 < d < 0.35:
            v += math.sin((d + 0.12) / 0.47 * math.pi) * 4.0
    return v


# ------------------------------------------------ camadas paradas (cache)
def bg_image():
    surf = skia.Surface(W, H); c = surf.getCanvas()
    sc.grade(c, sat=1.02, warm=0.3, bright=0.98, contrast=1.06)
    palace_crowd(c)
    c.restore()
    img = surf.makeImageSnapshot()
    return img


def shoulder_image():
    """Costas do imperador em primeiro plano (sobre o ombro)."""
    surf = skia.Surface(W, H); c = surf.getCanvas()
    P = ch.IMP
    pl.SCALE[0] = 3.2
    c.save(); c.translate(130, 1500); c.scale(3.2, 3.2)
    robe = pl.smooth([(-140, 200), (-120, -60), (-70, -140), (0, -170), (70, -140), (110, -60), (130, 200)], tension=0.4)
    pl.layer(c, robe, P['robe'], depth=0.3)
    pl.ink(c, [(-20, -160), (-10, -60), (-30, 120)], 2, pl.mul(P['robe'], 0.5), 0.6)
    pl.layer(c, pl.rr(-30, -190, 30, -160, 8), pl.mul(P['skin'], 0.85), depth=0.1)
    hat = pl.smooth([(-38, -180), (-40, -230), (-28, -262), (0, -268), (28, -262), (40, -230), (38, -180)], tension=0.4)
    pl.layer(c, hat, P['hat'], depth=0.2)
    pl.layer(c, pl.rr(-42, -196, 42, -180, 6), P['panel'], depth=0.06)
    # ponta da barba aparecendo do lado
    pl.layer(c, pl.tp([(34, -150), (46, -100), (40, -60)], 12, 3), P['beard'], depth=0.1)
    c.restore(); pl.SCALE[0] = 1.0
    return surf.makeImageSnapshot()


BG = bg_image()
SH = shoulder_image()


def frame(t):
    tq = math.floor(t * 15) / 15            # personagem "em dois"
    surf = skia.Surface(W, H); c = surf.getCanvas()
    # câmera: push-in lento (30 fps)
    z = 1.08 + 0.05 * ease(t / DUR)
    fx, fy = 520, 760
    c.save(); c.translate(500, 760); c.scale(z, z); c.translate(-fx, -fy)
    # foco: começa no ombro, puxa para o Ping em 0,5 s
    rf = ease((t - 0.05) / 0.5)
    c.drawImage(BG, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear),
                skia.Paint(ImageFilter=skia.ImageFilters.Blur(2 + 4 * rf, 2 + 4 * rf)))
    sc.beam(c, 560, -60, 1500, 180, 520, a=0.5)
    # Ping (vivo)
    rnd = random.Random(int(tq * 15))
    jx, jy = rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8)
    r = rms_at(tq) / (RMAX or 1)
    vis = viseme(tq)
    mk = vis if (vis and r > 0.06) else ('M' if vis else 'wobble')
    blink = 1.0 if any(0 <= tq - b < 0.1 for b in BLINKS) else 0.0
    squeeze = 4 * ease((tq - 2.85) / 0.3)
    breath = math.sin(tq * 2 * math.pi / 2.6)
    face = dict(mouth_kind=mk, mouth_open=min(1, r * 1.4), blink=blink, nod=nod_at(tq))
    ping_blur = 3.5 * (1 - rf)
    if ping_blur > 0.2:
        c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(ping_blur, ping_blur)))
    c.save(); c.translate(560 + jx, 1500 + jy); c.scale(1, 1 + 0.006 * breath); c.translate(-560, -1500)
    draw_char(c, ch.ping, 560, 1500, 3.15, expr='choro', pose='hold_pot', face=face, squeeze=squeeze)
    c.restore()
    if ping_blur > 0.2:
        c.restore()
    sc.dust(c, 400, 0, 760, 1400, n=60, t=t, seed=3, a=0.6)
    c.restore()
    # ombro do imperador em primeiro plano (parallax maior)
    zs = 1.0 + 0.02 * ease(t / DUR)
    sb = 1.5 + 9 * rf
    c.save(); c.translate(-30 * ease(t / DUR), 0); c.scale(zs, zs)
    c.drawImage(SH, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear),
                skia.Paint(ImageFilter=skia.ImageFilters.Blur(sb, sb)))
    c.restore()
    # legenda: nome em acento antes da fala
    chunks = [(0.18, 1.72, 'Eu cuidei da sua semente'), (1.72, 2.85, 'todo dia,'), (2.85, 9, 'mas ela não nasceu.')]
    cur = None
    for a, b, txt in chunks:
        if a <= t < b:
            cur = (a, txt)
    if cur:
        pop = 0.9 + 0.1 * ease((t - cur[0]) / 0.12)
        c.save(); c.translate(500, 1330); c.scale(pop, pop); c.translate(-500, -1330)
        caption_named(c, 'Ping', cur[1])
        c.restore()
    sc.finish(c, tq, vig=140)
    return surf.makeImageSnapshot()


def caption_named(c, name, line):
    size = 54
    f = skia.Font(pl.FONT['lf700'], size)
    nm = name + ': '
    wn, wl = f.measureText(nm), f.measureText(line)
    base = 1330 + 18
    top = base - size - 250
    c.drawRect(skia.Rect(-100, top, W + 100, H + 100), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, top), skia.Point(0, H)],
        [pl.C((10, 8, 12), 0), pl.C((10, 8, 12), 120 / 255), pl.C((10, 8, 12), 120 / 255)], [0, (base + 40 - top) / (H - top), 1])))
    x = 500 - (wn + wl) / 2
    sh = skia.Paint(AntiAlias=True, Color=pl.C((0, 0, 0), 110 / 255), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.5))
    c.drawString(nm, x + 2, base + 2, f, sh)
    c.drawString(nm, x, base, f, skia.Paint(AntiAlias=True, Color=pl.C((236, 160, 96))))
    c.drawString(line, x + wn + 2, base + 2, f, sh)
    c.drawString(line, x + wn, base, f, skia.Paint(AntiAlias=True, Color=pl.C((247, 241, 230))))


def audio_mix(path):
    sr = 48000
    n = int(DUR * sr)
    t = np.arange(n) / sr
    # voz tratada
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(OFFSET), '-t', str(DUR), '-i', os.path.join(AUD, 'ping_b5.wav'),
                    '-af', 'highpass=f=80,equalizer=f=300:t=q:w=1:g=-2.5,deesser=i=0.4,acompressor=ratio=3:threshold=-18dB,aecho=0.8:0.6:15:0.08,aresample=48000',
                    '-ac', '1', '/tmp/claude-0/voz.wav'], check=True)
    vw = wave.open('/tmp/claude-0/voz.wav'); v = np.frombuffer(vw.readframes(vw.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    voice = np.zeros(n); voice[:min(n, len(v))] = v[:n]
    # pad quente em ré menor + uma nota de violão (Karplus-Strong), bem baixos
    pad = np.zeros(n)
    for f0, a in [(73.42, 0.5), (146.83, 0.35), (174.61, 0.25), (220.0, 0.25)]:
        pad += a * np.sin(2 * np.pi * f0 * t + 0.3 * np.sin(2 * np.pi * 0.2 * t))
    pad *= 0.03 * np.minimum(1, t / 1.0) * np.minimum(1, (DUR - t) / 0.6)

    def pluck(f0, dur, amp):
        N = int(sr / f0); buf = np.random.default_rng(1).uniform(-1, 1, N); out = np.zeros(int(dur * sr))
        for i in range(len(out)):
            out[i] = buf[i % N]; buf[i % N] = 0.996 * 0.5 * (buf[i % N] + buf[(i + 1) % N])
        return amp * out
    gtr = np.zeros(n)
    for st, f0 in [(0.1, 293.66), (2.7, 220.0), (4.2, 174.61)]:
        p = pluck(f0, 1.6, 0.07); i = int(st * sr); gtr[i:i + len(p)] += p[:n - i]
    music = pad + gtr
    # ducking ~70% sob a voz (ataque 40 ms, liberação 300 ms)
    env = np.abs(voice); g = np.zeros(n); cur = 0
    for i in range(0, n, 48):
        tgt = 1.0 if env[i:i + 48].max() > 0.02 else 0.0
        k = 48 / (0.04 * sr) if tgt > cur else 48 / (0.3 * sr)
        cur += (tgt - cur) * min(1, k); g[i:i + 48] = cur
    music *= (1 - 0.7 * g)
    mix = voice + music * 0.55
    mix = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    ow = wave.open('/tmp/claude-0/mix.wav', 'wb'); ow.setnchannels(1); ow.setsampwidth(2); ow.setframerate(sr); ow.writeframes(mix.tobytes()); ow.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/claude-0/mix.wav', '-af', 'alimiter=limit=0.8,loudnorm=I=-14:TP=-1.5', '-ar', '48000', path], check=True)


if __name__ == '__main__':
    os.makedirs('/tmp/claude-0', exist_ok=True)
    audio_mix('/tmp/claude-0/pilot_audio.wav')
    nf = int(DUR * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-i', '/tmp/claude-0/pilot_audio.wav', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                          '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', os.path.join(HERE, 'piloto_ping.mp4')], stdin=subprocess.PIPE)
    for i in range(nf):
        img = frame(i / FPS)
        arr = img.toarray(colorType=skia.ColorType.kBGRA_8888_ColorType)
        p.stdin.write(arr.tobytes())
        if i in (0, 20, 60, 120):
            img.save(f'/tmp/claude-0/pilot_{i:03d}.png')
    p.stdin.close(); p.wait()
    print('ok', nf)
