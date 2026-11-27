# Print files of version 91, block 4: two variants for the Architect, each a held plate with one blocker more. Not print files.
#   T02b_P1b  PLA P1b with a cylinder in each box's 4.0 wire hole (the lead's hole through the rear wall): the PLA slice has a tree's
#             trunk standing through both (8.15 and 8.56 mm3); the ABS slice has none.
#   A06b_P3a  ABS P3a with a cylinder along each of the ten lip pockets (8.3 across, the lip's magnets): the ABS slice has interface
#             inside the mouths of the four upper ones (1.0 to 1.6 mm3), inside the record's blocker boxes.
#   Each cylinder by the rule of r91_26_blk.py: radius the hole's + 0.35 (8.3: + 0.6, as the door's magnet pockets), from 0.6 before
#   an open end to 0.3 past a closed one. make(): the blockers (the re-check's r91_tools 'blk') and the two jobs, started.
import os, json, math, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
OUT = os.path.join(L['W'], 'out'); BED = L['BED']
TOOLS91 = os.path.join(L['RD91'], 'r91_tools.py')


def _cyl(h):
    A, B = h['world']; a = [B[i] - A[i] for i in range(3)]; ln = math.sqrt(sum(c * c for c in a)); a = [c / ln for c in a]
    eA, eB = h['ends']; r = h['d'] / 2 + (0.6 if h['d'] == 8.3 else 0.35)
    p0 = [A[i] - a[i] * (0.3 if eA == 'closed' else 0.6) for i in range(3)]; p1 = [B[i] + a[i] * (0.3 if eB == 'closed' else 0.6) for i in range(3)]
    return {'cyl': [p0, p1], 'r': round(r, 3), 'label': 'hole %.2f, ends %s/%s (print files v91 variant)' % (h['d'], eA, eB)}


def make(wait=30, start=True):
    O = json.load(open(os.path.join(OUT, 'pf91_orient.json')))
    T2 = json.load(open(os.path.join(OUT, 'holes_T02_P1b.json'))); A6 = json.load(open(os.path.join(OUT, 'holes_A06_P3a.json')))
    wl = [h for h in T2 if h['part'] == 'spkbox_L' and h['d'] == 4.0 and h['ends'] == ['open', 'open']]
    wr = [h for h in T2 if h['part'] == 'spkbox_R' and h['d'] == 4.0 and h['ends'] == ['open', 'open']]
    lip = [h for h in A6 if h['part'] == 'shell' and h['d'] == 8.3]
    print('wire holes: left %s, right %s | lip pockets: %d' % ([h['world'] for h in wl], [h['world'] for h in wr], len(lip)))
    jobs = [{'cmd': 'blk', 'out': os.path.join(BED, 'spkbox_L_wire_blk.stl'), 'map': O['spkbox_L']['M'], 'items': [_cyl(h) for h in wl]},
            {'cmd': 'blk', 'out': os.path.join(BED, 'spkbox_R_wire_blk.stl'), 'map': O['spkbox_R']['M'], 'items': [_cyl(h) for h in wr]},
            {'cmd': 'blk', 'out': os.path.join(BED, 'shell_lip_blk.stl'), 'map': O['shell']['M'], 'items': [_cyl(h) for h in lip]}]
    L['tools']([('pf91_blk_var', 'multi2', jobs)], wait, prog=TOOLS91)
    print(open(os.path.join(OUT, 'pf91_blk_var.txt')).read())
    for (src, job, add) in (('T02_P1b', 'T02b_P1b', [('spkbox_L_wire_blk.stl', [-50, -20, 0]), ('spkbox_R_wire_blk.stl', [50, -20, 0])]),
                            ('A06_P3a', 'A06b_P3a', [('shell_lip_blk.stl', [0, -30, 0])])):
        s = json.load(open(os.path.join(L['W'], 'slicer', 'jobs', src, 'spec.json')))
        s['job'] = job; s.pop('deliver', None); s['title'] = s['title'] + ' - variant with one blocker more'; s['desc'] = 'work slice for the Architect - not a print file'
        for (stl, pos) in add:
            s['plates'][0]['objects'].append({'stl': stl, 'assemble': 1, 'subtype': 'support_blocker', 'pos': pos})
        L['mkjob'](s)
    if start:
        L['slicer']('start', ['T02b_P1b', 'A06b_P3a'])
def lin(wait=60):
    SO = os.path.join(L['W'], 'slicer', 'out')
    L['tools']([('pf91_lin_var_%s' % j, 'lin', [{'cmd': 'lin', 'job': os.path.join(SO, j)}]) for j in ('T02b_P1b', 'A06b_P3a')], wait,
               prog=os.path.join(L['RD91'], 'r91_lin.py'))


def check(wait=60):
    S = runpy.run_path(os.path.join(D, 'pf91_30_stop.py')); SO = S['SO']; lst = []
    for (j, src) in (('T02b_P1b', 'T02_P1b'), ('A06b_P3a', 'A06_P3a')):
        parts = S['PAIRS'][src][0]
        g = {'cmd': 'gsum', 'job': os.path.join(SO, j), 'out': os.path.join(OUT, 'gsum_%s.json' % j)}
        if parts:
            g['parts'] = parts
        lst.append(g)
        lst.append({'cmd': 'gcmp', 'a': os.path.join(OUT, 'gsum_%s.json' % j), 'b': os.path.join(OUT, 'gsum_%s.json' % src), 'label': j + ' against ' + src,
                    'parts': [[p[0], p[0]] for p in parts] if parts else [['_plate', '_plate']], 'out': os.path.join(OUT, 'gcmp_%s.json' % j)})
        h = {'cmd': 'holes', 'job': os.path.join(SO, j), 'out': os.path.join(OUT, 'holes_%s.json' % j)}
        if parts:
            h['parts'] = [[p[1], p[2]] for p in parts]
        else:
            h['parts'] = [list(S['SINGLE'][src])]
        lst.append(h)
    L['tools']([('pf91_check_var', 'gsum', lst)], wait)
    txt = open(os.path.join(OUT, 'pf91_check_var.txt')).read()
    print('\n'.join(l for l in txt.split('\n') if ('support' in l and ' 0.00 mm3' not in l) or l.startswith(('gcmp', 'gsum', 'holes', '   _plate', '   spk', '   clip', '      ', 'ERROR'))))
# END pf91_37_var.py
