#!/usr/bin/env bash
# 「ころころ、みかん。」組み立てスクリプト
#
#   clips/S01.mp4 〜 S10.mp4 … AIで生成した各カット（無い場合は仮カードで代用＝Vコンテになる）
#   audio/voice.wav          … セリフ・ナレーションを60秒タイムラインに並べたもの（任意）
#   audio/bgm.wav (or .mp3)  … BGM（任意。音量は BGM_VOL で調整, 既定 0.35）
#   audio/se.wav             … 効果音・環境音を60秒タイムラインに並べたもの（任意）
#
# 使い方:
#   ./assemble.sh            → out/master.mp4 (1920x1080 29.97p, -24LKFS, テロップ焼き込み)
#   ./assemble.sh --mxf      → 上記に加え out/master.mxf (MPEG-2 4:2:2 50Mbps) も出力
#   ./assemble.sh --clean    → テロップ無し版 out/clean.mp4 も出力（局で字幕を入れる場合用）
set -euo pipefail
cd "$(dirname "$0")"

MXF=0; CLEAN=0
for a in "$@"; do
  case "$a" in
    --mxf) MXF=1 ;;
    --clean) CLEAN=1 ;;
    *) echo "unknown option: $a" >&2; exit 1 ;;
  esac
done

FONT=${FONT:-/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf}
W=1920; H=1080; FPS=30000/1001
TOTAL=60
mkdir -p out/tmp

# 1) 各カットを規格(1920x1080, 29.97p, 尺ぴったり)にそろえる
list=out/tmp/concat.txt; : > "$list"
tail -n +2 shots.csv | while IFS=, read -r id start dur label; do
  src=""
  for ext in mp4 mov webm mkv; do [ -f "clips/$id.$ext" ] && src="clips/$id.$ext" && break; done
  dst="out/tmp/$id.mp4"
  if [ -n "$src" ]; then
    echo "[$id] $src"
    # 足りない尺は最終フレームを止めて延長、長い分はカット
    ffmpeg -nostdin -v error -y -i "$src" -an \
      -vf "scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H,setsar=1,fps=$FPS,tpad=stop_mode=clone:stop_duration=$dur,format=yuv420p" \
      -t "$dur" -c:v libx264 -crf 16 -preset medium "$dst"
  else
    echo "[$id] (クリップ無し → 仮カード)"
    ffmpeg -nostdin -v error -y -f lavfi -i "color=c=0x2b2b3a:s=${W}x${H}:r=$FPS:d=$dur" \
      -vf "drawtext=fontfile=$FONT:text='$id':fontsize=120:fontcolor=0xFFA500:x=(w-tw)/2:y=h/2-160,\
drawtext=fontfile=$FONT:text='$label':fontsize=56:fontcolor=white:x=(w-tw)/2:y=h/2,\
drawtext=fontfile=$FONT:text='%{pts\:hms\:$start}':fontsize=40:fontcolor=0xAAAAAA:x=(w-tw)/2:y=h/2+120,format=yuv420p" \
      -c:v libx264 -crf 18 -preset veryfast "$dst"
  fi
  echo "file '$id.mp4'" >> "$list"
done

ffmpeg -nostdin -v error -y -f concat -safe 0 -i "$list" -c copy out/tmp/video.mp4

# 2) 音声: voice + bgm をミックス（無ければ無音）
inputs=(); filt=""; n=0
for f in audio/voice.wav audio/bgm.wav audio/bgm.mp3 audio/se.wav; do
  [ -f "$f" ] || continue
  case "$f" in *bgm*) [ "${have_bgm:-0}" = 1 ] && continue; have_bgm=1; vol=${BGM_VOL:-0.35} ;; *) vol=1.0 ;; esac
  inputs+=(-i "$f"); filt+="[$((n+1)):a]aresample=48000,volume=$vol,apad[a$n];"; n=$((n+1))
done
if [ "$n" -eq 0 ]; then
  inputs+=(-f lavfi -i "anullsrc=r=48000:cl=stereo"); filt="[1:a]anull[mix]"; 
else
  for ((i=0;i<n;i++)); do filt+="[a$i]"; done
  filt+="amix=inputs=$n:normalize=0,aformat=channel_layouts=stereo[mixraw];[mixraw]loudnorm=I=-24:TP=-2:LRA=7[mix]"
fi

# 3) テロップ焼き込み＋音声合成 → マスター
encode () { # $1=出力 $2=映像フィルタ
  ffmpeg -nostdin -v error -y -i out/tmp/video.mp4 "${inputs[@]}" \
    -filter_complex "$filt;[0:v]$2[v]" -map "[v]" -map "[mix]" -t $TOTAL \
    -c:v libx264 -crf 14 -preset slow -pix_fmt yuv420p -r $FPS \
    -c:a aac -b:a 320k -ar 48000 -movflags +faststart "$1"
}
encode out/master.mp4 "ass=telop.ass:fontsdir=fonts"
echo "→ out/master.mp4"
[ "$CLEAN" = 1 ] && encode out/clean.mp4 "null" && echo "→ out/clean.mp4"

if [ "$MXF" = 1 ]; then
  ffmpeg -nostdin -v error -y -i out/master.mp4 \
    -c:v mpeg2video -pix_fmt yuv422p -b:v 50M -minrate 50M -maxrate 50M -bufsize 17825792 \
    -g 12 -bf 2 -intra_vlc 1 -non_linear_quant 1 -dc 10 -q:v 1 -qmin 1 -qmax 12 \
    -c:a pcm_s24le -ar 48000 -f mxf out/master.mxf
  echo "→ out/master.mxf （局の搬入仕様と必ず照合してください）"
fi

# 4) 確認: 尺とラウドネス
ffprobe -v error -show_entries format=duration -of default=nw=1 out/master.mp4
ffmpeg -hide_banner -nostats -i out/master.mp4 -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 || true
