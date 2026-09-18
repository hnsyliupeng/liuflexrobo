"""P16 Lighting states A (dusk) / B (blue night transition) / C (firefly night) on global timeline."""
import bpy, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()

def key(node_sock, frame, value):
    node_sock.default_value = value
    node_sock.keyframe_insert("default_value", frame=frame)

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    lc = G.get_coll("LAY_lights")
    for ob in list(lc.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    # ---------------- world ----------------
    w = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    if not bg:
        bg = w.node_tree.nodes.new("ShaderNodeBackground")
        w.node_tree.links.new(bg.outputs[0], w.node_tree.nodes["World Output"].inputs["Surface"])
    if w.node_tree.animation_data: w.node_tree.animation_data_clear()
    # STATE A dusk
    key(bg.inputs["Color"], 1,   (0.16, 0.10, 0.05, 1))
    key(bg.inputs["Strength"], 1, 0.30)
    key(bg.inputs["Color"], 192, (0.14, 0.09, 0.045, 1))
    key(bg.inputs["Strength"], 192, 0.26)
    # STATE B transition -> deep blue
    key(bg.inputs["Color"], 240, (0.030, 0.055, 0.120, 1))
    key(bg.inputs["Strength"], 240, 0.30)
    key(bg.inputs["Color"], 264, (0.012, 0.024, 0.060, 1))
    key(bg.inputs["Strength"], 264, 0.55)
    # STATE C firefly night
    key(bg.inputs["Color"], 720, (0.010, 0.020, 0.052, 1))
    key(bg.inputs["Strength"], 720, 0.52)

    # ---------------- sun (dusk) + moon (night) ----------------
    sun = bpy.data.objects.new("LIGHT_sun", bpy.data.lights.new("LIGHT_sun", "SUN"))
    lc.objects.link(sun)
    sun.data.angle = math.radians(1.5)
    sun.rotation_euler = (math.radians(70), 0, math.radians(-55))
    sun.data.color = (1.0, 0.55, 0.22)
    sun.data.energy = 3.5
    sun.data.keyframe_insert("energy", frame=1)
    sun.data.energy = 3.2; sun.data.keyframe_insert("energy", frame=192)
    sun.data.energy = 1.2; sun.data.keyframe_insert("energy", frame=225)
    sun.data.color = (1.0, 0.55, 0.22); sun.data.keyframe_insert("color", frame=192)
    sun.data.color = (0.55, 0.62, 0.95); sun.data.keyframe_insert("color", frame=245)
    sun.data.energy = 0.0; sun.data.keyframe_insert("energy", frame=264)
    sun.data.energy = 0.0; sun.data.keyframe_insert("energy", frame=720)
    # sun sinks during transition
    sun.rotation_euler = (math.radians(78), 0, math.radians(-55))
    sun.keyframe_insert("rotation_euler", frame=192)
    sun.rotation_euler = (math.radians(88), 0, math.radians(-55))
    sun.keyframe_insert("rotation_euler", frame=264)

    moon = bpy.data.objects.new("LIGHT_moon", bpy.data.lights.new("LIGHT_moon", "SUN"))
    lc.objects.link(moon)
    moon.data.angle = math.radians(6)
    moon.data.color = (0.45, 0.60, 1.0)
    moon.rotation_euler = (math.radians(38), 0, math.radians(160))
    moon.data.energy = 0.0; moon.data.keyframe_insert("energy", frame=240)
    moon.data.energy = 0.16; moon.data.keyframe_insert("energy", frame=280)
    moon.data.energy = 0.14; moon.data.keyframe_insert("energy", frame=720)

    # ---------------- dusk god-ray spots (shots 1-3) ----------------
    for i, (loc, tgt) in enumerate((((-3.2, -8.0, 6.5), (-1.6, -7.3, 0.0)),
                                    ((-3.6, -3.6, 6.5), (-4.8, -1.5, 0.0)))):
        sp = bpy.data.objects.new("LIGHT_shaft_%d" % i, bpy.data.lights.new("LIGHT_shaft_%d" % i, "SPOT"))
        lc.objects.link(sp)
        sp.location = loc
        d = Vector(tgt) - Vector(loc)
        sp.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        sp.data.spot_size = math.radians(28)
        sp.data.spot_blend = 0.4
        sp.data.color = (1.0, 0.62, 0.25)
        sp.data.energy = 13000
        sp.data.keyframe_insert("energy", frame=1)
        sp.data.energy = 2200; sp.data.keyframe_insert("energy", frame=192)
        sp.data.energy = 0; sp.data.keyframe_insert("energy", frame=250)
        sp.data.energy = 0; sp.data.keyframe_insert("energy", frame=720)

    # ---------------- warm character fill for dusk shots ----------------
    cf = bpy.data.objects.new("LIGHT_char_fill", bpy.data.lights.new("LIGHT_char_fill", "AREA"))
    lc.objects.link(cf)
    cf.location = (-0.6, -9.6, 1.7)
    d = Vector((-1.7, -7.0, 0.4)) - cf.location
    cf.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cf.data.size = 2.0
    cf.data.color = (1.0, 0.72, 0.42)
    cf.data.energy = 30; cf.data.keyframe_insert("energy", frame=1)
    cf.data.energy = 26; cf.data.keyframe_insert("energy", frame=192)
    cf.data.energy = 0; cf.data.keyframe_insert("energy", frame=235)
    cf.data.energy = 0; cf.data.keyframe_insert("energy", frame=720)

    # ---------------- night rim / fill ----------------
    rim = bpy.data.objects.new("LIGHT_night_rim", bpy.data.lights.new("LIGHT_night_rim", "AREA"))
    lc.objects.link(rim)
    rim.location = (-4.5, 7.5, 5.2)
    d = Vector((0.2, 4.0, 0.5)) - rim.location
    rim.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    rim.data.size = 6.0
    rim.data.color = (0.35, 0.5, 0.95)
    rim.data.energy = 0; rim.data.keyframe_insert("energy", frame=240)
    rim.data.energy = 60; rim.data.keyframe_insert("energy", frame=280)
    rim.data.energy = 55; rim.data.keyframe_insert("energy", frame=720)
    fill = bpy.data.objects.new("LIGHT_night_fill", bpy.data.lights.new("LIGHT_night_fill", "AREA"))
    lc.objects.link(fill)
    fill.location = (-1.9, 1.4, 2.3)
    d = Vector((0.2, 4.0, 0.4)) - fill.location
    fill.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    fill.data.size = 4.0
    fill.data.color = (0.30, 0.42, 0.80)
    fill.data.energy = 0; fill.data.keyframe_insert("energy", frame=250)
    fill.data.energy = 18; fill.data.keyframe_insert("energy", frame=290)
    fill.data.energy = 16; fill.data.keyframe_insert("energy", frame=720)

    # ---------------- dedicated cool character key for night act ----------------
    rk = bpy.data.objects.new("LIGHT_robot_key", bpy.data.lights.new("LIGHT_robot_key", "AREA"))
    lc.objects.link(rk)
    rk.location = (-1.4, 2.0, 2.0)
    d = Vector((0.2, 4.0, 0.42)) - rk.location
    rk.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    rk.data.size = 2.5
    rk.data.color = (0.42, 0.55, 0.95)
    rk.data.energy = 0; rk.data.keyframe_insert("energy", frame=240)
    rk.data.energy = 90; rk.data.keyframe_insert("energy", frame=280)
    rk.data.energy = 80; rk.data.keyframe_insert("energy", frame=720)

    # ---------------- mist density keys ----------------
    mm = bpy.data.materials.get("M_Mist")
    if mm:
        nt = mm.node_tree
        mr = next((n for n in nt.nodes if n.bl_idname == "ShaderNodeMapRange"), None)
        if mr:
            if nt.animation_data: nt.animation_data_clear()
            key(mr.inputs["To Min"], 1, 0.020)
            key(mr.inputs["To Min"], 192, 0.016)
            key(mr.inputs["To Min"], 264, 0.009)
            key(mr.inputs["To Min"], 613, 0.011)
            key(mr.inputs["To Min"], 720, 0.011)
    G.save(MASTER)
    print("LIGHTING_DONE")

main()

import os as _os; _os._exit(0)

