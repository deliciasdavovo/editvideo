"""Planos do roteiro da Laís (v3). Reaproveita os cenários de shots.py com a linha do tempo nova."""
import json, math, os, random, wave
import numpy as np
import skia
import paperlib as pl
import characters as ch
import scenes as sc
import shots
from shots import (ease, back_out, cam, cached, img, draw_char, palace_crowd, front_pots, outside_parade, ping_back,
                   window_room, s_plaza, s_seed, s_empty_soil, s_palace_wide, s_emperor_walk)
from scenes import W, H

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline3.json')))
# a linha do tempo nova passa a valer em shots.py (boca, legendas)
shots.TL = TL; shots.WORDS = TL['words']; shots.DUR = TL['duration']
_w = wave.open(os.path.join(HERE, 'audio3', 'narracao3.wav'))
shots._sr = _w.getframerate()
shots._X = np.frombuffer(_w.readframes(_w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
WORDS = shots.WORDS; DUR = shots.DUR
W_ = shots.W_


def face_of(t, who, base=None, nod=0.0):
    v, op = shots.viseme(t, who)
    blink = 1.0 if int(t * 10) % 37 == 0 else 0.0
    if who == 'imperador':
        f = shots.imp_face(t); return f
    if who == 'pai':
        mk = None
        if v:
            mk = {'A': 'o', 'O': 'o', 'U': 'o', 'E': 'smile', 'M': 'gentle'}[v] if op > 0.15 else 'gentle'
        return dict(mouth_kind=mk, blink=blink)
    if who == 'rival':
        return dict(mouth_kind=(v if v else base), blink=blink)
    return dict(mouth_kind=v or base, mouth_open=op, nod=nod, blink=blink)


def block(name):
    for b in TL['blocks']:
        if b['name'] == name:
            return b
    raise KeyError(name)


# ================================================= cenas
def c1_crowd(c, u, d, t):
    """Capa: Ping esconde o pote no meio das flores; o menino rival exibe o vaso enorme."""
    c.save(); cam(c, u, d, 1.04, 1.1, cx=500, cy=860)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=2)
    sc.beam(c, 360, -40, 1400, 200, 460, a=0.35)
    draw_char(c, ch.ping, 330, 1340, 2.25, expr='vergonha', pose='hide_pot', face=dict(blink=0.0))
    c.save(); c.translate(760, 1350); c.rotate(-3 * math.sin(t * 2.2)); c.translate(-760, -1350)
    draw_char(c, ch.rival, 760, 1350, 2.1, expr='orgulho', pose='carry', strain=1 + math.sin(t * 3))
    c.restore()
    c.restore()
    img(c, cached('front_pots', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)))


def c1_rival_talk(c, u, d, t):
    """O rival se inclina e debocha; Ping abaixa a cabeça."""
    c.save(); cam(c, u, d, 1.22, 1.28, cx=560, cy=700)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=5)
    talking = shots.speaking(t, 'rival') is not None
    nod = 6 * ease((t - block('c01_rival')['e']) / 0.5)
    draw_char(c, ch.ping, 330, 1420, 2.4, expr='vergonha', pose='hide_pot', face=dict(nod=nod, blink=0.0))
    c.save(); c.translate(790, 1420); c.rotate(-7); c.translate(-790, -1420)
    draw_char(c, ch.rival, 790, 1420, 2.25, expr='deboche', pose='carry', face=face_of(t, 'rival', 'smirk'), strain=1.5)
    c.restore()
    c.restore()


def year_card(c, u):
    """Cartão 'Um ano antes' (cai e sai)."""
    if u > 2.4:
        return
    k = ease(u / 0.45) if u < 1.9 else 1 - ease((u - 1.9) / 0.5)
    pl.SCALE[0] = 1
    c.save(); c.translate(500, -120 + 520 * k); c.rotate(3 * math.sin(u * 5) * math.exp(-u * 2))
    pl.layer(c, pl.rr(-230, -60, 230, 60, 8), (244, 234, 212), depth=0.5)
    pl.text(c, 'Um ano antes', 0, 18, 60, 'lf900', (52, 38, 34))
    c.restore()


def c2_plaza(c, u, d, t):
    s_plaza(c, u, d, t)
    year_card(c, u)


def c2_emperor(c, u, d, t):
    c.save(); cam(c, u, d, 1.1, 1.16, cx=520, cy=700)
    img(c, cached('plaza', lambda c: sc.plaza_bg(c)), blur=6)
    draw_char(c, ch.imperador, 520, 1650, 2.5, expr='sereno', pose='sleeves', face=face_of(t, 'imperador'))
    c.restore()


