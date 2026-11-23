import skia, paperlib as pl, characters as ch
from paperlib import C, text

W, H = 2400, 3060
surf = skia.Surface(W, H)
c = surf.getCanvas()
pl.paper_bg(c, W, H)
INK = (52, 38, 34)


def wrap(s, x, y, width, size, font='lorai', col=INK, lh=1.3):
    f = skia.Font(pl.FONT[font], size)
    words, line = s.split(), ''
    for w in words:
        t = (line + ' ' + w).strip()
        if f.measureText(t) > width and line:
            text(c, line, x, y, size, font, col, align='left'); y += size * lh; line = w
        else:
            line = t
    if line:
        text(c, line, x, y, size, font, col, align='left'); y += size * lh
    return y


def shape_icon(kind, x, y, r=18, col=INK):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4, Color=C(col))
    if kind == 'circulo':
        c.drawCircle(x, y, r, p)
    elif kind == 'quadrado':
        c.drawRect(skia.Rect(x - r, y - r, x + r, y + r), p)
    elif kind == 'retangulo':
        c.drawRect(skia.Rect(x - r * 0.55, y - r * 1.2, x + r * 0.55, y + r * 1.2), p)
    elif kind == 'triangulo':
        c.drawPath(pl.poly([(x, y - r * 1.1), (x + r, y + r * 0.8), (x - r, y + r * 0.8)]), p)
    elif kind == 'ret+tri':
        c.drawRect(skia.Rect(x - r * 0.55 - 12, y - r * 1.2, x + r * 0.55 - 12, y + r * 1.2), p)
        c.drawPath(pl.poly([(x + 6, y - r), (x + 30, y - r), (x + 18, y + r * 1.1)]), p)


def swatches(cols, x, y, s=34):
    for i, col in enumerate(cols):
        pl.layer(c, pl.rr(x + i * (s + 10), y, x + i * (s + 10) + s, y + s, 4), col, depth=0.05, rim=False)


text(c, 'O Pote Vazio', 80, 110, 76, 'lf900', INK, align='left')
text(c, 'folha de personagens v3 · roteiro da Laís · paper style 2.0', 80, 160, 30, 'lorai', INK, align='left')

BASE = 1190
SC = 2.1
cols = [
    dict(fn=ch.ping, x=330, sc=SC, name='Ping', shape='circulo',
         pal=[ch.PING['tunic'], ch.PING['skin'], ch.PING['hair'], ch.PING['pants'], ch.PING['sash']],
         ficha=['Quem é: o menino que faz tudo florir.', 'Quer: ser escolhido pelo imperador.',
                'Defeito: o orgulho do dom vira vergonha quando a semente falha.',
                'Jeito: rápido e saltitante; encolhe quando sente vergonha. Gesto: abraça o pote contra o peito.'],
         why='Círculo, ~2,6 cabeças, bochechas redondas, cabelo desalinhado. Verde-sálvia, linho cru e terra: a roupa liga Ping ao cultivo, não à riqueza.'),
    dict(fn=ch.pai, x=900, sc=SC, name='O pai', shape='quadrado',
         pal=[ch.PAI['tunic'], ch.PAI['skin'], ch.PAI['pants'], ch.PAI['straw'], ch.PAI['rope']],
         ficha=['Quem é: lavrador calado e firme.', 'Quer: que o filho não tenha vergonha da verdade.',
                'Contradição: fala pouco, mas a única frase dele muda a história.',
                'Jeito: lento e pesado. Gesto: a mão no ombro do filho.'],
         why='Quadrado, ombros largos, mãos de trabalhador. Cinza-verde e terra. Demonstra afeto por pequenos gestos, não por discursos.'),
    dict(fn=ch.imperador, x=1500, sc=SC, name='O imperador', shape='ret+tri',
         pal=[ch.IMP['robe'], ch.IMP['panel'], ch.IMP['beard'], ch.IMP['skin'], ch.IMP['sash']],
         ficha=['Quem é: velho imperador sem herdeiro.', 'Quer: um sucessor honesto.',
                'Contradição: parece severo (testa franzida), mas é justo; esconde o teste.',
                'Jeito: lento e solene. Gesto: mãos escondidas nas mangas; alisa a barba.'],
         why='Trapézio e linhas verticais, 4,6 cabeças, pálpebras pesadas e barba fina. Vermelho-terra e dourado. Nem cruel nem bondoso demais: o público não lê a intenção dele.'),
    dict(fn=ch.rival, x=2080, sc=SC, name='Menino rival', shape='triangulo',
         pal=[ch.RIVAL['tunic'], ch.RIVAL['red'], ch.RIVAL['vase'], ch.RIVAL['dark']],
         ficha=['Quem é: o vizinho que nunca perde a chance de se mostrar.', 'Quer: ser admirado.', 'Defeito: vaidade.',
                'Jeito: queixo erguido, passo de dono. Gesto: exibe o vaso que mal consegue carregar.'],
         why='Anguloso e alongado: orgulho. Ocre e vermelho, as cores mais quentes e chamativas da fila. O humor nasce do vaso grande demais para ele.'),
]
for col in cols:
    c.save(); c.translate(col['x'], BASE); c.scale(col['sc'], col['sc']); pl.SCALE[0] = col['sc']
    col['fn'](c); c.restore()
