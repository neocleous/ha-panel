# Print re-check of version 79, block 2: the support blockers under D416 to D418. No Fusion object.
#   main(): for each part a blocker mesh stl/bed/<part>_blk.stl in the part's own bed frame, and its list as json beside it:
#     - a cylinder along every hole that takes an insert, a magnet, a screw or a pilot (read on the model: out/r91_21_holes.json)
#       and that could hold support in this print direction: it lies or leans more than 30 deg, or it stands with its closed
#       end up. Radius = the hole's + 0.35 (PR27's figure), from 0.6 before an open end to 0.3 past a closed one;
#     - the record's boxes, in world coordinates as read back from the version-67 blocker meshes (out/blkinfo_*.txt):
#       the shell's chin band and side strips, its ten lip pockets, its exhaust rows; the screen plate's peg pocket and slot.
#   Holes that stand with the bed-side end open and nothing over them get no cylinder: nothing can grow in them, and a
#   cylinder there would take the interface from the face round the mouth (the base plate's counterbores).
import os, json, math, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'r91_lib.py'))
# part (bed mesh name) -> hole diameters that get a cylinder, extra radius
WHICH = {'shell': ([1.6, 3.4, 4.0], 0.35), 'door': ([1.6, 3.0, 4.0, 8.3], 0.35), 'spkbox_L': ([2.5, 2.7, 4.0, 6.2], 0.35),
         'spkbox_R': ([2.5, 2.7, 4.0, 6.2], 0.35), 'cradle': ([1.6, 3.4, 6.5], 0.35), 'bme_hood': ([2.2, 2.4], 0.35),
         'clip_L': ([3.4], 0.35), 'holder': ([1.6, 3.4], 0.35), 'grommet': ([2.2], 0.35), 'base_strict': ([6.5], 0.2)}
BOX = {'shell': [{'box': [[-100, 4.6, 0.0], [100, 7.0, 6.5]], 'label': 'chin band (record)'},
                 {'box': [[-100, 4.6, 2.0], [-87, 7.0, 48.5]], 'label': 'chin side strip -x (record)'},
                 {'box': [[87, 4.6, 2.0], [100, 7.0, 48.5]], 'label': 'chin side strip +x (record)'},
                 {'box': [[-50, -56.0, 162.5], [50, -38.0, 170.2]], 'label': 'exhaust rows (record)'}] +
                [{'box': [[sx * cx - 4.5, -62.0, cz - 4.5], [sx * cx + 4.5, -54.0, cz + 4.5]], 'label': 'lip pocket (record)'}
                 for sx in (-1, 1) for (cx, cz) in ((70.61, 24.73), (65.92, 59.49), (57.34, 94.15), (39.01, 130.28), (15.74, 147.38))],
       'screen': [{'box': [[-90.47, 3.35, 55.77], [-79.53, 7.08, 65.39]], 'label': 'peg slot (record)'},
                  {'box': [[80.28, 3.35, 55.77], [89.72, 7.08, 65.39]], 'label': 'peg pocket (record)'}]}


def items(part, key=None):
    O = json.load(open(os.path.join(L['RD'], 'out', 'r91_orient.json'))); H = json.load(open(os.path.join(L['RD'], 'out', 'r91_21_holes.json')))
    mesh = key or part; M = O[mesh]['M']; ds, er = WHICH.get(part, ([], 0.35)); out = []
    for h in H.get(mesh, []):
        if not h['hole'] or h['round_deg'] < 100 or h['d'] not in ds:
            continue
        A, B = h['A'], h['B']; a = [B[i] - A[i] for i in range(3)]; ln = math.sqrt(sum(c * c for c in a)); a = [c / ln for c in a]
        az = M[2][0] * a[0] + M[2][1] * a[1] + M[2][2] * a[2]                      # the axis in the bed frame, its height part
        ang = math.degrees(math.acos(min(1.0, abs(az))))
        eA, eB = h['ends']
        zA = M[2][0] * A[0] + M[2][1] * A[1] + M[2][2] * A[2]; zB = M[2][0] * B[0] + M[2][1] * B[1] + M[2][2] * B[2]
        top_closed = (eB if zB > zA else eA) == 'closed'
        if ang <= 30 and not top_closed and part != 'base_strict':
            continue
        r = h['d'] / 2 + (0.6 if h['d'] == 8.3 else er)
        p0 = [A[i] - a[i] * (0.3 if eA == 'closed' else 0.6) for i in range(3)]; p1 = [B[i] + a[i] * (0.3 if eB == 'closed' else 0.6) for i in range(3)]
        out.append({'cyl': [p0, p1], 'r': round(r, 3), 'label': 'hole %.2f, %s, ends %s/%s' % (h['d'], 'lying' if ang > 85 else 'leaning %.0f' % ang if ang > 5 else 'upright', eA, eB)})
    return out + BOX.get(part, [])


def main(only=None):
    O = json.load(open(os.path.join(L['RD'], 'out', 'r91_orient.json'))); jobs = []
    for part in ('shell', 'screen', 'door', 'spkbox_L', 'spkbox_R', 'cradle', 'bme_hood', 'clip_L', 'holder', 'grommet', 'base_strict'):
        if only and part not in only:
            continue
        key = 'base' if part == 'base_strict' else part
        it = items(part, key)
        if not it:
            print(part, 'no blocker'); continue
        jobs.append({'cmd': 'blk', 'out': os.path.join(L['BED'], part + '_blk.stl'), 'map': O[key]['M'], 'items': it})
        n = {}
        for i in it:
            k = i['label'].split(',')[0]; n[k] = n.get(k, 0) + 1
        print('%-12s %3d items: %s' % (part, len(it), ', '.join('%s x%d' % (k, v) for k, v in sorted(n.items()))))
    L['tools']([('blk_all', 'multi2', jobs)], 40)
    print(open(os.path.join(L['RD'], 'out', 'blk_all.txt')).read())
# END r91_26_blk.py
