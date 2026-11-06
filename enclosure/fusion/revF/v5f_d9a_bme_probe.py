# rev F d9a (2026-11-06), read-only: inputs for the BME680 pocket (audit finding 37, Daniel's decision 1 b: build to the
#   20 x 15 x 6 placeholder). Writes ~/Documents/HA_panel_renders/d_data/data/d9a_probe.json: bodies near the envelope,
#   the slot tool's faces, the wall along the envelope's normal on a grid (wall surface and thickness), the lip and door
#   near the envelope, and sections in the envelope's frame (planes along t and along u).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d9a_probe.json')
CE = (-73.44, -42.106, 91.325)                     # envelope centre (x_rel, y, z)
NO = (-0.751, -0.643, 0.15)                        # outward wall normal
TT = (0.6504, -0.7596, 0.0)                        # along the 20
UU = (0.1139, 0.0976, 0.9887)                      # along the 15 (up the wall)
WIN = [-100.0, -45.0, -70.0, -20.0, 60.0, 125.0]


def at(a, b, c):
    return tuple(CE[i] + a * TT[i] + b * UU[i] + c * NO[i] for i in range(3))


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        near = {}
        for b in X.comp.bRepBodies:
            if not (b.isLightBulbOn or b.name.endswith('_env') or b.name.startswith(('LEAD_', 'KO_', 'TOOL_bme'))):
                continue
            try:
                bb = wbb(X, b)
            except Exception:
                continue
            if bb[0] < WIN[1] and bb[1] > WIN[0] and bb[2] < WIN[3] and bb[3] > WIN[2] and bb[4] < WIN[5] and bb[5] > WIN[4]:
                near[b.name] = {'bb': [round(v, 2) for v in bb], 'vis': b.isLightBulbOn, 'cm3': round(b.volume, 4)}
        out['near'] = near
        for n in ('TOOL_bme680_slots', 'BME680_env'):
            b = X.body(n)
            if b is not None:
                fs = []
                for f in b.faces:
                    c = f.centroid; ok, nn = f.evaluator.getNormalAtPoint(f.pointOnFace)
                    fs.append([round(f.area * 100, 2), [round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2)],
                               [round(v, 3) for v in nw_of(nn)]])
                out['faces_' + n] = fs
        # wall along the outward normal on a grid in the envelope's (t, u) plane: entry / exit of the front shell
        names = ('HOUSING_F_front',)
        grid = {}
        for a in (-16.0, -12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0, 16.0):
            for b_ in (-12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0, 16.0):
                o = at(a, b_, -6.0)
                runs = solid_runs(X, (XC + o[0], o[1], o[2]), NO, 'HOUSING_F_front', 16.0)
                grid['%g,%g' % (a, b_)] = runs
        out['wall_runs_from_n-6'] = grid
        # the lip and the door along the same normal near the envelope's rear end
        lip = {}
        for a in (8.0, 10.0, 12.0, 14.0, 16.0, 18.0):
            for b_ in (-8.0, 0.0, 8.0):
                o = at(a, b_, -6.0)
                lip['%g,%g' % (a, b_)] = {'front': solid_runs(X, (XC + o[0], o[1], o[2]), NO, 'HOUSING_F_front', 16.0),
                                          'door': solid_runs(X, (XC + o[0], o[1], o[2]), NO, 'HOUSING_F_door', 16.0)}
        out['rear_runs'] = lip
        NB = ['HOUSING_F_front', 'HOUSING_F_door', 'BME680_env', 'TOOL_bme680_slots', 'LEAD_BME680', 'SPKBOX_R', 'MAIN_BRACKET',
              'LD2410C_env_F', 'SLAB_frame']
        PL = {
            'B_z91.3': ('z', 91.3, (-95.0, -50.0, -70.0, -20.0), NB),
            'B_z86': ('z', 86.0, (-95.0, -50.0, -70.0, -20.0), NB),
            'B_z97': ('z', 97.0, (-95.0, -50.0, -70.0, -20.0), NB),
            'B_z103': ('z', 103.0, (-95.0, -50.0, -70.0, -20.0), NB),
            'B_y-42': ('y', -42.1, (-95.0, -50.0, 70.0, 115.0), NB),
            'B_y-50': ('y', -50.0, (-95.0, -50.0, 70.0, 115.0), NB),
            'B_y-54': ('y', -54.0, (-95.0, -50.0, 70.0, 115.0), NB),
            'B_x-73': ('x', -73.4, (-70.0, -20.0, 70.0, 115.0), NB),
        }
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: v for k, v in out.items() if k not in ('sec', 'wall_runs_from_n-6', 'rear_runs', 'near', 'faces_TOOL_bme680_slots', 'faces_BME680_env')}
    log('v5f_d9a_bme_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
