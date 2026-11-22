"""Núcleo do paper style 2.0 — Os Músicos de Bremen.
Papel recortado + tecido costurado, luz motivada, sombras de camada."""
import skia, numpy as np, math, functools

W, H = 1080, 1920
FONTS = '/home/user/editvideo/bremen/fonts/'
TF = {k: skia.Typeface.MakeFromFile(FONTS + k + '.ttf') for k in ['LF700', 'LF900', 'LoraI']}
assert all(TF.values())

STYLE = dict(
    shadow_alpha=95, shadow_blur=5.0, shadow_blur_k=8.0, shadow_off=4.0, shadow_off_k=10.0,
    dark_side=0.66, rim_alpha=70, rim_w=1.8, stitch_alpha=150, stitch_w=2.2,
    grain_alpha=13, vignette_alpha=150, cap_size=54, cap_y=1330, cap_col=(247, 241, 230),
    accent={'BURRO': (232, 170, 80), 'GATO': (176, 196, 226)},
)

LIGHT = [(-0.6, -0.8)]  # direção de onde a luz vem (lista mutável, ajustada por cena)


def set_light(dx, dy):
    n = math.hypot(dx, dy) or 1
    LIGHT[0] = (dx / n, dy / n)


def C(rgb, a=255):
    return skia.Color(int(rgb[0]), int(rgb[1]), int(rgb[2]), int(a))


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def shade(rgb, k):
    return tuple(max(0, min(255, v * k)) for v in rgb)


def warm(rgb, k=1.12):
    r, g, b = rgb
    return (min(255, r * k + 6), min(255, g * (1 + (k - 1) * 0.7) + 3), min(255, b * (1 + (k - 1) * 0.2)))


def cool_dark(rgb, k):
    r, g, b = rgb
    return (r * k * 0.92, g * k * 0.97, min(255, b * k * 1.08 + 6))


# ---------------------------------------------------------------- texturas
def _tile(seed, kind):
    rng = np.random.default_rng(seed)
    n = 512
    base = rng.normal(0, 1, (n, n))
    for st in (1, 2, 4, 8, 8, 4):  # suaviza sem blocos
        base = (base + np.roll(base, st, 0) + np.roll(base, -st, 0) + np.roll(base, st, 1) + np.roll(base, -st, 1)) / 5
    base /= base.std() + 1e-9
    fine = rng.normal(0, 1, (n, n))
    v = 0.5 + base * 0.10 + fine * 0.035
    if kind == 'paper':
        for _ in range(260):  # fiapos
            x, y = rng.uniform(0, n, 2)
            ang = rng.uniform(0, math.pi)
            L = rng.uniform(8, 40)
            for s in np.linspace(0, L, int(L)):
                xi, yi = int(x + math.cos(ang) * s) % n, int(y + math.sin(ang) * s) % n
                v[yi, xi] -= rng.uniform(0.04, 0.10)
    else:  # tecido: trama
        xx, yy = np.meshgrid(np.arange(n), np.arange(n))
        weave = 0.06 * np.sin(xx * 2 * math.pi / 6) * np.sin(yy * 2 * math.pi / 6)
        v += weave + 0.03 * np.sin(xx * 2 * math.pi / 3)
    v = np.clip(v, 0, 1)
    g = (0.80 + 0.20 * v)  # multiplicador
    a = np.zeros((n, n, 4), np.uint8)
    a[..., 0] = a[..., 1] = a[..., 2] = (g * 255).astype(np.uint8)
    a[..., 3] = 255
    return skia.Image.fromarray(a)


TEX = {'paper': _tile(3, 'paper'), 'fabric': _tile(7, 'fabric')}
TEXSH = {k: v.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat) for k, v in TEX.items()}
TEXPAINT = {k: skia.Paint(AntiAlias=True, Shader=v, BlendMode=skia.BlendMode.kMultiply) for k, v in TEXSH.items()}


