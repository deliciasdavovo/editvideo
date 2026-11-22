"""Personagens de papel + tecido: Burro, Cachorro, Gato, Galo, ladrões, rato, coruja.
Todos de frente para a direita (exceto gato sentado e ladrões, de frente). Origem no chão."""
from lib import *

# paletas
BUR = dict(body=(140, 126, 114), muzzle=(226, 208, 178), mane=(64, 50, 46), ear_in=(222, 176, 160), scarf=(132, 36, 42),
           bl=(50, 92, 120), bl2=(200, 150, 62), hoof=(70, 58, 52))
DOG = dict(body=(236, 218, 188), patch=(176, 100, 54), ear=(168, 92, 48), nose=(48, 38, 40), scarf=(36, 112, 116))
CAT = dict(body=(126, 134, 152), chest=(236, 224, 202), cape=(124, 34, 46), gold=(214, 172, 72), eye=(196, 202, 92), ear_in=(214, 160, 160))
ROO = dict(o1=(218, 112, 40), o2=(226, 164, 64), comb=(200, 40, 38), tail=(34, 104, 112), tail2=(22, 70, 82), vest=(46, 78, 120),
           leg=(232, 176, 60), beak=(236, 190, 70))
INK = (44, 32, 30)
WHITE = (246, 240, 228)
PUPIL = (30, 24, 26)


def _p(c, path, col, depth=0.4, sil=None, a=255, **kw):
    layer(c, path, col, depth, a=a, sil=sil, **kw)


@functools.lru_cache(None)
def J(key):
    """geometria cacheada com borda cortada à mão"""
    return jag(GEOM[key](), amp=1.2, seed=hash(key) % 97)


GEOM = {}


def geom(name):
    def deco(f):
        GEOM[name] = f
        return f
    return deco


def eye(c, x, y, rx, ry, lid=0.0, look=(0, 0), sil=None, a=255, pupil_r=None, lid_col=None, low_lid=0.0, slit=False, iris=None):
    if sil is not None:
        return
    e = oval(x, y, rx, ry)
    fill(c, e, WHITE, a)
    c.save()
    c.clipPath(e, skia.ClipOp.kIntersect, True)
    pr = pupil_r or min(rx, ry) * 0.62
    px, py = x + look[0] * rx * 0.35, y + look[1] * ry * 0.3
    if iris:
        fill(c, circ(px, py, pr * 1.25), iris, a)
    if slit:
        fill(c, oval(px, py, pr * 0.32, pr * 1.05), PUPIL, a)
    else:
        fill(c, circ(px, py, pr), PUPIL, a)
    fill(c, circ(px + pr * 0.35, py - pr * 0.4, pr * 0.32), (255, 255, 255), a)
    if lid > 0:
        lc = lid_col or (120, 110, 100)
        fill(c, skia.Path().addRect if False else rr(x - rx - 2, y - ry - 2, x + rx + 2, y - ry + 2 * ry * lid, 2), lc, a)
    if low_lid > 0:
        lc = lid_col or (120, 110, 100)
        fill(c, rr(x - rx - 2, y + ry - 2 * ry * low_lid, x + rx + 2, y + ry + 2, 2), lc, a)
    c.restore()
    # linha da pálpebra
    ly = y - ry + 2 * ry * lid
    if lid >= 0.92:
        ink(c, smooth([(x - rx, y + 1), (x, y + ry * 0.45), (x + rx, y + 1)], False), INK, a * 0.9, 2.6)
    else:
        ink(c, smooth([(x - rx, ly + ry * 0.25), (x, ly - ry * 0.05), (x + rx, ly + ry * 0.25)], False), INK, a * 0.85, 2.4)


# =============================================================== BURRO
@geom('bur_body')
def _():
    return smooth([(-150, -300), (-90, -338), (0, -345), (90, -338), (150, -305), (168, -258), (142, -206), (60, -180),
                   (-40, -178), (-128, -196), (-168, -248)])


@geom('bur_thigh')
def _():
    return tp([(0, 0), (1, 60), (2, 120)], 50, 30)


@geom('bur_shin')
def _():
    return tp([(0, 0), (0, 55), (0, 102)], 27, 22)


@geom('bur_hoof')
def _():
    return rr(-15, 96, 17, 118, 7)


@geom('bur_neck')
def _():
    return smooth([(60, -322), (110, -392), (150, -452), (212, -440), (196, -380), (166, -300)])


@geom('bur_head')
def _():
    return union(oval(8, -24, 58, 50), oval(48, -2, 54, 40))


@geom('bur_muzzle')
def _():
    return rot_about(oval(82, 12, 62, 43), 18, 82, 12)


@geom('bur_ear')
def _():
    return smooth([(0, 0), (-24, -48), (-22, -112), (0, -158), (20, -112), (22, -48)])


@geom('bur_ear_in')
def _():
    return smooth([(0, -18), (-12, -52), (-10, -108), (0, -138), (9, -108), (11, -52)])


@geom('bur_tail')
def _():
    return tp([(0, 0), (-22, 42), (-30, 92), (-26, 132)], 13, 6)


@geom('bur_tuft')
def _():
    return smooth([(-38, 120), (-14, 118), (-12, 150), (-26, 176), (-40, 152)])


@geom('bur_scarf')
def _():
    return smooth([(98, -352), (150, -372), (176, -340), (124, -312), (100, -322)])


@geom('bur_scarf_tail')
def _():
    return tp([(0, 0), (10, 38), (2, 78)], 26, 14)


@geom('bur_blanket')
def _():
    return smooth([(-112, -326), (-40, -350), (52, -348), (108, -322), (114, -250), (-2, -244), (-118, -246)])


@geom('bur_mane')
def _():
    return tp([(66, -330), (98, -380), (128, -424), (150, -456)], 30, 18)


@geom('bur_tuftfore')
def _():
    return smooth([(-20, -66), (-2, -92), (14, -74), (30, -88), (34, -60), (8, -50)])


