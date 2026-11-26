# The close (brief block 6): the last pass's checks run again on the saved version by their own functions, READ-ONLY.
# The last pass's scripts (../model-v70/, read from its folder on the Mac) write their output into that folder and measure
# some distances through TMP_ bodies added to the document. Here each function is called directly: its printed output is
# caught into THIS pass's folder (the last pass's files are only read), and the two helpers that added bodies are replaced by
# ones that measure on temporary bodies, so the document is not touched.
#   old     one function of a last-pass script: main('old', tag, script=, func=, ref=, kw={...}). The output goes to
#           d60_<tag>.txt; with ref (a file of the last close) the two are compared line by line and only the count and the
#           lines that differ are printed (d60_<tag>_cmp.txt)
#   ride    the display module's ride-in (p95's 'ride', with a tag of this version so that nothing cached is read)
#   slide   a box with its driver, its foam and its lead slid onto the base plate (the library's slide, 17 positions), each side
#   cmp     plain: compare a file of this folder with a file of the last close, or (ref './name') with another of this folder
#   clear   drops what the last close left in the library's cache under its own tags and names (p95's rideholder, gridfit and
#           main01 keep their results there by face number or body name, and would hand back version 79's)
#   ls      the names and line counts of this folder's outputs with a given start
# Run: runpy.run_path(D + 'd60_close.py')['main'](stage, tag, **kw)
import runpy, io, contextlib, os, time
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
D70 = L['D70']


