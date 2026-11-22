"""Base de papel recortado (paper style 2.0) — O Pote Vazio.
Tudo que é recorte passa por layer(): borda à mão, luz motivada, sombra projetada,
sombra interna, filete de luz no lado aceso e fibra em multiply."""
import math, os
import numpy as np
import skia

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = {k: skia.Typeface.MakeFromFile(os.path.join(HERE, 'fonts', f)) for k, f in
        [('lf900', 'LF900.ttf'), ('lf700', 'LF700.ttf'), ('lorai', 'LoraI.ttf'), ('lora700', 'Lora700.ttf')]}
for k, v in FONT.items():
    assert v is not None, k

# ---------------------------------------------------------------- STYLE único
STYLE = dict(
    light=(-0.55, -0.83),          # direção PARA a luz (janela no alto à esquerda)
    lit_mix=0.13, lit_warm=(255, 244, 222),
    dark_mul=0.62, dark_cool=(40, 52, 78), dark_cool_mix=0.12,
    jag_amp=1.3, jag_step=5.0,
    shadow_col=(28, 22, 30), shadow_a=0.42,
    inner_a=0.30, rim_a=70 / 255, rim_w=1.8,
    fiber_a=0.55,
    ink=(44, 32, 30),
    paper_bg=(232, 220, 198),
    black_floor=(14, 19, 24), white_top=(244, 238, 227),
)

SCALE = [1.0]   # escala atual do mundo -> px (para manter amplitudes em px)


def C(rgb, a=1.0):
    r, g, b = rgb[:3]
    return skia.Color(int(max(0, min(255, r))), int(max(0, min(255, g))), int(max(0, min(255, b))),
                      int(max(0, min(255, a * 255))))


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def mul(a, k):
    return tuple(x * k for x in a[:3])


# ---------------------------------------------------------------- fibra
def _fiber_image(seed=3, n=512):
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, (n, n)).astype(np.float32)
    # suaviza em duas escalas (fibra + manchas)
    def blur(a, k):
        f = np.fft.rfft2(a)
        ky = np.fft.fftfreq(a.shape[0])[:, None]
        kx = np.fft.rfftfreq(a.shape[1])[None, :]
        return np.fft.irfft2(f * np.exp(-(kx ** 2 + ky ** 2) * (k ** 2) * 20), s=a.shape)
    v = 0.6 * blur(base, 2.0) / (blur(base, 2.0).std() + 1e-6) + 0.4 * blur(rng.normal(0, 1, (n, n)), 14) / 0.02
    v = (v - v.mean()) / (v.std() + 1e-6)
    img = 1.0 - 0.035 * np.clip(v, -3, 3) - 0.02
    # fiapos
    for _ in range(420):
        x, y = rng.uniform(0, n, 2)
        ang = rng.uniform(0, math.pi)
        L = rng.uniform(6, 26)
        d = rng.uniform(0.03, 0.08) * rng.choice([-1, 1])
        for t in np.linspace(0, 1, int(L * 2)):
            xx = int(x + math.cos(ang) * L * t + math.sin(t * 6) * 1.2) % n
            yy = int(y + math.sin(ang) * L * t) % n
            img[yy, xx] -= d
    img = np.clip(img, 0.80, 1.0)
    g = (img * 255).astype(np.uint8)
    rgba = np.dstack([g, g, g, np.full_like(g, 255)])
    return skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)


FIBER = _fiber_image()


def fiber_shader(scale=1.0):
    m = skia.Matrix.Scale(scale, scale)
    return FIBER.makeShader(skia.TileMode.kRepeat, skia.TileMode.kRepeat, skia.SamplingOptions(skia.FilterMode.kLinear), m)


# ---------------------------------------------------------------- caminhos
def smooth(pts, closed=True, tension=0.5):
    """Catmull-Rom -> cúbicas."""
    p = skia.Path()
    n = len(pts)
    if n < 2:
        return p
    p.moveTo(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else pts[(i + 1) % n]
        k = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 2, p1[1] + (p2[1] - p0[1]) * k / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 2, p2[1] - (p3[1] - p1[1]) * k / 2)
        p.cubicTo(*c1, *c2, *p2)
    if closed:
        p.close()
    return p


def poly(pts):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    return p