def burro(c, x, y, s=1.0, flip=False, pose=None, sil=None, a=255):
    """pose: walk (fase, 0=parado), head (graus), ears (0 em pé .. 1 caído), ear_wig, eyes (pálpebra 0..1),
    look (dx,dy), brow (-1 triste .. 1 decidido), mouth ('smile','neutral','sad','open'), m (abertura 0..1),
    tail (graus), breath, chest (estufar 0..1), knees (flexão 0..1)"""
    p = dict(walk=0, step=0.0, head=0, ears=0, ear_wig=0, eyes=0.12, look=(0.3, 0), brow=0, mouth='smile', m=0, tail=0,
             breath=0, chest=0, knees=0, blush=1)
    p.update(pose or {})
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    bc = BUR['body']
    ph = p['step']
    amp = 18 if p['walk'] else 0
    kn = p['knees']
    # pernas (de trás primeiro, mais escuras)
    legs = [(-92, -236, 0.0, 0.82), (104, -236, 0.5, 0.82), (-108, -236, 0.5, 1.0), (92, -236, 0.0, 1.0)]
    lie = p.get('lie', 0)
    bob = -abs(math.sin(ph * 2 * math.pi)) * 6 * (1 if p['walk'] else 0) + kn * 22 + lie * 150
    for hx, hy, off, k in legs:
        ang = amp * math.sin((ph + off) * 2 * math.pi) + lie * (-82 if hx > 0 else 82)
        knee = max(0, -amp * 1.1 * math.sin((ph + off) * 2 * math.pi + 1.2)) + kn * 25 + lie * 230
        c.save()
        c.translate(hx, hy + bob)
        c.rotate(ang - kn * 12)
        _p(c, J('bur_thigh'), shade(bc, k), 0.25, sil, a)
        c.translate(2, 118)
        c.rotate(knee * (1 if hx > 0 else -1) * 0.6 + kn * 24)
        _p(c, J('bur_shin'), shade(bc, k * 0.95), 0.2, sil, a)
        _p(c, J('bur_hoof'), BUR['hoof'], 0.1, sil, a)
        c.restore()
    c.translate(0, bob)
    # rabo
    c.save()
    c.translate(-160, -284)
    c.rotate(p['tail'] + 6 * math.sin(ph * 2 * math.pi + 2))
    _p(c, J('bur_tail'), shade(bc, 0.9), 0.2, sil, a)
    _p(c, J('bur_tuft'), BUR['mane'], 0.2, sil, a)
    c.restore()
    # pescoço + crina
    br = 1 + 0.012 * p['breath'] + 0.05 * p['chest']
    c.save()
    c.scale(1, br)
    _p(c, J('bur_neck'), bc, 0.35, sil, a)
    _p(c, J('bur_mane'), BUR['mane'], 0.2, sil, a)
    _p(c, J('bur_body'), bc, 0.5, sil, a, stitch=False)
    if sil is None:
        # remendo costurado na anca
        pr = J('bur_patch') if 'bur_patch' in GEOM else None
    _p(c, J('bur_blanket'), BUR['bl'], 0.35, sil, a, tex='fabric')
    if sil is None:
        plaid(c, J('bur_blanket'), BUR['bl'], BUR['bl2'], (30, 60, 84), 30, a)
        stitch_line(c, inset(J('bur_blanket'), 8), BUR['bl2'], a)
        # franja
        for fx in range(-110, 112, 9):
            ink(c, P([(fx, -247), (fx + 1, -233)], False), BUR['bl2'], a * 0.8, 2.5)
    c.restore()
    # cabeça
    c.save()
    c.translate(178, -432 * br)
    c.rotate(p['head'])
    droop = p['ears']
    wig = p['ear_wig']
    # orelha de trás
    c.save()
    c.translate(-2, -62)
    c.rotate(-24 - droop * 92 + wig * 0.7)
    _p(c, J('bur_ear'), shade(bc, 0.84), 0.3, sil, a)
    _p(c, J('bur_ear_in'), shade(BUR['ear_in'], 0.84), 0.0, sil, a, rim=False, shadow=False)
    c.restore()
    _p(c, J('bur_head'), bc, 0.4, sil, a)
    _p(c, J('bur_muzzle'), BUR['muzzle'], 0.25, sil, a)
    if sil is None:
        fill(c, oval(120, 4, 7, 5), (70, 52, 48), a)
        if p['blush']:
            fill(c, oval(40, 4, 16, 9), (220, 120, 110), a * 0.35, blur=3)
        # boca
        mo = p['mouth']
        m = p['m'] if mo == 'open' else 0
        if m > 0.08:
            mp = rot_about(oval(96, 36, 26 * (0.6 + 0.4 * m), 7 + 18 * m), 16, 96, 36)
            fill(c, mp, (70, 30, 34), a)
            c.save()
            c.clipPath(mp, skia.ClipOp.kIntersect, True)
            fill(c, oval(96, 36 + 12 * m, 18, 10), (210, 110, 110), a)
            fill(c, rr(76, 36 - 7 - 18 * m, 120, 36 - 2 - 16 * m, 3), WHITE, a * 0.9)
            c.restore()
        elif mo == 'sad':
            ink(c, smooth([(72, 34), (92, 26), (112, 32)], False), INK, a, 2.8)
        elif mo == 'neutral':
            ink(c, smooth([(72, 32), (92, 34), (112, 30)], False), INK, a, 2.8)
        else:
            ink(c, smooth([(70, 26), (92, 40), (116, 26)], False), INK, a, 2.8)
        # olho
        eye(c, 18, -30, 15, 18, p['eyes'], p['look'], pupil_r=8.5, lid_col=shade(bc, 0.85), a=a)
        bw = p['brow']
        ink(c, smooth([(2, -54 + bw * 4), (18, -60 - bw * 3), (34, -55 - bw * 7)], False), BUR['mane'], a, 5)
        _p(c, J('bur_tuftfore'), BUR['mane'], 0.15, None, a)
        for i in range(3):
            ink(c, smooth([(-6 + i * 10, -62), (0 + i * 10, -84), (8 + i * 10, -70)], False), (100, 84, 78), a * 0.8, 1.6)
    else:
        _p(c, J('bur_tuftfore'), BUR['mane'], 0.15, sil, a)
    # orelha da frente
    c.save()
    c.translate(18, -66)
    c.rotate(-4 - droop * 98 + wig)
    _p(c, J('bur_ear'), bc, 0.35, sil, a)
    _p(c, J('bur_ear_in'), BUR['ear_in'], 0.0, sil, a, rim=False, shadow=False)
    if sil is None:
        ink(c, smooth([(0, -20), (-2, -80), (0, -132)], False), shade(BUR['ear_in'], 0.8), a * 0.6, 1.6)
    c.restore()
    c.restore()
    # lenço
    _p(c, J('bur_scarf'), BUR['scarf'], 0.3, sil, a, tex='fabric', stitch=sil is None, stitch_col=(226, 170, 90))
    for dx, rotv in ((0, 6), (14, -10)):
        c.save()
        c.translate(150 + dx, -320)
        c.rotate(rotv + 4 * math.sin(ph * 2 * math.pi + dx))
        _p(c, J('bur_scarf_tail'), shade(BUR['scarf'], 0.9 if dx else 1.0), 0.2, sil, a, tex='fabric')
        c.restore()
    _p(c, circ(152, -322, 14), shade(BUR['scarf'], 1.1), 0.2, sil, a, tex='fabric')
    c.restore()


