# rev F d17a (2026-11-06), read-only: Daniel 21:00 – crank the main-board bracket's right column so a finger goes straight in
#   to the microSD. Right bracket lump: extents per height; the floor round the old foot (−49.5, −58.0) and the new spot
#   (−65.5, −57.5): solid, voids, top / bottom z; the shell's inner face and the door's inner face round the new foot / leg /
#   knee (rays). Writes ~/Documents/HA_panel_renders/d_data/data/d17a_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d17a_probe.json')
GUARD = {'HOUSING_F_front': 235.2273, 'SPKBOX_R': 26.3874}
ZS = [2.6, 3.0, 5.0, 8.0, 8.7, 9.6, 10.5, 11.2, 12.0, 15.0, 20.0, 25.0, 30.0, 34.0, 37.5, 41.0, 45.0, 60.0, 76.0, 80.5, 84.0]


def lumps_bb(X, t):
    return [[round(l.volume * 1000, 2)] + [round(c, 2) for c in wbb(X, X.tbm.copy(l))] for l in t.lumps]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s' % (k, None if b is None else round(b.volume, 4)))
        br = X.body('MAIN_BRACKET')
        out['bracket'] = {'cm3': round(br.volume, 4), 'lumps': lumps_bb(X, X.tbm.copy(br))}
        R = tb_copy(X, 'MAIN_BRACKET'); inter(X, R, wbox_rel(X, [-80.0, 0.0, -80.0, -40.0, 0.0, 100.0]))
        out['right'] = {'mm3': round(R.volume * 1000, 2), 'bb': [round(c, 2) for c in wbb(X, R)]}
        sl = {}
        for z in ZS:
            q = X.tbm.copy(R); inter(X, q, wbox_rel(X, [-80.0, 0.0, -80.0, -40.0, z - 0.05, z + 0.05]))
            sl['z%g' % z] = lumps_bb(X, q) if q.volume > 0 else []
        out['right_slices'] = sl
        fr = tb_copy(X, 'HOUSING_F_front')
        fl = {}
        for tag, bb in (('old', [-54.5, -44.5, -63.0, -53.0, -0.5, 3.2]), ('new', [-71.0, -60.0, -63.0, -52.5, -0.5, 3.2])):
            box = wbox_rel(X, bb)
            s_ = X.tbm.copy(fr); inter(X, s_, X.tbm.copy(box))
            v_ = X.tbm.copy(box); X.diff(v_, X.tbm.copy(fr))
            fl[tag] = {'solid_mm3': round(s_.volume * 1000, 2), 'solid_bb': [round(c, 2) for c in wbb(X, s_)] if s_.volume > 0 else None,
                       'void_lumps': lumps_bb(X, v_) if v_.volume > 0 else []}
        out['floor'] = fl
        frc = X.tbm.copy(fr); inter(X, frc, wbox_rel(X, [-90.0, -40.0, -70.0, -50.0, -1.0, 32.0]))    # cropped once: fast bars
        drc = tb_copy(X, 'HOUSING_F_door'); inter(X, drc, wbox_rel(X, [-90.0, -40.0, -80.0, -50.0, -1.0, 32.0]))

        def bar_hit(t, bb, axis, side):              # extreme coordinate of t inside a thin bar (side 1: max, 0: min)
            q = X.tbm.copy(t); inter(X, q, wbox_rel(X, bb))
            if q.volume <= 0:
                return None
            w = wbb(X, q); return round(w[2 * axis + side], 2)
        rz = {}
        for (x, y) in ((-49.5, -58.0), (-65.5, -57.5), (-65.5, -61.0), (-62.0, -54.5), (-69.0, -57.5), (-55.0, -45.0)):
            rz['%g_%g' % (x, y)] = [bar_hit(frc, [x - 0.05, x + 0.05, y - 0.05, y + 0.05, -1.0, 6.0], 2, 0),
                                    bar_hit(frc, [x - 0.05, x + 0.05, y - 0.05, y + 0.05, -1.0, 6.0], 2, 1)]
        out['floor_z_min_max'] = rz
        wall = {}
        for y in (-63.0, -62.5, -61.5, -60.5, -59.5, -58.5, -57.5, -56.5, -55.5, -54.5, -53.5):
            row = []
            for z in (4.0, 6.0, 8.0, 11.0, 15.0, 18.0, 21.0, 24.0, 27.0, 30.0):
                row.append([z, bar_hit(frc, [-90.0, -55.0, y - 0.05, y + 0.05, z - 0.05, z + 0.05], 0, 1)])
            wall['y%g' % y] = row
        out['shell_inner_x_max'] = wall
        door = {}
        for x in (-70.0, -68.0, -66.0, -64.0, -62.0, -60.0):
            row = []
            for z in (3.0, 6.0, 12.0, 20.0, 26.0):
                row.append([z, bar_hit(drc, [x - 0.05, x + 0.05, -80.0, -50.0, z - 0.05, z + 0.05], 1, 1)])
            door['x%g' % x] = row
        out['door_inner_y_max'] = door
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d17a_bracket_probe', 'probe', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
