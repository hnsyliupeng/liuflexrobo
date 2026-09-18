"""Repair material slots after matlib rebuild incident; rebind eye driver."""
import bpy, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G
MASTER = G.master_path()

RULES = [
    (("CHAR_001_head", "CHAR_001_torso", "CHAR_001_torso_panel", "CHAR_001_chassis",
      "CHAR_001_fender_L", "CHAR_001_fender_R"), "M_Robot_Paint"),
    (("CHAR_001_eye_rim_L", "CHAR_001_eye_rim_R"), "M_Robot_EyeRim"),
    (("CHAR_001_eye_L", "CHAR_001_eye_R", "CHAR_001_iris_L", "CHAR_001_iris_R"), "M_Robot_Eye"),
    (("CHAR_001_track_plates_L", "CHAR_001_track_plates_R"), "M_Track"),
]
PREFIX_RULES = [
    (("TREE_TRUNK_", "ROOT_", "ENV_hero_tree", "ENV_root", "ENV_midtree"), "M_Bark_Wet"),
    (("BACKGROUND_TREE", "ENV_bgtree"), "M_Bark_BG"),
    (("FALLEN_LOG", "ENV_fallen_log", "TWIG_", "ENV_twig"), "M_DarkWood"),
    (("FERN_", "ENV_fern"), "M_Fern"),
    (("MOSS_PATCH_", "ENV_rootmoss", "ENV_logmoss", "ENV_gmoss"), "M_Moss"),
    (("GROUND_LEAF_", "ENV_leaf"), "M_WetLeaves"),
    (("ROCK_SMALL", "ENV_rock"), "M_Stone"),
    (("ENV_mist",), "M_Mist"),
    (("ENV_ground",), "M_Mud"),
]
METAL_PREFIX = ("CHAR_001_hatch", "CHAR_001_seam", "CHAR_001_head_hatch", "CHAR_001_head_seam",
                "CHAR_001_rivets", "CHAR_001_vents", "CHAR_001_neck", "CHAR_001_shoulder",
                "CHAR_001_upperarm", "CHAR_001_forearm", "CHAR_001_hand", "CHAR_001_finger",
                "CHAR_001_wheel", "CHAR_001_antenna")

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    M = {m.name: m for m in bpy.data.materials}
    fixed = 0
    for ob in bpy.data.objects:
        if not ob.data or not hasattr(ob.data, "materials"):
            continue
        target = None
        for names, mat in RULES:
            if ob.name in names: target = mat; break
        if not target:
            for pref, mat in PREFIX_RULES:
                if ob.name.startswith(pref): target = mat; break
        if not target and ob.name.startswith(METAL_PREFIX): target = "M_Robot_Metal"
        if target and target in M:
            if len(ob.data.materials) == 0:
                ob.data.materials.append(M[target])
            elif ob.data.materials[0] is None:
                ob.data.materials[0] = M[target]
            fixed += 1
    # rebind eye brightness driver
    ctrl = bpy.data.objects.get("CHAR_001_ctrl")
    m = M.get("M_Robot_Eye")
    if m and ctrl:
        nt = m.node_tree
        node = next((n for n in nt.nodes if n.name == "EYE_BRIGHTNESS" or n.label == "EYE_BRIGHTNESS"), None)
        if node:
            try:
                nt.animation_data_clear()
            except Exception: pass
            fc = nt.driver_add('nodes["%s"].outputs[0].default_value' % node.name)
            d = fc.driver; d.type = "SCRIPTED"
            v = d.variables.new(); v.name = "eb"; v.type = "SINGLE_PROP"
            v.targets[0].id = ctrl; v.targets[0].data_path = '["EYE_BRIGHTNESS"]'
            d.expression = "eb"
            print("EYE_DRIVER_REBOUND")
    G.save(MASTER)
    print("FIXED_SLOTS:", fixed)
    print("FIX_DONE")

main()

import os as _os; _os._exit(0)

