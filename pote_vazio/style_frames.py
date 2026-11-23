import random, skia
import paperlib as pl
import characters as ch
import scenes as sc
from scenes import W, H

OUT = '/home/user/editvideo/pote_vazio/frames/'
import os; os.makedirs(OUT, exist_ok=True)


def draw_char(c, fn, x, y, s, **kw):
    c.save(); c.translate(x, y); c.scale(s, s); pl.SCALE[0] = s
    fn(c, **kw)
    c.restore(); pl.SCALE[0] = 1.0


def row_of_kids(c, y, s, xs, gray=0.0, seed=0, lowered=False):
    for i, x in enumerate(xs):
        sd = seed + i * 7
        lean = (-58 if i % 2 else 58)
        c.save(); c.translate(x, y); c.scale(s, s); pl.SCALE[0] = s
        sc.child(c, 0, 0, 1.0, sd, gray, part='body')
        sc.flower_pot(c, 0, -40 if not lowered else -20, 1.0, sd, gray, big=1.9 if not lowered else 1.3, lean=lean)
        sc.child(c, 0, 0, 1.0, sd, gray, part='head', look_down=lowered)
        c.restore(); pl.SCALE[0] = 1.0


def front_pots(c, xs, gray=0.0, s=2.0, base=1935):
    for x in xs:
        c.save(); c.translate(x, base); c.scale(s, s); pl.SCALE[0] = s
        sc.flower_pot(c, 0, 0, 1.0, int(x) % 13 + 2, gray, big=1.3)
        c.restore(); pl.SCALE[0] = 1.0


BACK_XS = [10, 120, 230, 340, 690, 800, 910, 1020]
MID_XS = [-10, 140, 280, 800, 950, 1090]


def palace_crowd(c, gray=0.0, lowered=False):
    sc.blurred(c, lambda c: (sc.palace_bg(c, gray=gray), sc.pillar(c, 120, 100, 780, 86, gray=gray, seed=1),
                             sc.pillar(c, 960, 100, 780, 86, gray=gray, seed=3)), 3)
    sc.blurred(c, lambda c: row_of_kids(c, 900, 0.66, BACK_XS, gray=gray, seed=1, lowered=lowered), 3)
    sc.blurred(c, lambda c: row_of_kids(c, 1090, 0.9, MID_XS, gray=gray, seed=30, lowered=lowered), 1.4)


def frame_cover(t=0.0, gray=0.0, dz=False, cap=True, name='sf1_capa'):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    sc.grade(c, sat=1.08, warm=0.35, bright=1.04, contrast=1.08)
    palace_crowd(c)
    sc.beam(c, 480, -40, 1340, 200, 460, a=0.5)
    c.save(); c.rotate(-5, 770, 1210)
    draw_char(c, ch.imperador, 770, 1210, 1.68, expr='sorriso', pose='beard')
    c.restore()
    draw_char(c, ch.ping, 450, 1300, 2.15, expr='choro', pose='hold_pot')
    sc.dust(c, 330, 80, 640, 1280, n=70, t=t, seed=3)
    sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)
    c.restore()  # grade
    if cap:
        sc.caption(c, ['Cem crianças trouxeram flores', 'lindas ao imperador,'])
    sc.finish(c, t, vig=120)
    if dz:
        sc.danger_zones(c)
    img = surf.makeImageSnapshot()
    img.save(OUT + name + '.png')
    return img


def outside_parade(c):
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Shader=skia.GradientShader.MakeLinear(
        [skia.Point(0, 250), skia.Point(0, 950)], [pl.C((190, 220, 236)), pl.C((236, 226, 190))])))
    pl.layer(c, sc.smooth([(-50, 760), (300, 700), (700, 730), (1100, 690), (1100, 1100), (-50, 1100)], tension=0.4), (130, 170, 100), depth=0.1)
    pl.layer(c, pl.rr(-50, 820, 1150, 1100, 1), (206, 180, 136), depth=0.05, shadow=False)
    sc.blurred(c, lambda c: row_of_kids(c, 905, 1.0, [560, 790, 1010], seed=50, gray=0.0), 1.2)


def frame_central(t=0.0, dz=False, name='sf2_vergonha'):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    pl.STYLE['light'] = (-0.75, -0.66)
    sc.grade(c, sat=0.92, warm=0.1, bright=0.96, contrast=1.05)
    sc.house_bg(c)
    sc.window(c, 400, 200, 1060, 860, outside=outside_parade)
    sc.beam(c, 640, 520, 1600, 420, 760, a=0.22)
    draw_char(c, ch.ping, 360, 1600, 3.0, expr='vergonha', pose='hide_pot')
    sc.dust(c, 420, 500, 1000, 1350, n=45, t=t, seed=5, a=0.5)
    c.restore()
    sc.caption(c, ['Na primavera, as crianças', 'passaram com flores enormes.'])
    sc.finish(c, t, vig=170)
    pl.STYLE['light'] = (-0.55, -0.83)
    if dz:
        sc.danger_zones(c)
    img = surf.makeImageSnapshot(); img.save(OUT + name + '.png'); return img


def frame_climax(t=0.0, dz=False, name='sf3_climax'):
    surf = skia.Surface(W, H); c = surf.getCanvas()
    g = 0.88
    sc.grade(c, sat=1.0, warm=0.2, bright=0.92, contrast=1.08)
    palace_crowd(c, gray=g, lowered=True)
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=pl.C((14, 18, 26), 0.45)))
    sc.beam(c, 430, -40, 1290, 170, 440, a=0.62)
    pl.flat(c, pl.ell(430, 1262, 210, 46), (255, 226, 160), 0.35, blur=20)
    c.save(); c.rotate(-5, 770, 1240)
    draw_char(c, ch.imperador, 770, 1240, 1.7, expr='sereno', pose='sleeves')
    c.restore()
    draw_char(c, ch.ping, 430, 1262, 1.95, expr='coragem', pose='hold_pot')
    sc.dust(c, 330, 80, 610, 1250, n=60, t=t, seed=8)
    sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990), gray=g), 9)
    c.restore()
    sc.caption(c, ['Só Ping teve coragem', 'de trazer a verdade.'])
    sc.finish(c, t, vig=190)
    if dz:
        sc.danger_zones(c)
    img = surf.makeImageSnapshot(); img.save(OUT + name + '.png'); return img


if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['1', '2', '3']
    if '1' in which:
        img = frame_cover()
        frame_cover(cap=False, name='capa_sem_legenda')
        skia.Image.open(OUT + 'capa_sem_legenda.png').resize(180, 320).save(OUT + 'capa_mini_180x320.png')
    if '2' in which:
        frame_central()
    if '3' in which:
        frame_climax()
    print('ok')
