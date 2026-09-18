# PERFORMANCE_LOG

| test | config | result |
|---|---|---|
| P0 bench sphere+volume | Cycles CPU 480x270 8spp OIDN | 1.98 s/frame |
| forest representative still | Cycles CPU 480x270 8spp OIDN, mist volume | ≈5.7–6.4 s/frame |
| 720-frame preview estimate | 480x270 8spp | ≈70–80 min single process |
| EEVEE Next headless | bpy module, no GPU | unavailable (engine needs GPU context) |
| Workbench headless | — | not used (clay only, no lighting validation) |

Engine decision (benchmark gate §36): **Cycles CPU** — only engine available headless;
throughput sufficient for 720-frame preview; final-quality representative frames at
1920x1080 64spp rendered separately (script 13).

Volumetrics: single global scatter volume, density 0.009–0.020 (keyframed by light state),
volume_step_rate 2.0, volume_bounces 0 — cheap, no geometry hiding.

Memory: master.blend ≈ 4.4 MB (procedural materials + linked duplicates); render RSS ≈ 1.3 GB.
