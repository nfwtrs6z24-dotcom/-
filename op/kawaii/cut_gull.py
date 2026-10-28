import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter
src,out=sys.argv[1],sys.argv[2]
im=Image.open(src).convert('RGBA'); a=np.array(im).astype(np.int16)
print('alpha min',a[...,3].min())
alpha=a[...,3].astype(np.uint8)
H,W=alpha.shape
def poly_mask(pts):
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(pts,fill=255); return m
L=[(0,0),(880,0),(815,420),(790,480),(760,560),(705,690),(0,720)]
Rw=[(1325,655),(1500,612),(W,520),(W,H),(1600,H),(1400,950),(1290,950),(1320,780)]
mL,mR=poly_mask(L),poly_mask(Rw)
def part(mask):
    p=im.copy(); al=np.array(p.getchannel('A')); al=np.minimum(al,np.array(mask)); p.putalpha(Image.fromarray(al)); return p
body=im.copy(); al=np.array(body.getchannel('A')); al[np.array(mL)>0]=0; al[np.array(mR)>0]=0; body.putalpha(Image.fromarray(al))
sc=0.5
for name,p in (('full',im),('body',body),('wingL',part(mL)),('wingR',part(mR))):
    p=p.resize((int(W*sc),int(H*sc)),Image.LANCZOS); p.save(f'{out}/{name}.png',optimize=True)
print('ok',W,H)
