# Block 1: the touch clips' screws and what stands round them. READ-ONLY (temporary bodies only).
#   names    every body of the unit, by name
#   head     an M3 x 8 button head (5.7 across, 1.65 high) drawn on each clip's screw, the screw's shank and its key, against every
#            body of the unit: shared volume as modelled, and with the screw at either end of the clip's slot (0.4 forward, 0.4 back)
#   key      the 2.0 key swept on a clip's screw at a given y, at step 22 ('build') or in service; which positions are free
#   room     what stands within 1.0 of the places a clip's screw line would need if it were moved back along y by 'back'
# Run: runpy.run_path(D + 'd14_clip.py')['main'](stage)  -> d14_<stage>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PY = -7.05; PZ = 38.0          # the clip pilot's axis, measured (d13 faces): y -7.05, z 38.0, along x; the clip's inboard face x 40.5


def st_names(k, X):
    cur = k.current(X, leads=True)
    print(len(cur), 'bodies in the unit:')
    print(', '.join(sorted(b.name for b in cur)))


def shared(k, X, t, skip=()):
    out = []
    for b in k.current(X, leads=True):
        if b.name in skip or not b.boundingBox.intersects(t.boundingBox):
            continue
        v = X.xv(t, X.tbm.copy(b)) if b.name not in k.BIG else k.xvol(X, t, b.name)
        if abs(v) > 0.0005:
            out.append('%s %.3f' % (b.name, v))
    return out


def st_head(k, X):
    k.budget(70)
    for sx, side in ((1, 'L'), (-1, 'R')):
        for dy in (0.0, 0.4, -0.4):
            y = PY + dy
            head = X.cyl((sx * 40.5, y, PZ), (sx * 38.85, y, PZ), 2.85)
            shank = X.cyl((sx * 40.5, y, PZ), (sx * 48.5, y, PZ), 1.5)
            print('side %s, screw at y %.2f: head shares %s' % (side, y, shared(k, X, head) or 'nothing'))
            if dy == 0.0:
                print('            shank (3.0 across, to x %.1f) shares %s' % (sx * 48.5, shared(k, X, shank) or 'nothing'))
        b = X.body('TOUCH_CLIP_' + side)
        for n in ('LD2410C_env_F', 'RADAR_HOLDER', 'GPIO_plugB_env', 'GPIO_plugA_env', 'PIPWR_a_env', 'HOUSING_F_front', 'TOUCH_PCB', 'LEAD_TOUCH', 'LEAD_RADAR'):
            o = X.body(n)
            if o is None:
                continue
            r = X.mm.measureMinimumDistance(b, o)
            if r.value * 10 < 12.0:
                print('   TOUCH_CLIP_%s to %-16s %.3f at %s' % (side, n, r.value * 10, k.r2(k.W(r.positionOne), 2)))


def st_room(k, X, back=1.4):
    k.budget(70)
    for sx, side in ((1, 'L'), (-1, 'R')):
        tests = {'clip plate grown back (x 40.5..43.5, y %.1f..-10.4, z 30..46)' % (-10.4 - back): (40.5, 43.5, -10.4 - back, -10.4, 30.0, 46.0),
                 'block grown back outside the box (x 43.5..46, same y, z 30..46)': (43.5, 46.0, -10.4 - back, -10.4, 30.0, 46.0),
                 'screw head moved back (x 38.85..40.5)': None}
        for nm, bx in tests.items():
            for grow in (0.0, 0.5, 1.0):
                if bx is None:
                    t = X.cyl((sx * (40.5 + grow), PY - back, PZ), (sx * (38.85 - grow), PY - back, PZ), 2.85 + grow)
                else:
                    a, b = sorted((sx * (bx[0] - grow), sx * (bx[1] + grow)))
                    t = X.wbox(a, b, bx[2] - grow, bx[3] + grow, bx[4] - grow, bx[5] + grow)
                print('side %s, %s, grown %.1f: %s' % (side, nm, grow, shared(k, X, t, skip=('TOUCH_CLIP_' + side, 'SPKBOX_' + side)) or 'nothing'))


