"""Personagens de O Pote Vazio (originais, paper style 2.0).
Coordenadas locais: origem nos pés, cabeça = ~100 unidades. Expressões por nome."""
import math
import skia
from paperlib import (layer, flat, ink, smooth, poly, ell, circ, rr, union, inter, diff, xform, tp,
                      ik, limb, contact_shadow, C, mix, mul, SCALE, STYLE)

# ============================================================ paletas
PING = dict(skin=(238, 200, 166), blush=(228, 128, 112), hair=(52, 51, 49), hair_hi=(96, 94, 90),
            tunic=(113, 134, 107), tunic_patch=(146, 162, 128), collar=(222, 208, 174),
            sash=(146, 113, 78), pants=(222, 208, 174), shoes=(60, 54, 48), eye=(40, 30, 28))
IMP = dict(skin=(230, 198, 170), robe=(154, 71, 57), robe_dk=(110, 48, 40), panel=(201, 163, 93),
           panel_dk=(150, 116, 58), collar=(204, 197, 179), sash=(67, 61, 49), beard=(204, 197, 179),
           hat=(67, 61, 49), jade=(201, 163, 93), eye=(40, 30, 28))
PAI = dict(skin=(199, 150, 112), hair=(52, 46, 42), gray=(150, 146, 140), tunic=(119, 120, 107),
           tunic_dk=(90, 92, 80), pants=(73, 66, 57), rope=(163, 139, 109), straw=(199, 161, 122),
           eye=(36, 26, 24), sandal=(110, 84, 60))
RIVAL = dict(skin=(236, 208, 176), tunic=(193, 139, 67), red=(163, 76, 55), vase=(225, 200, 150),
             dark=(68, 52, 43), bead=(150, 200, 220), petal=(226, 120, 150), petal2=(196, 80, 120), eye=(40, 30, 28))
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


