"""Narração do roteiro da Laís (v3): falas por cena + respiros de ação."""
import json, os, re, wave
import numpy as np
from montar_narracao import load, segments, syl

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, 'audio3')
# (arquivo, quem, texto, respiro ANTES, cena)
CLIPS = [
    ('c01_rival', 'rival', 'Você veio apresentar isso ao imperador?', 1.0, 1),
    ('c02_narr', 'narrador', 'O imperador estava velho e decidiu escolher seu sucessor de uma maneira bastante curiosa.', 1.6, 2),
    ('c02_imp', 'imperador', 'Cada criança receberá uma semente.', 0.45, 2),
    ('c03_imp', 'imperador', 'Daqui a um ano, retornem com aquilo que conseguirem cultivar.', 1.3, 3),
    ('c04_narr', 'narrador', 'Ping tinha um talento especial. Quase tudo que plantava florescia. Quase tudo...', 1.1, 4),
    ('c05_ping', 'ping', 'O que você está precisando?', 3.6, 5),
    ('c06_ping', 'ping', 'Pai, não posso aparecer lá de mãos vazias.', 3.2, 6),
    ('c06_pai', 'pai', 'Mas você fez o seu melhor, não fez?', 0.45, 6),
    ('c07_pai', 'pai', 'Então leve o resultado do seu esforço.', 1.4, 7),
    ('c08_imp', 'imperador', 'E a sua flor?', 3.6, 8),
    ('c08_ping', 'ping', 'Majestade, eu tentei. Mas a semente não cresceu.', 0.9, 8),
    ('c09_imp', 'imperador', 'Todas as sementes que entreguei haviam sido fervidas. Nenhuma poderia germinar.', 1.6, 9),
    ('c10_imp', 'imperador', 'Enfim encontrei alguém digno de governar.', 3.0, 10),
    ('c10_narr', 'narrador', 'Entre tantas flores, foi um pote vazio que revelou a verdade.', 0.9, 10),
]
TAIL = 1.2


def main():
    sr = 24000; parts = []; words = []; blocks = []; t = 0.0
    for name, who, txt, pre, scene in CLIPS:
        x, sr_ = load(os.path.join(A, name + '.wav')); assert sr_ == sr
        segs = segments(os.path.join(A, name + '.wav'))
        parts.append(np.zeros(int(pre * sr), np.float32)); t += pre
        b0 = t
        toks = txt.split(); S = [syl(w) for w in toks]
        seg_len = [b - a for a, b in segs]; tot = sum(seg_len)
        # palavras distribuídas pelos trechos, cortando na pontuação mais próxima da proporção de tempo
        assign, si, acc = [], 0, 0
        cum = np.cumsum(seg_len) / tot * sum(S)
        for i, w in enumerate(toks):
            assign.append(si); acc += S[i]
            if si < len(segs) - 1 and re.search(r'[,.;?!]$', w) and acc >= cum[si] - 3:
                si += 1
        pad = 0.03
        for k, (a, b) in enumerate(segs):
            seg = x[int(max(0, a - pad) * sr):int(min(len(x) / sr, b + pad) * sr)]
            idx = [i for i, s_ in enumerate(assign) if s_ == k]; dur = len(seg) / sr
            if idx:
                ss = sum(S[i] for i in idx); u = t + pad
                for i in idx:
                    d = (dur - 2 * pad) * S[i] / ss
                    words.append(dict(w=toks[i], s=round(u, 3), e=round(u + d, 3), who=who, block=name, scene=scene)); u += d
            parts.append(seg); t += dur
            if k < len(segs) - 1:
                g = segs[k + 1][0] - b
                p = min(g, 0.42) if g >= 0.3 else g
                parts.append(np.zeros(int(p * sr), np.float32)); t += p
        blocks.append(dict(name=name, who=who, s=round(b0, 3), e=round(t, 3), text=txt, scene=scene))
    parts.append(np.zeros(int(TAIL * sr), np.float32)); t += TAIL
    y = np.concatenate(parts)
    w = wave.open(os.path.join(A, 'narracao3.wav'), 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(np.clip(y, -32768, 32767).astype(np.int16).tobytes()); w.close()
    json.dump(dict(duration=round(t, 3), blocks=blocks, words=words), open(os.path.join(HERE, 'timeline3.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'duração {t:.2f}s, {len(words)} palavras')
    for b in blocks:
        print(f"{b['s']:6.2f}-{b['e']:6.2f} cena {b['scene']:2d} {b['who']:9s} {b['text'][:55]}")


if __name__ == '__main__':
    main()
