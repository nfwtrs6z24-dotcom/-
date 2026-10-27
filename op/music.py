import numpy as np, wave, sys
SR=48000; DUR=10.0; N=int(SR*DUR)
t=np.arange(N)/SR
L=np.zeros(N); R=np.zeros(N)
rng=np.random.default_rng(7)
B=0.5  # beat (120bpm)
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n<=0: return
    l=np.cos((pan+1)*np.pi/4); r=np.sin((pan+1)*np.pi/4)
    L[i:i+n]+=sig[:n]*gain*l*1.414; R[i:i+n]+=sig[:n]*gain*r*1.414
def env(n,a=0.002,d=0.3):
    x=np.arange(n)/SR; e=np.exp(-x/d); k=int(a*SR)
    if k>0: e[:k]*=np.linspace(0,1,k)
    return e
def lp(x,a):  # one-pole lowpass, a in (0,1)
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def saw(f,n,det=0.0):
    x=np.arange(n)/SR; return 2*((x*f*(1+det))%1)-1
def kick(g=1.0,dur=0.5):
    n=int(dur*SR); x=np.arange(n)/SR
    f=45+140*np.exp(-x/0.035); ph=2*np.pi*np.cumsum(f)/SR
    s=np.sin(ph)*np.exp(-x/0.16)+0.3*rng.standard_normal(n)*np.exp(-x/0.004)
    return np.tanh(s*1.6)*g
def snare(g=1.0):
    n=int(0.25*SR); x=np.arange(n)/SR
    nz=rng.standard_normal(n); nz=nz-lp(nz,0.25)
    return (nz*np.exp(-x/0.07)*0.8+np.sin(2*np.pi*190*x)*np.exp(-x/0.05)*0.5)*g
def hat(g=0.25,d=0.03):
    n=int(0.12*SR); nz=rng.standard_normal(n); nz=nz-lp(nz,0.6)
    return nz*env(n,0.0005,d)*g
def crash(g=0.6,d=1.6):
    n=int(3.0*SR); nz=rng.standard_normal(n); nz=nz-lp(nz,0.4)
    return nz*env(n,0.001,d)*g
def stab(freqs,dur,g=0.5,bright=0.35,d=0.25):
    n=int(dur*SR); s=np.zeros(n)
    for f in freqs:
        for det in (-0.006,0.0,0.007): s+=saw(f,n,det)
    s/=len(freqs)*3; s=lp(s,bright)
    return s*env(n,0.003,d)*g
def bass(f,dur,g=0.6):
    n=int(dur*SR); x=np.arange(n)/SR
    s=lp(saw(f,n),0.12)*1.5+0.5*np.sin(2*np.pi*f*x)
    e=np.minimum(1,x/0.004)*np.exp(-x/0.35)
    return np.tanh(s*e*1.5)*g
def note(n): return 440*2**((n-69)/12)
# --- 0-2s: intro ticks + riser
for k in range(16):
    add(hat(0.18 if k%4 else 0.3,0.02),k*0.125,pan=(-0.4 if k%2 else 0.4))
for k in range(4): add(np.sin(2*np.pi*1760*np.arange(int(0.05*SR))/SR)*env(int(0.05*SR),0.001,0.015)*0.25,k*B)
n=int(2.0*SR); x=np.arange(n)/SR
nz=rng.standard_normal(n); rs=np.zeros(n); s=0
cut=0.01+0.5*(x/2.0)**2
for i in range(n): s+=cut[i]*(nz[i]-s); rs[i]=s
rs*= (x/2.0)**2*0.6
sw=np.sin(2*np.pi*np.cumsum(220+880*(x/2)**3)/SR)*(x/2)**3*0.15
add(rs+sw,0.0)
add(lp(saw(note(38),int(2*SR)),0.05)*(x/2)*0.4,0.0)  # low drone
# --- hits 八 / 西 / ニュース
Dm=[note(62),note(65),note(69),note(74)]
for tt,ch,g in ((2.0,Dm,0.55),(2.5,[note(60),note(65),note(69),note(72)],0.55)):
    add(kick(1.0),tt); add(stab(ch,0.45,g,0.4,0.18),tt,0.0); add(bass(note(38),0.45),tt)
add(kick(1.1),3.0); add(crash(0.55),3.0,-0.2); add(snare(0.9),3.0)
# --- 3-7s groove: progression Dm Bb C A  (1 bar each = 2s? use 1s per chord, 4 chords x1)
prog=[(note(38),[note(62),note(65),note(69)]),(note(34),[note(62),note(65),note(70)]),
      (note(36),[note(64),note(67),note(72)]),(note(33),[note(61),note(64),note(69)])]
for bar in range(4):
    t0=3.0+bar*1.0; root,ch=prog[bar]
    for b in range(2):
        tb=t0+b*B
        if not (bar==0 and b==0): add(kick(0.9),tb)
        if b==1: add(snare(0.7),tb)
    for e in range(8):
        add(hat(0.22 if e%2 else 0.12,0.025 if e%2 else 0.015),t0+e*0.125,pan=0.35)
    # bass: 8ths octave pattern
    for e in range(4):
        add(bass(root*(2 if e%2 else 1),0.24,0.45),t0+e*0.25)
    # stabs on syncopation
    add(stab(ch,0.3,0.32,0.3,0.12),t0,-0.3); add(stab(ch,0.3,0.28,0.3,0.12),t0+0.375,0.3); add(stab(ch,0.3,0.26,0.3,0.12),t0+0.75,-0.3)
    # lead melody (brassy)
