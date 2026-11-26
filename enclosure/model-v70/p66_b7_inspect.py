# Block 7 (brief claude/brief-enclosure-audit-fixes-rest-2026-11-25.md): the parts as they stand at version 75. READ-ONLY.
#   'chin'    the shell's faces square to y near y 4.3 (the chin wall's inner face, D430) with their extent; the bodies set from the
#             touch board (TOUCH_*, KO_touch*, LEAD_TOUCH) with their world boxes
#   'clip'    TOUCH_CLIP_L faces; the box's pilot; the touch board's back and the parts on it
#   'carrier' RESP_CARRIER's four posts: faces and holes
#   'hood'    BME_HOOD faces and pegs; FOAM_bme_top_env; the shell's wall end and boss round it
#   'boxes'   SPKBOX_R's roof corner at (-93.5, -3.7, 82.0); SPKBOX_L's plug pocket walls
# Run: runpy.run_path(D + 'p66_b7_inspect.py')['main'](stage)  -> p66_<stage>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def pr(rows):
    for r in sorted(rows, key=lambda r: (r[0], str(r[1]), str(r[2]))):
        print('   ', r)


def chin(k, X):
    S = X.body('HOUSING_F_front')
    for f in S.faces:
        if f.geometry.surfaceType != k.PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(abs(n[1]) - 1) > 1e-4:
            continue
        p = k.W(f.pointOnFace)
        if 3.5 < p[1] < 5.5 and p[2] < 70:
            ws = [k.W(v.geometry) for v in f.vertices]
            print('   y %.4f n %+.0f %8.2f mm2 x %.2f..%.2f z %.2f..%.2f (bed %.4f)' % (p[1], n[1], f.area * 100, min(w[0] for w in ws), max(w[0] for w in ws),
                                                                         min(w[2] for w in ws), max(w[2] for w in ws), 6.7992 - p[1]))
    for n in X.names():
        if ('TOUCH' in n.upper() or n.startswith('KO_touch')) and not k.BACK.search(n):
            b = X.body(n)
            print('%-24s box %s vol %.3f faces %d visible %s' % (n, k.wbb(X, b), b.volume * 1000, b.faces.count, b.isLightBulbOn))
    print('all names with TOUCH or touch:', [n for n in X.names() if 'touch' in n.lower()])


def clip(k, X):
    b = X.body('TOUCH_CLIP_L')
    print('TOUCH_CLIP_L box %s' % k.wbb(X, b)); pr(k.faces(X, b, (-200, 200, -200, 200, -10, 400), amin=0.05))
    print('holes', k.holes_of(b, rmin=0.5, rmax=4))
    bx = X.body('SPKBOX_L')
    print('SPKBOX_L holes near the clip:', [r for r in k.holes_of(bx, rmin=1.0, rmax=1.5)])
    print('SPKBOX_L faces near the pilot (x 39..52, y -10..-4, z 33..43):'); pr(k.faces(X, bx, (39, 52, -10, -4, 33, 43), amin=0.05))


def carrier(k, X):
    b = X.body('RESP_CARRIER')
    print('RESP_CARRIER box %s' % k.wbb(X, b))
    for r in k.holes_of(b, rmin=1.5, rmax=3.0):
        print('  ', r)


def hood(k, X):
    b = X.body('BME_HOOD')
    print('BME_HOOD box %s faces %d' % (k.wbb(X, b), b.faces.count)); pr(k.faces(X, b, (-200, 200, -200, 200, -10, 400), amin=0.05))
    print('holes', k.holes_of(b, rmin=0.5, rmax=4))
    for n in ('FOAM_bme_top_env', 'FOAM_bme_env', 'BME680_env'):
        print('%s box %s vol %.3f' % (n, k.wbb(X, X.body(n)), X.body(n).volume * 1000))


def boxes(k, X):
    bR = X.body('SPKBOX_R')
    print('SPKBOX_R faces near (-93.5, -3.7, 82.0):'); pr(k.faces(X, bR, (-96, -88, -8, 0, 76, 86), amin=0.05))
    bL = X.body('SPKBOX_L')
    print('SPKBOX_L box %s' % k.wbb(X, bL))
    print('USBA_plug_env box %s' % k.wbb(X, X.body('USBA_plug_env')))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'chin': chin, 'clip': clip, 'carrier': carrier, 'hood': hood, 'boxes': boxes}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p66_%s.txt' % stage, _main, stage)
