"""P20 Editorial assembly — per-shot mp4 + 30.0s full film via bundled ffmpeg."""
import os, sys, subprocess, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()

def encode(frames_dir, out_mp4, fps=24):
    cmd = [FF, "-y", "-framerate", str(fps), "-i", os.path.join(frames_dir, "frame_%04d.jpg"),
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", out_mp4]
    subprocess.run(cmd, check=True, capture_output=True)
    print("ENCODED", out_mp4, flush=True)

def main():
    tag = os.environ.get("TAG", "preview")
    out_name = os.environ.get("OUT", "GLIMMER_%s_30S.mp4" % tag.upper())
    base = os.path.join(G.ROOT, "renders", tag)
    ed = os.path.join(G.ROOT, "editorial")
    os.makedirs(ed, exist_ok=True)
    clips = []
    for shot in G.SHOT_ORDER:
        d = os.path.join(base, shot)
        if not os.path.isdir(d):
            print("MISSING", d); continue
        mp4 = os.path.join(ed, "%s_%s.mp4" % (shot, tag))
        encode(d, mp4)
        clips.append(mp4)
    # concat
    lst = os.path.join(ed, "concat_%s.txt" % tag)
    with open(lst, "w") as fh:
        for c in clips:
            fh.write("file '%s'\n" % c)
    out = os.path.join(ed, out_name)
    subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True, capture_output=True)
    # probe
    pr = subprocess.run([FF, "-i", out], capture_output=True, text=True)
    import re
    dur = re.search(r"Duration: ([\d:.]+)", pr.stderr)
    print("FINAL_MOVIE", out, "DURATION", dur.group(1) if dur else "?", flush=True)
    print("EDITORIAL_DONE", flush=True)

main()

import os as _os; _os._exit(0)

