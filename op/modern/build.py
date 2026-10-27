import base64,sys
d=sys.argv[1]; b=lambda f:base64.b64encode(open(d+'/'+f,'rb').read()).decode()
s=open(d+'/op.src.html').read()
for k,f in (('__MIN__','fonts/mincho.woff2'),('__ZEN__','fonts/zen.woff2'),('__SERIF__','fonts/serif.woff2'),('__MONO__','fonts/mono.woff2'),('__GEIST__','fonts/geist.woff2'),('__AUDIO__','op.m4a')): s=s.replace(k,b(f))
open(d+'/hassei-news-op-modern.html','w').write(s)
