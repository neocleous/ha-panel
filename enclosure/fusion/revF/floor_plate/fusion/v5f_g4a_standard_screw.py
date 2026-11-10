# rev F g4a (2026-11-10): step 1, block 4 - the standard screw (Daniel 22:23: 1a, 2a, 3a). ISO 7380-1 M3 x 8, Ruthex M3 x 5.7, 2.0 key.
#   FLOOR_PLATE: the two cradle posts 5.0 taller (dia 8, top z 13.0), solid below the new insert hole dia 4.0 x 6.7 (z 6.3..13.0).
#   CRADLE_5807: legs cut at z 13.0 (were z 8.0..); the counterbore's seat stays at z 16.0 -> 3.0 clamped.
#   SPKBOX_L / _R: the eight driver pilots opened to dia 4.0 x 6.7 from the box face (y -3.0..-9.7); the inboard upper boss behind the
#     face (x +-52.75, z 45.75) from dia 7.0 to dia 7.5 over y -11.5..-6.0, solid behind the hole.
#   HOUSING_F_front: the four unused dia 2.5 pilots of the old box screws behind the inboard head pockets (y 2.0..5.0) filled.
# Dry by default; APPLY=True deletes the AUD_* tool templates, hides the old bodies as <name>_v45 and adds the new ones.
# PART: 'small' (plate, cradle, boxes) or 'shell'. Touch clips, cap and rim: no change.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False); PART = globals().get('PART', 'small')
GUARD = {'FLOOR_PLATE': 32988.7, 'CRADLE_5807': 2189.8, 'SPKBOX_L': 26181.9, 'SPKBOX_R': 25786.5, 'HOUSING_F_front': 201703.2}
CRA = [(6.5, -72.5), (-1.5, -72.5)]
XI, XO, ZL, ZU = 52.75, 88.25, 10.25, 45.75


