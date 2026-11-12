# rev F j6a2 (2026-11-12): close, block 6.1 - read-only: the interference matrix of j6a, finished for the pairs with a big body
#   (front shell, door, base plate, slab frame). j6a cut the small body's box out of the big body for every pair; with the shell or the
#   door as the tool that costs 25-35 s a pair (the tool is copied inside the boolean, lesson 133). Here:
#   1. the minimum distance of the two model bodies is measured first; a pair that does not touch (> 0.0005) is 0 mm3 and is done
#      (lesson 134);
#   2. a big body is cut once into NT slabs along its longest axis (cached; the slabs' volumes are checked against the body's);
#      a pair that touches is intersected slab by slab, only with the slabs its box reaches. Two big bodies: slab against slab.
#   Same cache table as j6a ('j6a'), so the pairs j6a finished are kept. Distances of the pairs with a big body: table 'j6a_d'.
#   A call stops after BUDGET seconds: call until 'left' is 0.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
BUDGET = globals().get('BUDGET', 30.0)
BIG = ('HOUSING_F_front', 'HOUSING_F_door', 'FLOOR_PLATE', 'SLAB_frame')
NT = 8
EXTRA = re.compile(r'^LCD_.* \(\d+\)$')


def bodies(X):
    out = current(X, leads=True)
    names = set(b.name for b in out)
    for b in X.root.bRepBodies:
        if EXTRA.match(b.name) and b.name not in names:
            out.append(b)
    return out


def slabs(b):                                   # (axis, [(lo, hi)], box centre, box sizes) of a model body, cm, design frame
    bb = b.boundingBox
    mn = [bb.minPoint.x, bb.minPoint.y, bb.minPoint.z]; mx = [bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z]
    sz = [mx[i] - mn[i] for i in range(3)]
    ax = sz.index(max(sz))
    st = sz[ax] / NT
    return ax, [(mn[ax] + i * st, mn[ax] + (i + 1) * st) for i in range(NT)], [(mn[i] + mx[i]) / 2.0 for i in range(3)], sz


VV = {}                                         # volume of each model body, read once a call: a big body's volume costs up to a second (lesson 135)


def tile(X, c, b, i, t0):                       # cached slab i of big body b; None if the budget is used up before it can be made
    k = ('tile', b.name, round(VV[b.name], 6), i)
    if k not in c:
        if time.time() - t0 > BUDGET:
            return None
        ax, rng, cen, sz = slabs(b)
        cc = list(cen); ss = [s + 0.02 for s in sz]
        cc[ax] = (rng[i][0] + rng[i][1]) / 2.0; ss[ax] = rng[i][1] - rng[i][0]
        box = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P3(*cc), V3(1, 0, 0), V3(0, 1, 0), ss[0], ss[1], ss[2]))
        X.tbm.booleanOperation(box, tcopy(X, b.name), BT.IntersectionBooleanType)
        c[k] = box
    kv = ('tilev',) + k[1:]
    if kv not in c:
        c[kv] = X.vol(c[k])                         # the volume of a detailed temporary body costs seconds: read once (lesson 135)
    return c[k]


def tvol(c, b, i):
    return c.get(('tilev', b.name, round(VV[b.name], 6), i))


