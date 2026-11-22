"""Cenários e elementos de O Pote Vazio + legenda, grade e acabamento."""
import math, random
import numpy as np
import skia
import paperlib as pl
from paperlib import layer, flat, ink, smooth, poly, ell, circ, rr, union, inter, tp, C, mix, mul, STYLE
import characters as ch

W, H = 1080, 1920


def set_scale(s):
    pl.SCALE[0] = s


# ------------------------------------------------------------ flores
GLOSSY = [(226, 72, 110), (244, 150, 40), (236, 200, 60), (196, 70, 190), (240, 96, 70), (120, 90, 220), (250, 120, 160)]


def gray_of(col, g):
    y = 0.3 * col[0] + 0.59 * col[1] + 0.11 * col[2]
    return mix(col, (y * 0.9 + 20, y * 0.9 + 20, y * 0.92 + 22), g)


def peony(c, x, y, r, col, gray=0.0, seed=0):
    col = gray_of(col, gray)
    rnd = random.Random(seed)
    for ring, (k, rr_) in enumerate([(9, 1.0), (7, 0.72), (5, 0.45)]):
        cc = mix(col, (255, 255, 255), 0.08 * ring) if gray < 0.5 else col
        for i in range(k):
            a = i / k * 2 * math.pi + ring * 0.4 + rnd.uniform(-0.15, 0.15)
            px, py = x + math.cos(a) * r * rr_ * 0.55, y + math.sin(a) * r * rr_ * 0.45
            petal = ell(px, py, r * 0.42 * rr_ + 2, r * 0.32 * rr_ + 2)
            petal = pl.xform(petal, rot=math.degrees(a), cx=px, cy=py)
            layer(c, petal, cc, depth=0.08, seed=seed + i + ring * 10, lit_mix=0.25 * (1 - gray))
    flat(c, circ(x, y, r * 0.14), gray_of((250, 220, 120), gray))
    if gray < 0.5:  # brilho de papel lustroso
        flat(c, ell(x - r * 0.25, y - r * 0.2, r * 0.3, r * 0.08), (255, 255, 255), 0.35 * (1 - gray))


def mum(c, x, y, r, col, gray=0.0, seed=0):
    col = gray_of(col, gray)
    n = 22
    for i in range(n):
        a = i / n * 2 * math.pi
        pts = [(x, y), (x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.5), (x + math.cos(a) * r, y + math.sin(a) * r * 0.85)]
        c.drawPath(tp(pts, r * 0.16, r * 0.06), skia.Paint(AntiAlias=True, Color=C(mul(col, 0.85 + 0.15 * (i % 2)))))
    layer(c, circ(x, y, r * 0.42), mix(col, (255, 255, 255), 0.15), depth=0.05, seed=seed)
    flat(c, circ(x, y, r * 0.15), gray_of((230, 180, 70), gray))


def leaf(c, x, y, ang, L, gray=0.0, seed=0):
    col = gray_of((70, 130, 70), gray)
    a = math.radians(ang)
    pts = [(x, y), (x + math.cos(a) * L * 0.5 - math.sin(a) * L * 0.08, y + math.sin(a) * L * 0.5 + math.cos(a) * L * 0.08),
           (x + math.cos(a) * L, y + math.sin(a) * L)]
    layer(c, tp(pts, L * 0.32, 1), col, depth=0.06, seed=seed, rim=False)
    ink(c, [pts[0], pts[2]], 1.0, mul(col, 0.5), 0.5)


