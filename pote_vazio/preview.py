import skia, paperlib as pl, scenes as sc, shots
TW, TH = 288, 512
cols = 5
n = len(shots.SHOTS)
rows = (n + cols - 1) // cols
S = skia.Surface(cols * (TW + 24) + 24, rows * (TH + 90) + 110)
C = S.getCanvas(); C.drawPaint(skia.Paint(Color=skia.Color(28, 26, 30)))
pl.text(C, 'O Pote Vazio · prévia dos planos (zonas do TikTok em vermelho)', 24, 60, 34, 'lf900', (240, 230, 214), align='left')
for i, sh in enumerate(shots.SHOTS):
    d = sh['e'] - sh['s']; u = d * 0.6; t = sh['s'] + u
    surf = skia.Surface(sc.W, sc.H); c = surf.getCanvas()
    sh['fn'](c, u, d, t)
    sc.finish(c, t, vig=130)
    sc.danger_zones(c)
    im = surf.makeImageSnapshot()
    x = 24 + (i % cols) * (TW + 24); y = 100 + (i // cols) * (TH + 90)
    C.drawImageRect(im, skia.Rect(x, y, x + TW, y + TH), skia.SamplingOptions(skia.FilterMode.kLinear))
    lab = sh['label'].replace('😄', '(gag)')
    pl.text(C, f"{i+1:02d} · {sh['s']:.1f}–{sh['e']:.1f}s", x, y + TH + 30, 22, 'lf900', (236, 160, 96), align='left')
    pl.text(C, lab[:34], x, y + TH + 58, 19, 'lf700', (230, 222, 206), align='left')
S.makeImageSnapshot().save('frames/previa_planos.png')
print('ok')
