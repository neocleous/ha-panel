# rev F block 2c (2026-11-03): Pi 5 moved 0.7 mm toward -x on the door (K10 "a cleaner placement that keeps the Pi on the
# door"). Why: the USB/RJ45 stacks reach x_rel 45.85 and the +x speaker frame starts at 47.5, so a 1.5 partition can't sit
# between them; the microSD reaches x_rel -44.15 on the other side. After the move: stacks 45.15 (+x partition cavity face
# 45.4 -> 0.25), microSD -44.85 (-x cavity face -45.3 -> 0.45), +x partition 45.4..46.9 -> 0.6 to the speaker frame.
# 1. PI5_F, PI5_F_cooler, KO_K7_fan, GPIO_plugA/B_env translated -0.7 in x (moveFeatures).
# 2. DOOR_F: old Pi bosses cut (r 3.9, z 2.5..8.1), old insert holes filled (r 2.05, z 0.8..2.5), intake field filled
#    (box z 0..2.5); new bosses (r 3.8 z 2.0..7.5 + land r 3.0 z 7.4..8.0), new insert holes (r 2.0 z 0.8..8.5) and the
#    10 x 10 intake field, all 0.7 toward -x.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
DX = -0.7
OLD = [(-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5)]
NEWH = [(x + DX, y) for (x, y) in OLD]
GRID_OLD = [(-16.1 + 3.0 * i, -36.7 + 3.0 * j) for i in range(10) for j in range(10)]
GRID_NEW = [(x + DX, y) for (x, y) in GRID_OLD]
MOVE = ['PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'GPIO_plugA_env', 'GPIO_plugB_env']


def run(_context):
    X = Ctx()
    out = {}
    try:
        coll = adsk.core.ObjectCollection.create()
        for n in MOVE:
            coll.add(X.body(n))
        bb0 = {n: round(X.body(n).boundingBox.minPoint.x * 10, 3) for n in MOVE}
        m = adsk.core.Matrix3D.create(); m.translation = V3(DX / 10, 0, 0)
        mf = X.feats.moveFeatures
        try:
            mi = mf.createInput2(coll); mi.defineAsFreeMove(m)
        except Exception:
            mi = mf.createInput(coll, m)
        mf.add(mi)
        out['moved_minx_world'] = {n: (bb0[n], round(X.body(n).boundingBox.minPoint.x * 10, 3)) for n in MOVE}
        door = X.body('DOOR_F')
        v0 = door.volume
        cut = None
        for (x, y) in OLD:
            c = X.wcyl_z(x, y, 3.9, 2.5, 8.1); cut = c if cut is None else X.union(cut, c)
        X.combine(door, [X.add(cut, 'DOOR_pi_old_cut_tmp')], op=CUT)
        fill = X.wbox(-18.1, 12.9, -38.7, -7.7, 0.0, 2.5)
        for (x, y) in OLD:
            X.union(fill, X.wcyl_z(x, y, 2.05, 0.8, 2.5))
        X.combine(X.body('DOOR_F'), [X.add(fill, 'DOOR_fill_tmp')])
        add = None
        for (x, y) in NEWH:
            a = X.wcyl_z(x, y, 3.8, 2.0, 7.5); X.union(a, X.wcyl_z(x, y, 3.0, 7.4, 8.0))
            add = a if add is None else X.union(add, a)
        addb = X.add(add, 'DOOR_pi_new_tmp')
        out['new_boss_interf'] = X.interference(addb, [X.body(n) for n in ('HOUSING_E', 'PI5_F', 'PI5_F_cooler')])
        X.combine(X.body('DOOR_F'), [addb])
        cut2 = None
        for (x, y) in NEWH:
            c = X.wcyl_z(x, y, 2.0, 0.8, 8.5); cut2 = c if cut2 is None else X.union(cut2, c)
        for (x, y) in GRID_NEW:
            X.union(cut2, X.wcyl_z(x, y, 1.0, -0.5, 3.0))
        X.combine(X.body('DOOR_F'), [X.add(cut2, 'DOOR_pi_cut_tmp')], op=CUT)
        door = X.body('DOOR_F')
        out['door_cm3'] = (round(v0, 3), round(door.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['probes'] = {
            'new_hole_open_z5': [not X.inside(door, x, y, 5.0) for (x, y) in NEWH],
            'new_boss_z7_r3.5': [X.inside(door, x + 3.5, y, 7.0) and X.inside(door, x - 3.5, y, 7.0) for (x, y) in NEWH],
            'new_floor_z0.4': [X.inside(door, x, y, 0.4) for (x, y) in NEWH],
            'old_boss_gone_z6_r3.7_far_side': [not X.inside(door, x + 3.75, y, 6.0) for (x, y) in OLD],
            'grid_open': sum(1 for (x, y) in GRID_NEW if not X.inside(door, x, y, 1.25)),
            'grid_bars_solid': sum(1 for (x, y) in GRID_NEW if X.inside(door, x + 1.5, y + 1.5, 1.25)),
            'old_grid_edge_col_filled': sum(1 for (x, y) in GRID_OLD if x > 10 and X.inside(door, x + 0.6, y, 1.25))}
        lcd = [b for b in X.comp.bRepBodies if b.name.startswith('LCD_')]
        res = {}
        for n in MOVE:
            r = X.interference(X.body(n), [door, X.body('HOUSING_E'), X.body('SLAB_frame')])
            res[n] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        out['interf_moved'] = res
        out['pi_extents_x_rel'] = (round(X.body('PI5_F').boundingBox.minPoint.x * 10 - XC, 2), round(X.body('PI5_F').boundingBox.maxPoint.x * 10 - XC, 2))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2c_pi_shift', 'Pi -0.7 x', out)
    print(json.dumps(out))