def flower_pot(c, x, y, s, seed=0, gray=0.0, big=1.0, lean=0.0):
    """Vaso de outra criança: flor enorme de papel lustroso."""
    rnd = random.Random(seed)
    col = GLOSSY[seed % len(GLOSSY)]
    potc = gray_of(rnd.choice([(70, 110, 150), (60, 120, 110), (150, 70, 60), (200, 170, 90)]), gray)
    h = 60 * s
    stem_top = y - h - 70 * s * big
    for k in range(3):
        sx = x + (k - 1) * 14 * s
        ink(c, [(sx, y - h), (sx + rnd.uniform(-6, 6) * s + lean * 0.4 * s, (y - h + stem_top) / 2), (sx + (k - 1) * 22 * s + lean * s, stem_top + 10 * s)],
            4 * s, gray_of((60, 110, 60), gray), 1.0, 3 * s)
    for k in range(4):
        leaf(c, x + (k - 1.5) * 12 * s, y - h - 20 * s * (k % 2 + 1), [200, -20, 230, -40][k], 46 * s, gray, seed + k)
    for k in range(3):
        fx, fy = x + (k - 1) * 26 * s * big + lean * s, stem_top + (12 if k != 1 else -6) * s
        rr_ = (34 if k == 1 else 26) * s * big
        (peony if (seed + k) % 2 == 0 else mum)(c, fx, fy, rr_, GLOSSY[(seed + k * 3) % len(GLOSSY)], gray, seed + k)
    body = smooth([(x - 32 * s, y - h), (x - 26 * s, y), (x + 26 * s, y), (x + 32 * s, y - h)], tension=0.3)
    layer(c, body, potc, depth=0.2, seed=seed + 40)
    layer(c, ell(x, y - h, 36 * s, 7 * s), mix(potc, (255, 255, 255), 0.15), depth=0.08, seed=seed + 41)
    if gray < 0.5:
        flat(c, rr(x - 24 * s, y - h * 0.8, x - 18 * s, y - h * 0.2, 3 * s), (255, 255, 255), 0.3)


def child(c, x, y, s, seed=0, gray=0.0, part='all', look_down=False):
    """Criança da fila (simples, para ficar de fundo). part: body | head | all"""
    rnd = random.Random(seed + 99)
    tunic = gray_of(rnd.choice([(170, 80, 70), (90, 100, 150), (200, 150, 70), (120, 90, 140), (80, 130, 100)]), gray * 0.6)
    skin = gray_of(rnd.choice([(232, 192, 156), (220, 176, 140)]), gray * 0.6)
    if part in ('body', 'all'):
        layer(c, rr(x - 30 * s, y - 150 * s, x + 30 * s, y - 40 * s, 14 * s), tunic, depth=0.15, seed=seed)
        for k in (-1, 1):
            layer(c, rr(x + k * 14 * s - 9 * s, y - 50 * s, x + k * 14 * s + 9 * s, y, 6 * s), gray_of((200, 190, 170), gray * 0.6), depth=0.1, seed=seed + k)
    if part == 'back':
        layer(c, rr(x - 30 * s, y - 150 * s, x + 30 * s, y - 40 * s, 14 * s), tunic, depth=0.15, seed=seed)
        for k in (-1, 1):
            layer(c, rr(x + k * 14 * s - 9 * s, y - 50 * s, x + k * 14 * s + 9 * s, y, 6 * s), gray_of((200, 190, 170), gray * 0.6), depth=0.1, seed=seed + k)
        for k in (-1, 1):
            layer(c, ell(x + k * 36 * s, y - 182 * s, 6 * s, 8 * s), skin, depth=0.1, seed=seed + 5 + k)
        layer(c, circ(x, y - 184 * s, 38 * s), (36, 30, 38), depth=0.15, seed=seed + 4)
        ink(c, [(x - 10 * s, y - 214 * s), (x - 4 * s, y - 190 * s), (x - 8 * s, y - 160 * s)], 2 * s, (74, 70, 88), 0.6)
        return
    if part in ('head', 'all'):
        hy = y - 182 * s + (6 * s if look_down else 0)
        layer(c, circ(x, hy, 36 * s), skin, depth=0.15, seed=seed + 3)
        hair = inter(circ(x, hy - 4 * s, 39 * s), rr(x - 50 * s, hy - 58 * s, x + 50 * s, hy - 4 * s + rnd.uniform(-8, 4) * s, 1))
        layer(c, hair, (36, 30, 38), depth=0.1, seed=seed + 4)
        if look_down:
            for k in (-1, 1):
                ink(c, [(x + k * 13 * s - 4 * s, hy + 8 * s), (x + k * 13 * s, hy + 10 * s), (x + k * 13 * s + 4 * s, hy + 8 * s)], 2.2 * s, (40, 28, 28), 0.9)
            ink(c, [(x - 6 * s, hy + 24 * s), (x, hy + 22 * s), (x + 6 * s, hy + 24 * s)], 2.2 * s, (80, 40, 40), 0.9)
        else:
            for k in (-1, 1):
                flat(c, ell(x + k * 13 * s, hy + 6 * s, 2.6 * s, 3.4 * s), (40, 28, 28))
            ink(c, [(x - 7 * s, hy + 20 * s), (x, hy + 24 * s), (x + 7 * s, hy + 20 * s)], 2.2 * s, (80, 40, 40), 0.9)
        for k in (-1, 1):
            flat(c, ell(x + k * 20 * s, hy + 14 * s, 6 * s, 4 * s), (230, 120, 110), 0.3)


