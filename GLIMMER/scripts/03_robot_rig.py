"""P6 CHAR_001 rig — rigid-part armature + drivers (track phase, eye brightness)."""
import bpy, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()

BONES = {
    # name: (head, tail, parent)
    "ROOT":            ((0, 0, 0),        (0, 0.12, 0),     None),
    "BODY_MAIN":       ((0, 0, 0.115),    (0, 0, 0.30),     "ROOT"),
    "HEAD_YAW":        ((0, 0, 0.33),     (0, 0, 0.40),     "BODY_MAIN"),
    "HEAD_PITCH":      ((0, 0, 0.40),     (0, 0, 0.50),     "HEAD_YAW"),
    "EYE_L_AIM":       ((0.062, -0.140, 0.485), (0.062, -0.20, 0.485), "HEAD_PITCH"),
    "EYE_R_AIM":       ((-0.062, -0.140, 0.485), (-0.062, -0.20, 0.485), "HEAD_PITCH"),
    "ANTENNA_BASE":    ((0, 0.02, 0.62),  (0, 0.035, 0.735), "HEAD_PITCH"),
    "ANTENNA_TIP":     ((0, 0.035, 0.735), (0, 0.10, 0.82),  "ANTENNA_BASE"),
    "ARM_L_SHOULDER":  ((0.088, 0, 0.30), (0.088, 0, 0.235), "BODY_MAIN"),
    "ARM_L_ELBOW":     ((0.088, 0, 0.235), (0.088, 0, 0.17), "ARM_L_SHOULDER"),
    "ARM_L_WRIST":     ((0.088, 0, 0.17), (0.088, 0, 0.115), "ARM_L_ELBOW"),
    "ARM_R_SHOULDER":  ((-0.088, 0, 0.30), (-0.088, 0, 0.235), "BODY_MAIN"),
    "ARM_R_ELBOW":     ((-0.088, 0, 0.235), (-0.088, 0, 0.17), "ARM_R_SHOULDER"),
    "ARM_R_WRIST":     ((-0.088, 0, 0.17), (-0.088, 0, 0.115), "ARM_R_ELBOW"),
    "FINGER_R_INDEX":  ((-0.088, -0.020, 0.16), (-0.088, -0.028, 0.10), "ARM_R_WRIST"),
    "TRACK_L_CTRL":    ((0, 0.095, 0.075), (0.2, 0.095, 0.075), "ROOT"),
    "TRACK_R_CTRL":    ((0, -0.095, 0.075), (0.2, -0.095, 0.075), "ROOT"),
}

