# rev F m3b (2026-11-13): ribbon pass, block 3 - checks on the whole unit at version 62. Read-only: temporary bodies and measurements.
#   It runs the fix pass's checks (v5f_k4a_unit_checks.py as k4, v5f_k4b_addenda.py as k4b; the library is k, the strip library m) with what
#   this pass changed: the two flat leads, the ADT plugs, no USBA_cable_env. Results are kept in k.c under the tag 62; every function stops
#   when the call's time is used up and says what is left.
#   setup()     the body groups and the parts of the leads that ride with the display module, for version 62
#   ride()      the display module's ride-in at 23 positions with the ribbon's and the cable's parts and the plug
#   slide()     the left speaker box sliding on with the ADT plug in the Pi and the cable behind it
#   way()       the plate unit's way in and out, with the cable's roll on it
#   reach5()    the reach standard at the five plugs of the brief, every plug in, with and without the leads as obstacles
#   matrix()    every current body against every other; diff() against the pairs of version 60 if they are still in memory
#   leads()     the three leads this pass laid against every other lead and every key path
import time
TAG = 62
LEADPART_NEW = {'LEAD_DSI': (35.0, 52.0, -20.0, 20.0, -26.0, 32.0),          # board frame: the ribbon from its connector to crease 3 and 12 of its drop
                'LEAD_USB_RESP': (36.0, 52.0, -5.0, 20.0, -16.0, 36.0)}      # the cable's run toward the door, its fold and 12 of its drop
CABLE_LOW = (40.0, 75.0, -62.0, -20.0, 5.0, 52.0)                           # world: the roll, the row over it, the fold at the bottom, the run to the plug
FIVE = ('Pi 2x3 (35-40)', 'Pi DSI', 'J8 speaker left', 'J6 touch', 'J2 Pi power')


def setup(X):
    k.ST['USBA'] = ['USBA_plug_env']                 # USBA_cable_env is retired: the flat cable is LEAD_USB_RESP
    lp = dict(k4b['LEADPART']); lp.update(LEADPART_NEW)
    if dict(k4['LEADPART']) != lp:
        k4['LEADPART'].clear(); k4['LEADPART'].update(lp)
        for q in [q for q in k.c if isinstance(q, tuple) and q[0] == 'k4lp' and q[1] == TAG]:
            del k.c[q]
        res = k.c.setdefault(('k4ride', TAG), {})
        for q in [q for q in res if q[0].startswith('part of')]:
            del res[q]
    q = ('k4p', TAG, 'cable on the unit')
    if q not in k.c:
        t = X.wbox(*CABLE_LOW)
        X.tbm.booleanOperation(t, k.tcopy(X, 'LEAD_USB_RESP'), k4['BT'].IntersectionBooleanType)
        k.c[q] = [t]
    return {n: [round(v, 1) for v in k4['sbox'](k4['leadpart'](X, TAG, n))] + [round(k4['leadpart'](X, TAG, n).volume * 1000.0, 1)]
            for n in LEADPART_NEW}, round(k.c[q][0].volume * 1000.0, 1)


def nz(res):                                         # the rows of a result that are not empty: {key: hits}
    return {q: v for q, v in res.items() if v}


def ride(X):
    res, left = k4['ride_in'](X, TAG)
    bad = nz(res)
    return len(res), left, {str(q): v for q, v in sorted(bad.items(), key=lambda t: str(t[0]))}


