#!/bin/bash
# Recreate headless Blender toolchain inside the repo (survives workspace snapshots).
# Usage: bash GLIMMER/scripts/00_bootstrap_env.sh
set -e
REPO=$(cd "$(dirname "$0")/../.." && pwd)
VENV=$REPO/GLIMMER/venv_prod
XLIBS=$REPO/GLIMMER/xlibs_prod
if [ ! -x $VENV/bin/python ]; then
  python3 -m venv $VENV
  $VENV/bin/pip install --no-cache-dir -q "bpy==4.5.6" imageio-ffmpeg numpy
fi
mkdir -p $XLIBS
cd $XLIBS
BP=$VENV/lib/python3.11/site-packages/bpy
if [ ! -f $XLIBS/libGL.so.1 ]; then
  echo "" > stub.c
  nm -D -u $BP/__init__.so $BP/lib/*.so 2>/dev/null | awk '{print $NF}' | grep -vE "^_Z|^\.*$" | sort -u > all_undef.txt
  python3 - <<'EOF'
import re
syms = sorted(set(l.split('@')[0] for l in open('all_undef.txt').read().split()))
groups = {
 'libGL.so.1': ('GLVND', lambda s: s.startswith('gl')),
 'libICE.so.6': ('ICE', lambda s: s.startswith('Ice')),
 'libSM.so.6': ('SM', lambda s: s.startswith('Sm')),
 'libXfixes.so.3': ('XFIXES', lambda s: s.startswith('XFixes')),
 'libXi.so.6': ('XI', lambda s: re.match(r'^(XI[A-Z]|XCloseDevice|XOpenDevice|XSelectExtensionEvent|XQueryDeviceState|XListInputDevices|XFreeDeviceList|XFreeDeviceState|XGrabDevice|XUngrabDevice|XGetExtensionVersion|XSendExtensionEvent|_X)', s) and not s.startswith('_Z')),
 'libXrender.so.1': ('XRENDER', lambda s: s.startswith('XRender')),
 'libxkbcommon.so.0': ('V_0.5.0', lambda s: s.startswith('xkb')),
}
for lib,(ver,pred) in groups.items():
    names=[s for s in syms if pred(s)]
    base=lib.split('.')[0]
    open(f'stub_{base}.c','w').write("\n".join(f"void {s}(void){{}}" for s in names) or f"void _stub_{base}(void){{}}")
    open(f'ver_{base}.map','w').write(f"{ver} {{ global: *; }};\n")
EOF
  for b in libGL libICE libSM libXfixes libXi libXrender libxkbcommon; do
    case $b in libGL) S=libGL.so.1;; libICE) S=libICE.so.6;; libSM) S=libSM.so.6;; libXfixes) S=libXfixes.so.3;; libXi) S=libXi.so.6;; libXrender) S=libXrender.so.1;; libxkbcommon) S=libxkbcommon.so.0;; esac
    gcc -shared -fPIC -Wl,-soname,$S -Wl,--version-script=ver_$b.map -o $S stub_$b.c
  done
fi
mkdir -p $REPO/GLIMMER/{caches,renders/preview,renders/review,renders/final,editorial,FINAL_DELIVERY,shots,assets,textures}
echo "BOOTSTRAP_OK venv=$VENV xlibs=$XLIBS"
