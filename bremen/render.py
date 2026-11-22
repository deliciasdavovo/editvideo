"""Planos, câmera, legenda, pós e saída de quadros — Os Músicos de Bremen (paper style 2.0)."""
import sys, json, re, os
from chars import *
import scenes as S

TL = json.load(open('/home/user/editvideo/bremen/audio/timeline.json'))
T_END = TL['T']
FPS = 30
EV = {e['key']: e for e in TL['events']}
WORDS = TL['words']


def norm(w):
    return re.sub(r'[^\wáéíóúâêôãõàç]', '', w.lower())


def Wt(word, n=1, clip=None):
    """início da n-ésima ocorrência da palavra (opcionalmente dentro de um clipe)"""
    k = 0
    for w in WORDS:
        if norm(w['w']) == norm(word) and (clip is None or w['clip'] == clip):
            k += 1
            if k == n:
                return w['t0']
    raise KeyError(word)


def env(key, t):
    """envelope de fala (0..1) do clipe key no tempo t (amostrado 'em dois')"""
    e = EV.get(key)
    if not e or t < e['t0'] or t > e['t1']:
        return 0.0
    t = on2(t)
    arr = TL['env'][key]
    i = int((t - e['t0']) * 30)
    if i >= len(arr):
        return 0.0
    return arr[i]


def mouth_lvl(key, t):
    v = env(key, t)
    return 0 if v < 0.12 else (0.45 if v < 0.45 else 0.9)


# ---------------------------------------------------------------- cache de cenários
BG = {}


def bg(name, layer_, **kw):
    key = (name, layer_, tuple(sorted(kw.items())))
    if key not in BG:
        s = skia.Surface(W + 2 * S.M, S.G + S.M + 700 + S.M)
        c = s.getCanvas()
        c.clear(skia.Color(0, 0, 0, 0))
        c.translate(S.M, S.M)
        getattr(S, 'bg_' + name)(c, layer_, **kw)
        BG[key] = s.makeImageSnapshot()
    return BG[key]


def draw_bg(c, name, layer_, **kw):
    c.drawImage(bg(name, layer_, **kw), -S.M, -S.M)


# ---------------------------------------------------------------- câmera
class Cam:
    def __init__(self, cx=540, cy=960, z=1.0):
        self.cx, self.cy, self.z = cx, cy, z

    def apply(self, c, par=1.0, ref=(540, 960)):
        # centro visual da área segura: x≈500, y≈800 (desloca o mundo ~40 px p/ esquerda)
        cx = ref[0] + (self.cx - ref[0]) * par
        cy = ref[1] + (self.cy - ref[1]) * par
        z = 1 + (self.z - 1) * (0.6 + 0.4 * par)
        c.translate(500, 800)
        c.scale(z, z)
        c.translate(-cx, -cy)


def camlerp(a, b, u):
    return Cam(lerp(a[0], b[0], u), lerp(a[1], b[1], u), lerp(a[2], b[2], u))


# ---------------------------------------------------------------- pós (grade, legenda, grão, vinheta)
GRAIN = grain_images()
VIG = None


def vignette(c, alpha):
    global VIG
    if VIG is None:
        s = skia.Surface(W, H)
        cc = s.getCanvas()
        cc.drawPaint(skia.Paint(Shader=skia.GradientShader.MakeRadial(skia.Point(500, 820), 1250,
                                                                         [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(8, 10, 16, 255)],
                                                                         [0, 0.5, 1])))
        VIG = s.makeImageSnapshot()
    c.drawImage(VIG, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=alpha / 255))


FONT_CAP = skia.Font(TF['LF700'], STYLE['cap_size'])
CAPS = TL['caps']


def wrap(text, font, maxw):
    words = text.split()
    if font.measureText(text) <= maxw:
        return [text]
    best = None
    for i in range(1, len(words)):
        a, b = ' '.join(words[:i]), ' '.join(words[i:])
        d = abs(font.measureText(a) - font.measureText(b))
        if (best is None or d < best[0]) and len(words[i:]) > 1:
            best = (d, [a, b])
    return best[1] if best else [text]


def caption(c, t):
    cur = None
    for cp in CAPS:
        if cp['t0'] <= t < cp['t1']:
            cur = cp
    # degradê suave sempre presente (começa ~250 px acima do texto e vai até a base)
    y0 = STYLE['cap_y'] - 300
    c.drawRect(skia.Rect(0, y0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y0), skia.Point(0, H)],
        [skia.Color(10, 12, 18, 0), skia.Color(10, 12, 18, 110), skia.Color(10, 12, 18, 120)], [0, 0.4, 1])))
    if not cur:
        return
    u = clamp((t - cur['t0']) / 0.12)
    sc = 0.9 + 0.1 * easeOutBack(u, 1.6)
    al = clamp((t - cur['t0']) / 0.06)
    text = cur['text']
    sp = cur['speaker']
    lines = wrap(text, FONT_CAP, 840)
    lh = STYLE['cap_size'] * 1.15
    ytop = STYLE['cap_y'] - (len(lines) - 1) * lh / 2
    c.save()
    c.translate(500, STYLE['cap_y'])
    c.scale(sc, sc)
    c.translate(-500, -STYLE['cap_y'])
    if sp:
        nf = skia.Font(TF['LF900'], 30)
        name = 'BURRO' if sp == 'BURRO' else 'GATO'
        wn = nf.measureText(name)
        c.drawString(name, 500 - wn / 2, ytop - lh * 0.95, nf, skia.Paint(AntiAlias=True, Color=C(STYLE['accent'][sp], 255 * al)))
    for i, ln in enumerate(lines):
        w = FONT_CAP.measureText(ln)
        x = 500 - w / 2
        y = ytop + i * lh + 18
        c.drawString(ln, x + 2, y + 2, FONT_CAP, skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(110 * al)), MaskFilter=blurmf(3)))
        c.drawString(ln, x, y, FONT_CAP, skia.Paint(AntiAlias=True, Color=C(STYLE['cap_col'], 255 * al)))
    c.restore()


# ---------------------------------------------------------------- utilidades de cena
def breath(t, f=0.25):
    return math.sin(t * 2 * math.pi * f)


def blink(t, period=3.7, seed=0.0, base=0.12):
    u = (t + seed) % period
    return 1.0 if u < 0.12 else base


