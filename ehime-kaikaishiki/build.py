#!/usr/bin/env python3
"""第33回愛媛県秋季学童軟式野球大会 開会式 — 横型/縦型 書き出しスクリプト

使い方:
    python3 build.py edit.json            # 横・縦の両方
    python3 build.py edit.json --only yoko
    python3 build.py edit.json --only tate

方針:
  * 画面を揺らすエフェクトは使わない（シェイク/ズームパンなし）。
  * カットは edit.json で指定した区切りでのみ切り替える。クロスフェードは任意。
  * 手ブレが目立つ素材だけ clip ごとに "stabilize": true で補正する。
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

FORMATS = {
    "yoko": (1920, 1080),
    "tate": (1080, 1920),
}
FPS = 30
# 少しコントラストを上げて締める、スポーツ向けのグレード
GRADE = "eq=contrast=1.08:saturation=1.12:gamma=0.98,unsharp=5:5:0.4"


def run(cmd):
    print("+", " ".join(str(c) for c in cmd), file=sys.stderr)
    subprocess.run(cmd, check=True)


def ts(sec):
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def to_sec(v):
    if isinstance(v, (int, float)):
        return float(v)
    parts = [float(p) for p in str(v).split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def clip_filter(clip, w, h):
    """素材を指定サイズに合わせる。縦型は横素材から切り出し位置 vx (0〜1) でクロップ。"""
    chain = []
    if clip.get("stabilize"):
        chain.append("deshake=rx=32:ry=32")
    vx = float(clip.get("vx", 0.5))
    vy = float(clip.get("vy", 0.5))
    # アスペクト比を保ったまま画面を埋め、はみ出しを指定位置でクロップ
    chain.append(
        f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos"
    )
    chain.append(f"crop={w}:{h}:(iw-{w})*{vx}:(ih-{h})*{vy}")
    if clip.get("slow"):
        chain.append(f"setpts={1/float(clip['slow'])}*PTS")
    chain += [GRADE, f"fps={FPS}", "format=yuv420p", "setsar=1"]
    return ",".join(chain)


def render_clips(edit, src_dir, work, fmt):
    w, h = FORMATS[fmt]
    outs = []
    for i, clip in enumerate(edit["clips"]):
        out = work / f"{fmt}_{i:03d}.mp4"
        start, end = to_sec(clip["in"]), to_sec(clip["out"])
        slow = float(clip.get("slow", 1))
        af = "aresample=48000"
        if slow != 1:
            af += f",atempo={max(0.5, slow)}"
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-ss", f"{start}", "-to", f"{end}", "-i", str(src_dir / clip["src"]),
            "-f", "lavfi", "-t", f"{(end - start) / slow}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex",
            f"[0:v]{clip_filter(clip, w, h)}[v];"
            f"[0:a]{af}[a0];[a0][1:a]amix=inputs=2:duration=longest:normalize=0[a]",
            "-map", "[v]", "-map", "[a]",
            "-t", f"{(end - start) / slow}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            str(out),
        ])
        outs.append((out, (end - start) / slow, clip))
    return outs


def join_clips(parts, work, fmt):
    """ハードカットでつなぐ。clip に "xfade": 秒 があればその境目だけクロスフェード。"""
    if not any(c.get("xfade") for _, _, c in parts[1:]):
        lst = work / f"{fmt}_list.txt"
        lst.write_text("".join(f"file '{p.resolve()}'\n" for p, _, _ in parts))
        out = work / f"{fmt}_joined.mp4"
        run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
             "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
        return out, sum(d for _, d, _ in parts)

    inputs, fc = [], []
    for p, _, _ in parts:
        inputs += ["-i", str(p)]
    vprev, aprev, total = "0:v", "0:a", parts[0][1]
    for i, (_, dur, clip) in enumerate(parts[1:], start=1):
        x = float(clip.get("xfade", 0))
        if x > 0:
            fc.append(f"[{vprev}][{i}:v]xfade=transition=fade:duration={x}:offset={total - x}[v{i}]")
            fc.append(f"[{aprev}][{i}:a]acrossfade=d={x}[a{i}]")
        else:
            fc.append(f"[{vprev}][{aprev}][{i}:v][{i}:a]concat=n=2:v=1:a=1[v{i}][a{i}]")
        vprev, aprev, total = f"v{i}", f"a{i}", total + dur - x
    out = work / f"{fmt}_joined.mp4"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", ";".join(fc), "-map", f"[{vprev}]", "-map", f"[{aprev}]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-c:a", "aac", "-b:a", "192k", str(out)])
    return out, total


def write_ass(edit, fmt, total, path):
    w, h = FORMATS[fmt]
    tate = fmt == "tate"
    big = 96 if tate else 92
    sub = 54 if tate else 50
    font = edit.get("font", "IPAGothic")
    accent = edit.get("accent_ass", "&H0000C8FF")  # 既定: ゴールド (BGR)
    lines = [
        "[Script Info]", "ScriptType: v4.00+",
        f"PlayResX: {w}", f"PlayResY: {h}", "WrapStyle: 2", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, "
        "Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Title,{font},{big},&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,4,0,1,6,3,5,60,60,0,1",
        f"Style: Sub,{font},{sub},{accent},{accent},&H00101010,&H90000000,-1,0,0,0,100,100,6,0,1,4,2,5,60,60,0,1",
        f"Style: Lower,{font},{sub},&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,-1,0,0,0,100,100,2,0,1,4,2,"
        f"{1 if not tate else 2},70,70,{90 if not tate else 260},1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    cx, cy = w // 2, h // 2
    # タイトル: フェード＋横方向にスッと入る（画面全体は揺らさない）
    # start/end が負の値なら「終わりから何秒前」
    for t in edit.get("titles", []):
        s, e = to_sec(t["start"]), to_sec(t["end"])
        s = total + s if s < 0 else s
        e = total + e if e < 0 else e
        text = t.get(f"text_{fmt}", t["text"])  # 縦型だけ改行位置を変えたいとき用
        main = text.replace("\n", "\\N")
        n = text.count("\n") + 1
        ty = cy - (sub // 2 + 20 if t.get("sub") else 0)
        sy = ty + big * n // 2 + sub // 2 + 30
        lines.append(
            f"Dialogue: 1,{ts(s)},{ts(e)},Title,,0,0,0,,"
            f"{{\\fad(400,400)\\move({cx - 40},{ty},{cx},{ty},0,400)}}{main}")
        if t.get("sub"):
            subtxt = t["sub"].replace("\n", "\\N")
            lines.append(
                f"Dialogue: 1,{ts(s + 0.25)},{ts(e)},Sub,,0,0,0,,"
                f"{{\\fad(400,400)\\move({cx + 40},{sy},{cx},{sy},0,400)}}{subtxt}")
    for t in edit.get("lower_thirds", []):
        s, e = to_sec(t["start"]), to_sec(t["end"])
        lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Lower,,0,0,0,,"
                     f"{{\\fad(250,250)}}{t['text'].replace(chr(10), '\\N')}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finish(edit, joined, total, ass, out, base):
    vf = (f"[0:v]ass={ass}:fontsdir=/usr/share/fonts,"
          f"fade=t=in:st=0:d=0.6,fade=t=out:st={total - 1.5}:d=1.5[v]")
    inputs = ["-i", str(joined)]
    bgm = edit.get("bgm")
    src_vol = float(edit.get("source_volume", 1.0))
    if bgm == "auto":
        # オリジナルBGMを映像の長さで生成し、曲終わりのキメを動画の最後に合わせる
        wav = base / "work" / "bgm_auto.wav"
        run([sys.executable, str(Path(__file__).with_name("bgm.py")), f"{total}", str(wav)])
        bgm_len = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
            capture_output=True, text=True, check=True).stdout)
        inputs += ["-ss", f"{max(0.0, bgm_len - total)}", "-i", str(wav)]
        bgm_vol = float(edit.get("bgm_volume", 0.8))
        af = (f"[0:a]volume={src_vol}[s];[1:a]volume={bgm_vol},afade=t=in:st=0:d=0.5[b];"
              f"[s][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    elif bgm:
        inputs += ["-stream_loop", "-1", "-i", str(base / bgm)]
        bgm_vol = float(edit.get("bgm_volume", 0.8))
        af = (f"[0:a]volume={src_vol}[s];[1:a]volume={bgm_vol},atrim=0:{total},"
              f"afade=t=in:st=0:d=0.5,afade=t=out:st={total - 2.0}:d=2.0[b];"
              f"[s][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]")
    else:
        af = f"[0:a]volume={src_vol},afade=t=out:st={total - 1.0}:d=1.0[a]"
    run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *inputs,
         "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]",
         "-t", f"{total}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "256k", str(out)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edit")
    ap.add_argument("--only", choices=list(FORMATS))
    args = ap.parse_args()

    edit_path = Path(args.edit).resolve()
    base = edit_path.parent
    edit = json.loads(edit_path.read_text(encoding="utf-8"))
    src_dir = base / edit.get("sources_dir", "footage")
    out_dir = base / edit.get("out_dir", "out")
    work = base / "work"
    out_dir.mkdir(exist_ok=True)
    work.mkdir(exist_ok=True)

    for fmt in ([args.only] if args.only else FORMATS):
        parts = render_clips(edit, src_dir, work, fmt)
        joined, total = join_clips(parts, work, fmt)
        ass = work / f"{fmt}.ass"
        write_ass(edit, fmt, total, ass)
        out = out_dir / f"{edit.get('name', 'kaikaishiki')}_{fmt}.mp4"
        finish(edit, joined, total, ass, out, base)
        print(f"書き出し完了: {out} ({total:.1f}s)")

    if not edit.get("keep_work"):
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
