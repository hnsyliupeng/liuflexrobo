"""P9 Layout — 10 cameras, robot per-shot placement, hero prop (twig), firefly markers."""
import bpy, bmesh, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()
S = G.SHOTS

# robot root (armature object) placement per shot: (frame, loc, yaw_deg) constant between cuts
ROBOT_PLACEMENT = [
    (1,   (-1.65, -8.60, 0.0), 178),
    (73,  (-4.55, -1.95, 0.0), 219),
    (145, (-4.70, -1.70, 0.0), 210),
    (193, (0.20, 4.05, 0.0),   0),
    (613, (0.20, 4.05, 0.0),   0),
]
# within-shot root motion (walking): (shot, lf_start, lf_end, loc_end, yaw_end)
ROBOT_MOVES = [
    ("SHOT_001", 1, 72, (-1.78, -6.60, 0.0), 180),
    ("SHOT_003", 145, 192, (-4.92, -1.28, 0.0), 210),
]

CAM_DEFS = {
    # shot: lens, [(global_frame, loc, look_at, extra)]
    "SHOT_001": (28, [(1, (-1.60, -12.60, 1.50), (-1.70, -5.0, 0.70)),
                      (72, (-1.62, -12.00, 1.45), (-1.72, -5.0, 0.68))], 4.0),
    "SHOT_002": (40, [(73, (-3.30, -3.60, 0.72), (-5.30, -0.60, 0.55)),
                      (144, (-3.30, -3.60, 0.72), (-5.30, -0.60, 0.55))], 2.8),
    "SHOT_003": (65, [(145, (-5.32, -2.35, 0.14), (-4.66, -1.62, 0.10)),
                      (192, (-5.45, -1.90, 0.13), (-4.80, -1.18, 0.10))], 2.0),
    "SHOT_004": (50, [(193, (0.25, 2.35, 0.62), (0.20, 4.05, 0.42)),
                      (264, (0.25, 1.45, 0.72), (0.20, 4.05, 0.45))], 2.8),
    "SHOT_005": (55, [(265, (0.62, 4.72, 0.78), (-0.55, 2.4, 0.72)),
                      (336, (0.62, 4.72, 0.78), (-0.55, 2.4, 0.72))], 2.0),
    "SHOT_006": (75, [(337, (-0.52, 3.05, 0.60), (0.16, 4.02, 0.50)),
                      (408, (-0.44, 3.20, 0.58), (0.16, 4.02, 0.52))], 1.6),
    "SHOT_007": (50, [(409, (-0.85, 3.05, 0.62), (0.20, 4.05, 0.52)),
                      (480, (-0.35, 2.85, 0.66), (0.20, 4.05, 0.54))], 2.2),
    "SHOT_008": (55, [(481, (1.15, 3.05, 0.50), (0.02, 3.98, 0.43)),
                      (552, (1.12, 3.02, 0.49), (0.00, 3.96, 0.43))], 2.8),
    "SHOT_009": (90, [(553, (-0.28, 3.63, 0.46), (-0.021, 3.956, 0.400)),
                      (612, (-0.22, 3.69, 0.45), (-0.021, 3.956, 0.400))], 2.8),
    "SHOT_010": (32, [(613, (0.30, -0.30, 0.95), (0.20, 4.3, 0.75)),
                      (720, (0.30, -2.10, 3.30), (0.20, 5.0, 1.10))], 5.6),
}
FOCUS = {
    "SHOT_001": (-1.75, -7.6, 0.4), "SHOT_002": (-4.55, -1.9, 0.4), "SHOT_003": (-4.75, -1.55, 0.1),
    "SHOT_004": (0.2, 4.0, 0.45), "SHOT_005": (-0.5, 2.6, 0.75), "SHOT_006": (0.16, 4.0, 0.5),
    "SHOT_007": (0.2, 4.0, 0.52), "SHOT_008": (-0.02, 3.93, 0.43), "SHOT_009": (-0.021, 3.956, 0.400),
    "SHOT_010": (0.2, 4.2, 0.6),
}

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    coll = G.get_coll("LAY_cameras")
    for ob in list(coll.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    rig = bpy.data.objects["CHAR_001_rig"]
    # ---- robot placement keys (constant across cuts, linear within moves)
    rig.animation_data_clear()
    rig.rotation_mode = "XYZ"
    for (f, loc, yaw) in ROBOT_PLACEMENT:
        rig.location = loc
        rig.rotation_euler = (0, 0, math.radians(yaw))
        rig.keyframe_insert("location", frame=f)
        rig.keyframe_insert("rotation_euler", frame=f)
    for (shot, a, b, loc_end, yaw_end) in ROBOT_MOVES:
        rig.location = loc_end
        rig.rotation_euler = (0, 0, math.radians(yaw_end))
        rig.keyframe_insert("location", frame=b)
        rig.keyframe_insert("rotation_euler", frame=b)
    for fc in rig.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
    # constant jumps: set interpolation CONSTANT just before cut frames
    for (f, loc, yaw) in ROBOT_PLACEMENT[1:]:
        for fc in rig.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                if abs(kp.co.x - f) < 0.5:
                    kp.interpolation = "CONSTANT"

    # ---- cameras
    for shot, (lens, keys, fstop) in CAM_DEFS.items():
        cd = bpy.data.cameras.new("CAM_%s" % shot)
        cd.lens = lens
        cd.sensor_width = 36
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cam = bpy.data.objects.new("CAM_%s" % shot, cd)
        coll.objects.link(cam)
        for (f, loc, look) in keys:
            cam.location = loc
            d = Vector(look) - Vector(loc)
            cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
            cam.keyframe_insert("location", frame=f)
            cam.keyframe_insert("rotation_euler", frame=f)
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_IN_OUT"
        # focus empty
        fe = bpy.data.objects.new("FOCUS_%s" % shot, None)
        fe.empty_display_size = 0.1
        fe.location = FOCUS[shot]
        coll.objects.link(fe)
        cd.dof.focus_object = fe

    # ---- hero twig for SHOT_003 (break anim in 09)
    old = bpy.data.objects.get("PROP_twig_hero")
    if old: bpy.data.objects.remove(old, do_unlink=True)
    bm = bmesh.new()
    n = 8
    rows = []
    for i in range(n + 1):
        t = i / n
        r = 0.006 * (1 - t * 0.6)
        x = t * 0.34
        z = 0.008 + 0.004 * math.sin(t * 5)
        c = bmesh.ops.create_circle(bm, cap_ends=True, segments=6, radius=r)
        vs = c["verts"]
        from mathutils import Matrix
        bmesh.ops.transform(bm, matrix=Matrix.Translation((x, 0, z)), verts=vs)
        rows.append(vs)
    for i in range(n):
        a, b = rows[i], rows[i + 1]
        for j in range(6):
            bm.faces.new((a[j], a[(j + 1) % 6], b[(j + 1) % 6], b[j]))
    twig = G.mesh_obj("PROP_twig_hero", bpy.data.collections["ENV_001_scene"], bm)
    twig.location = (-5.05, -1.55, 0.015)
    twig.rotation_euler = (0, 0, math.radians(115))
    twig.data.materials.append(bpy.data.materials["M_DarkWood"])
    # break pivot empty at 60% length
    piv = bpy.data.objects.new("PROP_twig_break", None)
    piv.empty_display_size = 0.05
    bpy.data.collections["ENV_001_scene"].objects.link(piv)
    mw = twig.matrix_world @ Vector((0.20, 0, 0.008))
    piv.location = mw
    # ---- camera clearance: remove scatter blocking lenses / sight lines
    import mathutils
    removed = 0
    for shot in CAM_DEFS:
        cam = bpy.data.objects["CAM_%s" % shot]
        fe = bpy.data.objects["FOCUS_%s" % shot]
        a = cam.location; b = fe.location
        ab = b - a; L2 = ab.length_squared
        for ob in list(bpy.data.collections["ENV_001_scene"].objects):
            if not ob.name.startswith(("ENV_fern", "ENV_leaf", "ENV_twig", "ENV_rock", "ENV_gmoss")):
                continue
            p = ob.location
            if (p - a).length < 0.55:
                bpy.data.objects.remove(ob, do_unlink=True); removed += 1; continue
            t = max(0.0, min(1.0, (p - a).dot(ab) / L2))
            if (p - (a + ab * t)).length < 0.30:
                bpy.data.objects.remove(ob, do_unlink=True); removed += 1
    print("CLEARANCE_REMOVED", removed)
    G.ensure_slots()
    G.save(MASTER)
    print("LAYOUT_DONE cams=%d" % len(CAM_DEFS))

main()

import os as _os; _os._exit(0)