def stack(c, x, y, s, t, sil=None, a=255, sing=0.0, wob=0.0, eyes_glow=False, build=None, tremble=0.0):
    """pirâmide: burro, cachorro, gato, galo. build = dict de progresso (0..1) de cada um subindo"""
    b = build or dict(dog=1, cat=1, roo=1)
    tt = on2(t)
    tr = tremble * math.sin(tt * 40)
    sw = wob * math.sin(tt * 7)
    c.save()
    c.translate(x, y)
    c.rotate(sw * 1.5)
    c.translate(-x, -y)
    knees = 0.25 * b['dog'] + 0.1 * spring(t, 0, 0) if False else 0.18 * b['dog']
    burro(c, x, y, s, pose=dict(head=-8 - 10 * sing, mouth='open' if sing else 'neutral', m=sing * (0.6 + 0.4 * abs(math.sin(tt * 9))),
                                 eyes=0.0 if sing else (0.35 if tremble else blink(t)), brow=0.6 if sing else -0.2, ears=0.1, knees=knees,
                                 look=(0.4, -0.4) if not tremble else (0, 0)), sil=sil, a=a)
    # cachorro sobre o lombo
    def place(prog, tx, ty, fromx, fromy):
        u = easeOutBack(prog, 1.2)
        return lerp(fromx, tx, u), lerp(fromy, ty, u) - math.sin(clamp(prog) * math.pi) * 120 * s
    dx, dy = place(b['dog'], x - 10 * s, y - 330 * s, x - 260 * s, y)
    if b['dog'] > 0:
        cachorro(c, dx + tr, dy, s * 1.05, pose=dict(mouth='open' if sing else 'closed', m=sing * (0.5 + 0.5 * abs(math.sin(tt * 11 + 1))),
                                                   ears=0.3 * sing + 0.1 * abs(sw), eyes=0.0 if sing else 0.3, look=(0.2, -0.5), brow=0.3,
                                                   t=t, tail=sing), sil=sil, a=a)
    cx_, cy_ = place(b['cat'], x + 20 * s, y - 465 * s, x - 300 * s, y)
    if b['cat'] > 0:
        gato(c, cx_ - tr, cy_, s * 1.1, pose=dict(mouth='open' if sing else 'smug', m=sing * (0.6 + 0.4 * abs(math.sin(tt * 8 + 2))),
                                                 brow='alarm' if sing else 'plot', head=4 * sw, t=t, eyes=0.1 if sing else 0.4), sil=sil, a=a)
    rx, ry = place(b['roo'], x + 20 * s, y - 735 * s, x + 320 * s, y)
    if b['roo'] > 0:
        galo(c, rx + tr, ry, s * 1.15, pose=dict(beak=sing * (0.6 + 0.4 * abs(math.sin(tt * 10))), head=-18 * sing, eye=1 if tremble else 0.5,
                                                puff=sing, flap=sing * 0.6, t=t), sil=sil, a=a)
    if eyes_glow and sil is not None:
        for ex, ey, r in ((x + 196 * s, y - 462 * s, 9), (dx + 140 * s, dy - 178 * s, 8), (cx_ - 26 * s, cy_ - 230 * s, 8),
                          (cx_ + 26 * s, cy_ - 230 * s, 8), (rx + 60 * s, ry - 200 * s, 7)):
            c.drawCircle(ex, ey, r * 3 * s, skia.Paint(AntiAlias=True, Color=skia.Color(255, 220, 120, 70), MaskFilter=blurmf(8)))
            fill(c, circ(ex, ey, r * s), (255, 228, 140), a)
    c.restore()


def bread(c, x, y, s=1.0, ang=0):
    c.save()
    c.translate(x, y)
    c.rotate(ang)
    c.scale(s, s)
    p = jag(smooth([(-70, 0), (-60, -40), (0, -56), (60, -40), (70, 0), (0, 10)]))
    layer(c, p, (200, 140, 70), 0.6, tex='fabric')
    for k in range(3):
        ink(c, smooth([(-30 + k * 26, -46), (-20 + k * 26, -30)], False), (150, 96, 50), 200, 3)
    c.restore()


def window_glass(c, rect, t, mode='night', monster=0.0, mon_scale=1.0, inside_light=False):
    """vidro da janela visto de dentro: noite lá fora; monster>0 desenha a sombra-monstro"""
    x0, y0, x1, y1 = rect
    clip = rr(x0, y0, x1, y1, 2)
    c.save()
    c.clipPath(clip, skia.ClipOp.kIntersect, True)
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, y0), skia.Point(0, y1)], [C((40, 64, 104)), C((70, 100, 140))])))
    S.stars(c, 14, 3, y1)
    c.drawCircle(x0 + (x1 - x0) * 0.8, y0 + 60, 36, skia.Paint(AntiAlias=True, Color=C((240, 232, 200)), MaskFilter=blurmf(2)))
    if monster > 0:
        mx = (x0 + x1) / 2 + 10
        stack(c, mx, y1 + 150 * mon_scale, 0.62 * mon_scale, t, sil=(14, 14, 26), a=int(255 * monster), eyes_glow=True, wob=0.3)
    c.restore()


def window_ext_glass(c, rect, t, glow=1.0):
    x0, y0, x1, y1 = rect
    c.save()
    c.clipPath(rr(x0, y0, x1, y1, 2), skia.ClipOp.kIntersect, True)
    fl = 1 + 0.03 * math.sin(t * 7) + 0.02 * math.sin(t * 13)
    c.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=skia.GradientShader.MakeRadial(
        skia.Point((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) * 0.8, [C((255, 210, 120)), C((220, 130, 60))])))
    # silhuetas dos ladrões lá dentro (comendo)
    for i, kx in enumerate((0.25, 0.55, 0.8)):
        hx = x0 + (x1 - x0) * kx
        hy = y1 - 40 + 6 * math.sin(t * 3 + i)
        fill(c, oval(hx, hy - 120, 48, 52), (120, 60, 40), 150)
        fill(c, rr(hx - 80, hy - 70, hx + 80, hy + 120, 30), (120, 60, 40), 150)
    c.restore()
    c.drawRect(skia.Rect(x0 - 200, y0 - 200, x1 + 200, y1 + 300), skia.Paint(Color=C((255, 180, 90), int(36 * glow * fl)), MaskFilter=blurmf(80)))


def particles(c, t, kind, n=40, seed=0, area=(-100, -100, 1180, 2020), a=180):
    r = np.random.default_rng(seed)
    x0, y0, x1, y1 = area
    for i in range(n):
        bx, by = r.uniform(x0, x1), r.uniform(y0, y1)
        sp = r.uniform(0.3, 1.0)
        sz = r.uniform(2, 6)
        if kind == 'dust':
            x = bx + 20 * math.sin(t * 0.4 * sp + i)
            y = (by - t * 12 * sp) % (y1 - y0) + y0
            fill(c, circ(x, y, sz * 0.6), (255, 240, 200), a * 0.5, blur=1.5)
        elif kind == 'leaf':
            x = (bx + t * 60 * sp) % (x1 - x0) + x0
            y = (by + t * 40 * sp + 30 * math.sin(t * sp * 2 + i)) % (y1 - y0) + y0
            lf = rot_about(oval(x, y, 10 + sz, 5 + sz * 0.4), t * 90 * sp + i * 40, x, y)
            fill(c, lf, [(196, 100, 50), (214, 150, 60), (160, 70, 46)][i % 3], a)
        elif kind == 'firefly':
            x = bx + 30 * math.sin(t * 0.7 * sp + i)
            y = by + 20 * math.cos(t * 0.5 * sp + i * 2)
            al = 0.5 + 0.5 * math.sin(t * 3 * sp + i)
            c.drawCircle(x, y, 10, skia.Paint(AntiAlias=True, Color=skia.Color(230, 240, 140, int(80 * al)), MaskFilter=blurmf(6)))
            fill(c, circ(x, y, 2.5), (240, 250, 180), 255 * al)
        elif kind == 'ember':
            x = bx + 15 * math.sin(t * 2 * sp + i)
            y = by - ((t * 80 * sp + i * 50) % 500)
            fill(c, circ(x, y, sz * 0.5), (255, 170, 80), a * (1 - ((t * 80 * sp + i * 50) % 500) / 500))


# ---------------------------------------------------------------- planos
SHOTS = []


def shot(t0, t1, grade=None, light=(-0.6, -0.8), trans=None):
    def deco(f):
        SHOTS.append(dict(t0=t0, t1=t1, f=f, grade=grade, light=light, trans=trans))
        return f
    return deco


G_ = S.G
GR_NIGHT = dict(sat=0.9, bright=1.0, tint=(0.92, 0.98, 1.1), contrast=1.05)
GR_COLD = dict(sat=0.55, bright=1.0, tint=(0.95, 1.0, 1.06), contrast=1.0)
GR_DAY = dict(sat=1.0, bright=1.02, tint=(1.03, 1.0, 0.94), contrast=1.04)
GR_SUNSET = dict(sat=1.05, bright=1.0, tint=(1.08, 0.97, 0.9), contrast=1.05)
GR_WARM = dict(sat=1.0, bright=1.02, tint=(1.06, 1.0, 0.9), contrast=1.05)
GR_MOON = dict(sat=0.7, bright=0.95, tint=(0.88, 0.96, 1.12), contrast=1.05)
GR_COVER = dict(sat=1.08, bright=1.06, tint=(1.04, 1.0, 0.97), contrast=1.1)