# ---------------------------------------------------------------- geometria
def P(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def smooth(pts, close=True, k=1 / 6):
    """Catmull-Rom -> cúbicas."""
    p = skia.Path()
    n = len(pts)
    p.moveTo(*pts[0])
    rng = range(n) if close else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (close or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        p.cubicTo(*c1, *c2, *p2)
    if close:
        p.close()
    return p


def oval(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def circ(cx, cy, r):
    return oval(cx, cy, r, r)


def rr(x0, y0, x1, y1, r):
    p = skia.Path()
    p.addRRect(skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r))
    return p


def union(*ps):
    out = ps[0]
    for q in ps[1:]:
        out = skia.Op(out, q, skia.PathOp.kUnion_PathOp)
    return out


def inter(a, b):
    return skia.Op(a, b, skia.PathOp.kIntersect_PathOp)


def diff(a, b):
    return skia.Op(a, b, skia.PathOp.kDifference_PathOp)


def xf(path, m):
    q = skia.Path(path)
    q.transform(m)
    return q


def rot_about(path, deg, cx, cy):
    return xf(path, skia.Matrix.RotateDeg(deg, skia.Point(cx, cy)))


def tp(pts, w0, w1, close_cap=True):
    """Fita afunilada ao longo de pts (largura w0 -> w1)."""
    n = len(pts)
    L, R = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = (w0 + (w1 - w0) * i / max(1, n - 1)) / 2
        L.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
        R.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
    return smooth(L + R[::-1], True)


def bez(p0, p1, p2, n=12):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n)]


_JAG = {}


def jag(path, amp=1.3, step=5.0, seed=1):
    """Borda cortada à mão (memoizada pelo conteúdo do path)."""
    key = (bytes(path.serialize()), amp, step, seed)
    r = _JAG.get(key)
    if r is None:
        if len(_JAG) > 60000:
            _JAG.clear()
        r = _jag(path, amp, step, seed)
        _JAG[key] = r
    return r


def _jag(path, amp=1.3, step=5.0, seed=1):
    """Borda cortada à mão: amostra o contorno e desloca na normal com ruído de senos."""
    out = skia.Path()
    it = skia.Path.Iter(path, True)
    # separa contornos
    contours = []
    cur = skia.Path()
    pm = skia.PathMeasure(path, True)
    k = 0
    while True:
        L = pm.getLength()
        if L <= 0:
            if not pm.nextContour():
                break
            continue
        n = max(8, int(L / step))
        pts = []
        ph = seed * 1.7 + k * 3.1
        for i in range(n):
            d = L * i / n
            pos, tan = pm.getPosTan(d)
            nx, ny = -tan.y(), tan.x()
            o = amp * (math.sin(d * 0.21 + ph) * 0.6 + math.sin(d * 0.57 + ph * 2.3) * 0.3 + math.sin(d * 1.31 + ph) * 0.25)
            pts.append((pos.x() + nx * o, pos.y() + ny * o))
        out.moveTo(*pts[0])
        for q in pts[1:]:
            out.lineTo(*q)
        out.close()
        k += 1
        if not pm.nextContour():
            break
    out.setFillType(path.getFillType())
    return out


# ---------------------------------------------------------------- desenho de camada
_blur_cache = {}


def blurmf(s):
    s = round(s, 1)
    if s not in _blur_cache:
        _blur_cache[s] = skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, max(0.1, s))
    return _blur_cache[s]


def layer(c, path, col, depth=0.5, a=255, tex='paper', stitch=False, stitch_col=None, rim=True,
          shadow=True, grad=True, sil=None, light_k=1.0, lightdir=None):
    """Recorte de papel/tecido: sombra projetada, degradê pela luz, textura multiply, costura, filete de luz.
    sil = cor (rgb) para desenhar como silhueta chapada."""
    if sil is not None:
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=C(sil, a)))
        return
    lx, ly = lightdir or LIGHT[0]
    b = path.computeTightBounds()
    if shadow and depth > 0:
        off = STYLE['shadow_off'] + STYLE['shadow_off_k'] * depth
        c.save()
        c.translate(-lx * off, -ly * off)
        c.drawPath(path, skia.Paint(AntiAlias=True, Color=skia.Color(20, 16, 24, int(STYLE['shadow_alpha'] * a / 255)),
                                    MaskFilter=blurmf(STYLE['shadow_blur'] + STYLE['shadow_blur_k'] * depth)))
        c.restore()
    cx, cy = b.centerX(), b.centerY()
    r = max(b.width(), b.height()) * 0.6 + 1
    lit = warm(col, 1.0 + 0.10 * light_k)
    dark = cool_dark(col, STYLE['dark_side'] + (1 - light_k) * 0.1)
    if grad:
        sh = skia.GradientShader.MakeLinear([skia.Point(cx + lx * r, cy + ly * r), skia.Point(cx - lx * r, cy - ly * r)],
                                            [C(lit, a), C(col, a), C(dark, a)], [0, 0.45, 1])
    else:
        sh = skia.Shaders.Color(C(col, a))
    c.drawPath(path, skia.Paint(AntiAlias=True, Shader=sh, Alphaf=a / 255))
    if tex:
        c.drawPath(path, TEXPAINT[tex] if a >= 255 else skia.Paint(AntiAlias=True, Shader=TEXSH[tex], BlendMode=skia.BlendMode.kMultiply,
                                                                Alphaf=a / 255))
    # sombra interna suave + filete
    c.save()
    c.clipPath(path, skia.ClipOp.kIntersect, True)
    c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=6,
                                Color=skia.Color(0, 0, 0, int(40 * a / 255)), MaskFilter=blurmf(3)))
    if rim:
        c.translate(-lx * 1.6, -ly * 1.6)
        c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=STYLE['rim_w'] * 2,
                                    Color=skia.Color(255, 246, 225, int(STYLE['rim_alpha'] * a / 255))))
    c.restore()
    if stitch:
        sc = stitch_col or shade(col, 1.45)
        stitch_line(c, inset(path, 7), sc, a)


