# Block 9, after the put: the key lines and the ways (brief block 9 point 5; log B section 4.B points 5 and 6). READ-ONLY but
# for TMP_ bodies, deleted again. Two states of the unit:
#   'build'    step 22 of the first build: shell and screen plate on the plate unit, touch board and clips in; no display module,
#              no cap, no door, none of the module's leads, the Pi power cable laid aside
#   'service'  everything in but the door and its grommet; the Pi power cable and its plug on J2 out (first out in service)
# Leads and keep-outs are never obstacles (they are pushed aside); the leads a path crosses are listed beside it.
#   'key'    the 2.0 key (shaft 2.4 across, long arm 101, short arm 16) with its short arm in the holder's M3: the long arm swept
#            in the plane x = xe about the screw's axis, every 5 deg from straight down round to past straight up (0 = pointing
#            back at the door, 90 = straight up); what each position meets
#   'm2'     the Phillips driver straight out of each M2 head (holder and radar on the bench)
#   'out'    the holder with the radar, its two screws and the lead's start, drawn back from its place by b at lifts h
#   'finger' a rounded fingertip 16 across from six directions onto the holder's top plate and tab (service)
#   'shell'  the shell's way down with the holder on the unit: the holder set b behind and h below its place against the shell,
#            the screen plate, the slab, the display and the touch board; then the slide home
#   'board'  the touch board's way out with the holder and the radar off (p71's walk), and the left clip's way with the holder
#            on and off
# Run: runpy.run_path(D + 'p89_b9_ways.py')['main'](stage, **kw)  -> p89_<stage>[_<state>].txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
MODULE = ('SLAB_frame', 'LCD_', 'RESP_', 'MAIN_')
CAPSET = ('HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env')
DOOR = ('HOUSING_F_door', 'GROMMET_usbc_F')
HSET = ('RADAR_HOLDER', 'LD2410C_env_F')
M3 = (-7.35, 57.6); HEAD_X = 36.6 - 1.65


def hard(k, X, state, skip=()):
    out = []
    for b in k.current(X, leads=False, kos=False):
        n = b.name
        if n in DOOR or n in skip or n == 'MAIN_J2_plug_env' or n.startswith('FOOT_'):
            continue
        if state == 'build' and (n.startswith(MODULE) or n in CAPSET):
            continue
        out.append(b)
    return out


def leads(k, X, state):
    if state == 'build':
        return []
    return [b for b in k.current(X, leads=True, kos=False) if b.name.startswith('LEAD_') and b.name not in ('LEAD_PI_POWER', 'LEAD_RADAR')]


def crops(k, X, bodies, box):
    zone = X.wbox(*box); out = []
    for b in bodies:
        t = X.tbm.copy(b)
        if not t.boundingBox.intersects(zone.boundingBox):
            continue
        X.sec(t, X.tbm.copy(zone))
        if t.faces.count:
            out.append((b.name, t))
    return out


def hits(X, movers, fixed, dx=0.0, dy=0.0, dz=0.0):
    h = {}
    for m in movers:
        t = X.move(X.tbm.copy(m), dx, dy, dz) if (dx or dy or dz) else m
        for nm, f in fixed:
            v = X.xv(t, f)
            if v > 0.0005:
                h[nm] = round(h.get(nm, 0) + v, 3)
    return h


def mind(k, X, t, fixed):
    best = None
    A = X.add(X.tbm.copy(t), 'TMP_a', show=False)
    for nm, f in fixed:
        B = X.add(X.tbm.copy(f), 'TMP_b', show=False)
        d = X.mm.measureMinimumDistance(A, B).value * 10.0
        B.deleteMe()
        if best is None or d < best[0]:
            best = (round(d, 2), nm)
    A.deleteMe()
    return best