# =============================================================== CACHORRO
@geom('dog_body')
def _():
    return smooth([(-122, -118), (-60, -150), (40, -152), (112, -136), (132, -96), (104, -58), (0, -48), (-100, -54), (-134, -86)])


@geom('dog_leg')
def _():
    return tp([(0, 0), (0, 30), (2, 62)], 34, 26)


@geom('dog_paw')
def _():
    return oval(8, 66, 22, 12)


@geom('dog_tail')
def _():
    return tp([(0, 0), (-26, -26), (-34, -64)], 20, 7)


@geom('dog_skull')
def _():
    return oval(14, -30, 52, 48)


@geom('dog_muzzle')
def _():
    return oval(62, -4, 50, 35)


@geom('dog_ear')
def _():
    return smooth([(0, 0), (16, 22), (22, 80), (12, 136), (-14, 142), (-28, 84), (-18, 22)])


@geom('dog_scarf')
def _():
    return smooth([(70, -150), (118, -126), (126, -92), (84, -100), (64, -118)])


@geom('dog_tongue')
def _():
    return smooth([(54, 22), (72, 22), (74, 50), (64, 60), (54, 50)])


def cachorro(c, x, y, s=1.0, flip=False, pose=None, sil=None, a=255):
    """pose: walk, step, head, ears (0 caídas .. 1 voando para cima), eyes, look, brow (-1 triste..1 alegre),
    mouth ('closed','smile','open','tongue'), m, tail (abano 0..1), lie (0 em pé .. 1 deitado)"""
    p = dict(walk=0, step=0.0, head=0, ears=0, eyes=0.42, look=(0.3, 0.1), brow=-0.6, mouth='closed', m=0, tail=0,
             breath=0, lie=0, t=0.0, blush=1)
    p.update(pose or {})
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    bc = DOG['body']
    ph = p['step']
    amp = 22 if p['walk'] else 0
    lie = p['lie']
    bob = -abs(math.sin(ph * 2 * math.pi)) * 4 * (1 if p['walk'] else 0) + lie * 46
    for hx, off, k in ((-80, 0.5, 0.84), (88, 0.0, 0.84), (-92, 0.0, 1.0), (78, 0.5, 1.0)):
        c.save()
        c.translate(hx, -78 + bob)
        ang = amp * math.sin((ph + off) * 2 * math.pi) + lie * (70 if hx > 0 else -70)
        c.rotate(ang)
        c.scale(1, 1 - lie * 0.3)
        _p(c, J('dog_leg'), shade(bc, k), 0.2, sil, a)
        _p(c, J('dog_paw'), shade(bc, k * 0.96), 0.15, sil, a)
        c.restore()
    c.translate(0, bob)
    # rabo
    c.save()
    c.translate(-124, -110)
    c.rotate(-10 + p['tail'] * 28 * math.sin(p['t'] * 2 * math.pi * 3.2) - lie * 40)
    _p(c, J('dog_tail'), DOG['patch'], 0.2, sil, a)
    c.restore()
    br = 1 + 0.015 * p['breath']
    c.save()
    c.scale(1, br)
    _p(c, J('dog_body'), bc, 0.45, sil, a)
    if sil is None:
        body = J('dog_body')
        c.save()
        c.clipPath(body, skia.ClipOp.kIntersect, True)
        layer(c, jag(oval(-30, -146, 62, 34)), DOG['patch'], 0.05, a=a, shadow=False)
        layer(c, jag(oval(-104, -92, 30, 34)), DOG['patch'], 0.05, a=a, shadow=False)
        stitch_line(c, inset(jag(oval(-30, -146, 62, 34)), 6), shade(DOG['patch'], 1.4), a)
        c.restore()
    c.restore()
    _p(c, J('dog_scarf'), DOG['scarf'], 0.25, sil, a, tex='fabric', stitch=sil is None, stitch_col=(226, 200, 140))
    # cabeça
    c.save()
    c.translate(108, -140 * br)
    c.rotate(p['head'])
    ears = p['ears']
    # orelha de trás
    c.save()
    c.translate(-4, -58)
    c.rotate(14 + ears * 150 + 6 * math.sin(p['t'] * 5))
    _p(c, J('dog_ear'), shade(DOG['ear'], 0.82), 0.3, sil, a, tex='fabric')
    c.restore()
    _p(c, J('dog_skull'), bc, 0.4, sil, a)
    if sil is None:
        c.save()
        c.clipPath(J('dog_skull'), skia.ClipOp.kIntersect, True)
        layer(c, jag(oval(4, -66, 48, 26)), DOG['patch'], 0.05, a=a, shadow=False)
        c.restore()
    _p(c, J('dog_muzzle'), bc, 0.3, sil, a)
    if sil is None:
        mo = p['mouth']
        m = p['m'] if mo == 'open' else 0
        if m > 0.08 or mo == 'tongue':
            mm = max(m, 0.45)
            mp = oval(66, 22, 26, 6 + 16 * mm)
            fill(c, mp, (80, 34, 38), a)
            if mo == 'tongue':
                layer(c, J('dog_tongue'), (220, 110, 120), 0.15, a=a)
        elif mo == 'smile':
            ink(c, smooth([(40, 18), (64, 30), (90, 18)], False), INK, a, 2.8)
        else:
            ink(c, smooth([(44, 22), (64, 26), (86, 22)], False), INK, a, 2.8)
        ink(c, P([(64, 4), (64, 22)], False), INK, a * 0.7, 2.2)
        layer(c, jag(oval(102, -16, 19, 14)), DOG['nose'], 0.2, a=a)
        fill(c, oval(98, -21, 6, 3), (150, 140, 140), a * 0.7)
        if p['blush']:
            fill(c, oval(44, -6, 15, 8), (220, 120, 110), a * 0.3, blur=3)
        eye(c, 32, -36, 13, 15, p['eyes'], p['look'], pupil_r=8, lid_col=shade(bc, 0.86), a=a)
        ink(c, smooth([(22, -18), (34, -14), (46, -18)], False), shade(bc, 0.7), a * 0.8, 1.8)  # olheira
        bw = p['brow']
        ink(c, smooth([(18, -58 - bw * 2), (32, -62 + bw * 6 - 2), (46, -60 + bw * 2)], False), DOG['patch'], a, 5)
        for i in range(5):
            fill(c, circ(70 + i * 7 % 18, -10 + (i * 5) % 12, 1.6), shade(bc, 0.6), a)
    # orelha da frente
    c.save()
    c.translate(-10, -52)
    c.rotate(6 + ears * 160 + 5 * math.sin(p['t'] * 5 + 1))
    _p(c, J('dog_ear'), DOG['ear'], 0.35, sil, a, tex='fabric', stitch=sil is None, stitch_col=(214, 150, 96))
    c.restore()
    c.restore()
    c.restore()