def almond_eye(c, x, y, kind, col, side=1, look=(0, 0), wet=False, rx=8.2, ry=6.0, cute=False, mono=False):
    """Olho amendoado pequeno e delicado (traço de livro ilustrado): ponto escuro,
    pálpebra superior em nanquim, brilho mínimo."""
    if kind in ('happy', 'closed'):
        if kind == 'happy':
            pts = [(x - rx * 1.15, y + 1.5), (x, y - ry * 0.9), (x + rx * 1.15, y + 1.5)]
        else:
            pts = [(x - rx * 1.15, y - 0.5), (x, y + ry * 0.5), (x + rx * 1.15, y - 0.5)]
        c.drawPath(tp(pts, 2.6, 2.0), skia.Paint(AntiAlias=True, Color=C(col)))
        return
    sy = {'open': 1.0, 'wide': 1.25, 'half': 0.95, 'down': 0.9, 'narrow': 0.8}[kind]
    ex, ey = x + look[0] * 0.6, y + look[1] * 0.5
    ic = (ex - side * rx, ey + 0.6)              # canto interno
    oc = (ex + side * rx * 1.08, ey - 1.0)        # canto externo levemente acima
    top = [(ic[0], ic[1]), (ex - side * rx * 0.3, ey - ry * sy), (ex + side * rx * 0.45, ey - ry * sy * 0.9), oc]
    bot = [(ex + side * rx * 0.3, ey + ry * sy * 0.62), (ex - side * rx * 0.4, ey + ry * sy * 0.55)]
    if mono:   # pálpebra única: topo mais reto, canto externo erguido, olho mais alongado
        ic = (ex - side * rx, ey + 1.2)
        oc = (ex + side * rx * 1.12, ey - ry * sy * 0.75)
        top = [ic, (ex - side * rx * 0.45, ey - ry * sy * 0.7), (ex + side * rx * 0.35, ey - ry * sy * 0.85), oc]
        bot = [(ex + side * rx * 0.45, ey + ry * sy * 0.55), (ex - side * rx * 0.35, ey + ry * sy * 0.6)]
    shape = smooth(top + bot, tension=0.5)
    if kind in ('half', 'down', 'narrow'):
        lid_y = ey - ry * sy * (0.5 if kind == 'half' else 0.3)
        shape = inter(shape, rr(ex - 20, lid_y, ex + 20, ey + 20, 1))
    else:
        lid_y = None
    # branco do olho + íris castanha + pupila (recortados dentro do amendoado)
    flat(c, shape, (250, 246, 238))
    c.save(); c.clipPath(shape, doAntiAlias=True)
    flat(c, ell(ex, ey + ry * sy * 0.1, rx * 1.3, ry * sy * 0.5), (220, 206, 196), 0.35, blur=1)  # sombra da pálpebra no branco
    ix, iy = ex + look[0] * 0.5, ey - ry * sy * 0.05 + look[1] * 0.4
    ir = ry * 1.02
    if mono:   # íris maior, um pouco mais baixa: a pálpebra cobre o alto
        ir = ry * 1.15; iy = ey + ry * sy * 0.08 + look[1] * 0.4
    flat(c, circ(ix, iy, ir), (92, 58, 38))
    flat(c, circ(ix, iy + ir * 0.25, ir * 0.75), (120, 80, 50), 0.6)
    flat(c, circ(ix, iy, ir * 0.5), (22, 16, 16))
    hl = (1.6 if not wet else 2.2) * (1.6 if cute else 1.0)
    flat(c, circ(ix - side * ir * 0.35, iy - ir * 0.4, hl), (255, 252, 244), 0.95)
    if cute:
        flat(c, circ(ix + side * ir * 0.35, iy + ir * 0.4, hl * 0.5), (255, 252, 244), 0.85)
    if wet:
        flat(c, ell(ex, ey + ry * sy * 0.5, rx * 0.9, 1.4), (200, 230, 240), 0.8)
    c.restore()
    # linha de baixo, bem leve
    ink(c, [(ic[0] + side * 1.5, ic[1] + 0.6), (ex, ey + ry * sy * 0.6 + 0.6), (oc[0] - side * 1.0, oc[1] + 1.2)], 1.0, col, 0.35, 0.6)
    # pálpebra superior (traço único, afina no canto externo)
    if lid_y is None:
        lid = [(ic[0] - side * 0.5, ic[1] - 0.4), (ex - side * rx * 0.3, ey - ry * sy - 0.8),
               (ex + side * rx * 0.5, ey - ry * sy * 0.95 - 0.6), (oc[0] + side * 1.8, oc[1] - 1.2)]
        if mono:
            lid = [(ic[0] - side * 0.3, ic[1] - 0.6), (ex - side * rx * 0.45, ey - ry * sy * 0.7 - 1.0),
                   (ex + side * rx * 0.35, ey - ry * sy * 0.85 - 1.0), (oc[0] + side * 2.6, oc[1] - 1.6)]
    else:
        lid = [(ic[0] - side * 0.5, lid_y + 0.8), (ex, lid_y - 0.6), (oc[0] + side * 1.8, lid_y - 0.4)]
    c.drawPath(tp(lid, 3.0 if mono else 2.4, 1.2 if mono else 1.0), skia.Paint(AntiAlias=True, Color=C(col)))


def brow(c, x, y, inner_dy, outer_dy, side, col, w=3.6, L=14, thick=None):
    """side=-1 olho esquerdo da tela. inner = perto do nariz."""
    xi = x - side * L * 0.45
    xo = x + side * L * 0.55
    pts = [(xi, y + inner_dy), (x, y + (inner_dy + outer_dy) / 2 - 1.5), (xo, y + outer_dy)]
    c.drawPath(tp(pts, thick or w, (thick or w) * 0.55), skia.Paint(AntiAlias=True, Color=C(col)))


