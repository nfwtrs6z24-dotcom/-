import numpy as np, wave, sys
SR=48000; DUR=12; N=SR*DUR; L=np.zeros(N); R=np.zeros(N); rng=np.random.default_rng(21)
def add(x,st,pan=0.,g=1.):
    i=int(st*SR); n=min(len(x),N-i)
    if n<=0 or i<0: return
    L[i:i+n]+=x[:n]*g*np.cos((pan+1)*np.pi/4)*1.414; R[i:i+n]+=x[:n]*g*np.sin((pan+1)*np.pi/4)*1.414
def lp(x,a):
    y=np.empty_like(x); s=0.
    for i in range(len(x)): s+=a*(x[i]-s); y[i]=s
    return y
def lpv(x,cut):
    y=np.empty_like(x); s=0.
    for i in range(len(x)): s+=cut[i]*(x[i]-s); y[i]=s
    return y
X=lambda d: np.arange(int(d*SR))/SR
nt=lambda m: 440*2**((m-69)/12)
def saws(f,x,dets=(-.006,0,.007)): return sum(2*((x*f*(1+d))%1)-1 for d in dets)/len(dets)
def bell(m,d=1.2,g=.2):
    x=X(d); f=nt(m); return (np.sin(2*np.pi*f*x)+.45*np.sin(2*np.pi*f*2.76*x)*np.exp(-x/.08)+.25*np.sin(2*np.pi*f*5.4*x)*np.exp(-x/.03))*np.exp(-x/.45)*np.minimum(1,x/.002)*g
def marimba(m,d=.5,g=.25):
    x=X(d); f=nt(m); return (np.sin(2*np.pi*f*x)+.3*np.sin(2*np.pi*f*4*x)*np.exp(-x/.02))*np.exp(-x/.16)*np.minimum(1,x/.002)*g
def lead(m,d,g=.16):   # bright brassy lead with a quick filter bloom
    x=X(d+.12); f=nt(m); s=saws(f,x)+.5*saws(f*2,x,(0,.004))
    cut=.06+.4*np.exp(-x/.09)+.1*np.minimum(1,x/.05); y=lpv(s,cut)
    e=np.minimum(1,x/.008)*np.minimum(1,np.clip((d+.12-x)/.1,0,1)); vib=1+.0*x
    return y*e*g
def stab(ms,d,g=.3,bright=.3,dec=.22):
    x=X(d); s=sum(saws(nt(m),x) for m in ms)/len(ms); return lp(s,bright)*np.minimum(1,x/.004)*np.exp(-x/dec)*g
def pad(ms,d,g=.12,a=.6,r=.8):
    x=X(d); s=sum(saws(nt(m),x,(-.004,.004)) for m in ms)/len(ms); e=np.minimum(1,x/a)*np.minimum(1,np.clip((d-x)/r,0,1)); return lp(s,.05)*e*g*3
def bass(m,d,g=.42):
    x=X(d); f=nt(m); s=lp(saws(f,x,(0,)),.1)*1.2+np.sin(2*np.pi*f*x); return np.tanh(s*np.minimum(1,x/.005)*np.exp(-x/.3)*1.3)*g
def kick(g=.9,d=.4):
    x=X(d); f=46+110*np.exp(-x/.03); return np.tanh((np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/.15)+.25*rng.standard_normal(len(x))*np.exp(-x/.004))*1.5)*g
def clap(g=.35):
    x=X(.22); n=rng.standard_normal(len(x)); n=n-lp(n,.3); e=sum(np.exp(-np.clip(x-o,0,None)/.01)*(x>=o) for o in (0,.01,.021))+.5*np.exp(-x/.09); return n*e*g
def snare(g=.5):
    x=X(.2); n=rng.standard_normal(len(x)); n=n-lp(n,.25); return (n*np.exp(-x/.06)*.8+np.sin(2*np.pi*200*x)*np.exp(-x/.04)*.5)*g
def hat(g=.12,d=.03):
    x=X(.14); n=rng.standard_normal(len(x)); n=n-lp(n,.7); return n*np.exp(-x/d)*g
