"""Planos de O Pote Vazio. Cada plano: f(c, u, t) desenha o quadro inteiro (u = segundos dentro do plano)."""
import json, math, os, random, wave
import numpy as np
import skia
import paperlib as pl
import characters as ch
import scenes as sc
from scenes import W, H
from style_frames import palace_crowd, row_of_kids, front_pots, draw_char, outside_parade

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
WORDS = TL['words']
DUR = TL['duration']


def norm(w):
    return ''.join(ch_ for ch_ in w.lower() if ch_.isalpha() or ch_ in 'áéíóúâêôãõàç')


def W_(word, n=1):
    k = 0
    for w in WORDS:
        if norm(w['w']) == word:
            k += 1
            if k == n:
                return w['s']
    raise KeyError((word, n))


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def back_out(x, o=1.08):
    x = max(0.0, min(1.0, x)); s = 1.70158 * (o - 1) * 10
    x -= 1; return x * x * ((s + 1) * x + s) + 1


# ------------------------------------------------ voz -> boca
_sr = 24000
_w = wave.open(os.path.join(HERE, 'audio', 'narracao_final.wav'))
_sr = _w.getframerate()
_X = np.frombuffer(_w.readframes(_w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def rms(t):
    i = int(t * _sr); seg = _X[max(0, i - 500):i + 500]
    return float(np.sqrt((seg ** 2).mean())) if len(seg) else 0.0


_RMAX = 0.12


def speaking(t, who):
    for w in WORDS:
        if w['who'] == who and w['s'] <= t < w['e']:
            return w
    return None


def viseme(t, who):
    w = speaking(t, who)
    if not w:
        return None, 0.0
    letters = [x for x in w['w'].lower() if x.isalpha()]
    k = min(len(letters) - 1, int((t - w['s']) / max(0.01, w['e'] - w['s']) * len(letters)))
    for j in range(k, -1, -1):
        L = letters[j]
        if L in 'aáàã': v = 'A'; break
        if L in 'eéêií': v = 'E'; break
        if L in 'oóôõ': v = 'O'; break
        if L in 'uú': v = 'U'; break
        if L in 'mbp': v = 'M'; break
    else:
        v = 'E'
    r = rms(t) / _RMAX
    return (v if r > 0.08 else 'M'), min(1.0, r)


def ping_face(t, base_mouth=None, blinks=(), nod=0.0, hat=False):
    v, op = viseme(t, 'ping')
    f = dict(mouth_kind=v or base_mouth, mouth_open=op, nod=nod, hat=hat)
    f['blink'] = 1.0 if any(0 <= t - b < 0.1 for b in blinks) or (int(t * 10) % 37 == 0) else 0.0
    return f


def imp_face(t):
    v, op = viseme(t, 'imperador')
    mk = None
    if v:
        mk = {'A': 'o', 'O': 'o', 'U': 'o', 'E': 'smile', 'M': 'gentle'}[v] if op > 0.15 else 'gentle'
    return dict(mouth_kind=mk, blink=1.0 if int(t * 10) % 41 == 0 else 0.0)


def cam(c, u, d, z0, z1, cx=500, cy=760, dx0=0, dx1=0, dy0=0, dy1=0):
    k = ease(u / max(0.01, d))
    z = z0 + (z1 - z0) * k
    c.translate(500, 760); c.scale(z, z); c.translate(-cx - (dx0 + (dx1 - dx0) * k), -cy - (dy0 + (dy1 - dy0) * k))


# ------------------------------------------------ caches de fundo
_CACHE = {}


def cached(key, fn):
    if key not in _CACHE:
        s = skia.Surface(W, H); c = s.getCanvas(); fn(c); _CACHE[key] = s.makeImageSnapshot()
    return _CACHE[key]


def img(c, im, blur=0):
    p = skia.Paint(ImageFilter=skia.ImageFilters.Blur(blur, blur)) if blur else None
    c.drawImage(im, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear), p)


# ================================================= planos
def s_cover(c, u, d, t):
    c.save(); cam(c, u, d, 1.0, 1.06, cx=520, cy=820)
    img(c, cached('palace', lambda c: palace_crowd(c)))
    sc.beam(c, 480, -40, 1340, 200, 460, a=0.5)
    # imperador passa sério e, ao chegar no Ping, sorri
    walk = ease(u / 2.2)
    ex = 960 - 190 * walk
    expr = 'testa_franzida' if u < 2.4 else 'sorriso'
    c.save(); c.rotate(-5 * walk, ex, 1210)
    draw_char(c, ch.imperador, ex, 1210, 1.68, expr=expr, pose='sleeves' if u < 2.4 else 'beard')
    c.restore()
    draw_char(c, ch.ping, 450, 1300, 2.15, expr='choro', pose='hold_pot', face=dict(blink=0.0))
    sc.dust(c, 330, 80, 640, 1280, n=70, t=t, seed=3)
    c.restore()
    img(c, cached('front_pots', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)))


