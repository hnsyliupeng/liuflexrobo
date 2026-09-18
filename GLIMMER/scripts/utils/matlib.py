"""GLIMMER procedural material library (Blender 4.5). Photoreal-leaning, node-based."""
import bpy, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glib as G

# ---------------------------------------------------------------- ROBOT
def mat_robot_paint():
    """Aged teal paint: edge chips -> dark oxidized metal, rust streaks, dirt, moss traces."""
    m, nt, b, out = G.new_mat("M_Robot_Paint")
    n = nt.nodes
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1400, 0)
    # --- masks
    noise_w = n.new("ShaderNodeTexNoise"); noise_w.location = (-1200, 300)
    noise_w.inputs["Scale"].default_value = 9.0
    noise_w.inputs["Detail"].default_value = 8.0
    noise_w.inputs["Roughness"].default_value = 0.7
    nt.links.new(tex.outputs["Object"], noise_w.inputs["Vector"])
    geo = n.new("ShaderNodeNewGeometry"); geo.location = (-1400, -300)
    # edge wear mask = pointiness sharpened * wear noise
    ramp_e = n.new("ShaderNodeValToRGB"); ramp_e.location = (-1200, -200)
    ramp_e.color_ramp.elements[0].position = 0.52
    ramp_e.color_ramp.elements[1].position = 0.62
    nt.links.new(geo.outputs["Pointiness"], ramp_e.inputs["Fac"])
    wear_mul = n.new("ShaderNodeMath"); wear_mul.operation = "MULTIPLY"; wear_mul.location = (-950, 0)
    nt.links.new(ramp_e.outputs["Color"], wear_mul.inputs[0])
    nt.links.new(noise_w.outputs["Fac"], wear_mul.inputs[1])
    wear = n.new("ShaderNodeMath"); wear.operation = "GREATER_THAN"; wear.location = (-800, 0)
    wear.inputs[1].default_value = 0.28
    nt.links.new(wear_mul.outputs[0], wear.inputs[0])
    # rust mask: large blotches concentrated low (z gradient) + cavities
    noise_r = n.new("ShaderNodeTexNoise"); noise_r.location = (-1200, -500)
    noise_r.inputs["Scale"].default_value = 3.5
    noise_r.inputs["Detail"].default_value = 6.0
    nt.links.new(tex.outputs["Object"], noise_r.inputs["Vector"])
    sep = n.new("ShaderNodeSeparateXYZ"); sep.location = (-1200, -700)
    nt.links.new(tex.outputs["Object"], sep.inputs["Vector"])
    zmap = n.new("ShaderNodeMapRange"); zmap.location = (-1000, -700)
    zmap.inputs["From Min"].default_value = -0.05
    zmap.inputs["From Max"].default_value = 0.35
    zmap.inputs["To Min"].default_value = 1.0
    zmap.inputs["To Max"].default_value = 0.25
    nt.links.new(sep.outputs["Z"], zmap.inputs["Value"])
    rust_m = n.new("ShaderNodeMath"); rust_m.operation = "MULTIPLY"; rust_m.location = (-800, -500)
    nt.links.new(noise_r.outputs["Fac"], rust_m.inputs[0])
    nt.links.new(zmap.outputs["Result"], rust_m.inputs[1])
    rust = n.new("ShaderNodeValToRGB"); rust.location = (-650, -500)
    rust.color_ramp.elements[0].position = 0.50
    rust.color_ramp.elements[1].position = 0.72
    nt.links.new(rust_m.outputs[0], rust.inputs["Fac"])
    # grime/mud mask (lower body)
    mud = n.new("ShaderNodeValToRGB"); mud.location = (-650, -750)
    mud.color_ramp.elements[0].position = 0.55
    mud.color_ramp.elements[1].position = 0.85
    nt.links.new(zmap.outputs["Result"], mud.inputs["Fac"])
    # --- base color chain: teal paint -> chips(metal) -> rust -> mud
    paint_mix = n.new("ShaderNodeMixRGB"); paint_mix.location = (-400, 200)
    paint_mix.inputs["Color1"].default_value = (0.055, 0.20, 0.19, 1)   # aged teal
    paint_mix.inputs["Color2"].default_value = (0.030, 0.030, 0.032, 1) # oxidized metal
    nt.links.new(wear.outputs[0], paint_mix.inputs["Fac"])
    rust_mix = n.new("ShaderNodeMixRGB"); rust_mix.location = (-220, 100)
    rust_mix.inputs["Color2"].default_value = (0.16, 0.045, 0.018, 1)
    nt.links.new(paint_mix.outputs["Color"], rust_mix.inputs["Color1"])
    nt.links.new(rust.outputs["Color"], rust_mix.inputs["Fac"])
    mud_mix = n.new("ShaderNodeMixRGB"); mud_mix.location = (-40, 0)
    mud_mix.inputs["Color2"].default_value = (0.045, 0.030, 0.018, 1)
    nt.links.new(rust_mix.outputs["Color"], mud_mix.inputs["Color1"])
    mfac = n.new("ShaderNodeMath"); mfac.operation = "MULTIPLY"; mfac.location = (-220, -200)
    mfac.inputs[1].default_value = 0.55
    nt.links.new(mud.outputs["Color"], mfac.inputs[0])
    nt.links.new(mfac.outputs[0], mud_mix.inputs["Fac"])
    nt.links.new(mud_mix.outputs["Color"], b.inputs["Base Color"])
    # --- roughness: paint semi-gloss wet, rust/mud rough
    rgh = n.new("ShaderNodeMapRange"); rgh.location = (-40, -400)
    rgh.inputs["To Min"].default_value = 0.32   # damp paint
    rgh.inputs["To Max"].default_value = 0.85
    nt.links.new(rust.outputs["Color"], rgh.inputs["Value"])
    nt.links.new(rgh.outputs["Result"], b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = 0.15
    # --- bump: scratches + dents
    scr = n.new("ShaderNodeTexNoise"); scr.location = (-400, -650)
    scr.inputs["Scale"].default_value = 55.0
    scr.inputs["Detail"].default_value = 6.0
    nt.links.new(tex.outputs["Object"], scr.inputs["Vector"])
    bump = n.new("ShaderNodeBump"); bump.location = (-40, -650)
    bump.inputs["Strength"].default_value = 0.12
    nt.links.new(scr.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m

def mat_robot_metal():
    """Dark worn steel for joints / tracks / antenna."""
    m, nt, b, out = G.new_mat("M_Robot_Metal")
    n = nt.nodes
    b.inputs["Base Color"].default_value = (0.028, 0.026, 0.025, 1)
    b.inputs["Metallic"].default_value = 0.9
    tex = n.new("ShaderNodeTexCoord")
    noi = n.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 18.0
    noi.inputs["Detail"].default_value = 8.0
    nt.links.new(tex.outputs["Object"], noi.inputs["Vector"])
    r = n.new("ShaderNodeMapRange")
    r.inputs["To Min"].default_value = 0.35; r.inputs["To Max"].default_value = 0.75
    nt.links.new(noi.outputs["Fac"], r.inputs["Value"])
    nt.links.new(r.outputs["Result"], b.inputs["Roughness"])
    bmp = n.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.15
    nt.links.new(noi.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m

def mat_rubber_track():
    """Muddy rubber/metal track plates."""
    m, nt, b, out = G.new_mat("M_Track")
    n = nt.nodes
    b.inputs["Metallic"].default_value = 0.35
    tex = n.new("ShaderNodeTexCoord")
    noi = n.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 30.0
    noi.inputs["Detail"].default_value = 8.0
    nt.links.new(tex.outputs["Object"], noi.inputs["Vector"])
    mixc = n.new("ShaderNodeMixRGB")
    mixc.inputs["Color1"].default_value = (0.02, 0.019, 0.018, 1)
    mixc.inputs["Color2"].default_value = (0.06, 0.042, 0.026, 1)  # mud
    nt.links.new(noi.outputs["Fac"], mixc.inputs["Fac"])
    nt.links.new(mixc.outputs["Color"], b.inputs["Base Color"])
    r = n.new("ShaderNodeMapRange")
    r.inputs["To Min"].default_value = 0.4; r.inputs["To Max"].default_value = 0.9
    nt.links.new(noi.outputs["Fac"], r.inputs["Value"])
    nt.links.new(r.outputs["Result"], b.inputs["Roughness"])
    bmp = n.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.3
    nt.links.new(noi.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m

def _reuse(name):
    m = bpy.data.materials.get(name)
    return m if (m and m.users > 0) else None

def mat_eye():
    """Cyan-blue emissive eye with inner aperture core; strength driven by EYE_BRIGHTNESS prop on robot ctrl."""
    r = _reuse("M_Robot_Eye")
    if r: return r
    m, nt, b, out = G.new_mat("M_Robot_Eye")
    n = nt.nodes
    nt.nodes.remove(b)
    em = n.new("ShaderNodeEmission"); em.location = (250, 0)
    em.inputs["Color"].default_value = (0.10, 0.62, 0.95, 1)
    # radial gradient: bright core, dimmer rim
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-600, 0)
    grad = n.new("ShaderNodeTexGradient"); grad.gradient_type = "SPHERICAL"; grad.location = (-400, 0)
    nt.links.new(tex.outputs["Object"], grad.inputs["Vector"])
    core = n.new("ShaderNodeMapRange"); core.location = (-200, 100)
    core.inputs["From Min"].default_value = 0.15
    core.inputs["From Max"].default_value = 0.9
    core.inputs["To Min"].default_value = 0.35
    core.inputs["To Max"].default_value = 1.6
    nt.links.new(grad.outputs["Fac"], core.inputs["Value"])
    mul = n.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.location = (0, 0)
    nt.links.new(core.outputs["Result"], mul.inputs[0])
    drv = n.new("ShaderNodeValue"); drv.location = (-200, -200)
    drv.name = "EYE_BRIGHTNESS"; drv.label = "EYE_BRIGHTNESS"
    drv.outputs[0].default_value = 1.0
    # NOTE: driver binding to CHAR_001_ctrl["EYE_BRIGHTNESS"] is added by 03_robot_rig.py
    nt.links.new(drv.outputs[0], mul.inputs[1])
    nt.links.new(mul.outputs[0], em.inputs["Strength"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    # glass-like coat ring handled by separate rim mesh
    return m

def mat_eye_rim():
    m, nt, b, out = G.new_mat("M_Robot_EyeRim")
    b.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1)
    b.inputs["Metallic"].default_value = 0.8
    b.inputs["Roughness"].default_value = 0.35
    return m

# ---------------------------------------------------------------- FOREST
def _bark_base(name, col_dark, col_light, scale=8.0, bump=0.5, mossy=True):
    m, nt, b, out = G.new_mat(name)
    n = nt.nodes
    tex = n.new("ShaderNodeTexCoord"); tex.location = (-1200, 0)
    wav = n.new("ShaderNodeTexNoise"); wav.location = (-1000, 200)
    wav.inputs["Scale"].default_value = scale
    wav.inputs["Detail"].default_value = 10.0
    wav.inputs["Roughness"].default_value = 0.75
    nt.links.new(tex.outputs["Object"], wav.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB"); ramp.location = (-800, 200)
    ramp.color_ramp.elements[0].color = col_dark
    ramp.color_ramp.elements[1].color = col_light
    nt.links.new(wav.outputs["Fac"], ramp.inputs["Fac"])
    last = ramp.outputs["Color"]
    if mossy:
        # moss on up-facing + noise
        geo = n.new("ShaderNodeNewGeometry"); geo.location = (-1000, -200)
        sepn = n.new("ShaderNodeSeparateXYZ"); sepn.location = (-800, -200)
        nt.links.new(geo.outputs["Normal"], sepn.inputs["Vector"])
        up = n.new("ShaderNodeMapRange"); up.location = (-650, -200)
        up.inputs["From Min"].default_value = 0.2
        up.inputs["From Max"].default_value = 0.8
        nt.links.new(sepn.outputs["Z"], up.inputs["Value"])
        mn = n.new("ShaderNodeTexNoise"); mn.location = (-800, -450)
        mn.inputs["Scale"].default_value = 6.0
        mn.inputs["Detail"].default_value = 8.0
        nt.links.new(tex.outputs["Object"], mn.inputs["Vector"])
        mm = n.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.location = (-500, -300)
        nt.links.new(up.outputs["Result"], mm.inputs[0])
        nt.links.new(mn.outputs["Fac"], mm.inputs[1])
        mr = n.new("ShaderNodeValToRGB"); mr.location = (-350, -300)
        mr.color_ramp.elements[0].position = 0.18
        mr.color_ramp.elements[1].position = 0.4
        nt.links.new(mm.outputs[0], mr.inputs["Fac"])
        mixm = n.new("ShaderNodeMixRGB"); mixm.location = (-150, 0)
        mixm.inputs["Color2"].default_value = (0.035, 0.09, 0.02, 1)
        nt.links.new(last, mixm.inputs["Color1"])
        nt.links.new(mr.outputs["Color"], mixm.inputs["Fac"])
        last = mixm.outputs["Color"]
        nt.links.new(mr.outputs["Color"], b.inputs["Roughness"])  # moss rough
    nt.links.new(last, b.inputs["Base Color"])
    if not mossy:
        b.inputs["Roughness"].default_value = 0.55
    bmpn = n.new("ShaderNodeBump"); bmpn.location = (-150, -600)
    bmpn.inputs["Strength"].default_value = bump
    nt.links.new(wav.outputs["Fac"], bmpn.inputs["Height"])
    nt.links.new(bmpn.outputs["Normal"], b.inputs["Normal"])
    return m

def mat_bark_wet():  return _bark_base("M_Bark_Wet", (0.020, 0.014, 0.009, 1), (0.075, 0.055, 0.036, 1), 7.0, 0.6)
def mat_bark_bg():   return _bark_base("M_Bark_BG", (0.022, 0.016, 0.011, 1), (0.06, 0.045, 0.03, 1), 5.0, 0.3, mossy=False)
def mat_dark_wood(): return _bark_base("M_DarkWood", (0.030, 0.020, 0.012, 1), (0.085, 0.060, 0.038, 1), 12.0, 0.5, mossy=False)

def mat_moss():
    m, nt, b, out = G.new_mat("M_Moss")
    n = nt.nodes
    tex = n.new("ShaderNodeTexCoord")
    noi = n.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 40.0
    noi.inputs["Detail"].default_value = 10.0
    nt.links.new(tex.outputs["Object"], noi.inputs["Vector"])
    mixc = n.new("ShaderNodeMixRGB")
    mixc.inputs["Color1"].default_value = (0.030, 0.085, 0.018, 1)
    mixc.inputs["Color2"].default_value = (0.055, 0.13, 0.03, 1)
    nt.links.new(noi.outputs["Fac"], mixc.inputs["Fac"])
    nt.links.new(mixc.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    if "Sheen Weight" in b.inputs: b.inputs["Sheen Weight"].default_value = 0.3
    bmp = n.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.6
    nt.links.new(noi.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m

def mat_wet_leaves():
    m, nt, b, out = G.new_mat("M_WetLeaves")
    n = nt.nodes
    tex = n.new("ShaderNodeTexCoord")
    noi = n.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 3.0
    noi.inputs["Detail"].default_value = 4.0
    nt.links.new(tex.outputs["Object"], noi.inputs["Vector"])
    ramp = n.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].color = (0.06, 0.028, 0.010, 1)   # wet brown
    cr.elements[1].color = (0.085, 0.055, 0.018, 1)  # ochre
    e = cr.elements.new(0.55); e.color = (0.045, 0.05, 0.012, 1)  # olive
    nt.links.new(noi.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.28  # wet sheen
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.3
    return m

def mat_mud():
    m, nt, b, out = G.new_mat("M_Mud")
    n = nt.nodes
    tex = n.new("ShaderNodeTexCoord")
    noi = n.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 14.0
    noi.inputs["Detail"].default_value = 10.0
    nt.links.new(tex.outputs["Object"], noi.inputs["Vector"])
    mixc = n.new("ShaderNodeMixRGB")
    mixc.inputs["Color1"].default_value = (0.028, 0.019, 0.012, 1)
    mixc.inputs["Color2"].default_value = (0.05, 0.036, 0.022, 1)
    nt.links.new(noi.outputs["Fac"], mixc.inputs["Fac"])
    nt.links.new(mixc.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.18   # wet mud reflective
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.4
    bmp = n.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.35
    nt.links.new(noi.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m

def mat_fern():
    m, nt, b, out = G.new_mat("M_Fern")
    n = nt.nodes
    b.inputs["Base Color"].default_value = (0.028, 0.075, 0.016, 1)
    b.inputs["Roughness"].default_value = 0.35
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = 0.2
    # translucency for backlit fronds
    tr = n.new("ShaderNodeBsdfTranslucent"); tr.location = (250, -250)
    tr.inputs["Color"].default_value = (0.06, 0.16, 0.03, 1)
    add = n.new("ShaderNodeAddShader"); add.location = (450, -100)
    nt.links.new(b.outputs["BSDF"], add.inputs[0])
    nt.links.new(tr.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    return m

def mat_stone():
    m, nt, b, out = G.new_mat("M_Stone")
    n = nt.nodes
    tex = n.new("ShaderNodeTexCoord")
    noi = n.new("ShaderNodeTexNoise"); noi.inputs["Scale"].default_value = 10.0
    noi.inputs["Detail"].default_value = 8.0
    nt.links.new(tex.outputs["Object"], noi.inputs["Vector"])
    mixc = n.new("ShaderNodeMixRGB")
    mixc.inputs["Color1"].default_value = (0.03, 0.03, 0.032, 1)
    mixc.inputs["Color2"].default_value = (0.07, 0.07, 0.072, 1)
    nt.links.new(noi.outputs["Fac"], mixc.inputs["Fac"])
    nt.links.new(mixc.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.3
    bmp = n.new("ShaderNodeBump"); bmp.inputs["Strength"].default_value = 0.4
    nt.links.new(noi.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], b.inputs["Normal"])
    return m

# ---------------------------------------------------------------- FIREFLY
def mat_firefly_glow():
    r = _reuse("M_Firefly_Glow")
    if r: return r
    m, nt, b, out = G.new_mat("M_Firefly_Glow")
    n = nt.nodes
    nt.nodes.remove(b)
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.62, 0.85, 0.12, 1)  # warm yellow-green
    drv = n.new("ShaderNodeValue"); drv.label = "GLOW_GAIN"
    mul = n.new("ShaderNodeMath"); mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = 1.0
    nt.links.new(drv.outputs[0], mul.inputs[0])
    mul.inputs[1].default_value = 24.0
    nt.links.new(mul.outputs[0], em.inputs["Strength"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m

def mat_firefly_body():
    m, nt, b, out = G.new_mat("M_Firefly_Body")
    b.inputs["Base Color"].default_value = (0.015, 0.012, 0.008, 1)
    b.inputs["Roughness"].default_value = 0.5
    return m

def mat_firefly_wing():
    m, nt, b, out = G.new_mat("M_Firefly_Wing")
    n = nt.nodes
    b.inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1)
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Alpha"].default_value = 0.18
    if "Transmission Weight" in b.inputs: b.inputs["Transmission Weight"].default_value = 0.5
    m.blend_method = "BLEND"
    return m

def mat_swarm_dot():
    """Tiny emissive dot for swarm instances; reveal gated by attribute 'reveal' vs frame driver."""
    r = _reuse("M_Swarm_Dot")
    if r: return r
    m, nt, b, out = G.new_mat("M_Swarm_Dot")
    n = nt.nodes
    nt.nodes.remove(b)
    attr = n.new("ShaderNodeAttribute"); attr.attribute_name = "ff_phase"
    val = n.new("ShaderNodeValue"); val.label = "REVEAL"
    fc = nt.driver_add('nodes["%s"].outputs[0].default_value' % val.name)
    d = fc.driver; d.type = "SCRIPTED"; d.expression = "min(max((frame-613)/95.0,0),1)"
    sub = n.new("ShaderNodeMath"); sub.operation = "SUBTRACT"
    nt.links.new(val.outputs[0], sub.inputs[0])
    nt.links.new(attr.outputs["Fac"], sub.inputs[1])
    gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.0
    nt.links.new(sub.outputs[0], gt.inputs[0])
    # per-firefly flicker: slow sine per phase
    flick = n.new("ShaderNodeMath"); flick.operation = "MULTIPLY_ADD"
    nt.links.new(attr.outputs["Fac"], flick.inputs[0])
    flick.inputs[1].default_value = 40.0
    sine = n.new("ShaderNodeMath"); sine.operation = "SINE"
    fr = n.new("ShaderNodeValue"); fr.label = "FRAME"
    fcd = nt.driver_add('nodes["%s"].outputs[0].default_value' % fr.name)
    fcd.driver.type = "SCRIPTED"; fcd.driver.expression = "frame"
    nt.links.new(fr.outputs[0], sine.inputs[0])
    nt.links.new(sine.outputs[0], flick.inputs[2])
    fmap = n.new("ShaderNodeMapRange")
    fmap.inputs["From Min"].default_value = -1.0; fmap.inputs["From Max"].default_value = 1.0
    fmap.inputs["To Min"].default_value = 0.35; fmap.inputs["To Max"].default_value = 1.0
    nt.links.new(flick.outputs[0], fmap.inputs["Value"])
    gate = n.new("ShaderNodeMath"); gate.operation = "MULTIPLY"
    nt.links.new(gt.outputs[0], gate.inputs[0])
    nt.links.new(fmap.outputs["Result"], gate.inputs[1])
    strength = n.new("ShaderNodeMath"); strength.operation = "MULTIPLY"; strength.inputs[1].default_value = 30.0
    nt.links.new(gate.outputs[0], strength.inputs[0])
    em = n.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.60, 0.83, 0.10, 1)
    nt.links.new(strength.outputs[0], em.inputs["Strength"])
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m

ALL = [mat_robot_paint, mat_robot_metal, mat_rubber_track, mat_eye, mat_eye_rim,
       mat_bark_wet, mat_bark_bg, mat_dark_wood, mat_moss, mat_wet_leaves, mat_mud,
       mat_fern, mat_stone, mat_firefly_glow, mat_firefly_body, mat_firefly_wing, mat_swarm_dot]

def build_all():
    out = {}
    for f in ALL:
        m = f()
        m.use_fake_user = True
        out[f.__name__] = m
    return out
