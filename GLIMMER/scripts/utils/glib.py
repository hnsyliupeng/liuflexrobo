"""GLIMMER shared helpers (Blender 4.5 / bpy module)."""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FPS = 24

# ---------------- global timeline (contiguous shots) ----------------
SHOTS = {
    "SHOT_001": (1, 72,   3.0, "WS",  28),
    "SHOT_002": (73, 144, 3.0, "FS",  40),
    "SHOT_003": (145, 192, 2.0, "CU", 65),
    "SHOT_004": (193, 264, 3.0, "MS", 50),
    "SHOT_005": (265, 336, 3.0, "OTS", 55),
    "SHOT_006": (337, 408, 3.0, "CU", 75),
    "SHOT_007": (409, 480, 3.0, "MCU", 50),
    "SHOT_008": (481, 552, 3.0, "MS", 55),
    "SHOT_009": (553, 612, 2.5, "ECU", 90),
    "SHOT_010": (613, 720, 4.5, "WS", 32),
}
SHOT_ORDER = list(SHOTS.keys())

def shot_local_to_global(shot, lf):
    a, b = SHOTS[shot][0], SHOTS[shot][1]
    return a + (lf - 1)

# ---------------- scene / io ----------------
def new_master():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, 720
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    return sc

def get_coll(name, link=True):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        if link:
            bpy.context.scene.collection.children.link(c)
    return c

def link_to(obj, coll):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)

def save(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print("SAVED:", path)

# ---------------- render helpers ----------------
def setup_cycles(sc, res_x=480, res_y=270, samples=8, thr=0.1):
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = thr
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 2
    sc.cycles.volume_bounces = 0
    sc.cycles.volume_step_rate = float(os.environ.get("VOLSTEP", "2.0"))
    sc.cycles.volume_max_steps = 64
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    sc.render.threads_mode = "AUTO"

def render_still(sc, path, frame=None, res_x=480, res_y=270, samples=8):
    setup_cycles(sc, res_x, res_y, samples)
    if frame: sc.frame_set(frame)
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("STILL:", path)

# ---------------- geometry helpers ----------------
def mesh_obj(name, coll, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob

def add_subsurf(ob, levels=2, render=2):
    m = ob.modifiers.new("subsurf", "SUBSURF")
    m.levels, m.render_levels = levels, render
    return m

def add_bevel(ob, width=0.004, segments=2, angle=40):
    m = ob.modifiers.new("bevel", "BEVEL")
    m.width = width; m.segments = segments
    m.limit_method = "ANGLE"; m.angle_limit = math.radians(angle)
    return m

def add_displace(ob, tex, strength=0.05, scale=1.0, mid=0.5):
    m = ob.modifiers.new("displace", "DISPLACE")
    m.texture = tex; m.strength = strength; m.texture_coords = "LOCAL"
    m.mid_level = mid
    return m

def new_tex(name, ttype="CLOUDS", **kw):
    t = bpy.data.textures.get(name) or bpy.data.textures.new(name, ttype)
    for k, v in kw.items():
        setattr(t, k, v)
    return t

def shade_smooth(ob, angle=45):
    for p in ob.data.polygons: p.use_smooth = True
    if hasattr(ob.data, "use_auto_smooth"):
        ob.data.use_auto_smooth = True
        ob.data.auto_smooth_angle = math.radians(angle)
    else:
        m = ob.modifiers.new("smooth_by_angle", "SMOOTH_BY_ANGLE") if False else None
        try:
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
            ob.select_set(False)
        except Exception:
            pass

def bm_cube(bm, size=(1,1,1), loc=(0,0,0)):
    r = bmesh.ops.create_cube(bm, size=1.0)
    verts = r["verts"]
    mat = Matrix.Diagonal(Vector(size)).to_4x4()
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(loc)) @ mat, verts=verts)
    return verts

def bm_sphere(bm, radius=0.5, segs=24, rings=16, loc=(0,0,0), scale=(1,1,1)):
    r = bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    verts = r["verts"]
    mat = Matrix.Translation(Vector(loc)) @ Matrix.Diagonal(Vector(scale)).to_4x4()
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts

def bm_cyl(bm, radius=0.5, depth=1.0, segs=16, loc=(0,0,0), rot=None, scale=(1,1,1)):
    r = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs,
                              radius1=radius, radius2=radius, depth=depth)
    verts = r["verts"]
    mat = Matrix.Translation(Vector(loc))
    if rot: mat = mat @ rot.to_4x4()
    mat = mat @ Matrix.Diagonal(Vector(scale)).to_4x4()
    bmesh.ops.transform(bm, matrix=mat, verts=verts)
    return verts

