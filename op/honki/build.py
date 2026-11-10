import base64,sys,os
d=sys.argv[1]; b=lambda f:base64.b64encode(open(d+'/'+f,'rb').read()).decode() if os.path.exists(d+'/'+f) else ''
s=open(d+'/op.src.html').read()
for k,f in (('__ROUND__','fonts/round.woff2'),('__AUDIO__','op.m4a'),('__GB__','gull/body.png'),('__GL__','gull/wingL.png'),('__GR__','gull/wingR.png')): s=s.replace(k,b(f))
open(d+'/hassei-news-op-honki.html','w').write(s)