# =============================================================== GATO (sentado, de frente / 3/4)
@geom('cat_body')
def _():
    return smooth([(-56, -20), (-72, -82), (-56, -142), (0, -162), (52, -142), (68, -82), (56, -20), (0, -8)])


@geom('cat_tail')
def _():
    return tp([(0, 0), (-46, 2), (-74, -24), (-80, -62), (-64, -88)], 24, 11)


@geom('cat_cape')
def _():
    return smooth([(-58, -150), (0, -160), (58, -150), (80, -62), (40, -74), (0, -62), (-44, -74), (-82, -62)])


@geom('cat_head')
def _():
    return union(oval(0, -26, 64, 52), P([(-62, -14), (-78, 4), (-50, 6)]), P([(62, -14), (78, 4), (50, 6)]))


@geom('cat_earL')
def _():
    return smooth([(-56, -52), (-46, -108), (-12, -74)], True, 0.08)


@geom('cat_earR')
def _():
    return smooth([(56, -52), (46, -108), (12, -74)], True, 0.08)


def gato(c, x, y, s=1.0, flip=False, pose=None, sil=None, a=255):
    """pose: head (graus), tilt, eyes (pálpebra), eyeL/eyeR (sobrescreve), look, brow ('smug','sus','plot','alarm','happy'),
    mouth ('smug','open','neutral','w'), m, tail, ears (0 normal .. 1 abaixadas), chin (erguer), paw (0..1 pata na boca/queixo),
    lick (0..1)"""
    p = dict(head=0, eyes=0.45, eyeL=None, eyeR=None, look=(0.2, 0), brow='smug', mouth='smug', m=0, tail=0, ears=0, chin=0,
             paw=0, breath=0, t=0.0, lick=0)
    p.update(pose or {})
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    bc = CAT['body']
    # rabo
    c.save()
    c.translate(-46, -14)
    c.rotate(p['tail'] + 4 * math.sin(p['t'] * 1.7))
    _p(c, J('cat_tail'), bc, 0.25, sil, a)
    if sil is None:
        for i, (tx, ty) in enumerate([(-34, -2), (-62, -14), (-76, -46)]):
            ink(c, smooth([(tx - 6, ty - 9), (tx, ty), (tx - 4, ty + 9)], False), shade(bc, 0.7), a * 0.8, 3)
    c.restore()
    br = 1 + 0.012 * p['breath']
    c.save()
    c.scale(1, br)
    _p(c, J('cat_body'), bc, 0.45, sil, a)
    if sil is None:
        layer(c, jag(oval(10, -74, 32, 50)), CAT['chest'], 0.1, a=a)
        for i in range(4):
            ink(c, smooth([(-2 + i * 7, -56 + i * 8), (6 + i * 7, -50 + i * 8)], False), shade(CAT['chest'], 0.85), a * 0.6, 1.6)
    # patas
    _p(c, jag(oval(-16, -6, 19, 11)), CAT['chest'], 0.15, sil, a)
    c.save()
    pw = p['paw']
    lk = p['lick']
    c.translate(28, -10)
    c.rotate(-pw * 120 - lk * 100)
    c.translate(0, -pw * 6)
    _p(c, jag(tp([(0, 0), (0, -30 * max(pw, lk)), (0, -36 * max(pw, lk) - 2)], 22, 20)), bc, 0.15, sil, a) if max(pw, lk) > 0.05 else None
    _p(c, jag(oval(0, -38 * max(pw, lk), 19, 11)), CAT['chest'], 0.15, sil, a)
    c.restore()
    # capa
    _p(c, J('cat_cape'), CAT['cape'], 0.35, sil, a, tex='fabric', stitch=sil is None, stitch_col=CAT['gold'])
    if sil is None:
        for i in range(5):
            fx = -40 + i * 20
            ink(c, smooth([(fx, -120), (fx + 4, -96), (fx - 2, -80)], False), shade(CAT['cape'], 1.5), a * 0.5, 1.6)
    _p(c, circ(0, -152, 10), CAT['gold'], 0.2, sil, a)
    c.restore()
    # cabeça
    c.save()
    c.translate(0, -170 * br)
    c.rotate(p['head'])
    c.translate(0, -p['chin'] * 6)
    eL, eR = p['ears'], p['ears']
    for nm, sx in (('cat_earL', -1), ('cat_earR', 1)):
        c.save()
        c.rotate(sx * p['ears'] * 38, sx * 34, -62)
        _p(c, J(nm), bc, 0.3, sil, a)
        if sil is None:
            inn = xf(J(nm), skia.Matrix.Scale(0.62, 0.62))
            inn = xf(inn, skia.Matrix.Translate(sx * 12, -24))
            layer(c, inn, CAT['ear_in'], 0.0, a=a, shadow=False, rim=False)
        c.restore()
    _p(c, J('cat_head'), bc, 0.4, sil, a)
    if sil is None:
        fill(c, oval(0, -4, 40, 22), shade(CAT['chest'], 0.98), a * 0.95)
        # listras na testa
        for dx in (-12, 0, 12):
            ink(c, smooth([(dx, -76), (dx * 1.1, -62)], False), shade(bc, 0.7), a * 0.8, 3)
        bw = p['brow']
        lidL = p['eyeL'] if p['eyeL'] is not None else p['eyes']
        lidR = p['eyeR'] if p['eyeR'] is not None else p['eyes']
        if bw == 'sus':
            lidL, lidR = 0.62, 0.2
        if bw == 'alarm':
            lidL = lidR = 0.0
        for ex, ld in ((-24, lidL), (24, lidR)):
            eye(c, ex, -30, 15, 12, ld, p['look'], pupil_r=7, lid_col=bc, a=a, slit=True, iris=CAT['eye'])
        # sobrancelhas
        bro = {'smug': (4, -4), 'sus': (8, -14), 'plot': (-6, -6), 'alarm': (-10, -10), 'happy': (-4, -4)}[bw]
        ink(c, smooth([(-38, -50 + bro[0] * 0.3), (-24, -54), (-10, -50 - bro[0] * 0.4)], False), shade(bc, 0.55), a, 3.5)
        ink(c, smooth([(10, -50 - bro[1] * 0.1), (24, -54 + bro[1] * 0.6), (38, -50 + bro[1] * 0.2)], False), shade(bc, 0.55), a, 3.5)
        # nariz e boca
        fill(c, P([(-7, -12), (7, -12), (0, -4)]), (200, 120, 130), a)
        mo = p['mouth']
        m = p['m'] if mo == 'open' else 0
        if m > 0.08:
            fill(c, oval(0, 8, 10 + 6 * m, 4 + 12 * m), (90, 36, 44), a)
            fill(c, oval(0, 12 + 8 * m, 7, 4), (210, 120, 130), a * 0.9)
        elif mo == 'smug':
            ink(c, smooth([(-16, 2), (-7, 8), (0, 2), (9, 6), (18, -2)], False), INK, a, 2.4)
        else:
            ink(c, smooth([(-12, 4), (-5, 9), (0, 4), (5, 9), (12, 4)], False), INK, a, 2.4)
        # bigodes assimétricos
        for i, (yy, l) in enumerate(((-6, 62), (0, 70), (6, 54))):
            ink(c, smooth([(-34, yy), (-34 - l * 0.5, yy - 4 + i * 2), (-34 - l, yy + 2 + i * 4)], False), (236, 232, 222), a * 0.85, 1.4)
            ink(c, smooth([(34, yy), (34 + l * 0.45, yy - 6 + i), (34 + l * 0.9, yy - 10 + i * 6)], False), (236, 232, 222), a * 0.85, 1.4)
        fill(c, oval(-40, 0, 12, 7), (220, 120, 120), a * 0.25, blur=3)
        fill(c, oval(40, 0, 12, 7), (220, 120, 120), a * 0.25, blur=3)
    c.restore()
    c.restore()