def c3_emperor_close(c, u, d, t):
    """Sobre o ombro do Ping: o imperador fala baixo, entregando a semente."""
    c.save(); cam(c, u, d, 1.14, 1.2, cx=600, cy=640)
    img(c, cached('plaza', lambda c: sc.plaza_bg(c)), blur=7)
    c.save(); c.rotate(5, 620, 1700)
    draw_char(c, ch.imperador, 620, 1700, 2.6, expr='sereno', pose='beard', face=face_of(t, 'imperador'))
    c.restore()
    c.restore()
    sc.blurred(c, lambda c: ping_back(c, 230, 2060, 3.3), 7)


def c4_prepare(c, u, d, t):
    """Ping prepara a terra com cuidado (talento: tudo à volta floresce)."""
    c.save(); cam(c, u, d, 1.08, 1.13, cx=520, cy=820)
    img(c, cached('room_prim', lambda c: window_room(c, 'primavera', 0)))
    sc.beam(c, 640, 260, 1500, 500, 800, a=0.2)
    # plantinhas que já floresceram no parapeito (o talento dele)
    for i, x in enumerate((360, 930)):
        g = back_out((u - 0.4 - 0.5 * i) / 0.5)
        if g > 0.01:
            c.save(); c.translate(x, 960); c.scale(g, g); pl.SCALE[0] = g
            sc.leaf(c, 0, 0, -120, 60); sc.leaf(c, 0, 0, -60, 60)
            sc.peony(c, 0, -80, 40, (220, 170, 90), 0.2, i)
            c.restore(); pl.SCALE[0] = 1
    draw_char(c, ch.ping, 300, 1500, 2.6, expr='concentrado', pose='down', face=dict(nod=2 * math.sin(t * 4)))
    c.restore()


def c5_seasons(c, u, d, t):
    seasons = ['verao', 'outono', 'inverno']
    seg = min(2, int(u / (d / 3)))
    c.save(); cam(c, u, d, 1.12, 1.12, cx=600, cy=760)
    img(c, cached('room_' + seasons[seg], lambda c: window_room(c, seasons[seg], 0)))
    c.restore()
    for k in range(3):
        sc.dust(c, 300, 260, 1000, 960, n=10, t=t, seed=20 + seg, a=0.4)


def c5_listen(c, u, d, t):
    """Ping encosta o ouvido no vaso: 'O que você está precisando?' ... nada."""
    c.save(); cam(c, u, d, 1.18, 1.26, cx=520, cy=840)
    img(c, cached('room_inv2', lambda c: window_room(c, 'inverno', 0, pot_x=-500)), blur=4)
    pl.SCALE[0] = 1
    # pote grande em primeiro plano, sobre a mesa
    pl.layer(c, pl.rr(-40, 1300, W + 40, 1420, 10), (128, 86, 54), depth=0.4)
    lean = ease(u / 0.6)
    c.save(); c.translate(440, 1700); c.rotate(14 * lean); c.translate(-440, -1700)
    expr = 'concentrado' if shots.speaking(t, 'ping') else 'decepcionado'
    draw_char(c, ch.ping, 440, 1700, 3.0, expr=expr, pose='down', face=face_of(t, 'ping', 'flat_down'))
    c.restore()
    c.save(); c.translate(800, 1330); c.scale(4.6, 4.6); pl.SCALE[0] = 4.6
    ch.pot(c, 0, 0, 1.0); c.restore(); pl.SCALE[0] = 1
    c.restore()


def c6_parade(c, u, d, t):
    c.save(); cam(c, u, d, 1.0, 1.05, cx=520, cy=800)
    pl.STYLE['light'] = (-0.75, -0.66)
    img(c, cached('open_room', lambda c: sc.house_bg(c)))
    sc.window(c, 400, 200, 1060, 860, outside=lambda c: (c.save(), c.translate(-160 * ease(u / d), 0), outside_parade(c), c.restore()))
    sc.beam(c, 640, 520, 1600, 420, 760, a=0.22)
    draw_char(c, ch.ping, 360, 1600, 3.0, expr='vergonha', pose='hide_pot', face=face_of(t, 'ping', 'wobble'))
    pl.STYLE['light'] = (-0.55, -0.83)
    c.restore()


def c6_pai(c, u, d, t):
    """Pai, em plano médio, responde com calma (sobre o ombro do Ping)."""
    c.save(); cam(c, u, d, 1.12, 1.16, cx=600, cy=700)
    img(c, cached('room_prim2', lambda c: sc.house_bg(c)), blur=5)
    draw_char(c, ch.pai, 620, 1720, 2.7, expr='terno', pose='rest', face=face_of(t, 'pai'))
    c.restore()
    sc.blurred(c, lambda c: ping_back(c, 220, 2080, 3.3), 7)


