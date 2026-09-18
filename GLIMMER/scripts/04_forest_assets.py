"""P4/P7 ENV_001 asset families — structural, displaced, non-lowpoly."""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, noise
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G, matlib as M

MASTER = G.master_path()
R = random.Random(7)

def open_master():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    return bpy.context.scene

def clean(coll_name):
    old = bpy.data.collections.get(coll_name)
    if old:
        for ob in list(old.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(old)
    return G.get_coll(coll_name)

# ------------------------------------------------------------------ trees
def make_trunk(name, coll, height=9.0, r_base=0.9, r_top=0.35, mats=(), seed=1, root_flare=True):
    """Tapered trunk with bark displacement + root flare lobes."""
    bm = bmesh.new()
    segs, rings = 24, 40
    verts_rows = []
    for i in range(rings + 1):
        t = i / rings
        z = t * height
        r = r_base * (1 - t) ** 0.9 * 0.75 + r_top * t + 0.02
        if root_flare:
            r += r_base * 0.55 * max(0.0, 1 - z / (r_base * 2.2)) ** 2
        row = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            # lobed flare: 5 root buttresses
            lobe = 1.0
            if root_flare and z < r_base * 2.0:
                lobe += 0.22 * max(0, math.cos(a * 5 + seed)) ** 2 * max(0.0, 1 - z / (r_base * 2.0))
            row.append(bm.verts.new((math.cos(a) * r * lobe, math.sin(a) * r * lobe, z)))
        verts_rows.append(row)
    for i in range(rings):
        for j in range(segs):
            v1 = verts_rows[i][j]; v2 = verts_rows[i][(j + 1) % segs]
            v3 = verts_rows[i + 1][(j + 1) % segs]; v4 = verts_rows[i + 1][j]
            bm.faces.new((v1, v2, v3, v4))
    ob = G.mesh_obj(name, coll, bm)
    tex = G.new_tex(name + "_bark", "CLOUDS", noise_scale=0.35, noise_depth=4)
    G.add_displace(ob, tex, strength=0.09, mid=0.5)
    tex2 = G.new_tex(name + "_bark2", "STUCCI", noise_scale=0.9)
    G.add_displace(ob, tex2, strength=0.02, mid=0.5)
    G.add_subsurf(ob, 1, 1)
    G.shade_smooth(ob, 50)
    for m in mats: ob.data.materials.append(m)
    return ob

def make_root(name, coll, length=2.2, r0=0.28, mats=(), seed=0, curve_up=0.35):
    """Tapered root snaking along ground."""
    bm = bmesh.new()
    segs, rings = 10, 16
    rows = []
    for i in range(rings + 1):
        t = i / rings
        x = t * length
        r = r0 * (1 - t) ** 1.2 + 0.02
        z = math.sin(t * 3.1 + seed) * curve_up * t * 0.4 + r * 0.55 * (1 - t * 0.6)
        y = math.sin(t * 2.0 + seed * 2) * 0.25 * t
        row = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            rr = r * (1 + 0.25 * max(0, math.cos(a * 3 + seed)) ** 2)
            row.append(bm.verts.new((x, y + math.cos(a) * rr, z + math.sin(a) * rr * 0.8)))
        rows.append(row)
    for i in range(rings):
        for j in range(segs):
            bm.faces.new((rows[i][j], rows[i][(j + 1) % segs], rows[i + 1][(j + 1) % segs], rows[i + 1][j]))
    ob = G.mesh_obj(name, coll, bm)
    tex = G.new_tex(name + "_b", "CLOUDS", noise_scale=0.25, noise_depth=3)
    G.add_displace(ob, tex, strength=0.05)
    G.shade_smooth(ob, 50)
    for m in mats: ob.data.materials.append(m)
    return ob

def make_fallen_log(name, coll, length=7.0, r=0.55, mats=()):
    bm = bmesh.new()
    segs, rings = 20, 46
    rows = []
    for i in range(rings + 1):
        t = i / rings
        x = (t - 0.5) * length
        rr = r * (1 - 0.25 * t) * (1 + 0.06 * math.sin(t * 20))
        z = r * 0.9 + math.sin(t * 2.4) * 0.08
        y = math.sin(t * 1.7) * 0.25
        row = []
        for j in range(segs):
            a = 2 * math.pi * j / segs
            row.append(bm.verts.new((x, y + math.cos(a) * rr, z + math.sin(a) * rr)))
        rows.append(row)
    for i in range(rings):
        for j in range(segs):
            bm.faces.new((rows[i][j], rows[i][(j + 1) % segs], rows[i + 1][(j + 1) % segs], rows[i + 1][j]))
    # end caps
    for row, flip in ((rows[0], True), (rows[-1], False)):
        f = bm.faces.new(row if flip else list(reversed(row)))
    ob = G.mesh_obj(name, coll, bm)
    tex = G.new_tex(name + "_b", "CLOUDS", noise_scale=0.4, noise_depth=4)
    G.add_displace(ob, tex, strength=0.08)
    G.shade_smooth(ob, 50)
    for m in mats: ob.data.materials.append(m)
    return ob

# ------------------------------------------------------------------ ferns
def make_fern(name, coll, fronds=7, scale=1.0, mats=(), seed=0):
    """Fern crown: arched rachis with paired pinnae leaflets (real structure)."""
    bm = bmesh.new()
    rnd = random.Random(seed)
    for f in range(fronds):
        ang = 2 * math.pi * f / fronds + rnd.uniform(-0.2, 0.2)
        tilt = rnd.uniform(0.55, 0.95)
        L = scale * rnd.uniform(0.55, 0.85)
        n_seg = 13
        rot = Matrix.Rotation(ang, 3, "Z")
        prev = None
        for i in range(n_seg + 1):
            t = i / n_seg
            # arch: rises then droops
            x = math.sin(t * 1.9) * L * 0.75
            z = math.sin(t * 2.6) * L * 0.42 * (1 - 0.35 * t)
            c = rot @ Vector((x, 0, z + 0.02))
            w = 0.10 * scale * math.sin(min(1.0, t * 1.15) * math.pi) ** 0.7 + 0.004
            # pinnae pair as flat quads angled down-out
            if i > 0:
                side = rot @ Vector((0, 1, 0))
                up = rot @ Vector((math.cos(t * 2.6) * 0.4, 0, math.cos(t * 1.9)))
                for s in (-1, 1):
                    p0 = c - side * 0.004 * s
                    p1 = c + side * (w * s)
                    p2 = p1 + (rot @ Vector((math.sin(t * 1.9 + 0.3), 0, -0.95))) * 0.05
                    p3 = p0 + (rot @ Vector((math.sin(t * 1.9 + 0.3), 0, -0.95))) * 0.05
                    vs = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
                    bm.faces.new(vs)
            # rachis segment
            if prev is not None:
                d = (c - prev).normalized()
                side = rot @ Vector((0, 1, 0))
                w0 = 0.006 * scale * (1 - t) + 0.0015
                vs = [bm.verts.new(prev - side * w0), bm.verts.new(prev + side * w0),
                      bm.verts.new(c + side * w0), bm.verts.new(c - side * w0)]
                bm.faces.new(vs)
            prev = c
    ob = G.mesh_obj(name, coll, bm)
    sol = ob.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.0015
    for m in mats: ob.data.materials.append(m)
    return ob

# ------------------------------------------------------------------ ground leaf / twig / moss / rock
def make_leaf(name, coll, mats=(), seed=0, size=0.09):
    rnd = random.Random(seed)
    bm = bmesh.new()
    n = 6
    pts = []
    for i in range(n + 1):
        t = i / n
        w = size * 0.35 * math.sin(t * math.pi) ** 0.7 + 0.002
        x = t * size
        z = math.sin(t * 2.2) * size * 0.18
        pts.append((x, w, z))
    rows = []
    for (x, w, z) in pts:
        rows.append([bm.verts.new((x, -w, z)), bm.verts.new((x, w, z))])
    for i in range(n):
        bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
    ob = G.mesh_obj(name, coll, bm)
    sol = ob.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.0008
    for m in mats: ob.data.materials.append(m)
    return ob

def make_twig(name, coll, mats=(), seed=0, length=0.35):
    rnd = random.Random(seed)
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(3)
    for i, bp in enumerate(sp.bezier_points):
        t = i / 3
        bp.co = (t * length, rnd.uniform(-0.03, 0.03) * t, 0.008 + rnd.uniform(-0.004, 0.004) * t + 0.004 * math.sin(t * 4))
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    cu.bevel_depth = 0.006
    cu.bevel_resolution = 2
    cu.use_fill_caps = True
    ob = bpy.data.objects.new(name, cu)
    coll.objects.link(ob)
    # side branchlets
    for m in mats: ob.data.materials.append(m)
    return ob

def make_moss_patch(name, coll, mats=(), seed=0, size=0.5):
    bm = bmesh.new()
    rnd = random.Random(seed)
    n = 10
    grid = {}
    for i in range(n + 1):
        for j in range(n + 1):
            x = (i / n - 0.5) * size
            y = (j / n - 0.5) * size
            d = math.sqrt(x * x + y * y) / (size * 0.5)
            h = max(0.0, 1 - d ** 2) * (0.02 + 0.02 * noise.noise(Vector((x * 8, y * 8, seed))))
            grid[(i, j)] = bm.verts.new((x, y, h))
    for i in range(n):
        for j in range(n):
            bm.faces.new((grid[(i, j)], grid[(i + 1, j)], grid[(i + 1, j + 1)], grid[(i, j + 1)]))
    ob = G.mesh_obj(name, coll, bm)
    G.shade_smooth(ob)
    for m in mats: ob.data.materials.append(m)
    return ob

def make_rock(name, coll, mats=(), seed=0, size=0.15):
    bm = bmesh.new()
    G.bm_sphere(bm, radius=size, segs=12, rings=8, scale=(1, 0.8, 0.6))
    for v in bm.verts:
        v.co += Vector((noise.noise(v.co * 6 + Vector((seed, 0, 0))) * 0.3 * size, ) * 3)
    ob = G.mesh_obj(name, coll, bm)
    G.shade_smooth(ob, 40)
    for m in mats: ob.data.materials.append(m)
    return ob

def make_bg_tree(name, coll, mats=(), seed=0, height=12.0, r=0.5):
    return make_trunk(name, coll, height=height, r_base=r, r_top=0.18, mats=mats, seed=seed, root_flare=False)

def main():
    sc = open_master()
    mats = {m.name: m for m in bpy.data.materials}
    need = ["M_Bark_Wet", "M_Bark_BG", "M_DarkWood", "M_Moss", "M_WetLeaves", "M_Mud", "M_Fern", "M_Stone"]
    if not all(k in mats for k in need):
        built = M.build_all()
        mats = {m.name: m for m in bpy.data.materials}
    coll = clean("ENV_001_assets")
    A = {}
    A["TREE_TRUNK_A"] = make_trunk("TREE_TRUNK_A", coll, 10.0, 1.1, 0.4, [mats["M_Bark_Wet"]], 1)
    A["TREE_TRUNK_B"] = make_trunk("TREE_TRUNK_B", coll, 8.0, 0.8, 0.3, [mats["M_Bark_Wet"]], 2)
    A["TREE_TRUNK_C"] = make_trunk("TREE_TRUNK_C", coll, 7.0, 0.55, 0.25, [mats["M_Bark_Wet"]], 3)
    for i in range(3):
        A["ROOT_%s" % "ABC"[i]] = make_root("ROOT_%s" % "ABC"[i], coll, 2.4 - i * 0.4, 0.3 - i * 0.06, [mats["M_Bark_Wet"]], i * 3)
    A["FALLEN_LOG_HERO"] = make_fallen_log("FALLEN_LOG_HERO", coll, 7.5, 0.6, [mats["M_DarkWood"]])
    for i in range(3):
        A["FERN_%s" % "ABC"[i]] = make_fern("FERN_%s" % "ABC"[i], coll, 10 + i * 3, 1.0 - i * 0.2, [mats["M_Fern"]], 10 + i)
    for i in range(2):
        A["MOSS_PATCH_%s" % "AB"[i]] = make_moss_patch("MOSS_PATCH_%s" % "AB"[i], coll, [mats["M_Moss"]], 20 + i, 0.6 + i * 0.4)
    for i in range(3):
        A["GROUND_LEAF_%s" % "ABC"[i]] = make_leaf("GROUND_LEAF_%s" % "ABC"[i], coll, [mats["M_WetLeaves"]], 30 + i, 0.08 + i * 0.03)
    for i in range(2):
        A["TWIG_%s" % "AB"[i]] = make_twig("TWIG_%s" % "AB"[i], coll, [mats["M_DarkWood"]], 40 + i, 0.3 + i * 0.15)
    A["ROCK_SMALL"] = make_rock("ROCK_SMALL", coll, [mats["M_Stone"]], 50, 0.14)
    A["BACKGROUND_TREE"] = make_bg_tree("BACKGROUND_TREE", coll, [mats["M_Bark_BG"]], 5, 14.0, 0.45)
    # park assets off to the side (layout script places instances)
    for i, (nm, ob) in enumerate(A.items()):
        ob.location = (30 + (i % 6) * 3, 30 + (i // 6) * 3, 0)
    G.ensure_slots()
    G.save(MASTER)
    print("ASSETS:", list(A.keys()))
    print("FOREST_ASSETS_DONE")

main()

import os as _os; _os._exit(0)