def mouth(c, x, y, kind, s=1.0, dark=(120, 44, 44), lip=(60, 30, 30), op=1.0):
    if kind in ('A', 'E', 'O', 'U'):
        rx, ry = {'A': (7.5, 6.5), 'E': (9.5, 3.8), 'O': (5.8, 6.8), 'U': (3.8, 4.4)}[kind]
        ry *= 0.55 + 0.6 * op
        p = smooth([(x - rx, y), (x - rx * 0.6, y - ry * 0.75), (x, y - ry * 0.85), (x + rx * 0.6, y - ry * 0.75), (x + rx, y),
                    (x + rx * 0.6, y + ry), (x, y + ry * 1.1), (x - rx * 0.6, y + ry)], tension=0.5)
        flat(c, p, dark)
        c.save(); c.clipPath(p, doAntiAlias=True)
        flat(c, ell(x, y + ry * 1.1, rx * 0.7, ry * 0.6), (214, 104, 104))
        if kind in ('A', 'E'):
            flat(c, rr(x - rx, y - ry * 1.2, x + rx, y - ry * 0.45, 1), (250, 246, 238), 0.9)
        c.restore()
        ink(c, [(x - rx - 1, y), (x, y - ry * 0.95), (x + rx + 1, y)], 1.6, lip, 0.5, 1.2)
        return
    if kind == 'M':
        ink(c, [(x - 7, y + 0.5), (x, y - 0.5), (x + 7, y + 0.5)], 3.0, lip, 0.95, 2.6)
        return
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
    'concentrado': dict(eyes='open', brows=(1, 1), mouth='tongue', blush=0.4, look=(2, 4)),
    'decepcionado': dict(eyes='open', brows=(-8, 5), mouth='flat_down', blush=0.35, look=(0, 4)),
    'vergonha':    dict(eyes='open', brows=(-9, 5), mouth='wobble', blush=1.5, look=(-4, 5), tilt=-9),
    'choro':       dict(eyes='open', brows=(-9, 5), mouth='cry', blush=0.8, wet=True, tears=True, look=(0, 1)),
    'coragem':     dict(eyes='open', brows=(0, -2), mouth='firm', blush=0.6, wet=True),
    'alegria':     dict(eyes='happy', brows=(-5, -3), mouth='smile_open', blush=0.75),
}


def ping_head(c, expr='neutro', t=0.0, mouth_kind=None, mouth_open=1.0, blink=0.0, nod=0.0, hat=False):
    """Ping fofinho, estilo livro infantil japonês: cabeça grande e redonda, bochechas cheias,
    cabelo okappa (franja reta), olhos grandes e baixos, nariz e boca pequenos."""
    e = PING_EXPR[expr]
    P = PING
    hx, hy = 0, -238
    c.save()
    c.rotate(e.get('tilt', 0), hx, hy + 40)
    c.translate(0, nod)
    # cabeça maior (≈2,6 cabeças de altura total)
    c.translate(0, -190); c.scale(1.2, 1.2); c.translate(0, 190)
    # volume de trás do cabelo
    back = smooth([(hx - 55, hy + 22), (hx - 57, hy - 16), (hx - 42, hy - 44), (hx, hy - 52), (hx + 42, hy - 44),
                   (hx + 57, hy - 16), (hx + 55, hy + 22)], tension=0.45)
    layer(c, back, P['hair'], depth=0.18, seed=1)
    # orelhas pequenas
    for s in (-1, 1):
        layer(c, ell(hx + s * 52, hy + 12, 8, 10), mul(P['skin'], 0.96), depth=0.1, seed=5 + s)
        flat(c, ell(hx + s * 52, hy + 13, 3.5, 5), mul(P['skin'], 0.82), 0.6)
    # rosto: redondo, mais largo embaixo (bochechas de bebê)
    pts = []
    for i in range(32):
        a = i / 32 * 2 * math.pi
        sx = 53 * (1 + 0.07 * max(0, math.sin(a)))
        sy = 49 * (1.04 if math.sin(a) > 0 else 1)
        pts.append((hx + math.cos(a) * sx, hy + 6 + math.sin(a) * sy))
    layer(c, smooth(pts), P['skin'], depth=0.2, seed=7)
    # bochechas rosadas grandes
    for s in (-1, 1):
        flat(c, ell(hx + s * 30, hy + 28, 13, 9), P['blush'], 0.42 * min(1.6, 0.6 + e['blush']), blur=6)
    look = e.get('look', (0, 0))
    for s in (-1, 1):
        almond_eye(c, hx + s * 20, hy + 14, 'closed' if blink > 0.5 else e['eyes'], P['eye'], side=s, look=look,
                   wet=e.get('wet', False), rx=8.6, ry=5.0, mono=True)
    # nariz mínimo
    flat(c, ell(hx, hy + 25, 2.8, 2.2), mul(P['skin'], 0.84), 0.9)
    mouth(c, hx, hy + 36, mouth_kind or e['mouth'], s=0.78, op=mouth_open)
    if e.get('tears'):
        tear_streams(c, [(hx - 22, hy + 22), (hx - 25, hy + 32), (hx - 23, hy + 44)],
                     [(hx + 22, hy + 22), (hx + 25, hy + 32), (hx + 24, hy + 42)])
    # okappa: franja reta + laterais retas na altura do queixo
    hair = smooth([(hx - 57, hy + 26), (hx - 59, hy - 14), (hx - 44, hy - 44), (hx, hy - 54), (hx + 44, hy - 44),
                   (hx + 59, hy - 14), (hx + 57, hy + 26), (hx + 46, hy + 26), (hx + 44, hy - 2), (hx + 40, hy - 6),
                   (hx + 20, hy - 5), (hx, hy - 4), (hx - 20, hy - 5), (hx - 40, hy - 6), (hx - 44, hy - 2), (hx - 46, hy + 26)],
                  tension=0.35)
    layer(c, hair, P['hair'], depth=0.18, seed=9)
    # brilho do cabelo (arco) e mechas finas
    c.drawPath(tp([(hx - 34, hy - 30), (hx - 10, hy - 41), (hx + 16, hy - 41), (hx + 34, hy - 32)], 5, 3),
               skia.Paint(AntiAlias=True, Color=C(P['hair_hi'], 0.7)))
    for x0 in (-36, -22, -8, 6, 20, 34):
        ink(c, [(hx + x0 * 0.7, hy - 47), (hx + x0 * 0.95, hy - 26), (hx + x0, hy - 6)], 1.6, P['hair_hi'], 0.6, 0.6)
    # fios desalinhados
    ink(c, [(hx + 40, hy - 30), (hx + 52, hy - 34), (hx + 58, hy - 26)], 2.2, P['hair'], 0.9, 0.8)
    # sobrancelhas curtinhas aparecendo logo abaixo da franja
    bi, bo = e['brows']
    for s in (-1, 1):
        brow(c, hx + s * 20, hy + 1, bi * 0.6, bo * 0.6, s, (40, 30, 34), w=3.0, L=11)
    if hat:   # o chapéu do imperador, grande demais para ele
        H_ = IMP
        hat_p = smooth([(hx - 46, hy - 30), (hx - 48, hy - 78), (hx - 34, hy - 104), (hx, hy - 110), (hx + 34, hy - 104),
                        (hx + 48, hy - 78), (hx + 46, hy - 30)], tension=0.4)
        layer(c, hat_p, H_['hat'], depth=0.2, seed=171)
        layer(c, rr(hx - 52, hy - 44, hx + 52, hy - 26, 7), H_['panel'], depth=0.06, seed=172)
        layer(c, ell(hx, hy - 60, 9, 10), H_['jade'], depth=0.08, seed=173)
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


