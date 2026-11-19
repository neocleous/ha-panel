"""Print files of version 67: checks on the slices (G-code), in the bed frame of each plate.
  - totals: time and grams of every job (result.json), per set;
  - holes: support lines inside the shell's four post insert holes (two in the adhesion test), as recheck3/offline/r3_final.py;
  - plate: the screen plate's support by place: under the raised border, in the peg pocket and slot, elsewhere; and the share
    of the border the top interface layer covers (lines grown 0.15), as r3_final.py;
  - tower/feature volumes by class (part, support, interface, brim, tower) per job.
The G-code parser is recheck3/offline/r3_gparse.py's parse(). Bed meshes: print_files_v67/_work/orient/<tag>_plan.stl (bed frame
before the job's offset); the world->bed matrices of 2026-11-16 (pf_2_orient_v65.json) for the holes' axes.
Usage: python3 check67.py <out dir> <orient dir> <pf_2_orient.json> totals|holes|plate [jobs...]"""
import sys, os, re, json, math
import numpy as np
RX = re.compile(r'([XYZEF])([-+]?\d*\.?\d+)')
A = math.pi * 0.875 ** 2
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12))
SUP = ('Support', 'Support interface', 'Support transition')


def parse(path):                                    # recheck3/offline/r3_gparse.py, unchanged
    feats = []; fidx = {}; seg = []; ftag = []
    x = y = 0.0; z = 0.0; zl = 0.0; w = 0.42; f = None; li = -1; layers = []; hdr = {}; tool = 0; obj = -1; labels = []
    with open(path, 'r', errors='replace') as fh:
        for line in fh:
            c = line[0]
            if c == ';':
                if line.startswith('; FEATURE:'):
                    nm = line[10:].strip()
                    if nm not in fidx:
                        fidx[nm] = len(feats); feats.append(nm)
                    f = fidx[nm]
                elif line.startswith('; LINE_WIDTH:'):
                    w = float(line[13:])
                elif line.startswith('; Z_HEIGHT:'):
                    zl = float(line[11:]); li += 1; layers.append(zl)
                elif line.startswith('; start printing object, unique label id:'):
                    lab = int(line.split(':')[1])
                    if lab not in labels: labels.append(lab)
                    obj = lab
                elif line.startswith('; stop printing object'):
                    obj = -1
                elif line.startswith('; total layer number:'):
                    hdr['n_layers'] = int(line.split(':')[1])
                elif line.startswith('; EXECUTABLE_BLOCK_END'):
                    break
                continue
            if c == 'T' and line[1:].strip().isdigit() and int(line[1:].strip()) < 16:
                tool = int(line[1:].strip()); continue
            if c != 'G' or not (line.startswith('G1 ') or line.startswith('G0 ')):
                continue
            k = line.find(';'); body = line if k < 0 else line[:k]
            nx, ny, e = x, y, None
            for a, v in RX.findall(body):
                if a == 'X': nx = float(v)
                elif a == 'Y': ny = float(v)
                elif a == 'Z': z = float(v)
                elif a == 'E': e = float(v)
            if e is not None and e > 0 and (nx != x or ny != y) and li >= 0 and f is not None:
                seg.append((x, y, nx, ny, zl, e, w, li, tool, obj)); ftag.append(f)
            x, y = nx, ny
    return np.array(seg, np.float32), np.array(ftag, np.uint8), feats, np.array(layers, np.float32), hdr


def cls_of(n):
    return 'interface' if n == 'Support interface' else ('support' if 'Support' in n else ('brim' if n in ('Brim', 'Skirt') else
           ('tower' if 'tower' in n.lower() else 'part')))


def load(out, job):
    S, F, names, L, hdr = parse(os.path.join(out, job, 'plate_1.gcode'))
    return S, F, names, L, hdr


def slab_to_world(x, up, d):
    return np.array([x, -d * C12 - up * S12, 143.3 - d * S12 + up * C12])


HOLES = (('top post, viewer left', 70, 27, 12.8), ('top post, viewer right', -70, 27, 12.8),
         ('bottom post, viewer left', 85, -82, 11.6), ('bottom post, viewer right', -85, -82, 11.6))


def holes(out, M, job, pos, which=HOLES, r=1.9, zmax=None):
    S, F, names, L, hdr = load(out, job)
    Mm = np.array(M); sup = np.isin(F, [i for i, n in enumerate(names) if n in SUP])
    tob = lambda W: np.atleast_2d(W) @ Mm[:3, :3].T + Mm[:3, 3] + np.array(pos, float)
    res = []
    for nm, x, up, d0 in which:
        a = tob(slab_to_world(x, up, d0))[0]; b = tob(slab_to_world(x, up, d0 + 6.35))[0]
        ax = (b - a) / np.linalg.norm(b - a); Ln = np.linalg.norm(b - a)
        P = np.stack([(S[:, 0] + S[:, 2]) / 2, (S[:, 1] + S[:, 3]) / 2, S[:, 4] - 0.1], axis=1).astype(float) - a
        t = P @ ax; rad = np.linalg.norm(P - np.outer(t, ax), axis=1); m = sup & (t > 0) & (t < Ln) & (rad < r)
        if zmax is not None:
            m &= S[:, 4] <= zmax + 1e-3
        ln = np.hypot(S[m, 2] - S[m, 0], S[m, 3] - S[m, 1])
        res.append((nm, round(float((ln * S[m, 6] * 0.2).sum()), 2), int(m.sum()), [round(float(c), 2) for c in a]))
    return res


