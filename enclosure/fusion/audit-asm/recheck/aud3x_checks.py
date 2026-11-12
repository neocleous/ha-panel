# aud3x_checks.py - assembly audit, re-check (2026-11-12, model version 60). TYPED COPY of the functions that were typed into
# the connector calls and attached to sys.modules['aud3x'] at run time. Not run in this form. k = sys.modules['aud3'] (v5f_k_lib.py),
# m = sys.modules['aud3x'] (aud3x_lib.py), A = sys.modules['aud2c'] (aud2_lib.py: TGT, DIRS, PIDIRS, PLUGB, RFIX, ORDER).
# All read-only: temporary bodies, distances, booleans on copies. Results live in m.RES between calls.
import sys, time, math
import adsk.core

STEPS = (0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 35, 40, 50, 60)
LOW = (-60.0, 60.0, -32.9, 36.0, -14.0, -1.0)                                  # board frame; the fix pass's boxes (v5f_k4b)
LEADPART = {'LEAD_GPIO_A1': LOW, 'LEAD_GPIO_A2': LOW, 'LEAD_GPIO_B': LOW, 'LEAD_LCD_5V': LOW,
            'LEAD_MIC_R': (-36.0, -26.5, -36.0, 32.9, -14.0, -1.0), 'LEAD_MIC_L': (31.0, 39.0, -36.0, 32.9, -14.0, -1.0),
            'LEAD_DSI': (40.0, 62.0, -29.0, 36.0, -16.0, 10.0), 'LEAD_USB_RESP': (60.0, 95.0, -36.0, 36.0, -16.0, -1.0)}
SPARE = ['LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_PI_POWER', 'LEAD_USB_RESP']


