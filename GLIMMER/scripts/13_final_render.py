"""P19 Final-quality render (1920x1080, high spp). Per user directive the delivered package
contains parameter-locked project + low-res validation renders; this module renders
representative final frames (one per shot) to prove final-quality feasibility.
Env: SHOTS="SHOT_001 ..." default = 4 representative shots."""
import bpy, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()
REPR = {"SHOT_001": 36, "SHOT_006": 372, "SHOT_009": 590, "SHOT_010": 690}

def main():
    shots = os.environ.get("SHOTS", " ".join(REPR.keys())).split()
    res = os.environ.get("RES", "1920x1080").split("x")
    spp = int(os.environ.get("SPP", "64"))
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    G.setup_cycles(sc, int(res[0]), int(res[1]), spp, thr=0.02)
    for shot in shots:
        f = int(os.environ.get("FRAME_%s" % shot, REPR.get(shot, G.SHOTS[shot][0])))
        sc.camera = bpy.data.objects["CAM_%s" % shot]
        outdir = os.path.join(G.ROOT, "renders", "final", shot)
        os.makedirs(outdir, exist_ok=True)
        t = time.time()
        sc.frame_set(f)
        sc.render.filepath = os.path.join(outdir, "frame_%04d.jpg" % f)
        bpy.ops.render.render(write_still=True)
        print("FINAL_FR %s %d %.1fs" % (shot, f, time.time() - t), flush=True)
    print("FINAL_RENDER_DONE", flush=True)

main()

import os as _os; _os._exit(0)