# ------------------------------------------------------------ palácio
def palace_bg(c, warm=1.0, gray=0.0):
    wall = gray_of((176, 128, 70), gray)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, 900)], [C(mul(wall, 0.65)), C(wall)])))
    c.drawPaint(skia.Paint(Shader=pl.fiber_shader(1.0), BlendMode=skia.BlendMode.kMultiply, Alphaf=0.6))
    # treliça da parede (janelas de papel)
    for wx in (90, 400, 710):
        layer(c, rr(wx, 180, wx + 280, 620, 10), gray_of((240, 214, 160), gray), depth=0.2, seed=wx)
        for k in range(1, 7):
            c.drawLine(wx + k * 40, 186, wx + k * 40, 614, skia.Paint(AntiAlias=True, Color=C(gray_of((120, 70, 40), gray), 0.7), StrokeWidth=4))
        for k in range(1, 11):
            c.drawLine(wx + 6, 180 + k * 40, wx + 274, 180 + k * 40, skia.Paint(AntiAlias=True, Color=C(gray_of((120, 70, 40), gray), 0.7), StrokeWidth=4))
    # viga e telhado interno
    layer(c, rr(-40, 110, W + 40, 170, 6), gray_of((150, 44, 40), gray), depth=0.4, seed=5)
    for k in range(12):
        flat(c, circ(40 + k * 92, 140, 8), gray_of((220, 180, 90), gray), 0.9)
    # chão em perspectiva (pedra kraft)
    floor = poly([(-200, 700), (W + 200, 700), (W + 600, H), (-600, H)])
    layer(c, floor, gray_of((196, 168, 128), gray), depth=0.05, shadow=False, rim=False, seed=6)
    for k in range(-8, 9):
        c.drawLine(W / 2 + k * 60, 700, W / 2 + k * 360, H, skia.Paint(AntiAlias=True, Color=C((120, 90, 60), 0.25), StrokeWidth=2))
    yy = 700
    for k in range(14):
        yy += 18 + k * 12
        c.drawLine(-200, yy, W + 200, yy, skia.Paint(AntiAlias=True, Color=C((120, 90, 60), 0.22), StrokeWidth=2))
    # tapete vermelho central
    rug = poly([(440, 700), (600, 700), (900, H), (140, H)])
    layer(c, rug, gray_of((150, 40, 42), gray), depth=0.03, shadow=False, rim=False, seed=7)
    for side in (-1, 1):
        ink(c, [(520 + side * 70, 700), (520 + side * 360, H)], 6, gray_of((214, 170, 80), gray), 0.9, 6)


