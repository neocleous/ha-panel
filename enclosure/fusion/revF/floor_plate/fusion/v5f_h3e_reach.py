# rev F h3e (2026-11-11): step 3, block 3 - read-only: the fingertip probe of g1b repeated with main board rev 3 in the model.
#   Tool: cylinder dia 24 x 60 (fingertip) and dia 40 x 60 (pinch), tip on the plug's top, axis toward the door in the six directions
#   of g1b (straight, 25 and 45 degrees down, 25 up, 25 to -x and to +x). 'round' repeats the fingertip with a rounded end (a ball of the
#   same radius at the tip), because a flat end tilted 25 degrees dips 5 mm below the plug's top on one side; 'round16' is a rounded
#   fingertip of 16, to tell by how much a direction is missed.
#   Display module in, door off, every other plug in: the neighbours' mated plugs are blocks on their sockets' outlines (JST 9.8 tall,
#   Dupont housing 16.5; the target's own plug left out). Against the shell (behind depth 18), cap, boxes, plate, Pi, cooler, inlet
#   cradle and board, carrier, ReSpeaker, the board with all its parts, the Pi power plug. Leads are counted apart: they can be pushed
#   aside. A direction counts as blocked above 1.0 mm3, as in g1b.
#   Pi-end housings: tip on the housing's top (z 32), axis up and back at 30, 45 and 60 degrees from the vertical, and 45 with 25 to
#   either side (the audit's F9 found 40 to 60 degrees back).
#   Results are cached per tool; a call stops after BUDGET seconds: call until 'left' is 0.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
BUDGET = globals().get('BUDGET', 28.0)
ONLY = globals().get('ONLY', None)
TARGETS = {'J11 VEML6030': ('B', -0.7, -12.0, 16.5), 'J5 radar': ('B', -40.3, -13.9, 9.8), 'J10 BME680': ('B', -34.3, -14.1, 16.5), 'J6 touch': ('B', 12.3, -22.2, 9.8),
           'J1 20 V': ('B', 0.0, -25.0, 9.8), 'J8 speaker left': ('B', 38.75, -25.0, 9.8), 'J9 speaker right': ('B', -39.0, -25.0, 9.8),
           'J2 Pi power plug': ('B', 21.6, -40.5, 5.0),
           'Pi 1x3 pins 1-3-5': ('W', -32.29, -6.71, 32.0), 'Pi 1x3 display lead': ('W', -32.29, -4.17, 32.0), 'Pi 2x5 pins 7-16': ('W', -22.13, -5.45, 32.0),
           'Pi 2x3 pins 35-40': ('W', 10.91, -5.45, 32.0)}
DIRS = {'straight': (0, 1, 0), 'down25': (0, 0.9063, -0.4226), 'down45': (0, 0.7071, -0.7071), 'up25': (0, 0.9063, 0.4226), 'to-x25': (-0.4226, 0.9063, 0),
        'to+x25': (0.4226, 0.9063, 0)}                               # slab frame (x, depth, Zd)
PIDIRS = {'back30': (0, -0.5, 0.866), 'back45': (0, -0.7071, 0.7071), 'back60': (0, -0.866, 0.5), 'back45 to-x25': (-0.4226, -0.6409, 0.6409),
          'back45 to+x25': (0.4226, -0.6409, 0.6409)}                # world (x, y, z)
PLUGS = {'J9': (-43.24, -34.76, -28.95, -22.11, 9.8), 'J1': (-4.24, 4.24, -28.95, -22.11, 9.8), 'J6': (9.41, 16.24, -28.93, -15.45, 9.8),
         'J8': (34.50, 43.00, -28.95, -22.11, 9.8), 'J5': (-43.20, -36.36, -20.60, -7.11, 9.8), 'J10': (-36.12, -32.48, -19.74, -8.49, 16.5),
         'J11': (-6.31, 4.94, -13.82, -10.18, 16.5), 'J2 socket': (17.16, 26.09, -28.95, -19.78, 3.44)}
# what-if runs: the loader may replace the targets, the plug blocks and the tools, and adds TAG to the status file's name
TARGETS = globals().get('TARGETS_OVERRIDE', TARGETS)
PLUGS = globals().get('PLUGS_OVERRIDE', PLUGS)
LABS = globals().get('LABS', ((12.0, 'finger24'), (20.0, 'pinch40'), (12.0, 'round24'), (8.0, 'round16')))
TAG = globals().get('TAG', '')
FIX = ['HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F', 'PI5_F_cooler', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env',
       'RESP_usbc_plug_env', 'PIPWR_a_env', 'BME_HOOD', 'LD2410C_env_F', 'MAIN_pcb', 'MAIN_PS1', 'MAIN_tall', 'MAIN_low', 'MAIN_J2_plug_env', 'TOUCH_CLIP_L',
       'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_plug_env', 'GROMMET_usbc_F', 'GPIO_plugA_env', 'GPIO_plugB_env']
