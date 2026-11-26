# Block 1: the touch clips' screws and what stands round them. READ-ONLY (temporary bodies only).
#   names    every body of the unit, by name
#   head     an M3 x 8 button head (5.7 across, 1.65 high) drawn on each clip's screw, the screw's shank and its key, against every
#            body of the unit: shared volume as modelled, and with the screw at either end of the clip's slot (0.4 forward, 0.4 back)
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


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'names': st_names, 'head': st_head, 'room': st_room}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag=None, **kw):
    L['out']('d14_%s.txt' % (tag or stage), _main, stage, **kw)
# END