def pillar(c, x, y0, y1, w, gray=0.0, seed=0):
    layer(c, rr(x - w / 2, y0, x + w / 2, y1, w * 0.2), gray_of((172, 46, 42), gray), depth=0.5, seed=seed)
    layer(c, rr(x - w / 2 - 8, y1 - 26, x + w / 2 + 8, y1, 4), gray_of((70, 50, 40), gray), depth=0.2, seed=seed + 1)
    layer(c, rr(x - w / 2 - 6, y0, x + w / 2 + 6, y0 + 30, 4), gray_of((210, 170, 80), gray), depth=0.2, seed=seed + 2)
    ink(c, [(x - w * 0.18, y0 + 40), (x - w * 0.2, y1 - 40)], 3, (255, 210, 180), 0.25)


def beam(c, x, y_top, y_bot, w_top, w_bot, a=0.35, col=(255, 226, 160)):
    p = poly([(x - w_top / 2, y_top), (x + w_top / 2, y_top), (x + w_bot / 2, y_bot), (x - w_bot / 2, y_bot)])
    c.drawPath(p, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y_top), skia.Point(0, y_bot)], [C(col, a), C(col, a * 0.35)]),
        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 18), BlendMode=skia.BlendMode.kScreen))


def dust(c, x0, y0, x1, y1, n=60, t=0.0, seed=1, a=0.7):
    rnd = random.Random(seed)
    for i in range(n):
        px = rnd.uniform(x0, x1) + math.sin(t * 0.6 + i) * 8
        py = (rnd.uniform(y0, y1) - t * 12 * rnd.uniform(0.3, 1)) % (y1 - y0) + y0
        r = rnd.uniform(1, 3.4)
        flat(c, circ(px, py, r), (255, 240, 200), a * rnd.uniform(0.3, 1), blur=r * 0.8)


# ------------------------------------------------------------ casa do Ping
def house_bg(c, outside_col=(150, 196, 120), gray=0.0):
    wall = gray_of((200, 170, 128), gray)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=C(wall)))
    c.drawPaint(skia.Paint(Shader=pl.fiber_shader(1.0), BlendMode=skia.BlendMode.kMultiply, Alphaf=0.7))
    # manchas de aquarela
    rnd = random.Random(3)
    for i in range(14):
        flat(c, ell(rnd.uniform(0, W), rnd.uniform(0, 1300), rnd.uniform(60, 180), rnd.uniform(40, 120)), mul(wall, 0.9), 0.25, blur=30)
    # vigas de madeira
    for x in (60, 1020):
        layer(c, rr(x - 26, 0, x + 26, 1500, 6), gray_of((120, 82, 52), gray), depth=0.4, seed=x)
        for k in range(8):
            ink(c, [(x - 14 + k % 3 * 10, k * 180 + 20), (x - 12 + k % 3 * 10, k * 180 + 150)], 1.4, (70, 44, 28), 0.5)
    layer(c, rr(-20, 80, W + 20, 130, 4), gray_of((120, 82, 52), gray), depth=0.4, seed=11)
    # chão de terra batida
    layer(c, rr(-40, 1360, W + 40, H + 40, 2), gray_of((150, 110, 74), gray), depth=0.05, shadow=False, rim=False, seed=12)
    for i in range(40):
        flat(c, ell(rnd.uniform(0, W), rnd.uniform(1380, H), rnd.uniform(8, 30), rnd.uniform(2, 5)), (110, 78, 50), 0.35)


def window(c, x0, y0, x1, y1, outside=None, gray=0.0):
    """Janela redonda (lua) com o lado de fora desenhado por outside(c)."""
    cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2
    hole = circ(cx, cy, r)
    c.save(); c.clipPath(hole, doAntiAlias=True)
    if outside:
        outside(c)
    c.restore()
    frame = pl.diff(circ(cx, cy, r + 26), hole)
    layer(c, frame, gray_of((126, 84, 52), gray), depth=0.45, seed=21)
    ink(c, [(cx - r - 10, cy), (cx - r + 4, cy - 30)], 1.5, (60, 36, 20), 0.5)


