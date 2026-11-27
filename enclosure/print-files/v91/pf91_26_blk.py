# Print files of version 91, block 1: the support blockers and enforcers. No Fusion object.
# The blockers are the re-check's r91_26_blk.py (D545: "the blockers from r91_26_blk.py"), its rules and lists unchanged, run here
# on version 91's hole list (print_recheck_v91/out/r91_21_holes.json, read where it is) and the matrices of record
# (out/pf91_orient.json, equal to the re-check's r91_orient.json), written into this step's stl/bed/:
#   - a cylinder along every hole that takes an insert, a magnet, a screw or a pilot (read on the model) and that could hold support
#     in this print direction: it lies or leans more than 30 deg, or it stands with its closed end up. Radius = the hole's + 0.35
#     (PR27's figure), from 0.6 before an open end to 0.3 past a closed one;
#   - the record's boxes, in world coordinates: the shell's chin band and side strips, its ten lip pockets, its exhaust rows; the
#     screen plate's peg pocket and slot.
#   Holes that stand with the bed-side end open and nothing over them get no cylinder (the base plate's counterbores).
#   main(): the blockers.  enf(): the door's enforcer (D418, the re-check's r91_30_final.enforcers()).
#   copies(): the pieces no script of the re-check makes again: the holder's enforcer (D468) and the PLA base plate's kept-free slab,
#             copied and checked by sha256.  cmp(): every piece against the re-check's, bytes after the header.
import os, json, math, runpy, shutil, struct
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
HOLES = os.path.join(L['RD91'], 'out', 'r91_21_holes.json')
ORJ = os.path.join(L['W'], 'out', 'pf91_orient.json')
TOOLS91 = os.path.join(L['RD91'], 'r91_tools.py')
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
ENF = {'door': [{'box': [[-13.8, -81.2, 27.6], [13.8, -79.7, 28.5]], 'label': 'baffle bottom (D418)'}]}
# where the re-check's latest copy of each piece is (the third look made the six changed parts' again; the others are older looks')
REF = {'shell_blk': 'print_recheck_v91', 'door_blk': 'print_recheck_v91', 'spkbox_L_blk': 'print_recheck_v91', 'spkbox_R_blk': 'print_recheck_v91',
       'clip_L_blk': 'print_recheck_v91', 'holder_blk': 'print_recheck_v91', 'screen_blk': 'print_recheck_v85', 'cradle_blk': 'print_recheck_v85',
       'bme_hood_blk': 'print_recheck_v85', 'base_strict_blk': 'print_recheck_v85', 'base_rimfree_blk': 'print_recheck_v85',
       'door_enf': 'print_recheck_v91', 'holder_enf': 'print_recheck_v91'}


def items(part, key=None):
    O = json.load(open(ORJ)); H = json.load(open(HOLES))
    mesh = key or part; M = O[mesh]['M']; ds, er = WHICH.get(part, ([], 0.35)); out = []
    for h in H.get(mesh, []):
        if not h['hole'] or h['round_deg'] < 100 or h['d'] not in ds:
            continue
        A, B = h['A'], h['B']; a = [B[i] - A[i] for i in range(3)]; ln = math.sqrt(sum(c * c for c in a)); a = [c / ln for c in a]
        az = M[2][0] * a[0] + M[2][1] * a[1] + M[2][2] * a[2]
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


def main(wait=50):
    O = json.load(open(ORJ)); jobs = []
    for part in ('shell', 'screen', 'door', 'spkbox_L', 'spkbox_R', 'cradle', 'bme_hood', 'clip_L', 'holder', 'grommet', 'base_strict'):
        key = 'base' if part == 'base_strict' else part
        it = items(part, key)
        if not it:
            print(part, 'no blocker'); continue
        jobs.append({'cmd': 'blk', 'out': os.path.join(L['BED'], part + '_blk.stl'), 'map': O[key]['M'], 'items': it})
        n = {}
        for i in it:
            k = i['label'].split(',')[0]; n[k] = n.get(k, 0) + 1
        print('%-12s %3d items: %s' % (part, len(it), ', '.join('%s x%d' % (k, v) for k, v in sorted(n.items()))))
    L['tools']([('pf91_blk_all', 'multi2', jobs)], wait, prog=TOOLS91)
    L['poll'](['pf91_blk_all'], 3000)


def enf(wait=30):
    O = json.load(open(ORJ)); jobs = []
    for part, it in ENF.items():
        jobs.append({'cmd': 'blk', 'out': os.path.join(L['BED'], part + '_enf.stl'), 'map': O[part]['M'], 'items': it})
    L['tools']([('pf91_enf_all', 'multi2', jobs)], wait, prog=TOOLS91)
    L['poll'](['pf91_enf_all'], 1200)


def copies():
    for f, src in (('holder_enf.stl', 'print_recheck_v91'), ('base_rimfree_blk.stl', 'print_recheck_v85')):
        a = os.path.join(L['HOME'], src, 'stl', 'bed', f); b = os.path.join(L['BED'], f)
        shutil.copy2(a, b)
        print('copied %-22s from %s: sha256 %s, same: %s' % (f, src, L['sha'](b)[:16], L['sha'](a) == L['sha'](b)))
    for f in ('holder_enf.stl', 'base_rimfree_blk.stl'):
        shas = {d: (L['sha'](os.path.join(L['HOME'], d, 'stl', 'bed', f)) or 'none')[:16] for d in ('print_recheck_v79', 'print_recheck_v85', 'print_recheck_v91')}
        print('   %s in the three looks: %s' % (f, shas))


def cmp():
    bad = []
    for k, src in REF.items():
        a = os.path.join(L['BED'], k + '.stl'); b = os.path.join(L['HOME'], src, 'stl', 'bed', k + '.stl')
        if not os.path.exists(a) or not os.path.exists(b):
            print('%-17s MISSING mine %s, %s %s' % (k, os.path.exists(a), src, os.path.exists(b))); bad.append(k); continue
        A = open(a, 'rb').read(); B = open(b, 'rb').read(); same = A[80:] == B[80:]
        print('%-17s %-6d triangles | %s: %s' % (k, struct.unpack_from('<I', A, 80)[0], src, 'same bytes after the header' if same else 'DIFFERS'))
        if not same:
            bad.append(k)
    print('ALL EQUAL' if not bad else 'NOT EQUAL: %s' % bad)
# END pf91_26_blk.py
