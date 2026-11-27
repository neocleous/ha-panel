# Print files of version 91, block 4: the stop rule (D507, D542). No Fusion object. Everything runs in background processes
# (pf91_tools.py; the re-check's r91_lin.py for the index the hole reading needs), started here and read on a later call.
#   gsum():  every print file's slice and every re-check slice it is compared with, summarised (pf91_tools gsum).
#   gcmp():  each pair compared: identity of the G-code; each part's own lines in all and layer by layer; its level faces.
#   lin():   the index (arcs made straight) of each print file's slice, for the hole reading.
#   holes(): every round hole of every part on its plate's own slice.   poll(prefix): the state of the background runs.
import os, json, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
H = L['HOME']; W = L['W']; OUT = os.path.join(W, 'out'); SO = os.path.join(W, 'slicer', 'out')
P1B = [['spkbox_L', 'spkbox_L', [-50, -20, 0]], ['spkbox_R', 'spkbox_R', [50, -20, 0]], ['clip_1', 'clip_L', [-37, 45, 0]], ['clip_2', 'clip_L', [-25, 45, 0]]]
P2 = [['carrier', 'carrier', [-38, 0, 0]], ['cradle', 'cradle', [47, -38, 0]], ['bme_hood', 'bme_hood', [47, 42, 0]]]
P7 = [['clamp_L', 'clamp_L', [-20, 60, 0]], ['clamp_R', 'clamp_R', [20, 60, 0]], ['holder', 'holder', [0, -60, 0]]]
# my job -> (parts on it, [(label, re-check look, re-check job, my part, its part)])
PAIRS = {
    'A00_adh': (None, [('adhesion test', 'print_recheck_v91', 'f2_chin8', '_plate', '_plate')]),
    'A01_P1a': (None, [('P1a base plate', 'print_recheck_v85', 'f2_base', '_plate', '_plate')]),
    'A02_P1b': (P1B, [('P1b', 'print_recheck_v91', 'p_P1b_clips', p[0], p[0]) for p in P1B]),
    'A03_P2': (P2, [('P2', 'print_recheck_v85', 'p_P2_noclip', p[0], p[0]) for p in P2]),
    'A04_P7': (P7, [('P7', 'print_recheck_v91', 'p_P7_clamps_holder', p[0], p[0]) for p in P7]),
    'A05_P3b': (None, [('P3b screen plate', 'print_recheck_v79', 'f2_screen', '_plate', '_plate')]),
    'A06_P3a': (None, [('P3a shell', 'print_recheck_v91', 'f2_shell', '_plate', '_plate')]),
    'A07_P5': (None, [('P5 slab', 'print_recheck_v79', 'f2_slab', '_plate', '_plate')]),
    'A08_P4a': (None, [('P4a cap', 'print_recheck_v79', 'f2_cap', '_plate', '_plate')]),
    'A09_P4b': (None, [('P4b grommet', 'print_recheck_v79', 'f2_grommet', '_plate', '_plate')]),
    'A10_P6': (None, [('P6 door', 'print_recheck_v91', 'f2_door', '_plate', '_plate')]),
    'T01_P1a': (None, [('PLA P1a', 'print_recheck_v85', 'pl_base', '_plate', '_plate')]),
    'T02_P1b': (P1B, [('PLA P1b', 'print_recheck_v91', 'p_P1b_clips_pla', p[0], p[0]) for p in P1B]),
    'T03_P2': (P2, [('PLA P2', 'print_recheck_v85', 'p_P2_noclip_pla', p[0], p[0]) for p in P2]),
    'T04_P7': (P7, [('PLA P7 clamp L', 'print_recheck_v91', 'pl_clampL', 'clamp_L', '_plate'), ('PLA P7 clamp R', 'print_recheck_v91', 'pl_clampR', 'clamp_R', '_plate'),
                    ('PLA P7 holder', 'print_recheck_v79', 'pl_holder', 'holder', '_plate')]),
    'T05_P3b': (None, [('PLA P3b', 'print_recheck_v79', 'pl_screen', '_plate', '_plate')]),
    'T06_P3a': (None, [('PLA P3a', 'print_recheck_v91', 'pl_shell', '_plate', '_plate')]),
    'T07_P5': (None, [('PLA P5', 'print_recheck_v79', 'pl_slab', '_plate', '_plate')]),
    'T08_P4a': (None, [('PLA P4a', 'print_recheck_v79', 'pl_cap', '_plate', '_plate')]),
    'T09_P4b': (None, [('PLA P4b', 'print_recheck_v79', 'pl_grommet', '_plate', '_plate')]),
    'T10_P6': (None, [('PLA P6', 'print_recheck_v91', 'pl_door', '_plate', '_plate')]),
}
# the parts and places each plate's holes are read for (bed place = the matrix of record and the object's place on the plate)
SINGLE = {'A00_adh': ('shell_chin8', [0, -30, 0]), 'A01_P1a': ('base', [0, 0, 0]), 'A05_P3b': ('screen', [0, 0, 0]), 'A06_P3a': ('shell', [0, -30, 0]),
          'A07_P5': ('slab', [34, 0, 0]), 'A08_P4a': ('cap', [0, -28, 0]), 'A09_P4b': ('grommet', [0, 52, 0]), 'A10_P6': ('door', [0, 0, 0]),
          'T01_P1a': ('base', [0, 75, 0]), 'T05_P3b': ('screen', [0, 0, 0]), 'T06_P3a': ('shell', [0, -30, 0]), 'T07_P5': ('slab', [34, 0, 0]),
          'T08_P4a': ('cap', [0, -28, 0]), 'T09_P4b': ('grommet', [0, 52, 0]), 'T10_P6': ('door', [0, 0, 0])}
