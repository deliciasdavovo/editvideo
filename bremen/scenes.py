"""Cenários (diorama de papel e tecido). Mundo = tela 1080x1920 com margem; chão em y≈1240."""
from lib import *

M = 320  # margem do cache
G = 1240  # linha do chão


def rng_(seed):
    return np.random.default_rng(seed)


def sky(c, top, bot, x0=-M, y0=-M, x1=W + M, y1=G, stains=True, seed=1):
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.Shaders.Blend(skia.BlendMode.kMultiply,
        skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [C(top), C(bot)]), TEXSH['paper'])))
    if stains:  # manchas de aquarela
        r = rng_(seed)
        for i in range(14):
            x, y = r.uniform(x0, x1), r.uniform(y0, y1)
            rad = r.uniform(80, 260)
            col = shade(mix(top, bot, (y - y0) / (y1 - y0)), r.uniform(0.86, 1.12))
            c.drawCircle(x, y, rad, skia.Paint(AntiAlias=True, Color=C(col, 46), MaskFilter=blurmf(rad * 0.35)))


def stars(c, n, seed, y1=900, col=(250, 240, 210)):
    r = rng_(seed)
    for i in range(n):
        x, y = r.uniform(-M, W + M), r.uniform(-M, y1)
        s = r.uniform(2, 5)
        p = P([(x, y - s * 2), (x + s * 0.5, y - s * 0.5), (x + s * 2, y), (x + s * 0.5, y + s * 0.5), (x, y + s * 2),
               (x - s * 0.5, y + s * 0.5), (x - s * 2, y), (x - s * 0.5, y - s * 0.5)])
        fill(c, p, col, int(r.uniform(140, 230)))


def moon(c, x, y, r, col=(244, 232, 196)):
    c.drawCircle(x, y, r * 2.6, skia.Paint(AntiAlias=True, Color=C(col, 30), MaskFilter=blurmf(r)))
    for k, a in ((1.35, 40), (1.15, 70)):
        fill(c, circ(x, y, r * k), col, a)
    layer(c, jag(circ(x, y, r)), col, 0.2, rim=False)
    for dx, dy, rr_ in ((-0.3, -0.2, 0.18), (0.25, 0.3, 0.12), (0.1, -0.35, 0.09)):
        fill(c, circ(x + dx * r, y + dy * r, rr_ * r), shade(col, 0.9), 120)


def sun(c, x, y, r, col=(250, 214, 140)):
    c.drawCircle(x, y, r * 3, skia.Paint(AntiAlias=True, Color=C(col, 50), MaskFilter=blurmf(r * 1.2)))
    for k, a in ((1.5, 50), (1.22, 90)):
        fill(c, circ(x, y, r * k), col, a)
    layer(c, jag(circ(x, y, r)), col, 0.1, rim=False, shadow=False)


def cloud(c, x, y, s, col, seed=0, a=255):
    r = rng_(seed)
    blobs = [(0, 0, 70), (-70, 14, 50), (70, 12, 56), (-130, 30, 34), (126, 30, 36), (30, -30, 52)]
    p = union(*[circ(x + bx * s, y + by * s, br * s) for bx, by, br in blobs])
    p = union(p, rr(x - 150 * s, y + 10 * s, x + 150 * s, y + 52 * s, 20 * s))
    layer(c, jag(p, 1.6), col, 0.3, a=a, rim=True)
    layer(c, jag(xf(p, skia.Matrix.Scale(0.7, 0.55)) if False else oval(x - 20 * s, y + 20 * s, 90 * s, 22 * s)), shade(col, 0.92), 0.0, a=a,
          shadow=False, rim=False)


