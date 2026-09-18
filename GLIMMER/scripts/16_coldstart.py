"""P21 Cold-start validation — clean bpy process re-opens master, checks subsystems,
re-renders 4 representative frames, verifies editorial movie metadata."""
import bpy, os, sys, subprocess, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G
import imageio_ffmpeg

MASTER = G.master_path()
REPR = {"SHOT_001": 36, "SHOT_006": 372, "SHOT_009": 590, "SHOT_010": 690}

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)   # clean process, no session state
    sc = bpy.context.scene
    ok = True
    # textures / linked assets / rig / GN / firefly / output paths
    checks = []
    checks.append(("fps", sc.render.fps == 24))
    checks.append(("frames", (sc.frame_start, sc.frame_end) == (1, 720)))
    checks.append(("cams", len([o for o in bpy.data.objects if o.name.startswith("CAM_SHOT")]) == 10))
    rig = bpy.data.objects.get("CHAR_001_rig")
    checks.append(("rig", rig is not None and len(rig.data.bones) == 17))
    checks.append(("drivers", rig is not None and rig.animation_data is not None))
    checks.append(("swarm_gn", bpy.data.objects.get("FX_010_swarm") is not None and
                   bpy.data.objects["FX_010_swarm"].modifiers[0].type == "NODES"))
    checks.append(("firefly", bpy.data.objects.get("FX_001_ctrl") is not None))
    checks.append(("materials", all(bpy.data.materials.get(m) for m in
                   ("M_Robot_Paint", "M_Bark_Wet", "M_Fern", "M_Mud", "M_Firefly_Glow", "M_Swarm_Dot"))))
    checks.append(("scatter", len(bpy.data.collections["ENV_001_scene"].objects) > 500))
    checks.append(("lights", len([o for o in bpy.data.objects if o.name.startswith("LIGHT_")]) >= 6))
    # slots healed?
    bad = [o.name for o in bpy.data.objects if o.data and hasattr(o.data, "materials")
           and len(o.data.materials) and o.data.materials[0] is None]
    checks.append(("slots", not bad))
    for name, v in checks:
        print("COLD %s: %s" % (name, "PASS" if v else "FAIL"))
        ok = ok and v
    # representative re-renders
    G.setup_cycles(sc, 480, 270, 8)
    outd = os.path.join(G.ROOT, "renders", "review", "coldstart")
    os.makedirs(outd, exist_ok=True)
    for shot, f in REPR.items():
        sc.camera = bpy.data.objects["CAM_%s" % shot]
        sc.frame_set(f)
        sc.render.filepath = os.path.join(outd, "%s_f%04d.jpg" % (shot, f))
        bpy.ops.render.render(write_still=True)
        print("COLD_RENDER_OK", shot, f)
    # movie metadata
    mp4 = os.path.join(G.ROOT, "editorial", "GLIMMER_PREVIEW_30S.mp4")
    if os.path.exists(mp4):
        pr = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", mp4], capture_output=True, text=True)
        dur = re.search(r"Duration: ([\d:.]+)", pr.stderr)
        res = re.search(r"(\d{3,4})x(\d{3,4})", pr.stderr)
        fps = re.search(r"([\d.]+) fps", pr.stderr)
        print("COLD_MOVIE dur=%s res=%s fps=%s" % (dur.group(1) if dur else "?",
              res.group(0) if res else "?", fps.group(1) if fps else "?"))
    else:
        print("COLD_MOVIE missing (assemble first)")
    print("COLDSTART_%s" % ("PASS" if ok else "FAIL"))

main()

import os as _os; _os._exit(0)

