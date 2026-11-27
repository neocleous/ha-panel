# Block 5 (D471, PR44): the gap between the hood's boss and the shell's rear wall, filled along the boss. Builds temporary
# bodies and keeps them in k.c; NOTHING IS PUT INTO THE DOCUMENT here (d21_put.py does that).
#
# The place (d50): the hood's boss is a round pin 6.0 across in the shell, lying level at z 100, its axis leaning 22 deg from x
# in the x-y plane; its free end (where the hood's ear seats) looks toward the middle and the back. Behind it (toward -y, which
# is up in the shell's print) stand the rear wall's inner face (y -53.6) and the sloping end face of the magnet's boss. Between
# the pin and these lies a gap 0.9 to about 3 high, which fills with support.
#   the fill   everything straight above the pin in the print (between the two planes z 97 and z 103 that touch the pin's sides,
#              from the level of its axis toward the wall) that is air today and joined to the gap, from the pin's root to a
#              plane SETBACK behind the pin's end face and parallel to it. The pin and the fill together stand as one block
#              with upright sides under the wall; nothing hangs. With it goes the slit, up to 0.75 wide, between the pin's
#              back end and the slanting end wall it grows from (d50: the pin's back end is cut square, the wall slants).
#              Nothing is added within PILOT_KEEP of the axis.
#   not filled the air beyond the pin's end face: the hood's ear sits there.
# Keys: b5_fill (the added material), b5_shell (the shell with it), b5_shell_before (the shell as it stood).
# Stages: build; hood (the added material against the hood at home and along its way off and out, the screw, the driver's
# line, the neighbours); main(stage) -> d51_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
SETBACK = 0.5            # the fill ends this far behind the pin's end face
S0 = -8.0                # along the axis from the end face's middle: where the fill's box begins (inside the block the pin grows from)
DB = 6.6                 # from the axis toward the wall: the box's reach (it ends inside the wall)
HALF = 3.0               # half the pin's width
PILOT_KEEP = 1.2         # nothing is added within this of the axis: the pilot (0.8) stays as it is
HN = (0.11394, 0.09756, 0.98869)      # the hood's own up (its pins' axis), as the last pass's p71 and p97 have it
HU = (0.7593, 0.6497, 0.0)            # level, toward the middle, away from the wall (p71)


def boss(k, X, sh):
    """The pin's axis (unit, x positive), the middle of its end face, its radius - read from the shell's faces."""
    cyl = None
    for f in sh.faces:
        g = f.geometry
        if g.surfaceType == CYL and abs(g.radius * 10 - 3.0) < 0.005:
            a = k.unit(k.wv(g.axis)); o = k.W(g.origin)
            if abs(a[2]) < 0.01 and abs(o[2] - 100.0) < 0.2 and -66 < o[0] < -54 and -55 < o[1] < -44:
                cyl = (a if a[0] > 0 else (-a[0], -a[1], -a[2]), o)
    if cyl is None:
        raise RuntimeError('the hood\'s boss not found')
    a, o = cyl
    end = None
    for f in sh.faces:
        if f.geometry.surfaceType != PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.unit(k.wv(nv))
        if abs(n[0] - a[0]) < 0.002 and abs(n[1] - a[1]) < 0.002 and abs(n[2]) < 0.002:
            c = k.W(f.centroid)
            off = [c[i] - o[i] for i in range(3)]; s = sum(off[i] * a[i] for i in range(3))
            r = math.sqrt(max(0.0, sum(q * q for q in off) - s * s))
            if r < 0.05:
                end = (c, f.area * 100)
    if end is None:
        raise RuntimeError('the boss\'s end face not found')
    return a, end[0], end[1]


def pt(E, a, bp, s, b, dz=0.0):
    return (E[0] + a[0] * s + bp[0] * b, E[1] + a[1] * s + bp[1] * b, E[2] + dz)


