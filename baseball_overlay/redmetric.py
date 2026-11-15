import os
import sys, subprocess, numpy as np
src, out = sys.argv[1], sys.argv[2]
W, H = 480, 270
cmd = ["ffmpeg", "-nostdin", "-v", "error", "-i", src, "-map", "0:v:0", "-vf", f"fps=1,scale={W}:{H}",
       "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
rows = []
t = 0
while True:
    b = p.stdout.read(W * H * 3)
    if len(b) < W * H * 3:
        break
    a = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(int)
    r, g, bl = a[..., 0], a[..., 1], a[..., 2]
    red = (r > 120) & (r - g > 55) & (r - bl > 45)
    navy = (bl > r + 10) & (bl > g) & (r < 90) & (bl < 140)
    fld = slice(70, 200)          # field band (outfield+infield) excluding foreground
    rows.append((t, int(red[fld].sum()), int(navy[fld].sum()), int(red[180:250, 80:300].sum())))
    t += 1
np.savetxt(out, np.array(rows), fmt="%d")
