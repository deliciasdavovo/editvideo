"""Personagens de O Pote Vazio (originais, paper style 2.0).
Coordenadas locais: origem nos pés, cabeça = ~100 unidades. Expressões por nome."""
import math
import skia
from paperlib import (layer, flat, ink, smooth, poly, ell, circ, rr, union, inter, diff, xform, tp,
                      ik, limb, contact_shadow, C, mix, mul, SCALE, STYLE)

# ============================================================ paletas
PING = dict(skin=(238, 198, 162), blush=(232, 120, 110), hair=(34, 30, 38), hair_hi=(74, 70, 88),
            tunic=(46, 122, 120), tunic_patch=(78, 146, 128), collar=(240, 228, 204),
            sash=(204, 84, 52), pants=(228, 214, 186), shoes=(52, 46, 56), eye=(38, 28, 30))
IMP = dict(skin=(230, 196, 168), robe=(44, 52, 92), robe_dk=(30, 34, 62), panel=(198, 160, 86),
           panel_dk=(150, 112, 52), collar=(238, 228, 206), sash=(170, 46, 44), beard=(238, 234, 224),
           hat=(32, 34, 52), jade=(92, 164, 122), eye=(36, 28, 30))
PAI = dict(skin=(206, 150, 108), hair=(36, 32, 34), gray=(150, 146, 148), tunic=(160, 112, 64),
           tunic_dk=(128, 86, 48), pants=(62, 72, 92), rope=(214, 186, 128), straw=(214, 178, 116),
           eye=(36, 26, 24), sandal=(120, 84, 54))
BIRD = dict(back=(146, 98, 60), belly=(236, 222, 196), cap=(98, 66, 48), cheek=(244, 236, 220),
            beak=(232, 176, 70), eye=(24, 20, 22), wing=(120, 80, 50))
POT = dict(clay=(184, 112, 70), band=(240, 226, 196), earth=(92, 66, 48), rim=(200, 128, 84))


# ============================================================ partes comuns
def eye(c, x, y, kind, col, rx=7.0, ry=9.5, look=(0, 0), wet=False, side=1):
    """kind: open | wide | half | down | happy | closed | narrow"""
    if kind in ('happy', 'closed'):
        if kind == 'happy':
            pts = [(x - rx * 1.2, y + 2), (x, y - ry * 0.8), (x + rx * 1.2, y + 2)]
        else:
            pts = [(x - rx * 1.2, y - 1), (x, y + ry * 0.55), (x + rx * 1.2, y - 1)]
        c.drawPath(tp(pts, 3.2 * rx / 7, 3.2 * rx / 7), skia.Paint(AntiAlias=True, Color=C(col)))
        return
    sy = {'open': 1, 'wide': 1.18, 'half': 0.62, 'down': 0.5, 'narrow': 0.42}[kind]
    ex, ey = x + look[0], y + look[1] + (ry * (1 - sy) * 0.6 if kind in ('half', 'down', 'narrow') else 0)
    e = ell(ex, ey, rx * (1.08 if kind == 'wide' else 1), ry * sy)
    if kind in ('half', 'down', 'narrow'):
        # pálpebra corta em cima
        lid_y = ey - ry * sy * (0.35 if kind == 'half' else 0.1)
        e = inter(e, rr(ex - 20, lid_y, ex + 20, ey + 30, 1))
    flat(c, e, col)
    k = rx / 7.0
    hl = (2.6 if not wet else 3.6) * k
    flat(c, circ(ex - rx * 0.3, ey - ry * sy * 0.35, hl), (255, 252, 244), 0.95)
    flat(c, circ(ex + rx * 0.35, ey + ry * sy * 0.3, hl * 0.45), (255, 252, 244), 0.8)
    if wet:
        flat(c, ell(ex, ey + ry * sy * 0.75, rx * 0.9, 2.2), (200, 230, 240), 0.7)
    # linha da pálpebra
    top = ey - ry * sy - 1.5
    if kind in ('half', 'down', 'narrow'):
        top = lid_y
    ink(c, [(ex - rx * 1.25, top + 2.5 * k), (ex, top - 0.8 * k), (ex + rx * 1.25, top + 2.5 * k)], 2.4 * k, col, 0.9, 1.4 * k)


