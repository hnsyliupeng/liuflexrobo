"""Fix bone-parent bind matrices (rigid parts), eye emission gain, misc look fixes."""
import bpy, math, os, sys
from mathutils import Matrix
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    arm = bpy.data.objects["CHAR_001_rig"]
    # rest-pose bone matrices in armature space
    sc.frame_set(1)
    fixed = 0
    for ob in bpy.data.objects:
        if ob.parent_type == "BONE" and ob.parent == arm:
            bone = arm.data.bones.get(ob.parent_bone)
            if not bone:
                continue
            P_rest = bone.matrix_local @ Matrix.Translation((0.0, bone.length, 0.0))
            ob.matrix_parent_inverse = P_rest.inverted()
            fixed += 1
    # verify head height at rest
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    he = bpy.data.objects["CHAR_001_head"].evaluated_get(dg)
    print("HEAD_Z_AFTER_FIX %.3f" % he.matrix_world.translation.z)

    # ---- eye emission gain x8
    m = bpy.data.materials.get("M_Robot_Eye")
    if m and m.node_tree.nodes.get("EYE_GAIN"):
        m.node_tree.nodes["EYE_GAIN"].inputs[1].default_value = 4.0
    if m and not m.node_tree.nodes.get("EYE_GAIN"):
        nt = m.node_tree
        em = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeEmission")
        mul = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeMath" and n.operation == "MULTIPLY"
                   and n.inputs[0].links and n.inputs[1].links)
        gain = nt.nodes.new("ShaderNodeMath"); gain.operation = "MULTIPLY"
        gain.name = gain.label = "EYE_GAIN"
        gain.inputs[1].default_value = 4.0
        nt.links.new(mul.outputs[0], gain.inputs[0])
        nt.links.new(gain.outputs[0], em.inputs["Strength"])
    # firefly: tame emission + warm practical light (no clipping, real local illumination)
    mg = bpy.data.materials.get("M_Firefly_Glow")
    if mg:
        muln = next((n for n in mg.node_tree.nodes if n.bl_idname == "ShaderNodeMath" and n.operation == "MULTIPLY"), None)
        if muln: muln.inputs[1].default_value = 6.0
    root = bpy.data.objects.get("FX_001_ctrl")
    if root:
        old = bpy.data.objects.get("LIGHT_ff_practical")
        if old: bpy.data.objects.remove(old, do_unlink=True)
        pl = bpy.data.objects.new("LIGHT_ff_practical", bpy.data.lights.new("LIGHT_ff_practical", "POINT"))
        pl.data.color = (0.75, 0.9, 0.25)
        pl.data.shadow_soft_size = 0.02
        bpy.data.collections["FX_fireflies"].objects.link(pl)
        pl.parent = root
        pl.location = (0.0, -0.020, 0.020)
        pl.data.energy = 2.0
        fc = pl.data.driver_add("energy")
        d = fc.driver; d.type = "SCRIPTED"
        v = d.variables.new(); v.name = "g"; v.type = "SINGLE_PROP"
        v.targets[0].id = root; v.targets[0].data_path = '["GLOW"]'
        d.expression = "g * 4.0"
        # cap GLOW keys at 1.0
        if root.animation_data and root.animation_data.action:
            for fcu in root.animation_data.action.fcurves:
                if fcu.data_path == '["GLOW"]':
                    for kp in fcu.keyframe_points:
                        if kp.co.y > 1.0: kp.co.y = 1.0
    if root:
        root.scale = (0.45, 0.45, 0.45)
    G.ensure_slots()
    G.save(MASTER)
    print("LOOKFIX_DONE fixed=%d" % fixed)

main()

import os as _os; _os._exit(0)