def crash(g=.4,d=1.4):
    x=X(3.0); n=rng.standard_normal(len(x)); n=n-lp(n,.45); return n*np.minimum(1,x/.002)*np.exp(-x/d)*g
def noise_sweep(d,g,up=True,p=2.0):
    x=X(d); n=rng.standard_normal(len(x)); u=x/d if up else 1-x/d; return lpv(n,.01+.5*u**2)*u**p*g
def gull(st,g=.13,pan=.2):
    for k,(d,f0,f1) in enumerate(((.16,1300,1900),(.12,1500,2000),(.24,1700,1100))):
        x=X(d); f=f0*(f1/f0)**(x/d); ph=2*np.pi*np.cumsum(f)/SR
        add((np.sin(ph)+.5*np.sin(2*ph)+.25*np.sin(3*ph))*np.sin(np.pi*x/d)**.6*g,st+[0,.18,.32][k],pan)
def sub(g=.8):
    x=X(1.4); f=40+34*np.exp(-x/.07); return np.tanh(np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-x/.7)*2)*g

B=.5
# ---- 0–2.5 harbour morning: waves, pad, bells, a gull, then the fly-by whoosh
x=X(3.0); w=lp(rng.standard_normal(len(x)),.06)*(.5+.5*np.sin(2*np.pi*.45*x-1.2))**2*np.minimum(1,x/.4)*np.minimum(1,np.clip((3.0-x)/.6,0,1))
add(w*.9,0,-.3); add(np.roll(w,9000)*.9,0,.3)
add(pad([50,57,62,66,69],2.7,.11,.5,.25),0)
for k,m in enumerate([74,78,81,86,85,81,78,81]): add(bell(m,1.3,.11),.3+k*.25,(k%2-.5)*.7)
gull(.55,.12,.4); gull(1.5,.07,-.3)
add(noise_sweep(.75,.5),1.75); add(np.sin(2*np.pi*np.cumsum(180+900*(X(.75)/.75)**3)/SR)*(X(.75)/.75)**2*.12,1.75)
# ---- 2.5–8 flight: D | Bm | G | A (1s each), then G – A build
add(kick(1.1),2.5); add(crash(.45),2.5,-.2); add(sub(.7),2.5)
prog=[(2.5,1.0,[62,66,69],38),(3.5,1.0,[59,62,66],35),(4.5,1.0,[55,59,62],43),(5.5,1.0,[57,61,64],45),(6.5,.75,[55,59,62],43),(7.25,.75,[57,61,64],45)]
t=2.5
while t<7.99:
    if t>2.5: add(kick(.95),t)
    k=int(round((t-2.5)/B))
    if k%2==1 and t<7.0: add(clap(.34),t,.1); add(snare(.3),t,-.1)
    for e in range(4): add(hat(.13 if e%2 else .07,.045 if e==2 else .02),t+e*.125,.4 if e%2 else -.3)
    t+=B
for st,d,ch,root in prog:
    n=int(round(d/.25))
    for e in range(n): add(bass(root+(12 if e%2 else 0),.24,.36),st+e*.25)
    add(stab([m+12 for m in ch],.3,.2,.32,.13),st,-.35); add(stab([m+12 for m in ch],.3,.16,.32,.13),st+.375,.35)
    if d>=1: add(stab([m+12 for m in ch],.3,.15,.32,.13),st+.75,-.35)
    add(pad(ch+[ch[0]+12],d+.2,.07,.05,.2),st)
mel=[(2.5,78,.25),(2.75,81,.25),(3.0,86,.5),(3.5,83,.25),(3.75,81,.25),(4.0,78,.5),(4.5,79,.25),(4.75,83,.25),(5.0,86,.5),(5.5,88,.25),(5.75,85,.25),(6.0,81,.5),
     (6.5,83,.25),(6.75,86,.25),(7.0,91,.25),(7.25,81,.25),(7.5,85,.25),(7.75,88,.25)]