def _build(half=HALF, setback=SETBACK):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    sh = X.body('HOUSING_F_front')
    a, E, ea = boss(k, X, sh)
    bp = (a[1], -a[0], 0.0)                                   # square to the axis, level, toward the wall (-y)
    print('pin: axis %s (%.2f deg from x), end face\'s middle %s (%.3f mm2); toward the wall %s' % (k.r2(a, 4), math.degrees(math.atan2(-a[1], a[0])), k.r2(E, 3), ea, k.r2(bp, 4)))
    s1 = -setback
    cen = pt(E, a, bp, (S0 + s1) / 2.0, DB / 2.0)
    box = X.obox(cen, a, bp, s1 - S0, DB, 2 * half)
    v0 = X.vol(box)
    X.dif(box, X.cyl(pt(E, a, bp, S0 - 1.0, 0.0), pt(E, a, bp, 1.0, 0.0), PILOT_KEEP))   # the pilot's place stays open
    v1 = X.vol(box)
    X.dif(box, X.tbm.copy(sh))
    print('box %.1f long, %.1f toward the wall, %.1f wide: %.3f; less the pilot\'s place %.3f; less the shell %.3f, lumps %d' % (s1 - S0, DB, 2 * half, v0, v1, X.vol(box), box.lumps.count))
    keep = None; kept = 0
    for lp in box.lumps:
        t = X.tbm.copy(lp); bb = k.r2(k.wbb(X, t), 2); v = X.vol(t)
        take = bb[3] > -53.45 and bb[2] < -53.55 and v > 0.01   # reaches from the pin's side of the gap to the rear wall
        print('   lump %9.4f mm3, world box %s: %s' % (v, bb, 'the gap, taken' if take else 'left'))
        if take:
            keep = t if keep is None else X.uni(keep, t); kept += 1
    if keep is None:
        raise RuntimeError('no gap found')
    new = X.tbm.copy(sh)
    X.uni(new, X.tbm.copy(keep))
    k.c['b5_fill'] = keep; k.c['b5_shell'] = new; k.c['b5_shell_before'] = X.tbm.copy(sh)
    print('fill: %.4f mm3 in %d lump(s), world box %s, faces %d' % (X.vol(keep), kept, k.r2(k.wbb(X, keep), 2), keep.faces.count))
    print('shell: %.3f -> %.3f, lumps %d -> %d, closed skins %d -> %d (more would mean a hollow shut in), faces %d -> %d' % (
        sh.volume * 1000, X.vol(new), sh.lumps.count, new.lumps.count, sh.shells.count, new.shells.count, sh.faces.count, new.faces.count))
    # the new shell's faces round the place: any on the box's far side or its root end would mean the box ended in air
    far = 0; root = 0; small = []
    zone = X.wbox(-70.0, -55.0, -58.0, -44.0, 95.0, 105.0).boundingBox
    for f in new.faces:
        if not f.boundingBox.intersects(zone):
            continue
        c = k.W(f.pointOnFace)
        if not (-70 < c[0] < -55 and -58 < c[1] < -44 and 95 < c[2] < 105):
            continue
        off = [c[i] - E[i] for i in range(3)]
        s = sum(off[i] * a[i] for i in range(3)); b = sum(off[i] * bp[i] for i in range(3))
        if f.geometry.surfaceType == PLN:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.unit(k.wv(nv))
            if abs(abs(sum(n[i] * bp[i] for i in range(3))) - 1) < 1e-3 and abs(b - DB) < 1e-3:
                far += 1
            if abs(abs(sum(n[i] * a[i] for i in range(3))) - 1) < 1e-3 and abs(s - S0) < 1e-3:
                root += 1
        if f.area * 100 < 0.05:
            small.append('%.4f mm2 at %s' % (f.area * 100, k.r2(c, 2)))
    print('new shell round the place: faces on the box\'s far side %d, on its root end %d (both must be 0); faces under 0.05 mm2: %s' % (far, root, small or 'none'))
    smb = sum(1 for f in sh.faces if f.area * 100 < 0.05); smn = sum(1 for f in new.faces if f.area * 100 < 0.05)
    print('faces under 0.05 mm2 in the whole shell: %d -> %d' % (smb, smn))
    for f in keep.faces:
        g = f.geometry; c = k.r2(k.W(f.pointOnFace), 2)
        if g.surfaceType == PLN:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            print('   fill face: flat %.3f mm2, normal %s, at %s' % (f.area * 100, k.r2(k.unit(k.wv(nv)), 3), c))
        elif g.surfaceType == CYL:
            print('   fill face: round r %.3f, %.3f mm2, at %s' % (g.radius * 10, f.area * 100, c))
        else:
            print('   fill face: other (%d), %.3f mm2, at %s' % (g.surfaceType, f.area * 100, c))
    print(L['stamp'](), 'after', X.state())


