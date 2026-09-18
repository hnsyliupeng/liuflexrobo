"""P3/P5 CHAR_001_LITTLE_ROBOT — structural model (rigid parts, real mechanical detail).
Run: python 02_robot_model.py   (opens/creates master blend, adds robot, saves)
"""
import bpy, bmesh, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G, matlib as M

MASTER = G.master_path()

def open_or_new():
    if os.path.exists(MASTER):
        bpy.ops.wm.open_mainfile(filepath=MASTER)
    else:
        G.new_master()
    return bpy.context.scene

def main():
    sc = open_or_new()
    old = bpy.data.collections.get("CHAR_001_robot")
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    for cu in list(bpy.data.curves):
        if cu.users == 0: bpy.data.curves.remove(cu)
    coll = G.get_coll("CHAR_001_robot")
    mats = M.build_all()
    mp, mm, mt, me, mer = (mats["mat_robot_paint"], mats["mat_robot_metal"],
                           mats["mat_rubber_track"], mats["mat_eye"], mats["mat_eye_rim"])

    P = {}  # part objects

    # ---------------- HEAD (sphere r .16 @ z .475, slightly squashed) ----------------
    bm = bmesh.new()
    G.bm_sphere(bm, radius=0.16, segs=32, rings=24, loc=(0, 0, 0), scale=(1.0, 0.96, 0.94))
    # panel seam: equatorial groove via inset ring (boolean-free: add slight ridge torus separately)
    head = G.mesh_obj("CHAR_001_head", coll, bm)
    head.location = (0, 0, 0.475)
    G.add_subsurf(head, 1, 2); G.shade_smooth(head)
    head.data.materials.append(mp); P["head"] = head
    # head seam ridge + top hatch
    bm = bmesh.new()
    G.bm_cyl(bm, radius=0.045, depth=0.02, segs=16, loc=(0, 0.02, 0.148))
    hatch = G.mesh_obj("CHAR_001_head_hatch", coll, bm)
    hatch.location = (0, 0, 0.475); G.add_bevel(hatch, 0.004, 2)
    hatch.data.materials.append(mm); P["hatch"] = hatch
    bm = bmesh.new()
    r = bmesh.ops.create_circle(bm, cap_ends=False, segments=48, radius=0.158)
    seam = G.mesh_obj("CHAR_001_head_seam", coll, bm)
    seam.location = (0, 0, 0.475); seam.rotation_euler = (math.radians(90), 0, 0)
    sk = seam.modifiers.new("skin", "SKIN") if False else None
    sol = seam.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.004
    seam.data.materials.append(mm); P["seam"] = seam

    # ---------------- EYES (rim + emissive lens), gaze pivots at eye centers --------
    for side, sy in (("L", 1), ("R", -1)):
        ex, ez = 0.062 * sy, 0.485
        bm = bmesh.new()
        G.bm_cyl(bm, radius=0.049, depth=0.022, segs=24, loc=(0, 0, 0), rot=G.rot_x(90))
        rim = G.mesh_obj("CHAR_001_eye_rim_%s" % side, coll, bm)
        rim.location = (ex, -0.132, ez)
        G.add_bevel(rim, 0.003, 2); G.shade_smooth(rim, 60)
        rim.data.materials.append(mer); P["eye_rim_" + side] = rim
        bm = bmesh.new()
        G.bm_sphere(bm, radius=0.040, segs=24, rings=16, loc=(0, 0, 0), scale=(1, 0.55, 1))
        lens = G.mesh_obj("CHAR_001_eye_%s" % side, coll, bm)
        lens.location = (ex, -0.140, ez)
        G.shade_smooth(lens)
        lens.data.materials.append(me); P["eye_" + side] = lens
        # iris core (brighter inner disc)
        bm = bmesh.new()
        G.bm_sphere(bm, radius=0.017, segs=16, rings=12, loc=(0, 0, 0), scale=(1, 0.4, 1))
        iris = G.mesh_obj("CHAR_001_iris_%s" % side, coll, bm)
        iris.location = (ex, -0.156, ez)
        G.shade_smooth(iris)
        iris.data.materials.append(me); P["iris_" + side] = iris

    # ---------------- ANTENNA (thin rod, bent tip, drooped) -------------------------
    cu = bpy.data.curves.new("CHAR_001_antenna", "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(3)
    pts = [(0, 0.02, 0.145), (0, 0.035, 0.26), (0, 0.055, 0.33), (0, 0.10, 0.345)]
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
    cu.bevel_depth = 0.0035; cu.bevel_resolution = 3; cu.use_fill_caps = True
    ant = bpy.data.objects.new("CHAR_001_antenna", cu)
    coll.objects.link(ant); ant.location = (0, 0, 0.475)
    ant.data.materials.append(mm); P["antenna"] = ant
    bm = bmesh.new(); G.bm_sphere(bm, radius=0.011, segs=12, rings=8, loc=(0, 0.10, 0.345))
    tip = G.mesh_obj("CHAR_001_antenna_tip", coll, bm)
    tip.location = (0, 0, 0.475); G.shade_smooth(tip)
    tip.data.materials.append(mm); P["ant_tip"] = tip

    # ---------------- TORSO (box + panels + rivets + vents) -------------------------
    bm = bmesh.new()
    G.bm_cube(bm, size=(0.15, 0.115, 0.13), loc=(0, 0, 0))
    torso = G.mesh_obj("CHAR_001_torso", coll, bm)
    torso.location = (0, 0, 0.265)
    G.add_bevel(torso, 0.010, 3); torso.data.materials.append(mp); P["torso"] = torso
    # front panel + chest light housing
    bm = bmesh.new()
    G.bm_cube(bm, size=(0.09, 0.012, 0.07), loc=(0, -0.062, 0.01))
    G.bm_cyl(bm, radius=0.016, depth=0.014, segs=12, loc=(0.0, -0.068, 0.032), rot=G.rot_x(90))
    panel = G.mesh_obj("CHAR_001_torso_panel", coll, bm)
    panel.location = (0, 0, 0.265); G.add_bevel(panel, 0.003, 2)
    panel.data.materials.append(mp); P["panel"] = panel
    # rivets
    bm = bmesh.new()
    for sx in (-1, 1):
        for sz in (-1, 1):
            G.bm_sphere(bm, radius=0.006, segs=8, rings=6, loc=(0.062 * sx, -0.059, 0.01 + 0.045 * sz))
    for sy in (-1, 1):
        G.bm_sphere(bm, radius=0.006, segs=8, rings=6, loc=(0.076 * sy, 0.0, -0.05))
    riv = G.mesh_obj("CHAR_001_rivets", coll, bm)
    riv.location = (0, 0, 0.265); G.shade_smooth(riv, 60)
    riv.data.materials.append(mm); P["rivets"] = riv
    # side vents
    bm = bmesh.new()
    for i in range(3):
        G.bm_cube(bm, size=(0.006, 0.05, 0.008), loc=(0.077, 0.01, -0.01 + i * 0.018))
        G.bm_cube(bm, size=(0.006, 0.05, 0.008), loc=(-0.077, 0.01, -0.01 + i * 0.018))
    vents = G.mesh_obj("CHAR_001_vents", coll, bm)
    vents.location = (0, 0, 0.265); vents.data.materials.append(mm); P["vents"] = vents
    # neck
    bm = bmesh.new(); G.bm_cyl(bm, radius=0.035, depth=0.05, segs=12, loc=(0, 0, 0.10))
    neck = G.mesh_obj("CHAR_001_neck", coll, bm)
    neck.location = (0, 0, 0.265); G.shade_smooth(neck, 60)
    neck.data.materials.append(mm); P["neck"] = neck

    # ---------------- ARMS (shoulder ball, upper, elbow, fore, wrist, hand) --------
    for side, sx in (("L", 1), ("R", -1)):
        sh = (0.088 * sx, 0.0, 0.30)
        bm = bmesh.new(); G.bm_sphere(bm, radius=0.028, segs=16, rings=12, loc=(0, 0, 0))
        sho = G.mesh_obj("CHAR_001_shoulder_%s" % side, coll, bm)
        sho.location = sh; G.shade_smooth(sho)
        sho.data.materials.append(mm); P["shoulder_" + side] = sho
        # upper arm (built along -Z from shoulder pivot)
        bm = bmesh.new()
        G.bm_cyl(bm, radius=0.014, depth=0.060, segs=12, loc=(0, 0, -0.032))
        G.bm_sphere(bm, radius=0.019, segs=12, rings=10, loc=(0, 0, -0.065))
        ua = G.mesh_obj("CHAR_001_upperarm_%s" % side, coll, bm)
        ua.location = sh; G.shade_smooth(ua, 60)
        ua.data.materials.append(mm); P["upperarm_" + side] = ua
        el = (sh[0], sh[1], sh[2] - 0.065)
        # forearm from elbow pivot
        bm = bmesh.new()
        G.bm_cyl(bm, radius=0.012, depth=0.055, segs=12, loc=(0, 0, -0.030))
        G.bm_cyl(bm, radius=0.014, depth=0.018, segs=12, loc=(0, 0, -0.058))
        fa = G.mesh_obj("CHAR_001_forearm_%s" % side, coll, bm)
        fa.location = el; G.shade_smooth(fa, 60)
        fa.data.materials.append(mm); P["forearm_" + side] = fa
        wr = (el[0], el[1], el[2] - 0.065)
        # hand: palm + curled fingers (merged) ; index separate for R
        bm = bmesh.new()
        G.bm_cube(bm, size=(0.030, 0.034, 0.016), loc=(0, 0, -0.012))
        for i, fy in enumerate((-0.011, 0.0, 0.011)):
            if side == "R" and i == 1:
                continue  # index finger separate
            G.bm_cube(bm, size=(0.009, 0.010, 0.030), loc=(0, fy - 0.020, -0.028))
            G.bm_cube(bm, size=(0.008, 0.009, 0.016), loc=(0, fy - 0.030, -0.046))
        G.bm_cube(bm, size=(0.009, 0.024, 0.010), loc=(0.016 * sx, -0.008, -0.020))  # thumb
        hd = G.mesh_obj("CHAR_001_hand_%s" % side, coll, bm)
        hd.location = wr; G.add_bevel(hd, 0.002, 2)
        hd.data.materials.append(mm); P["hand_" + side] = hd
        if side == "R":
            bm = bmesh.new()
            G.bm_cube(bm, size=(0.009, 0.010, 0.034), loc=(0, -0.020, -0.028))
            G.bm_cube(bm, size=(0.008, 0.009, 0.020), loc=(0, -0.026, -0.052))
            G.bm_sphere(bm, radius=0.006, segs=10, rings=8, loc=(0, -0.028, -0.062))
            idx = G.mesh_obj("CHAR_001_finger_R_index", coll, bm)
            idx.location = wr; G.add_bevel(idx, 0.0015, 2)
            idx.data.materials.append(mm); P["finger_R_index"] = idx

    # ---------------- CHASSIS + TRACKS ----------------------------------------------
    bm = bmesh.new()
    G.bm_cube(bm, size=(0.20, 0.16, 0.05), loc=(0, 0, 0))
    ch = G.mesh_obj("CHAR_001_chassis", coll, bm)
    ch.location = (0, 0, 0.115); G.add_bevel(ch, 0.008, 2)
    ch.data.materials.append(mp); P["chassis"] = ch
    TRACK_L = 0.62  # loop length approx (computed below from curve)
    for side, sy in (("L", 0.095), ("R", -0.095)):
        # track loop curve (elongated ellipse in XZ)
        cu = bpy.data.curves.new("track_loop_%s" % side, "CURVE"); cu.dimensions = "3D"
        sp = cu.splines.new("BEZIER"); sp.bezier_points.add(5)
        pts = [(-0.115, 0, 0.045), (0.0, 0, 0.075), (0.115, 0, 0.045),
               (0.135, 0, 0.0), (0.0, 0, -0.028), (-0.135, 0, 0.0)]
        for bp, p in zip(sp.bezier_points, pts):
            bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
        sp.use_cyclic_u = True
        loop = bpy.data.objects.new("CHAR_001_track_curve_%s" % side, cu)
        coll.objects.link(loop); loop.location = (0, sy, 0.075)
        P["track_curve_" + side] = loop
        # tread plate segment
        bm = bmesh.new()
        G.bm_cube(bm, size=(0.028, 0.055, 0.010), loc=(0, 0, 0))
        G.bm_cube(bm, size=(0.008, 0.055, 0.016), loc=(0.008, 0, -0.008))  # grouser
        plate = G.mesh_obj("CHAR_001_track_plates_%s" % side, coll, bm)
        plate.location = (0, sy, 0.075)
        ar = plate.modifiers.new("arr", "ARRAY")
        ar.fit_type = "FIT_CURVE"; ar.curve = loop
        ar.relative_offset_displace = (1.05, 0, 0)
        cvm = plate.modifiers.new("cur", "CURVE"); cvm.object = loop; cvm.deform_axis = "POS_X"
        plate.data.materials.append(mt); P["track_plates_" + side] = plate
        # wheels: drive sprocket + idler + 3 road wheels
        wheels = []
        for i, (wx, wz, wr_) in enumerate(((-0.115, 0.045, 0.045), (0.115, 0.045, 0.045),
                                           (-0.055, -0.005, 0.030), (0.0, -0.008, 0.030), (0.055, -0.005, 0.030))):
            bm = bmesh.new()
            G.bm_cyl(bm, radius=wr_, depth=0.045, segs=16, loc=(0, 0, 0), rot=G.rot_x(90))
            G.bm_cyl(bm, radius=wr_ * 0.4, depth=0.052, segs=10, loc=(0, 0, 0), rot=G.rot_x(90))
            w = G.mesh_obj("CHAR_001_wheel_%s_%d" % (side, i), coll, bm)
            w.location = (wx, sy, 0.075 + wz)
            G.shade_smooth(w, 60)
            w.data.materials.append(mm)
            w["wheel_radius"] = wr_
            wheels.append(w)
        P["wheels_" + side] = wheels
        # track housing fender
        bm = bmesh.new()
        G.bm_cube(bm, size=(0.24, 0.018, 0.055), loc=(0, 0.033 * (1 if sy > 0 else 1), 0.055))
        fen = G.mesh_obj("CHAR_001_fender_%s" % side, coll, bm)
        fen.location = (0, sy, 0.075); G.add_bevel(fen, 0.006, 2)
        fen.data.materials.append(mp); P["fender_" + side] = fen

    # store loop length on plates for drivers
    dg = bpy.context.evaluated_depsgraph_get()
    for side in ("L", "R"):
        loop = P["track_curve_" + side]
        le = loop.evaluated_get(dg)
        L = sum((le.data.splines[0].bezier_points[i].co - le.data.splines[0].bezier_points[(i + 1) % len(le.data.splines[0].bezier_points)].co).length for i in range(len(le.data.splines[0].bezier_points)))
        # better: use evaluated curve length via mesh conversion
        me = le.to_mesh()
        L = 0.0
        edges = {tuple(sorted(e.vertices)) for e in me.edges}
        le.to_mesh_clear()
        P["track_plates_" + side]["track_loop_len"] = 0.62  # placeholder, refined in rig script

    sc.frame_set(1)
    G.ensure_slots()
    G.save(MASTER)
    print("ROBOT_PARTS:", len(coll.objects))
    print("MODEL_DONE")

main()

import os as _os; _os._exit(0)

