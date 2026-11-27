#!/usr/bin/env python3
# Print re-check of version 79: offline tools of my own, beside part C's cgq.py (imported as a module, read where it is).
# Pure Python 3, runs OUTSIDE Fusion as a background process; touches no Fusion object; writes only under print_recheck_v91/.
#   cmpset   two STL files as sets of triangles (any order): how many triangles of each are not in the other
import sys, os, json, math, struct, time
PC = os.path.expanduser('~/Documents/HA_panel_renders/adversarial_audit_v69/c')
sys.path.insert(0, PC)
import cgq                                                    # noqa: E402  (part C's tools: read_stl, mesh_sections, Grid, get_index ...)


def _tris(path, q=None):
    b = open(path, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]; out = {}
    for t in range(n):
        f = struct.unpack_from('<9f', b, 84 + 50 * t + 12)
        if q:
            f = tuple(round(c / q) for c in f)
        v = [f[0:3], f[3:6], f[6:9]]; i = v.index(min(v)); k = (v[i], v[(i + 1) % 3], v[(i + 2) % 3])
        out[k] = out.get(k, 0) + 1
    return n, out


def cmd_cmpset(a):
    """args: pairs: [[label, stlA, stlB]], q (rounding step, default exact)."""
    for (lab, pa, pb) in a['pairs']:
        for q in (None, 1e-4, 1e-3):
            na, A = _tris(pa, q); nb, B = _tris(pb, q)
            onlyA = sum(c - min(c, B.get(k, 0)) for k, c in A.items()); onlyB = sum(c - min(c, A.get(k, 0)) for k, c in B.items())
            print('cmpset %-10s %s: A %d triangles, B %d | only in A %d, only in B %d' % (lab, 'exact' if q is None else 'rounded to %g' % q, na, nb, onlyA, onlyB))
            if onlyA == 0 and onlyB == 0:
                break


def _unit(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return [c / m for c in v]


def _dist_axis(p, A, B):
    """(distance of p from the line A-B, its place along it from A, the length A-B)."""
    d = [B[i] - A[i] for i in range(3)]; ln = math.sqrt(sum(c * c for c in d)) or 1e-9
    u = [c / ln for c in d]; q = [p[i] - A[i] for i in range(3)]; s = sum(q[i] * u[i] for i in range(3))
    r = math.sqrt(max(0.0, sum(c * c for c in q) - s * s))
    return r, s, ln


def _att(a_bed):
    ang = math.degrees(math.acos(min(1.0, abs(a_bed[2]))))
    return ('upright' if ang < 5 else 'lying' if ang > 85 else 'leaning %.0f' % ang), ang


def cmd_blkinfo(a):
    """The separate pieces of a blocker STL: bed box and world box of each. args: stl, map, pos."""
    b, n = cgq.read_stl(a['stl']); mp = cgq.load_map(a); par = {}

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    T = []
    for t in cgq.stl_tris(b, n):
        vs = [tuple(round(c, 3) for c in t[k:k + 3]) for k in (3, 6, 9)]
        for v in vs:
            par.setdefault(v, v)
        r0 = find(vs[0])
        for v in vs[1:]:
            par[find(v)] = r0
        T.append(vs)
    C = {}
    for vs in T:
        r = find(vs[0]); c = C.setdefault(r, [[1e9] * 3, [-1e9] * 3, 0])
        c[2] += 1
        for v in vs:
            for i in range(3):
                c[0][i] = min(c[0][i], v[i]); c[1][i] = max(c[1][i], v[i])
    print('blkinfo', os.path.basename(a['stl']), 'triangles', n, 'pieces', len(C))
    for lo, hi, nt in sorted(C.values(), key=lambda c: c[0]):
        w = ''
        if mp:
            ws = [cgq.b2w(mp[0], mp[1], (x + mp[1][0], y + mp[1][1], z + mp[1][2])) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
            w = ' | world x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f' % (min(p[0] for p in ws), max(p[0] for p in ws), min(p[1] for p in ws), max(p[1] for p in ws), min(p[2] for p in ws), max(p[2] for p in ws))
        print('  %3d tris  bed x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f%s' % (nt, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], w))


def _prism(A, B, r, n=24):
    """Triangles of a closed n-sided prism of radius r from A to B."""
    u = _unit([B[i] - A[i] for i in range(3)])
    k = min(range(3), key=lambda i: abs(u[i])); e = [0.0, 0.0, 0.0]; e[k] = 1.0
    v = _unit([u[1] * e[2] - u[2] * e[1], u[2] * e[0] - u[0] * e[2], u[0] * e[1] - u[1] * e[0]])
    w = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    ring = lambda P: [[P[i] + r * (math.cos(2 * math.pi * j / n) * v[i] + math.sin(2 * math.pi * j / n) * w[i]) for i in range(3)] for j in range(n)]
    ra = ring(A); rb = ring(B); T = []
    for j in range(n):
        k2 = (j + 1) % n
        T += [(ra[j], ra[k2], rb[k2]), (ra[j], rb[k2], rb[j]), (list(A), ra[k2], ra[j]), (list(B), rb[j], rb[k2])]
    return T


def _box(C8):
    """Triangles of a box from its 8 corners in the order x(lo,hi) y(lo,hi) z(lo,hi) nested as xyz bits."""
    q = lambda i, j, k: C8[i * 4 + j * 2 + k]
    F = [((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)),
         ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))]
    T = []
    for f in F:
        p = [q(*c) for c in f]; T += [(p[0], p[1], p[2]), (p[0], p[2], p[3])]
    return T


