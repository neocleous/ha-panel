# Support blocker / enforcer boxes given in WORLD mm, written as one STL in the bed frame of an oriented print (orient/<tag>_<okey>.json).
# Usage: python3 blockers.py <tag> <okey> <name> "x0,x1,y0,y1,z0,z1;..."
import sys, json, numpy as np, trimesh
tag, okey, name, spec = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
M = np.array(json.load(open('/mnt/user-data/outputs/rc/orient/%s_%s.json' % (tag, okey)))['M_world_to_bed'])
parts = []
for s in spec.split(';'):
    x0, x1, y0, y1, z0, z1 = [float(v) for v in s.split(',')]
    b = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    b.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    b.apply_transform(M); parts.append(b)
m = trimesh.util.concatenate(parts)
out = '/mnt/user-data/outputs/rc/orient/%s_%s_%s.stl' % (tag, okey, name)
m.export(out)
print(out, len(parts), 'boxes; bed bounds', np.round(m.bounds, 2).tolist())