def ping(c, expr='neutro', pose='hold_pot', t=0.0, face=None, squeeze=0.0, breath=0.0):
    face = face or {}
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
    if pose == 'hide_pot':
        pot(c, 30, -100, 0.92)
        for s_ in (-1, 1):
            sh_ = (s_ * 34, -184)
            el_, hd_ = ik(sh_, (s_ * 16, -112), 34, 32, s_)
            layer(c, limb(sh_, el_, 20, 17), mul(P['tunic'], 0.85), depth=0.2, seed=46 + s_)
            layer(c, limb(el_, hd_, 17, 15), mul(P['tunic'], 0.82), depth=0.2, seed=48 + s_)
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
        hands = {-1: (-28, -146 - squeeze), 1: (28, -146 - squeeze)}
    elif pose == 'hide_pot':
        hands = {-1: (-30, -118), 1: (30, -118)}
    else:  # down
        hands = {-1: (-44, -118), 1: (44, -118)}
    arm_parts = {}
    if pose == 'hide_pot':
        for s_ in (-1, 1):
            sh_ = (s_ * 36, -184)
            el_, hd_ = ik(sh_, (s_ * 16, -112), 34, 32, s_)
            layer(c, limb(sh_, (el_[0] + s_ * 2, el_[1]), 19, 16), P['tunic'], depth=0.2, seed=50 + s_)
        ping_head(c, expr, t, **face)
        return
    for s in (-1, 1):
        el, hd = ik(sh[s], hands[s], 34, 32, s)
        arm_parts[s] = (el, hd)
    # braço de trás (nenhum aqui) — pote antes das mãos
    for s in (-1, 1):
        el, hd = arm_parts[s]
        layer(c, limb(sh[s], el, 20, 17), P['tunic'], depth=0.2, seed=40 + s)
    if pose == 'hold_pot':
        pot(c, 0, -110 - squeeze, 1.0)
    for s in (-1, 1):
        el, hd = arm_parts[s]
        layer(c, limb(el, hd, 17, 15), mul(P['tunic'], 0.97), depth=0.2, seed=42 + s)
        layer(c, ell(hd[0], hd[1], 10, 9), P['skin'], depth=0.12, seed=44 + s)
        ink(c, [(hd[0] - s * 2, hd[1] - 4), (hd[0] + s * 5, hd[1] - 1)], 1.2, mul(P['skin'], 0.6), 0.5)
    ping_head(c, expr, t, **face)


