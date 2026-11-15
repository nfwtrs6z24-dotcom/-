#!/bin/bash
# encode_game.sh <gdir> <out.mp4> <src1> [src2 ...]   ; optional env TEST="-ss X -frames:v 1" for a still test
set -e
G=$1; OUT=$2; shift 2
SRC="concat:$(IFS='|'; echo "$*")"
args=(-i "$SRC" -itsoffset 1.0 -i $G/telop.mov)
fc="[0:v]bwdif=1[v0];[v0][1:v]overlay=eof_action=pass[c0]"; prev=c0; n=2; k=0
while read a b inn half aw hm; do k=$((k+1)); args+=(-i $G/sb/s$(printf %02d $k).png)
  fc+=";[$prev][$n:v]overlay=enable='between(t,$a,$b-0.001)'[c$n]"; prev=c$n; n=$((n+1)); done < $G/states.txt
add_timed(){ args+=(-loop 1 -framerate 60000/1001 -t $3 -i $1)
  fc+=";[$n:v]format=rgba,fade=in:st=0:d=0.35:alpha=1,fade=out:st=$(echo "$3-0.35"|bc):d=0.35:alpha=1,setpts=PTS+$2/TB[f$n];[$prev][f$n]overlay=eof_action=pass[c$n]"; prev=c$n; n=$((n+1)); }
add_timed $G/defense.png $(cat $G/defense_t.txt) 15
while read i t; do add_timed $G/bat/b$i.png $t 7; done < $G/bat/times.txt
if [ -f $G/overlays.txt ]; then while read p d t; do add_timed $G/$p.png $t $d; done < $G/overlays.txt; fi
fc+=";[$prev]format=yuv420p[out]"
if [ -n "$TEST" ]; then
  ffmpeg -nostdin -v error -y "${args[@]}" -filter_complex "$fc" -map "[out]" $TEST "$OUT"
else
  ffmpeg -nostdin -v error -y "${args[@]}" -filter_complex "$fc" -map "[out]" -map 0:a:0 ${CUT:+-t $CUT} -c:v libx264 -preset veryfast -crf 22 -profile:v high -level 4.2 -c:a aac -b:a 192k "$OUT"
fi