def c7_give(c, u, d, t):
    """O pai entrega o pote ao Ping."""
    c.save(); cam(c, u, d, 1.08, 1.12, cx=560, cy=780)
    img(c, cached('room_prim2', lambda c: sc.house_bg(c)), blur=3)
    sc.beam(c, 300, 0, 1500, 300, 600, a=0.18)
    got = ease((u - 0.8) / 0.8)
    draw_char(c, ch.ping, 420, 1560, 2.7, expr='coragem' if got > 0.5 else 'choro', pose='hold_pot' if got > 0.5 else 'down')
    c.save(); c.translate(820, 1580); c.scale(-1, 1); c.translate(-820, -1580)
    draw_char(c, ch.pai, 820, 1580, 2.7, expr='apoio', pose='apoio', face=face_of(t, 'pai'))
    c.restore()
    if got <= 0.5:   # pote nas mãos do pai, descendo até o Ping
        c.save(); c.translate(640 - 120 * got * 2, 1100 + 60 * got * 2); c.scale(2.7, 2.7); pl.SCALE[0] = 2.7
        ch.pot(c, 0, 0, 1.0); c.restore(); pl.SCALE[0] = 1
    c.restore()


def c7_walk(c, u, d, t):
    """Ping respira fundo e segue para o palácio."""
    c.save(); cam(c, u, d, 1.06, 1.1, cx=520, cy=800)
    img(c, cached('plaza', lambda c: sc.plaza_bg(c)))
    k = ease(u / d)
    s_ = 1.5 - 0.5 * k
    x = 420 + 80 * k; y = 1500 - 360 * k
    bob = 6 * abs(math.sin(t * 6))
    draw_char(c, ch.ping, x, y - bob, s_, expr='coragem', pose='hold_pot')
    c.restore()


def c8_asks(c, u, d, t):
    c.save(); cam(c, u, d, 1.14, 1.2, cx=540, cy=620)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=6)
    sc.beam(c, 560, -60, 1500, 200, 500, a=0.35)
    c.save(); c.rotate(4, 560, 1700)
    draw_char(c, ch.imperador, 560, 1700, 2.7, expr='testa_franzida', pose='sleeves', face=face_of(t, 'imperador'))
    c.restore()
    c.restore()


def c8_answer(c, u, d, t):
    import pilot
    c.save(); cam(c, u, d, 1.08, 1.13, cx=520, cy=760)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=6)
    sc.beam(c, 560, -60, 1500, 180, 520, a=0.5)
    draw_char(c, ch.ping, 560, 1500, 3.15, expr='choro', pose='hold_pot', face=face_of(t, 'ping', 'wobble'), squeeze=4 * ease((u - 2.0) / 0.3))
    sc.dust(c, 400, 0, 760, 1400, n=60, t=t, seed=3, a=0.6)
    c.restore()
    img(c, pilot.SH, blur=1.5 + 9 * ease(u / 0.5))


def c9_reveal(c, u, d, t):
    """O imperador sorri pela primeira vez e revela."""
    c.save(); cam(c, u, d, 1.16, 1.24, cx=540, cy=600)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=6)
    sc.beam(c, 540, -60, 1500, 200, 500, a=0.4)
    draw_char(c, ch.imperador, 640, 1720, 2.8, expr='sorriso' if u > 0.3 else 'sereno', pose='beard', face=face_of(t, 'imperador'))
    c.restore()
    sc.blurred(c, lambda c: ping_back(c, 170, 2080, 3.2), 7)


def c9_hide(c, u, d, t):
    """As outras crianças escondem os vasos (o rival tenta esconder o dele, grande demais)."""
    g = ease(u / 1.0) * 0.7
    c.save(); cam(c, u, d, 1.04, 1.08, cx=520, cy=840)
    gi = int(g * 8) / 8
    img(c, cached(f'palace_h{gi}', lambda c: palace_crowd(c, gray=gi, lowered=gi > 0.3)), blur=2)
    # rival tentando esconder o vaso atrás das costas (não cabe)
    c.save(); c.translate(560, 1400); c.scale(2.3, 2.3); pl.SCALE[0] = 2.3
    ch.big_vase(c, 30, -40, 0.72, seed=7)
    c.restore(); pl.SCALE[0] = 1
    draw_char(c, ch.rival, 560, 1400, 2.3, expr='vergonha' if u > 0.5 else 'susto', pose='hide')
    c.restore()