PART_BONE = {
    "CHAR_001_chassis": "BODY_MAIN",
    "CHAR_001_torso": "BODY_MAIN", "CHAR_001_torso_panel": "BODY_MAIN",
    "CHAR_001_rivets": "BODY_MAIN", "CHAR_001_vents": "BODY_MAIN",
    "CHAR_001_neck": "BODY_MAIN",
    "CHAR_001_head": "HEAD_PITCH", "CHAR_001_head_hatch": "HEAD_PITCH",
    "CHAR_001_head_seam": "HEAD_PITCH",
    "CHAR_001_eye_L": "EYE_L_AIM", "CHAR_001_iris_L": "EYE_L_AIM",
    "CHAR_001_eye_R": "EYE_R_AIM", "CHAR_001_iris_R": "EYE_R_AIM",
    "CHAR_001_eye_rim_L": "HEAD_PITCH", "CHAR_001_eye_rim_R": "HEAD_PITCH",
    "CHAR_001_antenna": "ANTENNA_BASE", "CHAR_001_antenna_tip": "ANTENNA_TIP",
    "CHAR_001_shoulder_L": "ARM_L_SHOULDER", "CHAR_001_upperarm_L": "ARM_L_SHOULDER",
    "CHAR_001_forearm_L": "ARM_L_ELBOW", "CHAR_001_hand_L": "ARM_L_WRIST",
    "CHAR_001_shoulder_R": "ARM_R_SHOULDER", "CHAR_001_upperarm_R": "ARM_R_SHOULDER",
    "CHAR_001_forearm_R": "ARM_R_ELBOW", "CHAR_001_hand_R": "ARM_R_WRIST",
    "CHAR_001_finger_R_index": "FINGER_R_INDEX",
}

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    coll = bpy.data.collections["CHAR_001_robot"]

    # ctrl object with custom props
    ctrl = bpy.data.objects.get("CHAR_001_ctrl")
    if not ctrl:
        ctrl = bpy.data.objects.new("CHAR_001_ctrl", None)
        ctrl.empty_display_size = 0.25
        coll.objects.link(ctrl)
    ctrl["EYE_BRIGHTNESS"] = 1.0
    ctrl["TRACK_PHASE"] = 0.0
    ctrl["GAZE_X"] = 0.0
    ctrl["GAZE_Y"] = 0.0

    # armature
    old = bpy.data.objects.get("CHAR_001_rig")
    if old: bpy.data.objects.remove(old, do_unlink=True)
    arm_data = bpy.data.armatures.new("CHAR_001_rig")
    arm = bpy.data.objects.new("CHAR_001_rig", arm_data)
    coll.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    print("PRE_EDIT", flush=True)
    bpy.ops.object.mode_set(mode="EDIT")
    print("IN_EDIT", flush=True)
    for name, (h, t, par) in BONES.items():
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail = h, t
        if par: eb.parent = arm_data.edit_bones[par]
    bpy.ops.object.mode_set(mode="OBJECT")
    print("POST_EDIT", flush=True)
    for pb in arm.pose.bones:
        pb.rotation_mode = "XYZ"

    from mathutils import Matrix as _M
    def bone_parent(ob, bone):
        b = arm.data.bones[bone]
        P_rest = b.matrix_local @ _M.Translation((0.0, b.length, 0.0))
        ob.parent = arm
        ob.parent_type = "BONE"
        ob.parent_bone = bone
        ob.matrix_parent_inverse = P_rest.inverted()

    print("PRE_PARENT", flush=True)
    for pname, bone in PART_BONE.items():
        ob = bpy.data.objects.get(pname)
        if ob: bone_parent(ob, bone)
    # tracks stay on ROOT
    for ob in coll.objects:
        if ob.name.startswith(("CHAR_001_track_", "CHAR_001_wheel_", "CHAR_001_fender_")):
            bone_parent(ob, "ROOT")

    print("PRE_DRIVERS", flush=True)
    for ob in coll.objects:
        if ob.name.startswith("CHAR_001_wheel_"):
            r = ob.get("wheel_radius", 0.035)
            ob.rotation_mode = "XYZ"
            fc = ob.driver_add("rotation_euler", 1)
            d = fc.driver; d.type = "SCRIPTED"
            v = d.variables.new(); v.name = "tp"; v.type = "SINGLE_PROP"
            v.targets[0].id = ctrl; v.targets[0].data_path = '["TRACK_PHASE"]'
            d.expression = "tp / %f" % r
    for side in ("L", "R"):
        pl = bpy.data.objects["CHAR_001_track_plates_%s" % side]
        fc = pl.driver_add("location", 0)
        d = fc.driver; d.type = "SCRIPTED"
        v = d.variables.new(); v.name = "tp"; v.type = "SINGLE_PROP"
        v.targets[0].id = ctrl; v.targets[0].data_path = '["TRACK_PHASE"]'
        d.expression = "(tp % 0.60)"   # wrap inside loop length
    # ---------- drivers: gaze from GAZE_X/Y ----------
    for side, sgn in (("L", 1), ("R", 1)):
        pb = arm.pose.bones["EYE_%s_AIM" % side]
        fc = pb.driver_add("rotation_euler", 0)
        d = fc.driver; d.type = "SCRIPTED"
        v = d.variables.new(); v.name = "gy"; v.type = "SINGLE_PROP"
        v.targets[0].id = ctrl; v.targets[0].data_path = '["GAZE_Y"]'
        d.expression = "gy"
        fc = pb.driver_add("rotation_euler", 1)
        d = fc.driver; d.type = "SCRIPTED"
        v = d.variables.new(); v.name = "gx"; v.type = "SINGLE_PROP"
        v.targets[0].id = ctrl; v.targets[0].data_path = '["GAZE_X"]'
        d.expression = "gx * %f" % sgn
    # ---------- driver: eye brightness into material ----------
    m = bpy.data.materials.get("M_Robot_Eye")
    if m:
        nt = m.node_tree
        node = nt.nodes.get("EYE_BRIGHTNESS")
        if node:
            fc = nt.driver_add('nodes["%s"].outputs[0].default_value' % node.name)
            d = fc.driver; d.type = "SCRIPTED"
            v = d.variables.new(); v.name = "eb"; v.type = "SINGLE_PROP"
            v.targets[0].id = ctrl; v.targets[0].data_path = '["EYE_BRIGHTNESS"]'
            d.expression = "eb"
    print("PRE_SAVE", flush=True)
    G.save(MASTER)
    print("RIG_DONE bones=%d" % len(arm_data.bones))

main()

import os as _os; _os._exit(0)