def s_ots_smile(c, u, d, t):
    """Close: o imperador sorri para o menino que chora (sobre o ombro do Ping => rosto do imperador)."""
    c.save(); cam(c, u, d, 1.12, 1.18, cx=560, cy=640)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=5)
    sc.beam(c, 600, -60, 1500, 200, 520, a=0.45)
    draw_char(c, ch.imperador, 600, 1700, 2.6, expr='sorriso', pose='beard', face=imp_face(t))
    c.restore()
    # Ping de costas, desfocado, em primeiro plano
    sc.blurred(c, lambda c: ping_back(c, 250, 2050, 3.4), 7)


def ping_back(c, x, y, s):
    """Ping de costas (para planos sobre o ombro)."""
    P = ch.PING
    c.save(); c.translate(x, y); c.scale(s, s); pl.SCALE[0] = s
    pl.layer(c, sc.smooth([(-60, -60), (-52, -190), (0, -200), (52, -190), (60, -60)], tension=0.4), P['tunic'])
    pl.layer(c, pl.rr(-16, -206, 16, -192, 5), P['collar'])
    for k in (-1, 1):
        pl.layer(c, pl.ell(k * 60, -268, 9, 12), P['skin'])
    pl.layer(c, sc.smooth([(-66, -232), (-68, -290), (-50, -330), (0, -342), (50, -330), (68, -290), (66, -232)], tension=0.4), P['hair'])
    for x0 in (-40, -20, 0, 20, 40):
        pl.ink(c, [(x0 * 0.7, -334), (x0, -280), (x0 * 1.05, -236)], 2, P['hair_hi'], 0.6, 0.6)
    pl.layer(c, pl.rr(-50, -144, 50, -128, 4), P['sash'])
    c.restore(); pl.SCALE[0] = 1


def s_garden(c, u, d, t):
    """Um ano antes: tudo que Ping toca floresce."""
    c.save(); cam(c, u, d, 1.08, 1.12, cx=520, cy=800)
    img(c, cached('garden_bg', lambda c: (sc.season_outside(c, 'primavera', 0, -60, -60, W + 60, 1300),
                                          pl.layer(c, pl.rr(-60, 1180, W + 60, H + 60, 1), (126, 170, 96), depth=0.1, shadow=False, rim=False))))
    rnd = random.Random(4)
    for i in range(9):
        x = 90 + i * 110 + rnd.uniform(-20, 20); y = 1180 + (i % 2) * 70
        g = back_out((u - 0.25 * i) / 0.5)
        if g > 0.01:
            c.save(); c.translate(x, y); c.scale(g, g); pl.SCALE[0] = g
            sc.leaf(c, 0, 0, -120, 50); sc.leaf(c, 0, 0, -60, 50)
            (sc.peony if i % 2 else sc.mum)(c, 0, -60, 34, sc.GLOSSY[i % 7], 0.15, i)
            c.restore(); pl.SCALE[0] = 1
    px = 300 + 380 * ease(u / d)
    draw_char(c, ch.ping, px, 1330, 2.1, expr='encanto', pose='down', face=dict(nod=2 * math.sin(t * 9)))
    c.restore()