# ------------------------------------------------------------ acabamento
def grade(c, sat=1.0, warm=0.0, bright=1.0, contrast=1.0):
    """Matriz de cor por cena aplicada em saveLayer (chamar antes de desenhar, fechar com c.restore())."""
    s = sat
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    m = [lr * (1 - s) + s, lg * (1 - s), lb * (1 - s), 0, 0,
         lr * (1 - s), lg * (1 - s) + s, lb * (1 - s), 0, 0,
         lr * (1 - s), lg * (1 - s), lb * (1 - s) + s, 0, 0,
         0, 0, 0, 1, 0]
    k = bright * contrast
    off = (1 - contrast) * 0.5 * 255 / 255
    for r in range(3):
        for j in range(3):
            m[r * 5 + j] *= k
        m[r * 5 + 4] = off + [warm * 0.06, warm * 0.02, -warm * 0.05][r]
    cf = skia.ColorFilters.Matrix(m)
    c.saveLayer(None, skia.Paint(ColorFilter=cf))


def floor_ceiling(img_canvas):
    pass


def caption(c, lines, name=None, name_col=(232, 150, 90)):
    """Legenda Libre Franklin 700 54 px, centrada em x=500, linhas em torno de y≈1330."""
    size, lh = 54, 54 * 1.15
    n = len(lines)
    base = 1330 - (n - 1) * lh / 2 + 18
    top = base - size - 250
    c.drawRect(skia.Rect(0, top, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, top), skia.Point(0, H)],
        [C((10, 8, 12), 0), C((10, 8, 12), 120 / 255), C((10, 8, 12), 120 / 255)], [0, (base + 40 - top) / (H - top), 1])))
    f = skia.Font(pl.FONT['lf700'], size)
    for i, line in enumerate(lines):
        y = base + i * lh
        w = f.measureText(line)
        x = 500 - w / 2
        sh = skia.Paint(AntiAlias=True, Color=C((0, 0, 0), 110 / 255), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.5))
        c.drawString(line, x + 2, y + 2, f, sh)
        c.drawString(line, x, y, f, skia.Paint(AntiAlias=True, Color=C((247, 241, 230))))


def finish(c, t=0.0, vig=150):
    pl.vignette(c, W, H, vig)
    pl.grain(c, W, H, t, 13)


def danger_zones(c):
    p = skia.Paint(Color=C((230, 30, 30), 0.25))
    c.drawRect(skia.Rect(0, 0, W, 150), p)
    c.drawRect(skia.Rect(0, 1440, W, H), p)
    c.drawRect(skia.Rect(940, 150, W, 1440), p)
    c.drawRect(skia.Rect(0, 150, 60, 1440), p)


def blurred(c, draw_fn, sigma):
    """Desenha draw_fn numa camada desfocada (profundidade de campo)."""
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(sigma, sigma)))
    draw_fn(c)
    c.restore()


