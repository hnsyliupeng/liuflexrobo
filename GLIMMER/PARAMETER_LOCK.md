# 《微光 / GLIMMER》 PARAMETER LOCK (v1.0 FINAL)

All values below are the LOCKED production parameters used for the delivered preview renders
and encoded in `GLIMMER/blend/final/GLIMMER_master.blend` + `GLIMMER/scripts/*`.
Do not change without opening a new ISSUE_LOG entry and a new review cycle.

## 1. Editorial lock
| item | value |
|---|---|
| shots | exactly 10 (SHOT_001..SHOT_010) |
| fps | 24 |
| total frames | 720 (global numbering 1..720) |
| duration | 30.000 s |
| shot ranges | S1 1-72, S2 73-144, S3 145-192, S4 193-264, S5 265-336, S6 337-408, S7 409-480, S8 481-552, S9 553-612, S10 613-720 |
| audio | none (silent picture by production decision; audio never gates picture) |

## 2. Render lock (preview / delivered quality)
| item | value |
|---|---|
| engine | Cycles CPU, Blender/bpy 4.5.6 |
| preview resolution | 480x270 (16:9), 100% |
| samples | 6 adaptive, adaptive_threshold 0.12 |
| denoise | OpenImageDenoise albedo+normal |
| volume step rate | 4.0 (preview), 1.0 (final rep) |
| volume bounces | 0; transparent bounces 8 |
| film exposure | 1.0; view transform AgX (base contrast), look None |
| final rep resolution | 1920x1080, 32 samples, thr 0.05 |
| frame cost (preview) | ~5.2 s/frame on 2-core CPU |

## 3. Lighting lock (3 states, keyed on global frames)
| light | type | keys (frame: value) | color |
|---|---|---|---|
| LIGHT_sun_dusk (A) | SUN angle 6deg | 1:3.5 -> 192:3.0 -> 264:0 | (1.0,0.62,0.32) |
| shafts 0/1 (A) | SPOT 25/18deg blend .35 | 1:13000 -> 192:10500 -> 250:0 | (1.0,0.55,0.25) |
| LIGHT_char_fill (A->B) | AREA 2.0 m | 1:30 -> 192:26 -> 235:0 | (1.0,0.72,0.42) |
| LIGHT_moon (B/C) | SUN angle 6deg | 280:2.00 -> 720:1.70 | (0.42,0.55,0.95) |
| LIGHT_night_rim (B/C) | AREA 3 m | 280:550 -> 720:460 | (0.5,0.65,1.0) at (-4.5,7.5,5.2) |
| LIGHT_night_fill (B/C) | AREA 4 m | 290:400 -> 720:340 | (0.35,0.48,0.9) at (-1.9,1.4,2.3) |
| LIGHT_robot_key (B/C) | AREA 1.4 m | 240:0 -> 280:26 -> 720:22 | (0.42,0.55,0.95) at (-1.0,2.9,1.35) |
| LIGHT_ff_practical | POINT r0.02 | driver energy = GLOW*4.0 | (0.75,0.9,0.25), parented FX_001_ctrl local (0,-0.02,0.02) |
| world (B/C) | sky ambient | 264:0.55 -> 720:0.52 | (0.05,0.09,0.20) |
| mist volume | principled volume | density 0.055 -> 0.028 by f192, aniso 0.35 | |

## 4. Character / FX locks
| item | locked value |
|---|---|
| CHAR_001 height (standing) | 0.57 m (seated at roots: chassis z ~0.12) |
| head | UV sphere r 0.155, teal painted metal (0.045,0.28,0.30) rough 0.38 |
| eyes | 2 emissive discs, gain chain EYE_GAIN x4.0; day 1.0 -> f264 0.25 -> S6 flicker -> S9/10 1.2 |
| torso | beveled box 0.24x0.16x0.26, rust-blend metal, chest panel + rivets |
| locomotion | twin tracks, 9 road wheels/side + sprocket/idler + tread plates (real tread structure) |
| arms | 3-segment thin arms, 3-segment fingers x2/hand; right arm reach solved numerically (09b), tip hold (-0.021,3.956,0.399) err 6 mm |
| antenna | bent wire + tip ball, sway driver |
| FX_001 hero firefly | scale 0.45 root; abdomen emitter strength 6.0 (multiply), thorax chitin dark, 2 veined wings flap driver 42 Hz visual alias; abdomen yaw 143deg keyed at landing |
| FX_010 swarm | GN point cloud 300-1200 pts, 3 layered noise fields + cluster bias, size 0.006-0.014, emission warm (1.0,0.85,0.35) |
| ENV_001 forest | single canonical set: hero tree r~1.1 buttress roots, 46 trunks, 1312 scatter instances (ferns/litter/rocks/moss), mud shader with puddle mask + displacement |

## 5. Camera lock (lens mm / f-stop / key frames)
S1 35mm f2.8 crane; S2 50 f2.8 dolly; S3 85 f2.0 push; S4 40 f2.8 static; S5 65 f2.8 track;
S6 100 f2.0 CU; S7 50 f2.8 orbit; S8 55 f2.8 SE 3/4 (1.15,3.05,0.50); S9 90 f2.8 macro ECU;
S10 35->28 f2.8 pull-back crane. Focus targets per shot in `08_layout_all_shots.py FOCUS`.

## 6. Animation frame-count lock
Per-shot local beats listed in `10_animation_firefly.py PATH` and `09_char_acting.py`;
all interpolation BEZIER ease-in-out except wing-flap ramp (LINEAR) and swarm drift (LINEAR noise).

## 7. Validation gates (must pass on any rebuild)
`16_coldstart.py`: master opens in clean bpy; 10 cams; 1312 scatter; 0 bad material slots;
drivers live (eyes/antenna/wings/swarm/practical); 4 rep frames render; editorial ffprobe = 30.00 s.
