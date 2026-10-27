import numpy as np, wave, sys
SR=48000; N=SR*10; L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(3)
def add(x,st,pan=0.,g=1.):
    i=int(st*SR); n=min(len(x),N-i)
    if n<=0: return
    L[i:i+n]+=x[:n]*g*np.cos((pan+1)*np.pi/4)*1.414; R[i:i+n]+=x[:n]*g*np.sin((pan+1)*np.pi/4)*1.414
def lp(x,a):
    y=np.empty_like(x); s=0.
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def note(m): return 440*2**((m-69)/12)
X=lambda d: np.arange(int(d*SR))/SR
def kick(g=.9):
    x=X(.45); f=48+90*np.exp(-x/.03); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/.18)*g
def clap(g=.4):
    x=X(.25); n=rng.standard_normal(len(x)); n=n-lp(n,.3); e=sum(np.exp(-np.clip(x-o,0,None)/.01)*(x>=o) for o in (0,.009,.018))+.5*np.exp(-x/.12)
    return n*e*g
def hat(g=.12,d=.03):
    x=X(.15); n=rng.standard_normal(len(x)); n=n-lp(n,.7); return n*np.exp(-x/d)*g
def epiano(m,d,g=.18):
    x=X(d); f=note(m); s=np.sin(2*np.pi*f*x+1.2*np.sin(2*np.pi*f*2*x)*np.exp(-x/.4))
    s+=.3*np.sin(2*np.pi*f*2.001*x)*np.exp(-x/.25)
    return s*np.minimum(1,x/.004)*np.exp(-x/(d*.6))*g
def pluck(m,d=.5,g=.22):
    x=X(d); f=note(m); s=sum(2*((x*f*(1+dt))%1)-1 for dt in (-.004,0,.005))/3
    cut=.05+.5*np.exp(-x/.06); y=np.empty_like(s); st=0.
    for i in range(len(s)): st+=cut[i]*(s[i]-st); y[i]=st
    return y*np.exp(-x/.18)*g
def subb(m,d,g=.4):
    x=X(d); return np.tanh(np.sin(2*np.pi*note(m)*x)*1.4)*np.minimum(1,x/.01)*np.minimum(1,(d-x)/.02).clip(0,1)*g
B=.5
# vinyl crackle + room tone throughout
cr=np.zeros(N); idx=rng.integers(0,N,900); cr[idx]=rng.standard_normal(900)*.35
noise=lp(rng.standard_normal(N),.05)*.02
add(cr+noise,0)
# 0-2: filtered pad on Fmaj9, ticking mono hats
pad=[53,57,60,64,67]; x=X(2.2); s=np.zeros(len(x))
for m in pad:
    for dt in (-.003,.003): s+=2*((x*note(m)*(1+dt))%1)-1
s=lp(s/10,.02)*np.minimum(1,x/1.2)*.9; add(s,0,0)
for k in range(8): add(hat(.06,.015),k*.25,.4)
# chords: Fmaj9 Em7 Dm9 Cmaj9 (each 1 bar = 2s at 120bpm) from 2.0
prog=[([53,57,60,64,67],41),([52,55,59,62,66],40),([50,53,57,60,64],38),([48,52,55,59,62],36)]
for bar in range(3):  # 2-8s, last bar dropped for the break
    t0=2+bar*2; ch,root=prog[bar]
    for b in range(4):
        tb=t0+b*B
        if tb<7.5: add(kick(),tb)
        if b in (1,3) and tb<7.5: add(clap(),tb,.1)
        for e in range(2):
            th=tb+e*.25
            if th<7.5: add(hat(.14 if e else .07,.06 if e else .02),th,.35)
    for k,o in enumerate((0,.75,1.5)):
        if t0+o<7.5:
            for m in ch: add(epiano(m+12,1.0,.07),t0+o+k*0.0,-.2)
    for o,d in ((0,.7),(.75,.6),(1.5,.45)):
        if t0+o<7.5: add(subb(root,d),t0+o)
# reveal plucks: 八 at 2.0, 西 at 2.5, ニュース at 3.5
for st,m in ((2.0,72),(2.5,76),(3.5,79),(3.625,81),(3.75,84)): add(pluck(m,.6,.2),st,(m%5-2)*.15)
# glide pluck melody 4-7s
for st,m in ((4.5,79),(4.75,76),(5.25,74),(5.5,72),(6.0,74),(6.25,76),(6.75,79)): add(pluck(m,.45,.13),st,.3)
# 7.25-8.0 break: reverse swell + tape-stop on the last chord
x=X(.75); n=rng.standard_normal(len(x)); n=n-lp(n,.4); add(n*(x/.75)**3*.25,7.25)
for m in (64,67,71,74): add(np.sin(2*np.pi*note(m)*x*(1-.4*(x/.75)**2))*(x/.75)**2*.06,7.25)
# 8.0: final — Cmaj9 bloom + kick + clap, then tail
add(kick(1.0),8.0); add(clap(.5),8.0)
for m in (48,55,59,62,64,67,71): add(epiano(m+12,2.0,.08),8.0)
add(subb(36,1.6,.45),8.0)
for st,m in ((8.0,84),(8.25,79),(8.5,83),(8.75,86)): add(pluck(m,.8,.12),st,.25)
for k in range(4): add(hat(.08,.05),8.5+k*.25,.4)
# light reverb + sidechain-ish pump after 2s
def verb(x):
    y=x.copy()
    for dl,g in ((.031,.3),(.043,.27),(.057,.22),(.089,.16),(.131,.12)):
        k=int(dl*SR); z=np.zeros_like(x)
        for r in range(1,6): z[k*r:]+=x[:-k*r]*g**r
        y+=lp(z,.25)
    return y
L=verb(L); R=verb(R)
f=np.ones(N); k=int(.6*SR); f[-k:]=np.linspace(1,0,k)**2; L*=f; R*=f
m=max(abs(L).max(),abs(R).max()); L=np.tanh(L/m*1.4)/np.tanh(1.4)*.89; R=np.tanh(R/m*1.4)/np.tanh(1.4)*.89
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([L,R],1)*32767).astype('<i2').tobytes()); w.close(); print('ok')
