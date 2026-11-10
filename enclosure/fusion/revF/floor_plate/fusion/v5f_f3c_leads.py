# rev F f3c (2026-11-10): floor plate pass, block 3 - leads re-routed to the main board's place behind the display.
# Each lead is a chain of cylinders and spheres through the nodes below (W = world x_rel, y, z; S = slab x_rel, depth, Zd).
# Main-board ends: the plug tops (19.8 above the component face = depth 52.5; J10 header 16.5 = depth 49.2), the J3/J4 wire pads
# at the component face, the J2 plug's cable end below the board. Device ends: the nodes of the version 42 leads.
# Dry by default: lengths, and what each lead touches. APPLY=True: old LEAD_* hidden as <name>_v42, new bodies added (hidden, as before).
import os, re
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
APPLY = globals().get('APPLY', False)
ROUTES = {
    'LEAD_PIGTAIL_20V': (1.6, [('W', 0, -65, 22), ('W', 0, -62, 28), ('W', 1, -52, 58), ('W', 2.5, -44, 78), ('S', 2.55, 54.5, -51.3)]),
    'LEAD_SPK_L': (1.6, [('W', 62, -54, 30), ('W', 62, -57, 34), ('W', 52, -59, 50), ('W', 44, -52, 66), ('W', 36, -47, 76), ('W', -28, -45, 78),
                         ('S', -30.95, 54.5, -50.0)]),
    'LEAD_SPK_R': (1.6, [('W', -62, -54, 30), ('W', -62, -57, 34), ('W', -52, -59, 50), ('W', -44, -52, 64), ('W', -36, -48, 73), ('W', 33, -47, 74.5),
                         ('S', 35.55, 54.5, -50.0)]),
    'LEAD_RADAR': (1.3, [('S', 33.25, 54.2, -10.0), ('S', 33.25, 56.0, -22.0), ('S', -44.0, 56.0, -22.0), ('S', -56.0, 40.0, -16.0), ('W', -69, -24, 128)]),
    'LEAD_TOUCH': (1.2, [('W', 12, 2, 46), ('W', 12, 1, 52), ('W', 8, -10, 70), ('W', 4, -45, 75.5), ('W', 0, -51, 95), ('S', -1.45, 54.2, -30.0)]),
    'LEAD_BME680': (1.5, [('S', 21.0, 51.0, -12.5), ('S', 21.0, 58.5, -26.0), ('S', -46.0, 58.5, -26.0), ('W', -67, -36, 84), ('W', -72, -41.5, 86),
                          ('W', -71, -40.5, 94)]),
    # the cap's back-left key path (Ø5 from (25.9, -37.8, 166.2) down and back) passes 5 behind this lead where they share x 22.5..25.5
    'LEAD_VEML': (1.5, [('S', 24.0, 51.0, -12.5), ('S', 24.0, 51.0, -5.5), ('S', 24.0, 46.0, -1.5), ('S', 24.0, 42.0, 3.0), ('S', 0.0, 34.6, 29.5),
                        ('W', 0, -40, 176)]),
    'LEAD_GPIO_A': (2.5, [('W', -26, -5, 32), ('W', -26, -5, 40), ('W', -10, -18, 62), ('W', 12, -36, 84), ('S', 17.05, 44.0, -42.25),
                          ('S', 17.05, 35.5, -42.25)]),
    'LEAD_GPIO_B': (1.8, [('W', 11, -5, 32), ('W', 11, -5, 40), ('W', 6, -18, 70), ('S', 9.6, 46.0, -50.0), ('S', 3.85, 44.0, -42.25),
                          ('S', 3.85, 35.0, -42.25)]),
    'LEAD_LCD_5V': (1.5, [('S', 33.0, 13.0, -2.4), ('S', 33.0, 24.0, -3.0), ('S', -45.6, 24.0, -3.0), ('S', -45.6, 19.5, -54.0), ('W', -40, -8, 60),
                          ('W', -32, -6, 44), ('W', -32, -5, 33)]),
    'LEAD_MIC_L': (1.0, [('S', 39.0, 20.0, -30.7), ('S', 39.0, 19.6, -10.5), ('S', 37.0, 21.5, 2.5), ('S', 21.0, 21.7, 27.8), ('W', 21, -26, 172)]),
    'LEAD_MIC_R': (1.0, [('S', -32.0, 20.0, -30.7), ('S', -30.0, 19.6, -10.5), ('S', -28.0, 21.5, 2.5), ('S', -21.0, 21.7, 27.8), ('W', -21, -26, 172)]),
    # rises at x 50, inboard of the key path to the +x box-top screw (along y at x 54..58, z 79.5), and crosses outboard between that
    # path (top z 82) and the lower-left display-screw path (bottom z 87.4 at y -52)
    'LEAD_USB_RESP': (1.7, [('W', 52, -54, 14), ('W', 51, -56, 22), ('W', 50, -56, 80), ('W', 55.5, -52, 85.2), ('W', 62, -45, 90), ('W', 77, -32, 103),
                            ('W', 81, -25.5, 113), ('S', 79.3, 25.4, -20.2)]),
    'LEAD_DSI': (1.5, [('W', 12, -50, 14), ('W', 14, -50, 30), ('W', 30, -40, 30), ('W', 34, -32, 33), ('W', 36, -28, 40), ('W', 42, -26, 76),
                       ('W', 50, -24, 82), ('S', 51.0, 24.0, -45.0), ('S', 50.0, 19.6, -31.0), ('W', 47, -3, 115)]),
    # ends on top of PIPWR_a_env (plug, 90 degree adapter and the first of the cable, to z 33 at x 18..31)
    'LEAD_PI_POWER': (2.5, [('S', -22.45, 29.2, -78.5), ('W', -18, -18, 60), ('W', 20, -45, 52), ('W', 26, -60, 44), ('W', 25, -66, 35.5)]),
}
ROUTES.update(globals().get('ROUTES_OVERRIDE', {}))
LEGACY = ('DOOR_tray', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip', 'AMP_env_20x20x10', 'BUCK_20to5V_env_43x25x13', 'DOOR_plate_revE', 'GROMMET_usbc',
          'HOUSING_F_front_d10_sliver', 'HOUSING_F_front_d12a_sliver1', 'LD2410C_env', 'MAIN_BRACKET_d1split_L', 'MAIN_BRACKET_d1split_R',
          'MAIN_BRACKET_d1split_plug', 'PD_trigger_env_20V', 'PI5_board', 'SPKBOX_L_r2', 'SPK_driver_D40', 'V11a_mx', 'V11a_px', 'V11a_up', 'V11b_mx',
          'V11b_px', 'V11b_up', 'V11c_straight', 'VOICEPE_back_env', 'VOICEPE_encoder_env', 'VOICEPE_pcb', 'BME680_env_revD', 'TOUCH_pcb_100x44')