# ============================================================ IMPERADOR
IMP_EXPR = {
    'sereno':        dict(eyes='narrow', brows=(0, 0), mouth='gentle', tilt=0),
    'testa_franzida': dict(eyes='narrow', brows=(7, -5), mouth='flat_down', tilt=0, frown=True),
    'pergunta':      dict(eyes='open', brows=(-6, 2), mouth='o', tilt=6),
    'sorriso':       dict(eyes='happy', brows=(-3, 4), mouth='smile', tilt=-3),
}


def imp_head(c, expr='sereno', t=0.0, mouth_kind=None, blink=0.0):
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
        eye(c, hx + s * 16, hy - 2, 'closed' if blink > 0.5 else e['eyes'], P['eye'], rx=5.5, ry=7)
        # pés de galinha
        for k in range(3):
            ink(c, [(hx + s * 25, hy - 4 + k * 3), (hx + s * 31, hy - 7 + k * 4)], 1.1, mul(P['skin'], 0.55), 0.5)
    # nariz romano
    nose = smooth([(hx - 2, hy - 8), (hx + 4, hy + 4), (hx + 6, hy + 16), (hx + 2, hy + 22), (hx - 5, hy + 21),
                   (hx - 4, hy + 6)], tension=0.45)
    layer(c, nose, mul(P['skin'], 0.95), depth=0.08, seed=63)
    ink(c, [(hx + 3, hy - 4), (hx + 7, hy + 8), (hx + 5, hy + 18)], 1.4, mul(P['skin'], 0.5), 0.55)
    # barba longa (triângulo) com fios
    beard = smooth([(hx - 15, hy + 30), (hx - 11, hy + 64), (hx - 5, hy + 112), (hx, hy + 132), (hx + 5, hy + 112),
                    (hx + 11, hy + 64), (hx + 15, hy + 30), (hx + 7, hy + 40), (hx, hy + 44), (hx - 7, hy + 40)], tension=0.4)
    layer(c, beard, P['beard'], depth=0.18, seed=64)
    for k in range(-2, 3):
        ink(c, [(hx + k * 3.5, hy + 48), (hx + k * 2.6, hy + 80), (hx + k * 1.0, hy + 116)], 1.1, (160, 154, 140), 0.55)
    mouth(c, hx, hy + 33, mouth_kind or e['mouth'], s=0.8)
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


def imperador(c, expr='sereno', pose='sleeves', t=0.0, face=None):
    face = face or {}
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
    imp_head(c, expr, t, **face)
    if pose == 'beard':
        layer(c, ell(18, -272, 9, 8), P['skin'], depth=0.1, seed=91)
        ink(c, [(14, -276), (22, -274)], 1.2, mul(P['skin'], 0.6), 0.5)


# ============================================================ PAI
PAI_EXPR = {
    'terno':  dict(eyes='half', brows=(-4, 3), mouth='gentle'),
    'apoio':  dict(eyes='happy', brows=(-3, 2), mouth='smile'),
}


def pai_head(c, expr='terno', t=0.0, mouth_kind=None, blink=0.0):
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
    mouth(c, hx, hy + 42, mouth_kind or e['mouth'], s=0.9)
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


def pai(c, expr='terno', pose='apoio', t=0.0, face=None, give=0.0):
    face = face or {}
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
    pai_head(c, expr, t, **face)


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


# ============================================================ MENINO RIVAL
RIVAL_EXPR = {
    'deboche':     dict(eyes='narrow', brows=(2, -4), mouth='smirk', tilt=-6),
    'orgulho':     dict(eyes='narrow', brows=(0, -5), mouth='smile', tilt=-8),
    'susto':       dict(eyes='open', brows=(-7, -6), mouth='o', tilt=4),
    'vergonha':    dict(eyes='half', brows=(-7, 4), mouth='flat_down', tilt=8),
}