def hill_layer(c, y, amp, col, seed, x0=-M, x1=W + M, fields=None, depth=0.3, ybot=None, freq=1.0):
    r = rng_(seed)
    ph = r.uniform(0, 6)
    pts = []
    for x in np.linspace(x0, x1, 40):
        yy = y - amp * (0.6 * math.sin(x * 0.004 * freq + ph) + 0.4 * math.sin(x * 0.011 * freq + ph * 2))
        pts.append((x, yy))
    yb = ybot or (G + M)
    pts = pts + [(x1, yb), (x0, yb)]
    p = jag(P(pts), 1.5, 6)
    layer(c, p, col, depth, tex='fabric' if fields else 'paper')
    if fields:  # retalhos de campos costurados
        c.save()
        c.clipPath(p, skia.ClipOp.kIntersect, True)
        k = 0
        xs = x0
        while xs < x1:
            wv = r.uniform(140, 300)
            col2 = fields[k % len(fields)]
            quad = P([(xs, y - amp * 2), (xs + wv, y - amp * 2), (xs + wv * 1.25 - 40, yb), (xs - 40, yb)])
            layer(c, jag(quad, 1.2), col2, 0.0, shadow=False, tex='fabric', a=170)
            stitch_line(c, P([(xs + wv, y - amp * 2), (xs + wv * 1.25 - 40, yb)], False), shade(col2, 1.35), 200)
            # sulcos
            for j in range(4):
                fy = y + 20 + j * 34
                ink(c, P([(xs + 10, fy), (xs + wv - 10, fy + 8)], False), shade(col2, 0.8), 80, 2)
            xs += wv
            k += 1
        c.restore()
    return p


def tree_round(c, x, y, s, col, trunk=(100, 70, 50), seed=0, depth=0.4, a=255):
    layer(c, jag(tp([(x, y), (x + 4 * s, y - 80 * s), (x, y - 150 * s)], 26 * s, 14 * s)), trunk, depth * 0.7, a=a)
    r = rng_(seed)
    blobs = [circ(x + r.uniform(-50, 50) * s, y - 170 * s + r.uniform(-40, 40) * s, r.uniform(48, 72) * s) for _ in range(5)]
    crown = union(*blobs)
    layer(c, jag(crown, 1.5), col, depth, a=a, tex='fabric')
    # folhas bordadas
    for i in range(9):
        lx, ly = x + r.uniform(-70, 70) * s, y - 170 * s + r.uniform(-60, 50) * s
        leaf = rot_about(oval(lx, ly, 12 * s, 6 * s), r.uniform(0, 180), lx, ly)
        fill(c, leaf, shade(col, r.uniform(1.1, 1.3)), int(200 * a / 255))
        ink(c, P([(lx - 9 * s, ly), (lx + 9 * s, ly)], False), shade(col, 0.7), 120 * a / 255, 1.2)


def grass(c, y, x0, x1, col, seed, h=34, n=60, a=255):
    r = rng_(seed)
    for i in range(n):
        x = r.uniform(x0, x1)
        hh = r.uniform(0.5, 1) * h
        lean = r.uniform(-12, 12)
        fill(c, tp([(x, y), (x + lean * 0.5, y - hh * 0.5), (x + lean, y - hh)], 7, 1), shade(col, r.uniform(0.8, 1.15)), a)


def planks(c, rect, col, vertical=True, seed=0, w=70, depth=0.2, nails=True, a=255, gap=3):
    x0, y0, x1, y1 = rect
    r = rng_(seed)
    pos = x0 if vertical else y0
    end = x1 if vertical else y1
    i = 0
    while pos < end:
        ww = w * r.uniform(0.85, 1.15)
        if vertical:
            pr = jag(rr(pos + gap / 2, y0, min(pos + ww, x1) - gap / 2, y1, 3), 1.0)
        else:
            pr = jag(rr(x0, pos + gap / 2, x1, min(pos + ww, y1) - gap / 2, 3), 1.0)
        cc = shade(col, r.uniform(0.88, 1.1))
        layer(c, pr, cc, depth, a=a, rim=True)
        # veios
        b = pr.computeTightBounds()
        for j in range(3):
            if vertical:
                xx = b.left() + b.width() * r.uniform(0.2, 0.8)
                ink(c, smooth([(xx, b.top() + 10), (xx + r.uniform(-6, 6), b.centerY()), (xx + r.uniform(-4, 4), b.bottom() - 10)], False),
                    shade(cc, 0.7), 70 * a / 255, 1.4)
            else:
                yy = b.top() + b.height() * r.uniform(0.2, 0.8)
                ink(c, smooth([(b.left() + 10, yy), (b.centerX(), yy + r.uniform(-5, 5)), (b.right() - 10, yy)], False), shade(cc, 0.7),
                    70 * a / 255, 1.4)
        if nails:
            if vertical:
                for ny in (y0 + 30, y1 - 30):
                    fill(c, circ(b.centerX(), ny, 4), (60, 50, 44), 200 * a / 255)
            else:
                for nx in (x0 + 30, x1 - 30):
                    fill(c, circ(nx, b.centerY(), 4), (60, 50, 44), 200 * a / 255)
        pos += ww
        i += 1