def _hood():
    k = L['load'](); X = k.K(); k.budget(60)
    print(L['stamp'](), 'before', X.state())
    F = k.c['b5_fill']
    hood = X.body('BME_HOOD')

    def d(a, b):
        r = X.mm.measureMinimumDistance(a, b)
        return r.value * 10.0, k.r2(k.W(r.positionOne), 2)

    print('the added material (%.3f mm3) at home against:' % X.vol(F))
    fb = k.wbb(X, F)
    for ob in k.current(X, leads=True):
        if ob.name == 'HOUSING_F_front':
            continue
        w = k.wbb(X, ob)
        if w[0] - 6 > fb[1] or w[1] + 6 < fb[0] or w[2] - 6 > fb[3] or w[3] + 6 < fb[2] or w[4] - 6 > fb[5] or w[5] + 6 < fb[4]:
            continue
        if ob.name == 'SCREWS_M2x6_env':
            for lp in ob.lumps:
                t = X.tbm.copy(lp); dd, p = d(F, t)
                if dd < 8:
                    print('   a screw of %-18s %.3f, on the fill at %s; shared %.4f' % (ob.name, dd, p, X.xv(X.tbm.copy(F), t)))
            continue
        dd, p = d(F, ob)
        if dd < 6.0:
            print('   %-28s %.3f, on the fill at %s%s' % (ob.name, dd, p, ('; shared %.4f' % X.xv(X.tbm.copy(F), X.tbm.copy(ob))) if dd < 0.0005 else ''))
    n = k.unit(HN); u = k.unit(HU)
    H = X.tbm.copy(hood)
    rows = []
    for Lf in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0):
        t = X.move(X.tbm.copy(H), Lf * n[0], Lf * n[1], Lf * n[2]); rows.append('%.1f: %.2f' % (Lf, d(F, t)[0]))
    print('hood lifted along its pegs, the fill to the hood: %s' % ', '.join(rows))
    for Lf in (2.1, 3.5):
        rows = []
        for m in (0.5, 1.0, 2.0, 4.0, 8.0, 12.0):
            t = X.move(X.tbm.copy(H), Lf * n[0] + m * u[0], Lf * n[1] + m * u[1], Lf * n[2] + m * u[2]); rows.append('%.1f: %.2f' % (m, d(F, t)[0]))
        print('lift %.1f, then toward the middle: %s' % (Lf, ', '.join(rows)))
    rows = []
    for s in (0.5, 1, 2, 4, 8, 12, 16, 24, 32, 48, 60):
        t = X.move(X.tbm.copy(H), 3.5 * HN[0] + s, 3.5 * HN[1], 3.5 * HN[2]); rows.append('%g: %.2f' % (s, d(F, t)[0]))
    print('lift 3.5, across (p97\'s way): %s' % ', '.join(rows))
    rows = []
    for s in (48.0, 60.0):
        for b in (5, 15, 30, 60):
            t = X.move(X.tbm.copy(H), 3.5 * HN[0] + s, 3.5 * HN[1] - b, 3.5 * HN[2]); rows.append('%g/%g: %.2f' % (s, b, d(F, t)[0]))
    print('lift 3.5, across / back out through the door opening: %s' % ', '.join(rows))
    # the driver's line: straight out of the screw's head along the pin's axis
    sh = X.body('HOUSING_F_front'); a, E, ea = boss(k, X, k.c['b5_shell_before'])
    for r in (2.0, 4.0, 8.0):
        bar = X.cyl((E[0] + a[0] * 0.2, E[1] + a[1] * 0.2, E[2]), (E[0] + a[0] * 150.0, E[1] + a[1] * 150.0, E[2]), r)
        print('a bar %.0f across along the pin\'s axis from 0.2 beyond its end face, 150 long: the fill to it %.3f' % (2 * r, d(F, bar)[0]))
    print(L['stamp'](), 'after', X.state())


def main(stage='build', **kw):
    L['out']('d51_%s.txt' % stage, {'build': _build, 'hood': _hood}[stage], **kw)
# END
