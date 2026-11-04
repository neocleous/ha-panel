# rev F rework R1c-1 (2026-11-04): extend the front shell's inner flange (lip) to 8 mm behind the joint and add the door's
# edge magnets (Daniel 2026-11-04 08:40: magnets).
# Why across the lap, not along y: behind the joint plane the back wall curves forward steeply (at z 140 the opening
# narrows from half-width 42.3 at y -55 to 23.1 at y -60), so y-axis magnet pairs have no room above z ~120. The lap
# (door wall over the lip, 0.2 apart) runs all round the arch, so the pairs sit across it, axis on the wall normal.
#   lip extension: (skin 1.4 - skin 0.2) ∩ (y -63.0...-58.0, z >= 6.5); upper-lane notches r 4.0 extended to y -63.5.
#   magnets D8 x 1.5 (N52), 5 per side at (z, y on the lap): (25, -59) (60, -59) (95, -59) (132, -58) (150, -56.5).
#   door pocket D8.3 from the outer surface in to 0.9 below the door's inner surface (magnet 1.5 + 0.1; 0.9 skin), closed
#     by the cloth (block 5); the pull draws the magnet into its pocket.
#   lip pad D12, 0.2...2.3 inside the door's inner surface (∩ INNER_E - skin 0.2); pocket D8.3 0.5...2.4 open to the cavity,
#     pull draws it into the pocket. Magnet faces 1.4 apart (0.9 + 0.2 + 0.3).
# D1 (block 5) moves the inner surface 0.7 inward under the cloth: re-run with D1 = 0.7 then (lip 0.9...2.1 etc.).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
D1 = 0.0
MAG = [(25.0, -59.0), (60.0, -59.0), (95.0, -59.0), (132.0, -58.0), (150.0, -56.5)]


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        ie = X.body('INNER_E'); fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        v0 = (fb.volume, db.volume)
        ext = X.tbm.copy(X.body('TOOL_inner_skin_1p4'))
        X.tbm.booleanOperation(ext, X.tbm.copy(X.body('TOOL_inner_skin_0p2')), B.DifferenceBooleanType)
        X.tbm.booleanOperation(ext, X.wbox(-150, 150, -63.0, -58.0, 6.5, 250), B.IntersectionBooleanType)
        out['lip_ext_cm3'] = round(ext.volume, 3)
        keep = X.tbm.copy(ie); X.tbm.booleanOperation(keep, X.tbm.copy(X.body('TOOL_inner_skin_0p2')), B.DifferenceBooleanType)
        pads = None; fcut = None; dcut = None; pts = {}
        for s in (1, -1):
            for (zm, ym) in MAG:
                a, c = 0.0, 110.0
                for _ in range(26):
                    m = (a + c) / 2
                    if X.inside(ie, XC + s * m, ym, zm): a = m
                    else: c = m
                p = Dw(XC + s * a, ym, zm)
                fl = X.comp.findBRepUsingPoint(p, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, 0.005, False)
                face = None
                for i in range(fl.count):
                    f = fl.item(i)
                    if f.body.name == 'INNER_E':
                        face = f; break
                if face is None:
                    raise RuntimeError('no INNER_E face at %s' % ((s, zm, ym),))
                ok, n = face.evaluator.getNormalAtPoint(p)
                n.normalize()
                q = lambda k: P3(p.x + n.x * k / 10, p.y + n.y * k / 10, p.z + n.z * k / 10)
                pts['%+d,%g' % (s, zm)] = {'x_rel': round(s * a, 2), 'n_world': (round(n.x, 3), round(n.y * C - n.z * S, 3), round(n.y * S + n.z * C, 3))}
                pad = X.tbm.createCylinderOrCone(q(0.0), 0.60, q(-(2.3 + D1)), 0.60)
                X.tbm.booleanOperation(pad, X.tbm.copy(keep), B.IntersectionBooleanType)
                pads = pad if pads is None else X.union(pads, pad)
                lp = X.tbm.createCylinderOrCone(q(-(0.5 + D1)), 0.415, q(-(2.4 + D1)), 0.415)
                fcut = lp if fcut is None else X.union(fcut, lp)
                dp = X.tbm.createCylinderOrCone(q(0.9 - D1), 0.415, q(3.2), 0.415)
                dcut = dp if dcut is None else X.union(dcut, dp)
        out['magnets'] = pts
        X.union(ext, pads)
        notch = None
        for xs in (47.5, -47.5):
            t = X.tbm.createCylinderOrCone(Dw(xs, -17.80, 146.23), 0.40, Dw(xs, -65.72, 110.12), 0.40)
            X.tbm.booleanOperation(t, X.wbox(-150, 150, -63.5, -53.4, 0, 250), B.IntersectionBooleanType)
            notch = t if notch is None else X.union(notch, t)
        X.diff(ext, notch); X.diff(ext, fcut)
        X.combine(fb, [X.add(ext, 'R1C_lip_tmp')])
        fb = X.body('HOUSING_F_front')
        X.combine(fb, [X.add(fcut, 'R1C_fcut_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        X.combine(db, [X.add(dcut, 'R1C_dcut_tmp')], op=CUT)
        db = X.body('HOUSING_F_door')
        out['cm3'] = {'front': (round(v0[0], 3), round(fb.volume, 3)), 'door': (round(v0[1], 3), round(db.volume, 3))}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        t = X.tbm.copy(fb); X.tbm.booleanOperation(t, X.tbm.copy(db), B.IntersectionBooleanType)
        out['front_x_door_mm3'] = round(t.volume * 1000, 3)
        out['front_vs_lanes'] = X.interference(fb, [X.body(n) for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')])
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1c1_lip_magnets', 'lip ext + magnets', out)
    print(json.dumps(out))
