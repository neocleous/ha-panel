# rev F audit-response d4e (2026-11-06): finding 32 done the printable way. d4c lengthened the four door bosses 0.3 to z 2.5,
#   but the door prints standing on its bottom edge (B6o: "door +z", bed = the z 2.8 face): bosses 0.3 below that edge would
#   be the only bed contact and the whole edge would start in the air. So the bosses go back to z 2.8 and the floor gets
#   the 0.3 instead: Ø8 × 0.3 pads (z 2.5–2.8, round the Ø3.4 screw holes) on the front shell under the four bosses (the
#   front prints floor-down, the pads grow up from the floor). Boss-on-pad sets the door height; the bottom edge keeps its
#   0.3 reveal over the floor. Screw stack (ISO 7380 M3 × 8 from below): head on the c-bore floor z 1.0, floor + pad z 1.0–2.8,
#   Ruthex M3 flush at the boss face z 2.8–8.5 (5.7 engaged), tip z 9.0, hole bottom z 9.5.
#   HOUSING_F_door (d4c state -> HOUSING_F_door_d4c, hidden): Ø8.1 cut z 2.3–2.8 at the four bosses.
#   HOUSING_F_front (d4c state -> HOUSING_F_front_d4c, hidden): pads Ø8 z 2.4–2.8 minus Ø3.4.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_door': 51.2068, 'HOUSING_F_front': 236.1755}
COPIES = {'HOUSING_F_door': 'HOUSING_F_door_d4c', 'HOUSING_F_front': 'HOUSING_F_front_d4c'}
BOSSES = ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0))


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        for n in COPIES.values():
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        for k, n in COPIES.items():
            c = X.add(X.tbm.copy(X.body(k)), n); c.isLightBulbOn = False
        db = X.body('HOUSING_F_door'); fb = X.body('HOUSING_F_front')
        v0d, v0f = db.volume, fb.volume
        cut = None; pad = None
        for (x, y) in BOSSES:
            c = X.wcyl_z(XC + x, y, 4.05, 2.3, 2.8); cut = c if cut is None else X.union(cut, c)
            p = X.wcyl_z(XC + x, y, 4.0, 2.4, 2.8); X.diff(p, X.wcyl_z(XC + x, y, 1.7, 0.0, 3.0)); pad = p if pad is None else X.union(pad, p)
        X.combine(db, [X.add(cut, 'D4E_bosscut_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        X.combine(fb, [X.add(pad, 'D4E_pad_tmp')]); fb = X.body('HOUSING_F_front')
        out['door_cm3'] = [round(v0d, 4), round(db.volume, 4)]; out['door_lumps'] = db.lumps.count
        out['front_cm3'] = [round(v0f, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        pr = {}
        for (x, y) in BOSSES:
            pr['%g,%g' % (x, y)] = {'boss_bottom_z2.8': not P(db, x + 3.0, y, 2.75) and P(db, x + 3.0, y, 2.85),
                                    'insert_hole_open': not P(db, x, y, 2.9) and not P(db, x, y, 9.4),
                                    'pad_z2.5-2.8': P(fb, x + 3.0, y, 2.65) and not P(fb, x + 3.0, y, 2.85) and not P(fb, x + 4.2, y, 2.65),
                                    'screw_hole_open': not P(fb, x, y, 2.65) and not P(fb, x, y, 1.5)}
        out['probes'] = pr
        out['all_probes_ok'] = all(all(v.values()) for v in pr.values())
        out['door_lowest_z'] = round(wbb(X, db)[4], 3)
        out['door_x_front_mm3'] = vol_x(X, X.tbm.copy(db), X.tbm.copy(fb))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['split'] = [b.name for b in X.comp.bRepBodies if ' (' in b.name and b.name.startswith(('HOUSING', 'GROMMET', 'CRADLE'))]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d4e_boss_pads', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