def rival_head(c, expr='deboche', t=0.0, mouth_kind=None, blink=0.0):
    e = RIVAL_EXPR[expr]
    P = RIVAL
    hx, hy = 0, -318
    c.save(); c.rotate(e.get('tilt', 0), hx, hy + 50)
    # coque pontudo (triângulo)
    layer(c, tp([(hx + 4, hy - 46), (hx + 6, hy - 66), (hx + 3, hy - 86)], 20, 3), P['dark'], depth=0.12, seed=201)
    for s_ in (-1, 1):
        layer(c, ell(hx + s_ * 40, hy + 6, 7, 11), mul(P['skin'], 0.95), depth=0.1, seed=202 + s_)
    face = smooth([(hx, hy - 52), (hx + 32, hy - 40), (hx + 40, hy - 4), (hx + 34, hy + 34), (hx + 14, hy + 56), (hx, hy + 60),
                   (hx - 14, hy + 56), (hx - 34, hy + 34), (hx - 40, hy - 4), (hx - 32, hy - 40)], tension=0.42)
    layer(c, face, P['skin'], depth=0.2, seed=204)
    hair = smooth([(hx - 42, hy + 4), (hx - 42, hy - 30), (hx - 24, hy - 54), (hx, hy - 58), (hx + 24, hy - 54), (hx + 42, hy - 30),
                   (hx + 42, hy + 4), (hx + 34, hy - 18), (hx + 10, hy - 28), (hx - 18, hy - 26), (hx - 36, hy - 14)], tension=0.4)
    layer(c, hair, P['dark'], depth=0.15, seed=205)
    # faixa vermelha na testa + conta azul + ponta solta
    band = smooth([(hx - 44, hy - 30), (hx, hy - 40), (hx + 44, hy - 30), (hx + 44, hy - 20), (hx, hy - 30), (hx - 44, hy - 20)], tension=0.3)
    layer(c, band, P['red'], depth=0.08, seed=206)
    layer(c, tp([(hx + 40, hy - 26), (hx + 62, hy - 20), (hx + 76, hy - 4)], 9, 3), P['red'], depth=0.08, seed=207)
    layer(c, ell(hx - 44, hy - 22, 6, 8), P['bead'], depth=0.06, seed=208)
    for s_ in (-1, 1):
        if blink > 0.5:
            ink(c, [(hx + s_ * 22 - 8, hy + 4), (hx + s_ * 22 + 8, hy + 3)], 2.6, P['eye'], 0.95)
        else:
            almond_eye(c, hx + s_ * 17, hy + 4, e['eyes'], P['eye'], side=s_, rx=8.5, ry=4.6, mono=True)
        brow(c, hx + s_ * 17, hy - 12, e['brows'][0], e['brows'][1], s_, (50, 38, 32), w=3.4, L=16)
    flat(c, ell(hx + 1, hy + 22, 3.4, 2.6), mul(P['skin'], 0.82), 0.9)
    for s_ in (-1, 1):
        flat(c, ell(hx + s_ * 24, hy + 26, 9, 6), (226, 140, 120), 0.3, blur=4)
    mk = mouth_kind or e['mouth']
    if mk == 'smirk':
        ink(c, [(hx - 7, hy + 38), (hx + 3, hy + 39), (hx + 11, hy + 33)], 2.6, (70, 34, 30), 0.95, 2.0)
    else:
        mouth(c, hx + 1, hy + 37, mk, s=0.8)
    c.restore()