def almond_eye(c, x, y, kind, col, side=1, look=(0, 0), wet=False, rx=6.4, ry=4.6):
    """Olho amendoado pequeno e delicado (traço de livro ilustrado): ponto escuro,
    pálpebra superior em nanquim, brilho mínimo."""
    if kind in ('happy', 'closed'):
        if kind == 'happy':
            pts = [(x - rx * 1.15, y + 1.5), (x, y - ry * 0.9), (x + rx * 1.15, y + 1.5)]
        else:
            pts = [(x - rx * 1.15, y - 0.5), (x, y + ry * 0.5), (x + rx * 1.15, y - 0.5)]
        c.drawPath(tp(pts, 2.6, 2.0), skia.Paint(AntiAlias=True, Color=C(col)))
        return
    sy = {'open': 1.0, 'wide': 1.3, 'half': 0.7, 'down': 0.55, 'narrow': 0.5}[kind]
    ex, ey = x + look[0] * 0.6, y + look[1] * 0.5
    ic = (ex - side * rx, ey + 0.6)              # canto interno
    oc = (ex + side * rx * 1.08, ey - 1.0)        # canto externo levemente acima
    top = [(ic[0], ic[1]), (ex - side * rx * 0.3, ey - ry * sy), (ex + side * rx * 0.45, ey - ry * sy * 0.9), oc]
    bot = [(ex + side * rx * 0.3, ey + ry * sy * 0.62), (ex - side * rx * 0.4, ey + ry * sy * 0.55)]
    shape = smooth(top + bot, tension=0.5)
    if kind in ('half', 'down', 'narrow'):
        lid_y = ey - ry * sy * (0.1 if kind == 'half' else -0.15)
        shape = inter(shape, rr(ex - 20, lid_y, ex + 20, ey + 20, 1))
    else:
        lid_y = None
    flat(c, shape, col)
    hl = 1.5 if not wet else 2.1
    flat(c, circ(ex - side * rx * 0.15, ey - ry * sy * 0.3, hl), (255, 252, 244), 0.9)
    if wet:
        flat(c, ell(ex, ey + ry * sy * 0.55, rx * 0.8, 1.4), (200, 230, 240), 0.8)
    # pálpebra superior (traço único, afina no canto externo)
    if lid_y is None:
        lid = [(ic[0] - side * 0.5, ic[1] - 0.4), (ex - side * rx * 0.3, ey - ry * sy - 0.8),
               (ex + side * rx * 0.5, ey - ry * sy * 0.95 - 0.6), (oc[0] + side * 1.8, oc[1] - 1.2)]
    else:
        lid = [(ic[0] - side * 0.5, lid_y + 0.8), (ex, lid_y - 0.6), (oc[0] + side * 1.8, lid_y - 0.4)]
    c.drawPath(tp(lid, 2.4, 1.0), skia.Paint(AntiAlias=True, Color=C(col)))


def brow(c, x, y, inner_dy, outer_dy, side, col, w=3.6, L=14, thick=None):
    """side=-1 olho esquerdo da tela. inner = perto do nariz."""
    xi = x - side * L * 0.45
    xo = x + side * L * 0.55
    pts = [(xi, y + inner_dy), (x, y + (inner_dy + outer_dy) / 2 - 1.5), (xo, y + outer_dy)]
    c.drawPath(tp(pts, thick or w, (thick or w) * 0.55), skia.Paint(AntiAlias=True, Color=C(col)))


def mouth(c, x, y, kind, s=1.0, dark=(120, 44, 44), lip=(60, 30, 30)):
    if kind == 'smile':
        ink(c, [(x - 9 * s, y - 2 * s), (x, y + 3.5 * s), (x + 9 * s, y - 2 * s)], 2.6 * s, lip, 0.9, 2.0 * s)
    elif kind == 'smile_open':
        p = smooth([(x - 11 * s, y - 3 * s), (x, y - 1 * s), (x + 11 * s, y - 3 * s), (x + 6 * s, y + 7 * s),
                    (x, y + 9 * s), (x - 6 * s, y + 7 * s)], tension=0.5)
        flat(c, p, dark)
        c.save(); c.clipPath(p, doAntiAlias=True)
        flat(c, ell(x, y + 9 * s, 7 * s, 4.5 * s), (220, 110, 110))
        flat(c, rr(x - 10 * s, y - 4 * s, x + 10 * s, y + 0.5 * s, 1), (252, 248, 240), 0.9)
        c.restore()
    elif kind == 'flat_down':
        ink(c, [(x - 8 * s, y + 2.5 * s), (x, y - 1.5 * s), (x + 8 * s, y + 2.5 * s)], 2.6 * s, lip, 0.9, 2.0 * s)
    elif kind == 'wobble':
        ink(c, [(x - 7 * s, y + 1 * s), (x - 3.5 * s, y - 1 * s), (x, y + 1 * s), (x + 3.5 * s, y - 1 * s),
                (x + 7 * s, y + 1 * s)], 2.3 * s, lip, 0.9, 2.0 * s)
    elif kind == 'cry':
        p = smooth([(x - 9 * s, y + 5 * s), (x - 5 * s, y - 2 * s), (x, y - 4 * s), (x + 5 * s, y - 2 * s),
                    (x + 9 * s, y + 5 * s), (x, y + 3 * s)], tension=0.5)
        flat(c, p, dark)
    elif kind == 'firm':
        ink(c, [(x - 7 * s, y), (x, y + 0.6 * s), (x + 7 * s, y)], 2.8 * s, lip, 0.9, 2.6 * s)
    elif kind == 'tongue':
        ink(c, [(x - 7 * s, y), (x + 1 * s, y + 1 * s), (x + 8 * s, y - 1 * s)], 2.5 * s, lip, 0.9, 2.2 * s)
        flat(c, ell(x + 5 * s, y + 3.5 * s, 3.6 * s, 3 * s), (224, 112, 112))
    elif kind == 'o':
        flat(c, ell(x, y + 1 * s, 4.5 * s, 5.5 * s), dark)
    elif kind == 'gentle':
        ink(c, [(x - 6 * s, y - 0.5 * s), (x, y + 2 * s), (x + 6 * s, y - 0.5 * s)], 2.2 * s, lip, 0.85, 1.8 * s)