def gato_walk(c, x, y, s=1.0, flip=False, step=0.0, walk=1, sil=None, a=255, t=0.0):
    """gato de perfil, andando com elegância (cauda em pé)"""
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    bc = CAT['body']
    amp = 16 * walk
    for hx, off, k in ((-44, 0.5, 0.84), (40, 0.0, 0.84), (-52, 0.0, 1.0), (34, 0.5, 1.0)):
        c.save()
        c.translate(hx, -62)
        c.rotate(amp * math.sin((step + off) * 2 * math.pi))
        _p(c, jag(tp([(0, 0), (0, 32), (2, 60)], 18, 14)), shade(bc, k), 0.2, sil, a)
        c.restore()
    c.save()
    c.translate(-62, -84)
    c.rotate(8 * math.sin(t * 2.2))
    _p(c, jag(tp([(0, 0), (-24, -30), (-18, -78), (4, -100)], 18, 10)), bc, 0.25, sil, a)
    c.restore()
    bob = -abs(math.sin(step * 2 * math.pi)) * 3 * walk
    c.translate(0, bob)
    _p(c, jag(smooth([(-72, -96), (-20, -116), (40, -112), (74, -90), (66, -62), (0, -54), (-66, -60)])), bc, 0.4, sil, a)
    _p(c, jag(smooth([(-30, -112), (40, -112), (66, -74), (20, -70), (-34, -84)])), CAT['cape'], 0.3, sil, a, tex='fabric',
       stitch=sil is None, stitch_col=CAT['gold'])
    c.save()
    c.translate(70, -112)
    _p(c, jag(smooth([(-14, -44), (-4, -78), (12, -50)], True, 0.1)), bc, 0.3, sil, a)
    _p(c, jag(smooth([(6, -46), (22, -78), (30, -44)], True, 0.1)), bc, 0.3, sil, a)
    _p(c, jag(oval(10, -24, 36, 30)), bc, 0.4, sil, a)
    if sil is None:
        fill(c, oval(26, -14, 18, 12), CAT['chest'], a)
        eye(c, 22, -30, 9, 6, 0.45, (0.6, 0), pupil_r=4, lid_col=bc, a=a, slit=True, iris=CAT['eye'])
        fill(c, P([(40, -20), (46, -18), (40, -14)]), (200, 120, 130), a)
        for i in range(2):
            ink(c, P([(36, -12 + i * 5), (70, -16 + i * 9)], False), (236, 232, 222), a * 0.8, 1.3)
    c.restore()
    _p(c, circ(64, -100, 7), CAT['gold'], 0.2, sil, a)
    c.restore()


