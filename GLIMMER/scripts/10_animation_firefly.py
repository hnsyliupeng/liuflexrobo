"""P15 Hero firefly path animation + swarm drift/glow timing."""
import bpy, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()
S = G.SHOTS
def lf(shot, f): return S[shot][0] + (f - 1)

HAND_TARGET = Vector((-0.021, 3.956, 0.409))

# (global_frame, position, glow)
PATH = [
    (lf("SHOT_005", 1),   (-1.90, 1.30, 1.05), 0.0),
    (lf("SHOT_005", 12),  (-1.75, 1.55, 0.95), 0.0),
    (lf("SHOT_005", 20),  (-1.35, 1.95, 0.88), 0.9),
    (lf("SHOT_005", 35),  (-0.85, 2.45, 0.80), 1.0),
    (lf("SHOT_005", 48),  (-0.62, 2.72, 0.86), 1.0),
    (lf("SHOT_005", 60),  (-0.48, 2.90, 0.74), 1.0),
    (lf("SHOT_005", 66),  (-0.42, 2.98, 0.80), 1.0),
    (lf("SHOT_005", 72),  (-0.46, 2.94, 0.76), 1.0),
    (lf("SHOT_006", 12),  (-0.38, 3.05, 0.66), 1.0),
    (lf("SHOT_006", 30),  (-0.30, 3.15, 0.60), 1.0),
    (lf("SHOT_006", 48),  (-0.24, 3.22, 0.64), 1.0),
    (lf("SHOT_006", 72),  (-0.28, 3.18, 0.58), 1.0),
    (lf("SHOT_007", 18),  (-0.10, 3.55, 0.62), 1.0),
    (lf("SHOT_007", 36),  (0.35, 4.15, 0.68), 1.0),
    (lf("SHOT_007", 54),  (0.62, 4.35, 0.60), 1.0),
    (lf("SHOT_007", 72),  (0.40, 3.85, 0.64), 1.0),
    (lf("SHOT_008", 18),  (0.05, 3.55, 0.62), 1.0),
    (lf("SHOT_008", 45),  (-0.05, 3.83, 0.48), 1.0),
    (lf("SHOT_008", 72),  (-0.028, 3.895, 0.455), 1.0),
    (lf("SHOT_009", 18),  (-0.045, 3.880, 0.430), 1.0),
    (lf("SHOT_009", 30),  (-0.030, 3.930, 0.420), 1.0),
    (lf("SHOT_009", 40),  HAND_TARGET[:], 1.15),
    (lf("SHOT_009", 60),  (HAND_TARGET + Vector((0.002, 0, 0.001)))[:], 1.2),
    (lf("SHOT_010", 1),   (HAND_TARGET + Vector((0.002, 0, 0.001)))[:], 1.2),
    (lf("SHOT_010", 24),  (0.00, 3.93, 0.85), 1.0),
    (lf("SHOT_010", 60),  (0.15, 4.10, 1.15), 1.0),
    (lf("SHOT_010", 108), (0.20, 4.40, 1.45), 1.0),
]

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    root = bpy.data.objects["FX_001_ctrl"]
    root.animation_data_clear()
    for (f, pos, glow) in PATH:
        root.location = pos
        root.keyframe_insert("location", frame=f)
        root["GLOW"] = glow
        root.keyframe_insert('["GLOW"]', frame=f)
    # easing: bezier ease-in-out for arcs; glow smooth
    for fc in root.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = "EASE_IN_OUT"
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
    # GLOW driver -> emission gain
    m = bpy.data.materials.get("M_Firefly_Glow")
    if m:
        nt = m.node_tree
        node = next((n for n in nt.nodes if n.label == "GLOW_GAIN"), None)
        if node:
            nt.animation_data_clear()
            fc = nt.driver_add('nodes["%s"].outputs[0].default_value' % node.name)
            d = fc.driver; d.type = "SCRIPTED"
            v = d.variables.new(); v.name = "g"; v.type = "SINGLE_PROP"
            v.targets[0].id = root; v.targets[0].data_path = '["GLOW"]'
            d.expression = "g"
    # orient abdomen toward S9 camera at landing
    root.rotation_mode = "XYZ"
    for (f, rz) in ((lf("SHOT_009", 30), 0.0), (lf("SHOT_009", 40), 2.50),
                    (lf("SHOT_009", 60), 2.50), (lf("SHOT_010", 1), 2.50), (lf("SHOT_010", 24), 0.0)):
        root.rotation_euler = (0, 0, rz)
        root.keyframe_insert("rotation_euler", frame=f)
    # wing flap: linear ramp prop
    if root.animation_data:
        act = root.animation_data.action
        fc = act.fcurves.new('["FLAP"]', action=None) if False else None
    root["FLAP"] = 0.0
    root.keyframe_insert('["FLAP"]', frame=1)
    root["FLAP"] = 720 * 7.0
    root.keyframe_insert('["FLAP"]', frame=720)
    for fcu in root.animation_data.action.fcurves:
        if fcu.data_path == '["FLAP"]':
            for kp in fcu.keyframe_points:
                kp.interpolation = "LINEAR"

    # ---- swarm drift via GN scene-time offset
    ng = bpy.data.node_groups.get("GN_FireflySwarm")
    if ng and not ng.nodes.get("drift_done"):
        n = ng.nodes
        setpos = next(nd for nd in n if nd.bl_idname == "GeometryNodeSetPosition")
        time_n = n.new("GeometryNodeInputSceneTime"); time_n.name = "drift_done"
        randv = n.new("FunctionNodeRandomValue"); randv.data_type = "FLOAT_VECTOR"
        randv.inputs["Min"].default_value = (-1, -1, -0.6)
        randv.inputs["Max"].default_value = (1, 1, 0.6)
        randv.inputs["Seed"].default_value = 77
        mul1 = n.new("ShaderNodeVectorMath"); mul1.operation = "SCALE"
        sinm = n.new("ShaderNodeMath"); sinm.operation = "SINE"
        tmul = n.new("ShaderNodeMath"); tmul.operation = "MULTIPLY"; tmul.inputs[1].default_value = 0.9
        ng.links.new(time_n.outputs["Seconds"], tmul.inputs[0])
        ph = n.new("ShaderNodeMath"); ph.operation = "MULTIPLY_ADD"
        rph = n.new("FunctionNodeRandomValue"); rph.data_type = "FLOAT"
        rph.inputs[2].default_value = 0.0; rph.inputs[3].default_value = 6.283
        rph.inputs["Seed"].default_value = 88
        ng.links.new(rph.outputs[1], ph.inputs[0])
        ph.inputs[1].default_value = 1.0
        ng.links.new(tmul.outputs[0], ph.inputs[2])
        ng.links.new(ph.outputs[0], sinm.inputs[0])
        ng.links.new(randv.outputs["Value"], mul1.inputs[0])
        ng.links.new(sinm.outputs[0], mul1.inputs["Scale"])
        amp = n.new("ShaderNodeVectorMath"); amp.operation = "SCALE"; amp.inputs["Scale"].default_value = 0.18
        ng.links.new(mul1.outputs[0], amp.inputs[0])
        ng.links.new(amp.outputs[0], setpos.inputs["Offset"])
    G.save(MASTER)
    print("FIREFLY_ANIM_DONE")

main()

import os as _os; _os._exit(0)

