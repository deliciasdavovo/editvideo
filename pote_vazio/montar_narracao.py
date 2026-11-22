"""Monta a narração completa (pausas da regra 1.6) e a linha do tempo das palavras."""
import json, re, subprocess, wave, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'audio')

# (arquivo, quem fala, texto, pausa ANTES do bloco)
BLOCKS = [
    ('narr_b1b2_v2', 'narrador', 'Cem crianças trouxeram flores lindas ao imperador, e ele não sorriu para nenhuma. Só sorriu para um menino que chorava com um vaso vazio. Esse é o fim da história de Ping. Um ano antes, tudo que Ping plantava florescia. O imperador era velho, sem filhos, e amava flores. Por isso, deu uma semente a cada criança.', 0.15),
    ('imp_b2_v2', 'imperador', 'Quem me trouxer a flor mais bonita em um ano será o próximo imperador.', 0.4),
    ('narr_b3', 'narrador', 'Ping plantou e regou todo dia. Nada nasceu. Trocou a terra. Nada. Passou para um vaso maior. Nada.', 0.55),
    ('narr_b4a', 'narrador', 'Na primavera, as crianças passaram com flores enormes. Ping teve vergonha.', 0.55),
    ('ping_b4', 'ping', 'Pai, eu não posso levar um vaso vazio.', 0.35),
    ('narr_b4b', 'narrador', 'Mas o pai disse que Ping fez o seu melhor, e isso bastava.', 0.38),
    ('narr_b5', 'narrador', 'Então Ping levou o vaso vazio ao palácio. O imperador passou pelas flores de testa franzida, e parou em Ping.', 0.55),
    ('imp_b5', 'imperador', 'Por que você trouxe um vaso vazio?', 0.35),
    ('ping_b5', 'ping', 'Eu cuidei da sua semente todo dia, mas ela não nasceu.', 0.4),
    ('imp_b6', 'imperador', 'Eu cozinhei todas as sementes. Nenhuma podia nascer.', 0.75),
    ('narr_b6', 'narrador', 'As outras flores vinham de sementes trocadas. Só Ping teve coragem de trazer a verdade.', 0.45),
    ('narr_b7', 'narrador', 'O menino que fazia tudo florir virou imperador com um vaso sem nenhuma flor.', 0.5),
]
TAIL = 0.45
# pausas internas especiais: (bloco, fim do trecho aprox.) -> pausa
SPECIAL = {('narr_b1b2_v2', 12.86): 0.75}


def load(p):
    w = wave.open(p); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32), sr


def segments(p, d=0.18):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-af', f'silencedetect=n=-40dB:d={d}', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    ev = [(m.group(1), float(m.group(2))) for m in re.finditer(r'silence_(start|end): ([0-9.]+)', out)]
    x, sr = load(p); dur = len(x) / sr; segs = []; cur = 0.0
    for k, t in ev:
        if k == 'start':
            if t > cur + 0.04:
                segs.append([cur, t])
        else:
            cur = t
    if cur < dur - 0.05:
        segs.append([cur, dur])
    return segs


def syl(w):
    return max(1, len(re.findall(r'[aeiouáéíóúâêôãõà]+', w.lower())))


def main():
    sr = 24000
    parts, words, blocks = [], [], []
    t = 0.0
    for name, who, txt, pre in BLOCKS:
        x, sr_ = load(os.path.join(A, name + '.wav'))
        assert sr_ == sr, (name, sr_)
        segs = segments(os.path.join(A, name + '.wav'))
        parts.append(np.zeros(int(pre * sr), np.float32)); t += pre
        b0 = t
        toks = txt.split()
        S = [syl(w) for w in toks]
        seg_len = [b - a for a, b in segs]
        tot_len, tot_syl = sum(seg_len), sum(S)
        # distribui palavras pelos trechos (proporcional à duração), respeitando pontuação como corte preferido
        assign, si, acc = [], 0, 0.0
        cum_target = np.cumsum(seg_len) / tot_len * tot_syl
        for i, w in enumerate(toks):
            assign.append(si)
            acc += S[i]
            if si < len(segs) - 1 and acc >= cum_target[si] - 0.5 * S[i] and re.search(r'[,.;?!]$', w):
                si += 1
            elif si < len(segs) - 1 and acc >= cum_target[si] + 2.5:
                si += 1
        # caso sobrem trechos sem palavra, funde-os ao anterior
        pad = 0.03
        for k, (a, b) in enumerate(segs):
            seg_audio = x[int(max(0, a - pad) * sr):int(min(len(x) / sr, b + pad) * sr)]
            seg_start = t
            idx = [i for i, s_ in enumerate(assign) if s_ == k]
            dur = len(seg_audio) / sr
            if idx:
                ssum = sum(S[i] for i in idx); u = seg_start + pad
                for i in idx:
                    d = (dur - 2 * pad) * S[i] / ssum
                    words.append(dict(w=toks[i], s=round(u, 3), e=round(u + d, 3), who=who, block=name)); u += d
            parts.append(seg_audio); t += dur
            if k < len(segs) - 1:
                g = segs[k + 1][0] - b
                p = 0.38 if g >= 0.5 else (0.3 if g >= 0.3 else 0.2)
                for (bn, et), sp in SPECIAL.items():
                    if bn == name and abs(b - et) < 0.35:
                        p = sp
                parts.append(np.zeros(int(p * sr), np.float32)); t += p
        blocks.append(dict(name=name, who=who, s=round(b0, 3), e=round(t, 3), text=txt))
    parts.append(np.zeros(int(TAIL * sr), np.float32)); t += TAIL
    y = np.concatenate(parts)
    w = wave.open(os.path.join(A, 'narracao.wav'), 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); w.close()
    # aceleração máxima permitida (1,03) para caber em 90 s
    AT = 1.03
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', os.path.join(A, 'narracao.wav'), '-af', f'atempo={AT}',
                    os.path.join(A, 'narracao_final.wav')], check=True)
    t /= AT
    for d_ in words + blocks:
        d_['s'] = round(d_['s'] / AT, 3); d_['e'] = round(d_['e'] / AT, 3)
    json.dump(dict(duration=round(t, 3), blocks=blocks, words=words), open(os.path.join(HERE, 'timeline.json'), 'w'),
              ensure_ascii=False, indent=1)
    nw = len(words)
    print(f'duração {t:.2f}s, {nw} palavras, {nw / t:.2f} palavras/s')
    for b in blocks:
        print(f"{b['s']:6.2f}-{b['e']:6.2f} {b['who']:9s} {b['text'][:50]}")


if __name__ == '__main__':
    main()