# ------------------------------------------------------------ praça (exterior do palácio)
def plaza_bg(c, t=0.0):
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 0), skia.Point(0, 900)], [C((150, 196, 222)), C((238, 224, 190))])))
    c.drawPaint(skia.Paint(Shader=pl.fiber_shader(1.0), BlendMode=skia.BlendMode.kMultiply, Alphaf=0.5))
    for k, (x, y, r) in enumerate([(160, 230, 60), (820, 180, 80)]):
        for j in range(3):
            layer(c, ell(x + j * r * 0.7 + (t * 6) % 40, y + (j % 2) * 10, r, r * 0.55), (250, 246, 236), depth=0.2, seed=k * 3 + j, rim=False)
    layer(c, smooth([(-80, 700), (300, 610), (700, 650), (1160, 590), (1160, 900), (-80, 900)], tension=0.4), (120, 160, 110), depth=0.15)
    # fachada do palácio
    layer(c, rr(140, 420, 940, 760, 6), (176, 52, 46), depth=0.3, seed=31)
    for x in range(200, 900, 110):
        layer(c, rr(x, 520, x + 36, 760, 4), (150, 40, 38), depth=0.15, seed=x)
    for k, (y0, w0) in enumerate([(380, 900), (300, 720)]):
        roof = poly([(540 - w0 / 2 - 40, y0 + 60), (540 + w0 / 2 + 40, y0 + 60), (540 + w0 / 2 - 30, y0), (540 - w0 / 2 + 30, y0)])
        layer(c, roof, (50, 66, 76), depth=0.35, seed=40 + k)
        for j in range(18):
            ink(c, [(540 - w0 / 2 + j * w0 / 17, y0 + 6), (540 - w0 / 2 + j * w0 / 17 - 6, y0 + 56)], 2, (90, 110, 120), 0.6)
        layer(c, rr(540 - w0 / 2 - 50, y0 + 52, 540 + w0 / 2 + 50, y0 + 66, 4), (214, 170, 80), depth=0.1, seed=50 + k)
    # escadaria
    for k in range(7):
        layer(c, rr(300 - k * 26, 760 + k * 30, 780 + k * 26, 792 + k * 30, 3), mix((220, 206, 180), (180, 160, 130), k / 7), depth=0.12, seed=60 + k)
    layer(c, rr(-40, 970, W + 40, H + 40, 1), (210, 190, 150), depth=0.05, shadow=False, rim=False, seed=70)
    for k in range(10):
        c.drawLine(-40, 1000 + k * k * 9, W + 40, 1000 + k * k * 9, skia.Paint(AntiAlias=True, Color=C((150, 120, 80), 0.25), StrokeWidth=2))


def season_outside(c, season, t=0.0, x0=0, y0=0, x1=W, y1=H):
    skies = {'primavera': ((170, 210, 230), (240, 230, 200)), 'verao': ((120, 186, 230), (250, 236, 190)),
             'outono': ((214, 170, 120), (240, 210, 170)), 'inverno': ((170, 184, 200), (226, 230, 236))}
    a, b = skies[season]
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y0), skia.Point(0, y1)], [C(a), C(b)])))
    hill = {'primavera': (130, 176, 110), 'verao': (100, 160, 90), 'outono': (190, 140, 80), 'inverno': (236, 240, 244)}[season]
    layer(c, smooth([(x0 - 50, y1 - 150), ((x0 + x1) / 2, y1 - 230), (x1 + 50, y1 - 170), (x1 + 50, y1 + 50), (x0 - 50, y1 + 50)], tension=0.4), hill, depth=0.1)
    rnd = random.Random(7)
    if season == 'outono':
        for i in range(26):
            px = rnd.uniform(x0, x1) + math.sin(t * 1.3 + i) * 30
            py = y0 + (rnd.uniform(0, 1) * (y1 - y0) + t * 90 * rnd.uniform(0.6, 1)) % (y1 - y0)
            leaf(c, px, py, rnd.uniform(0, 360) + t * 80, 22, 0, i)
    if season == 'inverno':
        for i in range(50):
            px = rnd.uniform(x0, x1) + math.sin(t + i) * 12
            py = y0 + (rnd.uniform(0, 1) * (y1 - y0) + t * 60 * rnd.uniform(0.5, 1)) % (y1 - y0)
            flat(c, circ(px, py, rnd.uniform(3, 7)), (255, 255, 255), 0.9)
    if season == 'verao':
        for i in range(40):
            px = rnd.uniform(x0, x1); py = y0 + (rnd.uniform(0, 1) * (y1 - y0) + t * 300) % (y1 - y0)
            ink(c, [(px, py), (px - 6, py + 30)], 2.2, (200, 220, 240), 0.6)


def sill(c, x0, x1, y):
    layer(c, rr(x0, y, x1, y + 34, 4), (128, 86, 54), depth=0.3, seed=80)
    for k in range(4):
        ink(c, [(x0 + 20 + k * 90, y + 10), (x0 + 80 + k * 90, y + 14)], 1.4, (70, 44, 28), 0.5)