WB = {'HOUSING_F_cap': (-77.0, 77.0, -41.8, -22.6, 172.6, 180.0), 'SPKBOX_L': (43.5, 95.9, -52.0, -3.0, 3.7, 84.0), 'SPKBOX_R': (-95.9, -43.5, -52.0, -3.0, 3.7, 84.0),
      'PI5_F': (-44.9, 45.2, -59.7, -2.0, 6.1, 25.9), 'PI5_F_cooler': (-42.5, 21.1, -50.1, -7.6, 13.6, 23.1), 'CRADLE_5807': (-11.0, 11.0, -84.6, -60.5, 13.0, 26.7),
      'PD_5807_env': (-10.2, 10.2, -84.6, -60.2, 19.5, 25.4), 'PIPWR_a_env': (-38.2, 31.2, -71.5, -59.1, 4.8, 33.9), 'TOUCH_CLIP_L': (40.5, 45.0, -8.5, 2.0, 30.0, 46.0),
      'TOUCH_CLIP_R': (-45.0, -40.5, -8.5, 2.0, 30.0, 46.0), 'TOUCH_PCB': (-45.0, 45.0, 2.7, 4.3, 6.0, 50.0), 'USBA_plug_env': (45.1, 55.1, -45.0, -22.9, 10.2, 18.2),
      'GROMMET_usbc_F': (-15.1, 15.1, -85.7, -79.5, 11.2, 33.1), 'GPIO_plugA_env': (-36.1, -15.8, -8.0, -2.9, 11.9, 32.0),
      'GPIO_plugB_env': (7.1, 14.8, -8.0, -2.9, 11.9, 32.0), 'plate': (-98.0, 98.0, -81.0, 6.0, 0.0, 13.0)}


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache(); res = c.setdefault('h3e', {})
        if 'crop_front_rear' not in c:
            t = X.cp(tcopy(X, 'HOUSING_F_front')); X.sec(t, X.dbox(-110, 110, 18, 140, -115, 35)); c['crop_front_rear'] = t
        fix = {'shell': c['crop_front_rear'], 'plate': X.wbox(-98.0, 98.0, -81.0, 6.0, 0.0, 13.0)}
        for n in FIX:
            if X.body(n) is not None:
                fix[n] = tcopy(X, n)
        leads = {b.name: tcopy(X, b.name) for b in current(X, leads=True) if b.name.startswith('LEAD_')}
        st['t_setup'] = round(time.time() - t0, 1)
        left = 0; out = {}
        for tn, tg in TARGETS.items():
            if ONLY and tn not in ONLY:
                continue
            pi = tg[0] == 'W'
            tip = Wp(*tg[1:]) if pi else Bp(*tg[1:])
            own = None
            if not pi:
                for pn, (u0, u1, v0, v1, h) in PLUGS.items():
                    if u0 <= tg[1] <= u1 and v0 <= tg[2] <= v1:
                        own = pn
            hard = dict(fix)
            if tn.startswith('J2'):
                hard.pop('MAIN_J2_plug_env', None)       # the tip is on this plug
            if pi:
                hard.pop('GPIO_plugA_env', None); hard.pop('GPIO_plugB_env', None)
            for pn, (u0, u1, v0, v1, h) in PLUGS.items():
                if pn != own and not (own is None and pn == 'J2 socket' and tn.startswith('J2')):
                    hard['plug ' + pn] = bbox_b(X, u0, u1, v0, v1, 0.0, h)
            row = {}
            for r, lab in LABS:
                free = []; blocked = {}; soft = {}
                for dn, dv in (PIDIRS if pi else DIRS).items():
                    key = '%s|%s|%s' % (tn, lab, dn)
                    if key not in res:
                        if time.time() - t0 > BUDGET:
                            left += 1; continue
                        if pi:
                            a = V3(dv[0], dv[1] * C + dv[2] * S, -dv[1] * S + dv[2] * C)
                        else:
                            a = V3(dv[0], -dv[1], dv[2])
                        end = P3(tip.x + 6.0 * a.x, tip.y + 6.0 * a.y, tip.z + 6.0 * a.z)
                        if lab.startswith('round'):
                            cc = P3(tip.x + r / 10.0 * a.x, tip.y + r / 10.0 * a.y, tip.z + r / 10.0 * a.z)
                            tool = X.tbm.createCylinderOrCone(cc, r / 10.0, end, r / 10.0)
                            X.uni(tool, X.tbm.createSphere(cc, r / 10.0))
                        else:
                            tool = X.tbm.createCylinderOrCone(tip, r / 10.0, end, r / 10.0)
                        wa = W(tip); we = W(end)
                        wb = [min(wa[i], we[i]) - r if j == 0 else max(wa[i], we[i]) + r for i in range(3) for j in range(2)]
                        hit = []; sft = []
                        for n, f in hard.items():
                            q = WB.get(n)
                            if q and (wb[0] > q[1] or wb[1] < q[0] or wb[2] > q[3] or wb[3] < q[2] or wb[4] > q[5] or wb[5] < q[4]):
                                continue
                            if not tool.boundingBox.intersects(f.boundingBox):
                                continue
                            t = X.cp(tool)
                            try:
                                X.tbm.booleanOperation(t, f, BT.IntersectionBooleanType); v = X.vol(t)
                            except Exception:
                                v = -1.0
                            if abs(v) > 1.0:
                                hit.append('%s %d' % (n.replace('HOUSING_F_', '').replace('MAIN_', ''), v))
                        for n, f in leads.items():
                            if not tool.boundingBox.intersects(f.boundingBox):
                                continue
                            t = X.cp(tool)
                            try:
                                X.tbm.booleanOperation(t, f, BT.IntersectionBooleanType); v = X.vol(t)
                            except Exception:
                                v = -1.0
                            if abs(v) > 1.0:
                                sft.append(n[5:])
                        res[key] = [hit, sft]
                    hit, sft = res[key]
                    if hit:
                        blocked[dn] = '; '.join(hit)
                    else:
                        free.append(dn)
                        if sft:
                            soft[dn] = ' '.join(sft)
                row[lab] = {'free': free, 'blocked': blocked, 'leads in the way': soft}
            out[tn] = row
            st['reach'] = out; st['left'] = left; st['t'] = round(time.time() - t0, 1); status3('h3e' + TAG, st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h3e' + TAG, st)


run(None)
