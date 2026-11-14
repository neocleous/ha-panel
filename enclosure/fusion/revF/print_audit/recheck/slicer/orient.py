# Oriented STLs for Bambu Studio: world mesh -> build frame (pa_geom.to_build: U up, z_min 0) -> XY bbox centre at (cx, cy).
# Writes /mnt/user-data/outputs/rc/orient/<tag>_<okey>.stl (binary) and <tag>_<okey>.json with the 4x4 world->bed matrix.
# Usage: python3 orient.py <tag> <okey> [ux uy uz] [spin] [cx cy]
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world, to_build, ORIENT
tag, okey = sys.argv[1], sys.argv[2]
U = ORIENT.get(tag, {}).get(okey)
a = sys.argv[3:]
if U is None:
    U = tuple(float(v) for v in a[:3]); a = a[3:]
spin = float(a[0]) if a else 0.0
cx, cy = (float(a[1]), float(a[2])) if len(a) >= 3 else (128.0, 128.0)
mw = load_world(tag)
mb, M = to_build(mw, U, spin)
c = (mb.bounds[0][:2] + mb.bounds[1][:2]) / 2
T = np.eye(4); T[0, 3] = cx - c[0]; T[1, 3] = cy - c[1]
mb.apply_transform(T); M = T @ M
out = '/mnt/user-data/outputs/rc/orient/%s_%s' % (tag, okey)
mb.export(out + '.stl')
json.dump({'tag': tag, 'okey': okey, 'U': list(map(float, U)), 'spin': spin, 'M_world_to_bed': M.tolist(),
           'bounds_bed': mb.bounds.tolist(), 'vol_mm3': float(mb.volume)}, open(out + '.json', 'w'), indent=1)
print(tag, okey, 'bounds', np.round(mb.bounds, 2).tolist(), 'h', round(float(mb.extents[2]), 2))
