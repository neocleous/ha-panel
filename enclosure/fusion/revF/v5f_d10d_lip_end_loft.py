# rev F d10d (2026-11-06): square-ish end on the lip (audit finding 4, decision 2 a). d10c's union of ~300 rotated station boxes
#   failed (ASM_INCONS_REL after 7 min, lesson 69). Instead: the outer face's end curve C (plane y -63.5, d10b stations) is
#   (pushed 0.02 outward, so the tool's side never lies exactly on the outer face's end edge) swept along one direction d = (0, 0.957, -0.289) - the band's normal at the top of the arch, and normal to the band's
#   run everywhere: the new end face is exactly square at the top and stays ≥ 50° to the inner face down the sides (the old
#   end met it at 17° … 38°). Tool TOOL_lip_end = loft between the region inside C (closed by a line across its two ends at z ≈ 6.6) and the same region
#   moved along d from -0.5 to 3.0 (no face of the tool on the old end plane); HOUSING_F_front minus the tool. The outer face (the door's lap) keeps its length; removal only.
#   MODE 'tool' (loader): builds TOOL_lip_end (hidden) and reports tool ∩ front; MODE 'cut': applies it (old front ->
#   HOUSING_F_front_d10, hidden) and checks the end's edges.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FR = 'HOUSING_F_front'
EXPECT = {FR: 235.8575}
STF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d10b_stations.json')
D = (0.0, 0.957, -0.289)
L = 3.0
YE = -63.5


def unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


def plane_at(X, y, name):
    pl = adsk.core.Plane.create(Dw(XC, y, 100.0), WY)
    ci = X.comp.constructionPlanes.createInput(); ci.setByPlane(pl)
    p = X.comp.constructionPlanes.add(ci); p.name = name; p.isLightBulbOn = False
    return p


def chain(st, eps=0.02):
    pts = []
    for s in st:
        if s[7] >= -0.5:
            continue
        tx, tz = s[3], s[5]; nu = (tz, -tx)                     # in-plane normal of C, pushed away from the arch's centre
        if nu[0] * s[0] + nu[1] * s[2] < 0:
            nu = (-nu[0], -nu[1])
        k = math.hypot(*nu) or 1.0
        pts.append((s[0] + eps * nu[0] / k, s[1], s[2] + eps * nu[1] / k))
    pts.sort(key=lambda p: -math.atan2(p[2], p[0]))
    out = []
    for p in pts:
        if not out or math.dist(p, out[-1]) > 0.6:
            out.append(p)
    return out


def profile_sketch(X, plane, pts, shift, name):
    sk = X.comp.sketches.add(plane); sk.name = name; sk.isLightBulbOn = False
    Q = lambda p: sk.modelToSketchSpace(Dw(XC + p[0] + shift[0], p[1] + shift[1], p[2] + shift[2]))
    coll = adsk.core.ObjectCollection.create()
    for p in pts:
        coll.add(Q(p))
    spl = sk.sketchCurves.sketchFittedSplines.add(coll)
    sk.sketchCurves.sketchLines.addByTwoPoints(spl.endSketchPoint, spl.startSketchPoint)
    pr = max((sk.profiles.item(i) for i in range(sk.profiles.count)), key=lambda p: p.areaProperties().area)
    return sk, pr