# ---- âncoras
tO = Wt('O', 1, 'b01a')  # "O monstro era"
tTodos = Wt('Todos')
tB01b = EV['b01b']['t0']
tDono = Wt('dono')
tBurroOp = Wt('burro', 3, 'b01b') if False else Wt('tinha')
tB02 = EV['b02_burro']['t0']
tN03a = EV['n03a']['t0']
tLatir = EV['burro_latir']['t0']
tLat = EV['sfx_latido']['t0']
tContr = EV['burro_contratado']['t0']
tN03b = EV['n03b']['t0']
tTal = EV['gato_talentos']['t0']
tN03c = EV['n03c']['t0']
tGalo = EV['sfx_galo']['t0']
tN04 = EV['n04']['t0']
tEeles = Wt('e', 1, 'n04')
tViram = Wt('Viram')
tLa = Wt('Lá')
tPlano = EV['gato_plano']['t0']
tConc = EV['burro_concerto']['t0']
tN05a = EV['n05a']['t0']
tJanela = Wt('Na', 1, 'n05a')
tEos = Wt('E', 2, 'n05a')
tConcert = EV['concert']['t0']
tN05b = EV['n05b']['t0']
tEpelo = Wt('E,', 1, 'n05b')
tN06 = EV['n06']['t0']
tLevou = Wt('Levou')
tArr = Wt('arranhada,')
tMord = Wt('mordida')
tCoice = Wt('coice.')
tJurou = Wt('jurou')
tN07 = EV['n07']['t0']
tMas7 = Wt('Mas', 1, 'n07')


# ===================== S1 capa: sombra-monstro na janela, ladrões fogem (interior)
@shot(0, tO, GR_COVER, (0.85, -0.3))
def s01(c, t, u):
    cam = camlerp((450, 660, 1.3), (450, 640, 1.38), ease(u))
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'interior', 'far', variant='lit')
    c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t, monster=1.0, mon_scale=1.12)
    S.fire(c, t, 960, S.G - 40, 0.9)
    draw_bg(c, 'interior', 'near', variant='lit')
    S.table(c, 120, 900, 1060)
    c.restore()
    c.save()
    # ladrões fugindo em primeiro plano (silhuetas de costas, quentes) — em coordenadas de tela
    tt = on2(t)
    for i, (kind, x0, sp) in enumerate((('largo', 150, 1.0), ('alto', 520, 1.2), ('baixo', 860, 0.9))):
        x = x0 + tt * 40 * sp * (1 if i != 0 else -1)
        ladrao(c, x, 1640 + 10 * math.sin(tt * 12 + i), 1.05, kind, pose=dict(run=tt * 2.2 * sp + i * 0.3, arms='up', lean=(-8 if i == 0 else 8),
                                                                           t=t), sil=(46, 26, 22))
    # pão voando
    bt = tt
    bread(c, 330 + bt * 60, 1050 - bt * 120 + bt * bt * 30, 1.2, bt * 200)
    c.restore()
    particles(c, t, 'ember', 12, 3, (800, 900, 1080, 1300))


# ===================== S2 revelação: os quatro empilhados tremendo diante da janela
@shot(tO, tTodos, GR_NIGHT, (0.0, -0.4))
def s02(c, t, u):
    cam = camlerp((600, 700, 1.0), (560, 760, 1.12), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 0.9)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t)
    stack(c, 560, S.G + 20, 0.92, t, tremble=1.0)
    c.restore()
    particles(c, t, 'firefly', 10, 4, (0, 300, 1080, 1300))


# ===================== S3 rostos velhos (close na pilha)
@shot(tTodos, tB01b, GR_NIGHT, (0.0, -0.4))
def s03(c, t, u):
    cam = camlerp((580, 560, 1.75), (580, 530, 1.85), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 0.9)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t)
    stack(c, 560, S.G + 20, 0.92, t, tremble=0.3)
    c.restore()


# ===================== S4 celeiro: mandado embora, porta fecha
@shot(tB01b, tDono, GR_COLD, (-0.85, -0.5), trans='page')
def s04(c, t, u):
    tl = t - tB01b
    cam = camlerp((520, 900, 1.0), (560, 920, 1.06), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'barn', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'barn', 'near')
    close = ramp(t, Wt('embora.') - 0.3, Wt('embora.') + 0.5, easeOutBack)
    S.door_panels(c, close)
    # burro sai andando da porta, cabeça baixa
    wk = ramp(tl, 0, 2.2)
    bx = lerp(330, 720, wk)
    tc = on2(t)
    # sombra longa e solitária (para a direita, longe da luz)
    c.save()
    c.translate(bx + 40, S.G + 10)
    c.scale(1.0, -0.22)
    c.skew(-1.6, 0)
    burro(c, 0, 0, 0.78, pose=dict(walk=wk < 1, step=tc * 0.8), sil=(40, 40, 50), a=110)
    c.restore()
    burro(c, bx, S.G + 10, 0.78, pose=dict(walk=wk < 1, step=tc * 0.8, head=14, ears=0.75 + 0.15 * close, eyes=0.45, brow=-0.8, mouth='sad',
                                           tail=8, look=(-0.4, 0.3)))
    c.restore()


# ===================== S5 patas cansadas + sacos tirados por mãos humanas
@shot(tDono, tBurroOp, GR_COLD, (-0.85, -0.5))
def s05(c, t, u):
    cam = camlerp((720, 1000, 1.55), (720, 980, 1.6), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'barn', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'barn', 'near')
    S.door_panels(c, 1.0)
    tc = on2(t)
    lift = ramp(t, tDono + 1.2, tDono + 3.6)
    kn = 0.35 * (1 - lift) + 0.08 * abs(math.sin(tc * 3))
    bx, by = 720, S.G + 10
    burro(c, bx, by, 0.78, pose=dict(head=16, ears=0.85, eyes=0.5, brow=-0.8, mouth='sad', knees=kn))
    # sacos
    for i, (sx, col) in enumerate(((-50, (190, 160, 110)), (40, (176, 146, 100)))):
        yy = by - 0.78 * 330 - 40 - (700 + i * 60) * ramp(t, tDono + 1.2 + i * 0.25, tDono + 3.8 + i * 0.25)
        p = jag(smooth([(bx + sx - 50, yy + 60), (bx + sx - 56, yy), (bx + sx - 30, yy - 50), (bx + sx + 30, yy - 50), (bx + sx + 56, yy),
                        (bx + sx + 50, yy + 60)]))
        layer(c, p, col, 0.5, tex='fabric', stitch=True, stitch_col=(120, 90, 60))
        ink(c, P([(bx + sx - 26, yy - 44), (bx + sx + 26, yy - 44)], False), (120, 90, 60), 200, 5)
        # mão + manga
        hx, hy = bx + sx, yy - 60 - 260 * (1 - ramp(t, tDono + 0.2, tDono + 1.2))
        layer(c, jag(tp([(hx + 20, hy - 300), (hx + 10, hy - 140), (hx, hy - 20)], 70, 56)), (90, 96, 120), 0.5, tex='fabric')
        layer(c, jag(oval(hx, hy, 32, 26)), (220, 176, 146), 0.4)
    c.restore()


# ===================== S6 close: orelhas caem e sobem uma a uma
@shot(tBurroOp, tB02, GR_COLD, (-0.85, -0.5))
def s06(c, t, u):
    cam = camlerp((860, 760, 2.25), (860, 760, 2.35), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'barn', 'far'); c.restore()
    c.save()
    cam.apply(c, 0.9)
    draw_bg(c, 'barn', 'near')
    S.door_panels(c, 1.0)
    t_op = Wt('opinião.')
    e1 = ramp(t, t_op - 0.2, t_op + 0.25, easeOutBack)
    e2 = ramp(t, t_op + 0.45, t_op + 0.8, easeOutBack)
    det = ramp(t, t_op + 0.6, t_op + 1.0)
    burro(c, 720, S.G + 10, 0.78, pose=dict(head=lerp(14, -4, det), ears=lerp(0.85, 0.05, (e1 + e2) / 2), ear_wig=(e1 - e2) * 40,
                                            eyes=lerp(0.5, 0.15, det), brow=lerp(-0.8, 1, det), mouth='neutral' if det < 0.5 else 'smile',
                                            look=(lerp(-0.3, 0.6, det), 0), breath=breath(t)))
    c.restore()


