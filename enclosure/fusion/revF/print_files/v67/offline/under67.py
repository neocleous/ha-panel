"""Print files of version 67: what lies under named faces of the shell that look at the bed (recheck3/offline/r3_under.py's
method on this run's bed mesh): per layer, the part of the model's section inside a world box that reaches more than `step`
beyond the layer below (opened by 0.08), and the share of it with support / interface lines in the 0.45 below.
Usage: python3 under67.py <gcode> <pos_y> [label]"""
import sys, json, numpy as np, shapely, trimesh
from shapely.geometry import box, MultiPolygon
from shapely.ops import unary_union
sys.path.insert(0, '.')
from check67 import parse, SUP
W0 = '/mnt/user-data/uploads/HA_panel_renders/print_files_v67/_work/'
ORI = json.load(open('/home/claude/pf_2_orient_v65.json')); M = np.array(ORI['shell']['M'])
PART_EXCL = ('Support', 'Support interface', 'Support transition', 'Brim', 'Skirt', 'Custom', 'Prime tower')
CASES = [('top post land, viewer left', [65, -19.5, 161], [75, -16.5, 172], 0.25),
         ('top post land, viewer right', [-75, -19.5, 161], [-65, -16.5, 172], 0.25),
         ('bottom post land and peg, viewer left', [79, 2.5, 54], [91, 6.2, 66.5], 0.25),
         ('bottom post land and peg, viewer right', [-91, 2.5, 54], [-79, 6.2, 66.5], 0.25),
         ('lip at the top of the arch', [-45, -63.4, 138], [45, -55.3, 158.5], 0.25),
         ('radar pocket and its brace', [-86, -34, 112], [-62, -5, 143], 0.25),
         ("cloth groove's roof, x -48..48", [-48.5, 4.4, 48.7], [48.5, 6.0, 50.6], 0.25),
         ("band along the chin's top edge (groove to screen)", [-92, 4.0, 50.4], [92, 6.6, 53.4], 0.1)]


class Shell:
    def __init__(self, pos):
        self.pos = np.array(pos, float)
        self.m = trimesh.load(W0 + 'orient/shell_plan.stl', process=True); self.m.apply_translation(self.pos); self._l = {}
    def to_bed(self, Wp):
        return np.atleast_2d(np.asarray(Wp, float)) @ M[:3, :3].T + M[:3, 3] + self.pos
    def layer(self, z):
        k = round(z, 4)
        if k not in self._l:
            sec = self.m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if sec is None: self._l[k] = MultiPolygon()
            else:
                p2, T = sec.to_2D()
                self._l[k] = unary_union([shapely.affinity.affine_transform(p, [T[0, 0], T[0, 1], T[1, 0], T[1, 1], T[0, 3], T[1, 3]]) for p in p2.polygons_full])
        return self._l[k]


def under(S, F, names, Lz, sh, wlo, whi, step):
    c = sh.to_bed([wlo, whi]); lo = c.min(0); hi = c.max(0); Wb = box(lo[0], lo[1], hi[0], hi[1])
    part = ~np.isin(F, [i for i, n in enumerate(names) if n in PART_EXCL])
    sup = np.isin(F, [i for i, n in enumerate(names) if n in SUP]); isif = np.isin(F, [i for i, n in enumerate(names) if n == 'Support interface'])
    near = (np.minimum(S[:, 0], S[:, 2]) < hi[0] + 1) & (np.maximum(S[:, 0], S[:, 2]) > lo[0] - 1) & (np.minimum(S[:, 1], S[:, 3]) < hi[1] + 1) & (np.maximum(S[:, 1], S[:, 3]) > lo[1] - 1)
    PL = sorted(set(S[part, 7].astype(int).tolist())); zs = [float(Lz[i]) for i in PL]
    tot = dict(area=0.0, sup=0.0, ifc=0.0); n = 0
    for k, li in enumerate(PL):
        zt = zs[k]; lh = zt - (zs[k - 1] if k else 0.0)
        if not (lo[2] - 0.21 <= zt <= hi[2] + 0.21): continue
        zm = zt - lh / 2; zb = zt - lh
        Mo = sh.layer(zm); Pr = sh.layer(zm - lh) if zm - lh > 0 else MultiPolygon()
        O = Mo.difference(Pr.buffer(step, quad_segs=3)).intersection(Wb).buffer(-0.08).buffer(0.08)
        if O.is_empty or O.area < 0.05: continue
        def cov(msk):
            s = S[msk]
            if not len(s): return 0.0
            co = np.stack([s[:, 0:2], s[:, 2:4]], axis=1).astype(float)
            return shapely.union_all(shapely.buffer(shapely.linestrings(co), s[:, 6].astype(float) / 2 + 0.15, quad_segs=3)).intersection(O).area / O.area
        below = near & (S[:, 4] > zb - 0.45) & (S[:, 4] <= zb + 1e-3)
        a = O.area; tot['area'] += a; tot['sup'] += cov(below & sup) * a; tot['ifc'] += cov(below & isif) * a; n += 1
    if tot['area'] > 0:
        tot['sup'] /= tot['area']; tot['ifc'] /= tot['area']
    return tot, n


if __name__ == '__main__':
    g = sys.argv[1]; posy = float(sys.argv[2]); label = sys.argv[3] if len(sys.argv) > 3 else g
    S, F, names, Lz, hdr = parse(g); sh = Shell((0, posy, 0))
    print(label)
    for nm, a, b, step in CASES:
        t, n = under(S, F, names, Lz, sh, a, b, step)
        print('   %-40s %7.1f mm2 over %2d layers | support under %3.0f%% (interface %3.0f%%)' % (nm, t['area'], n, 100 * t['sup'], 100 * t['ifc']))
