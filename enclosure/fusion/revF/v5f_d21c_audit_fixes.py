# rev F d21c (2026-11-07): the print audit's sub-millimetre options (report-print-audit-2026-11-07), sized for 0.20 mm layers.
#   F8 opt. 2: the front's four cap pads +0.1 (tops 172.5 -> 172.6) and the cap's four bosses -0.1 (ends 172.5 -> 172.6): the
#     contact moves onto a layer boundary of both prints (front from z 0, cap top face down from z 180), the cap's position is
#     unchanged; insert holes 6.0 -> 5.9 deep (Ruthex M3 5.7).
#   F10 opt. 2: the door's USB-C cutout top 27.9 -> 28.0 (door prints from z 2.8: 126 layers); grommet sleeve 0.1 -> 0.2.
#   F14 opt. 2: the LD2410C slot's roof 138.65 -> 138.85 (prints at 138.8): 0.30 over the board's top edge after rounding.
#   Each change is the B-rep face itself extruded by the step as a new tool body, then a TemporaryBRep union / cut of a copy;
#   old states -> *_d21 (hidden), tools deleted. DRY (default True) only finds the faces.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
EXP = {'HOUSING_F_front': 235.2269, 'HOUSING_F_cap': 9.9591, 'HOUSING_F_door': 47.2694}
AXES = [(-43.36, -32.85), (-25.91, -37.8), (25.91, -37.8), (43.36, -32.85)]


def wn(v):
    return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)


def wp(p):
    return (p.x * 10 - XC, wy(p), wz(p))


def fbox(f):                                                  # world box of a face from its vertices
    vs = [wp(v.geometry) for v in f.vertices]
    return [min(v[0] for v in vs), max(v[0] for v in vs), min(v[1] for v in vs), max(v[1] for v in vs),
            min(v[2] for v in vs), max(v[2] for v in vs)]


