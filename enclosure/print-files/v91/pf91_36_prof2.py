# Print files of version 91, block 4: the holes the hole reading flagged, band by band (pf91_tools hprof), on the print file's slice
# and on the re-check's own slice of the same plate (read where it is). No Fusion object.
#   shell(): the shell's four 8.3 pockets with support near their mouths on P3a in ABS.
#   wire():  the boxes' 4.0 wire holes on P1b in PLA (and in ABS for comparison).
import os, json, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
OUT = os.path.join(L['W'], 'out'); SO = os.path.join(L['W'], 'slicer', 'out')


def _flagged(job, thr=0.3, d=None):
    R = json.load(open(os.path.join(OUT, 'holes_%s.json' % job)))
    return [r for r in R if (r['support_mm3'] > thr and (d is None or r['d'] == d))]


def shell(wait=60):
    rows = _flagged('A06_P3a', d=8.3); lst = []
    for r in rows:
        print('shell pocket d %.2f world %s -> %s | bed %s -> %s' % (r['d'], r['world'][0], r['world'][1], r['bed'][0], r['bed'][1]))
        for jd in (os.path.join(SO, 'A06_P3a'), os.path.join(L['RD91'], 'slicer', 'out', 'f2_shell')):
            lst.append({'cmd': 'hprof', 'job': jd, 'A': r['bed'][0], 'B': r['bed'][1], 'd': r['d'], 'step': 0.2})
    L['tools']([('pf91_hprof_shell', 'hprof', lst)], wait)
    print(open(os.path.join(OUT, 'pf91_hprof_shell.txt')).read())


def wire(wait=60):
    rows = _flagged('T02_P1b', d=4.0); lst = []
    for r in rows:
        print('wire hole %s d %.2f world %s -> %s | bed %s -> %s' % (r['part'], r['d'], r['world'][0], r['world'][1], r['bed'][0], r['bed'][1]))
        for jd in (os.path.join(SO, 'T02_P1b'), os.path.join(SO, 'A02_P1b')):
            lst.append({'cmd': 'hprof', 'job': jd, 'A': r['bed'][0], 'B': r['bed'][1], 'd': r['d'], 'step': 0.25})
    L['tools']([('pf91_hprof_wire', 'hprof', lst)], wait)
    print(open(os.path.join(OUT, 'pf91_hprof_wire.txt')).read())
def seg(wait=45):
    """the support lines inside the first of the shell's flagged pockets: their kind and layers."""
    r = _flagged('A06_P3a', d=8.3)[0]
    lst = [{'cmd': 'hseg', 'job': os.path.join(SO, 'A06_P3a'), 'A': r['bed'][0], 'B': r['bed'][1], 'd': r['d'], 'show': 25}]
    L['tools']([('pf91_hseg_shell', 'hseg', lst)], wait)
    print(open(os.path.join(OUT, 'pf91_hseg_shell.txt')).read())
# END pf91_36_prof2.py