# ===================== S7 contra-plongée: "Vou para Bremen. Vou ser músico!" (estrada ao nascer do sol)
@shot(tB02, tN03a, GR_DAY, (-0.7, -0.6), trans='fold')
def s07(c, t, u):
    cam = camlerp((560, 820, 1.25), (600, 800, 1.3), ease(u))
    c.save(); cam.apply(c, 0.35); draw_bg(c, 'road', 'far', variant='sunrise'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near', variant='sunrise')
    m = mouth_lvl('b02_burro', t)
    chest = ramp(t, tB02 - 0.1, tB02 + 0.5, easeOutBack)
    wk = ramp(t, EV['b02_burro']['t1'] - 0.2, EV['b02_burro']['t1'] + 0.3)
    tc = on2(t)
    bx = 420 + max(0, t - EV['b02_burro']['t1']) * 160
    burro(c, bx, S.G + 20, 0.95, pose=dict(chest=chest, head=-6 + 3 * math.sin(tc * 5) * (m > 0), ears=0.0, mouth='open' if m else 'smile', m=m,
                                           brow=1, eyes=0.12 if blink(t, 3.1) < 1 else 1, look=(0.6, -0.2), walk=wk > 0.5, step=tc * 0.9,
                                           breath=breath(t)))
    c.restore()
    particles(c, t, 'leaf', 8, 5)


# ===================== S8 travelling: revela o cachorro deitado na cerca
@shot(tN03a, tLatir, GR_DAY, (-0.6, -0.75))
def s08(c, t, u):
    cam = camlerp((360, 900, 1.05), (640, 900, 1.08), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.fence(c, 600, 1400, S.G - 60, seed=4)
    tc = on2(t)
    wk = 1 - ramp(u, 0.65, 0.85)
    bx = lerp(200, 560, ease(clamp(u / 0.85)))
    cachorro(c, 860, S.G - 20, 0.95, pose=dict(lie=1, eyes=0.55, brow=-0.8, breath=2.5 * breath(t, 0.9), head=8, t=t, look=(-0.3, 0.2)))
    burro(c, bx, S.G + 10, 0.85, pose=dict(walk=wk > 0.1, step=tc * 0.9, eyes=blink(t), brow=0.4, look=(0.6, 0.2), head=6 * (1 - wk),
                                           breath=breath(t)))
    c.restore()
    particles(c, t, 'leaf', 8, 6)


# ===================== S9 sobre o ombro do burro: "Ainda sabe latir?"
@shot(tLatir, tLat, GR_DAY, (-0.6, -0.75))
def s09(c, t, u):
    cam = camlerp((760, 1000, 1.7), (770, 1010, 1.75), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.fence(c, 600, 1400, S.G - 60, seed=4)
    cachorro(c, 860, S.G - 20, 0.95, pose=dict(lie=1, eyes=lerp(0.6, 0.35, ramp(u, 0.3, 0.6)), brow=-0.6, breath=2 * breath(t, 0.9), head=8,
                                              t=t, look=(-0.6, -0.6)))
    c.restore()
    # ombro/cabeça do burro em primeiro plano, desfocado
    c.save()
    cam.apply(c, 1.25)
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(9, 9)))
    m = mouth_lvl('burro_latir', t)
    burro(c, 380, S.G + 330, 1.5, pose=dict(head=14, mouth='open' if m else 'smile', m=m, look=(0.6, 0.4), brow=0.3))
    c.restore()
    c.restore()


# ===================== S10 close: latido, orelhas voam 😄
@shot(tLat, tContr, GR_DAY, (-0.6, -0.75))
def s10(c, t, u):
    cam = camlerp((960, 920, 2.2), (960, 930, 2.25), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.fence(c, 600, 1400, S.G - 60, seed=4)
    m = mouth_lvl('sfx_latido', t)
    bark = ramp(t, tLat - 0.05, tLat + 0.12)
    ears = bark * (1 - ramp(t, tLat + 0.6, tLat + 1.3, easeInQuad)) + spring(t, tLat + 1.3, 0.12, 2.5, 5)
    cachorro(c, 860, S.G - 20, 0.95, pose=dict(lie=1 - 0.4 * bark, eyes=0.0 if m else lerp(0.35, 0.15, bark), brow=0.6 * bark, head=-10 * bark,
                                              mouth='open' if m else 'smile', m=max(m, 0.2 * bark), ears=ears, t=t, look=(0.2, -0.3)))
    c.restore()


# ===================== S11 dois: "Está contratado." cachorro levanta e abana o rabo
@shot(tContr, tN03b, GR_DAY, (-0.6, -0.75))
def s11(c, t, u):
    cam = camlerp((680, 900, 1.3), (690, 905, 1.34), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.fence(c, 600, 1400, S.G - 60, seed=4)
    m = mouth_lvl('burro_contratado', t)
    up = ramp(t, EV['burro_contratado']['t1'] - 0.2, EV['burro_contratado']['t1'] + 0.3, easeOutBack)
    burro(c, 560, S.G + 10, 0.85, pose=dict(head=-4, mouth='open' if m else 'smile', m=m, brow=0.8, look=(0.6, 0.3), eyes=blink(t)))
    cachorro(c, 870, S.G - 20, 0.95, pose=dict(lie=1 - up, eyes=0.2, brow=0.4, mouth='tongue' if up > 0.5 else 'smile', tail=up, t=t,
                                              ears=spring(t, EV['burro_contratado']['t1'] + 0.1, 0.25, 2.2, 3.5), look=(-0.5, -0.2)))
    c.restore()


# ===================== S12 muro de pedras: o gato erra o rato 😄
@shot(tN03b, tTal, GR_DAY, (-0.5, -0.8), trans='tear')
def s12(c, t, u):
    tl = t - tN03b
    cam = camlerp((560, 960, 1.15), (580, 960, 1.18), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.stone_wall(c, 300, 1400, S.G - 40, 170, seed=6) if False else c.drawImage(wall_img(), 0, 0)
    tc = on2(t)
    swipe = ramp(tl, 0.8, 1.0, easeOutBack) * (1 - ramp(tl, 1.3, 1.6))
    lick = ramp(tl, 2.0, 2.3) * (0.5 + 0.5 * math.sin(tc * 14)) * (1 - ramp(tl, 3.6, 3.9))
    rx = lerp(1000, 120, ramp(tl, 0.4, 1.6, lambda x: x))
    rato(c, rx, S.G - 210 + 4 * math.sin(tc * 30), 1.0, flip=True, step=tc * 4, t=t)
    gato(c, 720, S.G - 210, 1.05, pose=dict(paw=swipe, lick=lick, head=-10 * swipe + 6 * lick, brow='alarm' if swipe > 0.3 else 'smug',
                                            eyes=0.0 if swipe > 0.3 else (0.9 if lick > 0.1 else 0.45), mouth='neutral', t=t,
                                            look=(-0.6, 0.3) if swipe else (0.3, 0)))
    # burro e cachorro entram pela esquerda
    e = ramp(tl, 1.8, 3.6)
    burro(c, lerp(-300, 230, e), S.G + 30, 0.8, pose=dict(walk=e < 1, step=tc * 0.9, eyes=blink(t), look=(0.6, -0.2), brow=0.3))
    cachorro(c, lerp(-500, 40, e), S.G + 60, 0.75, pose=dict(walk=e < 1, step=tc * 1.3, eyes=0.25, brow=0.2, t=t, tail=0.6))
    c.restore()


_WALL = None


def wall_img():
    global _WALL
    if _WALL is None:
        s = skia.Surface(W + 400, H)
        cc = s.getCanvas()
        S.stone_wall(cc, 300, 1400, S.G - 40, 170, seed=6)
        _WALL = s.makeImageSnapshot()
    return _WALL


# ===================== S13 close gato: "Tenho outros talentos."
@shot(tTal, tN03c, GR_DAY, (-0.5, -0.8))
def s13(c, t, u):
    cam = camlerp((700, 900, 1.9), (705, 900, 1.95), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    c.drawImage(wall_img(), 0, 0)
    m = mouth_lvl('gato_talentos', t)
    chin = ramp(u, 0.0, 0.25, easeOutBack)
    gato(c, 720, S.G - 210, 1.05, pose=dict(chin=chin, head=-6 * chin, brow='smug', eyes=0.55, mouth='open' if m else 'smug', m=m, t=t,
                                            look=(-0.2, -0.3), breath=breath(t)))
    c.restore()
    # cachorro em primeiro plano desfocado olhando para o burro (reação)
    c.save()
    cam.apply(c, 1.3)
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(8, 8)))
    look = ramp(u, 0.55, 0.7)
    cachorro(c, 380, S.G + 140, 1.15, pose=dict(head=-6 - 18 * look, eyes=0.3, brow=0.6 * look, look=(lerp(0.6, -0.8, look), -0.3), t=t))
    c.restore()
    c.restore()


# ===================== S14 contra-plongée: galo na cerca, sopa fumegando ao fundo
@shot(tN03c, tGalo, GR_DAY, (-0.5, -0.8))
def s14(c, t, u):
    cam = camlerp((600, 760, 1.25), (600, 740, 1.32), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 0.7)
    # casinha da fazenda com a panela de sopa na janela
    farm(c, t)
    c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.fence(c, 300, 1100, S.G - 40, seed=8, h=230)
    tc = on2(t)
    galo(c, 640, S.G - 40 - 230 * 0.75 - 14, 1.3, pose=dict(flap=1.0, eye=1, t=t, head=6 * math.sin(tc * 9), tail=4 * math.sin(tc * 7),
                                                           step=tc, beak=0.2))
    gato(c, 260, S.G + 120, 0.9, pose=dict(brow='sus', look=(0.8, -0.8), t=t))
    cachorro(c, 860, S.G + 160, 0.8, flip=True, pose=dict(eyes=0.2, brow=0.4, look=(0.6, -0.8), head=-20, t=t))
    c.restore()


def farm(c, t):
    x, y = 260, S.G - 120
    layer(c, jag(rr(x - 180, y - 260, x + 180, y, 4)), (190, 170, 140), 0.4)
    layer(c, jag(P([(x - 220, y - 250), (x, y - 420), (x + 220, y - 250)])), (150, 70, 56), 0.4, tex='fabric')
    fill(c, rr(x - 60, y - 200, x + 60, y - 100, 4), (90, 70, 60))
    # panela
    layer(c, jag(smooth([(x - 46, y - 130), (x + 46, y - 130), (x + 40, y - 100), (x - 40, y - 100)])), (60, 60, 66), 0.3)
    for i in range(3):
        k = (t * 0.6 + i / 3) % 1
        sx = x - 20 + i * 20 + 10 * math.sin(t * 2 + i)
        sy = y - 140 - k * 160
        c.drawCircle(sx, sy, 14 + k * 20, skia.Paint(AntiAlias=True, Color=skia.Color(255, 255, 255, int(110 * (1 - k))), MaskFilter=blurmf(6)))


# ===================== S15 close galo canta indignado; gato abaixa as orelhas 😄
@shot(tGalo, tN04, GR_DAY, (-0.5, -0.8))
def s15(c, t, u):
    cam = camlerp((640, 760, 1.85), (640, 750, 1.9), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near')
    S.fence(c, 300, 1100, S.G - 40, seed=8, h=230)
    m = env('sfx_galo', t)
    pre = ramp(t, tGalo - 0.4, tGalo)
    galo(c, 640, S.G - 40 - 230 * 0.75 - 14, 1.3, pose=dict(puff=max(pre, 0.6), beak=min(1, m * 1.4), head=-26 * min(1, m * 2 + pre * 0.4),
                                                           eye=1, t=t, flap=0.3 * (m > 0.2)))
    c.restore()
    c.save()
    cam.apply(c, 1.25)
    ear = ramp(t, tGalo - 0.35, tGalo - 0.1)
    gato(c, 380, S.G + 120, 1.05, pose=dict(ears=ear, eyes=0.85 * ear + 0.4 * (1 - ear), brow='sus', mouth='neutral', t=t, look=(0.6, -0.6)))
    c.restore()


# ===================== S16 pôr do sol: os quatro andando, sombras se juntando; luz vira noite
@shot(tN04 - 1.5, tEeles, GR_SUNSET, (0.4, -0.3), trans=None)
def s16(c, t, u):
    tl = t - (tN04 - 1.5)
    cam = camlerp((520, 900, 1.0), (600, 900, 1.04), ease(u))
    c.save(); cam.apply(c, 0.3); draw_bg(c, 'road', 'far', variant='sunset'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'road', 'near', variant='sunset')
    tc = on2(t)
    sil = (40, 26, 30)
    xs = 560 + tl * 60
    gp = dict(walk=1, step=tc * 0.9)
    # sombras longas (para a esquerda, longe do sol à direita? sol à esquerda → sombras à direita)
    for f, dx, sc in ((burro, 0, 0.62), (cachorro, -170, 0.6)):
        c.save()
        c.translate(xs + dx, S.G + 20)
        c.scale(1, -0.25)
        c.skew(2.0, 0)
        f(c, 0, 0, sc, pose=dict(walk=1, step=tc * (0.9 if f is burro else 1.3), t=t), sil=(30, 18, 24), a=120)
        c.restore()
    burro(c, xs, S.G + 20, 0.62, pose=gp, sil=sil)
    cachorro(c, xs - 170, S.G + 30, 0.6, pose=dict(walk=1, step=tc * 1.3, t=t), sil=sil)
    gato_walk(c, xs - 300, S.G + 30, 0.7, step=tc * 1.2, sil=sil, t=t)
    galo(c, xs - 400, S.G + 30, 0.7, pose=dict(walk=1, step=tc * 1.5, march=1, t=t), sil=sil)
    c.restore()


# ===================== S17 floresta noturna: fome e frio
@shot(tEeles, tViram, GR_NIGHT, (0.4, -0.7), trans='iris')
def s17(c, t, u):
    cam = camlerp((500, 900, 1.08), (560, 900, 1.12), ease(u))
    c.save(); cam.apply(c, 0.25); draw_bg(c, 'forest', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'forest', 'near')
    tc = on2(t)
    sh = math.sin(tc * 40)
    burro(c, 640, S.G + 20, 0.78, pose=dict(ears=0.5, eyes=0.45, brow=-0.6, mouth='sad', head=10, breath=breath(t)))
    cachorro(c, 400, S.G + 40, 0.72, pose=dict(lie=0.6, eyes=0.5, brow=-0.8, t=t, look=(0.3, 0.4)))
    gato(c, 860, S.G + 30, 0.78, pose=dict(brow='plot', eyes=0.6, ears=0.4, t=t, tail=10))
    galo(c, 220, S.G + 40, 0.85, pose=dict(eye=0.6, t=t, head=3 * sh, puff=0.3), sil=None)
    c.restore()
    particles(c, t, 'firefly', 14, 7, (0, 300, 1080, 1300))


# ===================== S18 troca de foco: burro -> casa iluminada
@shot(tViram, tLa, GR_NIGHT, (0.4, -0.7))
def s18(c, t, u):
    rf = ramp(u, 0.15, 0.6)
    cam = camlerp((560, 760, 1.25), (600, 700, 1.32), ease(u))
    c.save(); cam.apply(c, 0.25); draw_bg(c, 'forest', 'far')
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(8 * (1 - rf) + 0.1, 8 * (1 - rf) + 0.1)))
    S.tiny_house(c, 700, 900, 1.6)
    c.restore()
    c.restore()
    c.save()
    cam.apply(c, 1.2)
    bl = 0.1 + 10 * rf
    c.saveLayer(None, skia.Paint(ImageFilter=skia.ImageFilters.Blur(bl, bl)))
    burro(c, 260, S.G + 300, 1.1, pose=dict(ears=lerp(0.5, 0.0, rf), eyes=0.12, brow=0.6 * rf, look=(0.8, -0.4), head=-6 * rf, mouth='smile'))
    c.restore()
    c.restore()
    particles(c, t, 'firefly', 10, 8, (0, 300, 1080, 1300))


# ===================== S19 banquete: mão pega o pão, ladrões rindo
@shot(tLa, tPlano, GR_WARM, (0.85, -0.3), trans='fold')
def s19(c, t, u):
    tc = on2(t)
    cam = camlerp((520, 1000, 1.5), (500, 860, 1.12), ease(clamp(u * 1.4)))
    c.save(); cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='lit'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t)
    S.fire(c, t, 960, S.G - 40, 0.9)
    draw_bg(c, 'interior', 'near', variant='lit')
    for i, (kind, x) in enumerate((('largo', 260), ('alto', 520), ('baixo', 780))):
        ladrao(c, x, 1190, 0.95, kind, pose=dict(expr='laugh' if (tc * 2 + i) % 2 < 1.3 else 'neutral', arms='eat' if i == 1 else 'table',
                                                 t=t, lean=3 * math.sin(tc * 4 + i)))
    S.table(c, 60, 1000, 1080)
    # mão pegando pão
    g = ramp(u, 0.0, 0.35)
    bx, by = 380, 1074 - 60 * g
    bread(c, bx, by, 1.0, -8 * g)
    layer(c, jag(tp([(bx - 300 + 200 * g, by - 200 + 120 * g), (bx - 60, by - 60), (bx - 20, by - 20)], 60, 46)), (150, 112, 70), 0.5,
          tex='fabric')
    layer(c, jag(oval(bx - 20, by - 26, 30, 24)), (222, 178, 146), 0.4)
    c.restore()
    particles(c, t, 'dust', 20, 9, (100, 300, 900, 1200))


# ===================== S20 close gato junto à janela: "Precisamos de um plano."
@shot(tPlano, tConc, GR_NIGHT, (0.0, -0.4), trans='iris')
def s20(c, t, u):
    cam = camlerp((420, 720, 1.9), (420, 720, 1.95), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t)
    m = mouth_lvl('gato_plano', t)
    gato(c, 420, 960, 1.15, pose=dict(paw=0.75, brow='plot', eyes=0.5, mouth='open' if m else 'neutral', m=m, t=t, look=(0.6, -0.2),
                                      head=-6))
    c.restore()


# ===================== S21 burro: "Um concerto."  S22 reação do gato 😄
@shot(tConc, EV['burro_concerto']['t1'] + 0.05, GR_NIGHT, (0.0, -0.4))
def s21(c, t, u):
    cam = camlerp((760, 760, 1.9), (760, 760, 1.95), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t)
    m = mouth_lvl('burro_concerto', t)
    up = ramp(t, tConc - 0.2, tConc + 0.2, easeOutBack)
    burro(c, 600, S.G + 10, 0.85, pose=dict(ears=lerp(0.4, -0.05, up), brow=1, eyes=0.05, mouth='open' if m else 'smile', m=m, look=(0.7, -0.2),
                                            head=-6 * up))
    c.restore()


@shot(EV['burro_concerto']['t1'] + 0.05, tN05a + 0.55, GR_NIGHT, (0.0, -0.4))
def s22(c, t, u):
    cam = Cam(420, 720, 2.1)
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t)
    turn = ramp(u, 0.1, 0.3, easeOutBack)
    gato(c, 420, 960, 1.15, pose=dict(brow='sus', head=8 * turn, look=(lerp(0.6, 1.0, turn), 0), mouth='neutral', t=t))
    c.restore()


