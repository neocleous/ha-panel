# HA panel print audit: speaker boxes, where the slicer's support goes (rev 2: the smallest enclosing hole wins, so support in a
#   screw tube's bore, which also lies inside the chamber outline, is counted as 'tube', not 'chamber').
#   Each support extrusion (G-code) and each support-contact cell (data CF_*.npz) is mapped to world coordinates and classed by the
#   box's y-section at that height (world y is the print height; contacts are tested 0.3 mm below their face):
#     tube    = inside an enclosed hole <= 500 mm2 (screw-tube bores, the rear-wall hole);
#     chamber = inside an enclosed hole > 500 mm2 (the sealed speaker chamber);
#     outside = not enclosed (USB-A slot, finger channel, under the clip block, under the hump's outer step), split into
#               'outside_top' (world z > 76.5, above the box top: box R's hump step) and 'outside_other'.
#   Volume per class = slicer support_mm3 x extrusion-length share (equal widths assumed). Writes data/box_support_split.json.
import sys, json, numpy as np
from shapely.geometry import Point, Polygon
from shapely.prepared import prep
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world, to_build, b2w
from pa_gview import parse
T = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
CLS = ('chamber', 'tube', 'outside_top', 'outside_other')


def holes_at(m, y):
    sec = m.section(plane_origin=[0, y, 0], plane_normal=[0, 1, 0]); H = []
    if sec is None:
        return H
    P2, _ = sec.to_2D(to_2D=T)
    for poly in P2.polygons_full:
        for r in poly.interiors:
            rp = Polygon(r); H.append((rp.area, prep(rp)))
    return sorted(H, key=lambda h: h[0])            # smallest first


def classify(m, pts, y):
    H = holes_at(m, y); out = []
    for p in pts:
        P = Point(p[0], p[2]); c = None
        for area, hp in H:
            if hp.contains(P):
                c = 'tube' if area <= 500 else 'chamber'; break
        if c is None:
            c = 'outside_top' if p[2] > 76.5 else 'outside_other'
        out.append(c)
    return out


out = {}
for tag in ('spkbox_L', 'spkbox_R'):
    m = load_world(tag); mb, M = to_build(m, (0, 1, 0))
    off = json.load(open('/home/claude/pa/data/C_%s_plan.json' % tag))['offset']
    S = parse('/home/claude/pa/slice/gc_%s_plan.gcode' % tag)
    sup = S[S[:, 5] <= 1]
    a = np.c_[sup[:, 1] - off[0], sup[:, 2] - off[1], sup[:, 0]]; b = np.c_[sup[:, 3] - off[0], sup[:, 4] - off[1], sup[:, 0]]
    mid = (b2w(M, a) + b2w(M, b)) / 2
    ln = np.hypot(sup[:, 3] - sup[:, 1], sup[:, 4] - sup[:, 2])
    cls = np.empty(len(sup), dtype=object)
    for zb in np.unique(sup[:, 0]):
        sel = np.nonzero(sup[:, 0] == zb)[0]
        cls[sel] = classify(m, mid[sel], float(np.median(mid[sel, 1])))
    vol = json.loads([l for l in open('/home/claude/pa/data/gcode_summary.jsonl') if 'gc_%s_plan' % tag in l][0])['support_mm3']
    share = {k: float(ln[cls == k].sum() / ln.sum()) for k in CLS}
    CF = np.load('/home/claude/pa/work/CF_%s_plan.npz' % tag); W = CF['world']
    ccls = np.empty(len(W), dtype=object)
    for yk in np.unique(np.round(W[:, 1], 1)):
        sel = np.nonzero(np.round(W[:, 1], 1) == yk)[0]
        ccls[sel] = classify(m, W[sel], float(yk) - 0.3)
    cell = json.load(open('/home/claude/pa/data/C_%s_plan.json' % tag))['area_mm2_est'] / len(W)
    out[tag] = {'support_mm3': vol, 'length_m': round(float(ln.sum()) / 1000, 1),
                'share_by_length': {k: round(v, 3) for k, v in share.items()},
                'mm3_est': {k: round(vol * v) for k, v in share.items()},
                'contact_mm2': {k: round(float((ccls == k).sum() * cell), 1) for k in CLS}}
    print(tag, json.dumps(out[tag]), flush=True)
json.dump(out, open('/home/claude/pa/data/box_support_split.json', 'w'), indent=1)
