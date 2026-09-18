# ISSUE_LOG

ID | SHOT | FRAME_RANGE | SEVERITY | CATEGORY | VISIBLE_EVIDENCE | ROOT_CAUSE | CORRECTION | REGRESSION_RISK | STATUS
---|---|---|---|---|---|---|---|---|---
I-001 | ALL | 1-720 | CRITICAL | rig | robot parts scattered at ground level, invisible in shots | bone-parent bind used stale unevaluated parent matrix (matrix_parent_inverse wrong → 90° offset) | 07_look_fix.py recomputes matrix_parent_inverse from rest bone.matrix_local @ tail | low (rigid rebind) | FIXED
I-002 | 004-010 | 193-720 | CRITICAL | lighting | night shots near-black | moon/rim/fill/world strengths too low for AgX | 11 v2: moon 0.38, rim 140, fill 45, world night 0.34 | dusk unchanged | FIXED
I-003 | 006-009 | 337-612 | HIGH | lookdev | eye glow not readable | emission strength ~1 too dim under AgX | EYE_GAIN ×9 node in M_Robot_Eye | watch clipping in S9/S10 | FIXED
I-004 | 001 | 1-72 | HIGH | layout | fallen log blocked WS view, no forest depth read | log placed on shot-1 sight line | log moved to (-6.0, 0.2); S2/S3 cams+robot re-placed west | S2 framing re-checked cycle 1 | FIXED
I-005 | 001-003 | 1-192 | MEDIUM | assets | trunks read as smooth cones ("chess pieces") | taper exponent 1.35 too conical | 04 v2 taper 0.9*0.75, flare 0.55, lobes 0.22 | silhouette check cycle 1 | FIXED
I-006 | all | all | MEDIUM | assets | ferns read as flat star cards | pinnae too sparse/wide | 04 v2: 13 segments, narrower pinnae | — | FIXED
I-007 | 004,006 | 193-408 | MEDIUM | layout | ferns/leaves occluding close cameras | scatter unaware of cameras | 08 clearance pass removes scatter within 0.55 m of cam / 0.30 m of sight line | slight density loss near cams | FIXED
I-008 | all | all | HIGH | pipeline | materials lost (white clay) after matlib rebuild | new_mat deleted in-use materials | new_mat reuses material with users; 06_fix_materials re-assigned 756 slots | — | FIXED
I-009 | all | all | MEDIUM | pipeline | scripts hang at interpreter exit (bpy module atexit) | bpy wheel exit cleanup deadlock | os._exit(0) appended to every script | — | FIXED
I-010 | 003 | 166-176 | LOW | anim | twig break timing vs track contact | manual keys | re-timed with track phase 1.95→2.40 | — | OPEN(monitor)
I-011 | all | all | CRITICAL | lookdev | forest renders white-clay again in v3 | material slots None on asset meshes (cascade of datablock removals via matlib rebuild paths) | glib.ensure_slots() self-heal pass wired into 02/04/05/08 + repair run; matlib no-bsdf materials guarded by _reuse() | medium (watch future rebuilds) | FIXED
I-012 | 001 | 1-72 | HIGH | cinematography | robot too large in WS (story beat "robot very small" lost) | camera too close | v4: cam at y=-12.6/12.0, focus -7.6 | — | FIXED
I-013 | all | all | MEDIUM | scatter | leaves/moss floating at fern/log/trunk heights ("black fin" artifact) | gz() used scene ray_cast hitting vegetation | v4: gz() ray-casts ground object only | — | FIXED
I-014 | 006-009 | 337-612 | MEDIUM | lookdev | eyes clip to white balls (cyan hue lost) | EYE_GAIN 9 too hot | v4 gain 4.0 | — | FIXED
I-015 | 001-003 | 1-192 | MEDIUM | lighting | dusk reads flat/muddy, no god-ray pools | open canopy + weak shafts vs sun | v4: sun 3.5/3.0, shafts 13000/10500 | — | FIXED
I-016 | 001-003 | 1-192 | MEDIUM | lighting | robot reads as black silhouette in dusk shafts | god-ray pools miss robot path; no warm fill on character | cycle-2: re-aim shaft_0 to robot path + add 20 W warm char fill for S1-S3 | — | OPEN
I-017 | 004-010 | 193-720 | HIGH | lighting | night silhouettes unreadable (robot/body black) | moon/rim/fill still under AgX | cycle-2: moon 1.2/1.05, rim 420/360, fill 150/130, world 0.55/0.52 | — | FIXED(c2 render)
I-018 | 009 | 553-612 | CRITICAL | anim/layout | firefly landed 0.6 m away from actual fingertip (arm pose never reached assumed target) | hand-target constant guessed, not solved | 09b_arm_solve.py numeric 3-DoF solve → fingertip (0.077,3.937,0.361); firefly path + S9 cam/focus re-synced | S8/S10 arm keys re-timed | FIXED(c2 render)
I-019 | 009 | 583-612 | HIGH | lookdev | firefly emitter clipped to white ellipse; finger unlit | emitter strength high + practical light trapped inside body mesh | emission 24→6, practical point light offset (0,-0.02,0.02) driver g*4, firefly scale 0.45, abdomen yaw-turned to camera at landing | — | FIXED(c2 render)
I-020 | 010 | 613-720 | MEDIUM | lookdev | swarm reads slightly star-wall uniform | layered random ok but cluster bias weak | accepted for preview; improve via density ramp in future pass | — | ACCEPTED
I-021 | 008-010 | 481-720 | CRITICAL | anim | arm reach solved against finger-root origin, not visual tip | solver used object origin | 09b now solves on evaluated FINGER_R_INDEX bone tail; err 6 mm; tip hold (-0.021,3.956,0.399) | firefly landing re-synced | FIXED
I-022 | 008 | 481-552 | HIGH | layout | S8 camera collinear with reach vector -> hand hidden behind head | cam SW of robot | S8 cam moved SE (1.15,3.05,0.50) 3/4 front, reach reads in profile | — | FIXED
I-023 | 009 | 553-612 | HIGH | lookdev | firefly glow faced away from camera at landing | abdomen +Y default | root yaw 143deg keyed at landing (frames 583-613->636 ramp out) | — | FIXED