def s_plaza(c, u, d, t):
    c.save(); cam(c, u, d, 1.08, 1.12, cx=520, cy=780)
    img(c, cached('plaza', lambda c: sc.plaza_bg(c)))
    draw_char(c, ch.imperador, 540, 790, 0.9, expr='sereno', pose='sleeves')
    for row, (y, s_, xs) in enumerate([(1180, 0.9, [140, 330, 520, 710, 900]), (1400, 1.15, [60, 300, 560, 820, 1060])]):
        for i, x in enumerate(xs):
            c.save(); c.translate(x, y); c.scale(s_, s_); pl.SCALE[0] = s_
            sc.child(c, 0, 0, 1.0, row * 10 + i, part='back')
            c.restore(); pl.SCALE[0] = 1
    c.restore()


def s_seed(c, u, d, t):
    """Close de objeto: a semente passa da mão do imperador para a mão do Ping."""
    c.save(); cam(c, u, d, 1.08, 1.14, cx=520, cy=780)
    img(c, cached('plaza', lambda c: sc.plaza_bg(c)), blur=9)
    pl.SCALE[0] = 1.0
    P, Q = ch.IMP, ch.PING
    k = ease(u / 1.2)
    # manga + mão grande do imperador (de cima)
    sl = sc.smooth([(-100, 200), (380, 420), (520, 560), (440, 640), (-100, 520)], tension=0.4)
    pl.layer(c, sl, P['robe'], depth=0.4)
    pl.layer(c, pl.rr(400, 520, 470, 600, 20), P['panel'], depth=0.1)
    pl.layer(c, pl.ell(520, 640 + 20 * k, 70, 50), P['skin'], depth=0.3)
    for f in range(4):
        pl.layer(c, pl.rr(470 + f * 24, 650 + 20 * k, 492 + f * 24, 720 + 20 * k, 11), pl.mul(P['skin'], 0.97), depth=0.15, seed=f)
    # mãozinhas em concha do Ping
    for s_ in (-1, 1):
        pl.layer(c, pl.ell(520 + s_ * 52, 1060, 70, 48), Q['skin'], depth=0.3, seed=10 + s_)
    pl.layer(c, pl.rr(380, 1080, 660, 1300, 40), Q['tunic'], depth=0.3)
    # semente caindo, brilhando
    sy = 700 + 340 * ease((u - 0.6) / 0.8)
    pl.flat(c, pl.circ(520, sy, 46), (255, 230, 150), 0.35, blur=20)
    pl.layer(c, pl.ell(520, sy, 12, 16), (150, 104, 60), depth=0.1)
    c.restore()


def s_emperor_speaks(c, u, d, t):
    c.save(); cam(c, u, d, 1.1, 1.16, cx=520, cy=700)
    img(c, cached('plaza', lambda c: sc.plaza_bg(c)), blur=6)
    draw_char(c, ch.imperador, 520, 1650, 2.5, expr='sereno', pose='beard', face=imp_face(t))
    c.restore()


def window_room(c, season, t, pot_x=640, with_ping=False, u=0.0):
    sc.house_bg(c)
    sc.window(c, 300, 260, 1000, 960, outside=lambda c: sc.season_outside(c, season, t, 300, 260, 1000, 960))
    sc.sill(c, 260, 1040, 960)
    c.save(); c.translate(pot_x, 960); c.scale(2.6, 2.6); pl.SCALE[0] = 2.6
    ch.pot(c, 0, 0, 1.0); c.restore(); pl.SCALE[0] = 1


def s_water(c, u, d, t):
    c.save(); cam(c, u, d, 1.08, 1.12, cx=520, cy=820)
    img(c, cached('room_prim', lambda c: window_room(c, 'primavera', 0)))
    sc.beam(c, 640, 260, 1500, 500, 800, a=0.2)
    draw_char(c, ch.ping, 330, 1500, 2.6, expr='concentrado', pose='down')
    # regador e gotas
    pl.SCALE[0] = 1
    pl.layer(c, pl.rr(380, 1020, 470, 1080, 14), (90, 130, 150), depth=0.2)
    pl.ink(c, [(470, 1040), (540, 980)], 8, (90, 130, 150), 1, 6)
    for i in range(5):
        y = 990 + ((t * 300 + i * 30) % 120)
        pl.flat(c, pl.ell(560 + i * 6, y, 3, 5), (160, 200, 230), 0.9)
    c.restore()


