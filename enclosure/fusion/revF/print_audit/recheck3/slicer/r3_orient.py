"""recheck3: bed meshes of version 67 for the audit slices. The 0.005 measurement meshes (model mm) are put on the bed with the
print files' own world-to-bed matrices (print_files/_work/data/pf_2_orient.json), so every part lies exactly where the re-checks
and the print files put it (shell: bed z = 6.7992 - world y). Binary STL; audit meshes, not print files."""
import sys, os, json, struct, numpy as np
sys.path.insert(0, '/home/claude/r3/scan/scripts')
from fdm_lib import *
ORI = json.load(open('/mnt/user-data/uploads/HA_panel_renders/print_files/_work/data/pf_2_orient.json'))
TAGS = {'screen': 'HOUSING_F_plate', 'shell': 'HOUSING_F_front', 'spkbox_L': 'SPKBOX_L', 'spkbox_R': 'SPKBOX_R', 'base': 'FLOOR_PLATE', 'carrier': 'RESP_CARRIER',
        'cradle': 'CRADLE_5807', 'clip_L': 'TOUCH_CLIP_L', 'clip_R': 'TOUCH_CLIP_R', 'bme_hood': 'BME_HOOD', 'cap': 'HOUSING_F_cap', 'grommet': 'GROMMET_usbc_F',
        'slab': 'SLAB_frame', 'door': 'HOUSING_F_door'}
def write_stl(path, V, F, name):
    a = V[F[:, 0]]; b = V[F[:, 1]]; c = V[F[:, 2]]
    n = np.cross(b - a, c - a); L = np.linalg.norm(n, axis=1); L[L == 0] = 1.0; n = n / L[:, None]
    rec = np.zeros(len(F), dtype=[('n', '<f4', 3), ('a', '<f4', 3), ('b', '<f4', 3), ('c', '<f4', 3), ('attr', '<u2')])
    rec['n'] = n; rec['a'] = a; rec['b'] = b; rec['c'] = c
    with open(path, 'wb') as f:
        f.write(('HA panel print recheck3 v67 %s bed mm (audit mesh, not a print file)' % name).encode().ljust(80, b' ')[:80]); f.write(struct.pack('<I', len(F))); f.write(rec.tobytes())
out = {}
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
for tag, body in TAGS.items():
    v = np.fromfile(os.path.join(MESH, body + '.v.f32'), dtype=np.float32).reshape(-1, 3).astype(float)
    t = np.fromfile(os.path.join(MESH, body + '.t.i32'), dtype=np.int32).reshape(-1, 3)
    W = to_world(v); M = np.array(ORI[tag]['M'])
    B = W @ M[:3, :3].T + M[:3, 3]
    write_stl(os.path.join(OUT, tag + '_plan.stl'), B, t, tag)
    m = trimesh.Trimesh(vertices=B, faces=t, process=False)
    out[tag] = dict(body=body, tris=int(len(t)), lo=[round(float(x), 4) for x in B.min(0)], hi=[round(float(x), 4) for x in B.max(0)], vol=round(float(abs(m.volume)), 2),
                    v65_lo=ORI[tag]['lo'], v65_hi=ORI[tag]['hi'], det=round(float(np.linalg.det(M[:3, :3])), 6))
    print('%-9s tris %7d lo %s hi %s vol %.1f | v65 lo %s hi %s' % (tag, len(t), out[tag]['lo'], out[tag]['hi'], out[tag]['vol'], ORI[tag]['lo'], ORI[tag]['hi']))
json.dump(out, open(os.path.join(OUT, 'r3_orient.json'), 'w'), indent=1)
