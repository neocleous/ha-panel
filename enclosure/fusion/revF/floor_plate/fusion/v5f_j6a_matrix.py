# rev F j6a (2026-11-12): close, block 6.1 - read-only: interference of every current body against every other, mm3.
#   Bodies: everything current() gives with leads and keep-outs (no backups, no legacy, no REF_/TOOL_/INNER/RENDER_/AUD_), plus the
#   display's standoffs whose names end in " (n)" (they are parts of the display; the backup filter drops them by their name).
#   Per pair the smaller body is copied and intersected with the larger one (lesson 105). Where the larger body is the front shell,
#   the door, the plate or the slab frame, the smaller body's box (grown 0.5) is first cut out of it, so that a detailed body never
#   meets the whole shell (lesson 115).
#   Results are kept in the cache and a call stops after BUDGET seconds: call until 'left' is 0. ONLY (global): restrict to pairs with
#   one of the named bodies.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
BUDGET = globals().get('BUDGET', 35.0)
ONLY = globals().get('ONLY', None)
BIG = ('HOUSING_F_front', 'HOUSING_F_door', 'FLOOR_PLATE', 'SLAB_frame')
EXTRA = re.compile(r'^LCD_.* \(\d+\)$')


def bodies(X):
    out = current(X, leads=True)
    names = set(b.name for b in out)
    for b in X.root.bRepBodies:
        if EXTRA.match(b.name) and b.name not in names:
            out.append(b)
    return out


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        bs = sorted(bodies(X), key=lambda b: b.volume)
        st['bodies'] = len(bs)
        res = c.setdefault('j6a', {})
        tm = c.setdefault('j6a_t', {})
        left = 0; fails = []; nxt = []
        for i, a in enumerate(bs):
            for b in bs[i + 1:]:
                if ONLY and a.name not in ONLY and b.name not in ONLY:
                    continue
                k = a.name + '|' + b.name
                if k in res:
                    continue
                if not a.boundingBox.intersects(b.boundingBox):
                    res[k] = 0.0; continue
                if time.time() - t0 > BUDGET:
                    left += 1
                    if len(nxt) < 12:
                        nxt.append(k)
                    continue
                tp = time.time()
                small = tcopy(X, a.name); big = tcopy(X, b.name)
                try:
                    if b.name in BIG:
                        bb = small.boundingBox
                        obb = adsk.core.OrientedBoundingBox3D.create(P3((bb.minPoint.x + bb.maxPoint.x) / 2.0, (bb.minPoint.y + bb.maxPoint.y) / 2.0, (bb.minPoint.z + bb.maxPoint.z) / 2.0),
                                                                     V3(1, 0, 0), V3(0, 1, 0), bb.maxPoint.x - bb.minPoint.x + 0.1, bb.maxPoint.y - bb.minPoint.y + 0.1,
                                                                     bb.maxPoint.z - bb.minPoint.z + 0.1)
                        piece = X.tbm.createBox(obb)
                        X.tbm.booleanOperation(piece, big, BT.IntersectionBooleanType)
                        if X.vol(piece) < 1e-6:
                            res[k] = 0.0; continue
                        big = piece
                    t = X.cp(small)
                    X.tbm.booleanOperation(t, big, BT.IntersectionBooleanType)
                    res[k] = round(X.vol(t), 2)
                except Exception:
                    res[k] = -1.0; fails.append(k)
                tm[k] = round(time.time() - tp, 1)
        st['pairs done'] = len(res); st['left'] = left; st['failed'] = fails
        st['next'] = nxt; st['slowest'] = sorted(tm.items(), key=lambda kv: -kv[1])[:10]
        st['not zero'] = {k: v for k, v in sorted(res.items()) if abs(v) > 0.005}
        st['names'] = [b.name for b in bs]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j6a', st)


run(None)