def tear_streams(c, pts_l, pts_r):
    for pts in (pts_l, pts_r):
        p = tp(pts, 4.5, 2.4)
        layer(c, p, (196, 226, 238), depth=0.05, a=0.55, fiber=False, inner=False, shadow=False)
        flat(c, ell(pts[-1][0], pts[-1][1] + 2, 3.6, 4.6), (196, 226, 238), 0.7)


# ============================================================ PING
PING_EXPR = {
    'neutro':      dict(eyes='open', brows=(0, 0), mouth='smile', blush=0.45),
    'encanto':     dict(eyes='wide', brows=(-5, -4), mouth='smile_open', blush=0.55),
    'concentrado': dict(eyes='half', brows=(1, 1), mouth='tongue', blush=0.4, look=(1.5, 2)),
    'decepcionado': dict(eyes='half', brows=(-6, 3), mouth='flat_down', blush=0.35, look=(0, 2)),
    'vergonha':    dict(eyes='down', brows=(-9, 4), mouth='wobble', blush=1.4, look=(-2, 4), tilt=-9),
    'choro':       dict(eyes='half', brows=(-8, 4), mouth='cry', blush=0.8, wet=True, tears=True),
    'coragem':     dict(eyes='open', brows=(3, -3), mouth='firm', blush=0.6, wet=True),
    'alegria':     dict(eyes='happy', brows=(-5, -3), mouth='smile_open', blush=0.75),
}


def ping_head(c, expr='neutro', t=0.0):
    e = PING_EXPR[expr]
    P = PING
    hx, hy = 0, -238
    c.save()
    c.rotate(e.get('tilt', 0), hx, hy + 40)
    # coque + fita (atrás)
    layer(c, circ(hx + 2, hy - 58, 15), P['hair'], depth=0.15, seed=1)
    for s in (-1, 1):
        layer(c, tp([(hx + 2, hy - 52), (hx + 2 + s * 14, hy - 46), (hx + 2 + s * 22, hy - 34)], 7, 3),
              P['sash'], depth=0.1, seed=2 + s)
    layer(c, ell(hx + 2, hy - 50, 9, 6), P['sash'], depth=0.1, seed=4)
    # orelhas
    for s in (-1, 1):
        layer(c, ell(hx + s * 50, hy + 4, 9, 11), mul(P['skin'], 0.96), depth=0.1, seed=5 + s)
        flat(c, ell(hx + s * 50, hy + 5, 4, 6), mul(P['skin'], 0.82), 0.6)
    # rosto (redondo, bochecha cheia)
    pts = []
    for i in range(28):
        a = i / 28 * 2 * math.pi
        r_x, r_y = 51, 48
        bulge = 1 + 0.06 * max(0, math.sin(a)) * abs(math.cos(a)) * 2
        pts.append((hx + math.cos(a) * r_x * bulge, hy + 4 + math.sin(a) * r_y * (1.02 if math.sin(a) > 0 else 1)))
    face = smooth(pts)
    layer(c, face, P['skin'], depth=0.2, seed=7)
    # blush
    for s in (-1, 1):
        flat(c, ell(hx + s * 31, hy + 20, 11, 7), P['blush'], 0.35 * e['blush'], blur=5)
    look = e.get('look', (0, 0))
    for s in (-1, 1):
        almond_eye(c, hx + s * 19, hy + 6, e['eyes'], P['eye'], side=s, look=look, wet=e.get('wet', False))
    # nariz botão
    flat(c, ell(hx + 1, hy + 18, 4.5, 3.6), mul(P['skin'], 0.86), 0.9)
    flat(c, circ(hx - 0.5, hy + 16.8, 1.4), (255, 240, 225), 0.7)
    mouth(c, hx + 1, hy + 31, e['mouth'])
    if e.get('tears'):
        tear_streams(c, [(hx - 21, hy + 14), (hx - 24, hy + 26), (hx - 22, hy + 38)],
                     [(hx + 21, hy + 14), (hx + 24, hy + 26), (hx + 23, hy + 36)])
    # cabelo (franja recortada) por cima
    hair = smooth([(hx - 53, hy + 14), (hx - 56, hy - 18), (hx - 40, hy - 46), (hx, hy - 56), (hx + 40, hy - 46),
                   (hx + 56, hy - 18), (hx + 53, hy + 14), (hx + 46, hy + 4), (hx + 44, hy - 12), (hx + 32, hy - 16),
                   (hx + 22, hy - 10), (hx + 10, hy - 18), (hx - 2, hy - 11), (hx - 14, hy - 19),
                   (hx - 27, hy - 11), (hx - 40, hy - 17), (hx - 45, hy - 2), (hx - 47, hy + 6)], tension=0.42)
    layer(c, hair, P['hair'], depth=0.18, seed=9)
    # mechas finas em tom diferente
    for k, (x0, x1, y1) in enumerate([(-30, -42, -10), (-12, -20, -12), (6, 0, -10), (24, 18, -12), (38, 44, -8),
                                      (-44, -52, 6), (46, 52, 4)]):
        ink(c, [(hx + x0 * 0.6, hy - 50), (hx + (x0 + x1) / 2, hy - 30), (hx + x1, hy + y1)], 2.6, P['hair_hi'], 0.75, 0.8)
    # sobrancelhas
    bi, bo = e['brows']
    for s in (-1, 1):
        brow(c, hx + s * 19, hy - 9, bi, bo, s, (30, 24, 28), w=3.8, L=15)
    c.restore()


