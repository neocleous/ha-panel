# Block 5, AA-A3: the window of the shell's way down, read directly (k4a's way_in at every body is slow: p52 did 112 of 2,128
# positions a call). The plate unit lifted in from below, b behind its place (world -y), by h (world -z), against the shell
# cropped to three places; the three stops of record (2026-11-15: 1.15 corners / 1.05 tongues / 1.50 door frame):
#   heads: DRV_screw_heads_env against the shell's front corners (|x| > 75, y -4..6, z 0..62)
#   tongues: FLOOR_PLATE against the chin (|x| < 60, y -3..8, z 0..12)
#   frame: SPKBOX_L, SPKBOX_R against the door frame's lower ends (y -58..-48, z 0..40)
# READ-ONLY (temporary bodies only). which: 'model' (HOUSING_F_front) or a k.c key holding a temporary shell.
# Run: runpy.run_path(D + 'p52b_window.py')['main'](which)  -> p52b_<which>.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
CASES = {
    'heads': (['DRV_screw_heads_env'], [(75, 110, -4, 6, 0, 62), (-110, -75, -4, 6, 0, 62)],
              (0.55, 0.6, 0.65, 0.7, 0.8, 1.0, 1.1, 1.15, 1.2), [0.5 * i for i in range(0, 125)]),
    'tongues': (['FLOOR_PLATE'], [(-100, 100, -3, 8, 0, 12)], (0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2), [0.25 * i for i in range(0, 17)]),
    'frame': (['SPKBOX_L', 'SPKBOX_R'], [(-110, 110, -58, -48, 0, 85)], (1.45, 1.5, 1.55, 1.6, 1.65), [1.0 * i for i in range(0, 31)]),
}


def _main(which, cases):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    sh = X.body('HOUSING_F_front') if which == 'model' else k.c[which]
    for c in cases:
        names, boxes, bs, hs = CASES[c]
        crops = []
        for bx in boxes:
            t = X.wbox(*bx); X.sec(t, X.tbm.copy(sh)); crops.append(t)
        # the movers cropped to the part that can meet the crops (the whole base plate, with its 475 holes, is slow to move)
        near = {'heads': None, 'tongues': (-100, 100, -6, 9, -1, 15), 'frame': (-100, 100, -53.0, -47.0, -1, 85)}[c]
        movers = []
        for n in names:
            m = X.tbm.copy(X.body(n))
            if near:
                X.sec(m, X.wbox(*near))
            movers.append(m)
        for b in bs:
            hit = []
            for h in hs:
                v = 0.0
                for m in movers:
                    t = X.move(X.tbm.copy(m), 0.0, -b, -h)
                    for cr in crops:
                        v += X.xv(t, cr)
                if v > 0.0005:
                    hit.append((h, round(v, 4)))
            print('%-8s b %.2f: %s' % (c, b, ('meets at lifts %s' % hit) if hit else 'clear at every lift'))
    print(L['stamp'](), 'after', X.state())


def main(which='model', cases=('heads', 'tongues', 'frame')):
    L['out']('p52b_%s_%s.txt' % (which, '_'.join(cases)), _main, which, cases)
