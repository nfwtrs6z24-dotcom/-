#!/usr/bin/env bash
# 「ころころ、みかん。」を最初から全部つくる（映像描画 → 音 → 書き出し）
#   ./make.sh            out/master.mp4
#   ./make.sh --mxf      局搬入用の out/master.mxf も
# 必要: python3, ffmpeg, pip install pycairo numpy pyopenjtalk
set -euo pipefail
cd "$(dirname "$0")"
python3 render/audio.py
python3 render/render.py
BGM_VOL=${BGM_VOL:-0.4} ./assemble.sh "$@"