def inset(path, d):
    """Contorno aproximadamente recuado (escala em torno do centro)."""
    b = path.computeTightBounds()
    if b.width() < 2 * d + 2 or b.height() < 2 * d + 2:
        return path
    sx = (b.width() - 2 * d) / b.width()
    sy = (b.height() - 2 * d) / b.height()
    m = skia.Matrix()
    m.setScale(sx, sy, b.centerX(), b.centerY())
    return xf(path, m)


def stitch_line(c, path, col, a=255, w=None, on=9, off=6):
    w = w or STYLE['stitch_w']
    c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap,
                                Color=C(col, STYLE['stitch_alpha'] * a / 255), PathEffect=skia.DashPathEffect.Make([on, off], 0)))


def ink(c, path, col=(40, 30, 28), a=150, w=2.0):
    c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w, StrokeCap=skia.Paint.kRound_Cap,
                                StrokeJoin=skia.Paint.kRound_Join, Color=C(col, a)))


def fill(c, path, col, a=255, blur=0):
    p = skia.Paint(AntiAlias=True, Color=C(col, a))
    if blur:
        p.setMaskFilter(blurmf(blur))
    c.drawPath(path, p)


def plaid(c, path, base, c1, c2, step=26, a=255, ang=0):
    """Xadrez costurado dentro de path."""
    c.save()
    c.clipPath(path, skia.ClipOp.kIntersect, True)
    b = path.computeTightBounds()
    cx, cy = b.centerX(), b.centerY()
    c.rotate(ang, cx, cy)
    R = max(b.width(), b.height())
    x = cx - R
    i = 0
    while x < cx + R:
        col = c1 if i % 3 == 0 else c2
        aa = 120 if i % 3 == 0 else 70
        c.drawRect(skia.Rect(x, cy - R, x + step * 0.42, cy + R), skia.Paint(Color=C(col, aa * a / 255)))
        c.drawRect(skia.Rect(cx - R, x - cx + cy, cx + R, x - cx + cy + step * 0.42), skia.Paint(Color=C(col, aa * a / 255)))
        x += step
        i += 1
    c.restore()


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def easeOutBack(x, s=1.4):
    x = clamp(x)
    c3 = s + 1
    return 1 + c3 * (x - 1) ** 3 + s * (x - 1) ** 2


def easeInQuad(x):
    x = clamp(x)
    return x * x


def ramp(t, t0, t1, f=ease):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return f((t - t0) / (t1 - t0))


def lerp(a, b, t):
    return a + (b - a) * t


def spring(t, t0, amp=1.0, freq=2.2, damp=4.0):
    """oscilação amortecida a partir de t0"""
    if t < t0:
        return 0.0
    u = t - t0
    return amp * math.exp(-damp * u) * math.sin(2 * math.pi * freq * u)


def on2(t):
    """personagens animados 'em dois' (15 fps efetivos)"""
    return math.floor(t * 15) / 15


# ---------------------------------------------------------------- pós
def grain_images(n=6, seed=11):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        g = rng.normal(128, 40, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)
        a = np.zeros((H // 2, W // 2, 4), np.uint8)
        a[..., 0] = a[..., 1] = a[..., 2] = g
        a[..., 3] = 255
        out.append(skia.Image.fromarray(a))
    return out


def grade_matrix(sat=1.0, bright=1.0, tint=(1, 1, 1), contrast=1.0, lift=(14, 19, 24)):
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    s = sat
    m = [
        lr * (1 - s) + s, lg * (1 - s), lb * (1 - s),
        lr * (1 - s), lg * (1 - s) + s, lb * (1 - s),
        lr * (1 - s), lg * (1 - s), lb * (1 - s) + s,
    ]
    out = []
    for r in range(3):
        k = bright * tint[r] * contrast
        off = (1 - contrast) * 0.5 + lift[r] / 255 * 0.6
        out += [m[r * 3] * k, m[r * 3 + 1] * k, m[r * 3 + 2] * k, 0, off]
    out += [0, 0, 0, 1, 0]
    return out