def rot_x(a): return Matrix.Rotation(math.radians(a), 3, "X")
def rot_y(a): return Matrix.Rotation(math.radians(a), 3, "Y")
def rot_z(a): return Matrix.Rotation(math.radians(a), 3, "Z")

def driver(obj, path, expr, variables=(), index=-1):
    """variables: list of (name, target_obj, data_path, index)"""
    fc = obj.driver_add(path, index)
    d = fc.driver
    d.type = "SCRIPTED"
    for (nm, tobj, dpath, didx) in variables:
        v = d.variables.new(); v.name = nm; v.type = "SINGLE_PROP"
        t = v.targets[0]; t.id = tobj; t.data_path = dpath
        if didx >= 0: t.index = didx
    d.expression = expr
    return fc

# ---------------- material helpers ----------------
def new_mat(name):
    m = bpy.data.materials.get(name)
    if m: bpy.data.materials.remove(m)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); out.location = (600, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (250, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m, nt, bsdf, out

def set_in(node, names, val):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = val
            return True
    return False

def master_path():
    return os.environ.get("GLIMMER_MASTER", os.path.join(ROOT, "blend", "final", "GLIMMER_master.blend"))

# ---------------- self-healing material assignment ----------------
_MAT_RULES = [
    (("CHAR_001_head", "CHAR_001_torso", "CHAR_001_torso_panel", "CHAR_001_chassis",
      "CHAR_001_fender_L", "CHAR_001_fender_R"), "M_Robot_Paint"),
    (("CHAR_001_eye_rim_L", "CHAR_001_eye_rim_R"), "M_Robot_EyeRim"),
    (("CHAR_001_eye_L", "CHAR_001_eye_R", "CHAR_001_iris_L", "CHAR_001_iris_R"), "M_Robot_Eye"),
    (("CHAR_001_track_plates_L", "CHAR_001_track_plates_R"), "M_Track"),
    (("TREE_TRUNK_", "ROOT_", "ENV_hero_tree", "ENV_root", "ENV_midtree"), "M_Bark_Wet"),
    (("BACKGROUND_TREE", "ENV_bgtree"), "M_Bark_BG"),
    (("FALLEN_LOG", "ENV_fallen_log", "TWIG_", "ENV_twig", "PROP_twig"), "M_DarkWood"),
    (("FERN_", "ENV_fern"), "M_Fern"),
    (("MOSS_PATCH_", "ENV_rootmoss", "ENV_logmoss", "ENV_gmoss"), "M_Moss"),
    (("GROUND_LEAF_", "ENV_leaf"), "M_WetLeaves"),
    (("ROCK_SMALL", "ENV_rock"), "M_Stone"),
    (("ENV_mist",), "M_Mist"),
    (("ENV_ground",), "M_Mud"),
    (("FX_001_abdomen",), "M_Firefly_Glow"),
    (("FX_001_body",), "M_Firefly_Body"),
    (("FX_001_wing_",), "M_Firefly_Wing"),
    (("FX_010_dot_src",), "M_Swarm_Dot"),
]
_METAL_PREFIX = ("CHAR_001_hatch", "CHAR_001_head_hatch", "CHAR_001_head_seam", "CHAR_001_seam",
                 "CHAR_001_rivets", "CHAR_001_vents", "CHAR_001_neck", "CHAR_001_shoulder",
                 "CHAR_001_upperarm", "CHAR_001_forearm", "CHAR_001_hand", "CHAR_001_finger",
                 "CHAR_001_wheel", "CHAR_001_antenna")

def ensure_slots():
    """Repair None/missing material slots by name rules (idempotent)."""
    M = {m.name: m for m in bpy.data.materials}
    fixed = 0
    for ob in bpy.data.objects:
        if not ob.data or not hasattr(ob.data, "materials"):
            continue
        target = None
        for names, mat in _MAT_RULES:
            if ob.name.startswith(names) or ob.name in names:
                target = mat
                break
        if not target and ob.name.startswith(_METAL_PREFIX):
            target = "M_Robot_Metal"
        if not target or target not in M:
            continue
        mats = ob.data.materials
        if len(mats) == 0:
            mats.append(M[target]); fixed += 1
        elif mats[0] is None:
            mats[0] = M[target]; fixed += 1
    print("ENSURE_SLOTS fixed=%d" % fixed, flush=True)
    return fixed
