"""Front as a PrusaSlicer 3MF with support blockers (boxes, world mm x_rel): the four cap-screw pads' undersides, the
exhaust rows and the 10 lip magnet pockets. Usage: d22_blocker_3mf.py <front.stl> <out.3mf> [pads|all]"""
import sys, io, zipfile, numpy as np
src, out, mode = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else 'all')
with open(src, 'rb') as fh:
    fh.read(80); n = int(np.frombuffer(fh.read(4), np.uint32)[0])
    d = np.frombuffer(fh.read(n * 50), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]))
V = d['v'].reshape(-1, 3).astype(np.float64)
Vr, inv = np.unique(np.round(V, 4), axis=0, return_inverse=True)
T = inv.reshape(-1, 3)
boxes = []
for s in (1, -1):                                              # pad undersides (SL / SR, BL / BR), above the rib bottoms
    boxes.append(('pad_side', sorted((s * 30.0, s * 50.0)), (-46.0, -26.0), (166.0, 169.7)))
    boxes.append(('pad_back', sorted((s * 18.5, s * 33.5)), (-47.0, -30.0), (166.0, 169.7)))
if mode == 'all':
    boxes.append(('exhaust', (-46.0, 46.0), (-58.0, -40.0), (160.5, 170.2)))
    for (x, y, z) in ((72.59, -60.47, 24.92), (67.74, -60.20, 59.85), (58.87, -59.66, 94.70), (39.89, -58.68, 131.11), (16.04, -58.15, 148.35)):
        for s in (1, -1):
            boxes.append(('magnet', (s * x - 5.0, s * x + 5.0), (y - 5.0, y + 5.0), (z - 5.0, z + 5.0)))
BV, BT = [], []
for i, (nm, (x0, x1), (y0, y1), (z0, z1)) in enumerate(boxes):
    o = len(Vr) + 8 * i
    BV += [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    q = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1), (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    BT += [(o + a, o + c, o + b) for (a, b, c) in q]       # outward normals for this vertex order: flip to outward
Vall = np.vstack([Vr, np.array(BV)]); Tall = np.vstack([T, np.array(BT)])
# orient each box's triangles outward (centroid test)
for i in range(len(boxes)):
    o = len(T) + 12 * i; c = np.array(BV[8 * i:8 * i + 8]).mean(0)
    for k in range(o, o + 12):
        a, b, cc = Vall[Tall[k]]
        if np.dot(np.cross(b - a, cc - a), a - c) < 0:
            Tall[k] = Tall[k][[0, 2, 1]]
buf = io.StringIO()
buf.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
          'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n<resources>\n<object id="1" type="model">\n<mesh>\n<vertices>\n')
np.savetxt(buf, Vall, fmt='<vertex x="%.4f" y="%.4f" z="%.4f"/>')
buf.write('</vertices>\n<triangles>\n')
np.savetxt(buf, Tall, fmt='<triangle v1="%d" v2="%d" v3="%d"/>')
buf.write('</triangles>\n</mesh>\n</object>\n</resources>\n<build>\n<item objectid="1"/>\n</build>\n</model>\n')
cfg = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n<object id="1" instances_count="1">\n'
       '<metadata type="object" key="name" value="front_d22"/>\n']
cfg.append('<volume firstid="0" lastid="%d">\n<metadata type="volume" key="name" value="front"/>\n'
           '<metadata type="volume" key="volume_type" value="ModelPart"/>\n</volume>\n' % (len(T) - 1))
for i, b in enumerate(boxes):
    f0 = len(T) + 12 * i
    cfg.append('<volume firstid="%d" lastid="%d">\n<metadata type="volume" key="name" value="blk_%s_%d"/>\n'
               '<metadata type="volume" key="volume_type" value="SupportBlocker"/>\n</volume>\n' % (f0, f0 + 11, b[0], i))
cfg.append('</object>\n</config>\n')
ct = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
      '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n</Types>\n')
rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        '</Relationships>\n')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct); z.writestr('_rels/.rels', rels)
    z.writestr('3D/3dmodel.model', buf.getvalue()); z.writestr('Metadata/Slic3r_PE_model.config', ''.join(cfg))
print('vertices', len(Vall), 'triangles', len(Tall), 'blockers', len(boxes))