# =============================================================== GALO
def _feather_rows(c, clip, cols, a):
    c.save()
    c.clipPath(clip, skia.ClipOp.kIntersect, True)
    b = clip.computeTightBounds()
    row = 0
    y = b.top() + 6
    while y < b.bottom() + 14:
        x = b.left() - 10 + (row % 2) * 9
        while x < b.right() + 10:
            f = smooth([(x - 10, y - 4), (x + 10, y - 4), (x + 8, y + 10), (x, y + 18), (x - 8, y + 10)])
            col = cols[(row + int(x / 18)) % len(cols)]
            fill(c, f, shade(col, 0.82), a, blur=1.5)
            fill(c, xf(f, skia.Matrix.Translate(-1, -2)), col, a)
            ink(c, smooth([(x, y + 1), (x, y + 14)], False), shade(col, 0.7), a * 0.6, 1.2)
            x += 18
        y += 12
        row += 1
    c.restore()


@geom('roo_body')
def _():
    return smooth([(-62, -112), (-22, -142), (40, -146), (76, -116), (72, -72), (34, -54), (-30, -56), (-64, -80)])


@geom('roo_vest')
def _():
    return smooth([(-30, -134), (22, -138), (44, -86), (8, -64), (-36, -76)])


@geom('roo_wing')
def _():
    return smooth([(-46, -110), (8, -112), (22, -92), (-6, -78), (-50, -86)])


@geom('roo_head')
def _():
    return union(circ(10, -30, 25), oval(0, -6, 26, 22))


@geom('roo_comb')
def _():
    return union(circ(-12, -54, 15), circ(4, -64, 18), circ(22, -60, 16), circ(34, -50, 12), oval(10, -48, 30, 12))


@geom('roo_wattle')
def _():
    return smooth([(26, -18), (38, -16), (40, 4), (30, 12), (24, 0)])


def galo(c, x, y, s=1.0, flip=False, pose=None, sil=None, a=255):
    """pose: walk, step, head (graus), beak (abertura 0..1), eye (0 normal .. 1 arregalado), puff (peito 0..1),
    flap (0..1), tail, march (0..1 marcha exagerada)"""
    p = dict(walk=0, step=0.0, head=0, beak=0, eye=0, puff=0, flap=0, tail=0, t=0.0, march=0)
    p.update(pose or {})
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    ph = p['step']
    lift = (14 + 18 * p['march']) if p['walk'] else 0
    for off, k in ((0.5, 0.85), (0.0, 1.0)):
        c.save()
        c.translate(2 + (off - 0.25) * 14, -62)
        sw = (22 + 10 * p['march']) * math.sin((ph + off) * 2 * math.pi) if p['walk'] else 0
        c.rotate(sw)
        up = max(0, math.sin((ph + off) * 2 * math.pi)) * lift
        legp = jag(tp([(0, 0), (2, 30 - up * 0.4), (0, 62 - up)], 7, 5))
        _p(c, legp, shade(ROO['leg'], k), 0.15, sil, a)
        for dx in (-12, 2, 16):
            ink(c, P([(0, 62 - up), (dx, 66 - up)], False), shade(ROO['leg'], k * 0.8), a, 4) if sil is None else \
                ink(c, P([(0, 62 - up), (dx, 66 - up)], False), sil, a, 4)
        c.restore()
    bob = -abs(math.sin(ph * 2 * math.pi)) * 5 * (1 if p['walk'] else 0)
    c.translate(0, bob)
    # cauda
    c.save()
    c.translate(-56, -108)
    c.rotate(p['tail'] + 3 * math.sin(p['t'] * 2.3))
    for i in range(5):
        ang = -60 + i * 22
        rad = math.radians(ang - 90)
        L = 120 - abs(i - 2) * 12
        tip = (math.cos(rad) * L * 0.9 - 30, math.sin(rad) * L)
        mid = (tip[0] * 0.4 - 30, tip[1] * 0.6 - 20)
        f = jag(tp(bez((0, 0), mid, tip, 10), 22, 4))
        _p(c, f, ROO['tail'] if i % 2 == 0 else ROO['tail2'], 0.25, sil, a, tex='fabric')
    c.restore()
    puff = 1 + 0.12 * p['puff']
    c.save()
    c.translate(20, -100)
    c.scale(puff, puff)
    c.translate(-20, 100)
    _p(c, J('roo_body'), ROO['o1'], 0.45, sil, a)
    if sil is None:
        _feather_rows(c, J('roo_body'), [ROO['o1'], ROO['o2'], shade(ROO['o1'], 1.08)], a)
    _p(c, J('roo_vest'), ROO['vest'], 0.3, sil, a, tex='fabric', stitch=sil is None, stitch_col=(220, 200, 150))
    if sil is None:
        fill(c, circ(30, -110, 4), ROO['beak'], a)
        fill(c, circ(34, -90, 4), ROO['beak'], a)
    c.save()
    c.translate(-46, -100)
    c.rotate(-p['flap'] * 50 * (0.5 + 0.5 * math.sin(p['t'] * 30)))
    c.translate(46, 100)
    _p(c, J('roo_wing'), ROO['o2'], 0.3, sil, a)
    if sil is None:
        for i in range(4):
            ink(c, smooth([(-40 + i * 12, -104), (-34 + i * 12, -86)], False), shade(ROO['o2'], 0.7), a * 0.7, 1.6)
    c.restore()
    c.restore()
    # cabeça
    c.save()
    c.translate(44, -136)
    c.rotate(p['head'])
    _p(c, jag(tp([(-14, 22), (-4, 6), (6, -14)], 46, 30)), ROO['o2'], 0.3, sil, a)  # pescoço / colar
    _p(c, J('roo_comb'), ROO['comb'], 0.3, sil, a, tex='fabric')
    _p(c, J('roo_head'), ROO['o1'], 0.35, sil, a)
    bk = p['beak']
    c.save()
    c.translate(30, -24)
    c.rotate(bk * 30)
    _p(c, jag(P([(0, 0), (22, 2), (0, 8)])), shade(ROO['beak'], 0.9), 0.15, sil, a)
    c.restore()
    c.save()
    c.translate(30, -24)
    c.rotate(-bk * 14)
    _p(c, jag(P([(-2, -10), (30, -2), (0, 2)])), ROO['beak'], 0.2, sil, a)
    c.restore()
    _p(c, J('roo_wattle'), ROO['comb'], 0.2, sil, a, tex='fabric')
    if sil is None:
        er = 7 + 4 * p['eye']
        eye(c, 14, -34, er, er, 0.0 if p['eye'] > 0.3 else 0.1, (0.4, -0.1), pupil_r=er * 0.5, a=a)
        if p['eye'] > 0.3:
            ink(c, smooth([(2, -50), (14, -54), (26, -50)], False), INK, a, 2.5)
    c.restore()
    c.restore()


