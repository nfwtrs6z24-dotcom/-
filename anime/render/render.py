"""全カットを描画して ../clips/S01.mp4 〜 S10.mp4 に書き出す。
python3 render.py            全カット
python3 render.py S03 S04    指定カットだけ
"""
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import cairo

from common import W, H
import post
import scenes

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, '..', 'clips')


def render(name):
    cls = getattr(scenes, name)
    shot = cls()
    n = math.ceil(shot.dur * 30000 / 1001) + 1
    out = os.path.join(CLIPS, f'{name}.mp4')
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
                          '-r', '30000/1001', '-i', '-', '-c:v', 'libx264', '-crf', '12', '-preset', 'medium',
                          '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    t0 = time.time()
    for i in range(n):
        frame = post.render_frame(shot, surf, cairo, i * 1001 / 30000, 1001 / 30000, i, name)
        p.stdin.write(frame.tobytes())
    p.stdin.close()
    p.wait()
    return f'{name}: {n} frames, {time.time() - t0:.0f}s'


if __name__ == '__main__':
    os.makedirs(CLIPS, exist_ok=True)
    names = sys.argv[1:] or [c.__name__ for c in scenes.SHOTS]
    with Pool(min(4, len(names))) as pool:
        for msg in pool.imap_unordered(render, names):
            print(msg, flush=True)