for st,m,d in mel: add(lead(m,d,.15),st,.12); add(bell(m+12,.5,.05),st,-.3)
# build into the cloud
for k in range(16): add(snare(.14+.42*(k/15)),7.0+k*.0625,(k%2-.5)*.5)
add(noise_sweep(1.6,.42),6.4); add(np.sin(2*np.pi*np.cumsum(260+1500*(X(1.5)/1.5)**2.5)/SR)*(X(1.5)/1.5)**2*.09,6.5)
# ---- 8.0 title: hit + letter pops
add(kick(1.2,.6),8.0); add(sub(.9),8.0); add(crash(.55,1.6),8.0,.25); add(crash(.4,1.6),8.0,-.3)
add(stab([62,69,74,78,81],1.4,.42,.45,.5),8.0); add(pad([50,57,62,66,69,74],1.9,.1,.02,.5),8.0); add(bass(38,1.4,.5),8.0)
for st,m in ((8.0,74),(8.25,78),(8.5,81),(8.625,83),(8.75,86),(8.875,90)): add(marimba(m,.6,.3),st,(m%3-1)*.3); add(bell(m+12,.9,.1),st,(m%2-.5)*.6)
for tt in (8.5,9.0): add(kick(.9),tt)
add(clap(.3),8.5); add(clap(.3),9.0)
for k in range(8): add(hat(.1,.03),8.0+k*.125+.0,.4)
# gull glides in: whistle-ish whoosh, cry, tom fill
gull(8.95,.1,.5)
add(noise_sweep(.55,.4),8.95,.5)
for k,(tt,f) in enumerate(((9.0,190),(9.125,170),(9.25,150),(9.375,120))):
    x=X(.25); add(np.sin(2*np.pi*np.cumsum(f*(1+.5*np.exp(-x/.03)))/SR)*np.exp(-x/.09)*.45,tt,(k-1.5)*.3)
# ---- 9.5 landing stinger: Dmaj9, bells cascade, long tail
add(kick(1.25,.7),9.5); add(sub(1.0),9.5); add(crash(.6,2.0),9.5,.2); add(crash(.45,2.0),9.5,-.25); add(clap(.4),9.5)
add(stab([50,62,66,69,73,76,81],2.4,.5,.5,.9),9.5); add(pad([38,50,57,62,66,69,76],2.5,.13,.02,1.4),9.5); add(bass(26,2.2,.6),9.5)
for k,m in enumerate([86,90,93,98,97,93,90,86,93,98]): add(bell(m,1.6,.085),9.5+k*.075,(k%3-1)*.6)
add(lead(86,.9,.12),9.5,0)
x=X(2.5); w2=lp(rng.standard_normal(len(x)),.06)*np.minimum(1,x/1.0)*np.minimum(1,np.clip((2.5-x)/.8,0,1)); add(w2*.5,9.5,-.3); add(np.roll(w2,7000)*.5,9.5,.3)
def verb(x):
    y=x.copy()
    for dl,g in ((.0297,.32),(.0371,.28),(.0411,.26),(.0437,.23),(.071,.18),(.113,.14)):
        k=int(dl*SR); z=np.zeros_like(x)
        for r in range(1,6): z[k*r:]+=x[:-k*r]*g**r
        y+=lp(z,.3)
    return y
L=verb(L); R=verb(R)
# gentle sidechain pump on the groove section
env=np.ones(N)
tt=2.5
while tt<8.0:
    i=int(tt*SR); n=int(.22*SR); env[i:i+n]=np.minimum(env[i:i+n],.72+.28*np.linspace(0,1,n)**.7); tt+=B
L*=env; R*=env
f=np.ones(N); k=int(.9*SR); f[-k:]=np.linspace(1,0,k)**2
L*=f; R*=f
m=max(abs(L).max(),abs(R).max()); L=np.tanh(L/m*1.9)/np.tanh(1.9)*.9; R=np.tanh(R/m*1.9)/np.tanh(1.9)*.9
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.stack([L,R],1)*32767).astype('<i2').tobytes()); w.close(); print('ok')