# ===================== S23 pirâmide subindo (stagger), joelhos do burro dobram
@shot(tN05a + 0.55, tJanela, GR_NIGHT, (0.0, -0.4))
def s23(c, t, u):
    cam = camlerp((560, 820, 1.0), (560, 620, 0.98), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t)
    td = Wt('cachorro', 1, 'n05a')
    tg = Wt('gato', 1, 'n05a')
    tr = Wt('galo.', 1, 'n05a')
    b = dict(dog=ramp(t, td - 0.2, td + 0.5, lambda x: x), cat=ramp(t, tg - 0.2, tg + 0.45, lambda x: x), roo=ramp(t, tr - 0.1, tr + 0.4, lambda x: x))
    stack(c, 560, S.G + 20, 0.92, t, build=b)
    c.restore()


# ===================== S24 interior: sombra-monstro na janela (eco do 1º quadro)
@shot(tJanela, tEos, GR_WARM, (0.85, -0.3))
def s24(c, t, u):
    tc = on2(t)
    cam = camlerp((470, 780, 1.1), (470, 740, 1.22), ease(u))
    c.save(); cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='lit'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t, monster=ramp(u, 0.0, 0.3), mon_scale=1.12)
    S.fire(c, t, 960, S.G - 40, 0.9)
    draw_bg(c, 'interior', 'near', variant='lit')
    S.table(c, 120, 900, 1060)
    c.restore()
    c.save()
    stop = ramp(u, 0.3, 0.5)
    for i, (kind, x) in enumerate((('largo', 150), ('alto', 520), ('baixo', 860))):
        ladrao(c, x, 1640, 1.05, kind, pose=dict(arms='eat' if stop < 0.5 else 'table', t=t * (1 - stop)), sil=(46, 26, 22))
    c.restore()