# =============================================================== LADRÕES (de frente)
TH = {
    'largo': dict(w=1.25, h=1.0, coat=(150, 112, 70), vest=(196, 150, 70), skin=(222, 178, 146), hair=(52, 40, 34), pants=(70, 62, 70)),
    'alto': dict(w=0.86, h=1.22, coat=(124, 40, 46), vest=(110, 82, 60), skin=(226, 190, 160), hair=(80, 60, 44), pants=(56, 52, 62)),
    'baixo': dict(w=1.08, h=0.84, coat=(94, 106, 66), vest=(84, 98, 58), skin=(230, 186, 156), hair=(96, 70, 50), pants=(66, 58, 50)),
}


def ladrao(c, x, y, s, kind, pose=None, sil=None, a=255):
    """pose: expr ('laugh','scared','neutral','pant'), arms ('table','up','point','eat','run'), run (fase), lean, look"""
    p = dict(expr='neutral', arms='table', run=None, lean=0, t=0.0, look=(0, 0), m=0, drop=0)
    p.update(pose or {})
    k = TH[kind]
    w, h = k['w'], k['h']
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    c.rotate(p['lean'])
    # pernas
    if p['run'] is not None:
        ph = p['run']
        for side, off in ((-1, 0), (1, 0.5)):
            c.save()
            c.translate(side * 26 * w, -170 * h)
            c.rotate(35 * math.sin((ph + off) * 2 * math.pi))
            _p(c, jag(tp([(0, 0), (0, 90 * h), (0, 170 * h)], 46 * w, 36 * w)), k['pants'], 0.3, sil, a, tex='fabric')
            _p(c, jag(oval(10, 172 * h, 30, 14)), (54, 40, 34), 0.2, sil, a)
            c.restore()
    else:
        for side in (-1, 1):
            _p(c, jag(tp([(side * 26 * w, -170 * h), (side * 28 * w, -80 * h), (side * 28 * w, 0)], 46 * w, 38 * w)), k['pants'], 0.3, sil, a,
               tex='fabric')
            _p(c, jag(oval(side * 30 * w + 8 * side, 2, 32, 14)), (54, 40, 34), 0.2, sil, a)
    # tronco
    torso = jag(smooth([(-70 * w, -330 * h), (70 * w, -330 * h), (92 * w, -150 * h), (60 * w, -150 * h), (-60 * w, -150 * h), (-92 * w, -150 * h)]))
    _p(c, torso, k['coat'], 0.45, sil, a, tex='fabric', stitch=sil is None, stitch_col=shade(k['coat'], 1.6))
    if sil is None:
        vest = jag(smooth([(-34 * w, -326 * h), (34 * w, -326 * h), (46 * w, -160 * h), (0, -150 * h), (-46 * w, -160 * h)]))
        layer(c, vest, k['vest'], 0.2, a=a, tex='fabric')
        plaid(c, vest, k['vest'], shade(k['vest'], 0.7), shade(k['vest'], 1.25), 18, a) if kind == 'largo' else None
        for i in range(3):
            fill(c, circ(0, (-300 + i * 50) * h, 5), (220, 190, 120), a)
        ink(c, smooth([(-20 * w, -250 * h), (-30 * w, -200 * h)], False), shade(k['coat'], 0.6), a * 0.6, 2)
    # braços
    arms = p['arms']
    t = p['t']
    for side in (-1, 1):
        c.save()
        c.translate(side * 74 * w, -310 * h)
        if arms == 'up':
            a1, a2 = side * (150 + 10 * math.sin(t * 20 + side)), side * 20
        elif arms == 'point':
            a1, a2 = (side * 20, side * 10) if side < 0 else (-100, -10)
        elif arms == 'eat':
            a1, a2 = (side * 20, side * 140 + 10 * math.sin(t * 6)) if side > 0 else (side * 30, side * 60)
        elif arms == 'run':
            a1, a2 = side * 30 + 40 * math.sin((p['run'] or 0) * 2 * math.pi + (0 if side < 0 else math.pi)), side * 60
        else:  # mesa
            a1, a2 = -side * 8, -side * 50
        c.rotate(-a1 if side > 0 else -a1)
        _p(c, jag(tp([(0, 0), (0, 60), (0, 110)], 38, 32)), shade(k['coat'], 0.92), 0.3, sil, a, tex='fabric')
        c.translate(0, 110)
        c.rotate(-a2 * 0.5)
        _p(c, jag(tp([(0, 0), (0, 50), (0, 96)], 32, 26)), shade(k['coat'], 0.92), 0.3, sil, a, tex='fabric')
        _p(c, jag(oval(0, 106, 20, 18)), k['skin'], 0.25, sil, a)
        c.restore()
    # cabeça
    c.save()
    c.translate(0, -360 * h)
    head = jag(oval(0, -50, 62 * (1.12 if kind == 'largo' else 0.92 if kind == 'alto' else 1.06), 66 * (1.1 if kind == 'alto' else 1.0)))
    _p(c, jag(rr(-24, -10, 24, 20, 8)), shade(k['skin'], 0.9), 0.2, sil, a)
    _p(c, head, k['skin'], 0.4, sil, a)
    ex = p['expr']
    if sil is None:
        # olhos
        lk = p['look']
        if ex == 'laugh':
            for sx in (-1, 1):
                ink(c, smooth([(sx * 30 - 12, -62), (sx * 30, -72), (sx * 30 + 12, -62)], False), INK, a, 3.5)
        else:
            r = 14 if ex == 'scared' else 9
            for sx in (-1, 1):
                eye(c, sx * 26, -64, r, r + 1, 0.0 if ex == 'scared' else 0.25, lk, pupil_r=r * (0.38 if ex == 'scared' else 0.6), a=a,
                    lid_col=k['skin'])
            if ex == 'scared':
                for sx in (-1, 1):
                    ink(c, smooth([(sx * 14, -86), (sx * 28, -92), (sx * 42, -84)], False), k['hair'], a, 4)
        # nariz
        if kind == 'largo':
            layer(c, jag(circ(0, -40, 18)), shade(k['skin'], 0.92), 0.25, a=a)
            fill(c, circ(-6, -46, 5), (240, 160, 150), a * 0.6)
        elif kind == 'alto':
            layer(c, jag(smooth([(-6, -70), (8, -70), (30, -26), (-4, -30)])), shade(k['skin'], 0.95), 0.25, a=a)
        else:
            layer(c, jag(circ(0, -42, 12)), (226, 150, 140), 0.2, a=a)
        # boca / barba / bigode
        if kind == 'largo':
            layer(c, jag(smooth([(-64, -46), (64, -46), (52, 6), (0, 26), (-52, 6)])), k['hair'], 0.25, a=a, tex='fabric')
            for i in range(7):
                ink(c, smooth([(-40 + i * 13, -30), (-42 + i * 13, 0)], False), shade(k['hair'], 1.6), a * 0.5, 1.5)
        if kind == 'baixo':
            layer(c, jag(smooth([(-40, -30), (-10, -34), (0, -28), (10, -34), (42, -28), (20, -18), (0, -22), (-22, -18)])), k['hair'], 0.2,
                  a=a)
        mo = (0.9 if ex == 'laugh' else 0.8 if ex == 'scared' else 0.5 if ex == 'pant' else 0.0) + p['m']
        my = -14 if kind != 'largo' else -10
        if mo > 0.1:
            fill(c, oval(0, my, 14 + 6 * (ex == 'laugh'), 4 + 12 * mo), (90, 30, 34), a)
        else:
            ink(c, smooth([(-14, my), (0, my + 3), (14, my)], False), INK, a, 2.6)
        # cabelo / chapéu
        if kind == 'alto':
            layer(c, jag(smooth([(-74, -96), (74, -96), (66, -108), (40, -112), (34, -170), (-34, -170), (-40, -112), (-66, -108)])),
                  (110, 74, 46), 0.35, a=a, tex='fabric', stitch=True, stitch_col=(190, 150, 100))
        else:
            layer(c, jag(smooth([(-58, -78), (-40, -112), (0, -122), (40, -112), (60, -78), (40, -96), (0, -102), (-40, -96)])),
                  k['hair'], 0.25, a=a)
        fill(c, oval(-34, -40, 12, 7), (230, 130, 120), a * 0.35, blur=3)
        fill(c, oval(34, -40, 12, 7), (230, 130, 120), a * 0.35, blur=3)
    elif kind == 'alto':
        fill(c, smooth([(-74, -96), (74, -96), (66, -108), (40, -112), (34, -170), (-34, -170), (-40, -112), (-66, -108)]), sil, a)
    c.restore()
    c.restore()


