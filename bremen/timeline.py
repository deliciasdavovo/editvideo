"""Monta a trilha de voz (sem aceleração; pausas aparadas) e a linha do tempo de palavras e legendas."""
import json, re, numpy as np, wave
from audio_proc import load, tighten

D = '/home/user/editvideo/bremen/audio/'
SR = 24000
TXT = {
    'b01': "Três ladrões fugiram apavorados de um monstro de quatro cabeças. O monstro era um burro, um cachorro, um gato e um galo. "
           "Todos velhos demais para servir. Tudo começou quando o burro foi mandado embora. O dono decidiu que ele já não servia "
           "para nada. O burro tinha outra opinião.",
    'b02_burro': "Vou para Bremen. Vou ser músico!",
    'n03a': "Na estrada, achou um cachorro velho demais para caçar.",
    'burro_latir': "Ainda sabe latir?",
    'burro_contratado': "Está contratado.",
    'n03b': "Depois, um gato que não pegava ratos.",
    'gato_talentos': "Tenho outros talentos.",
    'n03c': "E um galo que ia virar sopa amanhã.",
    'n04': "Mas a noite caiu, e eles tinham fome e frio. Viram uma casa iluminada. Lá dentro, três ladrões se fartavam.",
    'gato_plano': "Precisamos de um plano.",
    'burro_concerto': "Um concerto.",
    'n05a': "O burro embaixo, o cachorro em cima, depois o gato e o galo. Na janela, a sombra virou um monstro. E os quatro cantaram.",
    'n05b': "Foi a primeira apresentação da banda. E, pelo desespero da plateia, provavelmente a última.",
    'n06': "Um ladrão voltou no escuro. Levou uma arranhada, uma mordida e um coice. E jurou aos outros que a casa estava cheia de monstros.",
    'n07': "Os quatro nunca chegaram a Bremen. Mas encontraram um lugar onde envelhecer não significava deixar de pertencer.",
}
SPEAKER = {'b02_burro': 'BURRO', 'burro_latir': 'BURRO', 'burro_contratado': 'BURRO', 'burro_concerto': 'BURRO',
           'gato_talentos': 'GATO', 'gato_plano': 'GATO'}
# legendas: trechos montados à mão (3–7 palavras)
CHUNKS = {
    'b01': ["Três ladrões fugiram apavorados", "de um monstro de quatro cabeças.", "O monstro era um burro,", "um cachorro, um gato e um galo.",
            "Todos velhos demais para servir.", "Tudo começou quando o burro", "foi mandado embora.", "O dono decidiu que ele",
            "já não servia para nada.", "O burro tinha outra opinião."],
    'b02_burro': ["Vou para Bremen.", "Vou ser músico!"],
    'n03a': ["Na estrada, achou um cachorro", "velho demais para caçar."],
    'burro_latir': ["Ainda sabe latir?"], 'burro_contratado': ["Está contratado."],
    'n03b': ["Depois, um gato", "que não pegava ratos."],
    'gato_talentos': ["Tenho outros talentos."],
    'n03c': ["E um galo que ia", "virar sopa amanhã."],
    'n04': ["Mas a noite caiu,", "e eles tinham fome e frio.", "Viram uma casa iluminada.", "Lá dentro, três ladrões", "se fartavam."],
    'gato_plano': ["Precisamos de um plano."], 'burro_concerto': ["Um concerto."],
    'n05a': ["O burro embaixo,", "o cachorro em cima,", "depois o gato e o galo.", "Na janela, a sombra", "virou um monstro.",
             "E os quatro cantaram."],
    'n05b': ["Foi a primeira apresentação", "da banda.", "E, pelo desespero da plateia,", "provavelmente a última."],
    'n06': ["Um ladrão voltou no escuro.", "Levou uma arranhada,", "uma mordida e um coice.", "E jurou aos outros",
            "que a casa estava cheia", "de monstros."],
    'n07': ["Os quatro nunca", "chegaram a Bremen.", "Mas encontraram um lugar", "onde envelhecer não significava",
            "deixar de pertencer."],
}

SEQ = [('b01a', 0.15), ('b01b', 0.7), ('b02_burro', 0.4), ('n03a', 0.55), ('burro_latir', 0.35), ('sfx_latido', 0.25),
       ('burro_contratado', 0.3), ('n03b', 0.6), ('gato_talentos', 0.35), ('n03c', 0.55), ('sfx_galo', 0.2), ('n04', 1.7),
       ('gato_plano', 0.45), ('burro_concerto', 0.35), ('n05a', 1.0), ('concert', 0.15), ('n05b', 0.35), ('n06', 0.75), ('n07', 0.8)]
TAIL = 0.6


def syl(w):
    return max(1, len(re.findall(r'[aeiouáéíóúâêôãõà]+', w.lower()))) + (0.6 if re.search(r'[.,!?]$', w) else 0)