# ===================== S25 close janela (fora): os quatro cantam
@shot(tEos, EV['concert']['t1'] + 0.1, GR_NIGHT, (0.0, -0.4))
def s25(c, t, u):
    cam = camlerp((580, 540, 1.45), (580, 520, 1.52), ease(u))
    c.save(); cam.apply(c, 0.4); draw_bg(c, 'night_ext', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'night_ext', 'near')
    window_ext_glass(c, S.WIN_EXT, t, 1.2)
    sing = env('concert', t) > 0.05
    stack(c, 560, S.G + 20, 0.92, t, sing=1.0 if sing else 0.0, wob=1.0 if sing else 0.2)
    c.restore()


# ===================== S26a ladrões fogem, cadeira cai, pão voa
@shot(EV['concert']['t1'] + 0.1, tEpelo, GR_WARM, (0.85, -0.3))
def s26(c, t, u):
    tl = t - (EV['concert']['t1'] + 0.1)
    tc = on2(t)
    cam = camlerp((520, 900, 1.12), (540, 900, 1.16), ease(u))
    c.save(); cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='lit'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t)
    S.fire(c, t, 960, S.G - 40, 0.9)
    draw_bg(c, 'interior', 'near', variant='lit')
    S.table(c, 60, 1000, 1080)
    fall = ramp(tl, 0.3, 0.8, easeInQuad)
    S.chair(c, 720, 1420, 0.9, 95 * fall + spring(tl, 0.8, 6, 3, 6))
    for i, (kind, x0) in enumerate((('largo', 300), ('alto', 560), ('baixo', 780))):
        go = ramp(tl, 0.2 + i * 0.25, 3.6 + i * 0.3, lambda x: x)
        x = x0 + go * (1300 - x0 + 200)
        ladrao(c, x, 1420, 0.95, kind, pose=dict(expr='scared', run=tc * 2.4 + i * 0.3, arms='up', lean=12, t=t))
    bt = clamp(tl / 1.6)
    bread(c, 420 + bt * 200, 1060 - math.sin(bt * math.pi) * 300 + bt * 300, 1.0, bt * 360)
    c.restore()


