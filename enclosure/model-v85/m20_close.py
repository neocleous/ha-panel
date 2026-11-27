# Block 4, the close: read on the saved version. READ-ONLY (temporary bodies only). Outputs go to THIS pass's folder; the last
# pass's scripts are called by their own functions and their folder is only read.
#   matrix   the interference table by the method of the last three passes (c3k.K4NS['matrix']): call again until FINISHED;
#            m20_matrix_<tag>.txt and .json
#   compare  pairs new, gone and changed by more than 0.001 mm3 between version 85's table (../drivers_seat_v80/d02_matrix_ds7.json)
#            and this one
#   guards   counts, and the 17 guard volumes by both readings against version 85's (the brief's table)
#   walk     the shell's way down (../model-v80/d27_fits.st_walk): case, side, behind, to the side
#   slide    a box with its driver, foam and lead slid onto the base plate (c3k.K4NS['slide'], 17 positions; as d60_close._slide)
#   tabkey   the 2.0 key on each box-top screw (k.line, the key's two sections, every 5 along it), from the head's top outward on
#            the screw's line, against every body of the unit but leads; with the boxes of the model and with their _v85 copies
# Run: L.checked('m20_close.py', sha)['main'](stage, tag, **kw)  -> m20_<stage>_<tag>.txt
import runpy, time, json, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
D80 = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'm00_lib.py')
THRESH = 0.0005


def st_matrix(k, X, tag='bm', sec=55, fresh=True):
    q = ('k4m', tag)
    if fresh and q not in k.c:
        h = k.hc(); n = 0
        for key in list(h.keys()):
            if isinstance(key, tuple) and key and key[0] in ('tc', 'tile'):
                del h[key]; n += 1
        print('dropped %d cached copies and slabs before a fresh table' % n)
    t0 = time.time(); k.budget(sec)
    res, left, nb = k.K4NS['matrix'](X, tag)
    print('%s  tag %s: bodies %d, pairs done %d, left this call %d, %.1f s' % (L['stamp'](), tag, nb, len(res), left, time.time() - t0))
    if left == 0:
        nz = {'%s | %s' % p: v for p, v in res.items() if abs(v) > THRESH}
        print('FINISHED: %d pairs, %d not zero (above %.4f mm3)' % (len(res), len(nz), THRESH))
        L['jdump']('m20_matrix_%s.json' % tag, {'tag': tag, 'read': L['stamp'](), 'bodies': nb, 'pairs': len(res), 'state': X.state(), 'not_zero': dict(sorted(nz.items()))})


def _norm(d):
    o = {}
    for p, v in d.items():
        a, b = [s.strip() for s in p.split('|')]
        o[tuple(sorted((a, b)))] = v
    return o


def st_compare(k, X, a=D80 + 'd02_matrix_ds7.json', b='bm'):
    A = _norm(json.load(open(a))['not_zero']); B = _norm(json.load(open(D + 'm20_matrix_%s.json' % b))['not_zero'])
    print('version 85 (%s): %d pairs not zero; this table (%s): %d' % (a.split('/')[-1], len(A), b, len(B)))
    for p in sorted(set(B) - set(A)):
        print('NEW      %-58s %12.4f' % (' | '.join(p), B[p]))
    for p in sorted(set(A) - set(B)):
        print('GONE     %-58s %12.4f' % (' | '.join(p), A[p]))
    for p in sorted(set(A) & set(B)):
        if abs(A[p] - B[p]) > 0.001:
            print('CHANGED  %-58s %12.4f -> %12.4f' % (' | '.join(p), A[p], B[p]))
    print('same pairs, same volumes within 0.001: %d' % sum(1 for p in set(A) & set(B) if abs(A[p] - B[p]) <= 0.001))