def dist_t(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return (round(r.value * 10, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))


def mind_t(k, X, t, fixed):
    best = None
    for nm, f in fixed:
        d = X.mm.measureMinimumDistance(t, f).value * 10.0
        if best is None or d < best[0]:
            best = (round(d, 2), nm)
    return best


def lines(text):
    return [l.rstrip() for l in text.splitlines() if l.strip() and not l.startswith('20') and not l.lstrip().startswith(('time', '%'))]


def compare(new_text, ref, maxd=16, width=210):
    out = []
    if '*' in ref:                                   # the newest of the last pass's files of that name
        import glob
        fs = sorted(glob.glob(D70 + ref), key=os.path.getmtime)
        if fs:
            ref = os.path.basename(fs[-1])
    p = ref if ref.startswith('/') else (D + ref[2:] if ref.startswith('./') else D70 + ref)
    if not os.path.exists(p):
        return ['no file %s in the last pass\'s folder' % ref]
    a = lines(open(p).read()); b = lines(new_text)
    if len(a) == len(b):
        df = [(x, y) for x, y in zip(a, b) if x != y]
        out.append('against %s: %d lines, %d differ' % (ref, len(b), len(df)))
        for x, y in df[:maxd]:
            out.append('   was: ' + x.strip()[:width]); out.append('   now: ' + y.strip()[:width])
        if len(df) > maxd:
            out.append('   ... %d more' % (len(df) - maxd))
    else:
        sa = set(a); sb = set(b)
        gone = [x for x in a if x not in sb]; new = [y for y in b if y not in sa]
        out.append('against %s: %d lines then, %d now; %d only then, %d only now' % (ref, len(a), len(b), len(gone), len(new)))
        for x in gone[:maxd]:
            out.append('   then: ' + x.strip()[:width])
        for y in new[:maxd]:
            out.append('   now:  ' + y.strip()[:width])
    return out


def _old(tag, script, func, ref, kw, sec, setg=None):
    k = L['load'](); X = k.K(); k.budget(sec)
    st0 = X.state()
    m = runpy.run_path(D70 + script)
    g = m[func].__globals__                          # runpy hands back a copy; the functions look their helpers up here
    if 'dist' in g and g['dist'].__code__.co_argcount == 4:
        g['dist'] = dist_t
    if 'mind' in g:
        g['mind'] = mind_t
    for name, val in (setg or {}).items():           # a list of the script cut down, to run one long check in parts
        g[name] = val
    if 'k_' in g:                                    # p58 keeps the library under this name, set by its own main
        g['k_'] = k
    if 'ctmp' in g:
        g['ctmp'] = lambda X_, name, box: L['crop'](X_, name, box)
    kw = dict(kw or {})
    if isinstance(kw.get('pts'), str) and kw['pts'].startswith('@'):      # the positions of the last close, read from its output
        import re
        kw['pts'] = [tuple(float(v) for v in q.groups()) for q in (re.match(r'\s*\(\s*([-\d.]+),\s*([-\d.]+),\s*([-\d.]+)\):', l) for l in open(D70 + kw['pts'][1:])) if q]
    buf = io.StringIO(); t0 = time.time()
    with contextlib.redirect_stdout(buf):
        print(L['stamp'](), 'before', st0)
        m[func](k, X, **kw)
        print(L['stamp'](), 'after', X.state())
    text = buf.getvalue()
    open(D + 'd60_%s.txt' % tag, 'w').write(text)
    res = ['%s %s %s -> d60_%s.txt, %d lines, %.1f s; version %s, modified %s' % (script, func, {q: (v if q != 'pts' else '%d positions' % len(v)) for q, v in kw.items()} or '', tag, len(lines(text)), time.time() - t0, X.state()['version'], X.state()['modified'])]
    if ref:
        res += compare(text, ref)
    open(D + 'd60_%s_cmp.txt' % tag, 'w').write('\n'.join(res) + '\n')
    print('\n'.join(res))


def _ride(tag, leads, ref, sec):
    k = L['load'](); X = k.K(); k.budget(sec)
    P95 = runpy.run_path(D70 + 'p95_close_checks.py')
    keep = P95['_groups'](k, X)
    try:
        res, left = k.K4NS['ride_in'](X, tag, leads=leads)
    finally:
        for g, v in keep.items():
            k.ST[g] = v
    hits = {str(key): v for key, v in res.items() if v and 'no part in the box' not in v}
    text = 'ride-in, the whole module, %s: %d positions done, left %d; positions with an overlap: %s\n' % (
        'with the leads\' parts that ride with it' if leads else 'leads left out', len(res), left, hits if hits else 'none')
    open(D + 'd60_%s.txt' % tag, 'w').write('%s %s\n' % (L['stamp'](), X.state()) + text)
    print(text.strip())
    if ref and left == 0:
        print('\n'.join(compare(text, ref)))


def _slide(tag, side, sec):
    k = L['load'](); X = k.K(); k.budget(sec)
    o = 'R' if side == 'L' else 'L'
    moving = tuple(n for n in ('SPKBOX_' + side, 'SPK_' + side, 'FOAM_spk_%s_env' % side, 'LEAD_SPK_' + side) if X.body(n))
    fixed = tuple(n for n in ('FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'CRADLE_5807', 'PD_5807_env', 'USBA_plug_env', 'USBA_cable_env',
                              'LEAD_USB_RESP', 'SPKBOX_' + o, 'SPK_' + o, 'FOAM_spk_%s_env' % o, 'LEAD_SPK_' + o, 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR') if X.body(n))
    res = k.K4NS['slide'](X, tag, moving=moving, fixed=fixed)
    bad = {str(q): h for q, h in res.items() if h}
    text = 'the %s box slid onto the base plate, moving %s, 17 positions from 50 in front to home, against %s: %d positions read: %s\n' % (
        'left' if side == 'L' else 'right', list(moving), list(fixed), len(res), bad or 'nothing shared at any')
    open(D + 'd60_%s.txt' % tag, 'w').write('%s %s\n' % (L['stamp'](), X.state()) + text)
    print(text.strip())


def main(stage, tag='', script=None, func=None, ref=None, kw=None, sec=66, leads=False, side='L', setg=None):
    if stage == 'old':
        _old(tag, script, func, ref, kw, sec, setg)
    elif stage == 'ride':
        _ride(tag, leads, ref, sec)
    elif stage == 'slide':
        _slide(tag, side, sec)
    elif stage == 'cmp':
        print('%s:' % tag); print('\n'.join(compare(open(D + tag).read(), ref, maxd=(kw or {}).get('maxd', 16))))
    elif stage == 'clear':
        k = L['load']()
        gone = [q for q in list(k.c.keys()) if q in ('close_rideholder', 'close_gridfit', 'close_main01') or (isinstance(q, tuple) and len(q) > 1 and q[1] in ('close79', 'v79s15'))]
        for q in gone:
            del k.c[q]
        print('dropped from the library\'s cache: %d entries of the last close (close79, v79s15, close_rideholder, close_gridfit, close_main01)' % len(gone))
    elif stage == 'ls':
        import glob
        for pre in (kw or {}).get('pre', ()):
            fs = sorted(glob.glob(D + pre + '*.txt'))
            print(pre + ': ' + ', '.join('%s(%d)' % (os.path.basename(f)[len(pre):-4], sum(1 for _ in open(f))) for f in fs))
# END
