"""Render final de O Pote Vazio (paper style 2.0)."""
import math, os, re, subprocess, sys, wave
import numpy as np
import skia
import paperlib as pl
import scenes as sc
import shots
from shots import SHOTS, WORDS, DUR, ease
from scenes import W, H

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
TMP = '/tmp/claude-0/render'
os.makedirs(TMP, exist_ok=True)
NAMES = {'ping': 'Ping', 'imperador': 'Imperador'}
TITLE_T = [3.4, 8.0]


# ------------------------------------------------ legenda em trechos de 3–7 palavras
def build_chunks():
    # 1) orações: quebra em pontuação ou troca de bloco/falante
    clauses, cur = [], []
    for w in WORDS:
        if cur and w['block'] != cur[-1]['block']:
            clauses.append(cur); cur = []
        cur.append(w)
        if re.search(r'[.,;?!]$', w['w']):
            clauses.append(cur); cur = []
    if cur:
        clauses.append(cur)
    # 2) oração de 1 palavra junta com a seguinte do mesmo bloco (ou a anterior)
    merged = []
    i = 0
    while i < len(clauses):
        ck = clauses[i]
        if len(ck) == 1 and i + 1 < len(clauses) and clauses[i + 1][0]['block'] == ck[0]['block'] and len(clauses[i + 1]) <= 7:
            merged.append(ck + clauses[i + 1]); i += 2; continue
        if len(ck) == 1 and merged and merged[-1][-1]['block'] == ck[0]['block'] and len(merged[-1]) <= 6:
            merged[-1] = merged[-1] + ck; i += 1; continue
        merged.append(ck); i += 1
    # 3) orações longas divididas em pedaços iguais de até 6 palavras
    out = []
    for ck in merged:
        n = len(ck)
        if n <= 7:
            out.append(ck); continue
        parts = math.ceil(n / 6)
        size = math.ceil(n / parts)
        for j in range(0, n, size):
            out.append(ck[j:j + size])
    res = []
    for i, ck in enumerate(out):
        s = ck[0]['s']
        e = out[i + 1][0]['s'] if i + 1 < len(out) else ck[-1]['e'] + 0.4
        e = min(e, ck[-1]['e'] + 0.9)
        res.append(dict(s=s, e=e, text=' '.join(w['w'] for w in ck), who=ck[0]['who']))
    return res


CHUNKS = build_chunks()


def split_lines(text, font, maxw=860):
    f = skia.Font(pl.FONT['lf700'], 54)
    if f.measureText(text) <= maxw:
        return [text]
    ws = text.split()
    best, bd = None, 1e9
    for k in range(1, len(ws)):
        a, b = ' '.join(ws[:k]), ' '.join(ws[k:])
        d = abs(f.measureText(a) - f.measureText(b))
        if f.measureText(a) <= maxw and f.measureText(b) <= maxw and d < bd and len(ws[k:]) > 1:
            best, bd = [a, b], d
    return best or [text]


def draw_caption(c, t):
    for ck in CHUNKS:
        if ck['s'] <= t < ck['e']:
            name = NAMES.get(ck['who'])
            prefix = (name + ': ') if name else ''
            lines = split_lines(prefix + ck['text'], None)
            pop = 0.9 + 0.1 * ease((t - ck['s']) / 0.12)
            size, lh = 54, 54 * 1.15
            f = skia.Font(pl.FONT['lf700'], size)
            n = len(lines)
            base = 1330 - (n - 1) * lh / 2 + 18
            top = base - size - 250
            c.drawRect(skia.Rect(0, top, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
                [skia.Point(0, top), skia.Point(0, H)],
                [pl.C((10, 8, 12), 0), pl.C((10, 8, 12), 120 / 255), pl.C((10, 8, 12), 120 / 255)], [0, (base + 40 - top) / (H - top), 1])))
            c.save(); c.translate(500, 1330); c.scale(pop, pop); c.translate(-500, -1330)
            sh = skia.Paint(AntiAlias=True, Color=pl.C((0, 0, 0), 110 / 255), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.5))
            for i, line in enumerate(lines):
                y = base + i * lh
                x = 500 - f.measureText(line) / 2
                if i == 0 and prefix:
                    c.drawString(prefix, x + 2, y + 2, f, sh)
                    c.drawString(prefix, x, y, f, skia.Paint(AntiAlias=True, Color=pl.C((236, 160, 96))))
                    rest = line[len(prefix):]
                    xr = x + f.measureText(prefix)
                    c.drawString(rest, xr + 2, y + 2, f, sh)
                    c.drawString(rest, xr, y, f, skia.Paint(AntiAlias=True, Color=pl.C((247, 241, 230))))
                else:
                    c.drawString(line, x + 2, y + 2, f, sh)
                    c.drawString(line, x, y, f, skia.Paint(AntiAlias=True, Color=pl.C((247, 241, 230))))
            c.restore()
            return