def big_vase(c, x, y, s=1.0, flowers=True, hidden=0.0, seed=0):
    """Vaso enorme creme com faixa de escamas vermelhas e flores cor-de-rosa."""
    P = RIVAL
    if flowers:
        for k, (fx, fy, r) in enumerate([(40, -215, 30), (88, -238, 34), (126, -200, 28), (64, -180, 26), (110, -168, 24), (20, -182, 22)]):
            ink(c, [(x, y - 150 * s), (x + fx * 0.5 * s, y - 180 * s), (x + fx * s, y + fy * s + 20 * s)], 4 * s, (70, 120, 70), 1, 3 * s)
        for k, (fx, fy, r) in enumerate([(40, -215, 30), (88, -238, 34), (126, -200, 28), (64, -180, 26), (110, -168, 24), (20, -182, 22)]):
            import scenes as _sc
            _sc.peony(c, x + fx * s, y + fy * s, r * s, P['petal'] if k % 2 else P['petal2'], 0.0, seed + k)
    body = smooth([(x - 26 * s, y - 165 * s), (x - 22 * s, y - 140 * s), (x - 70 * s, y - 100 * s), (x - 80 * s, y - 50 * s),
                   (x - 50 * s, y), (x + 50 * s, y), (x + 80 * s, y - 50 * s), (x + 70 * s, y - 100 * s), (x + 22 * s, y - 140 * s),
                   (x + 26 * s, y - 165 * s)], tension=0.4)
    layer(c, body, P['vase'], depth=0.3, seed=seed + 20)
    band = inter(body, rr(x - 100 * s, y - 102 * s, x + 100 * s, y - 76 * s, 1))
    layer(c, band, P['red'], depth=0.04, shadow=False, seed=seed + 21)
    c.save(); c.clipPath(band, doAntiAlias=True)
    for row in range(3):
        for k in range(-9, 10):
            cx = x + k * 10 * s + (5 * s if row % 2 else 0); cy = y - 98 * s + row * 9 * s
            c.drawPath(skia.Path().addCircle(cx, cy, 5 * s), skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=1.4 * s,
                       Color=C((240, 214, 170), 0.85)))
    c.restore()
    for k in range(-5, 6):
        ink(c, [(x + k * 12 * s - 5 * s, y - 50 * s), (x + k * 12 * s, y - 44 * s), (x + k * 12 * s + 5 * s, y - 50 * s)], 1.5 * s, P['red'], 0.8)
    layer(c, ell(x, y - 165 * s, 28 * s, 7 * s), mix(P['vase'], (255, 255, 255), 0.15), depth=0.05, seed=seed + 22)
    return body


def rival(c, expr='deboche', pose='carry', t=0.0, face=None, strain=0.0):
    """Anguloso e alongado (~3,8 cabeças): carrega um vaso que mal consegue sustentar."""
    face = face or {}
    P = RIVAL
    contact_shadow(c, 0, 0, 56, 8)
    for s_ in (-1, 1):
        layer(c, rr(s_ * 14 - 9, -130, s_ * 14 + 9, -14, 5), P['dark'], depth=0.12, seed=210 + s_)
        layer(c, smooth([(s_ * 14 - 14, -16), (s_ * 14 + 18 * s_, -16), (s_ * 14 + 14 * s_, -4), (s_ * 14 - 12, -2)], tension=0.3), P['dark'], depth=0.1, seed=212 + s_)
    layer(c, rr(-9, -270, 9, -252, 4), mul(P['skin'], 0.9), depth=0.05, seed=214)
    tunic = poly([(-36, -262), (36, -262), (48, -120), (-48, -120)])
    layer(c, tunic, P['tunic'], depth=0.25, seed=215)
    layer(c, rr(-50, -132, 50, -118, 3), P['red'], depth=0.05, seed=216)
    ink(c, [(-10, -262), (8, -200), (6, -132)], 2.2, mul(P['tunic'], 0.55), 0.6)
    sh = {-1: (-36, -252), 1: (36, -252)}
    lean = strain * 4
    if pose == 'carry':
        hands = {-1: (-58, -110 + lean), 1: (58, -110 + lean)}
    elif pose == 'hide':
        hands = {-1: (-30, -170), 1: (30, -170)}
    else:
        hands = {-1: (-50, -130), 1: (50, -130)}
    for s_ in (-1, 1):
        el, hd = ik(sh[s_], hands[s_], 52, 50, s_)
        layer(c, limb(sh[s_], el, 18, 16), P['tunic'], depth=0.2, seed=217 + s_)
    if pose == 'carry':
        big_vase(c, 0, -46 + lean * 0.5, 0.72, seed=7)
    for s_ in (-1, 1):
        el, hd = ik(sh[s_], hands[s_], 52, 50, s_)
        layer(c, limb(el, hd, 16, 14), P['tunic'], depth=0.2, seed=219 + s_)
        layer(c, limb((el[0] * 0.25 + hd[0] * 0.75, el[1] * 0.25 + hd[1] * 0.75), hd, 18, 18), P['red'], depth=0.1, seed=221 + s_)
        layer(c, ell(hd[0], hd[1], 10, 9), P['skin'], depth=0.12, seed=223 + s_)
    rival_head(c, expr, t, **face)
