"""P17 Preview render — per-shot low-res Cycles stills (denoised).
Env: SHOTS="SHOT_001 SHOT_002" | ALL ; RES=480x270 ; SPP=8 ; OUTDIR suffix via TAG
"""
import bpy, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()

def main():
    shots = os.environ.get("SHOTS", "ALL")
    res = os.environ.get("RES", "480x270").split("x")
    resx, resy = int(res[0]), int(res[1])
    spp = int(os.environ.get("SPP", "8"))
    tag = os.environ.get("TAG", "preview")
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    G.setup_cycles(sc, resx, resy, spp, thr=float(os.environ.get("THR", "0.1")))
    names = G.SHOT_ORDER if shots == "ALL" else shots.split()
    for shot in names:
        a, b = G.SHOTS[shot][0], G.SHOTS[shot][1]
        cam = bpy.data.objects["CAM_%s" % shot]
        sc.camera = cam
        outdir = os.path.join(G.ROOT, "renders", tag, shot)
        os.makedirs(outdir, exist_ok=True)
        for f in range(a, b + 1):
            outp = os.path.join(outdir, "frame_%04d.jpg" % f)
            if os.path.exists(outp) and os.environ.get("SKIP_EXISTING", "1") == "1":
                continue
            t = time.time()
            sc.frame_set(f)
            sc.render.filepath = outp
            bpy.ops.render.render(write_still=True)
            print("FR %s %d %.1fs" % (shot, f, time.time() - t), flush=True)
        print("SHOT_RENDER_DONE %s" % shot, flush=True)
    print("PREVIEW_RENDER_DONE", flush=True)

main()

import os as _os; _os._exit(0)

