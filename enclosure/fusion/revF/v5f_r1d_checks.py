# rev F rework R1d (2026-11-04), read-only (TemporaryBRep only): checks for the rear-door block.
# 1. interference of HOUSING_F_front / HOUSING_F_door / PD_5807_env with every component envelope (bbox-prefiltered).
# 2. door removal: the door copy moved straight back (-y) 1, 3, 10, 30, 80 mm -> intersection with the front and the 5807.
# 3. joint scans (x intervals of front / door) at z 25, 95, 140 on both sides at y -55.15 (gap) and -57.0 (lap).
# 4. magnet pockets: door pocket open 1.5 outside the door's inner surface, 0.4 skin solid; lip pocket open 1.2 inside,
#    pad solid 0.3 inside; pocket rims clear of the door's front edge (y -55.3).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MAG = [(25.0, -59.0), (60.0, -59.0), (95.0, -59.0), (132.0, -58.0), (150.0, -56.5)]


def segs(f, a, b, st):
    out = []; cur = None; v = a
    while v <= b + 1e-9:
        s = f(v)
        if s and cur is None: cur = v
        if not s and cur is not None: out.append([round(cur, 2), round(v - st, 2)]); cur = None
        v += st
    if cur is not None: out.append([round(cur, 2), round(b, 2)])
    return out


def overlap(a, b):
    A = a.boundingBox; Bb = b.boundingBox
    return not (A.maxPoint.x < Bb.minPoint.x or Bb.maxPoint.x < A.minPoint.x or A.maxPoint.y < Bb.minPoint.y or
                Bb.maxPoint.y < A.minPoint.y or A.maxPoint.z < Bb.minPoint.z or Bb.maxPoint.z < A.minPoint.z)


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door'); pe = X.body('PD_5807_env'); ie = X.body('INNER_E')
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'GPIO_plugA_env', 'GPIO_plugB_env', 'SPK_L', 'SPK_R', 'TOUCH_PCB',
                 'KO_touch_back', 'SLAB_frame', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'KO_5807_pigtail']
        comps += [n for n in names if n.startswith('LCD_')]
        res = {}; checked = 0
        for tgt in (fb, db, pe):
            r = {}
            for n in comps + (['KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR'] if tgt is fb else []):
                o = X.body(n)
                if o is None or not overlap(tgt, o):
                    continue
                checked += 1
                v = X.interference(tgt, [o])[n]
                if v > 0:
                    r[n] = v
            res[tgt.name] = r or 'all 0'
        out['interference_nonzero'] = res; out['pairs_checked'] = checked
        log('v5f_r1d_checks', 'interference', out)
        sweep = {}
        for d in (1.0, 3.0, 10.0, 30.0, 80.0):
            t = X.tbm.copy(db)
            m = adsk.core.Matrix3D.create(); m.translation = V3(0, -d * C / 10, d * S / 10)   # world -y by d
            X.tbm.transform(t, m)
            a = X.tbm.copy(t); X.tbm.booleanOperation(a, X.tbm.copy(fb), B.IntersectionBooleanType)
            b = X.tbm.copy(t); X.tbm.booleanOperation(b, X.tbm.copy(pe), B.IntersectionBooleanType)
            sweep[d] = {'vs_front_mm3': round(a.volume * 1000, 3), 'vs_5807_mm3': round(b.volume * 1000, 3)}
        out['door_removal_sweep'] = sweep
        log('v5f_r1d_checks', 'sweep', sweep)
        sc = {}
        for z, x0, x1 in ((25.0, 68.0, 84.0), (95.0, 52.0, 72.0), (140.0, 30.0, 52.0)):
            for s in (1, -1):
                for y in (-55.15, -57.0):
                    sc['%+d,z%g,y%g' % (s, z, y)] = {'front': segs(lambda x: X.inside(fb, XC + s * x, y, z), x0, x1, 0.1),
                                                    'door': segs(lambda x: X.inside(db, XC + s * x, y, z), x0, x1, 0.1)}
        out['joint_scans'] = sc
        mags = {}
        for s in (1, -1):
            for (zm, ym) in MAG:
                a, c = 0.0, 110.0
                for _ in range(26):
                    m = (a + c) / 2
                    if X.inside(ie, XC + s * m, ym, zm): a = m
                    else: c = m
                p = Dw(XC + s * a, ym, zm)
                fl = X.comp.findBRepUsingPoint(p, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, 0.005, False)
                face = [fl.item(i) for i in range(fl.count) if fl.item(i).body.name == 'INNER_E'][0]
                ok, n = face.evaluator.getNormalAtPoint(p); n.normalize()
                q = lambda k: P3(p.x + n.x * k / 10, p.y + n.y * k / 10, p.z + n.z * k / 10)
                ins = lambda b, pt: b.pointContainment(pt) in INS
                mags['%+d,%g' % (s, zm)] = {'door_pocket_open': not ins(db, q(1.6)), 'door_skin': ins(db, q(0.45)),
                                           'lip_pocket_open': not ins(fb, q(-1.2)), 'lip_pad_skin': ins(fb, q(-0.35)),
                                           'lap_gap_open': not ins(fb, q(-0.1)) and not ins(db, q(-0.1))}
        out['magnets'] = mags
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1d_checks', 'rear door checks', out)
    print(json.dumps(out))