def pot(c, x, y, s=1.0, empty=True, seed=0.0):
    """Pote de barro com faixa pintada; terra de papel kraft. (x,y) = base."""
    P = POT
    w0, w1, h = 30 * s, 22 * s, 56 * s
    body = smooth([(x - w0 - 4 * s, y - h), (x - w0, y - h * 0.62), (x - w1 - 2 * s, y - h * 0.15), (x - w1, y),
                   (x + w1, y), (x + w1 + 2 * s, y - h * 0.15), (x + w0, y - h * 0.62), (x + w0 + 4 * s, y - h)],
                  tension=0.4)
    layer(c, body, P['clay'], depth=0.25, seed=seed + 11)
    band = inter(body, rr(x - 50 * s, y - h * 0.62, x + 50 * s, y - h * 0.42, 1))
    layer(c, band, P['band'], depth=0.05, shadow=False, seed=seed + 12)
    # ondinhas pintadas na faixa
    for k in range(5):
        xx = x - 22 * s + k * 11 * s
        ink(c, [(xx - 4 * s, y - h * 0.5), (xx, y - h * 0.56), (xx + 4 * s, y - h * 0.5)], 1.8 * s, (60, 96, 130), 0.85)
    # borda
    layer(c, ell(x, y - h, w0 + 7 * s, 7 * s), P['rim'], depth=0.12, seed=seed + 13)
    # terra (kraft) — vazio
    layer(c, ell(x, y - h + 0.5 * s, w0 + 2 * s, 4.6 * s), P['earth'], depth=0.02, shadow=False, rim=False, seed=seed + 14)
    for k in range(6):
        flat(c, circ(x - 18 * s + k * 7 * s, y - h + (1 if k % 2 else -0.5) * s, 1.3 * s), mul(P['earth'], 0.7), 0.8)
    return body


def ping(c, expr='neutro', pose='hold_pot', t=0.0):
    P = PING
    contact_shadow(c, 0, 0, 46, 7)
    # pernas + sapatos
    for s in (-1, 1):
        leg = rr(s * 15 - 12, -100, s * 15 + 12, -14, 8)
        layer(c, leg, P['pants'], depth=0.15, seed=20 + s)
        layer(c, rr(s * 15 - 14, -30, s * 15 + 14, -20, 4), mul(P['pants'], 0.92), depth=0.06, seed=22 + s)
        ink(c, [(s * 15 - 10, -26), (s * 15 + 10, -25)], 1.4, (120, 100, 80), 0.6)
        layer(c, ell(s * 17, -9, 17, 9), P['shoes'], depth=0.12, seed=24 + s)
    # pescoço
    layer(c, rr(-10, -200, 10, -182, 4), mul(P['skin'], 0.9), depth=0.05, seed=26)
    # túnica (trapézio arredondado)
    tunic = smooth([(-34, -190), (34, -190), (44, -150), (52, -98), (40, -90), (0, -88), (-40, -90), (-52, -98), (-44, -150)],
                   tension=0.35)
    layer(c, tunic, P['tunic'], depth=0.25, seed=27)
    # remendo costurado
    patch = poly([(-38, -122), (-20, -124), (-19, -104), (-37, -103)])
    layer(c, patch, P['tunic_patch'], depth=0.04, shadow=False, seed=28)
    for k in range(5):
        ink(c, [(-39 + k * 4.4, -126), (-38 + k * 4.4, -121)], 1.3, (238, 226, 200), 0.85)
        ink(c, [(-39 + k * 4.4, -101), (-38 + k * 4.4, -106)], 1.3, (238, 226, 200), 0.85)
    # dobras de nanquim
    ink(c, [(20, -140), (24, -118), (30, -96)], 1.6, mul(P['tunic'], 0.45), 0.55)
    ink(c, [(-8, -132), (-6, -110), (-10, -92)], 1.4, mul(P['tunic'], 0.45), 0.45)
    # gola mandarim + abotoamento
    layer(c, rr(-16, -194, 16, -182, 5), P['collar'], depth=0.05, seed=29)
    ink(c, [(4, -182), (12, -164), (22, -150)], 2.0, P['collar'], 0.95, 2.0)
    for k, yy in enumerate((-170, -158)):
        layer(c, ell(11 + k * 6, yy, 3.4, 2.4), P['sash'], depth=0.03, shadow=False, seed=30 + k)
    # faixa (acento)
    sash = smooth([(-46, -142), (46, -142), (48, -130), (-48, -130)], tension=0.2)
    layer(c, sash, P['sash'], depth=0.08, seed=32)
    layer(c, tp([(30, -134), (36, -120), (32, -104)], 8, 4), P['sash'], depth=0.08, seed=33)
    layer(c, tp([(30, -134), (24, -118), (26, -106)], 7, 3), mul(P['sash'], 0.9), depth=0.08, seed=34)
    # braços
    sh = {-1: (-34, -184), 1: (34, -184)}
    if pose == 'hold_pot':
        hands = {-1: (-28, -146), 1: (28, -146)}
    elif pose == 'hide_pot':
        hands = {-1: (-30, -118), 1: (30, -118)}
    else:  # down
        hands = {-1: (-44, -118), 1: (44, -118)}
    arm_parts = {}
    for s in (-1, 1):
        el, hd = ik(sh[s], hands[s], 34, 32, s)
        arm_parts[s] = (el, hd)
    # braço de trás (nenhum aqui) — pote antes das mãos
    for s in (-1, 1):
        el, hd = arm_parts[s]
        layer(c, limb(sh[s], el, 20, 17), P['tunic'], depth=0.2, seed=40 + s)
    if pose == 'hold_pot':
        pot(c, 0, -110, 1.0)
    for s in (-1, 1):
        el, hd = arm_parts[s]
        layer(c, limb(el, hd, 17, 15), mul(P['tunic'], 0.97), depth=0.2, seed=42 + s)
        layer(c, ell(hd[0], hd[1], 10, 9), P['skin'], depth=0.12, seed=44 + s)
        ink(c, [(hd[0] - s * 2, hd[1] - 4), (hd[0] + s * 5, hd[1] - 1)], 1.2, mul(P['skin'], 0.6), 0.5)
    ping_head(c, expr, t)


