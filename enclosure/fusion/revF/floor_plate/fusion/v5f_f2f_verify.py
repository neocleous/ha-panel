# rev F f2f (2026-11-10): read-only checks after block 2.
#   A  interference: every changed or new body against every visible body (hidden backups, REF_/TOOL_/INNER/KO_/RENDER_ excluded)
#   B  lift-in: plate + boxes + drivers + screw heads + Pi + cooler + inlet cradle and board as one unit, 1.3 behind its place
#      (window 1.05..1.5), rising from 90 below to its height, then forward - against the shell and what is fixed to it (door off)
#   C  what is left of the old floor's features on the shell (z 2.8..12 inside the walls)
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
NEW = ['FLOOR_PLATE', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'DRV_screw_heads_env', 'RESP_CARRIER', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env',
       'MAIN_C7_env', 'MAIN_J2_plug_env', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env']
UNIT = ['FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env',
        'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
FIX = ['HOUSING_F_front', 'HOUSING_F_cap', 'SLAB_frame', 'TOUCH_PCB', 'RESP_CARRIER', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'RESP_pcb',
       'RESP_top_env', 'RESP_mic_env', 'LCD_pcb_76x110', 'LCD_components_env_d8.8']
SKIPP = ('REF_', 'TOOL_', 'INNER', 'KO_', 'RENDER_', 'LEAD_')
MODE = globals().get('MODE', 'ABC')


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        vis = [b for b in X.root.bRepBodies if b.isLightBulbOn and not b.name.startswith(SKIPP) and not b.name.endswith('_v42')]
        st['visible'] = len(vis)
        tc = {}

        def tcopy(b):
            if b.name not in tc:
                tc[b.name] = X.cp(b)
            return tc[b.name]

        def inter(a, b):                       # mm3; a, b model bodies; the smaller is copied fresh, the bigger reused
            if not a.boundingBox.intersects(b.boundingBox):
                return 0.0
            s, g = (a, b) if a.faces.count <= b.faces.count else (b, a)
            t = X.cp(s)
            try:
                X.tbm.booleanOperation(t, tcopy(g), BT.IntersectionBooleanType)
            except Exception:
                return -1.0
            return X.vol(t)
        if 'A' in MODE:
            out = {}
            done = set()
            for n in NEW:
                a = X.body(n)
                for b in vis:
                    if b.name == n or (b.name, n) in done:
                        continue
                    done.add((n, b.name))
                    v = inter(a, b)
                    if abs(v) > 0.02:
                        out['%s~%s' % (n, b.name)] = round(v, 2)
            st['A'] = out; st['tA'] = round(time.time() - t0, 1); status('f2f', st)
        if 'B' in MODE:
            sh = X.cp(X.body('HOUSING_F_front')); X.sec(sh, X.wbox(-130, 130, -110, 40, -5, 100))
            fix = [('HOUSING_F_front', sh)] + [(n, X.cp(X.body(n))) for n in FIX[1:] if X.body(n) is not None]
            unit = [(n, X.cp(X.body(n))) for n in UNIT if X.body(n) is not None]
            st['unit_missing'] = [n for n in UNIT if X.body(n) is None]
            res = {}
            steps = [(-1.3, -dz) for dz in (90, 60, 40, 25, 15, 8, 4, 2, 1, 0.5, 0)] + [(-1.05, -dz) for dz in (40, 8, 2, 0)] + \
                    [(-1.5, -dz) for dz in (40, 8, 2, 0)] + [(-0.9, 0), (-0.5, 0), (-0.2, 0), (0, 0)]
            for (dy, dz) in steps:
                hit = {}
                for n, u in unit:
                    m = X.cp(u); X.move(m, dy=dy, dz=dz)
                    mb = m.boundingBox
                    for fn, f in fix:
                        if not mb.intersects(f.boundingBox):
                            continue
                        t = X.cp(m)
                        try:
                            X.tbm.booleanOperation(t, f, BT.IntersectionBooleanType); v = X.vol(t)
                        except Exception:
                            v = -1.0
                        if abs(v) > 0.02:
                            hit['%s~%s' % (n, fn.replace('HOUSING_F_', 'H_'))] = round(v, 2)
                res['dy%g dz%g' % (dy, dz)] = hit
                st['B'] = res; st['tB'] = round(time.time() - t0, 1); status('f2f', st)
        if 'C' in MODE:
            t = X.cp(X.body('HOUSING_F_front')); X.sec(t, X.wbox(-78, 78, -62, -1.0, 2.8, 12.0))
            st['C'] = [l for l in X.lumps(t)[:10]]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f2f', st)


run(None)
