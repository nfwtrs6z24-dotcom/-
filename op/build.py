import base64,sys
d=sys.argv[1]; b=lambda f:base64.b64encode(open(f,'rb').read()).decode()
s=open(d+'/op.src.html').read()
for k,f in (('__DELA__','fonts/dela.woff2'),('__ZEN__','fonts/zen.woff2'),('__OSW__','fonts/oswald.woff2'),('__MONO__','fonts/mono.woff2'),('__AUDIO__','op.m4a')):
    s=s.replace(k,b(d+'/'+f))
open(d+'/hassei-news-op.html','w').write(s)
