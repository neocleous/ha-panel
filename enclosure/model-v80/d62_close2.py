# The close (brief block 6): this pass's own closing checks, read on the saved version. READ-ONLY (temporary bodies only).
#   total   every body this pass changed against its hidden copy of version 79: what was added and removed in all (volumes,
#           lumps, the box of all of it). New bodies are named.
#   outer   the outer skin: what of each changed printed body lies outside the cloth reference (REF_F_outer, the last passes'
#           method c3.outside), now and on its copy of version 79. The same volume in the same lumps = nothing outside changed.
#           Then what this pass added to or took from each body within 'near' of the reference's own surface (a shell of the
#           reference 2 x near thick): volumes, to show how near the changes come to the skin from inside.
#   leads   every lead of the unit against every body this pass changed: the smallest distance now and with that body's copy of
#           version 79 in its place, where either is under 'lim'; and the leads this pass changed against all bodies
# Run: runpy.run_path(D + 'd62_close2.py')['main'](stage, tag)  -> d62_<stage>_<tag>.txt
import runpy, sys
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
CHANGED = ('HOUSING_F_front', 'FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'RESP_CARRIER',
           'SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'SCREWS_M2x6_env', 'LEAD_SPK_L', 'LEAD_SPK_R', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR')
NEW = ('FOAM_spk_L_env', 'FOAM_spk_R_env')
PRINTED_CH = CHANGED[:7]


def dd(X, a, b):
    """added (a less b) and removed (b less a) as temporary bodies"""
    add = X.tbm.copy(a); X.dif(add, X.tbm.copy(b))
    rem = X.tbm.copy(b); X.dif(rem, X.tbm.copy(a))
    return add, rem


def st_total(k, X):
    print('%-20s %12s %12s | %10s %5s | %10s %5s | box of all that changed' % ('body', 'now', 'version 79', 'added', 'lumps', 'removed', 'lumps'))
    for n in CHANGED:
        b = X.body(n); o = X.body(n + '_v79')
        add, rem = dd(X, b, o)
        la = X.lumps(add, maxv=1e9) if add.faces.count else []; lr = X.lumps(rem, maxv=1e9) if rem.faces.count else []
        bx = [q[1] for q in la + lr if q[1]]
        box = [round(fn(q[i] for q in bx), 1) for i, fn in ((0, min), (1, max), (2, min), (3, max), (4, min), (5, max))] if bx else []
        print('%-20s %12.3f %12.3f | %10.3f %5d | %10.3f %5d | %s' % (n, b.volume * 1000, o.volume * 1000, sum(q[0] or 0 for q in la), len(la), sum(q[0] or 0 for q in lr), len(lr), box))
    for n in NEW:
        b = X.body(n)
        print('%-20s %12.3f   new in this pass, lumps %d, visible %s, box %s' % (n, b.volume * 1000, b.lumps.count, b.isLightBulbOn, k.r2(k.wbb(X, b), 1)))


