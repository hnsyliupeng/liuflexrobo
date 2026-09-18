"""Apply smooth-by-angle shading to character/FX meshes (kill visible facets at 1080p)."""
import bpy, math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G
bpy.ops.wm.open_mainfile(filepath=G.master_path())
n = 0
for ob in bpy.data.objects:
    if ob.type == "MESH" and (ob.name.startswith("CHAR_001") or ob.name.startswith("FX_001") or ob.name.startswith("CHAR_001_finger")):
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        try:
            bpy.ops.object.shade_auto_smooth(angle=math.radians(35))
            n += 1
        except Exception as e:
            print("SMOOTH_SKIP", ob.name, e)
print("SMOOTH_PASS objs=", n)
G.save(G.master_path())
print("SMOOTH_DONE")
main_done = True

import os as _os; _os._exit(0)

