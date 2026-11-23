import subprocess,re,numpy as np,wave,sys
def load(p):
    w=wave.open(p); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32); return x,sr
def speech(p,d=0.18):
    out=subprocess.run(['ffmpeg','-hide_banner','-i',p,'-af',f'silencedetect=n=-40dB:d={d}','-f','null','-'],capture_output=True,text=True).stderr
    ev=[(m.group(1),float(m.group(2))) for m in re.finditer(r'silence_(start|end): ([0-9.]+)',out)]
    x,sr=load(p); dur=len(x)/sr; segs=[]; cur=0.0
    for k,t in ev:
        if k=='start':
            if t>cur+0.02: segs.append((cur,t))
        else: cur=t
    if cur<dur-0.05: segs.append((cur,dur))
    return x,sr,segs
def gap(sr,s): return np.zeros(int(sr*s),np.float32)
# narrador: pausas por posição (fim de frase 0.4, vírgula 0.2, depois do gancho 0.7)
x,sr,segs=speech('narr_b1b2_v2.wav')
print('narr segs',[(round(a,2),round(b,2)) for a,b in segs])
ends={3.97:.3,6.12:.4,10.2:.4,12.86:.7,17.17:.4,22.26:.45}
def pause_after(b):
    for t,p in ends.items():
        if abs(b-t)<0.35: return p
    return 0.2
pad=0.03; parts=[gap(sr,.15)]
for i,(a,b) in enumerate(segs):
    parts.append(x[int(max(0,a-pad)*sr):int(min(len(x)/sr,b+pad)*sr)])
    if i<len(segs)-1: parts.append(gap(sr,pause_after(b)))
parts.append(gap(sr,.45))
y,sr2,s2=speech('imp_b2_v2.wav'); a,b=s2[0][0],s2[-1][1]
parts.append(y[int((a-pad)*sr):int((b+pad)*sr)]); parts.append(gap(sr,.5))
out=np.concatenate(parts)
w=wave.open('amostra_inicio.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(np.clip(out,-32768,32767).astype(np.int16).tobytes()); w.close()
print('dur',len(out)/sr)