# ============================================================ IMPERADOR
IMP_EXPR = {
    'sereno':        dict(eyes='narrow', brows=(0, 0), mouth='gentle', tilt=0),
    'testa_franzida': dict(eyes='narrow', brows=(7, -5), mouth='flat_down', tilt=0, frown=True),
    'pergunta':      dict(eyes='open', brows=(-6, 2), mouth='o', tilt=6),
    'sorriso':       dict(eyes='happy', brows=(-3, 4), mouth='smile', tilt=-3),
}


def imp_head(c, expr='sereno', t=0.0):
    e = IMP_EXPR[expr]
    P = IMP
    hx, hy = 0, -392
    c.save()
    c.rotate(e.get('tilt', 0), hx, hy + 60)
    # orelhas longas
    for s in (-1, 1):
        layer(c, ell(hx + s * 38, hy + 4, 8, 17), mul(P['skin'], 0.95), depth=0.1, seed=60 + s)
    # rosto longo
    face = smooth([(hx, hy - 54), (hx + 30, hy - 46), (hx + 39, hy - 10), (hx + 36, hy + 26), (hx + 22, hy + 50),
                   (hx, hy + 56), (hx - 22, hy + 50), (hx - 36, hy + 26), (hx - 39, hy - 10), (hx - 30, hy - 46)], tension=0.45)
    layer(c, face, P['skin'], depth=0.2, seed=62)
    # rugas da testa
    for k, yy in enumerate((-30, -22)):
        ink(c, [(hx - 16 + k * 3, hy + yy), (hx, hy + yy - 2), (hx + 16 - k * 3, hy + yy)], 1.3, mul(P['skin'], 0.55), 0.5)
    if e.get('frown'):
        ink(c, [(hx - 3, hy - 14), (hx - 2, hy - 4)], 1.6, mul(P['skin'], 0.5), 0.7)
        ink(c, [(hx + 3, hy - 14), (hx + 2, hy - 4)], 1.6, mul(P['skin'], 0.5), 0.7)
    for s in (-1, 1):
        eye(c, hx + s * 16, hy - 2, e['eyes'], P['eye'], rx=5.5, ry=7)
        # pés de galinha
        for k in range(3):
            ink(c, [(hx + s * 25, hy - 4 + k * 3), (hx + s * 31, hy - 7 + k * 4)], 1.1, mul(P['skin'], 0.55), 0.5)
    # nariz romano
    nose = smooth([(hx - 2, hy - 8), (hx + 4, hy + 4), (hx + 6, hy + 16), (hx + 2, hy + 22), (hx - 5, hy + 21),
                   (hx - 4, hy + 6)], tension=0.45)
    layer(c, nose, mul(P['skin'], 0.95), depth=0.08, seed=63)
    ink(c, [(hx + 3, hy - 4), (hx + 7, hy + 8), (hx + 5, hy + 18)], 1.4, mul(P['skin'], 0.5), 0.55)
    # barba longa (triângulo) com fios
    beard = smooth([(hx - 26, hy + 26), (hx - 20, hy + 60), (hx - 8, hy + 110), (hx, hy + 128), (hx + 8, hy + 110),
                    (hx + 20, hy + 60), (hx + 26, hy + 26), (hx + 12, hy + 40), (hx, hy + 44), (hx - 12, hy + 40)], tension=0.4)
    layer(c, beard, P['beard'], depth=0.18, seed=64)
    for k in range(-3, 4):
        ink(c, [(hx + k * 5, hy + 48), (hx + k * 4, hy + 80), (hx + k * 1.6, hy + 112)], 1.2, (170, 166, 160), 0.55)
    mouth(c, hx, hy + 33, e['mouth'], s=0.8)
    # bigode caído
    for s in (-1, 1):
        layer(c, tp([(hx + s * 2, hy + 25), (hx + s * 16, hy + 28), (hx + s * 28, hy + 44), (hx + s * 32, hy + 66)], 6, 2),
              P['beard'], depth=0.12, seed=66 + s)
    # sobrancelhas longas e brancas, caídas
    bi, bo = e['brows']
    for s in (-1, 1):
        pts = [(hx + s * 5, hy - 14 + bi), (hx + s * 20, hy - 18 + (bi + bo) / 2), (hx + s * 36, hy - 12 + bo), (hx + s * 46, hy + 2 + bo)]
        layer(c, tp(pts, 6, 2), P['beard'], depth=0.08, seed=68 + s)
    # chapéu alto
    hat = smooth([(hx - 34, hy - 36), (hx - 36, hy - 80), (hx - 26, hy - 104), (hx, hy - 110), (hx + 26, hy - 104),
                  (hx + 36, hy - 80), (hx + 34, hy - 36)], tension=0.4)
    layer(c, hat, P['hat'], depth=0.2, seed=70)
    for k in range(3):
        ink(c, [(hx - 20 + k * 20, hy - 46), (hx - 18 + k * 18, hy - 100)], 1.2, (70, 72, 100), 0.5)
    layer(c, rr(hx - 38, hy - 50, hx + 38, hy - 36, 6), P['panel'], depth=0.06, seed=71)
    for k in range(7):
        flat(c, circ(hx - 30 + k * 10, hy - 43, 2), P['panel_dk'], 0.8)
    layer(c, ell(hx, hy - 62, 8, 9), P['jade'], depth=0.08, seed=72)
    c.restore()