def rato(c, x, y, s=1.0, flip=False, step=0.0, sil=None, a=255, t=0.0, sleep=False):
    c.save()
    c.translate(x, y)
    c.scale(-s if flip else s, s)
    col = (150, 142, 140)
    ink(c, smooth([(-30, -10), (-60, -14 + 6 * math.sin(t * 9)), (-80, -4)], False), (200, 150, 150) if sil is None else sil, a, 3)
    _p(c, jag(smooth([(-34, -6), (-22, -30), (8, -34), (34, -16), (30, -4), (-30, -2)])), col, 0.3, sil, a)
    _p(c, jag(circ(8, -36, 12)), col, 0.25, sil, a)
    if sil is None:
        fill(c, circ(8, -36, 7), (220, 170, 170), a)
        if sleep:
            ink(c, smooth([(18, -24), (22, -22), (26, -24)], False), INK, a, 2)
        else:
            fill(c, circ(22, -22, 3), PUPIL, a)
        fill(c, circ(36, -14, 3.5), (200, 120, 130), a)
    for off in (0, 0.5):
        lx = -14 + off * 28 + 6 * math.sin((step + off) * 2 * math.pi)
        ink(c, P([(lx, -4), (lx + 3, 2)], False), shade(col, 0.7) if sil is None else sil, a, 4)
    c.restore()


def coruja(c, x, y, s=1.0, sil=None, a=255, t=0.0):
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    col = (120, 98, 80)
    _p(c, jag(smooth([(-34, -10), (-40, -60), (-24, -98), (0, -104), (24, -98), (40, -60), (34, -10), (0, 0)])), col, 0.3, sil, a)
    _p(c, jag(P([(-30, -92), (-36, -118), (-14, -100)])), col, 0.2, sil, a)
    _p(c, jag(P([(30, -92), (36, -118), (14, -100)])), col, 0.2, sil, a)
    if sil is None:
        layer(c, jag(oval(0, -42, 22, 30)), (200, 176, 140), 0.1, a=a)
        bl = 0.92 if (t % 3.1) < 0.15 else 0.55
        for sx in (-1, 1):
            fill(c, circ(sx * 15, -76, 14), (232, 200, 120), a)
            eye(c, sx * 15, -76, 11, 11, bl, (0, 0), pupil_r=6, lid_col=col, a=a)
        fill(c, P([(-5, -66), (5, -66), (0, -54)]), (220, 170, 70), a)
    c.restore()