def slide(X):
    fixed = ('FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'CRADLE_5807', 'PD_5807_env', 'USBA_plug_env', 'LEAD_USB_RESP', 'SPKBOX_R', 'SPK_R')
    res = k4['slide'](X, TAG, fixed=fixed)
    return len(res), {str(q): v for q, v in sorted(nz(res).items(), key=lambda t: (t[0][0], -t[0][1]))}


def way(X):                                          # in: the unit lifted in from below; out: for service, with module, cap and touch board in the shell
    res, left = k4['way_in'](X, TAG, extra=('cable on the unit',))
    out, left2 = k4b['way_out'](X, TAG)
    # the cable's roll on the unit on its way out, against the same fixed bodies
    rc = k.c.setdefault(('m3cable', TAG), {})
    fixed = [n for n in k4['names_of'](X, 'SHELL', 'RADAR', 'BME', 'MODULE', 'CAP') if n not in ('SLAB_frame', 'LCD_glass', 'LCD_panel_body')]
    fixed += ['TOUCH_PCB', 'TOUCH_components_env', 'LEAD_DSI', 'LEAD_SPK_L']
    p = k.c[('k4p', TAG, 'cable on the unit')][0]
    wb = k.wbb(X, p); box = (wb[0] - 1.0, wb[1] + 1.0, wb[2] - 2.6, wb[3] + 1.0, wb[4] - 81.0, wb[5] + 1.0)
    pos = [(b, 0.0) for b in (0.25, 0.5, 0.75, 1.0, 1.3, 1.5)] + [(b, float(h)) for b in (1.3, 1.5) for h in (0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 40, 60, 80)]
    left3 = 0
    for b, h in pos:
        if (b, h) in rc:
            continue
        if k.late():
            left3 += 1; continue
        t = X.move(X.tbm.copy(p), 0.0, -b, -h); hit = {}
        for f in fixed:
            v = sum(X.xv(t, c) for c in k4['crop'](X, TAG, f, box))
            if abs(v) > 0.0005:
                hit[f] = round(v, 3)
        rc[(b, h)] = hit
    return ({'in': [len(res), left, {str(q): v for q, v in nz(res).items()}],
             'out': [len(out), left2, {str(q): v for q, v in nz(out).items()}],
             'cable out': [len(rc), left3, {str(q): v for q, v in nz(rc).items()}]})


def reach5(X, targets=FIVE):
    leads = [b.name for b in k.current(X, leads=True) if b.name.startswith('LEAD_')]
    out = {}
    for tn in targets:
        row = {}
        for lab, extra in (('no leads', ()), ('leads', tuple(n for n in leads if not (tn == 'Pi DSI' and n == 'LEAD_DSI')))):
            r = k4['reach'](X, TAG, tn, k4['ALLP'], extra=extra)
            if r is None:
                return out, tn
            row[lab] = r
        out[tn] = row
    return out, None


def matrix(X):
    res, left, n = k4['matrix'](X, TAG)
    return n, len(res), left, {q: v for q, v in res.items() if v}


def diff(X):                                         # against the fix pass's result for version 60, if this Fusion session still holds it
    new = {q: v for q, v in k.c.get(('k4m', TAG), {}).items() if v}
    old = k.c.get(('k4m', 60))
    if old is None:
        return None
    old = {q: v for q, v in old.items() if v}
    sym = lambda d: {tuple(sorted(q)): v for q, v in d.items()}
    a = sym(old); b = sym(new)
    return {'only 60': {q: a[q] for q in a if q not in b}, 'only 62': {q: b[q] for q in b if q not in a},
            'changed': {q: (a[q], b[q]) for q in a if q in b and abs(a[q] - b[q]) > 0.05}, 'n60': len(a), 'n62': len(b)}


def leads(X, mine=('LEAD_DSI', 'LEAD_USB_RESP', 'LEAD_SPK_L'), lim=6.0):
    cur = k.current(X, leads=True)
    others = [b for b in cur if b.name.startswith('LEAD_') or b.name.startswith('KO_')]
    out = {}
    for a in mine:
        A = X.body(a); row = []
        for b in others:
            if b.name == a:
                continue
            d = X.mm.measureMinimumDistance(A, b).value * 10.0
            if d <= lim:
                v = k4['overlap'](X, TAG, A, b) if d < 0.0005 else 0.0
                row.append((round(d, 2), k.sn(b.name), round(v, 1)))
        out[a] = sorted(row)
    return out