mel=[(3.0,74,0.375),(3.375,72,0.375),(3.75,74,0.25),(4.0,77,0.5),(4.5,74,0.5),(5.0,76,0.375),(5.375,79,0.375),(5.75,81,0.25),(6.0,73,0.5),(6.5,76,0.5)]
for st,m,d in mel:
    n=int(d*SR); xx=np.arange(n)/SR
    vib=1+0.004*np.sin(2*np.pi*5.5*xx)*np.minimum(1,xx/0.15)
    ph=np.cumsum(note(m)*vib)/SR
    s=(2*(ph%1)-1)+0.6*(2*((ph*1.005)%1)-1)
    s=lp(s,0.22)*np.minimum(1,xx/0.01)*np.minimum(1,(d-xx)/0.03).clip(0,1)*0.22
    add(s,st,0.1)
# --- 7-8s: snare roll build + riser
for k in range(16):
    add(snare(0.25+0.6*(k/15)),7.0+k*0.0625,pan=(k%2-0.5)*0.4)
n=int(1.0*SR); x=np.arange(n)/SR
add(np.sin(2*np.pi*np.cumsum(300+1200*x**2)/SR)*x**2*0.12,7.0)
add(bass(note(33),1.0,0.5),7.0)
# --- 8s final hit with long tail
fin=[note(50),note(57),note(62),note(65),note(69),note(74)]
add(kick(1.2,0.8),8.0); add(crash(0.7,1.8),8.0,0.2); add(crash(0.5,1.8),8.0,-0.3)
add(stab(fin,2.0,0.75,0.5,0.7),8.0)
add(bass(note(26),2.0,0.8),8.0)

# --- extra impact layers
def sub(g=1.0,d=0.9):
    n=int(1.6*SR); x=np.arange(n)/SR
    f=38+30*np.exp(-x/0.08); return np.tanh(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/d)*2.2)*g
def revcym(dur,g=0.5):
    n=int(dur*SR); nz=rng.standard_normal(n); nz=nz-lp(nz,0.35); x=np.arange(n)/SR
    return nz*(x/dur)**3*g
def zap(g=0.35):
    n=int(0.16*SR); x=np.arange(n)/SR
    f=2400*np.exp(-x/0.03)+120; sq=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))
    sq=np.round(sq*np.exp(-x/0.06)*6)/6
    return sq*g
def clap(g=0.5):
    n=int(0.2*SR); nz=rng.standard_normal(n); nz=nz-lp(nz,0.3); x=np.arange(n)/SR
    e=np.zeros(n)
    for o in (0,0.011,0.022): k=int(o*SR); e[k:]+=np.exp(-(x[:n-k])/0.012)
    e+=np.exp(-x/0.09)*0.6
    return nz*e*g
add(revcym(1.0,0.55),1.0); add(revcym(1.0,0.6),7.0)
for h,g in ((2.0,0.8),(2.5,0.8),(3.0,1.0),(8.0,1.2)): add(sub(g),h)
for h in (4.0,5.5,6.25,6.5): add(zap(0.3),h,pan=0.5 if h%1 else -0.5)
for bar in range(4):
    add(clap(0.35),3.5+bar*1.0,0.15)
# whoosh into the zoom
n=int(1.0*SR); x=np.arange(n)/SR; nz=rng.standard_normal(n); w=np.zeros(n); st=0
for i in range(n):
    a=0.02+0.4*(x[i])**2; st+=a*(nz[i]-st); w[i]=st
add(w*x**1.5*0.7,7.0)
# final brass-ish second stab and a taiko-style low drum
add(stab([note(50),note(57),note(62),note(66),note(69)],1.5,0.4,0.55,0.5),8.0,0.25)
for k,tt in enumerate((8.0,8.375,8.5)): add(kick(0.7 if k else 0,0.6),tt)

# simple stereo reverb (multi-tap feedback delays)
def verb(x):
    y=x.copy()
    for dl,g in ((0.0297,0.35),(0.0371,0.3),(0.0411,0.28),(0.0437,0.25),(0.071,0.2),(0.113,0.15)):
        k=int(dl*SR); z=np.zeros_like(x)
        for rep in range(1,6): 
            if k*rep<len(x): z[k*rep:]+=x[:-k*rep]*(g**rep)
        y+=lp(z,0.3)
    return y
L=verb(L); R=verb(R)
# fade out last 0.6s
f=np.ones(N); k=int(0.6*SR); f[-k:]=np.linspace(1,0,k)**2
L*=f; R*=f
m=max(np.abs(L).max(),np.abs(R).max()); L=np.tanh(L/m*1.8)/np.tanh(1.8)*0.89; R=np.tanh(R/m*1.8)/np.tanh(1.8)*0.89
out=(np.stack([L,R],1)*32767).astype('<i2')
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes()); w.close()
print("ok")
