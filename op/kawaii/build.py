import base64,sys
d=sys.argv[1]; b=lambda f:base64.b64encode(open(d+'/'+f,'rb').read()).decode()
s=open(d+'/op.src.html').read()
for k,f in (('__POP__','fonts/pop.woff2'),('__MARU__','fonts/maru.woff2'),('__FRED__','fonts/fredoka.woff2'),('__AUDIO__','op.m4a')): s=s.replace(k,b(f))
open(d+'/hassei-news-op-kawaii.html','w').write(s)
s=open(d+'/hassei-news-op-kawaii.html').read()
for k,f in (('__GB__','gull/body.png'),('__GL__','gull/wingL.png'),('__GR__','gull/wingR.png')): s=s.replace(k,b(f))
open(d+'/hassei-news-op-kawaii.html','w').write(s)