def planes(b, nz, z):                                         # planar faces with world normal (0, 0, nz) at height z
    res = []
    for f in b.faces:
        if f.geometry.objectType != adsk.core.Plane.classType():
            continue
        ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = wn(n)
        if abs(n[2] - nz) > 0.001:
            continue
        bb = fbox(f)
        if abs(bb[4] - z) < 0.002 and abs(bb[5] - z) < 0.002:
            res.append((f, bb, round(f.area * 100, 3)))
    return res


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True); tools = []
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
            if X.body(k + '_d21') is not None:
                raise RuntimeError(k + '_d21 exists already')
        fr_b, cap_b, door_b = X.body('HOUSING_F_front'), X.body('HOUSING_F_cap'), X.body('HOUSING_F_door')
        inb = lambda bb, x, y: bb[0] - 0.01 <= x <= bb[1] + 0.01 and bb[2] - 0.01 <= y <= bb[3] + 0.01
        pads = [p for p in planes(fr_b, 1.0, 172.5) if any(inb(p[1], x, y) for x, y in AXES)]
        bosses = [p for p in planes(cap_b, -1.0, 172.5) if abs(p[2] - 37.699) < 0.05]
        roof = [p for p in planes(fr_b, -1.0, 138.65) if abs(p[2] - 65.2) < 0.1 and p[1][0] > -77.0 and p[1][1] < -64.5]
        cut = [p for p in planes(door_b, -1.0, 27.9) if abs(p[1][0] + 12.2) < 0.01 and abs(p[1][1] - 12.2) < 0.01]
        out['faces'] = {'pads': [[a, [round(c, 2) for c in bb]] for f, bb, a in pads], 'bosses': [[a, [round(c, 2) for c in bb]] for f, bb, a in bosses],
                        'roof': [[a, [round(c, 2) for c in bb]] for f, bb, a in roof], 'cutout': [[a, [round(c, 2) for c in bb]] for f, bb, a in cut]}
        if len(pads) != 4 or len(bosses) != 4 or len(roof) != 1 or len(cut) != 1:
            raise RuntimeError('faces found: pads %d bosses %d roof %d cutout %d' % (len(pads), len(bosses), len(roof), len(cut)))
        exp_dv = {'front': sum(a for f, bb, a in pads) * 0.1 - roof[0][2] * 0.2, 'cap': -sum(a for f, bb, a in bosses) * 0.1,
                  'door': -cut[0][2] * 0.1}
        out['expected_dv_mm3'] = {k: round(v, 3) for k, v in exp_dv.items()}
        if not dry:
            ext = X.comp.features.extrudeFeatures

            def tool(f, d_mm, z_lo, z_hi):                     # the face extruded by d_mm; must land in [z_lo, z_hi]
                for sg in (1.0, -1.0):
                    inp = ext.createInput(f, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
                    inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(sg * d_mm / 10.0))
                    fe = ext.add(inp); t = fe.bodies.item(0); bb = wbb(X, X.tbm.copy(t))
                    if abs(bb[4] - z_lo) < 0.005 and abs(bb[5] - z_hi) < 0.005:
                        tools.append(t); return t
                    t.deleteMe()
                raise RuntimeError('tool on the wrong side for a face at %s' % [round(c, 2) for c in fbox(f)])
            fr = tb_copy(X, 'HOUSING_F_front'); cp = tb_copy(X, 'HOUSING_F_cap'); dr = tb_copy(X, 'HOUSING_F_door')
            v0 = {'front': fr.volume, 'cap': cp.volume, 'door': dr.volume}
            for f, bb, a in pads:
                X.union(fr, X.tbm.copy(tool(f, 0.1, 172.5, 172.6)))
            X.diff(fr, X.tbm.copy(tool(roof[0][0], 0.2, 138.65, 138.85)))
            for f, bb, a in bosses:
                X.diff(cp, X.tbm.copy(tool(f, 0.1, 172.5, 172.6)))
            X.diff(dr, X.tbm.copy(tool(cut[0][0], 0.1, 27.9, 28.0)))
            dv = {'front': (fr.volume - v0['front']) * 1000, 'cap': (cp.volume - v0['cap']) * 1000, 'door': (dr.volume - v0['door']) * 1000}
            out['dv_mm3'] = {k: round(v, 3) for k, v in dv.items()}
            for k in dv:
                if abs(dv[k] - exp_dv[k]) > 0.5:
                    raise RuntimeError('%s: volume change %.3f mm3, expected %.3f' % (k, dv[k], exp_dv[k]))
            res = {}
            for (old, tb) in (('HOUSING_F_front', fr), ('HOUSING_F_cap', cp), ('HOUSING_F_door', dr)):
                o = X.body(old); app = o.appearance; mat = o.material; vis = o.isLightBulbOn
                o.name = old + '_d21'; o.isLightBulbOn = False
                nb = X.add(tb, old)
                for attr, val in (('material', mat), ('appearance', app), ('isLightBulbOn', vis)):
                    try:
                        setattr(nb, attr, val)
                    except Exception:
                        pass
                res[old] = [round(nb.volume, 4), nb.lumps.count]
            out['applied'] = res
            for t in tools:
                t.deleteMe()
            tools = []
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            nf, nc, nd = X.body('HOUSING_F_front'), X.body('HOUSING_F_cap'), X.body('HOUSING_F_door')
            pr = {}
            for (x, y) in AXES:
                k = '%g,%g' % (x, y); xo = x + (4.75 if x < 0 else -4.75)    # a point on the pad's lobe, 4.75 from the axis
                pr['pad_' + k] = [I(nf, xo, y, 172.55), not I(nf, xo, y, 172.65)]
                pr['boss_' + k] = [I(nc, x + 3.0, y, 172.65), not I(nc, x + 3.0, y, 172.55), not I(nc, x, y, 173.0)]
            pr['roof'] = [not I(nf, -70.65, -23.1, 138.8), I(nf, -70.65, -23.1, 138.9), I(nf, -70.65, -23.1, 140.6)]
            pr['cutout'] = [not I(nd, 0.0, -82.3, 27.95), I(nd, 0.0, -82.3, 28.05), I(nd, 0.0, -82.3, 28.5)]
            out['probes'] = pr
            out['probes_ok'] = all(all(v) for v in pr.values())
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        for t in tools:
            try:
                t.deleteMe()
            except Exception:
                pass
    log('v5f_d21c_audit_fixes', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