BACK = re.compile(r'(_v42|_[a-e]\d+[a-z0-9]*| \(\d+\))$')


def run(_context):
    st = {'apply': APPLY}
    t0 = time.time()
    try:
        X = K()

        def pt(n):
            return Wp(n[1], n[2], n[3]) if n[0] == 'W' else Dp(n[1], n[2], n[3])
        cur = [b for b in X.root.bRepBodies if not BACK.search(b.name) and not b.name.startswith(('REF_', 'TOOL_', 'INNER', 'RENDER_', 'LEAD_'))
               and b.name not in LEGACY]
        if globals().get('NAMES'):
            st['current'] = ' '.join(sorted(b.name for b in cur))
        tc = {}
        res = {}; new = {}
        for name, (r, nodes) in ROUTES.items():
            ps = [pt(n) for n in nodes]
            L = sum(ps[i].distanceTo(ps[i + 1]) for i in range(len(ps) - 1)) * 10.0
            body = None
            for i in range(len(ps) - 1):
                c = X.tbm.createCylinderOrCone(ps[i], r / 10.0, ps[i + 1], r / 10.0)
                body = c if body is None else X.uni(body, c)
                if i > 0:
                    X.uni(body, X.tbm.createSphere(ps[i], (r + 0.05) / 10.0))
            old = X.body(name)
            hits = {}
            bb = body.boundingBox
            for b in cur:
                if not b.boundingBox.intersects(bb):
                    continue
                if b.name not in tc:
                    tc[b.name] = X.cp(b)
                t = X.cp(body)
                try:
                    X.tbm.booleanOperation(t, tc[b.name], BT.IntersectionBooleanType); v = X.vol(t)
                except Exception:
                    v = -1.0
                if abs(v) > 0.3:
                    ls = X.lumps(t)
                    vo = 0.0
                    if old is not None and old.boundingBox.intersects(b.boundingBox):
                        u = X.cp(old)
                        try:
                            X.tbm.booleanOperation(u, tc[b.name], BT.IntersectionBooleanType); vo = X.vol(u)
                        except Exception:
                            vo = -1.0
                    hits[b.name.replace('HOUSING_F_', 'H_')] = [round(v, 1), round(vo, 1)] + ([int(q) for q in ls[0][1]] if ls and ls[0][1] else [])
            res[name[5:]] = {'L': round(L), 'old': round(old.volume * 1000 / (math.pi * r * r)) if old is not None else None, 'hit': hits}
            new[name] = (body, old)
            st['leads'] = res; status('f3c', st)
        if APPLY:
            for name, (body, old) in new.items():
                if old is not None:
                    X.retire(old)
                X.add(body, name, like=old, show=False)
            st['added'] = [X.dups(), X.root.bRepBodies.count]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('f3c', st)


run(None)