def run(_context):
    st = {'apply': APPLY, 'part': PART}
    t0 = time.time()
    name = 'g4a_%s_%s' % (PART, 'apply' if APPLY else 'dry')
    try:
        X = K()
        nm = X.names()
        st['doc'] = X.doc.name
        try:
            st['version'] = X.doc.dataFile.versionNumber
        except Exception:
            st['version'] = None
        st['AUD'] = len([n for n in nm if n.startswith('AUD_')]); st['tmp'] = [n for n in nm if n.startswith('RENDER_tmp_')]
        todo = ['FLOOR_PLATE', 'CRADLE_5807', 'SPKBOX_L', 'SPKBOX_R'] if PART == 'small' else ['HOUSING_F_front']
        for n in todo:
            if n + '_v45' in nm:
                raise RuntimeError('%s_v45 exists: already applied' % n)
            v = X.vol(X.body(n))
            if abs(v - GUARD[n]) > 0.3:
                raise RuntimeError('guard %s %.1f (expected %.1f)' % (n, v, GUARD[n]))
        if st['tmp']:
            raise RuntimeError('temporary render bodies present')

        def frac(body, tool):
            full = X.vol(tool); t = X.cp(tool)
            X.tbm.booleanOperation(t, body, BT.IntersectionBooleanType)
            return round(X.vol(t) / full, 3)

        def tube(x, z, y0, y1, ri, ro):
            t = X.cyly(x, z, ro, y0, y1); X.dif(t, X.cyly(x, z, ri, y0 - 0.1, y1 + 0.1)); return t

        new = {}
        if PART == 'small':
            # ---- plate ----
            old = X.body('FLOOR_PLATE'); p = X.cp(old)
            for (x, y) in CRA:
                X.uni(p, X.cylz(x, y, 4.0, 2.0, 13.0))
            for (x, y) in CRA:
                X.dif(p, X.cylz(x, y, 2.0, 6.3, 13.6))
            add = X.cp(p); X.dif(add, X.cp(old))
            st['plate'] = {'vol': [round(X.vol(old), 1), round(X.vol(p), 1)], 'lumps': p.lumps.count, 'added': X.lumps(add, 3000)}
            new['FLOOR_PLATE'] = (old, p)
            # ---- cradle ----
            oc = X.body('CRADLE_5807'); c = X.cp(oc)
            cut = X.wbox(-30, 30, -95, -55, 7.0, 13.0)
            rem = X.cp(oc); X.sec(rem, X.cp(cut))
            st['cradle'] = {'removed': X.lumps(rem, 3000), 'legs expected mm3': round(2 * math.pi * (16.0 - 1.7 ** 2) * 5.0, 2)}
            X.dif(c, cut)
            st['cradle']['vol'] = [round(X.vol(oc), 1), round(X.vol(c), 1)]; st['cradle']['lumps'] = c.lumps.count
            st['cradle']['bottom'] = X.lumps(X.cp(c), 20000)[0][1]
            st['cradle']['in new plate'] = round(X.clash(c, p), 3)
            new['CRADLE_5807'] = (oc, c)
            status(name, st)
            # ---- boxes ----
            for side, sg in (('L', 1.0), ('R', -1.0)):
                ob = X.body('SPKBOX_' + side); b = X.cp(ob); log = {}
                v1 = X.vol(b)
                X.uni(b, X.cyly(sg * XI, ZU, 3.75, -11.5, -6.0)); log['boss'] = round(X.vol(b) - v1, 2); v1 = X.vol(b)
                for x in (XI, XO):
                    for z in (ZL, ZU):
                        X.dif(b, X.cyly(sg * x, z, 2.0, -9.7, -2.9))
                log['holes'] = round(X.vol(b) - v1, 2)
                log['vol'] = [round(X.vol(ob), 1), round(X.vol(b), 1)]; log['lumps'] = b.lumps.count
                chk = {}
                for x in (XI, XO):
                    for z in (ZL, ZU):
                        chk['%g/%g' % (sg * x, z)] = [frac(b, X.cyly(sg * x, z, 1.95, -9.65, -3.05)), frac(b, tube(sg * x, z, -9.7, -3.0, 2.0, 3.6)),
                                                      frac(b, X.cyly(sg * x, z, 2.0, -11.4, -10.6)), frac(b, X.cyly(sg * x, z, 2.0, -10.6, -9.75))]
                log['holes: core, wall 1.6, solid 0.9-1.7 behind, solid 0-0.9 behind'] = chk
                addb = X.cp(b); X.dif(addb, X.cp(ob)); log['added'] = X.lumps(addb, 3000)
                spk = X.body('SPK_' + side)
                log['driver envelope in box before / after'] = [round(X.clash(ob, spk), 2), round(X.clash(b, spk), 2)]
                st[side] = log; new['SPKBOX_' + side] = (ob, b)
                status(name, st)
        else:
            of = X.body('HOUSING_F_front'); f = X.cp(of)
            st['t_copy'] = round(time.time() - t0, 1)
            pre = {}
            for sg in (1.0, -1.0):
                for z in (ZL, ZU):
                    pre['%g/%g' % (sg * XI, z)] = [frac(of, X.cyly(sg * XI, z, 1.2, 2.05, 4.95)), frac(of, tube(sg * XI, z, 2.05, 5.1, 1.25, 1.35)),
                                                   frac(of, X.cyly(sg * XI, z, 1.35, 5.0, 5.1)), frac(of, X.cyly(sg * XI, z, 1.35, 5.1, 6.0))]
            st['before: hole core, ring to r 1.35, 0.1 behind, 0.9 beyond'] = pre
            for sg in (1.0, -1.0):
                for z in (ZL, ZU):
                    X.uni(f, X.cyly(sg * XI, z, 1.35, 2.0, 5.1))
            addf = X.cp(f); X.dif(addf, X.cp(of))
            st['shell'] = {'vol': [round(X.vol(of), 1), round(X.vol(f), 1)], 'lumps': f.lumps.count, 'added': X.lumps(addf, 3000)}
            post = {}
            for sg in (1.0, -1.0):
                for z in (ZL, ZU):
                    post['%g/%g' % (sg * XI, z)] = [frac(f, X.cyly(sg * XI, z, 1.2, 2.05, 4.95)), frac(f, X.cyly(sg * XI, z, 4.1, 1.0, 1.95))]
            st['after: hole core solid, pocket in front still empty (0)'] = post
            new['HOUSING_F_front'] = (of, f)
            status(name, st)
        if APPLY:
            n_aud = 0
            for b in [b for b in X.root.bRepBodies if b.name.startswith('AUD_')]:
                b.deleteMe(); n_aud += 1
            st['AUD deleted'] = n_aud
            for n, (old, tb) in new.items():
                X.retire(old, '_v45')
                nb = X.add(tb, n, like=old, show=True)
                st.setdefault('applied', {})[n] = [round(X.vol(nb), 1), nb.lumps.count, nb.isLightBulbOn]
            st['dups'] = X.dups(); st['n_bodies'] = len(X.names())
            st['AUD left'] = [n for n in X.names() if n.startswith('AUD_')]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status(name, st)


run(None)