pl.SCALE[0] = 1.0

# silhuetas (teste)
text(c, 'teste da silhueta', 2080, 2850, 26, 'lf700', INK)
sil = skia.Surface(W, H)
sc2 = sil.getCanvas()
for fn, x, s in [(ch.ping, 1900, 0.34), (ch.pai, 1990, 0.34), (ch.imperador, 2090, 0.34), (ch.rival, 2200, 0.34)]:
    sc2.save(); sc2.translate(x, 3030); sc2.scale(s, s); pl.SCALE[0] = s; fn(sc2); sc2.restore()
pl.SCALE[0] = 1.0
img = sil.makeImageSnapshot()
c.saveLayer(None, None)
c.drawImage(img, 0, 0)
c.drawPaint(skia.Paint(Color=C((24, 20, 24)), BlendMode=skia.BlendMode.kSrcIn))
c.restore()

# textos das fichas
for col in cols:
    x0 = col['x'] - 250
    y = BASE + 80
    shape_icon(col['shape'], x0 + 22, y - 18)
    text(c, col['name'], x0 + 62, y, 50, 'lf900', INK, align='left')
    swatches(col['pal'], x0, y + 24)
    y += 104
    for line in col['ficha']:
        y = wrap(line, x0, y, 500, 25, 'lf700', INK, 1.25) + 4
    y += 6
    wrap(col['why'], x0, y, 500, 24, 'lorai', (90, 70, 60), 1.28)

# expressões
EY = 2020
text(c, 'Expressões e poses que o roteiro usa', 80, 1790, 44, 'lf900', INK, align='left')
heads = [(ch.ping_head, 'ping', e, n) for e, n in [('neutro', 'neutro'), ('encanto', 'encanto'), ('concentrado', 'regando'),
                                                   ('decepcionado', 'decepção'), ('vergonha', 'vergonha *'),
                                                   ('choro', 'choro'), ('coragem', 'coragem'), ('alegria', 'alegria')]]
heads += [(ch.imp_head, 'imp', e, n) for e, n in [('sereno', 'sereno'), ('testa_franzida', 'testa franzida *'),
                                                 ('pergunta', 'pergunta'), ('sorriso', 'sorriso')]]
heads += [(ch.pai_head, 'pai', e, n) for e, n in [('terno', 'terno'), ('apoio', 'apoio')]]
heads += [(ch.rival_head, 'rival', e, n) for e, n in [('deboche', 'deboche *'), ('orgulho', 'orgulho'), ('susto', 'susto'), ('vergonha', 'vergonha')]]
CENTER = {'ping': (0, -262), 'imp': (0, -392), 'pai': (0, -340), 'rival': (0, -330)}
SCH = {'ping': 1.15, 'imp': 0.95, 'pai': 1.05, 'bird': 2.2}
SCH = {'ping': 1.5, 'imp': 1.2, 'pai': 1.3, 'rival': 1.3}
rows = [[h for h in heads if h[1] == 'ping'], [h for h in heads if h[1] != 'ping']]
ROWY = [2080, 2560]
group_x = {}
for r, row in enumerate(rows):
    step = (W - 160) / len(row)
    for i, (fn, who, e, n) in enumerate(row):
        x = 80 + step * (i + 0.5)
        group_x.setdefault(who, []).append((x, r))
        s = SCH[who]
        c.save(); c.translate(x, ROWY[r]); c.scale(s, s); c.translate(-CENTER[who][0], -CENTER[who][1]); pl.SCALE[0] = s
        fn(c, e); c.restore(); pl.SCALE[0] = 1.0
        text(c, n, x, ROWY[r] + (250 if who == 'imp' else 160), 27, 'lf700', INK)
names = {'ping': 'Ping', 'imp': 'Imperador', 'pai': 'Pai', 'rival': 'Menino rival'}
for who, xs in group_x.items():
    r = xs[0][1]; x0, x1 = xs[0][0], xs[-1][0]
    yy = ROWY[r] - (200 if r == 0 else 240)
    text(c, names[who], (x0 + x1) / 2, yy, 32, 'lf900', (150, 70, 50))
    c.drawLine(x0 - 60, yy + 14, x1 + 60, yy + 14, skia.Paint(AntiAlias=True, Color=C((150, 70, 50), 0.6), StrokeWidth=2))
text(c, '* a expressão que mostra o defeito ou a contradição do personagem', 80, H - 50, 24, 'lorai', (90, 70, 60), align='left')
surf.makeImageSnapshot().save('/home/user/editvideo/pote_vazio/folha_personagens.png')
print('ok')
