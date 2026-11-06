# rev F d11a (2026-11-06), read-only: inputs for the microSD extender (audit finding 25, Daniel's decision 3 A: the watch
#   winder's flex extender). Writes ~/Documents/HA_panel_renders/d_data/data/d11a_probe.json: the card's protruding end on the
#   Pi, the right box near it, every body in the floor corner behind the box (where the socket holder can go), and
#   sections through the card, the box and the door.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d11a_probe.json')
WIN = [-100.0, -30.0, -95.0, 0.0, 0.0, 30.0]            # x_rel, y, z: right floor corner and the Pi's -x end


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        near = {}
        for b in X.comp.bRepBodies:
            if not b.isLightBulbOn and not b.name.endswith('_env') and not b.name.startswith(('LEAD_', 'KO_')):
                continue
            try:
                bb = wbb(X, b)
            except Exception:
                continue
            if bb[0] < WIN[1] and bb[1] > WIN[0] and bb[2] < WIN[3] and bb[3] > WIN[2] and bb[4] < WIN[5] and bb[5] > WIN[4]:
                near[b.name] = {'bb': [round(v, 2) for v in bb], 'vis': b.isLightBulbOn}
        out['near'] = near
        # the Pi's -x end: what sticks out past the PCB edge (card), and the PCB's own -x edge
        pi = X.body('PI5_F')
        q = X.tbm.copy(pi); inter(X, q, X.wbox(XC - 47.0, XC - 43.3, -62.0, 2.0, 3.0, 12.0))
        out['pi_beyond_-43.3'] = {'mm3': round(q.volume * 1000, 2), 'bb': [round(v, 2) for v in wbb(X, q)] if q.volume > 0 else None}
        q = X.tbm.copy(pi); inter(X, q, X.wbox(XC - 47.0, XC - 38.0, -62.0, 2.0, 3.0, 8.0))
        out['pi_below_pcb_x-47..-38'] = {'mm3': round(q.volume * 1000, 2), 'bb': [round(v, 2) for v in wbb(X, q)] if q.volume > 0 else None}
        q = X.tbm.copy(pi); inter(X, q, X.wbox(XC - 47.0, XC + 47.0, -62.0, 2.0, 3.0, 7.95))
        out['pi_below_z7.95'] = {'mm3': round(q.volume * 1000, 2), 'bb': [round(v, 2) for v in wbb(X, q)] if q.volume > 0 else None}
        # rays along +x at the card's height to find its end and the box wall
        rx = {}
        for y in (-45.0, -40.0, -35.0, -30.0, -25.0, -20.0, -15.0):
            for z in (6.5, 7.0, 7.5):
                hs = ray_hits(X, (XC - 60.0, y, z), (1, 0, 0), ('PI5_F', 'SPKBOX_R', 'HOUSING_F_front'))
                rx['%g,%g' % (y, z)] = [[round(h[2], 2), h[1]] for h in hs[:6]]
        out['rays_x'] = rx
        NB = ['PI5_F', 'PI5_F_cooler', 'SPKBOX_R', 'SPK_R', 'HOUSING_F_front', 'HOUSING_F_door', 'MAIN_BRACKET', 'LEAD_SPK_R',
              'CRADLE_5807', 'PIPWR_a_env', 'FOOT_RR', 'FOOT_FR']
        PL = {
            'S_z6.8': ('z', 6.8, (-95.0, -20.0, -92.0, 0.0), NB),
            'S_z3.0': ('z', 3.0, (-95.0, -20.0, -92.0, 0.0), NB),
            'S_z10': ('z', 10.0, (-95.0, -20.0, -92.0, 0.0), NB),
            'S_x-44': ('x', -44.0, (-92.0, 0.0, 0.0, 30.0), NB),
            'S_x-50': ('x', -50.0, (-92.0, 0.0, 0.0, 30.0), NB),
            'S_x-60': ('x', -60.0, (-92.0, 0.0, 0.0, 30.0), NB),
            'S_x-70': ('x', -70.0, (-92.0, 0.0, 0.0, 30.0), NB),
            'S_y-30': ('y', -30.0, (-95.0, -20.0, 0.0, 30.0), NB),
            'S_y-56': ('y', -56.0, (-95.0, -20.0, 0.0, 30.0), NB),
            'S_y-62': ('y', -62.0, (-95.0, -20.0, 0.0, 30.0), NB),
        }
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    short = {k: v for k, v in out.items() if k not in ('sec', 'rays_x', 'near')}
    log('v5f_d11a_sd_probe', 'probe', short)
    print(json.dumps(short, separators=(',', ':')))
