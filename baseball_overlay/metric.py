import os
import sys, subprocess, numpy as np
src = sys.argv[1]; out = sys.argv[2]
W, H = 480, 270
cmd = ["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps=1,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
rows = []
t = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    a = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(int)
    white = (a.min(axis=2) > 185) & (a.max(axis=2) - a.min(axis=2) < 40)
    field = white[140:190, :].copy()      # y 560-760 full-res
    field[:, :] &= True
    # tent / bench area under left tent (full-res x 880-1340, y 870-1040)
    tent = white[217:260, 220:335]
    rows.append((t, int(field.sum()), int(tent.sum())))
    t += 1
np.savetxt(out, np.array(rows), fmt="%d")