SEASONS = ['verao', 'outono', 'inverno']


def s_seasons(c, u, d, t):
    seg = min(2, int(u / (d / 3)))
    c.save(); cam(c, u, d, 1.06, 1.06, cx=650, cy=760)
    img(c, cached('room_' + SEASONS[seg], lambda c: window_room(c, SEASONS[seg], 0)))
    pl.SCALE[0] = 1
    # pardal: pousa, espia o pote, vai embora decepcionado (😄)
    v = (u % (d / 3)) / (d / 3)
    bx = 900 - 140 * ease(v / 0.3) + (400 * ease((v - 0.75) / 0.25))
    by = 950 - 30 * math.sin(min(1, v / 0.3) * math.pi) - 200 * ease((v - 0.75) / 0.25)
    expr = 'curioso' if v < 0.55 else 'decepcionado'
    c.save(); c.translate(bx, by); c.scale(-3.0 if v < 0.75 else 3.0, 3.0); pl.SCALE[0] = 3.0
    ch.pardal(c, expr); c.restore(); pl.SCALE[0] = 1
    c.restore()


def s_big_pot(c, u, d, t):
    c.save(); cam(c, u, d, 1.08, 1.08, cx=520, cy=820)
    img(c, cached('room_inv', lambda c: (sc.house_bg(c), sc.window(c, 300, 200, 900, 800, outside=lambda c: sc.season_outside(c, 'inverno', 0, 300, 200, 900, 800)))))
    pl.SCALE[0] = 1
    g = back_out(u / 0.5)
    c.save(); c.translate(680, 1440); c.scale(8.5 * g, 8.5 * g); pl.SCALE[0] = 8.5
    ch.pot(c, 0, 0, 1.0); c.restore(); pl.SCALE[0] = 1
    draw_char(c, ch.ping, 260, 1420, 2.1, expr='decepcionado', pose='down', face=dict(nod=-3 * ease((u - 0.8) / 0.3)))
    c.restore()


def s_parade(c, u, d, t):
    c.save(); cam(c, u, d, 1.0, 1.05, cx=520, cy=800)
    pl.STYLE['light'] = (-0.75, -0.66)
    sc.house_bg(c)
    def outside(c):
        outside_parade(c)
    sc.window(c, 400, 200, 1060, 860, outside=lambda c: (c.save(), c.translate(-120 * ease(u / d), 0), outside(c), c.restore()))
    sc.beam(c, 640, 520, 1600, 420, 760, a=0.22)
    draw_char(c, ch.ping, 360, 1600, 3.0, expr='vergonha', pose='hide_pot')
    pl.STYLE['light'] = (-0.55, -0.83)
    c.restore()


def s_ping_pai(c, u, d, t):
    """Sobre o ombro do pai: Ping pede (fala)."""
    c.save(); cam(c, u, d, 1.1, 1.14, cx=520, cy=760)
    img(c, cached('room_prim2', lambda c: sc.house_bg(c)), blur=5)
    draw_char(c, ch.ping, 520, 1640, 3.2, expr='vergonha', pose='hide_pot', face=ping_face(t, 'wobble'))
    c.restore()
    def pai_back(c):
        c.save(); c.translate(980, 2100); c.scale(3.6, 3.6); pl.SCALE[0] = 3.6
        P = ch.PAI
        pl.layer(c, sc.smooth([(-100, -40), (-90, -280), (0, -300), (90, -280), (100, -40)], tension=0.4), P['tunic'])
        pl.layer(c, pl.ell(-20, -230, 70, 48), P['straw'])
        for k in (-1, 1):
            pl.layer(c, pl.ell(k * 48, -350, 8, 12), P['skin'])
        pl.layer(c, pl.rr(-50, -410, 50, -300, 26), P['hair'])
        pl.layer(c, pl.rr(-22, -312, 22, -290, 6), P['skin'])
        c.restore(); pl.SCALE[0] = 1
    sc.blurred(c, pai_back, 9)