def c10_kneel(c, u, d, t):
    """O imperador se ajoelha: os dois na mesma altura."""
    c.save(); cam(c, u, d, 1.12, 1.18, cx=520, cy=760)
    img(c, cached('palace', lambda c: palace_crowd(c)), blur=5)
    sc.beam(c, 520, -60, 1500, 260, 620, a=0.45)
    kneel = ease(u / 1.0)
    draw_char(c, ch.imperador, 720, 1760 + 110 * kneel, 2.4, expr='sorriso', pose='sleeves', face=face_of(t, 'imperador'))
    draw_char(c, ch.ping, 330, 1560, 2.5, expr='coragem' if u < d - 1.2 else 'alegria', pose='hold_pot')
    # mão do imperador no ombro do Ping
    if kneel > 0.6:
        P = ch.IMP; pl.SCALE[0] = 1
        sl = sc.smooth([(700, 1180), (560, 1060), (470, 1040), (470, 1090), (600, 1220)], tension=0.4)
        pl.layer(c, sl, P['robe'], depth=0.25)
        pl.layer(c, pl.ell(455, 1060, 30, 24), P['skin'], depth=0.12)
    c.restore()
    img(c, cached('front_pots', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)))


def c10_end(c, u, d, t):
    """Plano final: entre tantas flores, o pote vazio."""
    c.save(); cam(c, u, d, 1.0, 1.06, cx=520, cy=880)
    img(c, cached('palace', lambda c: palace_crowd(c)))
    c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=pl.C((255, 220, 160), 0.1)))
    sc.beam(c, 470, -40, 1340, 220, 520, a=0.5)
    draw_char(c, ch.imperador, 770, 1330, 1.7, expr='sorriso', pose='sleeves')
    draw_char(c, ch.ping, 430, 1290, 2.0, expr='alegria', pose='hold_pot')
    sc.dust(c, 300, 80, 760, 1280, n=60, t=t, seed=9)
    c.restore()
    img(c, cached('front_pots', lambda c: sc.blurred(c, lambda c: front_pots(c, (40, 270, 740, 990)), 9)))


def build():
    b = {x['name']: x for x in TL['blocks']}
    A = [
        (0.0, c1_crowd, 'C1 o único pote vazio', ''),
        (b['c01_rival']['s'] - 0.05, c1_rival_talk, 'C1 o rival debocha', ''),
        (b['c01_rival']['e'] + 0.9, c2_plaza, 'C2 um ano antes: o imperador', 'page'),
        (b['c02_imp']['s'] - 0.15, c2_emperor, 'C2 "cada criança receberá..."', ''),
        (b['c02_imp']['e'] + 0.4, s_seed, 'C3 a semente nas mãos de Ping', ''),
        (b['c03_imp']['s'] + 0.6, c3_emperor_close, 'C3 "daqui a um ano..."', ''),
        (b['c04_narr']['s'] - 0.3, c4_prepare, 'C4 Ping prepara a terra', 'sheet'),
        (W_('quase', 2) - 0.2, s_empty_soil, 'C4 "quase tudo..."', ''),
        (b['c04_narr']['e'] + 0.4, c5_seasons, 'C5 os meses passam', 'iris'),
        (b['c05_ping']['s'] - 0.5, c5_listen, 'C5 o ouvido no vaso', ''),
        (b['c06_ping']['s'] - 0.6, c6_parade, 'C6 a vergonha', 'tear_r'),
        (b['c06_pai']['s'] - 0.1, c6_pai, 'C6 o pai responde', ''),
        (b['c07_pai']['s'] - 0.5, c7_give, 'C7 o pai entrega o pote', ''),
        (b['c07_pai']['e'] + 0.5, c7_walk, 'C7 rumo ao palácio', 'popup'),
        (b['c08_imp']['s'] - 1.8, s_emperor_walk, 'C8 o imperador passa sem sorrir', 'tear_l'),
        (b['c08_imp']['s'] - 0.1, c8_asks, 'C8 "e a sua flor?"', ''),
        (b['c08_ping']['s'] - 0.25, c8_answer, 'C8 a verdade', ''),
        (b['c09_imp']['s'] - 0.45, c9_reveal, 'C9 a revelação', ''),
        (b['c09_imp']['e'] + 0.2, c9_hide, 'C9 as crianças escondem os vasos', ''),
        (b['c10_imp']['s'] - 0.6, c10_kneel, 'C10 o imperador se ajoelha', ''),
        (b['c10_narr']['s'] - 0.2, c10_end, 'C10 o pote vazio', ''),
    ]
    out = []
    for i, (s0, fn, label, trans) in enumerate(A):
        e0 = A[i + 1][0] if i + 1 < len(A) else DUR
        out.append(dict(s=max(0.0, s0), e=e0, fn=fn, label=label, trans=trans))
    return out


SHOTS = build()
shots.SHOTS = SHOTS