def reach(b, ax, rng):                          # indices of the slabs a body's box reaches
    bb = b.boundingBox
    lo = [bb.minPoint.x, bb.minPoint.y, bb.minPoint.z][ax]; hi = [bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z][ax]
    return [i for i, (a, z) in enumerate(rng) if hi >= a and lo <= z]


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        st['t'] = [round(time.time() - t0, 1)]
        bl = bodies(X)
        st['t'].append(round(time.time() - t0, 1))
        vv = {}
        for b in bl:
            vv[b.entityToken] = b.volume
            VV[b.name] = vv[b.entityToken]
        bs = sorted(bl, key=lambda b: vv[b.entityToken])
        st['t'].append(round(time.time() - t0, 1))
        st['bodies'] = len(bs)
        res = c.setdefault('j6a', {}); dd = c.setdefault('j6a_d', {}); tm = c.setdefault('j6a_t', {})
        left = 0; fails = []; nxt = []
        # names, boxes and volumes are read once a call: the double loop below makes 4 753 pairs, and a big body's volume costs up to
        #   a second per read (lesson 135)
        nm = [b.name for b in bs]
        bx = []
        for b in bs:
            bb = b.boundingBox
            bx.append((bb.minPoint.x, bb.minPoint.y, bb.minPoint.z, bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z))
        for i, a in enumerate(bs):
            for j0 in range(i + 1, len(bs)):
                b = bs[j0]
                k = nm[i] + '|' + nm[j0]
                if k in res:
                    continue
                p = bx[i]; q = bx[j0]
                if p[0] > q[3] or q[0] > p[3] or p[1] > q[4] or q[1] > p[4] or p[2] > q[5] or q[2] > p[5]:
                    res[k] = 0.0; continue
                if time.time() - t0 > BUDGET:
                    left += 1
                    if len(nxt) < 8:
                        nxt.append(k)
                    continue
                tp = time.time()
                try:
                    if b.name in BIG:
                        if k not in dd:
                            dd[k] = round(dist(X, a, b), 4)
                        if dd[k] > 0.0005:
                            res[k] = 0.0; tm[k] = round(time.time() - tp, 1); continue
                        ax, rng, cen, sz = slabs(b)
                        if a.name in BIG:
                            ax2, rng2, cen2, sz2 = slabs(a)
                            parts = []
                            ok = True
                            for j in range(NT):
                                tj = tile(X, c, a, j, t0)
                                if tj is None:
                                    ok = False; break
                                parts.append(tj)
                        else:
                            parts = [tcopy(X, a.name)]; ok = True
                        v = 0.0
                        if ok:
                            for sm in parts:
                                if sm.faces.count == 0:
                                    continue
                                for j in reach(sm, ax, rng):
                                    tj = tile(X, c, b, j, t0)
                                    if tj is None:
                                        ok = False; break
                                    if tj.faces.count == 0 or not sm.boundingBox.intersects(tj.boundingBox):
                                        continue
                                    t = X.cp(sm)
                                    X.tbm.booleanOperation(t, tj, BT.IntersectionBooleanType)
                                    v += X.vol(t)
                                if not ok:
                                    break
                        if not ok:
                            left += 1
                            if len(nxt) < 8:
                                nxt.append(k)
                            continue
                        res[k] = round(v, 2)
                    else:
                        t = X.cp(tcopy(X, a.name))
                        X.tbm.booleanOperation(t, tcopy(X, b.name), BT.IntersectionBooleanType)
                        res[k] = round(X.vol(t), 2)
                except Exception:
                    res[k] = -1.0; fails.append([k, traceback.format_exc().splitlines()[-1]])
                tm[k] = round(time.time() - tp, 1)
        st['t'].append(round(time.time() - t0, 1))
        st['pairs done'] = len(res); st['left'] = left; st['failed'] = fails
        st['t'].append(round(time.time() - t0, 1))
        st['next'] = nxt; st['slowest'] = sorted(tm.items(), key=lambda kv: -kv[1])[:10]
        tl = {}
        for b in bs:
            if b.name in BIG:
                have = [tvol(c, b, j) for j in range(NT)]
                tl[b.name] = [sum(1 for h in have if h is not None), round(sum(h for h in have if h is not None), 1), round(vv[b.entityToken] * 1000.0, 1)]
        st['slabs (made, their mm3, the body mm3)'] = tl
        st['t'].append(round(time.time() - t0, 1))
        st['not zero'] = {k: v for k, v in sorted(res.items()) if abs(v) > 0.005}
        st['touching, 0 mm3'] = sorted(k for k, d in dd.items() if d <= 0.0005 and abs(res.get(k, 1.0)) <= 0.005)
        st['names'] = nm
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j6a', st)


run(None)