def plate(out, orient, job, pos=(0, 0, 0)):
    import trimesh, shapely
    from shapely.ops import unary_union
    from shapely.geometry import MultiPolygon, Polygon
    m = trimesh.load(os.path.join(orient, 'screen_plan.stl')); m.apply_translation(pos)
    def layer(z):
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1]); p2, T = sec.to_2D()
        polys = [shapely.affinity.affine_transform(p, [T[0, 0], T[0, 1], T[1, 0], T[1, 1], T[0, 3], T[1, 3]]) for p in p2.polygons_full]
        return unary_union(polys)
    def polys_of(g):
        return [g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))
    L1 = layer(0.1); L8 = layer(1.5); B = L8.difference(L1.buffer(0.01))
    hl = [Polygon(r) for p in polys_of(L1) for r in p.interiors if 40 < Polygon(r).area < 100]
    S, F, names, L, hdr = load(out, job)
    sup = np.isin(F, [i for i, n in enumerate(names) if n in SUP]); isif = np.isin(F, [i for i, n in enumerate(names) if n == 'Support interface'])
    def foot(mask, grow=0.0):
        s = S[mask]
        if not len(s): return MultiPolygon()
        co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float)
        return shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2 + grow, quad_segs=3))
    Fs = foot(sup); top = isif & (S[:, 4] > 0.7)
    cov = (foot(top, 0.15).intersection(B).area / B.area) if top.any() else 0.0
    if not top.any():                                       # plain trees: the top support layer, whatever its type
        zt = S[sup, 4].max() if sup.any() else 0
        cov_any = foot(sup & (np.abs(S[:, 4] - zt) < 1e-3), 0.15).intersection(B).area / B.area if sup.any() else 0.0
    else:
        cov_any = None
    ins = sum(Fs.intersection(h).area for h in hl)
    else_ = Fs.difference(unary_union([B.buffer(0.3)] + hl))
    big = sorted([p for p in polys_of(else_) if p.area > 1], key=lambda p: -p.area)
    return {'border_mm2': round(B.area, 1), 'n_border': len(polys_of(B)), 'holes_mm2': [round(h.area, 1) for h in hl],
            'support_mm2': round(Fs.area, 1), 'under_border_mm2': round(Fs.intersection(B).area, 1), 'in_pocket_slot_mm2': round(ins, 2),
            'elsewhere_mm2': round(Fs.difference(unary_union([B] + hl)).area, 1),
            'top_interface_cover_pct': round(100 * cov, 1), 'top_support_cover_pct': (round(100 * cov_any, 1) if cov_any is not None else None),
            'support_layer_tops': sorted(set(np.round(S[sup, 4], 2).tolist())),
            'outside_border_pieces': [[round(p.area, 1)] + [round(c, 1) for c in np.array(p.bounds)[[0, 2, 1, 3]]] for p in big[:6]]}


def classes(out, job):
    S, F, names, L, hdr = load(out, job)
    tot = {}
    for i, n in enumerate(names):
        v = float(S[F == i, 5].sum() * A)
        if v > 0:
            tot[cls_of(n)] = tot.get(cls_of(n), 0.0) + v
    return {k: round(v, 1) for k, v in tot.items()}, hdr.get('n_layers')


def totals(out, jobs):
    res = {}
    for j in jobs:
        r = json.load(open(os.path.join(out, j, 'result.json'))); pl = r['sliced_plates'][0]
        res[j] = {'print_min': round(pl['main_predication'] / 60.0, 1), 'prep_min': round(pl['total_predication'] / 60.0, 1),
                  'g': [round(f['total_used_g'], 2) for f in pl['filaments']], 'warn': (pl.get('warning_message') or '').replace('\n', ' ')[:200],
                  'rc': r.get('return_code')}
    return res


if __name__ == '__main__':
    out, orient, ori, what = sys.argv[1:5]; jobs = sys.argv[5:]
    ORI = json.load(open(ori))
    if what == 'totals':
        print(json.dumps(totals(out, jobs), indent=1))
    elif what == 'holes':
        for j in jobs:
            pos = (0, -30, 0) if j.startswith(('A', 'F')) else (0, 0, 0)
            zmax = 8.0 if 'adh' in j else None
            which = HOLES[2:] if 'adh' in j else HOLES
            print(j, holes(out, ORI['shell']['M'], j, pos, which, zmax=zmax))
    elif what == 'plate':
        for j in jobs:
            print(j, json.dumps(plate(out, orient, j)))
    elif what == 'classes':
        for j in jobs:
            print(j, classes(out, j))