def s_pai_hand(c, u, d, t):
    c.save(); cam(c, u, d, 1.08, 1.12, cx=560, cy=780)
    img(c, cached('room_prim2', lambda c: sc.house_bg(c)), blur=3)
    sc.beam(c, 300, 0, 1500, 300, 600, a=0.18)
    reach = ease(u / 0.8)
    expr_p = 'choro' if u < 1.8 else 'coragem'
    draw_char(c, ch.ping, 420, 1560, 2.7, expr=expr_p, pose='hold_pot' if u > 1.6 else 'hide_pot')
    c.save(); c.translate(820, 1580); c.scale(-1, 1); c.translate(-820, -1580)
    draw_char(c, ch.pai, 820, 1580, 2.7, expr='apoio' if u > 0.6 else 'terno', pose='apoio')
    c.restore()
    c.restore()


def s_palace_wide(c, u, d, t):
    c.save(); cam(c, u, d, 1.0, 1.08, cx=520, cy=900)
    img(c, cached('palace', lambda c: palace_crowd(c)))
    sc.beam(c, 520, -40, 1340, 200, 460, a=0.3)
    px = 520; py = 1100 + 60 * ease(u / d)
    draw_char(c, ch.ping, px, py, 1.3, expr='decepcionado', pose='hold_pot')
    c.restore()
    img(c, cached('front_pots', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)))


def s_emperor_walk(c, u, d, t):
    c.save(); cam(c, u, d, 1.12, 1.12, cx=520, cy=760)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=4)
    bob = 6 * abs(math.sin(t * 3.2))
    draw_char(c, ch.imperador, 400, 1700 - bob, 2.5, expr='testa_franzida', pose='sleeves')
    c.restore()
    # flores passando em primeiro plano (travelling)
    off = (u * 260) % 520
    sc.blurred(c, lambda c: front_pots(c, (1100 - off, 580 - off, 1620 - off), s=2.4, base=2000), 10)


def s_emperor_asks(c, u, d, t):
    c.save(); cam(c, u, d, 1.14, 1.2, cx=540, cy=620)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=6)
    sc.beam(c, 560, -60, 1500, 200, 500, a=0.35)
    c.save(); c.rotate(4, 560, 1700)
    draw_char(c, ch.imperador, 560, 1700, 2.7, expr='pergunta', pose='sleeves', face=imp_face(t))
    c.restore()
    c.restore()


def s_ping_answer(c, u, d, t):
    import pilot
    c.save(); cam(c, u, d, 1.08, 1.13, cx=520, cy=760)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=6)
    sc.beam(c, 560, -60, 1500, 180, 520, a=0.5)
    draw_char(c, ch.ping, 560, 1500, 3.15, expr='choro', pose='hold_pot',
              face=ping_face(t, 'wobble'), squeeze=4 * ease((u - 2.4) / 0.3))
    sc.dust(c, 400, 0, 760, 1400, n=60, t=t, seed=3, a=0.6)
    c.restore()
    img(c, pilot.SH, blur=1.5 + 9 * ease(u / 0.5))


def s_reveal(c, u, d, t):
    c.save(); cam(c, u, d, 1.16, 1.24, cx=540, cy=600)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=6)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=pl.C((14, 18, 26), 0.3 * ease(u / d))))
    sc.beam(c, 540, -60, 1500, 200, 500, a=0.4)
    draw_char(c, ch.imperador, 640, 1720, 2.8, expr='sereno', pose='beard', face=imp_face(t))
    c.restore()
    sc.blurred(c, lambda c: ping_back(c, 170, 2080, 3.2), 7)