def ell(cx, cy, rx, ry):
    p = skia.Path()
    p.addOval(skia.Rect(cx - rx, cy - ry, cx + rx, cy + ry))
    return p


def circ(cx, cy, r):
    return ell(cx, cy, r, r)


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


def xform(path, dx=0, dy=0, rot=0, sx=1, sy=None, cx=0, cy=0):
    sy = sx if sy is None else sy
    m = skia.Matrix()
    m.setTranslate(dx, dy)
    m.preRotate(rot, cx, cy)
    m.preScale(sx, sy, cx, cy)
    q = skia.Path(path)
    q.transform(m)
    return q


def tp(pts, w0, w1, closed_ends=True):
    """Fita afunilada ao longo de uma polilinha (mechas, sobrancelhas, galhos)."""
    n = len(pts)
    L, R = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * t) / 2
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return smooth(L + R[::-1], closed=True, tension=0.45)


def jag(path, amp=None, step=None, seed=0.0):
    amp = (STYLE['jag_amp'] if amp is None else amp) / SCALE[0]
    step = (STYLE['jag_step'] if step is None else step) / SCALE[0]
    out = skia.Path()
    m = skia.PathMeasure(path, False)
    k = 0
    while True:
        L = m.getLength()
        if L > 0:
            n = max(8, int(L / step))
            pts = []
            for i in range(n):
                pos, tan = m.getPosTan(L * i / n)
                nx, ny = -tan.y(), tan.x()
                s = i * step * SCALE[0]
                o = amp * (0.55 * math.sin(s * 0.37 + seed + k) + 0.3 * math.sin(s * 1.13 + 2.1 * seed) + 0.15 * math.sin(s * 2.9 + k * 3))
                pts.append((pos.x() + nx * o, pos.y() + ny * o))
            if m.isClosed():
                out.addPoly([skia.Point(*q) for q in pts], True)
            else:
                out.addPoly([skia.Point(*q) for q in pts], False)
        k += 1
        if not m.nextContour():
            break
    out.setFillType(path.getFillType())
    return out


# ---------------------------------------------------------------- layer()
def layer(c, path, col, depth=0.5, a=1.0, shadow=True, fiber=True, rim=True, inner=True,
          rough=True, seed=0.0, light=None, grad=True, lit_mix=None, dark_mul=None):
    L = light or STYLE['light']
    p = jag(path, seed=seed) if rough else path
    s = 1.0 / SCALE[0]
    b = p.getBounds()
    cx, cy = b.centerX(), b.centerY()
    r = max(b.width(), b.height()) / 2 + 1
    if shadow:
        off = (4 + 12 * depth) * s
        sig = (5 + 9 * depth) * s * 0.5
        sp = skia.Paint(AntiAlias=True, Color=C(STYLE['shadow_col'], STYLE['shadow_a'] * a),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sig))
        c.save()
        c.translate(-L[0] * off, -L[1] * off)
        c.drawPath(p, sp)
        c.restore()
    lm = STYLE['lit_mix'] if lit_mix is None else lit_mix
    dm = STYLE['dark_mul'] if dark_mul is None else dark_mul
    lit = mix(col, STYLE['lit_warm'], lm)
    dark = mix(mul(col, dm), STYLE['dark_cool'], STYLE['dark_cool_mix'])
    fp = skia.Paint(AntiAlias=True)
    if grad:
        fp.setShader(skia.GradientShader.MakeLinear(
            [skia.Point(cx + L[0] * r, cy + L[1] * r), skia.Point(cx - L[0] * r, cy - L[1] * r)],
            [C(lit, a), C(col, a), C(dark, a)], [0.0, 0.45, 1.0]))
    else:
        fp.setColor(C(col, a))
    c.drawPath(p, fp)
    c.save()
    c.clipPath(p, doAntiAlias=True)
    if fiber:
        c.drawPaint(skia.Paint(Shader=fiber_shader(s), BlendMode=skia.BlendMode.kMultiply,
                               Alphaf=STYLE['fiber_a'] * a))
    if inner:
        ip = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=7 * s,
                        Color=C(mul(col, 0.35), STYLE['inner_a'] * a),
                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3 * s))
        c.drawPath(p, ip)
    if rim:
        rp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=STYLE['rim_w'] * s * 2)
        rp.setShader(skia.GradientShader.MakeLinear(
            [skia.Point(cx + L[0] * r, cy + L[1] * r), skia.Point(cx, cy)],
            [C((255, 248, 232), STYLE['rim_a'] * a), C((255, 248, 232), 0)]))
        c.drawPath(p, rp)
    c.restore()
    return p


