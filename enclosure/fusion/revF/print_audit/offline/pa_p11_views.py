# HA panel print audit (P11): G-code layer views of the flagged regions (PrusaSlicer 2.7.2, assumed X2D/ASA profile).
#   Coordinates on the plots are build-frame mm (bed minus the arrange offset). Grey = layer below, red = support,
#   magenta = support interface, blue = bridge infill, orange = overhang perimeter, black = part.
import sys; sys.path.insert(0, '/home/claude/pa')
from pa_gview import view
OFF = {'bracket_L_plan': (82.5, 186.7), 'bracket_R_plan': (181.25, 186.199), 'slab_plan': (238.275, 151.44),
       'front_plan': (128.003, 164.978), 'grommet_plan': (150.15, 128.0), 'door_plan': None, 'cradle_plan': None,
       'spkbox_R_plan': None}
V = [
 ('bracket_L_plan', 0.2, (28, 62, -80, -44), 'bracket L z0.2 first layer'),
 ('bracket_L_plan', 7.2, (28, 62, -80, -44), 'bracket L z7.2'),
 ('bracket_L_plan', 40.0, (28, 62, -80, -44), 'bracket L z40 tree trunk'),
 ('bracket_L_plan', 74.2, (34, 52, -70, -50), 'bracket L z74.2 top arm on support'),
 ('bracket_R_plan', 0.2, (-70, -34, -80, -44), 'bracket R z0.2 first layer'),
 ('bracket_R_plan', 18.4, (-70, -34, -80, -44), 'bracket R z18.4 plate on support'),
 ('bracket_R_plan', 18.6, (-70, -34, -80, -44), 'bracket R z18.6'),
 ('bracket_R_plan', 74.2, (-52, -34, -70, -50), 'bracket R z74.2 top arm on support'),
 ('slab_plan', 0.2, (-200, -20, -142, 95), 'slab glass-down z0.2'),
 ('slab_plan', 1.0, (-200, -20, -142, 95), 'slab z1.0 support interface'),
 ('slab_plan', 1.4, (-200, -20, -142, 95), 'slab z1.4 ledge over interface'),
 ('slab_plan', 1.4, (-200, -160, -142, -100), 'slab z1.4 corner detail'),
 ('front_plan', 169.4, (-56, 56, -56, -20), 'front z169.4 SL/SR pads'),
 ('front_plan', 169.6, (-56, 56, -56, -20), 'front z169.6 SL/SR pads'),
 ('front_plan', 120.0, (-56, 56, -56, -20), 'front z120 pad support column'),
 ('front_plan', 114.4, (-92, -58, -36, -6), 'front z114.4 LD cradle floor'),
 ('front_plan', 143.0, (-100, 100, -20, 12), 'front z143 top band'),
 ('grommet_plan', 0.2, (-38, -8, -20, 20), 'grommet flange-down z0.2'),
 ('grommet_plan', 0.6, (-38, -8, -20, 20), 'grommet z0.6'),
 ('grommet_plan', 1.4, (-38, -8, -20, 20), 'grommet z1.4'),
 ('grommet_plan', 2.2, (-38, -8, -20, 20), 'grommet z2.2'),
]
if __name__ == '__main__':
    import json
    out = []
    for tag, z, crop, title in V:
        fn = '/home/claude/pa/img/p11/%s_z%.1f%s.png' % (tag.replace('_plan', ''), z, '_c' if 'detail' in title else '')
        zz = view('/home/claude/pa/slice/gc_%s.gcode' % tag, z, OFF[tag], crop=crop, out=fn, title=title, size=(5, 4.2), dpi=110, below=z - 0.2)
        out.append((fn, zz)); print(fn, zz)
    json.dump(out, open('/home/claude/pa/data/p11_views.json', 'w'))