def s_climax(c, u, d, t):
    g = ease(u / 1.4) * 0.88
    c.save(); cam(c, u, d, 1.0, 1.05, cx=520, cy=820)
    gi = int(g * 8) / 8
    img(c, cached(f'palace_g{gi}', lambda c: palace_crowd(c, gray=gi, lowered=gi > 0.5)))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=pl.C((14, 18, 26), 0.45 * g)))
    sc.beam(c, 430, -40, 1290, 170, 440, a=0.3 + 0.32 * ease(u / 1.4))
    pl.flat(c, pl.ell(430, 1262, 210, 46), (255, 226, 160), 0.35 * ease(u / 1.4), blur=20)
    c.save(); c.rotate(-5, 770, 1240)
    draw_char(c, ch.imperador, 770, 1240, 1.7, expr='sereno', pose='sleeves')
    c.restore()
    draw_char(c, ch.ping, 430, 1262, 1.95, expr='coragem', pose='hold_pot')
    sc.dust(c, 330, 80, 610, 1250, n=60, t=t, seed=8)
    c.restore()
    img(c, cached(f'front_pots_g{gi}', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990), gray=gi), 9)))


def s_end(c, u, d, t):
    c.save(); cam(c, u, d, 1.04, 1.1, cx=540, cy=820)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=3)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=pl.C((255, 220, 160), 0.12)))
    sc.beam(c, 520, -40, 1340, 240, 560, a=0.45)
    c.save(); c.rotate(-4, 760, 1230)
    draw_char(c, ch.imperador, 760, 1230, 1.72, expr='sorriso', pose='sleeves')
    c.restore()
    c.save(); c.translate(820, 1230 - 340 * 1.72); c.scale(-2.2, 2.2); pl.SCALE[0] = 2.2
    ch.pardal(c, 'curioso'); c.restore(); pl.SCALE[0] = 1
    draw_char(c, ch.ping, 430, 1300, 2.1, expr='alegria', pose='hold_pot', face=dict(hat=True))
    sc.dust(c, 300, 80, 760, 1280, n=60, t=t, seed=9)
    c.restore()
    img(c, cached('front_pots', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)))


# ------------------------------------------------ lista de planos ancorada nas palavras
def build_shots():
    A = [
        (0.0, s_cover, 'abertura: imperador passa e sorri para o vaso vazio', ''),
        (W_('só', 1), s_ots_smile, 'close: o sorriso do imperador', ''),
        (W_('um', 2) - 0.1, s_garden, 'um ano antes: tudo floresce', 'page'),
        (W_('o', 1) if False else W_('imperador', 2) - 0.25, s_plaza, 'praça: o imperador sem filhos', 'tear_r'),
        (W_('deu', 1), s_seed, 'close: a semente', ''),
        (W_('quem', 1) - 0.15, s_emperor_speaks, 'contra-plongée: o concurso', ''),
        (W_('ping', 3) - 0.2, s_water, 'Ping planta e rega', 'sheet'),
        (W_('nada', 1), s_seasons, 'janela: estações + pardal 😄', ''),
        (W_('passou', 1), s_big_pot, 'o vaso enorme 😄', ''),
        (W_('na', 1) - 0.2, s_parade, 'o desfile pela janela: vergonha', 'iris'),
        (W_('pai', 1) - 0.15, s_ping_pai, 'Ping pede ao pai', ''),
        (W_('mas', 1) - 0.1, s_pai_hand, 'a mão do pai no ombro', ''),
        (W_('então', 1) - 0.2, s_palace_wide, 'palácio: o vaso vazio no mar de cor', 'popup'),
        (W_('imperador', 4) - 0.1, s_emperor_walk, 'o imperador de testa franzida', ''),
        (W_('por', 2) - 0.1, s_emperor_asks, 'a pergunta', ''),
        (W_('eu', 2) - 0.25, s_ping_answer, 'a verdade (sobre o ombro)', ''),
        (W_('eu', 3) - 0.45, s_reveal, 'a revelação', ''),
        (W_('as', 3) - 0.15, s_climax, 'clímax: as flores perdem a cor', ''),
        (W_('o', 6) - 0.2 if False else W_('menino', 2) - 0.3, s_end, 'fim: o menino do vaso vazio', 'tear_l'),
    ]
    out = []
    for i, (s0, fn, label, trans) in enumerate(A):
        e0 = A[i + 1][0] if i + 1 < len(A) else DUR
        out.append(dict(s=max(0.0, s0), e=e0, fn=fn, label=label, trans=trans))
    return out


SHOTS = build_shots()