def mingap(X, movers, fixed, lim=4.0):            # {mover: (mm, fixed label, point on the mover, point on the fixed body)}; None if the boxes are further apart than lim
    k = sys.modules['aud3']; m = sys.modules['aud3x']
    out = {}
    for ml, mb in movers:
        q = m.bb6(mb); best = None
        for fl, fb, fq in fixed:
            dx = max(fq[0] - q[3], q[0] - fq[3], 0.0); dy = max(fq[1] - q[4], q[1] - fq[4], 0.0); dz = max(fq[2] - q[5], q[2] - fq[5], 0.0)
            if math.sqrt(dx * dx + dy * dy + dz * dz) * 10.0 > lim:
                continue
            r = X.mm.measureMinimumDistance(mb, fb); g = r.value * 10.0
            if best is None or g < best[0]:
                best = (round(g, 3), fl, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
        out[ml] = best
    return out


def lift(X, b, hs, names, fixed, t0, lim=48.0):   # plate unit's parts b behind and h below their place: smallest distance to the shell crops
    m = sys.modules['aud3x']
    res = m.RES.setdefault('lift', {}); left = 0
    for h in hs:
        for n in names:
            if (n, b, h) in res:
                continue
            if time.time() - t0 > lim:
                left += 1; continue
            res[(n, b, h)] = mingap(X, [(n, m.mv(X, m.tl(X, n)[0], (0.0, -b, -h)))], fixed).get(n)
    return left
# fixed = m.items(X, crops=['loL', 'loR']); loL = shell cropped to world (0, 100, -64.5, 11, 2, 100), loR its mirror
# names = SPKBOX_L, SPKBOX_R, SPK_L, SPK_R, DRV_screw_heads_env; b = 0.5, 1.0, 1.2, 1.3, 1.5 .. 2.0; h = 80 .. 0
# screw heads again as eight cylinders r 2.85 / r 2.70 x 1.65 at (+-52.75, +-88.25; z 10.25, 45.75), and cut by a sphere
# R = (r*r + 1.15*1.15) / 2.3 centred 1.65 - R behind the top (a dome with 0.5 left at the rim: assumed)


def plate(X, bs, hs, t0, lim=50.0):               # the plate's eight slabs against the shell cropped to z 2..9
    m = sys.modules['aud3x']
    fixed = m.items(X, crops=['botL', 'botR'])
    res = m.RES.setdefault('plate', {}); left = 0
    for b in bs:
        for h in hs:
            if (b, h) in res:
                continue
            if time.time() - t0 > lim:
                left += 1; continue
            best = None
            for i, p in enumerate(m.tl(X, 'FLOOR_PLATE')):
                q = mingap(X, [('p%d' % i, m.mv(X, p, (0.0, -b, -h)))], fixed, 3.0)['p%d' % i]
                if q is not None and (best is None or q[0] < best[0]):
                    best = q
            res[(b, h)] = best
    return left


def ride_setup(X):                                # the display module's pieces and the lead parts that ride with it
    k = sys.modules['aud3']; m = sys.modules['aud3x']
    if 'ride_mov' in m.RES:
        return
    m.crop(X, 'HOUSING_F_front', 'rideS', (-100, 100, 4, 80, -80, 30), 'S')
    mov = []
    for b in k.st(X, 'MODULE'):
        ps = m.tl(X, b.name)
        for i, p in enumerate(ps):
            mov.append((b.name if len(ps) == 1 else '%s#%d' % (b.name, i), p))
    for n in sorted(LEADPART):
        t = X.bbox(*LEADPART[n]); X.sec(t, m.tl(X, n)[0])
        mov.append(('part of ' + n, t))
    m.RES['ride_mov'] = mov
    m.RES['ride_fix'] = m.items(X, names=['PI', 'PIPWR', 'CRADLE', 'INLET', 'BOXES', 'USBA', 'TOUCH', 'RADAR', 'BME'], crops=['rideS'])


def ride(X, t0, lim=48.0, steps=STEPS):           # every piece at every position: smallest distance within 3, and the volume where it is zero
    m = sys.modules['aud3x']
    res = m.RES.setdefault('ride', {}); left = 0
    fx = m.RES['ride_fix']
    for lab, p in m.RES['ride_mov']:
        for s in steps:
            if (lab, s) in res:
                continue
            if time.time() - t0 > lim:
                left += 1; continue
            t = m.mvn(X, p, s)
            g = mingap(X, [(lab, t)], fx, 3.0)[lab]
            if g is not None and g[0] < 0.005:
                g = g + (m.clash(X, [(lab, t)], fx, 0.0005),)
            res[(lab, s)] = g
    return left


def reach2(X, tn, plugs, leads, r=8.0):           # the reach standard of 2026-11-11 with lead bodies as extra obstacles: {direction: {obstacle: mm3}}
    A = sys.modules['aud2c']; k = sys.modules['aud3']; m = sys.modules['aud3x']
    res = m.RES.setdefault('reach', {})
    key = (tn, tuple(sorted(plugs)), tuple(sorted(leads)))
    if key in res:
        return res[key]
    tg = A.TGT[tn]; pi = tg[0] == 'W'
    tip = tuple(tg[1:]) if pi else k.B2W(*tg[1:])
    shell = m.crop(X, 'HOUSING_F_front', 'reachS', (-110, 110, 18, 140, -115, 35), 'S')
    fixed = [('shell', t) for t in shell] + [('plate', t) for t in m.tl(X, 'FLOOR_PLATE')]
    own = None
    if not pi:
        for pn, (u0, u1, v0, v1, h) in A.PLUGB.items():
            if u0 <= tg[1] <= u1 and v0 <= tg[2] <= v1:
                own = pn
    for pn, (u0, u1, v0, v1, h) in A.PLUGB.items():
        if pn in plugs and pn != own:
            fixed.append(('plug ' + pn, X.bbox(u0, u1, v0, v1, 0.0, h)))
    names = list(A.RFIX)
    if 'J2' in plugs and not tn.startswith('J2'):
        names.append('MAIN_J2_plug_env')
    if 'GPIO' in plugs and not pi:
        names += ['GPIO_plugA_env', 'GPIO_plugB_env']
    fixed += [(k.sn(n).replace('MAIN_', ''), m.tl(X, n)[0]) for n in names]
    fixed += [(n, m.tl(X, n)[0]) for n in leads]
    out = {}
    for dn, d in (A.PIDIRS if pi else A.DIRS).items():
        a = d if pi else k.wv(adsk.core.Vector3D.create(d[0], -d[1], d[2]))
        tool = m.finger(X, tip, a, r)
        hit = {}
        for n, b in fixed:
            if not tool.boundingBox.intersects(b.boundingBox):
                continue
            v = X.xv(tool, b)
            if abs(v) > 1.0:
                hit[n] = round(hit.get(n, 0.0) + v)
        out[dn] = hit
    res[key] = out
    return out
# build order: plugs = dict(A.ORDER)[tn], leads = the two microphone leads (and LEAD_DSI for the board's plugs)
# everything plugged: plugs = A.ALLP less the plug's own, leads = SPARE (less LEAD_PI_POWER for J2)

# Places of the spare lengths: m.finger(X, tip, a, 8.0) against every current body and the shell crops, blocked above 1.0 mm3.
#   microphone coils: tip = k.W(k.Dp(20.0 or -14.0, 23.5, 14.5)); slab-frame directions straight, 25, 45, 65 down, 25 down and 25 sideways;
#   from above: tip k.W(k.Dp(x, 20.0, 24.5)), up, 20 back, along the screen, 20 to the middle; tweezers m.finger(X, tip, a, 3.0, 120.0) at 15..35 down
#   DSI fold (38.5, -33, 56), Pi power lap (26, -47, 55), USB loop (55, -55, 28), anchor (58.5, -56.5, 6): back, 25 and 45 up, 25 down, 25 sideways
# DSI strips (0.4 thick): X.bbox(45.3, 45.7, -8, 8, -23.4, 6.0); (.., -8, 8, -23.4, -13.0); (.., -28.5, -8, -22.0, -6.0); (.., -28.5, -12.5, -6.0, 14.0)
#   and 14..40; X.wbox(30.4, 46.4, -34.2, -33.8, 43, 69); (30.4, 46.4, -30.7, -30.3, 43.5, 69.6); (31, 47, -27.8, -26.6, 43, 75);
#   (38.0, 38.4, -58, -42, 30, 82) and at x 35.8, 40.8; (12.8, 13.2, -55.75, -44.25, 14, 30); (14, 38, -58, -42, 29.8, 30.2) and at z 27


def pic(X, name, show, eye, tgt, ext, up=(0, 0, 1), w=1600, h=1200):   # NOT read-only: visibility, camera, a picture file on the Mac
    import os, adsk
    k = sys.modules['aud3']; m = sys.modules['aud3x']
    m.PIC['only'](X, show)                        # v5f_k_pic.py: the templates AUD_* and the bodies named, nothing else
    k.cam(X, eye, tgt, ext=ext, up=up)
    adsk.doEvents()
    d = os.path.expanduser('~/Documents/HA_panel_renders/audit-recheck')
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    return X.app.activeViewport.saveAsImageFile(path, w, h), path
# before the first picture: m.RES['vis0'] = names of the visible bodies, m.RES['cam0'] = the camera; after the last: X.wipe('AUD_'),
# m.PIC['restore'](X, m.RES['vis0']), the camera set back. Closing state: version 60 of 60, 386 bodies, 36 visible (the same set), no AUD_* body, modified.