# ------------------------------------------------ cartão do livro (cai aos 3,4 s, sai voando ~8 s)
def title_card(c, t):
    t0, t1 = TITLE_T
    if not (t0 <= t < t1 + 0.6):
        return
    if t < t1:
        k = ease((t - t0) / 0.6)
        y = -260 + (265 + 260) * k
        swing = 6 * math.sin((t - t0) * 6) * math.exp(-(t - t0) * 2.2)
    else:
        k = ease((t - t1) / 0.6)
        y = 265 - 600 * k
        swing = -8 * k
    sc_ = 0.7
    pl.SCALE[0] = sc_
    c.save(); c.translate(500, y); c.rotate(swing); c.scale(sc_, sc_)
    pl.layer(c, pl.rr(-330, -120, 330, 110, 10), (244, 234, 212), depth=0.6)
    pl.text(c, 'O Pote Vazio', 0, -10, 84, 'lf900', (52, 38, 34))
    pl.text(c, 'Demi · 1990', 0, 60, 40, 'lorai', (110, 80, 60))
    c.save(); c.translate(140, 128); c.rotate(-5)
    pl.layer(c, pl.rr(-170, -30, 170, 30, 6), (168, 52, 42), depth=0.3)
    pl.text(c, 'ALERTA DE SPOILER', 0, 13, 34, 'lf900', (246, 236, 220))
    c.restore()
    pl.flat(c, pl.circ(0, -96, 9), (180, 60, 50))
    c.restore()
    pl.SCALE[0] = 1


# ------------------------------------------------ transições
def transition(c, kind, prev_img, k):
    """Desenha o plano anterior por cima do novo, revelando o novo conforme k (0→1)."""
    k = ease(k)
    if kind in ('tear_r', 'tear_l'):
        edge = W * (1 - k) if kind == 'tear_r' else W * k
        pts = []
        for i in range(41):
            y = i * H / 40
            pts.append((edge + 18 * math.sin(i * 1.7) + 10 * math.sin(i * 4.1), y))
        if kind == 'tear_r':
            poly = [(-10, -10)] + [(pts[0][0], -10)] + pts + [(pts[-1][0], H + 10), (-10, H + 10)]
        else:
            poly = [(W + 10, -10)] + [(pts[0][0], -10)] + pts + [(pts[-1][0], H + 10), (W + 10, H + 10)]
        p = pl.poly(poly)
        c.save(); c.clipPath(p, doAntiAlias=True); c.drawImage(prev_img, 0, 0); c.restore()
        c.drawPath(p, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=7, Color=pl.C((244, 236, 220), 0.9)))
    elif kind == 'sheet':
        y = H * (1 - k)
        c.save(); c.clipRect(skia.Rect(0, 0, W, y)); c.drawImage(prev_img, 0, 0); c.restore()
        c.drawRect(skia.Rect(0, y - 4, W, y + 18), skia.Paint(Color=pl.C((0, 0, 0), 0.3), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8)))
    elif kind == 'iris':
        r = 1200 * k
        p = skia.Path(); p.addRect(skia.Rect(0, 0, W, H)); p.addCircle(500, 760, r); p.setFillType(skia.PathFillType.kEvenOdd)
        c.save(); c.clipPath(p, doAntiAlias=True); c.drawImage(prev_img, 0, 0); c.restore()
    elif kind in ('page', 'popup'):
        # o plano antigo vira como página (encolhe para a esquerda com sombra)
        w = W * (1 - k)
        c.save(); c.clipRect(skia.Rect(0, 0, w, H))
        c.drawImageRect(prev_img, skia.Rect(0, 0, max(1, w), H), skia.SamplingOptions(skia.FilterMode.kLinear))
        c.drawRect(skia.Rect(w - 60, 0, w, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [skia.Point(w - 60, 0), skia.Point(w, 0)], [pl.C((0, 0, 0), 0), pl.C((0, 0, 0), 0.35)])))
        c.restore()


