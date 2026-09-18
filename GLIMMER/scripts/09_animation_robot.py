"""P11-P14 Robot performance blocking+polish across global timeline (mechanical motion language)."""
import bpy, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

MASTER = G.master_path()
S = G.SHOTS

def lf(shot, f):  # local frame (1-based) -> global
    return S[shot][0] + (f - 1)

def main():
    bpy.ops.wm.open_mainfile(filepath=MASTER)
    sc = bpy.context.scene
    arm = bpy.data.objects["CHAR_001_rig"]
    ctrl = bpy.data.objects["CHAR_001_ctrl"]
    pb = arm.pose.bones
    for b in pb:
        b.rotation_mode = "XYZ"
    # clear previous PERFORMANCE anim but keep object-level placement from 08
    if arm.animation_data:
        for tr in list(arm.animation_data.nla_tracks):
            arm.animation_data.nla_tracks.remove(tr)
        act = arm.animation_data.action
        if act:
            for fc in list(act.fcurves):
                if fc.data_path.startswith("pose.bones"):
                    act.fcurves.remove(fc)
    ctrl.animation_data_clear()

    A = {}  # collect keyframes: (data_path_holder, channel) -> list
    def key_bone(bone, frame, rx=None, ry=None, rz=None, loc=None):
        b = pb[bone]
        if rx is not None: b.rotation_euler[0] = math.radians(rx)
        if ry is not None: b.rotation_euler[1] = math.radians(ry)
        if rz is not None: b.rotation_euler[2] = math.radians(rz)
        if loc is not None: b.location = loc
        b.keyframe_insert("rotation_euler", frame=frame)
        if loc is not None:
            b.keyframe_insert("location", frame=frame)

    def key_ctrl(frame, **props):
        for k, v in props.items():
            ctrl[k] = v
        ctrl.keyframe_insert('["%s"]' % list(props)[0] if len(props) == 1 else '["EYE_BRIGHTNESS"]', frame=frame) if False else None
        for k in props:
            ctrl.keyframe_insert('["%s"]' % k, frame=frame)

    # ================= SHOT_001 walk (lonely, tired) =================
    s = "SHOT_001"
    ctrl["TRACK_PHASE"] = 0.0; ctrl.keyframe_insert('["TRACK_PHASE"]', frame=lf(s, 1))
    ctrl["TRACK_PHASE"] = 1.65; ctrl.keyframe_insert('["TRACK_PHASE"]', frame=lf(s, 72))
    # body bob + slight pitch (mechanical per-step)
    for f in range(1, 73, 6):
        ph = (f % 12) / 12.0
        key_bone("BODY_MAIN", lf(s, f), rx=1.2 * math.sin(ph * 2 * math.pi), loc=(0, 0.004 * math.sin(ph * 4 * math.pi), 0))
    key_bone("HEAD_YAW", lf(s, 1), rz=0); key_bone("HEAD_YAW", lf(s, 30), rz=4); key_bone("HEAD_YAW", lf(s, 60), rz=-3); key_bone("HEAD_YAW", lf(s, 72), rz=0)
    key_bone("HEAD_PITCH", lf(s, 1), rx=3)   # tired droop
    key_bone("ANTENNA_BASE", lf(s, 1), rx=-4); key_bone("ANTENNA_BASE", lf(s, 36), rx=-7); key_bone("ANTENNA_BASE", lf(s, 72), rx=-5)
    key_bone("ARM_L_SHOULDER", lf(s, 1), rx=4); key_bone("ARM_L_SHOULDER", lf(s, 36), rx=-3); key_bone("ARM_L_SHOULDER", lf(s, 72), rx=4)
    key_bone("ARM_R_SHOULDER", lf(s, 1), rx=-3); key_bone("ARM_R_SHOULDER", lf(s, 36), rx=4); key_bone("ARM_R_SHOULDER", lf(s, 72), rx=-3)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.85)

    # ================= SHOT_002 stop at log =================
    s = "SHOT_002"
    ctrl["TRACK_PHASE"] = 1.65; ctrl.keyframe_insert('["TRACK_PHASE"]', frame=lf(s, 1))
    ctrl["TRACK_PHASE"] = 1.95; ctrl.keyframe_insert('["TRACK_PHASE"]', frame=lf(s, 30))
    for f in range(1, 31, 6):
        ph = (f % 12) / 12.0
        key_bone("BODY_MAIN", lf(s, f), rx=1.0 * math.sin(ph * 2 * math.pi), loc=(0, 0.003 * math.sin(ph * 4 * math.pi), 0))
    key_bone("BODY_MAIN", lf(s, 38), rx=1.5, loc=(0, -0.004, 0))   # settle
    key_bone("BODY_MAIN", lf(s, 46), rx=0.0, loc=(0, 0.0, 0))
    key_bone("HEAD_YAW", lf(s, 47), rz=0); key_bone("HEAD_YAW", lf(s, 53), rz=10); key_bone("HEAD_YAW", lf(s, 57), rz=10)
    key_bone("HEAD_YAW", lf(s, 63), rz=-9); key_bone("HEAD_YAW", lf(s, 66), rz=-9); key_bone("HEAD_YAW", lf(s, 72), rz=0)
    key_bone("HEAD_PITCH", lf(s, 61), rx=3); key_bone("HEAD_PITCH", lf(s, 72), rx=6)
    key_bone("ANTENNA_BASE", lf(s, 46), rx=-5); key_bone("ANTENNA_BASE", lf(s, 52), rx=-9); key_bone("ANTENNA_BASE", lf(s, 64), rx=-6)
    key_ctrl(lf(s, 72), EYE_BRIGHTNESS=0.8)

    # ================= SHOT_003 tracks CU =================
    s = "SHOT_003"
    ctrl["TRACK_PHASE"] = 1.95; ctrl.keyframe_insert('["TRACK_PHASE"]', frame=lf(s, 1))
    ctrl["TRACK_PHASE"] = 2.40; ctrl.keyframe_insert('["TRACK_PHASE"]', frame=lf(s, 48))
    for f in range(1, 49, 6):
        ph = (f % 12) / 12.0
        key_bone("BODY_MAIN", lf(s, f), rx=0.8 * math.sin(ph * 2 * math.pi), loc=(0, 0.003 * math.sin(ph * 4 * math.pi), 0))
    # twig break prop anim
    twig = bpy.data.objects.get("PROP_twig_hero")
    if twig:
        twig.animation_data_clear()
        twig.rotation_mode = "XYZ"
        base_r = twig.rotation_euler[2]
        for f, bend in ((1, 0), (20, 0), (26, -14), (30, -22), (31, -8), (48, -10)):
            twig.rotation_euler = (math.radians(bend), 0, base_r)
            twig.keyframe_insert("rotation_euler", frame=lf(s, f))
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.8)

    # ================= SHOT_004 sit + eyes dim =================
    s = "SHOT_004"
    key_bone("BODY_MAIN", lf(s, 1), rx=0, loc=(0, 0, 0))
    key_bone("BODY_MAIN", lf(s, 12), rx=-6, loc=(0, -0.05, 0))
    key_bone("BODY_MAIN", lf(s, 24), rx=-11, loc=(0, -0.095, 0))   # seated lean
    key_bone("HEAD_PITCH", lf(s, 24), rx=4)
    key_bone("HEAD_PITCH", lf(s, 40), rx=9)
    key_bone("HEAD_PITCH", lf(s, 48), rx=11)
    key_bone("ARM_L_SHOULDER", lf(s, 1), rx=0); key_bone("ARM_L_SHOULDER", lf(s, 24), rx=14)
    key_bone("ARM_R_SHOULDER", lf(s, 1), rx=0); key_bone("ARM_R_SHOULDER", lf(s, 24), rx=12)
    key_bone("ARM_L_ELBOW", lf(s, 24), rx=18); key_bone("ARM_R_ELBOW", lf(s, 24), rx=16)
    key_bone("ANTENNA_BASE", lf(s, 24), rx=-6); key_bone("ANTENNA_BASE", lf(s, 40), rx=-3)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.8)
    key_ctrl(lf(s, 48), EYE_BRIGHTNESS=0.55)
    key_ctrl(lf(s, 72), EYE_BRIGHTNESS=0.25)

    # ================= SHOT_005 first firefly: micro-notice =================
    s = "SHOT_005"
    key_bone("BODY_MAIN", lf(s, 1), rx=-11, loc=(0, -0.095, 0))
    key_bone("HEAD_PITCH", lf(s, 1), rx=11)
    key_bone("HEAD_YAW", lf(s, 1), rz=0)
    key_bone("HEAD_YAW", lf(s, 40), rz=0)
    key_bone("HEAD_YAW", lf(s, 58), rz=5)
    key_bone("HEAD_YAW", lf(s, 72), rz=6)
    key_bone("HEAD_PITCH", lf(s, 58), rx=9)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.25)
    key_ctrl(lf(s, 45), EYE_BRIGHTNESS=0.30)
    key_ctrl(lf(s, 72), EYE_BRIGHTNESS=0.38)
    ctrl["GAZE_X"] = 0.0; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 1))
    ctrl["GAZE_X"] = 0.10; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 60))
    ctrl["GAZE_X"] = 0.12; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 72))

    # ================= SHOT_006 eyes awaken =================
    s = "SHOT_006"
    key_bone("BODY_MAIN", lf(s, 1), rx=-11, loc=(0, -0.095, 0))
    key_bone("HEAD_PITCH", lf(s, 1), rx=9)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.22)
    key_ctrl(lf(s, 16), EYE_BRIGHTNESS=0.15)
    key_ctrl(lf(s, 18), EYE_BRIGHTNESS=0.55)   # flicker
    key_ctrl(lf(s, 21), EYE_BRIGHTNESS=0.18)
    key_ctrl(lf(s, 24), EYE_BRIGHTNESS=0.60)
    key_ctrl(lf(s, 27), EYE_BRIGHTNESS=0.45)
    key_ctrl(lf(s, 40), EYE_BRIGHTNESS=0.90)
    key_bone("HEAD_PITCH", lf(s, 41), rx=6)
    key_bone("HEAD_PITCH", lf(s, 60), rx=-4)
    key_bone("HEAD_PITCH", lf(s, 72), rx=-6)
    ctrl["GAZE_X"] = 0.12; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 1))
    ctrl["GAZE_X"] = 0.05; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 50))
    ctrl["GAZE_X"] = 0.0; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 72))
    ctrl["GAZE_Y"] = 0.0; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 1))
    ctrl["GAZE_Y"] = -0.10; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 72))

    # ================= SHOT_007 head follows orbit (overshoot beat) ======
    s = "SHOT_007"
    key_bone("BODY_MAIN", lf(s, 1), rx=-11, loc=(0, -0.095, 0))
    key_bone("HEAD_PITCH", lf(s, 1), rx=-6)
    key_bone("HEAD_YAW", lf(s, 1), rz=6)
    key_bone("HEAD_YAW", lf(s, 20), rz=18)
    key_bone("HEAD_YAW", lf(s, 40), rz=30)
    key_bone("HEAD_YAW", lf(s, 46), rz=34)   # overshoot
    key_bone("HEAD_YAW", lf(s, 58), rz=26)   # slow correct
    key_bone("HEAD_YAW", lf(s, 72), rz=22)
    key_bone("HEAD_PITCH", lf(s, 30), rx=-9)
    key_bone("HEAD_PITCH", lf(s, 60), rx=-7)
    key_bone("ANTENNA_BASE", lf(s, 20), rx=-4); key_bone("ANTENNA_BASE", lf(s, 46), rx=-8); key_bone("ANTENNA_BASE", lf(s, 72), rx=-5)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.9)
    ctrl["GAZE_X"] = 0.0; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 1))
    ctrl["GAZE_X"] = 0.25; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 40))
    ctrl["GAZE_X"] = 0.18; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 72))

    # ================= SHOT_008 the reach =================
    s = "SHOT_008"
    key_bone("BODY_MAIN", lf(s, 1), rx=-11, loc=(0, -0.095, 0))
    key_bone("HEAD_YAW", lf(s, 1), rz=22)
    key_bone("HEAD_YAW", lf(s, 18), rz=16)
    key_bone("HEAD_PITCH", lf(s, 1), rx=-7)
    # right arm: from rest to extended, extremely slow
    key_bone("ARM_R_SHOULDER", lf(s, 1), rx=12)
    key_bone("ARM_R_ELBOW", lf(s, 1), rx=16)
    key_bone("ARM_R_WRIST", lf(s, 1), rx=10)
    key_bone("ARM_R_SHOULDER", lf(s, 19), rx=10)
    key_bone("ARM_R_SHOULDER", lf(s, 45), rx=-58)
    key_bone("ARM_R_ELBOW", lf(s, 45), rx=-18)
    key_bone("ARM_R_WRIST", lf(s, 46), rx=6)
    key_bone("ARM_R_WRIST", lf(s, 60), rx=-14)
    key_bone("ARM_R_SHOULDER", lf(s, 60), rx=-62)
    key_bone("ARM_R_SHOULDER", lf(s, 72), rx=-62)
    key_bone("ARM_R_ELBOW", lf(s, 72), rx=-14)
    key_bone("ARM_R_WRIST", lf(s, 72), rx=-14)
    # index finger: curled -> extended stable
    key_bone("FINGER_R_INDEX", lf(s, 45), rx=35)
    key_bone("FINGER_R_INDEX", lf(s, 61), rx=2)
    key_bone("FINGER_R_INDEX", lf(s, 72), rx=0)
    # left arm stays still
    key_bone("ARM_L_SHOULDER", lf(s, 1), rx=14); key_bone("ARM_L_SHOULDER", lf(s, 72), rx=14)
    key_bone("ANTENNA_BASE", lf(s, 1), rx=-5); key_bone("ANTENNA_BASE", lf(s, 72), rx=-5)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.9)
    ctrl["GAZE_X"] = 0.18; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 1))
    ctrl["GAZE_X"] = 0.10; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 72))
    ctrl["GAZE_Y"] = -0.10; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 1))
    ctrl["GAZE_Y"] = -0.06; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 72))

    # ================= SHOT_009 hold (no drift) =================
    s = "SHOT_009"
    key_bone("BODY_MAIN", lf(s, 1), rx=-11, loc=(0, -0.095, 0))
    key_bone("ARM_R_SHOULDER", lf(s, 1), rx=-62); key_bone("ARM_R_SHOULDER", lf(s, 60), rx=-62)
    key_bone("ARM_R_ELBOW", lf(s, 1), rx=-14); key_bone("ARM_R_ELBOW", lf(s, 60), rx=-14)
    key_bone("ARM_R_WRIST", lf(s, 1), rx=-14); key_bone("ARM_R_WRIST", lf(s, 60), rx=-14)
    key_bone("FINGER_R_INDEX", lf(s, 1), rx=0); key_bone("FINGER_R_INDEX", lf(s, 60), rx=0)
    key_bone("ARM_L_SHOULDER", lf(s, 1), rx=14); key_bone("ARM_L_SHOULDER", lf(s, 60), rx=14)
    key_bone("HEAD_YAW", lf(s, 1), rz=16); key_bone("HEAD_YAW", lf(s, 60), rz=14)
    key_bone("HEAD_PITCH", lf(s, 1), rx=-2); key_bone("HEAD_PITCH", lf(s, 60), rx=1)
    key_bone("ANTENNA_BASE", lf(s, 1), rx=-5); key_bone("ANTENNA_BASE", lf(s, 60), rx=-5)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.95)
    ctrl["GAZE_X"] = 0.10; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 1))
    ctrl["GAZE_Y"] = -0.06; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 1))
    ctrl["GAZE_Y"] = -0.14; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 60))

    # ================= SHOT_010 quiet uplift =================
    s = "SHOT_010"
    key_bone("BODY_MAIN", lf(s, 1), rx=-11, loc=(0, -0.095, 0))
    key_bone("BODY_MAIN", lf(s, 40), rx=-7, loc=(0, -0.085, 0))
    key_bone("BODY_MAIN", lf(s, 108), rx=-7, loc=(0, -0.085, 0))
    key_bone("HEAD_PITCH", lf(s, 1), rx=1)
    key_bone("HEAD_PITCH", lf(s, 36), rx=-8)
    key_bone("HEAD_PITCH", lf(s, 108), rx=-8)
    key_bone("HEAD_YAW", lf(s, 1), rz=14); key_bone("HEAD_YAW", lf(s, 108), rz=0)
    key_bone("ARM_R_SHOULDER", lf(s, 1), rx=-62)
    key_bone("ARM_R_SHOULDER", lf(s, 50), rx=6)
    key_bone("ARM_R_ELBOW", lf(s, 50), rx=10)
    key_bone("ARM_R_WRIST", lf(s, 50), rx=8)
    key_bone("FINGER_R_INDEX", lf(s, 50), rx=20)
    key_bone("ARM_L_SHOULDER", lf(s, 1), rx=14); key_bone("ARM_L_SHOULDER", lf(s, 108), rx=10)
    key_ctrl(lf(s, 1), EYE_BRIGHTNESS=0.95)
    key_ctrl(lf(s, 50), EYE_BRIGHTNESS=1.0)
    ctrl["GAZE_Y"] = -0.14; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 1))
    ctrl["GAZE_Y"] = -0.20; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 60))
    ctrl["GAZE_Y"] = -0.16; ctrl.keyframe_insert('["GAZE_Y"]', frame=lf(s, 108))
    ctrl["GAZE_X"] = 0.10; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 1))
    ctrl["GAZE_X"] = 0.0; ctrl.keyframe_insert('["GAZE_X"]', frame=lf(s, 108))

    # ---- spline cleanup: bezier auto-clamped on all bone/ctrl fcurves, ease holds
    if arm.animation_data and arm.animation_data.action:
        for fc in arm.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_IN_OUT"
    if ctrl.animation_data and ctrl.animation_data.action:
        for fc in ctrl.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "EASE_IN_OUT"
    G.save(MASTER)
    print("ROBOT_ANIM_DONE")

main()

import os as _os; _os._exit(0)

