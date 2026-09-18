# 《微光 / GLIMMER》 FINAL PRODUCTION REPORT
Principal Production Agent sole execution report — evidence-only. Date: 2026-09-18.
Branch `arena/01a0afae-liuflexrobo`, repo `hnsyliupeng/liuflexrobo`, project root `GLIMMER/`.

## 1. Delivery summary (verified)
| gate | required | actual | evidence |
|---|---|---|---|
| shots | 10 | 10 | `SHOT_MANIFEST.json`, 10 cams in master |
| duration | 30.0 s | 00:00:30.00 | ffprobe on `editorial/GLIMMER_PREVIEW_30S.mp4` (also inside 16_coldstart) |
| fps / frames | 24 / 720 | 24 / 720 | `renders/preview/SHOT_001..010` counts 72/72/48/72/72/72/72/72/60/108 |
| preview review cycles | >=3 | 3 | cycle-1 (720f), cycle-2a (night 528f), cycle-2b/3 (night 528f locked) — logs `preview_render.log`, `preview_render_c2.log`, `preview_render_c2b.log`, `preview_render_c3.log` |
| cold-start validation | pass | 11/11 PASS | `16_coldstart.py` → COLDSTART_PASS (cams/rig/drivers/swarm/materials/scatter/lights/slots + 4 rep frames + movie probe) |
| story/character lock | no drift | locked | STORY_LOCK.md; CHAR_001 0.57 m, teal sphere head, cyan eyes, box torso, twin tracked treads, thin arms, bent antenna — visible in `renders/preview/SHOT_001/frame_0036.jpg` etc. |
| structural realism | no primitive-stacking | modeled + scattered | 1312 scatter instances, tread plates, veined wings, buttress-root hero tree, mud/fern shaders (ASSET_MANIFEST.md) |
| audio | never gates picture | silent by decision | no audio stream in mp4s (ffprobe: 1 video stream) |

## 2. Review-cycle findings & fixes (excerpt; full list ISSUE_LOG.md I-001..I-024)
- Cycle 1: night shots unreadable (I-017) → lighting state B/C uplift; S9 firefly clipped + hand unlit (I-019) → emitter 24→6, practical point light w/ GLOW driver, firefly scale 0.45.
- Cycle 2a: firefly landed 0.6 m from real fingertip (I-018) → numeric 3-DoF arm solve `09b_arm_solve.py`; solved on finger-root not tip (I-021) → bone-tail solve, err 6 mm; S8 cam collinear with reach (I-022) → SE 3/4 cam; S9 glow faced away (I-023) → abdomen yaw 143° at landing.
- Cycle 2b: hero trunk washed pale by character key (I-024) → key moved to 1.1 m, 26→22 W, inverse-square falloff; locked.

## 3. Locked parameters
See `PARAMETER_LOCK.md` (editorial, render, lighting 3-state keys, character/FX, cameras, anim counts, gates).

## 4. Render economics (actual)
- preview 480x270 SPP6 thr0.12 volstep4: ~5.2 s/frame → 720 frames ≈ 65-75 min/pass on 2-core CPU.
- final rep 1920x1080 SPP32 thr0.05: 4 representative frames (S1 f36, S6 f372, S9 f590, S10 f690).
- Full-quality 720-frame final render intentionally NOT run (user directive: cheap tests only; parameters locked instead).

## 5. Deliverable tree
`FINAL_DELIVERY/` (built by `15_package.py`):
- `GLIMMER_PREVIEW_30S.mp4` (30.00 s master edit) + `shots/SHOT_00X_preview.mp4` x10
- `frames_preview/` 720 jpgs; `frames_final_rep/` 4x 1080p
- `blend/GLIMMER_master.blend`; `scripts/` 17 modular scripts + utils; `docs/` this report, PARAMETER_LOCK, ISSUE_LOG, SHOT_MANIFEST.json, storyboard contact sheet
- `GLIMMER_FINAL_DELIVERY.zip` at repo root (gitignored by convention; rebuilt by 15_package.py)

## 6. Reproduction
```
cd GLIMMER && ./scripts/00_bootstrap_env.sh          # venv_prod + xlibs_prod (~35 s, idempotent)
LD_LIBRARY_PATH=$PWD/xlibs_prod ./venv_prod/bin/python -u scripts/16_coldstart.py   # validate master
LD_LIBRARY_PATH=$PWD/xlibs_prod SHOTS=ALL RES=480x270 SPP=6 THR=0.12 VOLSTEP=4 \
  ./venv_prod/bin/python -u scripts/12_preview_render.py                            # 720 frames
LD_LIBRARY_PATH=$PWD/xlibs_prod TAG=preview ./venv_prod/bin/python -u scripts/14_editorial.py
```