MODULE = ('SLAB_frame', 'LCD_', 'RESP_', 'MAIN_')
CAPSET = ('HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env')
DOOR = ('HOUSING_F_door', 'GROMMET_usbc_F')


def hard(k, X, state, skip=()):
    # the bodies in place, as ../model-v70/p89_b9_ways.py has the two states: 'build' = step 22 (no display module, no cap, no
    # door), 'service' = everything in but the door; leads and keep-outs are not obstacles; the Pi power plug on J2 is out
    out = []
    for b in k.current(X, leads=False, kos=False):
        n = b.name
        if n in DOOR or n in skip or n == 'MAIN_J2_plug_env' or n.startswith('FOOT_'):
            continue
        if state == 'build' and (n.startswith(MODULE) or n in CAPSET):
            continue
        out.append(b)
    return out


def st_key(k, X, y=PY, state='build', holder=False, sides=('L', 'R'), swap=None, grow=0.0):
    # The 2.0 key (shaft 2.4 across, long arm 101, short arm 16) on a clip's screw at (y, z 38): short arm in the screw, the head's
    # top at x +-38.85, elbow at x +-24.9; the long arm swept in the plane of the elbow from pointing back (0 deg) to straight up
    # (90 deg), every 5 deg. 'swap' maps model body names to k.c keys (the plan's temporary bodies stand in for them).
    # grow > 0 thickens the key by that much all round, to show the room it has.
    import math
    k.budget(70)
    swap = swap or {}
    off = () if holder else ('RADAR_HOLDER', 'LD2410C_env_F')
    for side in sides:
        sx = 1.0 if side == 'L' else -1.0
        xe = sx * 24.9
        zone = X.wbox(min(xe, sx * 41.0) - 3.0, max(xe, sx * 41.0) + 3.0, -120.0, 12.0, -50.0, 185.0)
        fx = []
        for b in hard(k, X, state, skip=off):
            t = X.tbm.copy(k.c[swap[b.name]] if b.name in swap else b)
            if not t.boundingBox.intersects(zone.boundingBox):
                continue
            X.sec(t, X.tbm.copy(zone))
            if t.faces.count:
                fx.append((b.name, t))
        def hits(t):
            h = {}
            for nm, f in fx:
                v = X.xv(t, f)
                if v > 0.0005:
                    h[nm] = round(v, 3)
            return h
        short = X.cyl((xe - sx * 1.2, y, PZ), (sx * 38.85 - sx * 1.3, y, PZ), 1.2 + grow)
        head = X.cyl((sx * 40.5, y, PZ), (sx * 38.85, y, PZ), 2.85 + grow)
        print('clip %s, screw at y %.2f, state %s, holder and radar %s, key grown %.1f: head meets %s; short arm meets %s' % (
            side, y, state, 'on' if holder else 'off', grow, hits(head) or 'nothing', hits(short) or 'nothing'))
        free = []; rows = []
        for phi in range(0, 96, 5):
            r = math.radians(phi)
            arm = X.cyl((xe, y, PZ), (xe, y - 101.0 * math.cos(r), PZ + 101.0 * math.sin(r)), 1.2 + grow)
            h = hits(arm)
            if not h:
                free.append(phi)
            else:
                rows.append('%d: %s' % (phi, h))
            if k.late():
                print('time'); break
        runs = []
        for p in free:
            if runs and p - runs[-1][1] == 5:
                runs[-1][1] = p
            else:
                runs.append([p, p])
        print('   free sectors: %s' % ['%d to %d' % (a, b) for a, b in runs])
        for r in rows:
            print('   meets at ' + r)


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'names': st_names, 'head': st_head, 'room': st_room, 'key': st_key}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag=None, **kw):
    L['out']('d14_%s.txt' % (tag or stage), _main, stage, **kw)
# END