def key(k, X, state='service', xes=(21.0,), step=5, **kw):
    for xe in xes:
        zone = (xe - 3.0, xe + 3.0, -120.0, 12.0, -50.0, 185.0)
        fx = crops(k, X, hard(k, X, state), zone); ld = crops(k, X, leads(k, X, state), zone)
        short = X.cyl((xe - 1.2, M3[0], M3[1]), (HEAD_X + 1.3, M3[0], M3[1]), 1.2)
        fs = crops(k, X, hard(k, X, state), (xe - 3.0, 38.0, -12.0, -2.0, 52.0, 63.0))
        print('%s, elbow at x %.1f: the short arm (x %.1f..%.1f) meets %s; nearest %s' % (state, xe, xe - 1.2, HEAD_X + 1.3, hits(X, [short], fs) or 'nothing', mind(k, X, short, fs)))
        free = []
        for phi in range(kw.get('lo', -90), kw.get('hi', 125), step):
            if k.late():
                print('time'); break
            r = math.radians(phi)
            arm = X.cyl((xe, M3[0], M3[1]), (xe, M3[0] - 101.0 * math.cos(r), M3[1] + 101.0 * math.sin(r)), 1.2)
            h = hits(X, [arm], fx); hl = hits(X, [arm], ld)
            if not h:
                free.append(phi)
            print('   %4d deg: %s%s%s' % (phi, h or 'free', (' nearest %s' % (mind(k, X, arm, fx),)) if not h and phi % 15 == 0 else '', ('  | leads in the way: %s' % hl) if hl else ''))
        runs = []
        for p in free:
            if runs and p - runs[-1][1] == step:
                runs[-1][1] = p
            else:
                runs.append([p, p])
        print('   free sectors: %s' % ['%d to %d (%d deg)' % (a, b, b - a) for a, b in runs])


def m2(k, X, **kw):
    bench = [X.body('RADAR_HOLDER'), X.body('LD2410C_env_F')]
    for x, z in ((22.5, 31.6), (40.5, 48.8)):
        o = (x, -5.19, z)
        print('M2 at (x %.1f, z %.1f), head\'s flat face at y -5.19, driver along -y:' % (x, z))
        print('   MICRO ', k.fm(k.line(X, o, (0, -1, 0), k.MICRO, bench, st0=0.5, step=1.0)))


def hset(k, X):
    mv = [X.tbm.copy(X.body(n)) for n in HSET]
    s = X.wbox(18, 45, -8, 3, 27, 52); X.sec(s, X.tbm.copy(X.body('SCREWS_M2x6_env'))); mv.append(s)
    l = X.wbox(20, 28, -13, -5, 38, 52); X.sec(l, X.tbm.copy(X.body('LEAD_RADAR'))); mv.append(l)
    return mv


def out(k, X, state='service', **kw):
    mv = hset(k, X)
    zone = (-6.0, 48.0, -90.0, 6.0, 20.0, 80.0)
    fx = crops(k, X, hard(k, X, state, skip=HSET + ('SCREWS_M2x6_env',)), zone)
    ld = crops(k, X, leads(k, X, state), zone)
    print('%s: fixed in the zone: %s' % (state, sorted(n for n, t in fx)))
    for h in (0.0, 3.0, 6.0, 9.0, 12.0):
        row = []
        for b in (0.0, 0.3, 0.7, 1.0, 2.0, 3.0, 5.0, 7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 76.0):
            if k.late():
                row.append('time'); break
            hh = hits(X, mv, fx, 0, -b, h); hl = hits(X, mv, ld, 0, -b, h)
            row.append((b, hh or 'clear', hl or ''))
        print('lift %.0f:' % h)
        for r in row:
            print('    back %s' % (r,))


def path(k, X, state='service', pts=(), **kw):
    mv = hset(k, X)
    zone = (-30.0, 48.0, -95.0, 6.0, 20.0, 90.0)
    fx = crops(k, X, hard(k, X, state, skip=HSET + ('SCREWS_M2x6_env',)), zone)
    ld = crops(k, X, leads(k, X, state), zone)
    print('%s: the holder set moved by (toward the middle, back, up):' % state)
    for dx, b, h in pts:
        if k.late():
            print('time'); break
        hh = hits(X, mv, fx, -dx, -b, h); hl = hits(X, mv, ld, -dx, -b, h)
        near = '' if hh else ' nearest %s' % (mind(k, X, X.move(X.tbm.copy(mv[0]), -dx, -b, h), fx),)
        print('   (%5.1f, %5.1f, %4.1f): %s%s%s' % (dx, b, h, hh or 'clear', near, ('  | leads: %s' % hl) if hl else ''))


def finger(k, X, state='service', **kw):
    fx = hard(k, X, state, skip=HSET + ('SCREWS_M2x6_env',))      # the holder itself is what the fingertip is on
    tip = [(16.0, 70.0)]
    for lab, o in (('top plate\'s rear edge, middle', (31.0, -10.4, 52.1)), ('tab\'s rear edge', (38.3, -10.7, 58.0)), ('the screw\'s head', (HEAD_X, M3[0], M3[1]))):
        print('%s %s:' % (lab, o))
        for nm, u in (('straight back', (0, -1, 0)), ('25 up', k.tilt((0, -1, 0), (0, 0, 1), 25)), ('45 up', k.tilt((0, -1, 0), (0, 0, 1), 45)), ('25 down', k.tilt((0, -1, 0), (0, 0, -1), 25)),
                      ('25 toward the middle', k.tilt((0, -1, 0), (-1, 0, 0), 25)), ('25 toward the left box', k.tilt((0, -1, 0), (1, 0, 0), 25))):
            if lab.startswith('the screw') :
                u = k.tilt((-1, 0, 0), u, 0) if False else u
            r = k.line(X, o, u, tip, fx, st0=8.0, step=4.0, head=0.0)
            print('   %-22s %s' % (nm, k.short(r)))


