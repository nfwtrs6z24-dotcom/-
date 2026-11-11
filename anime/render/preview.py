"""確認用: 各カットの静止画を並べたコンタクトシートを書き出す。
python3 preview.py OUT.png [S01:0.5,S02:3 ...]"""
import sys
import cairo
from common import W, H
import post
import scenes

out = sys.argv[1]
specs = sys.argv[2].split(',') if len(sys.argv) > 2 else [f'S{i:02d}:{f}' for i in range(1, 11) for f in (0.5,)]
cols = 3
rows = (len(specs) + cols - 1) // cols
sheet = cairo.ImageSurface(cairo.FORMAT_RGB24, cols * W // 3, rows * H // 3)
sc = cairo.Context(sheet)
cache = {}
for i, sp in enumerate(specs):
    name, tt = sp.split(':')
    if name not in cache:
        cache[name] = getattr(scenes, name)()
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    fr = bytearray(post.render_frame(cache[name], s, cairo, float(tt), 1001 / 30000, i, name).tobytes())
    s = cairo.ImageSurface.create_for_data(fr, cairo.FORMAT_RGB24, W, H, W * 4)
    sc.save()
    sc.translate((i % cols) * W / 3, (i // cols) * H / 3)
    sc.scale(1 / 3, 1 / 3)
    sc.set_source_surface(s)
    sc.paint()
    sc.restore()
    sc.set_source_rgb(1, 1, 0)
    sc.move_to((i % cols) * W / 3 + 8, (i // cols) * H / 3 + 22)
    sc.set_font_size(20)
    sc.show_text(sp)
sheet.write_to_png(out)
