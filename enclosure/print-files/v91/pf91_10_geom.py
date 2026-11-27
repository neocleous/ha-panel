# Print files of version 91, block 1: the meshes. READ-ONLY on the design (only temporary B-rep copies, never added to it).
#   export(budget)  world STL of the 17 printed bodies from version 91, meshed as the chain does (0.01 mm chordal, 10 deg).
#   cut8()          the adhesion test's piece: the shell's first 8.0 in its print (bed z = 6.7992 - world y), as the re-check's.
#   orient()        the bed meshes by part C's own tool (cgq.py orient), with the same matrices and the same calls as the
#                   re-check's r91_20_orient.main(); the maps go to out/pf91_orient.json.
#   cmp()           every world and bed mesh against the re-check's (print_recheck_v91/stl/), bytes after the 80-byte header;
#                   the maps against out/r91_orient.json.
# Long calls stop after their budget and go on at the next call. No time.sleep().
import os, json, math, time, struct, runpy
L = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pf91_lib.py'))
C12, S12, H0, XC = L['C12'], L['S12'], L['H0'], L['XC']
ORJ = os.path.join(L['W'], 'out', 'pf91_orient.json')
ORI_PATH = os.path.join(L['HOME'], 'print_files', '_work', 'data', 'pf_2_orient.json')
ORI_SHA = '1d37da540a429178f2a9b8ec5e0747dcf0f08c8a8273a09f0694a2d5443c8cf2'      # enclosure/print-files/README.md on docs
I3 = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
KEYS = ('shell', 'screen', 'slab', 'door', 'base', 'spkbox_L', 'spkbox_R', 'carrier', 'cradle', 'cap', 'grommet', 'bme_hood',
        'clamp_L', 'clamp_R', 'clip_L', 'clip_R', 'holder', 'shell_chin8')


def w2d(x, y, z):
    """world mm -> design cm (the inverse of world_mesh's frame)."""
    return ((x + XC) / 10.0, (C12 * y + S12 * (z - H0)) / 10.0, (-S12 * y + C12 * (z - H0)) / 10.0)


def export(budget=45.0):
    t0 = time.time(); rep, root = L['guard'](strict=True)
    recp = os.path.join(L['W'], 'out', 'pf91_10_export.json')
    out = json.load(open(recp)) if os.path.exists(recp) else {}
    now = []
    for tag, bn in L['PRINTS']:
        if tag in out:
            continue
        if time.time() - t0 > budget:
            break
        b = root.bRepBodies.itemByName(bn)
        P, T = L['world_mesh'](b, 0.01, 10.0)
        n = L['write_stl'](os.path.join(L['WORLD'], tag + '.stl'), P, T, tag)
        out[tag] = {'body': bn, 'tris': n, 'vol_mm3': round(b.volume * 1000.0, 3), 't': L['stamp']()}
        now.append(tag); json.dump(out, open(recp, 'w'), indent=1)
    left = [t for t, _ in L['PRINTS'] if t not in out]
    rep2, _ = L['guard'](strict=True)
    print('export: done now', now, '| left', left, '| modified after:', rep2['modified'], '| s %.1f' % (time.time() - t0))
    for t in now:
        r = out[t]; print('  %-9s %-16s tris %7d  vol %11.3f' % (t, r['body'], r['tris'], r['vol_mm3']))


