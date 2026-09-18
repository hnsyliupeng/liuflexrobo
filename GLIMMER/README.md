# GLIMMER 《微光》 — 30 s / 10 shots / 24 fps autonomous animation project

Principal production agent project (single-agent pipeline, Blender 4.5 LTS via headless `bpy`).

## What this is
A complete, parameter-locked production of the locked story 《微光 / GLIMMER》:
10 shots, exactly 720 editorial frames @ 24 fps = 30.0 s, one canonical forest environment,
one rigged robot character (CHAR_001), one hero firefly (FX_001) + 900-point GN swarm (FX_010),
three keyframed lighting states (dusk / blue-night transition / firefly night), Cycles CPU
rendering with AgX view transform. No background music by design.

## Repository map
- `STORY_LOCK.md`, `SHOT_MANIFEST.json` — locked story & exact timing
- `reference/GLIMMER_storyboard_contact_sheet.png` — approved 10-panel visual baseline
- `scripts/` — modular production pipeline (00 discovery → 15 package), `scripts/utils/` shared libs
- `blend/final/GLIMMER_master.blend` — single-source master (all shots on global timeline 1–720,
  10 cameras `CAM_SHOT_001..010`, collections `CHAR_001_robot`, `ENV_001_assets`,
  `ENV_001_scene`, `FX_fireflies`, `LAY_cameras`, `LAY_lights`)
- `renders/review/` — representative validation stills (480×270 Cycles, denoised)
- `renders/preview/SHOT_xxx/` — 720-frame preview sequence (480×270)
- `editorial/` — per-shot mp4 + assembled 30.0 s film
- `FINAL_DELIVERY/` + `GLIMMER_FINAL_DELIVERY.zip` — packaged delivery
- Production memory: `TASK_STATE.md`, `PRODUCTION_PLAN.md`, `ASSET_MANIFEST.md`,
  `SHOT_STATUS.md`, `ISSUE_LOG.md`, `PERFORMANCE_LOG.md`, `CHANGE_LOG.md`

## Running the pipeline
```bash
export LD_LIBRARY_PATH=/home/user/.xlibs     # stub X/GL libs for headless bpy
/home/user/.venv/bin/python scripts/NN_name.py
```
Render preview: `SHOTS=ALL RES=480x270 SPP=8 python scripts/12_preview_render.py`
Assemble: `TAG=preview python scripts/14_editorial.py`
Final-quality representative frames: `python scripts/13_final_render.py`

## Delivery scope (per producer directive)
Parameters / materials / model structure / animation timing are locked and delivered with
low-res validation renders + assembled 30 s preview film. A full 720-frame 1080p final render
is NOT included (script 13 reproduces it: 1920×1080, 64 spp, OIDN).
