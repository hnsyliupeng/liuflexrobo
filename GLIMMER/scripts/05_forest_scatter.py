"""P7 ENV_001 assembly — canonical forest, layered scatter (HERO/PRIMARY/SECONDARY/BACKGROUND)."""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G, matlib as M

MASTER = G.master_path()
R = random.Random(11)

def clean(name):
    old = bpy.data.collections.get(name)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    return G.get_coll(name)

def inst(src, coll, loc, rot_z=0.0, rot_x=0.0, rot_y=0.0, scale=1.0, name=None):
    ob = src.copy()   # shares mesh data
    ob.location = loc
    ob.rotation_euler = (math.radians(rot_x), math.radians(rot_y), math.radians(rot_z))
    ob.scale = (scale, scale, scale)
    coll.objects.link(ob)
    if name: ob.name = name
    return ob

def ground_height(dg, x, y, zmax=6.0):
    hit, loc, nrm, idx, ob, mat = bpy.context.scene.ray_cast(dg, Vector((x, y, zmax)), Vector((0, 0, -1)))
    return loc.z if hit else 0.0

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    mats = {m.name: m for m in bpy.data.materials}
    if "M_Mud" not in mats:
        M.build_all()
        mats = {m.name: m for m in bpy.data.materials}
    A = {ob.name: ob for ob in bpy.data.collections["ENV_001_assets"].objects}

    coll = clean("ENV_001_scene")

    # ---------------- ground ----------------
    bm = bmesh.new()
    N = 96; S = 46.0
    grid = {}
    for i in range(N + 1):
        for j in range(N + 1):
            x = (i / N - 0.5) * S; y = (j / N - 0.5) * S
            grid[(i, j)] = bm.verts.new((x, y, 0))
    for i in range(N):
        for j in range(N):
            bm.faces.new((grid[(i, j)], grid[(i + 1, j)], grid[(i + 1, j + 1)], grid[(i, j + 1)]))
    ground = G.mesh_obj("ENV_ground", coll, bm)
    t1 = G.new_tex("ground_lumps", "CLOUDS", noise_scale=2.5, noise_depth=3)
    G.add_displace(ground, t1, strength=0.5, mid=0.5)
    t2 = G.new_tex("ground_fine", "STUCCI", noise_scale=0.35)
    G.add_displace(ground, t2, strength=0.09, mid=0.5)
    G.shade_smooth(ground)
    ground.data.materials.append(mats["M_Mud"])

    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()

    def gz(x, y):
        hit, loc, nrm, idx = ground.ray_cast(Vector((x, y, 6.0)), Vector((0, 0, -1)))
        return loc.z if hit else 0.0

    # ---------------- hero tree + roots (PRIMARY) ----------------
    inst(A["TREE_TRUNK_A"], coll, (0.4, 6.2, gz(0.4, 6.2) - 0.1), rot_z=15, name="ENV_hero_tree")
    root_spots = [(-1.6, 4.4, 200, 1.15), (1.9, 4.6, -25, 1.0), (-0.4, 3.9, 185, 0.9),
                  (2.6, 6.6, -60, 1.2), (-2.6, 6.4, 240, 1.1), (0.9, 3.6, 175, 0.75)]
    for i, (x, y, rz, s) in enumerate(root_spots):
        src = A["ROOT_%s" % "ABC"[i % 3]]
        inst(src, coll, (x, y, gz(x, y) - 0.06), rot_z=rz, scale=s, name="ENV_root_%d" % i)
    # moss on roots
    for i, (x, y, rz, s) in enumerate(root_spots[:4]):
        mx, my = x + 0.5 * math.cos(math.radians(rz)), y + 0.5 * math.sin(math.radians(rz))
        inst(A["MOSS_PATCH_A"], coll, (mx, my, gz(mx, my) + 0.10), rot_z=R.uniform(0, 360), scale=s * 0.9, name="ENV_rootmoss_%d" % i)

    # ---------------- fallen log (PRIMARY) ----------------
    lx, ly = -6.0, 0.2
    inst(A["FALLEN_LOG_HERO"], coll, (lx, ly, gz(lx, ly) - 0.05), rot_z=28, name="ENV_fallen_log")
    for i in range(5):
        t = (i + 0.5) / 5
        a = math.radians(28)
        px = lx + (t - 0.5) * 7.0 * math.cos(a); py = ly + (t - 0.5) * 7.0 * math.sin(a)
        inst(A["MOSS_PATCH_%s" % "AB"[i % 2]], coll, (px, py, gz(px, py) + 0.95 - 0.12 * i % 2), rot_z=R.uniform(0, 360), scale=R.uniform(0.8, 1.3), name="ENV_logmoss_%d" % i)

    # ---------------- mid trees (PRIMARY/SECONDARY) ----------------
    mid = [(-5.5, 2.0, "B", 1.0), (4.8, 1.2, "C", 1.1), (-4.2, -4.5, "C", 0.9), (6.0, -3.0, "B", 0.85),
           (-7.5, -1.0, "B", 1.2), (3.2, -6.5, "C", 1.0)]
    for i, (x, y, k, s) in enumerate(mid):
        inst(A["TREE_TRUNK_%s" % k], coll, (x, y, gz(x, y) - 0.1), rot_z=R.uniform(0, 360), scale=s, name="ENV_midtree_%d" % i)

    # ---------------- background ring (BACKGROUND) ----------------
    for i in range(60):
        a = 2 * math.pi * i / 60 + R.uniform(-0.08, 0.08)
        r = R.uniform(11.0, 19.0)
        x, y = math.cos(a) * r, math.sin(a) * r + 3
        inst(A["BACKGROUND_TREE"], coll, (x, y, -0.3), rot_z=R.uniform(0, 360), scale=R.uniform(0.8, 1.5), name="ENV_bgtree_%d" % i)

    # ---------------- ferns (HERO near path & roots, SECONDARY elsewhere) --------
    fern_spots = []
    for i in range(34):   # path corridor
        fern_spots.append((R.uniform(-3.6, 1.6), R.uniform(-10.5, -0.5), R.uniform(0.7, 1.3)))
    for i in range(20):   # root area
        fern_spots.append((R.uniform(-3.4, 3.4), R.uniform(1.5, 6.0), R.uniform(0.7, 1.2)))
    for i in range(24):   # secondary scatter
        a = R.uniform(0, 2 * math.pi); r = R.uniform(5, 10)
        fern_spots.append((math.cos(a) * r, math.sin(a) * r + 2, R.uniform(0.8, 1.5)))
    for i, (x, y, s) in enumerate(fern_spots):
        src = A["FERN_%s" % "ABC"[i % 3]]
        inst(src, coll, (x, y, gz(x, y) - 0.02), rot_z=R.uniform(0, 360), scale=s, name="ENV_fern_%d" % i)

    # ---------------- leaf litter (HERO dense near path/roots) ----------------
    for i in range(1100):
        if i < 260:
            x, y = R.uniform(-3.4, 1.8), R.uniform(-10.5, -0.3)
        elif i < 420:
            x, y = R.uniform(-3.4, 3.4), R.uniform(1.0, 6.5)
        else:
            a = R.uniform(0, 2 * math.pi); r = R.uniform(4, 11)
            x, y = math.cos(a) * r, math.sin(a) * r + 2
        src = A["GROUND_LEAF_%s" % "ABC"[i % 3]]
        inst(src, coll, (x, y, gz(x, y) + 0.004), rot_z=R.uniform(0, 360), rot_x=R.uniform(-8, 8), scale=R.uniform(0.7, 1.5), name="ENV_leaf_%d" % i)

    # ---------------- twigs & rocks ----------------
    for i in range(26):
        x, y = R.uniform(-4, 3), R.uniform(-7, 5)
        src = A["TWIG_%s" % "AB"[i % 2]]
        inst(src, coll, (x, y, gz(x, y) + 0.01), rot_z=R.uniform(0, 360), scale=R.uniform(0.7, 1.3), name="ENV_twig_%d" % i)
    for i in range(16):
        x, y = R.uniform(-4, 4), R.uniform(-7, 6)
        inst(A["ROCK_SMALL"], coll, (x, y, gz(x, y) + 0.02), rot_z=R.uniform(0, 360), scale=R.uniform(0.5, 1.6), name="ENV_rock_%d" % i)
    for i in range(14):
        x, y = R.uniform(-3.5, 3.5), R.uniform(-6, 6)
        inst(A["MOSS_PATCH_%s" % "AB"[i % 2]], coll, (x, y, gz(x, y) + 0.01), rot_z=R.uniform(0, 360), scale=R.uniform(0.6, 1.4), name="ENV_gmoss_%d" % i)

    # ---------------- mist volume ----------------
    bm = bmesh.new(); G.bm_cube(bm, size=(44, 44, 7), loc=(0, 2, 3.2))
    mist = G.mesh_obj("ENV_mist", coll, bm)
    mm = bpy.data.materials.get("M_Mist")
    if not mm:
        mm = bpy.data.materials.new("M_Mist"); mm.use_nodes = True
        nt = mm.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        vs = nt.nodes.new("ShaderNodeVolumeScatter")
        vs.inputs["Anisotropy"].default_value = 0.35
        tex = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tex.outputs["Object"], sep.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -0.5
        mr.inputs["From Max"].default_value = 0.5
        mr.inputs["To Min"].default_value = 0.020
        mr.inputs["To Max"].default_value = 0.002
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], vs.inputs["Density"])
        nt.links.new(vs.outputs[0], out.inputs["Volume"])
    mist.data.materials.append(mm)
    mist.visible_shadow = False

    G.ensure_slots()
    G.save(MASTER)
    print("SCATTER_OBJECTS:", len(coll.objects))
    print("FOREST_SCATTER_DONE")

main()

import os as _os; _os._exit(0)