def shell(k, X, **kw):
    mv = hset(k, X)
    names = ['HOUSING_F_front', 'HOUSING_F_plate', 'SLAB_frame', 'TOUCH_PCB', 'TOUCH_components_env', 'HOUSING_F_cap', 'BME_HOOD'] + \
            [b.name for b in k.current(X, leads=False, kos=False) if b.name.startswith(('LCD_', 'RESP_', 'MAIN_'))]
    zone = (-8.0, 50.0, -20.0, 12.0, 20.0, 130.0)
    fx = crops(k, X, [X.body(n) for n in names], zone)
    ld = crops(k, X, [X.body(n) for n in ('LEAD_TOUCH', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_DSI', 'LEAD_MIC_L')], zone)
    print('fixed with the shell, in the zone: %s' % sorted(n for n, t in fx))
    for s in (0.0, 0.25, -0.25):
        for b in (0.95, 1.2, 1.6):
            met = []; ml = []
            for i in range(0, 32):
                h = 2.0 * i
                if k.late():
                    met.append('time'); break
                hh = hits(X, mv, fx, s, -b, -h); hl = hits(X, mv, ld, s, -b, -h)
                if hh:
                    met.append((h, hh))
                if hl:
                    ml.append((h, hl))
            print('unit %.2f behind, %+.2f to one side, lifts 0 to 62 below: %s%s' % (b, s, met or 'clear at every lift', ('  | leads: %s' % ml) if ml else ''))
    for b in (1.6, 1.2, 0.95, 0.8, 0.7, 0.6, 0.5, 0.4, 0.2, 0.0):
        print('at seat height, %.2f behind: %s' % (b, hits(X, mv, fx, 0, -b, 0) or 'clear'))


def board(k, X, **kw):
    P71 = runpy.run_path(D + 'p71_b7_ways.py')
    movers = [X.tbm.copy(X.body('TOUCH_PCB')), X.tbm.copy(X.body('TOUCH_components_env'))]
    fixed = P71['near'](k, X, (-60, 60, -30, 10, -2, 110), ('TOUCH_PCB', 'TOUCH_components_env', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SCREWS_M2x6_env') + HSET)
    print('the touch board, holder and radar off; fixed near it: %d bodies' % len(fixed))
    for h in (0.25, 0.5, 1.0):
        print('up %.2f: %s' % (h, hits(X, movers, fixed, 0, 0, h) or 'clear'))
    for b in (0.5, 1.0, 2.0, 3.0, 4.0, 5.0):
        print('up 1, back %.1f: %s' % (b, hits(X, movers, fixed, 0, -b, 1.0) or 'clear'))
    for bb in (3.0, 4.0):
        for h in (2.0, 3.0, 5.0, 10.0, 20.0, 30.0):
            print('up 1, back %.0f, up %.1f more: %s' % (bb, h - 1.0, hits(X, movers, fixed, 0, -bb, h) or 'clear'))
    c = X.tbm.copy(X.body('TOUCH_CLIP_L'))
    for lab, skip in (('holder on', ()), ('holder and radar off', HSET)):
        fx = P71['near'](k, X, (10, 50, -20, 10, 20, 66), ('TOUCH_CLIP_L', 'KO_touch_back') + (('SCREWS_M2x6_env',) if skip else ()) + skip)
        for back in (0.0, 0.4):
            print('left clip, %s, %.1f back, toward the middle: %s' % (lab, back, [(s, hits(X, [c], fx, -s, -back, 0) or 'clear') for s in (0.0, 0.3, 0.5, 1.0, 2.0, 4.0, 8.0)]))


def _main(stage, kw):
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    try:
        {'key': key, 'm2': m2, 'out': out, 'path': path, 'finger': finger, 'shell': shell, 'board': board}[stage](k, X, **kw)
    finally:
        for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
            b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, **kw):
    tag = stage + ('_' + kw['state'] if 'state' in kw else '') + ('_' + kw['tag'] if 'tag' in kw else '')
    kw.pop('tag', None)
    L['out']('p89_%s.txt' % tag, _main, stage, kw)