def cloud_mark(c, x, y, s, col, a=0.85):
    ink(c, [(x - 8 * s, y + 2 * s), (x - 4 * s, y - 5 * s), (x + 2 * s, y - 4 * s), (x + 3 * s, y + 1 * s), (x - 1 * s, y + 2 * s)],
        1.8 * s, col, a, 1.2 * s)
    ink(c, [(x + 3 * s, y + 1 * s), (x + 8 * s, y - 2 * s), (x + 11 * s, y + 3 * s)], 1.8 * s, col, a, 1.2 * s)


def imperador(c, expr='sereno', pose='sleeves', t=0.0):
    P = IMP
    contact_shadow(c, 0, 0, 70, 9)
    # sapatos de ponta curva
    for s in (-1, 1):
        layer(c, smooth([(s * 14, -14), (s * 44, -14), (s * 54, -22), (s * 50, -6), (s * 14, -2)], tension=0.4), P['hat'], depth=0.1, seed=80 + s)
    # manto
    robe = smooth([(-48, -340), (48, -340), (62, -300), (78, -150), (94, -14), (0, -8), (-94, -14), (-78, -150), (-62, -300)], tension=0.3)
    layer(c, robe, P['robe'], depth=0.3, seed=82)
    # painel dourado com nuvens vazadas
    panel = poly([(-22, -310), (22, -310), (38, -12), (-38, -12)])
    layer(c, panel, P['panel'], depth=0.06, seed=83)
    for (x, y, s) in [(-10, -230, 1.1), (12, -190, 1.0), (-14, -140, 1.2), (14, -96, 1.1), (-6, -52, 1.3), (16, -34, 0.9)]:
        cloud_mark(c, x, y, s, P['panel_dk'])
    for k in range(9):
        flat(c, circ(-30 + k * 7.5, -20, 2.2), P['robe_dk'], 0.85)
    # vincos do manto
    for s in (-1, 1):
        ink(c, [(s * 48, -250), (s * 60, -150), (s * 70, -30)], 1.6, mul(P['robe'], 0.45), 0.6)
    # gola cruzada
    ink(c, [(-26, -342), (0, -300), (18, -268)], 5, P['collar'], 0.95, 5)
    ink(c, [(26, -342), (6, -312)], 5, P['collar'], 0.95, 5)
    # faixa vermelha (acento)
    layer(c, rr(-50, -290, 50, -276, 4), P['sash'], depth=0.06, seed=84)
    layer(c, tp([(-14, -280), (-18, -250), (-12, -220)], 8, 4), P['sash'], depth=0.06, seed=85)
    # pescoço
    layer(c, rr(-12, -350, 12, -334, 4), mul(P['skin'], 0.9), depth=0.05, seed=86)
    # mangas largas
    for s in (-1, 1):
        if pose == 'sleeves':
            sleeve = smooth([(s * 46, -338), (s * 70, -300), (s * 74, -250), (s * 60, -214), (s * 4, -218), (s * 6, -250),
                             (s * 34, -280)], tension=0.4)
        else:  # beard: braço direito (s=+1) ergue a mão para a barba
            if s == 1:
                sleeve = smooth([(46, -338), (72, -300), (64, -262), (30, -252), (16, -270), (36, -300)], tension=0.4)
            else:
                sleeve = smooth([(-46, -338), (-72, -300), (-80, -220), (-70, -170), (-44, -176), (-50, -240)], tension=0.4)
        layer(c, sleeve, mul(P['robe'], 1.08), depth=0.25, seed=88 + s)
        ink(c, [(s * 54, -310), (s * 60, -262)], 1.4, mul(P['robe'], 0.45), 0.55)
    if pose == 'sleeves':
        layer(c, rr(-10, -228, 10, -212, 5), P['panel'], depth=0.05, seed=90)  # punho dourado no encontro
    imp_head(c, expr, t)
    if pose == 'beard':
        layer(c, ell(18, -272, 9, 8), P['skin'], depth=0.1, seed=91)
        ink(c, [(14, -276), (22, -274)], 1.2, mul(P['skin'], 0.6), 0.5)