# ===================== S26b os bichos entram e tomam a mesa
@shot(tEpelo, tN06, GR_WARM, (0.85, -0.3))
def s26b(c, t, u):
    tc = on2(t)
    cam = camlerp((700, 980, 1.4), (700, 990, 1.45), ease(u))
    c.save(); cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='lit'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t)
    S.fire(c, t, 960, S.G - 40, 0.9)
    draw_bg(c, 'interior', 'near', variant='lit')
    S.chair(c, 720, 1420, 0.9, 95)
    burro(c, 300, 1390, 0.85, pose=dict(mouth='smile', eyes=blink(t), brow=0.6, look=(0.6, 0.2), breath=breath(t)))
    S.table(c, 300, 1100, 1080)
    grab = ramp(u, 0.25, 0.45, easeOutBack)
    cachorro(c, 620, 1060, 0.7, pose=dict(mouth='tongue' if grab < 0.5 else 'closed', eyes=0.2, brow=0.6, tail=1, t=t))
    if grab > 0.5:
        bread(c, 700, 1000, 0.7, -10)
    galo(c, 860, 1068, 0.8, pose=dict(head=10, eye=0.3, puff=0.6, t=t))
    gato(c, 980, 1070, 0.75, pose=dict(brow='smug', eyes=0.7, t=t, lick=0.5 + 0.5 * math.sin(tc * 10)))
    c.restore()


# ===================== S27 escuro: botas do ladrão entrando
@shot(tN06, tLevou, GR_MOON, (-0.6, -0.5), trans='iris')
def s27(c, t, u):
    tc = on2(t)
    cam = camlerp((700, 1300, 1.7), (760, 1300, 1.75), ease(u))
    c.save(); cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='dark'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t)
    S.fire(c, t, 960, S.G - 40, 0.35, a=160)
    draw_bg(c, 'interior', 'near', variant='dark')
    x = lerp(1250, 700, ease(u))
    ladrao(c, x, 1500, 1.0, 'alto', pose=dict(run=tc * 1.2, arms='table', expr='neutral', lean=-6, t=t))
    # olhos do gato brilhando no escuro
    gl = ramp(u, 0.5, 0.8)
    for ex in (420, 452):
        c.drawCircle(ex, 1310, 26, skia.Paint(AntiAlias=True, Color=skia.Color(230, 230, 120, int(80 * gl)), MaskFilter=blurmf(10)))
        fill(c, oval(ex, 1310, 9, 6 * (1 if blink(t, 2.3) < 1 else 0.1)), (230, 236, 130), 255 * gl)
    c.restore()


# ===================== S28 ping-pong: arranhada, mordida, coice
@shot(tLevou, tJurou, GR_MOON, (-0.6, -0.5))
def s28(c, t, u):
    tc = on2(t)
    c.save()
    if t < tMord:  # arranhada
        cam = Cam(520, 1000, 1.6)
        cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='dark'); c.restore(); c.save(); cam.apply(c, 1.0)
        draw_bg(c, 'interior', 'near', variant='dark')
        sw = ramp(t, tArr - 0.05, tArr + 0.1, easeOutBack) * (1 - ramp(t, tArr + 0.4, tArr + 0.6))
        ladrao(c, 760, 1500, 1.0, 'alto', pose=dict(arms='point', expr='scared' if sw > 0.3 else 'neutral', lean=-10 * sw, t=t))
        gato(c, 460, 1450, 1.0, pose=dict(paw=sw, brow='alarm', eyes=0.0, mouth='open', m=0.6 * sw, t=t, ears=0.8))
        if sw > 0.4:
            for k in range(3):
                ink(c, P([(600 + k * 18, 1130 + k * 8), (660 + k * 18, 1210 + k * 8)], False), (240, 240, 200), 220, 4)
    elif t < tCoice:  # mordida
        cam = Cam(600, 1250, 1.7)
        cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='dark'); c.restore(); c.save(); cam.apply(c, 1.0)
        draw_bg(c, 'interior', 'near', variant='dark')
        bite = ramp(t, tMord - 0.05, tMord + 0.12, easeOutBack)
        ladrao(c, 820 + 30 * bite, 1500, 1.0, 'alto', pose=dict(arms='up', expr='scared', lean=10 * bite, run=None, t=t))
        cachorro(c, 520 + 40 * bite, 1450, 1.05, pose=dict(mouth='open', m=0.5, ears=0.3, brow=0.6, eyes=0.1, head=-6, t=t, tail=1))
    else:  # coice
        cam = Cam(560, 1050, 1.15)
        cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='dark'); c.restore(); c.save(); cam.apply(c, 1.0)
        draw_bg(c, 'interior', 'near', variant='dark')
        k = ramp(t, tCoice - 0.08, tCoice + 0.1, easeOutBack)
        fly = ramp(t, tCoice + 0.05, tCoice + 0.9)
        c.save()
        c.translate(420, 1400)
        c.rotate(-10 * k)
        c.translate(-420, -1400)
        burro(c, 420, 1400, 0.8, flip=True, pose=dict(head=6, eyes=0.6, brow=0.8, mouth='smile', tail=30 * k))
        c.restore()
        ladrao(c, 760 + fly * 500, 1500 - math.sin(fly * math.pi) * 300, 1.0, 'alto', pose=dict(arms='up', expr='scared', lean=30 * fly, t=t))
        galo(c, 200, 700, 0.8, pose=dict(beak=0.8 * (fly > 0.1), head=-20, puff=1, t=t))
    c.restore()


# ===================== S29 floresta: "a casa está cheia de monstros!" (clímax)
@shot(tJurou, tN07, GR_NIGHT, (0.4, -0.7), trans='tear')
def s29(c, t, u):
    tc = on2(t)
    cam = camlerp((540, 900, 1.15), (560, 860, 1.25), ease(u))
    c.save(); cam.apply(c, 0.25); draw_bg(c, 'forest', 'far'); c.restore()
    c.save()
    cam.apply(c, 1.0)
    draw_bg(c, 'forest', 'near')
    # galho com coruja indiferente
    layer(c, jag(tp([(1100, 420), (900, 470), (760, 500)], 30, 12)), (30, 36, 50), 0.4)
    coruja(c, 860, 478, 0.9, t=t)
    ladrao(c, 620, S.G + 30, 0.85, 'alto', pose=dict(expr='scared', arms='point', lean=-6 + 3 * math.sin(tc * 20), t=t))
    for i, (kind, x) in enumerate((('largo', 280), ('baixo', 900))):
        sc = ramp(u, 0.3 + i * 0.1, 0.5 + i * 0.1)
        ladrao(c, x, S.G + 50, 0.8, kind, pose=dict(expr='scared' if sc > 0.5 else 'neutral', arms='up' if sc > 0.5 else 'table', t=t))
    c.restore()
    particles(c, t, 'firefly', 8, 9, (0, 300, 1080, 1300))


# ===================== S30 patas juntas junto à lareira
@shot(tN07, tMas7, GR_WARM, (0.85, -0.3), trans='fold')
def s30(c, t, u):
    cam = camlerp((560, 1240, 2.0), (560, 1230, 2.05), ease(u))
    cozy(c, t, cam, sleep=True)


