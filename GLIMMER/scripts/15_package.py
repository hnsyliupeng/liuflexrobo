"""P22 Final package — populate FINAL_DELIVERY, write manifests, zip."""
import os, sys, shutil, subprocess, json, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utils"))
import glib as G

FD = os.path.join(G.ROOT, "FINAL_DELIVERY")

def cp(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dst)

def main():
    os.makedirs(FD, exist_ok=True)
    # film
    ed = os.path.join(G.ROOT, "editorial")
    for f in os.listdir(ed):
        if f.endswith(".mp4"):
            cp(os.path.join(ed, f), os.path.join(FD, "film", f))
    if os.path.exists(os.path.join(ed, "GLIMMER_PREVIEW_30S.mp4")):
        cp(os.path.join(ed, "GLIMMER_PREVIEW_30S.mp4"), os.path.join(FD, "film", "GLIMMER_30S_FINAL.mp4"))
    # blender project
    cp(os.path.join(G.ROOT, "blend", "final", "GLIMMER_master.blend"), os.path.join(FD, "blender", "GLIMMER_master.blend"))
    # scripts / docs / reference
    cp(os.path.join(G.ROOT, "scripts"), os.path.join(FD, "scripts"))
    cp(os.path.join(G.ROOT, "reference"), os.path.join(FD, "reference"))
    for doc in ("README.md", "STORY_LOCK.md", "SHOT_MANIFEST.json", "ASSET_MANIFEST.md",
                "PRODUCTION_PLAN.md", "SHOT_STATUS.md", "ISSUE_LOG.md", "PERFORMANCE_LOG.md",
                "TASK_STATE.md", "CHANGE_LOG.md"):
        p = os.path.join(G.ROOT, doc)
        if os.path.exists(p):
            cp(p, os.path.join(FD, doc))
    cp(os.path.join(G.ROOT, "SHOT_MANIFEST.json"), os.path.join(FD, "GLIMMER_SHOT_MANIFEST.json"))
    # representative final renders
    fr = os.path.join(G.ROOT, "renders", "final")
    if os.path.isdir(fr):
        cp(fr, os.path.join(FD, "renders"))
    # preview frame sequences (low-res validation)
    pv = os.path.join(G.ROOT, "renders", "preview")
    if os.path.isdir(pv) and os.environ.get("INCLUDE_PREVIEW_FRAMES", "0") == "1":
        cp(pv, os.path.join(FD, "renders_preview"))
    # zip
    zpath = os.path.join(G.ROOT, "GLIMMER_FINAL_DELIVERY")
    if os.path.exists(zpath + ".zip"):
        os.remove(zpath + ".zip")
    subprocess.run(["sh", "-c", "cd %s && zip -qr %s.zip FINAL_DELIVERY -x '*.blend1*'" % (G.ROOT, zpath)], check=False)
    print("PACKAGE_DONE zip=%s.zip" % zpath)

main()

import os as _os; _os._exit(0)