def cut8(zcut=8.0):
    import adsk.core, adsk.fusion
    t0 = time.time(); rep, root = L['guard'](strict=True)
    tbm = adsk.fusion.TemporaryBRepManager.get()
    tb = tbm.copy(root.bRepBodies.itemByName('HOUSING_F_front'))
    y0 = 6.7992 - zcut; y1, x0, x1, z0, z1 = 80.0, -200.0, 200.0, -60.0, 360.0
    wc = (0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1))
    cx, cy, cz = w2d(*wc)
    obb = adsk.core.OrientedBoundingBox3D.create(adsk.core.Point3D.create(cx, cy, cz), adsk.core.Vector3D.create(1, 0, 0),
                                                 adsk.core.Vector3D.create(0, C12, -S12), (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
    box = tbm.createBox(obb)
    ok = tbm.booleanOperation(tb, box, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    P, T = L['world_mesh'](tb, 0.01, 10.0)
    n = L['write_stl'](os.path.join(L['WORLD'], 'shell_chin8.stl'), P, T, 'shell_chin8')
    ys = [p[1] for p in P]
    out = {'bool_ok': ok, 'vol_mm3': round(tb.volume * 1000.0, 3), 'lumps': tb.lumps.count, 'tris': n, 'world_y': [round(min(ys), 4), round(max(ys), 4)],
           'brief': 29036.621, 's': round(time.time() - t0, 1)}
    rep2, _ = L['guard'](strict=True)
    out['modified_after'] = rep2['modified']
    L['jdump']('pf91_10_cut8.json', out)
    print(json.dumps(out))


def orient(wait=60):
    ob = open(ORI_PATH, 'rb').read(); import hashlib
    if hashlib.sha256(ob).hexdigest() != ORI_SHA:
        raise RuntimeError('the matrices of record changed: ' + ORI_PATH)
    ORI = json.loads(ob); WD = L['WORLD']; B = L['BED']
    hood = json.load(open(os.path.join(L['PC'], 'slicer', 'out', 'hood_H2_n', 'map.json')))['M']
    jobs = []

    def add(key, tag, M=None, R=None, keep=True):
        a = {'cmd': 'orient', 'stl': os.path.join(WD, tag + '.stl'), 'out': os.path.join(B, key + '.stl'), 'json': ORJ, 'key': key}
        if M is not None:
            a['M'] = M; a['keep_xy'] = keep
        else:
            a['R'] = R
        jobs.append(a)
    for tag in ('shell', 'screen', 'slab', 'door', 'base', 'spkbox_L', 'spkbox_R', 'carrier', 'cradle', 'cap', 'clip_L', 'clip_R'):
        add(tag, tag, M=ORI[tag]['M'])
    add('shell_chin8', 'shell_chin8', M=ORI['shell']['M'])
    add('bme_hood', 'bme_hood', M=hood, keep=False)
    for tag in ('grommet', 'clamp_L', 'clamp_R', 'holder'):
        add(tag, tag, R=I3)
    os.makedirs(B, exist_ok=True)
    L['tools']([('pf91_orient_all', 'multi', jobs)], wait, prog=L['CGQ'])
    L['poll'](['pf91_orient_all'], 600)


def cmp():
    R91 = L['RD91']; res = {}
    for sub in ('world', 'bed'):
        for k in KEYS:
            a = os.path.join(L['W'], 'stl', sub, k + '.stl'); b = os.path.join(R91, 'stl', sub, k + '.stl')
            if not os.path.exists(a) or not os.path.exists(b):
                res[sub + '/' + k] = 'MISSING mine %s, re-check %s' % (os.path.exists(a), os.path.exists(b)); continue
            A = open(a, 'rb').read(); Bb = open(b, 'rb').read()
            na = struct.unpack_from('<I', A, 80)[0]; nb = struct.unpack_from('<I', Bb, 80)[0]
            res[sub + '/' + k] = '%s (%d / %d triangles)' % ('same bytes after the header' if A[80:] == Bb[80:] else 'DIFFERS', na, nb)
    O = json.load(open(ORJ)); R = json.load(open(os.path.join(R91, 'out', 'r91_orient.json')))
    for k in KEYS:
        res['map/' + k] = 'equal' if (k in O and k in R and O[k]['M'] == R[k]['M']) else 'DIFFERS or missing'
    for k, v in res.items():
        print('%-22s %s' % (k, v))
    bad = [k for k, v in res.items() if not (v.startswith('same') or v == 'equal')]
    print('ALL EQUAL' if not bad else 'NOT EQUAL: %s' % bad)
    L['jdump']('pf91_10_cmp.json', res)
# END pf91_10_geom.py
