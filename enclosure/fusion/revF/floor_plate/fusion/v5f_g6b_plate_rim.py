# rev F g6b (2026-11-10): base plate - the rim's top lowered so the cloth can be turned under the shell's and the door's bottom edges
# (Daniel 23:07, "the cloth wraps underneath" = option 1 of the proposal).
#   Band: 3.0 wide inward from the plate's top outline (the body's outline at z 2.4..2.5), all round, lowered from z 2.5 to z 1.8
#   (sides: in to x 91.3; chin: in to y 3.4; door: in to y -80.8 at the middle). Built as outline prism minus the prism moved 3.0 in
#   16 directions and intersected. Everything the plate carries above z 1.8 inside the band goes with it.
#   Chin rest pads shortened to y 1.9..3.3; the two small rest pads under the side walls near the back removed.
# Dry by default; APPLY=True hides the old plate as FLOOR_PLATE_v46 and adds the new one.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
BAND, ZLOW, CLOTH = 3.0, 1.8, 0.7


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    name = 'g6b_apply' if APPLY else 'g6b_dry'
    try:
        X = K()
        nm = X.names()
        if any(n.startswith(('AUD_', 'RENDER_tmp_')) for n in nm) or 'FLOOR_PLATE_v46' in nm:
            raise RuntimeError('state: templates present or already applied')
        P = X.body('FLOOR_PLATE')
        if abs(X.vol(P) - 33466.2) > 0.3:
            raise RuntimeError('guard FLOOR_PLATE %.1f' % X.vol(P))
        sl = X.cp(X.body('REF_F_outer')); X.sec(sl, X.wbox(-130, 130, -110, 40, 2.4, 2.5))
        st['outline slice mm2'] = round(X.vol(sl) / 0.1, 1)
        prism = None
        for k in range(-7, 6):
            t = X.cp(sl); X.move(t, 0, 0, 0.1 * k)
            prism = t if prism is None else X.uni(prism, t)
        X.sec(prism, X.wbox(-130, 130, -110, 40, ZLOW, 3.0))
        st['prism'] = [round(X.vol(prism), 1), prism.lumps.count]

        def erode(d):
            e = X.cp(prism)
            for k in range(16):
                a = math.pi / 8 * k
                t = X.cp(prism); X.move(t, d * math.cos(a), d * math.sin(a), 0.0)
                X.sec(e, t)
            return e

        band = X.cp(prism); X.dif(band, erode(BAND))
        st['band'] = [round(X.vol(band), 1), band.lumps.count]
        new = X.cp(P); X.dif(new, band)
        for sx in (1.0, -1.0):
            X.dif(new, X.wbox(sx * 7.0, sx * 19.0, 3.3, 4.6, 2.5, 3.0))
            X.dif(new, X.wbox(sx * 79.0, sx * 87.0, -54.0, -46.0, 2.5, 3.0))
        st['plate'] = {'vol': [round(X.vol(P), 1), round(X.vol(new), 1)], 'lumps': new.lumps.count}
        rem = X.cp(P); X.dif(rem, X.cp(new))
        st['removed'] = [round(X.vol(rem), 1), [[l[0], l[1]] for l in X.lumps(rem, 4000)[:12]]]
        status(name, st)
        # what the band took from the plate's features above z 2.5 (pads, posts)
        feat = X.cp(rem); X.sec(feat, X.wbox(-130, 130, -110, 40, 2.52, 3.0))
        st['removed above z 2.5'] = [[l[0], l[1]] for l in X.lumps(feat, 4000)[:12]]
        # the cloth zone: the outer 2.6 of the outline, where the cloth is turned under the shell's and the door's edge
        ring = X.cp(prism); X.dif(ring, erode(2.6))
        S = X.cp(X.body('HOUSING_F_front')); X.sec(S, X.wbox(-130, 130, -110, 40, 2.8, 3.3))
        D = X.cp(X.body('HOUSING_F_door')); X.sec(D, X.wbox(-130, 130, -110, 40, 2.8, 3.3))
        res = {}
        for nm_, E in (('shell', S), ('door', D)):
            for drop in (CLOTH + 0.25, 0.25):
                t = X.cp(E); X.move(t, 0, 0, -drop)
                ring_d = X.cp(ring); X.move(ring_d, 0, 0, 0.0)
                # edge material inside the cloth zone, lowered by 'drop', against the old and the new plate
                z0 = 2.8 - drop
                tz = X.cp(t); X.sec(tz, X.wbox(-130, 130, -110, 40, z0, z0 + 0.5))
                # restrict to the ring in plan: the ring spans z 1.8..3.0, the lowered edge z0..z0+0.5 lies inside that range
                X.sec(tz, X.cp(ring))
                res['%s edge in the cloth zone lowered %.2f: mm3 in old / new plate' % (nm_, drop)] = [round(X.clash(tz, P), 2), round(X.clash(tz, new), 2)]
        st['room under the edges'] = res
        # sections

        def runs(B, axis, a0, a1, c1, c2):
            if axis == 'x':
                n = X.wbox(a0, a1, c1 - 0.02, c1 + 0.02, c2 - 0.02, c2 + 0.02)
            else:
                n = X.wbox(c1 - 0.02, c1 + 0.02, a0, a1, c2 - 0.02, c2 + 0.02)
            X.tbm.booleanOperation(n, B, BT.IntersectionBooleanType)
            i = 0 if axis == 'x' else 2
            return sorted([[l[1][i], l[1][i + 1]] for l in X.lumps(n, 400) if l[1]])
        STN = {'chin centre (x 0, along y)': ('y', -4.0, 9.0, 0.0), 'chin at the rest pad (x 13, along y)': ('y', -4.0, 9.0, 13.0),
               'chin at the tongue (x 30, along y)': ('y', -4.0, 9.0, 30.0), 'side (y -30, along x)': ('x', 86.0, 98.0, -30.0),
               'side near the back (y -50, along x)': ('x', 78.0, 98.0, -50.0), 'back centre (x 0, along y)': ('y', -90.0, -74.0, 0.0),
               'back at x 40 (along y)': ('y', -90.0, -66.0, 40.0), 'back at the door screw (x -19, along y)': ('y', -90.0, -70.0, -19.0)}
        sec = {}
        for sn, (ax, a0, a1, c1) in STN.items():
            sec[sn] = {'z%g' % z: runs(new, ax, a0, a1, c1, z) for z in (1.5, 1.75, 2.0, 2.45, 2.65)}
        st['sections of the new plate'] = sec
        if APPLY:
            X.retire(P, '_v46')
            nb = X.add(new, 'FLOOR_PLATE', like=P, show=True)
            st['applied'] = [round(X.vol(nb), 1), nb.lumps.count, nb.isLightBulbOn]; st['dups'] = X.dups(); st['n_bodies'] = len(X.names())
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status(name, st)


run(None)