def fence(c, x0, x1, y, col=(132, 98, 66), h=170, seed=0, depth=0.35):
    r = rng_(seed)
    for yy in (y - h * 0.75, y - h * 0.35):
        layer(c, jag(P([(x0, yy - 12), (x1, yy - 16), (x1, yy + 12), (x0, yy + 14)]), 1.2), shade(col, 0.95), depth)
    x = x0
    while x < x1:
        layer(c, jag(P([(x - 14, y + 10), (x + 14, y + 10), (x + 13, y - h), (x, y - h - 18), (x - 13, y - h)]), 1.2),
              shade(col, r.uniform(0.9, 1.08)), depth + 0.1)
        x += r.uniform(150, 190)


def stone_wall(c, x0, x1, y, h=150, col=(150, 140, 126), seed=0):
    r = rng_(seed)
    rows = 3
    for j in range(rows):
        yy = y - (j + 1) * h / rows
        x = x0 - r.uniform(0, 40)
        while x < x1:
            ww = r.uniform(70, 120)
            p = jag(smooth([(x + 4, yy + 4), (x + ww - 4, yy + 6), (x + ww, yy + h / rows - 2), (x + ww * 0.5, yy + h / rows + 2),
                            (x, yy + h / rows - 4)]), 1.5)
            layer(c, p, shade(col, r.uniform(0.85, 1.12)), 0.3)
            x += ww
    # musgo bordado
    for i in range(30):
        xx = r.uniform(x0, x1)
        fill(c, circ(xx, y - h + r.uniform(-4, 10), r.uniform(5, 11)), (110, 128, 70), 150)


def window_frame(c, x0, y0, x1, y1, col=(110, 76, 50), depth=0.4):
    t = 26
    fr = diff(rr(x0 - t, y0 - t, x1 + t, y1 + t, 6), rr(x0, y0, x1, y1, 2))
    layer(c, jag(fr, 1.2), col, depth)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    layer(c, jag(rr(mx - 8, y0, mx + 8, y1, 2)), col, depth * 0.8)
    layer(c, jag(rr(x0, my - 8, x1, my + 8, 2)), col, depth * 0.8)
    layer(c, jag(rr(x0 - t - 16, y1 + t - 6, x1 + t + 16, y1 + t + 20, 4)), shade(col, 1.1), depth)


def god_rays(c, x, y, ang, spread, length, col, a=40):
    for k in range(5):
        a0 = ang + (k - 2) * spread / 5
        p = P([(x, y), (x + math.cos(math.radians(a0 - 3)) * length, y + math.sin(math.radians(a0 - 3)) * length),
               (x + math.cos(math.radians(a0 + 3)) * length, y + math.sin(math.radians(a0 + 3)) * length)])
        c.drawPath(p, skia.Paint(AntiAlias=True, Color=C(col, a), MaskFilter=blurmf(30), BlendMode=skia.BlendMode.kScreen))