CAL = [['P16a', [113.0, 97.0, 1.0], [113.0, 97.0, 8.0], 1.6], ['P16b', [113.0, 103.0, 1.0], [113.0, 103.0, 8.0], 1.6],
       ['H20', [120.0, 100.0, 0.0], [120.0, 100.0, 8.0], 2.0], ['P16L', [127.0, 92.0, 4.0], [127.0, 99.0, 4.0], 1.6],
       ['P27L', [136.0, 99.0, 4.15], [136.0, 108.0, 4.15], 2.7], ['H40W', [144.4, 100.0, 1.5], [144.4, 100.0, 8.0], 4.0]]


def _refname(look, job):
    return 'ref_%s_%s' % (look.replace('print_recheck_', ''), job)


def gsum(wait=0):
    lst = []; seen = set()
    for job, (parts, pairs) in PAIRS.items():
        a = {'cmd': 'gsum', 'job': os.path.join(SO, job), 'out': os.path.join(OUT, 'gsum_%s.json' % job)}
        if parts:
            a['parts'] = parts
        lst.append(('gsum_' + job, 'gsum', a))
        for (lab, look, rj, mp, rp) in pairs:
            nm = _refname(look, rj)
            if nm in seen:
                continue
            seen.add(nm); b = {'cmd': 'gsum', 'job': os.path.join(H, look, 'slicer', 'out', rj), 'out': os.path.join(OUT, 'gsum_%s.json' % nm)}
            if parts and rp != '_plate':
                b['parts'] = parts
            lst.append(('gsum_' + nm, 'gsum', b))
    for c in ('T00_cal', 'A00_cal'):
        lst.append(('gsum_' + c, 'gsum', {'cmd': 'gsum', 'job': os.path.join(SO, c), 'out': os.path.join(OUT, 'gsum_%s.json' % c)}))
    # one process per group of runs, at most eight at once
    groups = [lst[i::8] for i in range(8)]
    L['tools']([('pf91_gsum_%d' % i, 'gsum', [x[2] for x in g]) for i, g in enumerate(groups)], wait)


def gcmp(wait=50):
    lst = []
    for job, (parts, pairs) in PAIRS.items():
        mp_list = [[p[3], p[4]] for p in pairs]; look, rj = pairs[0][1], pairs[0][2]
        if job == 'T04_P7':
            for (lab, lk, r, mp, rp) in pairs:
                lst.append({'cmd': 'gcmp', 'a': os.path.join(OUT, 'gsum_%s.json' % job), 'b': os.path.join(OUT, 'gsum_%s.json' % _refname(lk, r)),
                            'label': lab, 'parts': [[mp, rp]], 'out': os.path.join(OUT, 'gcmp_%s_%s.json' % (job, mp))})
            continue
        lst.append({'cmd': 'gcmp', 'a': os.path.join(OUT, 'gsum_%s.json' % job), 'b': os.path.join(OUT, 'gsum_%s.json' % _refname(look, rj)),
                    'label': pairs[0][0], 'parts': mp_list, 'out': os.path.join(OUT, 'gcmp_%s.json' % job)})
    L['tools']([('pf91_gcmp', 'gcmp', lst)], wait)
    print(open(os.path.join(OUT, 'pf91_gcmp.txt')).read())


def lin(wait=0):
    jobs = [j for j in PAIRS] + ['T00_cal', 'A00_cal']
    groups = [jobs[i::6] for i in range(6)]
    L['tools']([('pf91_lin_%d' % i, 'lin', [{'cmd': 'lin', 'job': os.path.join(SO, j)} for j in g]) for i, g in enumerate(groups)], wait,
               prog=os.path.join(L['RD91'], 'r91_lin.py'))


def holes(wait=0):
    lst = []
    for job, (parts, pairs) in PAIRS.items():
        a = {'cmd': 'holes', 'job': os.path.join(SO, job), 'out': os.path.join(OUT, 'holes_%s.json' % job)}
        if parts:
            a['parts'] = [[p[1], p[2]] for p in parts]
        else:
            m, pos = SINGLE[job]; a['parts'] = [[m, pos]]
            if m == 'shell_chin8':
                a['key'] = {'shell_chin8': 'shell'}
        lst.append(a)
    for c in ('T00_cal', 'A00_cal'):
        lst.append({'cmd': 'holes', 'job': os.path.join(SO, c), 'parts': [], 'extra': CAL, 'out': os.path.join(OUT, 'holes_%s.json' % c)})
    groups = [lst[i::6] for i in range(6)]
    L['tools']([('pf91_holes_%d' % i, 'holes', g) for i, g in enumerate(groups)], wait)


def poll(prefix='pf91_'):
    names = sorted(f[:-9] for f in os.listdir(OUT) if f.endswith('.pid.json') and f.startswith(prefix))
    L['poll'](names, 300)
# END pf91_30_stop.py