def cozy(c, t, cam, sleep=True, shadows=0.0):
    c.save(); cam.apply(c, 1.0); draw_bg(c, 'interior', 'far', variant='cozy')
    # sombras na parede: viram uma só
    if shadows > 0:
        c.save()
        c.translate(80 * (1 - shadows), 0)
        stack(c, 420, 1150, 0.55, 0, sil=(70, 44, 34), a=int(110 * shadows))
        c.restore()
    c.restore()
    c.save()
    cam.apply(c, 1.0)
    window_glass(c, S.WIN_INT, t)
    S.fire(c, t, 960, S.G - 40, 1.0)
    draw_bg(c, 'interior', 'near', variant='cozy')
    br = breath(t, 0.18)
    burro(c, 420, S.G + 210, 0.8, pose=dict(lie=1.0, eyes=0.95 if sleep else 0.4, mouth='smile', ears=0.3, head=16, breath=br))
    cachorro(c, 640, S.G + 260, 0.75, pose=dict(lie=1, eyes=1.0, mouth='smile', brow=0.3, t=t, breath=br))
    gato(c, 820, S.G + 250, 0.7, pose=dict(eyes=1.0, mouth='smug', brow='happy', t=t, tail=-20, breath=br))
    rato(c, 900, S.G + 260, 0.8, flip=True, sleep=True, t=t)
    galo(c, 220, S.G + 220, 0.75, pose=dict(head=20, eye=0, t=t, puff=0.3))
    c.restore()
    particles(c, t, 'ember', 12, 3, (880, 900, 1060, 1200))


# ===================== S31 recuo: sombras viram uma só; até a casa na floresta
@shot(tMas7, T_END, GR_WARM, (0.85, -0.3))
def s31(c, t, u):
    pull = ease(clamp(u / 0.75))
    if u < 0.78:
        cam = camlerp((560, 1180, 1.7), (520, 900, 0.95), pull)
        cozy(c, t, cam, shadows=ramp(u, 0.2, 0.6))
    else:
        v = ramp(u, 0.78, 1.0)
        cam = camlerp((540, 860, 1.6), (540, 860, 1.0), v)
        c.save(); cam.apply(c, 0.25); draw_bg(c, 'forest', 'far'); c.restore()
        c.save(); cam.apply(c, 1.0); draw_bg(c, 'forest', 'near')
        S.tiny_house(c, 540, S.G - 20, 2.4)
        c.restore()
        particles(c, t, 'firefly', 12, 11, (0, 300, 1080, 1300))


SHOTS.sort(key=lambda s: s['t0'])
# fecha buracos: cada plano vai até o início do próximo
for i in range(len(SHOTS) - 1):
    SHOTS[i]['t1'] = SHOTS[i + 1]['t0']
SHOTS[-1]['t1'] = T_END


# ---------------------------------------------------------------- composição
def render_shot(sh, t):
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(C((20, 22, 30)))
    set_light(*sh['light'])
    u = clamp((t - sh['t0']) / max(0.01, sh['t1'] - sh['t0']))
    sh['f'](c, t, u)
    return surf.makeImageSnapshot()


def transition(c, img_a, img_b, kind, v):
    """v: 0..1"""
    c.drawImage(img_a, 0, 0)
    if kind == 'iris':
        if v < 0.5:
            r = lerp(1300, 0, ease(v * 2))
            c.save(); c.clipPath(circ(500, 800, r), skia.ClipOp.kDifference, True)
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=C((12, 14, 20)))); c.restore()
        else:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=C((12, 14, 20))))
            r = lerp(0, 1300, ease((v - 0.5) * 2))
            c.save(); c.clipPath(circ(500, 800, r), skia.ClipOp.kIntersect, True); c.drawImage(img_b, 0, 0); c.restore()
    elif kind == 'tear':
        x = lerp(W + 80, -80, ease(v))
        pts = [(x + 18 * math.sin(y * 0.05) + 10 * math.sin(y * 0.13), y) for y in range(-20, H + 40, 30)]
        p = P(pts + [(W + 100, H + 40), (W + 100, -20)])
        c.save(); c.clipPath(p, skia.ClipOp.kIntersect, True); c.drawImage(img_b, 0, 0); c.restore()
        c.save(); c.translate(-8, 0)
        c.drawPath(P(pts + [(pts[-1][0] + 16, H + 40), (pts[0][0] + 16, -20)][::-1] if False else pts, False),
                   skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=14, Color=C((240, 232, 214))))
        c.restore()
    elif kind == 'fold':  # cenário novo se ergue dobrando da base (pop-up)
        e = easeOutBack(v, 1.1)
        c.save()
        c.translate(0, H)
        c.scale(1, max(0.001, e))
        c.translate(0, -H)
        c.drawImage(img_b, 0, 0)
        c.restore()
        c.drawRect(skia.Rect(0, H - H * e - 30, W, H - H * e), skia.Paint(Color=skia.Color(0, 0, 0, int(80 * (1 - v))), MaskFilter=blurmf(12)))
    elif kind == 'page':  # página vira levando o cenário antigo
        e = ease(v)
        c.drawImage(img_b, 0, 0)
        c.save()
        c.translate(0, 0)
        c.scale(max(0.001, 1 - e), 1)
        c.drawImage(img_a, 0, 0)
        c.restore()
        xe = W * (1 - e)
        c.drawRect(skia.Rect(xe, 0, xe + 60, H), skia.Paint(Color=skia.Color(0, 0, 0, int(90 * math.sin(e * math.pi))), MaskFilter=blurmf(20)))
    else:
        c.drawImage(img_b, 0, 0)


TR_DUR = 0.55


def frame(t, idx):
    # plano atual
    cur = None
    for i, sh in enumerate(SHOTS):
        if sh['t0'] <= t < sh['t1'] or (i == len(SHOTS) - 1 and t >= sh['t0']):
            cur = i
            break
    sh = SHOTS[cur]
    trans = sh['trans']
    if trans and cur > 0 and t < sh['t0'] + TR_DUR:
        a = render_shot(SHOTS[cur - 1], t)
        b = render_shot(sh, t)
        surf = skia.Surface(W, H)
        cc = surf.getCanvas()
        transition(cc, a, b, trans, (t - sh['t0']) / TR_DUR)
        img = surf.makeImageSnapshot()
    else:
        img = render_shot(sh, t)
    # grade
    g = dict(sh['grade'] or {})
    fl = 1 + 0.012 * math.sin(t * 5.3) + 0.008 * math.sin(t * 11.7)
    g['bright'] = g.get('bright', 1.0) * fl
    # s16: a luz do pôr do sol migra para noite durante o plano
    if sh['f'].__name__ == 's16':
        u = clamp((t - tN04) / max(0.1, sh['t1'] - tN04))
        g = dict(sat=lerp(1.05, 0.85, u), bright=lerp(1.0, 0.72, u) * fl, tint=(lerp(1.08, 0.9, u), lerp(0.97, 0.96, u), lerp(0.9, 1.12, u)),
                 contrast=1.05)
    out = skia.Surface(W, H)
    c = out.getCanvas()
    c.drawImage(img, 0, 0, skia.SamplingOptions(), skia.Paint(ColorFilter=skia.ColorFilters.Matrix(grade_matrix(**g))))
    # vinheta (mais leve na capa)
    vignette(c, 90 if t < tO else STYLE['vignette_alpha'])
    caption(c, t)
    # grão (renovado a cada 2 quadros)
    gi = GRAIN[(idx // 2) % len(GRAIN)]
    c.save(); c.scale(2, 2)
    c.drawImage(gi, 0, 0, skia.SamplingOptions(), skia.Paint(Alphaf=STYLE['grain_alpha'] / 255, BlendMode=skia.BlendMode.kOverlay))
    c.restore()
    # fade final
    if t > T_END - 0.6:
        c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(8, 8, 12, int(255 * ramp(t, T_END - 0.6, T_END)))))
    return out


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for ts in sys.argv[2:]:
            t = float(ts)
            f = frame(t, int(t * FPS))
            f.makeImageSnapshot().save(f'/tmp/claude-0/-home-user-editvideo/d5421e05-e9f7-5b9c-8d37-360e387ea0df/scratchpad/still_{t:06.2f}.png')
    elif mode == 'range':
        a, b = int(sys.argv[2]), int(sys.argv[3])
        out = sys.stdout.buffer
        for i in range(a, b):
            f = frame(i / FPS, i)
            out.write(f.makeImageSnapshot().tobytes())
    elif mode == 'shots':
        for sh in SHOTS:
            print(f"{sh['f'].__name__:6s} {sh['t0']:7.2f} {sh['t1']:7.2f} {sh['trans']}")