# =================================================================== cenários (desenho completo, cacheado)
def bg_barn(c, layer_='far'):
    set_light(-0.85, -0.5)
    if layer_ == 'far':
        sky(c, (176, 186, 190), (214, 210, 198), seed=3)
        sun(c, 120, 330, 60, (238, 228, 200))
        cloud(c, 820, 300, 0.9, (226, 226, 222), 1)
        cloud(c, 300, 480, 0.6, (216, 218, 216), 2)
        hill_layer(c, 980, 60, (150, 160, 150), 5, depth=0.2)
        hill_layer(c, 1080, 50, (138, 146, 120), 6, fields=[(150, 152, 112), (128, 140, 104), (160, 150, 110)], depth=0.25)
    else:
        # chão do pátio
        layer(c, jag(P([(-M, G - 20), (W + M, G - 30), (W + M, G + M + 700), (-M, G + M + 700)]), 2), (156, 132, 100), 0.2, tex='paper')
        r = rng_(9)
        for i in range(80):  # palha
            x, y = r.uniform(-M, W + M), r.uniform(G, G + 600)
            ang = r.uniform(-0.4, 0.4)
            ink(c, P([(x, y), (x + 30 * math.cos(ang), y + 30 * math.sin(ang))], False), (206, 176, 104), 170, 2.4)
        # celeiro
        bx0, bx1, by0 = -180, 700, 360
        layer(c, jag(P([(bx0 - 40, by0 + 120), ((bx0 + bx1) / 2, by0 - 120), (bx1 + 40, by0 + 120)]), 1.5), (96, 72, 64), 0.5)
        planks(c, (bx0, by0 + 100, bx1, G), (150, 96, 80), True, 4, 64)
        # porta (vão escuro)
        dx0, dx1, dy0 = 160, 560, 700
        layer(c, jag(rr(dx0, dy0, dx1, G, 4)), (50, 38, 34), 0.0, shadow=False)
        for i in range(10):
            fill(c, oval(dx0 + 60 + i * 30, G - 30 - (i % 3) * 18, 50, 24), (170, 140, 80), 120)
        layer(c, jag(P([(dx0 - 30, dy0 - 30), (dx1 + 30, dy0 - 30), (dx1 + 30, dy0), (dx0 - 30, dy0)])), (110, 74, 56), 0.4)
        # fardos de feno
        for hx, hy in ((640, G + 10), (760, G - 30)):
            p = jag(rr(hx, hy - 90, hx + 150, hy, 14))
            layer(c, p, (206, 170, 96), 0.4, tex='fabric')
            for j in range(5):
                ink(c, P([(hx + 10, hy - 80 + j * 16), (hx + 140, hy - 76 + j * 16)], False), (170, 130, 60), 150, 2)
            stitch_line(c, P([(hx + 50, hy - 90), (hx + 50, hy)], False), (120, 80, 40), 255)
            stitch_line(c, P([(hx + 100, hy - 90), (hx + 100, hy)], False), (120, 80, 40), 255)
        # forcado encostado
        ink(c, P([(720, G - 330), (690, G - 40)], False), (110, 80, 54), 255, 9)
        for k in (-14, 0, 14):
            ink(c, smooth([(722 + k, G - 330), (726 + k * 1.2, G - 380), (730 + k * 1.3, G - 410)], False), (120, 120, 120), 255, 4)
        fence(c, 820, W + M, G + 10, (128, 104, 82), 150, 3)


def door_panels(c, close, col=(140, 90, 74)):
    """portas do celeiro (0 aberta .. 1 fechada)"""
    dx0, dx1, dy0 = 160, 560, 700
    w = (dx1 - dx0) / 2 * close
    for side in (0, 1):
        if w < 2:
            continue
        x0 = dx0 if side == 0 else dx1 - w
        planks(c, (x0, dy0, x0 + w, G), col, True, 11 + side, 44, depth=0.5, nails=False)
        ink(c, P([(x0 + 6, dy0 + 20), (x0 + w - 6, G - 20)], False), shade(col, 0.6), 180, 8)


def bg_road(c, layer_='far', variant='day'):
    set_light(-0.6, -0.75)
    if variant == 'sunrise':
        top, bot, sunc, sp = (214, 196, 170), (240, 214, 170), (252, 222, 160), (180, 760)
    elif variant == 'sunset':
        top, bot, sunc, sp = (120, 84, 92), (240, 150, 84), (252, 196, 110), (300, 1010)
    else:
        top, bot, sunc, sp = (196, 200, 196), (238, 216, 170), (250, 226, 160), (180, 380)
    if layer_ == 'far':
        sky(c, top, bot, seed=7)
        sun(c, sp[0], sp[1], 70 if variant != 'sunset' else 110, sunc)
        for i, (x, y, s) in enumerate(((760, 260, 0.9), (260, 520, 0.6), (980, 620, 0.5))):
            cloud(c, x, y, s, mix((244, 236, 222), bot, 0.3) if variant != 'sunset' else (232, 150, 120), i + 3)
        hill_layer(c, 940, 70, mix((150, 156, 160), bot, 0.25), 11, depth=0.15)
        hill_layer(c, 1030, 55, (160, 150, 104), 12,
                   fields=[(176, 150, 86), (150, 140, 84), (190, 120, 70), (140, 128, 70)] if variant != 'sunset' else
                   [(150, 92, 70), (130, 84, 70), (170, 104, 70)], depth=0.25)
        for i, x in enumerate((60, 880, 1060, -120)):
            tree_round(c, x, 1090 + (i % 2) * 20, 0.8, (196, 100, 50) if i % 2 else (210, 150, 60), seed=i + 20, depth=0.25)
    else:
        # estrada de terra
        layer(c, jag(P([(-M, G - 70), (W + M, G - 90), (W + M, G + M + 700), (-M, G + M + 700)]), 2), (176, 150, 112), 0.15)
        layer(c, jag(P([(-M, G - 30), (W + M, G - 50), (W + M, G + 120), (-M, G + 140)]), 2), (200, 172, 128), 0.1)
        r = rng_(13)
        for i in range(40):
            x, y = r.uniform(-M, W + M), r.uniform(G - 30, G + 130)
            fill(c, oval(x, y, r.uniform(3, 7), r.uniform(2, 4)), (150, 126, 96), 160)
        grass(c, G - 60, -M, W + M, (130, 128, 70), 3, 40, 120)
        grass(c, G + 160, -M, W + M, (120, 116, 64), 4, 60, 160)
        # folhas de outono no chão
        for i in range(36):
            x, y = r.uniform(-M, W + M), r.uniform(G + 150, G + 600)
            lf = rot_about(oval(x, y, 14, 7), r.uniform(0, 180), x, y)
            fill(c, lf, [(196, 100, 50), (214, 150, 60), (160, 70, 46)][i % 3], 220)


