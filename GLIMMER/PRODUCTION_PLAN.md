# PRODUCTION PLAN — GLIMMER

State machine P0→P22 as locked in the production prompt. Execution record:

- P0 discovery: bpy 4.5.6 headless validated; X/GL stub libs built; Cycles CPU benchmark 2 s/frame (simple) / 6 s/frame (forest+volume). EEVEE unavailable headless → Cycles chosen by benchmark, not preference.
- P1 ingest: storyboard contact sheet (re)generated as single visual baseline → reference/.
- P2 plan: this document + SHOT_MANIFEST.json (exact 10-shot timing, 720 frames).
- P3/P5 robot blockout+final: 02_robot_model.py — 42 rigid parts, real mechanical structure (tread plates via array+closed-curve deform, 5 wheels/side with rolling drivers, panel/rivet/vent detail, emissive eye stack).
- P6 rig: 03_robot_rig.py — 17-bone rigid armature + drivers (§25/§26/§27/§28).
- P4/P7 forest: 04_forest_assets.py (19-asset families, displaced bark, structured ferns) + 05_forest_scatter.py (canonical ENV_001, layered HERO/PRIMARY/SECONDARY/BACKGROUND scatter, 26-tree background ring, mist volume).
- P8 fireflies: 06_firefly.py — structured hero insect (abdomen/thorax/head/wings, flap driver) + GN swarm 900 pts, per-point phase attribute, frame-driven reveal + sine drift.
- P9 layout: 08_layout_all_shots.py — 10 cams (lens/DOF/moves per manifest), robot per-shot placement, camera clearance pass, hero twig prop.
- P10 animatic gate: layout preview movie (cycle renders) — story readable without dialogue.
- P11–P14 animation: 09_animation_robot.py — passes A–G in one blocking+polish pass per shot (story poses → timing → mechanical body → track contact → head/eyes → arms/finger → antenna), bezier ease, holds preserved.
- P15 firefly anim: 10_animation_firefly.py — bezier-eased arc path w/ hover, slowdown before landing, glow ramp; swarm reveal 613–708.
- P16 lighting: 11_lighting.py — states A/B/C keyframed on one global timeline (continuity guaranteed), god-ray spots, moon/rim/fill, mist density keys.
- P17 review loop: representative stills → 720-frame preview → 30 s assembly → critique → fixes (see ISSUE_LOG).
- P18 optimization: linked duplicates, GN instancing, low spp + OIDN, volume step rate.
- P19 final: representative 1080p frames (script 13) — full 720-frame 1080p not rendered per user directive (package = locked parameters + validation renders).
- P20 editorial: 14_editorial.py — per-shot mp4 + concat = exactly 30.0 s.
- P21 cold-start: clean bpy process re-opens master, re-renders representative frames (documented in FINAL REPORT).
- P22 package: 15_package.py → FINAL_DELIVERY + zip.
