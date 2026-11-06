# rev F d10c (2026-11-06): square end on the lip (audit finding 4, Daniel's decision 2 a: feather edges do not print well).
#   The lip's end is the plane y -63.5, which meets the leaning band at 17° (top) to 38° (sides): the inner face runs on past
#   the outer face's end by delta = 1.5 (sides) … 4.0 (top) and tapers to a knife edge. At every d10b station along the outer
#   face's end edge (~1 mm apart; the K5 notch edges excluded) a box cuts away the band beyond the plane through that edge and
#   the band's normal: the end becomes a 1.2 face square to the band, the outer face (the lap surface) keeps its full length,
#   only the inner face's overhang goes. Removal only, so the door's slide-off path cannot gain an interference.
#   HOUSING_F_front changed in place (old -> HOUSING_F_front_d10, hidden).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FR = 'HOUSING_F_front'
EXPECT = {FR: 235.8575}
STF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d10b_stations.json')


def unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


def tree_union(X, parts):
    while len(parts) > 1:
        nxt = []
        for i in range(0, len(parts) - 1, 2):
            nxt.append(X.union(parts[i], parts[i + 1]))
        if len(parts) % 2:
            nxt.append(parts[-1])
        parts = nxt
    return parts[0]


def knife_count(X, body, ymax=-61.0):
    n = 0; worst = 180.0; where = None
    for e in body.edges:
        if wy(e.startVertex.geometry) > ymax or wy(e.endVertex.geometry) > ymax:
            continue
        p = e.pointOnEdge
        fs = list(e.faces)
        if len(fs) != 2:
            continue
        ok1, n1 = fs[0].evaluator.getNormalAtPoint(p); ok2, n2 = fs[1].evaluator.getNormalAtPoint(p)
        a = math.degrees(math.acos(max(-1.0, min(1.0, n1.dotProduct(n2)))))
        dih = 180.0 - a                              # dihedral of a convex edge
        if dih < worst:
            worst = dih; where = [round(p.x * 10 - XC, 2), round(wy(p), 2), round(wz(p), 2)]
        if dih < 30.0:
            n += 1
    return n, round(worst, 1), where


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        fb = X.body(FR)
        if abs(fb.volume - EXPECT[FR]) > 0.0005:
            raise RuntimeError('guard: front %s' % round(fb.volume, 4))
        if X.body('HOUSING_F_front_d10') is not None:
            raise RuntimeError('HOUSING_F_front_d10 exists already')
        st = json.load(open(STF))['stations']
        boxes = []; used = 0
        for s in st:
            q = s[0:3]; tau = unit(s[3:6]); n = unit(s[6:9]); ex = unit(s[9:12]); dl = s[12]
            if n[1] > -0.5 or dl <= 0.05:
                continue
            nin = tuple(-c for c in n)
            k = sum(nin[i] * tau[i] for i in range(3)); nin = unit(tuple(nin[i] - k * tau[i] for i in range(3)))
            le = dl + 1.5
            c = tuple(q[i] + nin[i] * 0.6 + ex[i] * le / 2 for i in range(3))
            boxes.append(lbox(X, c, tau, nin, 1.4, 2.4, le)); used += 1
        out['stations_used'] = used
        CH = globals().get('CHUNK', 24)
        clip = X.wbox(-250, 250, -250, -58.0, 6.4, 260)
        tools = []
        for i in range(0, len(boxes), CH):
            t_ = tree_union(X, boxes[i:i + CH]); inter(X, t_, X.tbm.copy(clip)); tools.append(t_)
        out['chunks'] = len(tools); out['t_tools_s'] = round(time.time() - t0, 1)
        fcopy = tb_copy(X, FR); rem_v = 0.0
        for t_ in tools:
            r_ = X.tbm.copy(t_); inter(X, r_, X.tbm.copy(fcopy)); rem_v += r_.volume
        out['tool_mm3'] = round(sum(t_.volume for t_ in tools) * 1000, 1); out['removed_mm3_sum'] = round(rem_v * 1000, 1)
        out['knife_before'] = knife_count(X, fb)
        if not dry:
            c0 = X.add(tb_copy(X, FR), 'HOUSING_F_front_d10'); c0.isLightBulbOn = False
            v0 = fb.volume
            for j, t_ in enumerate(tools):
                X.combine(fb, [X.add(t_, 'D10C_tool_%d_tmp' % j)], op=CUT); fb = X.body(FR)
            out['front_cm3'] = [round(v0, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
            out['front_voids'] = sum(1 for li in range(fb.lumps.count) for si in range(fb.lumps.item(li).shells.count)
                                     if fb.lumps.item(li).shells.item(si).isVoid)
            out['knife_after'] = knife_count(X, fb)
            out['door_x_front'] = vol_x(X, tb_copy(X, 'HOUSING_F_door'), tb_copy(X, FR))
        out['dry'] = dry
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d10c_lip_square_end', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