# ------------------------------------------------ quadro
_PREV = {}


def shot_at(t):
    for i, s in enumerate(SHOTS):
        if s['s'] <= t < s['e']:
            return i
    return len(SHOTS) - 1


def draw_shot(c, i, t):
    s = SHOTS[i]
    d = s['e'] - s['s']; u = t - s['s']
    # cortes internos em planos longos: segunda metade com enquadramento mais fechado
    if d > 5.0 and u > d * 0.52:
        c.save(); c.translate(500, 720); c.scale(1.16, 1.16); c.translate(-500, -720)
        s['fn'](c, u, d, t)
        c.restore()
    else:
        s['fn'](c, u, d, t)


def render_frame(t):
    i = shot_at(t)
    surf = skia.Surface(W, H); c = surf.getCanvas()
    draw_shot(c, i, t)
    s = SHOTS[i]
    if s['trans'] and t - s['s'] < 0.55 and i > 0:
        ps = SHOTS[i - 1]
        ps_surf = skia.Surface(W, H); pc = ps_surf.getCanvas()
        draw_shot(pc, i - 1, s['s'] - 1 / FPS)
        transition(c, s['trans'], ps_surf.makeImageSnapshot(), (t - s['s']) / 0.55)
    title_card(c, t)
    draw_caption(c, t)
    # fade final curto
    sc.finish(c, math.floor(t * 15) / 15, vig=140)
    if t > DUR - 0.6:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=pl.C((8, 6, 10), ease((t - (DUR - 0.6)) / 0.6) * 0.0)))
    return surf.makeImageSnapshot()


# ------------------------------------------------ áudio
def pluck(sr, f0, dur, amp, seed=1):
    N = max(2, int(sr / f0)); buf = np.random.default_rng(seed).uniform(-1, 1, N)
    out = np.zeros(int(dur * sr))
    for i in range(len(out)):
        j = i % N
        out[i] = buf[j]; buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % N])
    # passa-baixa simples
    out = np.convolve(out, np.ones(4) / 4, mode='same')
    return amp * out