# ============================================================ PAI
PAI_EXPR = {
    'terno':  dict(eyes='half', brows=(-4, 3), mouth='gentle'),
    'apoio':  dict(eyes='happy', brows=(-3, 2), mouth='smile'),
}


def pai_head(c, expr='terno', t=0.0):
    e = PAI_EXPR[expr]
    P = PAI
    hx, hy = 0, -345
    for s in (-1, 1):
        layer(c, ell(hx + s * 47, hy + 4, 8, 12), mul(P['skin'], 0.95), depth=0.1, seed=101 + s)
    face = rr(hx - 46, hy - 50, hx + 46, hy + 54, 30)
    layer(c, face, P['skin'], depth=0.2, seed=103)
    # cabelo curto, chato, grisalho nas têmporas
    hair = smooth([(hx - 48, hy - 6), (hx - 50, hy - 40), (hx - 30, hy - 58), (hx + 30, hy - 58), (hx + 50, hy - 40),
                   (hx + 48, hy - 6), (hx + 40, hy - 26), (hx, hy - 34), (hx - 40, hy - 26)], tension=0.35)
    layer(c, hair, P['hair'], depth=0.15, seed=104)
    for s in (-1, 1):
        layer(c, tp([(hx + s * 44, hy - 30), (hx + s * 47, hy - 14), (hx + s * 46, hy - 2)], 7, 3), P['gray'], depth=0.04, shadow=False, seed=105 + s)
    for k in range(-2, 3):
        ink(c, [(hx + k * 14, hy - 52), (hx + k * 16, hy - 34)], 1.6, (80, 74, 80), 0.6)
    for s in (-1, 1):
        eye(c, hx + s * 18, hy, e['eyes'], P['eye'], rx=5, ry=6.5)
        brow(c, hx + s * 18, hy - 15, e['brows'][0], e['brows'][1], s, (34, 28, 28), w=6.5, L=19)
    # nariz grande e redondo
    layer(c, ell(hx, hy + 18, 10, 9), mul(P['skin'], 0.93), depth=0.08, seed=107)
    flat(c, circ(hx - 3, hy + 15, 2.2), (255, 236, 214), 0.5)
    # bigode
    for s in (-1, 1):
        layer(c, tp([(hx + s * 2, hy + 29), (hx + s * 14, hy + 30), (hx + s * 22, hy + 38)], 8, 3), P['hair'], depth=0.06, seed=108 + s)
    mouth(c, hx, hy + 42, e['mouth'], s=0.9)
    for s in (-1, 1):
        ink(c, [(hx + s * 24, hy + 26), (hx + s * 27, hy + 38)], 1.3, mul(P['skin'], 0.55), 0.5)


def pai_hat(c):
    P = PAI
    hx, hy = 0, -345
    # chapéu de palha pendurado nas costas (atrás do ombro esquerdo, inclinado)
    c.save(); c.translate(hx - 64, hy + 78); c.rotate(-28)
    layer(c, ell(0, 0, 62, 40), P['straw'], depth=0.25, seed=100)
    layer(c, ell(0, -4, 26, 18), mul(P['straw'], 0.92), depth=0.08, seed=99)
    for r in (34, 46, 56):
        c.drawPath(xform(ell(0, 0, r, r * 0.64)), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                   StrokeWidth=1.3, Color=C((150, 112, 60), 0.45)))
    for k in range(16):
        a = k / 16 * 2 * math.pi
        ink(c, [(math.cos(a) * 26, math.sin(a) * 17), (math.cos(a) * 58, math.sin(a) * 37)], 1.0, (150, 112, 60), 0.3, 0.6)
    c.restore()
    ink(c, [(hx - 30, hy + 52), (hx - 50, hy + 66)], 1.6, (120, 90, 50), 0.8)


