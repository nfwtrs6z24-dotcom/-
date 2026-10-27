import numpy as np, wave, sys
SR=48000; N=SR*10; L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(11)
def add(x,st,pan=0.,g=1.):
    i=int(st*SR); n=min(len(x),N-i)
    if n<=0: return
    L[i:i+n]+=x[:n]*g*np.cos((pan+1)*np.pi/4)*1.414; R[i:i+n]+=x[:n]*g*np.sin((pan+1)*np.pi/4)*1.414
def lp(x,a):
    y=np.empty_like(x); s=0.
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
X=lambda d: np.arange(int(d*SR))/SR
nt=lambda m: 440*2**((m-69)/12)
def bell(m,d=1.2,g=.2):   # music box / glockenspiel
    x=X(d); f=nt(m); return (np.sin(2*np.pi*f*x)+.45*np.sin(2*np.pi*f*2.76*x)*np.exp(-x/.08)+.25*np.sin(2*np.pi*f*5.4*x)*np.exp(-x/.03))*np.exp(-x/.45)*np.minimum(1,x/.002)*g
def marimba(m,d=.5,g=.25):
    x=X(d); f=nt(m); return (np.sin(2*np.pi*f*x)+.3*np.sin(2*np.pi*f*4*x)*np.exp(-x/.02))*np.exp(-x/.16)*np.minimum(1,x/.002)*g
def uke(m,d=.6,g=.16):    # karplus-strong pluck
    n=int(d*SR); p=int(SR/nt(m)); buf=rng.uniform(-1,1,p); out=np.empty(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=.5*(buf[i%p]+buf[(i+1)%p])*.996
    return out*g
def strum(ms,st,g=.14,dn=True):
    for k,m in enumerate(ms if dn else ms[::-1]): add(uke(m,.7,g),st+k*.012,(k-1.5)*.15)
def boing(f0,f1,d=.35,g=.3):
    x=X(d); f=f0*(f1/f0)**(x/d)*(1+.04*np.sin(2*np.pi*18*x)); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/(d*.5))*np.minimum(1,x/.004)*g
def pop(g=.35):
    x=X(.09); f=900*np.exp(-x/.015)+250; return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/.025)*g
def kick(g=.5):
    x=X(.3); f=60+80*np.exp(-x/.02); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/.09)*g
def clap(g=.22):
    x=X(.18); n=rng.standard_normal(len(x)); n=n-lp(n,.3); return n*(np.exp(-x/.01)+.4*np.exp(-x/.07))*g
def shaker(g=.06):
    x=X(.08); n=rng.standard_normal(len(x)); n=n-lp(n,.8); return n*np.sin(np.pi*np.clip(x/.06,0,1))*g
def bass(m,d,g=.3):
    x=X(d); return np.sin(2*np.pi*nt(m)*x)*np.minimum(1,x/.005)*np.exp(-x/.4)*g
def whistle(f0,f1,d,g=.15):
    x=X(d); f=f0*(f1/f0)**(x/d); return np.sin(2*np.pi*np.cumsum(f*(1+.01*np.sin(2*np.pi*6*x)))/SR)*np.minimum(1,x/.03)*np.minimum(1,(d-x)/.05).clip(0,1)*g
# 0-1.2 music box intro
for k,m in enumerate([72,76,79,84,79,76,83,79]): add(bell(m,1.0,.14),.15+k*.13,(k%2-.5)*.4)
# mascot jump 1.2 / land 1.65 / hop
add(boing(220,900,.42,.28),1.2); add(pop(.3),1.65)
add(boing(300,1200,.5,.22),2.0,.3); add(whistle(700,1400,.55,.08),2.0,.3)
# letter pops: 八 西 ニ ュ ー ス
for st,m in ((2.0,72),(2.5,76),(3.0,79),(3.125,81),(3.25,84),(3.375,88)):
    add(pop(.32),st); add(bell(m,.9,.2),st,(m%3-1)*.3)
# groove 2.0-7.0: C Am F G (1s each from 3.0), pickup bar 2.0-3.0 on C
prog=[(2.0,[60,64,67,72],48),(3.0,[60,64,67,72],48),(4.0,[57,60,64,69],45),(5.0,[53,57,60,65],41),(6.0,[55,59,62,67],43)]
for st,ch,root in prog:
    for b in range(2):
        tb=st+b*.5; add(kick(),tb)
        if b==1: add(clap(),tb,.1)
        for e in range(4): add(shaker(),tb+e*.125,.45)
    if st>=3.0:
        strum(ch,st,.13); strum(ch,st+.375,.08,False); strum(ch,st+.75,.1)
    add(bass(root,.45),st); add(bass(root+7,.4),st+.5)
mel=[(3.5,76),(3.75,79),(4.0,81),(4.25,79),(4.5,76),(5.0,77),(5.25,76),(5.5,74),(5.75,72),(6.0,74),(6.25,79),(6.5,83),(6.75,86)]
for st,m in mel: add(marimba(m,.5,.22),st,-.2)
# fish splashes
for st in (4.4,5.9): add(pop(.15),st); add(pop(.12),st+.82)
# 7.0 spin jump: slide whistle up then down
add(whistle(500,1800,.6,.14),7.0); add(whistle(1600,600,.4,.12),7.6)
for k in range(8): add(bell(84+[0,2,4,7,9,12,14,16][k],.4,.08),7.0+k*.1,(k%2-.5)*.6)
# 8.0 ta-da!
add(kick(.6),8.0); add(clap(.3),8.0)
strum([48,55,60,64,67,72],8.0,.2); 
for k,m in enumerate([72,76,79,84,88,91]): add(bell(m,1.6,.13),8.0+k*.06,(k%3-1)*.4)
add(bass(36,1.5,.4),8.0)
for k in range(4): add(shaker(.05),8.5+k*.25,.4)
add(marimba(84,.6,.2),8.6); add(marimba(91,.8,.18),8.75)   # wink sparkle
# iris close
add(boing(900,200,.45,.2),9.35)
def verb(x):
    y=x.copy()
    for dl,g in ((.029,.25),(.041,.22),(.053,.2),(.079,.15)):
        k=int(dl*SR); z=np.zeros_like(x)
        for r in range(1,5): z[k*r:]+=x[:-k*r]*g**r
        y+=lp(z,.3)
    return y
L=verb(L); R=verb(R)
f=np.ones(N); k=int(.5*SR); f[-k:]=np.linspace(1,0,k)**2; L*=f; R*=f
m=max(abs(L).max(),abs(R).max()); L=np.tanh(L/m*1.3)/np.tanh(1.3)*.89; R=np.tanh(R/m*1.3)/np.tanh(1.3)*.89
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([L,R],1)*32767).astype('<i2').tobytes()); w.close(); print('ok')