def flat(c, path, col, a=1.0, blur=0, rough=False):
    p = jag(path) if rough else path
    pt = skia.Paint(AntiAlias=True, Color=C(col, a))
    if blur:
        pt.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur / SCALE[0]))
    c.drawPath(p, pt)


def ink(c, pts, w=2.0, col=None, a=0.75, w1=None, closed=False):
    """Linha fina de nanquim feita à mão (fita afunilada levemente tremida)."""
    col = col or STYLE['ink']
    w1 = w * 0.35 if w1 is None else w1
    path = tp(pts, w / SCALE[0] * 1.0 if False else w, w1)
    c.drawPath(path, skia.Paint(AntiAlias=True, Color=C(col, a)))


def contact_shadow(c, cx, cy, rx, ry, a=0.45):
    flat(c, ell(cx, cy, rx, ry), (20, 16, 22), a, blur=6)


# ---------------------------------------------------------------- IK de 2 segmentos
def ik(sh, hand, l1, l2, side):
    """Cotovelo SEMPRE para fora: side=-1 braço esquerdo da tela (dobra p/ esquerda), +1 direito."""
    dx, dy = hand[0] - sh[0], hand[1] - sh[1]
    d = math.hypot(dx, dy)
    d = min(d, l1 + l2 - 0.01)
    a = math.atan2(dy, dx)
    cosb = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    b = math.acos(max(-1, min(1, cosb)))
    # escolhe o sinal que joga o cotovelo para o lado de fora (x mais na direção de side)
    e1 = (sh[0] + l1 * math.cos(a + b), sh[1] + l1 * math.sin(a + b))
    e2 = (sh[0] + l1 * math.cos(a - b), sh[1] + l1 * math.sin(a - b))
    elbow = e1 if (e1[0] - e2[0]) * side > 0 else e2
    hx = elbow[0] + l2 * (hand[0] - elbow[0]) / (math.hypot(hand[0] - elbow[0], hand[1] - elbow[1]) or 1)
    hy = elbow[1] + l2 * (hand[1] - elbow[1]) / (math.hypot(hand[0] - elbow[0], hand[1] - elbow[1]) or 1)
    return elbow, (hx, hy)


def limb(a, b, w0, w1):
    """Peça de papel de um segmento (manga, antebraço): cápsula afunilada."""
    return tp([a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b], w0, w1)


# ---------------------------------------------------------------- texto
def text(c, s, x, y, size, font='lf700', col=(40, 30, 28), a=1.0, align='center', shadow=False):
    f = skia.Font(FONT[font], size)
    w = f.measureText(s)
    if align == 'center':
        x -= w / 2
    elif align == 'right':
        x -= w
    if shadow:
        c.drawString(s, x + 2, y + 2, f, skia.Paint(AntiAlias=True, Color=C((0, 0, 0), 0.43),
                                                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.5)))
    c.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=C(col, a)))
    return w


def paper_bg(c, w, h, col=None):
    col = col or STYLE['paper_bg']
    c.drawPaint(skia.Paint(Color=C(col)))
    c.drawPaint(skia.Paint(Shader=fiber_shader(1.0), BlendMode=skia.BlendMode.kMultiply, Alphaf=0.45))


def grain(c, w, h, t=0, a=12):
    rng = np.random.default_rng(int(t * 15) + 7)
    n = rng.integers(0, 255, (h // 2, w // 2), dtype=np.uint8)
    rgba = np.dstack([n, n, n, np.full_like(n, a)])
    img = skia.Image.fromarray(rgba, colorType=skia.ColorType.kRGBA_8888_ColorType)
    c.save()
    c.scale(2, 2)
    c.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(BlendMode=skia.BlendMode.kOverlay))
    c.restore()


def vignette(c, w, h, a=160):
    p = skia.Paint(Shader=skia.GradientShader.MakeRadial(
        skia.Point(w / 2, h * 0.45), max(w, h) * 0.72,
        [C((0, 0, 0), 0), C((0, 0, 0), 0), C((8, 6, 12), a / 255)], [0, 0.55, 1.0]))
    c.drawPaint(p)