def cmd_blk(a):
    """A support-blocker STL in a part's bed frame (no plate offset). args: out, map (the part's M; its pos is not applied),
    items: [{'cyl': [A, B] world, 'r': r, 'label'} | {'box': [lo, hi] world, 'label'}]."""
    M = json.load(open(a['map']))['M'] if isinstance(a['map'], str) else a['map']
    w2b = lambda p: [M[r][0] * p[0] + M[r][1] * p[1] + M[r][2] * p[2] + M[r][3] for r in range(3)]
    T = []
    for it in a['items']:
        if 'cyl' in it:
            T += _prism(w2b(it['cyl'][0]), w2b(it['cyl'][1]), it['r'])
        else:
            lo, hi = it['box']
            T += _box([w2b((x, y, z)) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    o = bytearray(84 + 50 * len(T)); o[0:80] = b'HA panel print re-check v91 support blockers bed mm'.ljust(80, b' ')
    struct.pack_into('<I', o, 80, len(T))
    for i, (p, q, r_) in enumerate(T):
        struct.pack_into('<12fH', o, 84 + 50 * i, 0.0, 0.0, 0.0, *p, *q, *r_, 0)
    open(a['out'], 'wb').write(o)
    json.dump(a['items'], open(a['out'][:-4] + '.json', 'w'), indent=0)
    print('blk', os.path.basename(a['out']), 'items', len(a['items']), 'triangles', len(T))


def cmd_cls(a):
    """A slice's faces that look at the bed (ovh.json: what each rests on), sorted into those inside a listed hole and the rest;
    and the support printed inside each hole. args: job, holes (json), key (part), map, min (mm2 listed, default 1.0),
    skip_d (hole diameters not looked at), show."""
    job = a['job']; mp = cgq.load_map(a); M, pos = mp
    H = [h for h in json.load(open(a['holes']))[a['key']] if h['hole'] and h['round_deg'] >= a.get('min_round', 100) and h['d'] not in a.get('skip_d', [])]
    for h in H:
        h['bA'] = cgq.w2b(M, pos, h['A']); h['bB'] = cgq.w2b(M, pos, h['B'])
        ab = _unit([h['bB'][i] - h['bA'][i] for i in range(3)]); h['att'], h['ang'] = _att(ab)
        h['g'] = {}; h['sv'] = 0.0; h['iv'] = 0.0
    ov = json.load(open(os.path.join(job, 'ovh.json'))); rest = []
    print('cls', os.path.basename(job), '| totals, mm2 summed over layers:', ov.get('totals_mm2_layers'))
    for g in ov['groups']:
        wb = g.get('wbox'); hit = None
        pts = [g['world0']] if g.get('world0') else []
        if wb:
            pts.append([(wb[0][i] + wb[1][i]) / 2 for i in range(3)])
        for h in H:
            for p in pts:
                r, s, ln = _dist_axis(p, h['A'], h['B'])
                if r <= h['d'] / 2 + 0.7 and -0.7 <= s <= ln + 0.7:
                    hit = h; break
            if hit:
                break
        if hit:
            e = hit['g'].setdefault(g['kind'], [0, 0.0, 99.0, 0.0]); e[0] += 1; e[1] += g['area']; e[2] = min(e[2], g['z0']); e[3] = max(e[3], g['z1'])
        else:
            rest.append(g)
    # support lines inside each hole
    ix = cgq.get_index(job); nm = ix['names']; HH = [h for h in H if h['att'] != 'upright' or 'closed' in h['ends']]
    for Ly in ix['layers']:
        if not Ly['ns']:
            continue
        hs = Ly['hs'] or Ly['hm'] or 0.2; zm = Ly['z'] - hs / 2.0
        cand = [h for h in HH if min(h['bA'][2], h['bB'][2]) - h['d'] <= zm <= max(h['bA'][2], h['bB'][2]) + h['d']]
        if not cand:
            continue
        for (x1, y1, x2, y2, w, f) in cgq.segs(Ly):
            n_ = nm[f]
            if n_ not in cgq.SUPPORT_F:
                continue
            p = ((x1 + x2) / 2, (y1 + y2) / 2, zm)
            for h in cand:
                r, s, ln = _dist_axis(p, h['bA'], h['bB'])
                if r <= h['d'] / 2 + 0.05 and 0.0 <= s <= ln:
                    v = math.hypot(x2 - x1, y2 - y1) * w * hs
                    h['sv'] += v
                    if n_ == 'Support interface':
                        h['iv'] += v
                    break
    print('holes of the part looked at: %d (hole diameters skipped: %s)' % (len(H), a.get('skip_d', [])))
    print('  d     attitude    ends            world A -> B                                   | support inside mm3 (of it interface) | faces inside: kind n area z0-z1')
    for h in sorted(H, key=lambda h: (h['d'], h['A'])):
        if not h['g'] and h['sv'] == 0 and not a.get('all'):
            continue
        print('  %-5.2f %-11s %-15s (%.1f, %.1f, %.1f) -> (%.1f, %.1f, %.1f) | %7.2f (%5.2f) | %s' % (
            h['d'], h['att'], '/'.join(h['ends']), h['A'][0], h['A'][1], h['A'][2], h['B'][0], h['B'][1], h['B'][2], h['sv'], h['iv'],
            '; '.join('%s %d %.1f z %.2f-%.2f' % (k, e[0], e[1], e[2], e[3]) for k, e in sorted(h['g'].items()))))
    quiet = sum(1 for h in H if not h['g'] and h['sv'] == 0)
    print('  holes with no support inside and no face listed: %d' % quiet)
    mn = a.get('min', 1.0); rest.sort(key=lambda g: -g['area'])
    by = {}
    for g in rest:
        e = by.setdefault(g['kind'], [0, 0.0]); e[0] += 1; e[1] += g['area']
    print('faces outside the holes, by what they rest on (groups, mm2 summed over layers):', {k: [v[0], round(v[1], 1)] for k, v in by.items()})
    print('  kind            bed z0-z1  L   area: sup gap br ov air | world box')
    for g in rest[:a.get('show', 60)]:
        if g['area'] < mn:
            continue
        wb = g.get('wbox') or [[0, 0, 0], [0, 0, 0]]
        print('  %-15s %6.2f-%6.2f %3d %7.1f: %6.1f %6.1f %6.1f %6.1f %6.1f | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (
            g['kind'], g['z0'], g['z1'], g['layers'], g['area'], g['sup'], g['gap'], g['br'], g['ov'], g['air'], wb[0][0], wb[1][0], wb[0][1], wb[1][1], wb[0][2], wb[1][2]))
    json.dump({'holes': [{k: h[k] for k in ('d', 'A', 'B', 'att', 'ends', 'sv', 'iv', 'g', 'round_deg', 'len')} for h in H], 'rest': rest},
              open(os.path.join(job, 'cls.json'), 'w'), indent=0)


CMDS = {'cmpset': cmd_cmpset, 'blkinfo': cmd_blkinfo, 'blk': cmd_blk, 'cls': cmd_cls}

if __name__ == '__main__':
    t0 = time.time(); arg = sys.argv[2]
    A = json.load(open(arg)) if os.path.exists(arg) else json.loads(arg)
    for a in (A if isinstance(A, list) else [A]):
        try:
            CMDS[a.get('cmd', sys.argv[1])](a)
        except Exception:
            import traceback
            print('ERROR in', a.get('cmd', sys.argv[1]), json.dumps(a)[:300]); traceback.print_exc()
        sys.stdout.flush()
    print('[%s  %.1f s]' % (time.strftime('%Y-%m-%d %H:%M:%S'), time.time() - t0))
# END r91_tools.py