def pai(c, expr='terno', pose='apoio', t=0.0):
    P = PAI
    contact_shadow(c, 0, 0, 64, 9)
    pai_hat(c)
    for s in (-1, 1):
        layer(c, rr(s * 22 - 18, -160, s * 22 + 18, -34, 10), P['pants'], depth=0.15, seed=120 + s)
        layer(c, rr(s * 22 - 19, -50, s * 22 + 19, -36, 4), mul(P['pants'], 1.12), depth=0.05, seed=122 + s)
        layer(c, rr(s * 22 - 10, -36, s * 22 + 10, -10, 4), P['skin'], depth=0.05, seed=124 + s)
        layer(c, ell(s * 24, -7, 22, 8), P['sandal'], depth=0.1, seed=126 + s)
        ink(c, [(s * 24 - 12, -12), (s * 24 + 12, -12)], 2.2, mul(P['sandal'], 0.6), 0.8)
    layer(c, rr(-13, -300, 13, -282, 5), mul(P['skin'], 0.9), depth=0.05, seed=128)
    tunic = smooth([(-56, -292), (56, -292), (72, -250), (74, -150), (0, -144), (-74, -150), (-72, -250)], tension=0.25)
    layer(c, tunic, P['tunic'], depth=0.28, seed=129)
    ink(c, [(-30, -290), (0, -240), (0, -150)], 2.0, P['tunic_dk'], 0.7)
    ink(c, [(40, -230), (46, -190), (44, -158)], 1.5, P['tunic_dk'], 0.55)
    # remendo no ombro + corda na cintura
    layer(c, poly([(30, -286), (52, -284), (54, -264), (32, -266)]), mul(P['tunic'], 1.12), depth=0.04, shadow=False, seed=130)
    for k in range(5):
        ink(c, [(30 + k * 5, -289), (31 + k * 5, -284)], 1.2, (90, 60, 30), 0.7)
    layer(c, rr(-74, -194, 74, -184, 4), P['rope'], depth=0.06, seed=131)
    for k in range(14):
        ink(c, [(-70 + k * 10.5, -193), (-64 + k * 10.5, -185)], 1.1, mul(P['rope'], 0.6), 0.6)
    layer(c, tp([(-20, -188), (-26, -168), (-22, -150)], 6, 3), P['rope'], depth=0.06, seed=132)
    sh = {-1: (-52, -280), 1: (52, -280)}
    if pose == 'apoio':
        hands = {-1: (-66, -168), 1: (88, -176)}
    else:
        hands = {-1: (-72, -170), 1: (72, -170)}
    for s in (-1, 1):
        el, hd = ik(sh[s], hands[s], 54, 50, s)
        layer(c, limb(sh[s], el, 30, 26), P['tunic'], depth=0.22, seed=134 + s)
        mid = (el[0] + (hd[0] - el[0]) * 0.2, el[1] + (hd[1] - el[1]) * 0.2)
        layer(c, limb(el, hd, 22, 18), P['skin'], depth=0.2, seed=136 + s)
        layer(c, limb(el, mid, 30, 28), mul(P['tunic'], 1.1), depth=0.1, seed=138 + s)  # manga dobrada
        layer(c, ell(hd[0], hd[1], 14, 12), P['skin'], depth=0.12, seed=140 + s)
        ink(c, [(hd[0] - 6, hd[1] - 3), (hd[0] + 6, hd[1] - 4)], 1.3, mul(P['skin'], 0.6), 0.5)
    pai_head(c, expr, t)


# ============================================================ PARDAL
BIRD_EXPR = {
    'curioso':      dict(tilt=-16, eye='wide', droop=0),
    'decepcionado': dict(tilt=8, eye='half', droop=1),
}


def pardal(c, expr='curioso', t=0.0):
    e = BIRD_EXPR[expr]
    P = BIRD
    contact_shadow(c, 0, 0, 20, 4)
    for s in (-1, 1):
        ink(c, [(s * 5, -12), (s * 6, -2), (s * 6 + 4, 0)], 1.8, (90, 60, 40), 0.9, 1.4)
    tail = tp([(-14, -24), (-30, -30 + 6 * e['droop']), (-42, -32 + 12 * e['droop'])], 12, 6)
    layer(c, tail, P['wing'], depth=0.12, seed=150)
    layer(c, ell(0, -22, 22, 16), P['back'], depth=0.18, seed=151)
    layer(c, ell(4, -16, 16, 10), P['belly'], depth=0.04, shadow=False, seed=152)
    wing = smooth([(-14, -30), (8, -32), (14, -24), (2, -14 + 2 * e['droop']), (-20, -16 + 4 * e['droop'])], tension=0.4)
    layer(c, wing, P['wing'], depth=0.1, seed=153)
    for k in range(4):
        ink(c, [(-14 + k * 6, -26), (-10 + k * 6, -18)], 1.2, (240, 224, 196), 0.6)
    c.save()
    c.rotate(e['tilt'], 12, -36)
    layer(c, circ(14, -40, 13), P['back'], depth=0.15, seed=154)
    layer(c, smooth([(4, -50), (16, -54), (26, -46), (14, -44)], tension=0.4), P['cap'], depth=0.04, shadow=False, seed=155)
    layer(c, ell(18, -35, 7, 5), P['cheek'], depth=0.02, shadow=False, seed=156)
    layer(c, poly([(25, -42), (35, -39), (25, -35)]), P['beak'], depth=0.05, seed=157)
    eye(c, 18, -42, e['eye'], P['eye'], rx=2.8, ry=3.4)
    c.restore()