def build_audio(path):
    sr = 48000
    n = int((DUR + 0.2) * sr)
    tt = np.arange(n) / sr
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(HERE, 'audio', 'narracao_final.wav'), '-af',
                    'highpass=f=80,equalizer=f=300:t=q:w=1:g=-2.5,deesser=i=0.4,acompressor=ratio=3:threshold=-18dB:attack=10:release=120,aecho=0.8:0.6:15:0.08,aresample=48000',
                    '-ac', '1', f'{TMP}/voz.wav'], check=True)
    vw = wave.open(f'{TMP}/voz.wav'); v = np.frombuffer(vw.readframes(vw.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    voice = np.zeros(n); voice[:min(n, len(v))] = v[:n]
    # trilha: violão lento (0,6 s por nota) Dm–Bb–F–C + pad, some no respiro; drone no conflito
    chords = [[146.83, 174.61, 220.0, 293.66], [116.54, 146.83, 174.61, 233.08], [87.31, 130.81, 174.61, 220.0], [130.81, 164.81, 196.0, 261.63]]
    music = np.zeros(n)
    t_ = 0.2; k = 0; seed = 3
    climax = shots.W_('as', 3)
    while t_ < DUR - 1.2:
        ch_ = chords[(k // 4) % 4]
        f0 = ch_[k % 4]
        step = 0.65 if not (climax - 1 < t_ < climax + 5) else 1.5
        p = pluck(sr, f0, 1.8, 0.08, seed); i = int(t_ * sr); music[i:i + len(p)] += p[:max(0, n - i)]
        t_ += step; k += 1; seed += 1
    # acorde final (ré maior: resolve)
    for j, f0 in enumerate([146.83, 185.0, 220.0, 293.66]):
        p = pluck(sr, f0, 2.5, 0.07, 90 + j); i = int((DUR - 1.4 + j * 0.06) * sr); music[i:i + len(p)] += p[:max(0, n - i)]
    pad = np.zeros(n)
    for f0, a in [(73.42, 0.5), (146.83, 0.3), (220.0, 0.2)]:
        pad += a * np.sin(2 * np.pi * f0 * tt + 0.3 * np.sin(2 * np.pi * 0.17 * tt))
    pad *= 0.022
    # drone grave no conflito (vergonha → palácio)
    d0, d1 = shots.W_('na', 1), shots.W_('eu', 3)
    drone = 0.03 * np.sin(2 * np.pi * 55 * tt) * np.clip(np.minimum((tt - d0) / 2, (d1 - tt) / 1.5), 0, 1)
    music += pad + drone
    fade = np.clip((DUR - tt) / 0.7, 0, 1)
    music *= fade
    # efeitos: whoosh nas transições, plic nas gags, tok no vaso
    sfx = np.zeros(n)
    rng = np.random.default_rng(5)
    for s in SHOTS:
        if s['trans']:
            i = int(max(0, s['s'] - 0.05) * sr); L = int(0.5 * sr)
            noise = rng.normal(0, 1, L) * np.hanning(L) * 0.05
            noise = np.convolve(noise, np.ones(30) / 30, mode='same')
            sfx[i:i + L] += noise[:max(0, n - i)]
    def plic(at, f0=1400, amp=0.12):
        i = int(at * sr); L = int(0.09 * sr); e = np.exp(-np.arange(L) / (0.015 * sr))
        sfx[i:i + L] += (amp * np.sin(2 * np.pi * f0 * np.arange(L) / sr) * e)[:max(0, n - i)]
    for s in SHOTS:
        if s['fn'] is shots.s_seasons:
            d = s['e'] - s['s']
            for j in range(3):
                plic(s['s'] + j * d / 3 + 0.05, 1300 + j * 120, 0.09)
        if s['fn'] is shots.s_big_pot:
            plic(s['s'] + 0.02, 420, 0.18)
        if s['fn'] is shots.s_garden:
            for j in range(9):
                plic(s['s'] + 0.25 * j + 0.1, 1500 + j * 60, 0.05)
    # ducking ~70% da música sob a voz (ataque 40 ms, liberação 300 ms)
    env = np.abs(voice); g = np.zeros(n); cur = 0.0; hop = 48
    for i in range(0, n, hop):
        tgt = 1.0 if env[i:i + hop].max() > 0.02 else 0.0
        kk = hop / (0.04 * sr) if tgt > cur else hop / (0.3 * sr)
        cur += (tgt - cur) * min(1, kk); g[i:i + hop] = cur
    music *= (1 - 0.7 * g)
    mix = voice + music * 0.55 + sfx * 0.6
    mix = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    ow = wave.open(f'{TMP}/mix.wav', 'wb'); ow.setnchannels(1); ow.setsampwidth(2); ow.setframerate(sr); ow.writeframes(mix.tobytes()); ow.close()
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{TMP}/mix.wav', '-af', 'alimiter=limit=0.8,loudnorm=I=-14:TP=-1.5',
                    '-ar', '48000', '-ac', '2', path], check=True)


def render_part(a, b, out):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for f in range(a, b):
        img = render_frame(f / FPS)
        p.stdin.write(img.toarray(colorType=skia.ColorType.kBGRA_8888_ColorType).tobytes())
        if f % 150 == 0:
            print('frame', f, flush=True)
    p.stdin.close(); p.wait()


if __name__ == '__main__':
    mode = sys.argv[1]
    NF = int(math.ceil(DUR * FPS))
    if mode == 'part':
        k, K = int(sys.argv[2]), int(sys.argv[3])
        a = NF * k // K; b = NF * (k + 1) // K
        render_part(a, b, f'{TMP}/part{k}.mp4')
    elif mode == 'audio':
        build_audio(f'{TMP}/audio.wav')
    elif mode == 'still':
        t = float(sys.argv[2]); render_frame(t).save(sys.argv[3])
