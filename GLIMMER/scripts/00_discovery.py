"""P0 ENVIRONMENT DISCOVERY — verify bpy headless, engines, devices, quick benchmark frame."""
import bpy, sys, time, os

OUT = os.path.join(os.path.dirname(__file__), "..", "caches")

def main():
    print("BLENDER_VERSION:", bpy.app.version_string)
    print("BINARY:", bpy.app.binary_path)
    engines = [e.bl_idname if hasattr(e, "bl_idname") else e for e in
               bpy.types.RenderEngine.__subclasses__()]
    prefs = bpy.context.preferences
    cprefs = prefs.addons.get("cycles")
    gpu_info = "none"
    if cprefs:
        c = cprefs.preferences
        devs = []
        for dt in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
            try:
                c.compute_device_type = dt
                c.refresh_devices()
                devs += [(d.name, d.type) for d in c.devices if d.type != "CPU"]
            except Exception:
                pass
        gpu_info = str(devs) if devs else "CPU-only"
        if not devs:
            c.compute_device_type = "NONE"
    print("GPU_DEVICES:", gpu_info)
    print("ENGINES:", [i.identifier for i in
          bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items])

    # --- quick benchmark: sphere + volume-ish material, 480x270, cycles 8spp denoise
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 0))
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -1))
    bpy.ops.object.light_add(type="AREA", location=(3, -3, 4))
    bpy.context.object.data.energy = 500
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.location = (0, -6, 1.5)
    sc.camera = cam
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 8
    sc.cycles.use_denoising = True
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.1
    sc.cycles.max_bounces = 3
    sc.render.resolution_x = 480
    sc.render.resolution_y = 270
    sc.render.image_settings.file_format = "JPEG"
    sc.render.filepath = os.path.join(OUT, "bench_cycles.jpg")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t
    print("BENCH_CYCLES_480x270_8spp_sec: %.2f" % dt)

    # workbench headless test
    try:
        sc.render.engine = "BLENDER_WORKBENCH"
        sc.render.filepath = os.path.join(OUT, "bench_workbench.jpg")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("BENCH_WORKBENCH_sec: %.2f" % (time.time() - t))
    except Exception as e:
        print("WORKBENCH_FAIL:", e)

    # eevee headless test
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
        sc.render.filepath = os.path.join(OUT, "bench_eevee.jpg")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print("BENCH_EEVEE_sec: %.2f" % (time.time() - t))
    except Exception as e:
        print("EEVEE_FAIL:", type(e).__name__, e)
    print("DISCOVERY_DONE")

main()

import os as _os; _os._exit(0)

