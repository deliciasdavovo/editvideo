import numpy as np, wave, glob, os, json
D='/home/user/editvideo/bremen/audio'
def load(p):
    w=wave.open(p); sr=w.getframerate(); x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    if w.getnchannels()==2: x=x.reshape(-1,2).mean(1)
    return x,sr
def tighten(x,sr,cap=0.36,thr_db=-40,edge=0.03):
    hop=int(sr*0.01); n=len(x)//hop
    e=np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop]**2)+1e-12) for i in range(n)])
    db=20*np.log10(e+1e-9); sil=db<thr_db
    # edges
    nz=np.where(~sil)[0]
    if len(nz)==0: return x,[]
    a=max(0,nz[0]-int(edge*100)); b=min(n,nz[-1]+1+int(edge*100))
    out=[]; segs=[]; i=a; t=0
    while i<b:
        j=i
        if sil[i]:
            while j<b and sil[j]: j+=1
            L=j-i
            keep=min(L,int(cap*100))
            out.append(x[i*hop:(i*hop)+keep*hop]); t+=keep*hop
        else:
            while j<b and not sil[j]: j+=1
            segs.append((t/sr,(t+(j-i)*hop)/sr))
            out.append(x[i*hop:j*hop]); t+=(j-i)*hop
        i=j
    return np.concatenate(out),segs
if __name__=='__main__':
    tot=0
    for p in sorted(glob.glob(D+'/*.wav')):
        if 'amostra' in p or '/t_' in p: continue
        x,sr=load(p); y,s=tighten(x,sr); tot+=len(y)/sr
        print(os.path.basename(p),round(len(x)/sr,2),'->',round(len(y)/sr,2))
    print('total',tot)