def bg_night_ext(c, layer_='far'):
    set_light(0.3, -0.6)
    if layer_ == 'far':
        sky(c, (16, 26, 46), (38, 56, 84), seed=21)
        stars(c, 90, 4)
        moon(c, 860, 260, 70)
        for i, (x, s, col) in enumerate(((-60, 1.3, (30, 44, 70)), (980, 1.4, (28, 40, 64)), (160, 1.0, (40, 56, 86)))):
            tree_round(c, x, 1140, s, col, trunk=(30, 36, 50), seed=40 + i, depth=0.3)
    else:
        layer(c, jag(P([(-M, G - 40), (W + M, G - 50), (W + M, G + M + 700), (-M, G + M + 700)]), 2), (34, 46, 54), 0.2)
        grass(c, G - 40, -M, W + M, (40, 60, 64), 5, 40, 120)
        # parede da casa
        layer(c, jag(P([(120, 150), (W + M, 150), (W + M, G), (120, G)]), 1.2), (90, 76, 70), 0.6)
        planks(c, (120, 150, W + M, G - 220), (96, 80, 72), False, 9, 80, depth=0.3)
        # base de pedra
        stone_wall(c, 120, W + M, G, 220, (104, 100, 104), 9)
        # janela (vidro desenhado ao vivo)
        window_frame(c, 360, 420, 900, 900, (86, 62, 46))


WIN_EXT = (360, 420, 900, 900)


def bg_forest(c, layer_='far'):
    set_light(0.4, -0.7)
    if layer_ == 'far':
        sky(c, (12, 20, 38), (30, 46, 72), seed=31)
        stars(c, 60, 8, 600)
        moon(c, 240, 300, 56)
        r = rng_(5)
        for row, (col, wv, yb) in enumerate((((32, 46, 76), 50, 1180), ((24, 36, 62), 70, 1220))):
            x = -M + row * 60
            while x < W + M:
                ww = wv * r.uniform(0.7, 1.3)
                layer(c, jag(P([(x, yb), (x + ww * 0.2, -M), (x + ww * 0.8, -M), (x + ww, yb)]), 1.4), shade(col, r.uniform(0.9, 1.1)),
                      0.2 + row * 0.1, tex='fabric')
                x += ww + r.uniform(60, 180)
    else:
        layer(c, jag(P([(-M, G - 40), (W + M, G - 60), (W + M, G + M + 700), (-M, G + M + 700)]), 2), (24, 34, 44), 0.2)
        grass(c, G - 50, -M, W + M, (34, 54, 60), 7, 50, 140)
        r = rng_(8)
        for x in (-160, 940, 1180):
            layer(c, jag(P([(x, G + 80), (x + 30, -M), (x + 150, -M), (x + 190, G + 80)]), 1.6), (18, 26, 40), 0.6, tex='fabric')
            for j in range(5):
                yy = r.uniform(100, G)
                ink(c, smooth([(x + 40, yy), (x + 90, yy + 20), (x + 150, yy - 10)], False), (34, 46, 64), 160, 2)
        for x in range(-M, W + M, 140):
            layer(c, jag(union(circ(x, G + 60, 70), circ(x + 60, G + 40, 60), circ(x + 120, G + 70, 66))), (20, 36, 40), 0.4,
                  tex='fabric')