def st_guards(k, X):
    st = X.state(); names = X.names(); cur = k.current(X, leads=True)
    df = X.doc.dataFile
    kinds = {}
    for b in cur:
        n = b.name
        q = 'printed' if n in L['PRINTED'] else 'lead' if n.startswith('LEAD_') else 'keep-out' if n.startswith('KO_') else 'bought or envelope'
        kinds[q] = kinds.get(q, 0) + 1
    print('version %d of %d, modified %s; bodies %d, visible %d, in the unit %d %s; _v79 %d, _v85 %d; TMP_ %d' % (
        df.versionNumber, df.latestVersionNumber, X.doc.isModified, st['bodies'], st['visible'], len(cur), kinds,
        sum(1 for n in names if n.endswith('_v79')), sum(1 for n in names if n.endswith('_v85')), sum(1 for n in names if n.startswith('TMP_'))))
    bad = 0
    for n in L['PRINTED']:
        b = X.body(n); vp = b.volume * 1000.0; vh = L['vhi'](b); rp, rh = L['GUARD85'][n]
        same = abs(vp - rp) < 0.0015 and abs(vh - rh) < 0.0015
        if not same and n not in L['MAY_CHANGE']:
            bad += 1
        print('%-16s %13.3f %13.3f | version 85 %13.3f %13.3f | %s' % (n, vp, vh, rp, rh, 'same' if same else ('changed (may)' if n in L['MAY_CHANGE'] else 'CHANGED: MAY NOT')))
    print('printed parts that changed and may not: %d' % bad)
    for n in ('SCREWS_M2x6_env', 'SCREWS_M2x6_env_v85', 'SPKBOX_L_v85', 'SPKBOX_R_v85'):
        b = X.body(n)
        print('%-22s %12.3f / %12.3f, lumps %d, visible %s' % (n, b.volume * 1000, L['vhi'](b), b.lumps.count, b.isLightBulbOn))


def st_walk(k, X, case='boxes', side='L', bs=(0.95, 1.3, 1.6), s=0.0, sec=70):
    F27 = runpy.run_path(D80 + 'd27_fits.py')
    F27['st_walk'](k, X, case=case, side=side, bs=bs, s=s, sec=sec)


def st_slide(k, X, side='L', tag='bm', sec=66):
    k.budget(sec)
    o = 'R' if side == 'L' else 'L'
    moving = tuple(n for n in ('SPKBOX_' + side, 'SPK_' + side, 'FOAM_spk_%s_env' % side, 'LEAD_SPK_' + side) if X.body(n))
    fixed = tuple(n for n in ('FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'CRADLE_5807', 'PD_5807_env', 'USBA_plug_env', 'USBA_cable_env',
                              'LEAD_USB_RESP', 'SPKBOX_' + o, 'SPK_' + o, 'FOAM_spk_%s_env' % o, 'LEAD_SPK_' + o, 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR') if X.body(n))
    res = k.K4NS['slide'](X, tag + side, moving=moving, fixed=fixed)
    bad = {str(q): h for q, h in res.items() if h}
    print('the %s box slid onto the base plate, moving %s, against %s: %d positions read: %s' % (
        'left' if side == 'L' else 'right', list(moving), list(fixed), len(res), bad or 'nothing shared at any'))


def st_tabkey(k, X, sides=('L', 'R')):
    k.budget(72)
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        u = (-0.172 * sx, -0.985, 0.0)
        mouth = (58.67 * sx, -0.06, 80.0)
        seat = tuple(mouth[i] + u[i] * 4.16 for i in range(3))            # the tab's rear face on the screw's line (m10_stack_c3)
        top = tuple(seat[i] + u[i] * 1.65 for i in range(3))              # the head's top (ISO 7380, 1.65 high)
        for use_copy in (False, True):
            hard = []
            for b in k.current(X, leads=False, kos=False):
                if b.name in ('SCREWS_M2x6_env', 'DRV_screw_heads_env'):
                    continue
                if use_copy and b.name in ('SPKBOX_L', 'SPKBOX_R'):
                    hard.append(X.body(b.name + '_v85')); continue
                hard.append(b)
            r = k.line(X, top, u, k.KEY20, hard)
            print('box-top screw %s, head top %s, key 2.0 on the line %s, boxes %s: %s; nearest beyond the head %s' % (
                s, k.r2(top, 2), k.r2(u, 3), 'version 85 (_v85)' if use_copy else 'as they stand', k.fm(r), r['rows']))
            if k.late():
                print('time'); return


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    try:
        {'matrix': st_matrix, 'compare': st_compare, 'guards': st_guards, 'walk': st_walk, 'slide': st_slide, 'tabkey': st_tabkey}[stage](k, X, **kw)
    finally:
        for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
            b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m20_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
