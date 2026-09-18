"""Solve right-arm reach pose so fingertip lands on a reachable target; re-key S8-S10 arm."""
import bpy, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()
S = G.SHOTS
def lf(shot, f): return S[shot][0] + (f - 1)

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    arm = bpy.data.objects["CHAR_001_rig"]
    pb = arm.pose.bones
    sc.frame_set(lf("SHOT_008", 72))
    dg = bpy.context.evaluated_depsgraph_get()
    shw = pb["ARM_R_SHOULDER"].matrix.evaluated_get(dg) if False else None
    shw = arm.matrix_world @ pb["ARM_R_SHOULDER"].matrix @ Vector((0, 0, 0))
    target = shw + Vector((-0.130, -0.095, 0.100))
    print("SOLVE shoulder", [round(v, 3) for v in shw], "target", [round(v, 3) for v in target])

    def fingertip():
        dg = bpy.context.evaluated_depsgraph_get()
        pbone = arm.pose.bones["FINGER_R_INDEX"]
        pbone_eval = arm.evaluated_get(dg).pose.bones["FINGER_R_INDEX"]
        tail = arm.evaluated_get(dg).matrix_world @ pbone_eval.tail
        return tail

    def evaluate(sh_rx, sh_rz, el_rx, wr_rx):
        pb["ARM_R_SHOULDER"].rotation_euler = (math.radians(sh_rx), 0, math.radians(sh_rz))
        pb["ARM_R_ELBOW"].rotation_euler = (math.radians(el_rx), 0, 0)
        pb["ARM_R_WRIST"].rotation_euler = (math.radians(wr_rx), 0, 0)
        bpy.context.view_layer.update()
        return (fingertip() - target).length

    for fc in list(act.fcurves) if (act := arm.animation_data.action) else []:
        if fc.data_path.startswith("pose.bones") and any(b in fc.data_path for b in
           ("ARM_R_SHOULDER", "ARM_R_ELBOW", "ARM_R_WRIST", "FINGER_R_INDEX")):
            fc.mute = True
    best = None
    for sh_rx in range(-100, -19, 12):
        for sh_rz in range(-50, 51, 15):
            for el_rx in range(-70, 1, 14):
                d = evaluate(sh_rx, sh_rz, el_rx, -15)
                if best is None or d < best[0]:
                    best = (d, sh_rx, sh_rz, el_rx)
    d, sh_rx, sh_rz, el_rx = best
    for _ in range(2):
        for dsh in (-6, -3, 0, 3, 6):
            for dshz in (-8, -4, 0, 4, 8):
                for del_ in (-8, -4, 0, 4, 8):
                    dd = evaluate(sh_rx + dsh, sh_rz + dshz, el_rx + del_, -15)
                    if dd < d:
                        d, sh_rx, sh_rz, el_rx = dd, sh_rx + dsh, sh_rz + dshz, el_rx + del_
    print("SOLVE best err=%.4f sh=(%d,%d) el=%d wr=-15" % (d, sh_rx, sh_rz, el_rx))

    # re-key arm across S8 hold -> S9 -> S10 lower
    def key(frame, sh_rx_v, sh_rz_v, el_v, wr_v, fi_v):
        pb["ARM_R_SHOULDER"].rotation_euler = (math.radians(sh_rx_v), 0, math.radians(sh_rz_v))
        pb["ARM_R_ELBOW"].rotation_euler = (math.radians(el_v), 0, 0)
        pb["ARM_R_WRIST"].rotation_euler = (math.radians(wr_v), 0, 0)
        pb["FINGER_R_INDEX"].rotation_euler = (math.radians(fi_v), 0, 0)
        for bn in ("ARM_R_SHOULDER", "ARM_R_ELBOW", "ARM_R_WRIST", "FINGER_R_INDEX"):
            pb[bn].keyframe_insert("rotation_euler", frame=frame)

    act = arm.animation_data.action
    for fc in list(act.fcurves):
        if fc.data_path.startswith("pose.bones") and any(b in fc.data_path for b in
           ("ARM_R_SHOULDER", "ARM_R_ELBOW", "ARM_R_WRIST", "FINGER_R_INDEX")):
            act.fcurves.remove(fc)
    rest = (12, 0, 16, 10, 35)
    key(lf("SHOT_008", 1), *rest)
    key(lf("SHOT_008", 19), rest[0] - 4, rest[1], rest[2] - 4, rest[3], rest[4])
    key(lf("SHOT_008", 45), sh_rx * 0.6 + rest[0] * 0.4, sh_rz * 0.6, el_rx * 0.6 + 16 * 0.4, 0, 20)
    key(lf("SHOT_008", 61), sh_rx, sh_rz, el_rx, -15, 2)
    key(lf("SHOT_008", 72), sh_rx, sh_rz, el_rx, -15, 0)
    key(lf("SHOT_009", 1), sh_rx, sh_rz, el_rx, -15, 0)
    key(lf("SHOT_009", 60), sh_rx, sh_rz, el_rx, -15, 0)
    key(lf("SHOT_010", 1), sh_rx, sh_rz, el_rx, -15, 0)
    key(lf("SHOT_010", 50), 6, 0, 10, 8, 20)
    key(lf("SHOT_010", 108), 6, 0, 10, 8, 20)
    for fc in act.fcurves:
        if fc.data_path.startswith("pose.bones"):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"; kp.easing = "EASE_IN_OUT"
    # report final fingertip at S9 hold
    sc.frame_set(lf("SHOT_009", 40))
    print("SOLVE fingertip@592", [round(v, 3) for v in fingertip()])
    with open(os.path.join(G.ROOT, "caches", "solve_target.txt"), "w") as fh:
        fh.write("%.4f %.4f %.4f\n" % (target.x, target.y, target.z))
    G.save(MASTER)
    print("ARM_SOLVE_DONE")

main()

import os as _os; _os._exit(0)