def tiny_house(c, x, y, s, glow=1.0):
    layer(c, jag(rr(x - 70 * s, y - 100 * s, x + 70 * s, y, 4)), (60, 52, 56), 0.3)
    layer(c, jag(P([(x - 90 * s, y - 96 * s), (x, y - 170 * s), (x + 90 * s, y - 96 * s)])), (44, 40, 52), 0.3)
    wcol = (255, 190, 90)
    c.drawCircle(x, y - 55 * s, 90 * s, skia.Paint(AntiAlias=True, Color=C(wcol, int(70 * glow)), MaskFilter=blurmf(40 * s)))
    fill(c, rr(x - 26 * s, y - 76 * s, x + 26 * s, y - 34 * s, 3), wcol, int(255 * glow))
    ink(c, P([(x, y - 76 * s), (x, y - 34 * s)], False), (80, 50, 30), 255, 3 * s)
    ink(c, P([(x - 26 * s, y - 55 * s), (x + 26 * s, y - 55 * s)], False), (80, 50, 30), 255, 3 * s)


def bg_interior(c, layer_='far', variant='lit'):
    """interior: parede com vigas, janela ao fundo à esquerda, lareira à direita"""
    set_light(0.85, -0.3)
    dark = variant == 'dark'
    base = (176, 132, 96) if not dark else (60, 66, 84)
    if layer_ == 'far':
        c.drawRect(skia.Rect(-M, -M, W + M, G + M + 700), skia.Paint(Color=C(base)))
        sky(c, base, shade(base, 0.8), -M, -M, W + M, G, seed=51)
        # vigas
        for x in (-40, 520, 1080):
            layer(c, jag(rr(x, -M, x + 70, G, 4)), (100, 70, 48) if not dark else (40, 44, 58), 0.4)
            for j in range(5):
                ink(c, P([(x + 20 + j * 8, -M), (x + 24 + j * 8, G)], False), (70, 48, 34) if not dark else (30, 34, 46), 60, 1.4)
        layer(c, jag(rr(-M, 160, W + M, 220, 4)), (100, 70, 48) if not dark else (40, 44, 58), 0.4)
        # janela (vidro ao vivo)
        window_frame(c, *WIN_INT, (96, 66, 44) if not dark else (40, 40, 52))
        # lareira
        fx0, fx1 = 760, 1180
        layer(c, jag(rr(fx0, 520, fx1, G, 8)), (130, 120, 116) if not dark else (60, 60, 72), 0.5)
        stone_wall(c, fx0, fx1, G, 720, (140, 128, 118) if not dark else (66, 66, 80), 3)
        layer(c, jag(rr(fx0 + 80, 860, fx1 - 60, G, 60)), (30, 20, 20), 0.0, shadow=False)
        layer(c, jag(rr(fx0 - 30, 490, fx1 + 30, 540, 6)), (110, 76, 50) if not dark else (44, 44, 56), 0.5)
        # prateleira com potes
        layer(c, jag(rr(80, 640, 440, 662, 4)), (110, 76, 50) if not dark else (44, 44, 56), 0.4)
        for i, (px, pc) in enumerate(((120, (170, 110, 70)), (200, (90, 110, 130)), (290, (190, 160, 90)), (380, (140, 80, 70)))):
            layer(c, jag(rr(px - 26, 572 + i % 2 * 14, px + 26, 640, 12)), pc if not dark else shade(pc, 0.4), 0.3)
    else:
        # chão de tábuas
        planks(c, (-M, G - 20, W + M, G + M + 700), (140, 98, 64) if not dark else (50, 52, 66), False, 33, 90, depth=0.15)
        if variant == 'cozy':
            p = jag(oval(500, G + 260, 520, 170), 1.6)
            layer(c, p, (150, 52, 50), 0.2, tex='fabric')
            stitch_line(c, inset(p, 22), (226, 180, 90))
            stitch_line(c, inset(p, 60), (226, 180, 90))
            plaid(c, inset(p, 80), (150, 52, 50), (196, 140, 60), (110, 36, 40), 34, 120)


WIN_INT = (250, 330, 650, 760)


