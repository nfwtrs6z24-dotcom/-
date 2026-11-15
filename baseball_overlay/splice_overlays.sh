#!/bin/bash
# splice_overlays.sh <video.mp4> <times.txt: "png start dur" per line, png path relative to times dir>
# Re-encodes only keyframe-aligned windows around each overlay and splices them back in (exact frame count).
set -e
F="$1"; TT="$2"; TD=$(dirname "$TT")
W="${OVERLAY_WORK:-$(cd "$(dirname "$0")" && pwd)}"
J=$W/spl_$$; mkdir -p $J/seg $J/win
ffprobe -v error -select_streams v -skip_frame nokey -show_entries frame=pts_time -of csv=p=0 "$F" | tr -d ',' > $J/kf.txt
python3 -I - "$J" "$TT" <<'EOF'
import sys, bisect
J, TT = sys.argv[1], sys.argv[2]
k = [float(x) for x in open(J + "/kf.txt") if x.strip()]
items = [l.split() for l in open(TT) if l.strip()]
win = []
for png, t, dur in sorted(items, key=lambda x: float(x[1])):
    t, dur = float(t), float(dur)
    a = k[bisect.bisect_right(k, t - 0.5) - 1]; b = k[bisect.bisect_left(k, t + dur + 0.5)]
    if win and a <= win[-1][1]:
        win[-1][1] = max(win[-1][1], b); win[-1][2].append((png, t, dur))
    else:
        win.append([a, b, [(png, t, dur)]])
with open(J + "/win.txt", "w") as f:
    for a, b, its in win:
        f.write(f"{a} {b} " + " ".join(f"{p}:{t}:{d}" for p, t, d in its) + "\n")
EOF
i=0
while read A B rest; do i=$((i+1)); args=(-ss $A -i "$F"); fc=""; prev="0:v"; n=1
  for it in $rest; do IFS=: read p t d <<< "$it"; off=$(python3 -c "print($t-$A)"); fo=$(python3 -c "print($d-0.35)")
    args+=(-loop 1 -framerate 60000/1001 -t $d -i "$TD/$p.png")
    fc+="[$n:v]format=rgba,fade=in:st=0:d=0.35:alpha=1,fade=out:st=$fo:d=0.35:alpha=1,setpts=PTS+$off/TB[f$n];[$prev][f$n]overlay=eof_action=pass[c$n];"; prev="c$n"; n=$((n+1)); done
  dur=$(python3 -c "print(round(($B-$A)*60000/1001)*1001/60000)")
  ffmpeg -nostdin -v error -y "${args[@]}" -filter_complex "${fc}[$prev]format=yuv420p[out]" -map "[out]" -t $dur -an -c:v libx264 -preset veryfast -crf 18 -profile:v high -level 4.2 -video_track_timescale 60000 $J/win/w$(printf %03d $i).mp4
done < $J/win.txt
times=$(awk '{printf "%.4f,%.4f,", $1-0.01, $2-0.01}' $J/win.txt | sed 's/,$//')
ffmpeg -nostdin -v error -y -i "$F" -map 0:v -c copy -f segment -segment_times "$times" -reset_timestamps 1 $J/seg/s%03d.mp4
L=$J/list.txt; : > $L
for s in $J/seg/*.mp4; do idx=$((10#$(basename $s .mp4 | tr -d s)))
  if [ $((idx%2)) -eq 1 ]; then w=$J/win/w$(printf %03d $(((idx+1)/2))).mp4
    a=$(ffprobe -v error -show_entries stream=nb_frames -of csv=p=0 $s); b=$(ffprobe -v error -show_entries stream=nb_frames -of csv=p=0 $w)
    [ "$a" = "$b" ] || { echo "frame mismatch $s=$a $w=$b"; exit 1; }
    echo "file '$w'" >> $L
  else echo "file '$s'" >> $L; fi; done
ffmpeg -nostdin -v error -y -f concat -safe 0 -i $L -i "$F" -map 0:v -map 1:a -c copy -movflags +faststart "$F.new.mp4"
a=$(ffprobe -v error -show_entries stream=nb_frames -of csv=p=0 -select_streams v "$F"); b=$(ffprobe -v error -show_entries stream=nb_frames -of csv=p=0 -select_streams v "$F.new.mp4")
[ "$a" = "$b" ] || { echo "total frame mismatch $a $b"; exit 1; }
mv "$F.new.mp4" "$F"; rm -rf $J; echo "spliced $(wc -l < $TT) overlays, frames=$b"