def align(words, segs):
    """distribui palavras na fala (sem os silêncios) proporcional às sílabas; pontuação tende a cair nos silêncios"""
    tot = sum(b - a for a, b in segs)
    wts = [syl(w) for w in words]
    W = sum(wts)
    out = []
    acc = 0
    def at(sp):  # tempo real dado tempo de fala acumulado
        for a, b in segs:
            if sp <= b - a:
                return a + sp
            sp -= b - a
        return segs[-1][1]
    for w, k in zip(words, wts):
        s0 = at(acc / W * tot + 1e-4)
        acc += k
        e0 = at(acc / W * tot - 1e-4)
        out.append([w, s0, e0])
    # puxa inícios de palavra após pontuação para o próximo segmento de fala
    for i in range(1, len(out)):
        if re.search(r'[.,!?]$', out[i - 1][0]):
            for a, b in segs:
                if a >= out[i - 1][1] and a <= out[i][1] + 0.35 and a > out[i - 1][2] - 0.25:
                    out[i][1] = max(out[i][1], a) if a - out[i][1] < 0.4 else out[i][1]
                    break
    return out


def build():
    clips = {}
    for k in list(TXT) + ['sfx_latido', 'sfx_galo', 'sfx_zurro', 'sfx_miado']:
        x, sr = load(D + ('b01_narr' if k == 'b01' else k) + '.wav')
        y, segs = tighten(x, sr)
        clips[k] = (y, segs)
    # divide b01 no fim de "servir."
    y, segs = clips['b01']
    words = TXT['b01'].split()
    al = align(words, segs)
    iw = words.index('servir.')
    tcut = al[iw][2]
    # silêncio mais próximo
    gaps = [(segs[i][1], segs[i + 1][0]) for i in range(len(segs) - 1)]
    g = min(gaps, key=lambda g: abs((g[0] + g[1]) / 2 - tcut))
    cut = int(((g[0] + g[1]) / 2) * SR)
    clips['b01a'] = (y[:cut], [s for s in segs if s[1] <= cut / SR])
    clips['b01b'] = (y[cut:], [(a - cut / SR, b - cut / SR) for a, b in segs if a >= cut / SR])
    # concerto: os quatro juntos
    parts = [clips[k][0] for k in ('sfx_zurro', 'sfx_latido', 'sfx_miado', 'sfx_galo')]
    L = max(len(p) for p in parts) + int(0.3 * SR)
    con = np.zeros(L, np.float32)
    for i, p in enumerate(parts):
        o = int(i * 0.09 * SR)
        con[o:o + len(p)] += p[:L - o] * 0.62
    clips['concert'] = (con, [(0, L / SR)])
    t = 0.0
    voice = []
    events = []
    for k, gap in SEQ:
        voice.append(np.zeros(int(gap * SR), np.float32))
        t += gap
        y, segs = clips[k]
        events.append(dict(key=k, t0=t, t1=t + len(y) / SR, segs=[(t + a, t + b) for a, b in segs]))
        voice.append(y)
        t += len(y) / SR
    voice.append(np.zeros(int(TAIL * SR), np.float32))
    v = np.concatenate(voice)
    with wave.open(D + 'voice.wav', 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(v, -1, 1) * 32767).astype(np.int16).tobytes())
    # palavras + legendas
    words_all = []
    caps = []
    txtmap = dict(TXT)
    words_b01 = TXT['b01'].split()
    txtmap['b01a'] = ' '.join(words_b01[:iw + 1])
    txtmap['b01b'] = ' '.join(words_b01[iw + 1:])
    chmap = dict(CHUNKS)
    ch = CHUNKS['b01']
    ci = ch.index('Todos velhos demais para servir.')
    chmap['b01a'] = ch[:ci + 1]
    chmap['b01b'] = ch[ci + 1:]
    for e in events:
        k = e['key']
        if k not in txtmap:
            continue
        ws = txtmap[k].split()
        segs = e['segs']
        al = align(ws, segs)
        for w, a, b in al:
            words_all.append(dict(w=w, t0=a, t1=b, clip=k))
        # legendas
        idx = 0
        chs = chmap[k]
        for j, chunk in enumerate(chs):
            n = len(chunk.split())
            t0 = al[idx][1]
            t1 = al[idx + n - 1][2]
            caps.append(dict(text=chunk, t0=t0, t1=t1, speaker=SPEAKER.get(k), clip=k))
            idx += n
        assert idx == len(ws), (k, idx, len(ws))
    # legenda fica até a próxima (ou +0.6 s)
    for i, cp in enumerate(caps):
        nxt = caps[i + 1]['t0'] if i + 1 < len(caps) else cp['t1'] + 0.8
        cp['t1'] = min(nxt, cp['t1'] + 0.7) if nxt - cp['t1'] > 0.05 else nxt
    # envelope de cada fala de personagem (para boca)
    env = {}
    for e in events:
        if e['key'] in SPEAKER or e['key'].startswith('sfx') or e['key'] == 'concert':
            y, _ = clips[e['key']]
            hop = SR // 30
            r = [float(np.sqrt(np.mean(y[i:i + hop] ** 2))) for i in range(0, len(y), hop)]
            mx = max(r) or 1
            env[e['key']] = [v / mx for v in r]
    T = len(v) / SR
    json.dump(dict(T=T, events=events, words=words_all, caps=caps, env=env), open(D + 'timeline.json', 'w'), ensure_ascii=False, indent=0)
    return T, events, caps


if __name__ == '__main__':
    T, ev, caps = build()
    print('T', round(T, 2))
    for e in ev:
        print(f"{e['key']:18s} {e['t0']:6.2f} {e['t1']:6.2f}")
    words = sum(len(TXT[k].split()) for k in TXT)
    print('palavras', words, 'w/s', round(words / T, 2))