def fire(c, t, x, y, s=1.0, a=255):
    """fogo de papel tremulando (ao vivo)"""
    cols = [(240, 110, 40), (250, 160, 60), (255, 220, 120)]
    for k, col in enumerate(cols):
        sc = (1 - k * 0.28) * s
        pts = []
        n = 7
        for i in range(n):
            ang = math.pi + i / (n - 1) * math.pi
            fl = 1 + 0.25 * math.sin(t * 9 + i * 1.7 + k)
            rr_ = (90 if i % 2 else 60) * sc * fl
            pts.append((x + math.cos(ang) * 90 * sc, y + math.sin(ang) * rr_ * 1.6))
        pts = [(x - 95 * sc, y)] + pts + [(x + 95 * sc, y)]
        layer(c, jag(smooth(pts), 1.2, seed=k), col, 0.0, a=a, shadow=False, rim=False, grad=False)
    for i in range(3):
        layer(c, jag(rr(x - 100 * s + i * 50 * s, y - 10, x - 20 * s + i * 50 * s, y + 18, 8)), (90, 56, 40), 0.2, a=a)


def table(c, x0, x1, y, food=True, eaten=0.0, cloth=(214, 196, 160)):
    layer(c, jag(rr(x0, y, x1, y + 40, 6)), (126, 86, 56), 0.5)
    for lx in (x0 + 30, x1 - 60):
        layer(c, jag(rr(lx, y + 30, lx + 30, y + 260, 6)), (110, 74, 50), 0.4)
    cl = jag(P([(x0 + 40, y - 4), (x1 - 40, y - 4), (x1 - 60, y + 70), (x0 + 60, y + 70)]), 1.4)
    layer(c, cl, cloth, 0.2, tex='fabric', stitch=True, stitch_col=(160, 60, 50))
    if food:
        # pão, queijo, frutas, jarra
        mx = (x0 + x1) / 2
        items = [
            ('bread', mx - 150, y - 6), ('cheese', mx + 30, y - 6), ('fruit', mx + 150, y - 6), ('jug', mx - 260, y - 6), ('fruit2', mx - 40, y - 6)]
        for kind, ix, iy in items:
            if kind == 'bread':
                p = jag(smooth([(ix - 70, iy), (ix - 60, iy - 40), (ix, iy - 56), (ix + 60, iy - 40), (ix + 70, iy)]))
                layer(c, p, (200, 140, 70), 0.3, tex='fabric')
                for k in range(3):
                    ink(c, smooth([(ix - 30 + k * 26, iy - 46), (ix - 20 + k * 26, iy - 30)], False), (150, 96, 50), 200, 3)
            elif kind == 'cheese':
                p = jag(P([(ix - 50, iy), (ix + 50, iy), (ix + 50, iy - 40), (ix - 30, iy - 56)]))
                layer(c, p, (236, 196, 90), 0.3)
                for hx, hy in ((ix - 10, iy - 24), (ix + 22, iy - 14)):
                    fill(c, circ(hx, hy, 7), (200, 160, 70), 255)
            elif kind in ('fruit', 'fruit2'):
                for k, (fx, fc) in enumerate(((-26, (190, 60, 50)), (6, (210, 150, 50)), (34, (140, 60, 90)))):
                    layer(c, jag(circ(ix + fx, iy - 22, 22)), fc, 0.3, tex='fabric')
            elif kind == 'jug':
                p = jag(smooth([(ix - 34, iy), (ix - 40, iy - 60), (ix - 24, iy - 100), (ix + 24, iy - 100), (ix + 40, iy - 60), (ix + 34, iy)]))
                layer(c, p, (110, 130, 150), 0.3)
                stitch_line(c, P([(ix - 36, iy - 50), (ix + 36, iy - 50)], False), (230, 220, 200))


def chair(c, x, y, s=1.0, ang=0.0, col=(120, 82, 52)):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    layer(c, jag(rr(-60, -150, 60, -126, 4)), col, 0.4)
    layer(c, jag(rr(-60, -330, -40, -130, 4)), col, 0.4)
    layer(c, jag(rr(40, -330, 60, -130, 4)), col, 0.4)
    layer(c, jag(rr(-60, -330, 60, -300, 4)), col, 0.4)
    for lx in (-56, 40):
        layer(c, jag(rr(lx, -130, lx + 16, 0, 4)), shade(col, 0.9), 0.3)
    c.restore()