def knife_count(X, body, ymax=-60.0, zmin=6.7):
    n = 0; worst = 180.0; where = None
    for e in body.edges:
        g0 = e.startVertex.geometry; g1 = e.endVertex.geometry
        if wy(g0) > ymax or wy(g1) > ymax or wz(g0) < zmin or wz(g1) < zmin:
            continue
        fs = list(e.faces)
        if len(fs) != 2:
            continue
        p = e.pointOnEdge
        ok1, n1 = fs[0].evaluator.getNormalAtPoint(p); ok2, n2 = fs[1].evaluator.getNormalAtPoint(p)
        dih = 180.0 - math.degrees(math.acos(max(-1.0, min(1.0, n1.dotProduct(n2)))))
        if dih < worst:
            worst = dih; where = [round(p.x * 10 - XC, 2), round(wy(p), 2), round(wz(p), 2)]
        if dih < 30.0:
            n += 1
    return n, round(worst, 1), where


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); mode = globals().get('MODE', 'tool')
    try:
        fb = X.body(FR)
        if abs(fb.volume - EXPECT[FR]) > 0.0005:
            raise RuntimeError('guard: front %s' % round(fb.volume, 4))
        d = unit(D)
        if mode == 'tool':
            k_ = 1
            while X.body('TOOL_lip_end_fail%d' % k_) is not None:
                k_ += 1
            if X.body('TOOL_lip_end') is not None:                       # a failed earlier run: keep it, hidden, renamed
                X.body('TOOL_lip_end').name = 'TOOL_lip_end_fail%d' % k_
                for coll_ in (X.comp.sketches, X.comp.constructionPlanes):
                    for i_ in range(coll_.count):
                        o_ = coll_.item(i_)
                        if o_.name in ('sk_lip_end_0', 'sk_lip_end_1', 'PL_lip_end_0', 'PL_lip_end_1'):
                            o_.name = o_.name + '_fail%d' % k_
            pts = chain(json.load(open(STF))['stations'])
            pts = pts[::2] if len(pts) > 200 else pts
            out['n_pts'] = len(pts); out['ends'] = [[round(c, 2) for c in pts[0]], [round(c, 2) for c in pts[-1]]]
            s0 = tuple(-0.5 * c for c in d); sh = (d[0] * L, d[1] * L, d[2] * L)
            p1 = plane_at(X, YE + s0[1], 'PL_lip_end_0')
            p2 = plane_at(X, YE + sh[1], 'PL_lip_end_1')
            s1, pr1 = profile_sketch(X, p1, pts, s0, 'sk_lip_end_0')
            s2, pr2 = profile_sketch(X, p2, pts, sh, 'sk_lip_end_1')
            li = X.feats.loftFeatures.createInput(NEW)
            li.loftSections.add(pr1); li.loftSections.add(pr2); li.isSolid = True
            lf = X.feats.loftFeatures.add(li)
            tb = lf.bodies.item(0); tb.name = 'TOOL_lip_end'; tb.isLightBulbOn = False
            q = X.tbm.copy(tb); inter(X, q, tb_copy(X, FR))
            out['tool_cm3'] = round(tb.volume, 4); out['cut_mm3'] = round(q.volume * 1000, 2); out['cut_lumps'] = q.lumps.count
            lumps = []
            for i in range(q.lumps.count):
                bb = q.lumps.item(i).boundingBox
                c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
                lumps.append([round(c.x * 10 - XC, 1), round(wy(c), 1), round(wz(c), 1)])
            out['cut_lump_centres'] = lumps[:20]
            out['cut_bb'] = [round(v, 2) for v in wbb(X, q)] if q.volume > 0 else None
            out['tool_x_door'] = vol_x(X, tb_copy(X, 'TOOL_lip_end'), tb_copy(X, 'HOUSING_F_door'))
        else:
            tb = X.body('TOOL_lip_end')
            if X.body('HOUSING_F_front_d10') is not None:
                raise RuntimeError('HOUSING_F_front_d10 exists already')
            out['knife_before'] = knife_count(X, fb)
            c0 = X.add(tb_copy(X, FR), 'HOUSING_F_front_d10'); c0.isLightBulbOn = False
            v0 = fb.volume
            X.combine(fb, [tb], op=CUT, keep=True); fb = X.body(FR)
            out['front_cm3'] = [round(v0, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
            out['front_voids'] = sum(1 for li in range(fb.lumps.count) for si in range(fb.lumps.item(li).shells.count)
                                     if fb.lumps.item(li).shells.item(si).isVoid)
            out['knife_after'] = knife_count(X, fb)
            out['door_x_front'] = vol_x(X, tb_copy(X, 'HOUSING_F_door'), tb_copy(X, FR))
            tb.isLightBulbOn = False
        out['mode'] = mode
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d10d_lip_end_loft', globals().get('MODE', 'tool'), out)
    print(json.dumps(out, separators=(',', ':')))
