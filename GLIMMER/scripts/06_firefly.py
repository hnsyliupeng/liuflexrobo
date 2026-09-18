"""P8 FX_001 hero firefly + FX_010 swarm (geometry nodes, deterministic seed)."""
import bpy, bmesh, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G, matlib as M

MASTER = G.master_path()

def clean(name):
    old = bpy.data.collections.get(name)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    return G.get_coll(name)

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    mats = {m.name: m for m in bpy.data.materials}
    for k in ("M_Firefly_Glow", "M_Firefly_Body", "M_Firefly_Wing", "M_Swarm_Dot"):
        if k not in mats:
            M.build_all(); mats = {m.name: m for m in bpy.data.materials}; break
    coll = clean("FX_fireflies")

    # ---------------- hero firefly (structured insect) ----------------
    bm = bmesh.new()
    # abdomen (emissive), thorax, head — elongated along +Y (forward = -Y later via rig)
    G.bm_sphere(bm, radius=0.011, segs=14, rings=10, loc=(0, 0.012, 0), scale=(0.8, 1.5, 0.8))
    abd = G.mesh_obj("FX_001_abdomen", coll, bm); G.shade_smooth(abd)
    abd.data.materials.append(mats["M_Firefly_Glow"])
    bm = bmesh.new()
    G.bm_sphere(bm, radius=0.010, segs=12, rings=8, loc=(0, -0.004, 0.001), scale=(0.85, 1.1, 0.9))
    G.bm_sphere(bm, radius=0.007, segs=10, rings=8, loc=(0, -0.016, 0.002))
    body = G.mesh_obj("FX_001_body", coll, bm); G.shade_smooth(body)
    body.data.materials.append(mats["M_Firefly_Body"])
    # wings: two thin elongated planes, hinged at thorax
    for side, s in (("L", 1), ("R", -1)):
        bm = bmesh.new()
        rows = []
        n = 6
        for i in range(n + 1):
            t = i / n
            w = 0.006 * math.sin(t * math.pi) ** 0.6 + 0.0008
            y = -0.004 - t * 0.026
            x = s * (0.004 + t * 0.004)
            rows.append((bm.verts.new((x - w, y, 0.004)), bm.verts.new((x + w, y, 0.004))))
        for i in range(n):
            bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
        wg = G.mesh_obj("FX_001_wing_%s" % side, coll, bm)
        wg.data.materials.append(mats["M_Firefly_Wing"])
    # parent wings/body to abdomen root empty
    root = bpy.data.objects.new("FX_001_ctrl", None)
    root.empty_display_size = 0.05
    coll.objects.link(root)
    for nm in ("FX_001_abdomen", "FX_001_body", "FX_001_wing_L", "FX_001_wing_R"):
        ob = bpy.data.objects[nm]
        mw = ob.matrix_world.copy()
        ob.parent = root
        ob.matrix_world = mw
    # wing flap drivers (fast, subtle)
    for side, s in (("L", 1), ("R", -1)):
        ob = bpy.data.objects["FX_001_wing_%s" % side]
        ob.rotation_mode = "XYZ"
        fc = ob.driver_add("rotation_euler", 1)
        d = fc.driver; d.type = "SCRIPTED"
        v = d.variables.new(); v.name = "f"; v.type = "SINGLE_PROP"
        v.targets[0].id = root; v.targets[0].data_path = '["FLAP"]'
        d.expression = "(0.5 + 0.45*sin(f*1.0)) * %f" % s
    root["FLAP"] = 0.0

    # ---------------- swarm dot instance source ----------------
    bm = bmesh.new()
    G.bm_sphere(bm, radius=0.010, segs=8, rings=6)
    dot = G.mesh_obj("FX_010_dot_src", coll, bm); G.shade_smooth(dot)
    dot.data.materials.append(mats["M_Swarm_Dot"])
    dot.location = (0, 0, -20)   # park below ground; instanced via GN

    # ---------------- swarm GN object ----------------
    me = bpy.data.meshes.new("FX_010_swarm_base")
    swarm = bpy.data.objects.new("FX_010_swarm", me)
    coll.objects.link(swarm)
    ng = bpy.data.node_groups.new("GN_FireflySwarm", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n = ng.nodes
    out = n.new("NodeGroupOutput")
    pts = n.new("GeometryNodePoints")
    pts.inputs["Count"].default_value = 900
    setpos = n.new("GeometryNodeSetPosition")
    # random position in layered volumes: deep forest shell around hero tree
    rand = n.new("FunctionNodeRandomValue")
    rand.data_type = "FLOAT_VECTOR"
    rand.inputs["Min"].default_value = (-14.0, -8.0, 0.15)
    rand.inputs["Max"].default_value = (14.0, 16.0, 4.5)
    rand.inputs["Seed"].default_value = 4
    ng.links.new(rand.outputs["Value"], setpos.inputs["Position"])
    ng.links.new(pts.outputs["Points"], setpos.inputs["Geometry"])
    # cluster bias: pull 60% of points toward root/tree zone via second random + mix by id parity
    idx = n.new("GeometryNodeInputIndex")
    mod2 = n.new("ShaderNodeMath"); mod2.operation = "MODULO"; mod2.inputs[1].default_value = 2.0
    ng.links.new(idx.outputs["Index"], mod2.inputs[0])
    rand2 = n.new("FunctionNodeRandomValue")
    rand2.data_type = "FLOAT_VECTOR"
    rand2.inputs["Min"].default_value = (-4.5, 0.5, 0.2)
    rand2.inputs["Max"].default_value = (4.5, 8.5, 3.2)
    rand2.inputs["Seed"].default_value = 9
    mixv = n.new("ShaderNodeMix"); mixv.data_type = "VECTOR"
    ng.links.new(mod2.outputs[0], mixv.inputs["Factor"])
    ng.links.new(rand.outputs["Value"], mixv.inputs[4])   # A vector
    ng.links.new(rand2.outputs["Value"], mixv.inputs[5])  # B vector
    ng.links.new(mixv.outputs[1], setpos.inputs["Position"])
    # per-point phase attribute
    store = n.new("GeometryNodeStoreNamedAttribute")
    store.data_type = "FLOAT"; store.domain = "POINT"
    store.inputs["Name"].default_value = "ff_phase"
    rphase = n.new("FunctionNodeRandomValue")
    rphase.data_type = "FLOAT"
    rphase.inputs[2].default_value = 0.0
    rphase.inputs[3].default_value = 1.0
    rphase.inputs["Seed"].default_value = 21
    ng.links.new(rphase.outputs[1], store.inputs["Value"])
    ng.links.new(setpos.outputs["Geometry"], store.inputs["Geometry"])
    # instance dots
    iop = n.new("GeometryNodeInstanceOnPoints")
    objinfo = n.new("GeometryNodeObjectInfo")
    objinfo.inputs["Object"].default_value = dot
    objinfo.transform_space = "ORIGINAL"
    ng.links.new(store.outputs["Geometry"], iop.inputs["Points"])
    ng.links.new(objinfo.outputs["Geometry"], iop.inputs["Instance"])
    # random scale
    rs = n.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"
    rs.inputs[2].default_value = 0.5; rs.inputs[3].default_value = 1.4
    rs.inputs["Seed"].default_value = 33
    ng.links.new(rs.outputs[1], iop.inputs["Scale"])
    ng.links.new(iop.outputs["Instances"], out.inputs["Geometry"])
    mod = swarm.modifiers.new("gn", "NODES")
    mod.node_group = ng
    G.save(MASTER)
    print("FIREFLY_DONE")

main()

import os as _os; _os._exit(0)