def st_outer(k, X, near=1.0, names=None, pieces=True):
    ref = X.body('REF_F_outer'); names = names or PRINTED_CH
    print('cloth reference REF_F_outer: %.3f mm3, lumps %d, box %s' % (ref.volume * 1000, ref.lumps.count, k.r2(k.wbb(X, ref), 1)))
    for n in (names if pieces != 'only' else ()):
        row = []
        for nm in (n, n + '_v79'):
            t = X.tbm.copy(X.body(nm)); X.dif(t, X.tbm.copy(ref))
            row.append((round(X.vol(t), 3), t.lumps.count) if t.faces.count else (0.0, 0))
        print('%-18s outside the reference: now %.3f mm3 in %d lump(s); version 79 %.3f in %d%s' % (n, row[0][0], row[0][1], row[1][0], row[1][1], '' if row[0] == row[1] else '   DIFFERENT'))
    # a shell of the reference's surface: the reference less itself drawn in by 'near' is not to be had from a temporary body,
    # so the changes are read against the reference's faces instead: the smallest distance of what was added or removed
    faces = [f for f in ref.faces]
    print('reference faces: %d' % len(faces))
    for n in (names if pieces else ()):
        add, rem = dd(X, X.body(n), X.body(n + '_v79'))
        for lab, t in (('added', add), ('removed', rem)):
            if not t.faces.count:
                print('%-18s %-8s nothing' % (n, lab)); continue
            best = None
            for lp in t.lumps:
                c = X.tbm.copy(lp)
                # inside the reference the body-to-body distance is 0: read the distance to its faces
                dmin = None
                cb = c.boundingBox
                for f in faces:
                    fb = f.boundingBox
                    if (fb.minPoint.x - 0.3 > cb.maxPoint.x or fb.maxPoint.x + 0.3 < cb.minPoint.x or fb.minPoint.y - 0.3 > cb.maxPoint.y or
                            fb.maxPoint.y + 0.3 < cb.minPoint.y or fb.minPoint.z - 0.3 > cb.maxPoint.z or fb.maxPoint.z + 0.3 < cb.minPoint.z):
                        continue
                    r = X.mm.measureMinimumDistance(c, f); d = r.value * 10.0
                    if dmin is None or d < dmin[0]:
                        dmin = (d, k.r2(k.W(r.positionOne), 1))
                if dmin and (best is None or dmin[0] < best[0]):
                    best = (round(dmin[0], 3), round(X.vol(c), 3), dmin[1])
            print('%-18s %-8s nearest to the reference\'s surface: %s' % (n, lab, ('%.3f (a piece of %.3f mm3, at %s)' % best) if best else 'more than 3 from every face of it'))


def st_leads(k, X, lim=2.0):
    k.budget(70)
    leads = [b for b in k.current(X, leads=True) if b.name.startswith('LEAD_')]
    print('leads in the unit: %d' % len(leads))
    done = k.c.setdefault('d62_leads_v%d' % X.state()['version'], {})
    for ld in leads:
        if ld.name in done:
            continue
        if k.late():
            print('time: call again'); break
        lb = ld.boundingBox; rows = []
        for n in CHANGED + NEW:
            if n == ld.name:
                continue
            b = X.body(n); o = X.body(n + '_v79')
            e = lim / 10.0 + 0.05
            def far(q):
                w = q.boundingBox
                return (w.minPoint.x - e > lb.maxPoint.x or w.maxPoint.x + e < lb.minPoint.x or w.minPoint.y - e > lb.maxPoint.y or
                        w.maxPoint.y + e < lb.minPoint.y or w.minPoint.z - e > lb.maxPoint.z or w.maxPoint.z + e < lb.minPoint.z)
            dn = None if far(b) else X.mm.measureMinimumDistance(ld, b).value * 10.0
            do = None if (o is None or far(o)) else X.mm.measureMinimumDistance(X.body(ld.name + '_v79') or ld, o).value * 10.0
            if (dn is not None and dn < lim) or (do is not None and do < lim):
                vn = X.xv(X.tbm.copy(ld), X.tbm.copy(b)) if dn is not None and dn < 0.0005 else 0.0
                rows.append('%s now %s%s, version 79 %s' % (n, 'more than %.1f' % lim if dn is None else '%.3f' % dn, (' (shared %.3f)' % vn) if vn > 0.0005 else '',
                                                           'not there' if o is None else ('more than %.1f' % lim if do is None else '%.3f' % do)))
        done[ld.name] = rows
    for ld in leads:
        if ld.name in done:
            print('%-18s %s' % (ld.name, '; '.join(done[ld.name]) or 'no changed body within %.1f, now or at version 79' % lim))
    print('read %d of %d' % (len(done), len(leads)))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'total': st_total, 'outer': st_outer, 'leads': st_leads}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d62_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
