#!/usr/bin/env python3
# Print files of version 91: offline tools for the stop rule (D507, D542). Pure Python 3, runs OUTSIDE Fusion as a background
# process; touches no Fusion object; writes only under print_files_v91/_work/.
#   gsum   one slice's G-code read whole: every non-comment line hashed (the slice's identity); the filament extruded by feature
#          kind, layer by layer, and by part (each part a box on the plate); masses at the G-code's own densities.
#          args: job (slice folder), out (json), boxes [[name, xmin, xmax, ymin, ymax]] (optional)
#   gcmp   two gsum results compared: identity; by part, the part's own lines (every kind but support, interface, prime tower,
#          brim and skirt) in all and layer by layer; the layers that carry top and bottom surfaces, bridges and interface.
#          args: a, b (gsum json), label, tol_layer (mm3, default 0.5), tol_rel (default 0.005)
#   holes  every round hole of every part on a plate (print_recheck_v91/out/r91_21_holes.json, or a list given), read on the plate's
#          own slice: the support line volume whose middle lies inside the hole's cylinder (radius less 0.05), and the part's own lines
#          in a ring 0.0 to 1.2 outside the hole (proof that the hole was found where the part is). Uses part C's cgq (read where it is)
#          on the index made by the re-check's r91_lin.py.
#          args: job, parts [[mesh, pos]], extra [[label, A_bed, B_bed, d]] (holes given in bed mm), dmax, out
import sys, os, json, math, hashlib, time
PC = os.path.expanduser('~/Documents/HA_panel_renders/adversarial_audit_v69/c')
R91 = os.path.expanduser('~/Documents/HA_panel_renders/print_recheck_v91')
W = os.path.expanduser('~/Documents/HA_panel_renders/print_files_v91/_work')
NOT_OWN = ('upport', 'Prime tower', 'Brim', 'Skirt', 'Wipe', 'Custom')
FA = math.pi * (1.75 / 2) ** 2          # filament cross-section, mm2


def _own(k):
    return not any(s in k for s in NOT_OWN)


def _wr(p, obj):
    if not os.path.abspath(p).startswith(W + os.sep):
        raise RuntimeError('refused, outside the work folder: ' + p)
    json.dump(obj, open(p, 'w'), indent=1)


def cmd_gsum(a):
    t0 = time.time(); gp = os.path.join(a['job'], 'plate_1.gcode'); boxes = list(a.get('boxes') or [])
    if a.get('parts'):                      # [[name, mesh, pos]]: each part's box on the plate from its world mesh, 1.5 wider all round
        sys.path.insert(0, PC); import cgq, struct
        O = json.load(open(os.path.join(W, 'out', 'pf91_orient.json')))
        for (name, mesh, pos) in a['parts']:
            b = open(os.path.join(W, 'stl', 'world', mesh + '.stl'), 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
            lo = [1e9] * 3; hi = [-1e9] * 3
            for t in range(n):
                f = struct.unpack_from('<9f', b, 84 + 50 * t + 12)
                for k in range(9):
                    i = k % 3; lo[i] = min(lo[i], f[k]); hi[i] = max(hi[i], f[k])
            cs = [cgq.w2b(O[mesh]['M'], pos, (xx, yy, zz)) for xx in (lo[0], hi[0]) for yy in (lo[1], hi[1]) for zz in (lo[2], hi[2])]
            boxes.append([name, min(c[0] for c in cs) - 1.5, max(c[0] for c in cs) + 1.5, min(c[1] for c in cs) - 1.5, max(c[1] for c in cs) + 1.5])
        print('boxes', [[bx[0]] + [round(c, 1) for c in bx[1:]] for bx in boxes])
    h = hashlib.sha256(); nlines = 0; feat = 'none'; z = 0.0; lay = -1; x = y = 0.0; tool = 0; rel = True
    dens = None; ver = None
    K = {}            # part -> kind -> mm3 of filament
    LZ = {}           # part -> layer index -> [z, own, top, bottom, bridge, interface, support]
    zs = []
    with open(gp, errors='replace') as f:
        for ln in f:
            if ln.startswith(';'):
                if ln.startswith('; FEATURE: '):
                    feat = ln[11:].strip()
                elif ln.startswith('; Z_HEIGHT: '):
                    z = float(ln[12:])
                elif ln.startswith('; CHANGE_LAYER'):
                    lay += 1; zs.append(None)
                elif ln.startswith('; filament_density'):
                    try:
                        dens = [float(v) for v in ln.replace('=', ':').split(':', 1)[1].replace(',', ' ').split()]
                    except ValueError:
                        dens = None
                elif ver is None and 'BambuStudio' in ln:
                    ver = ln.strip()[:80]
                continue
            s = ln.split(';', 1)[0].strip()
            if not s:
                continue
            h.update(s.encode()); h.update(b'\n'); nlines += 1
            if lay >= 0 and zs[lay] is None:
                zs[lay] = z
            c = s[:3]
            if s.startswith('M83'):
                rel = True; continue
            if s.startswith('M82'):
                rel = False; continue
            if s[0] == 'T' and s[1:].isdigit():
                tool = int(s[1:]); continue
            if c in ('G1 ', 'G0 ', 'G2 ', 'G3 '):
                nx, ny, e = x, y, None; moved = False
                for tok in s.split()[1:]:
                    k = tok[0]
                    if k == 'X':
                        nx = float(tok[1:]); moved = True
                    elif k == 'Y':
                        ny = float(tok[1:]); moved = True
                    elif k == 'E':
                        e = float(tok[1:])
                if e is not None and e > 0 and moved and rel and lay >= 0:
                    mx = (x + nx) / 2; my = (y + ny) / 2; part = '_plate'
                    for (nm, x0, x1, y0, y1) in boxes:
                        if x0 <= mx <= x1 and y0 <= my <= y1:
                            part = nm; break
                    v = e * FA; kk = '%s|T%d' % (feat, tool)
                    d = K.setdefault(part, {}); d[kk] = d.get(kk, 0.0) + v
                    r = LZ.setdefault(part, {}).setdefault(lay, [0.0] * 6)
                    if _own(feat):
                        r[0] += v
                    if feat == 'Top surface':
                        r[1] += v
                    elif feat == 'Bottom surface':
                        r[2] += v
                    elif feat == 'Bridge':
                        r[3] += v
                    elif feat == 'Support interface':
                        r[4] += v
                    elif 'upport' in feat:
                        r[5] += v
                x, y = nx, ny
    out = {'job': os.path.basename(a['job']), 'sha_moves': h.hexdigest(), 'lines': nlines, 'layers': lay + 1, 'z': zs, 'density': dens, 'slicer': ver,
           'kinds': {p: {k: round(v, 3) for k, v in d.items()} for p, d in K.items()},
           'layers_by_part': {p: {str(i): [round(c, 4) for c in r] for i, r in d.items()} for p, d in LZ.items()}, 's': round(time.time() - t0, 1)}
    _wr(a['out'], out)
    print('gsum %s: %d lines, %d layers, sha %s, slicer %s, density %s, parts %s | %.1f s' % (
        out['job'], nlines, lay + 1, out['sha_moves'][:16], ver, dens, sorted(K), time.time() - t0))


def _tot(kinds, own=None):
    t = {'own': 0.0, 'support': 0.0, 'interface': 0.0, 'tower': 0.0, 'brim': 0.0}
    for k, v in kinds.items():
        f = k.split('|')[0]
        if f == 'Support interface':
            t['interface'] += v
        elif 'upport' in f:
            t['support'] += v
        elif 'Prime tower' in f or 'Wipe' in f:
            t['tower'] += v
        elif 'Brim' in f or 'Skirt' in f:
            t['brim'] += v
        elif _own(f):
            t['own'] += v
    return t


def cmd_gcmp(a):
    A = json.load(open(a['a'])); B = json.load(open(a['b'])); tl = a.get('tol_layer', 0.5); tr = a.get('tol_rel', 0.005)
    sc = a.get('scale', 1.0)                 # B's volumes times this (one filament's flow against another's)
    if sc != 1.0:
        B['kinds'] = {p: {k: v * sc for k, v in d.items()} for p, d in B['kinds'].items()}
        B['layers_by_part'] = {p: {i: [c * sc for c in r] for i, r in d.items()} for p, d in B['layers_by_part'].items()}
        print('gcmp: the second slice\'s volumes are taken times %.4f' % sc)
    same = A['sha_moves'] == B['sha_moves']
    print('gcmp %s: %s vs %s | identity: %s (%d / %d lines; %d / %d layers) | slicers %s / %s' % (
        a.get('label', ''), A['job'], B['job'], 'THE SAME G-CODE' if same else 'differs', A['lines'], B['lines'], A['layers'], B['layers'],
        (A['slicer'] or '')[-12:], (B['slicer'] or '')[-12:]))
    pmap = a.get('parts') or [[p, p] for p in sorted(set(A['kinds']) & set(B['kinds']))]
    res = {'label': a.get('label'), 'identity': same, 'parts': {}}
    for pa, pb in pmap:
        ka = A['kinds'].get(pa, {}); kb = B['kinds'].get(pb, {}); ta = _tot(ka); tb = _tot(kb)
        la = A['layers_by_part'].get(pa, {}); lb = B['layers_by_part'].get(pb, {})
        n = max([int(i) for i in la] + [int(i) for i in lb] + [0]) + 1
        bad = []; flags = {'top': [], 'bottom': [], 'bridge': [], 'interface': []}
        for i in range(n):
            ra = la.get(str(i), [0.0] * 6); rb = lb.get(str(i), [0.0] * 6)
            dz = abs(ra[0] - rb[0])
            if dz > max(tl, tr * max(ra[0], rb[0])):
                bad.append((i, round(ra[0], 2), round(rb[0], 2)))
            for j, nm in ((1, 'top'), (2, 'bottom'), (3, 'bridge'), (4, 'interface')):
                if (ra[j] > 0.05) != (rb[j] > 0.05):
                    flags[nm].append((i, round(ra[j], 2), round(rb[j], 2)))
        d_own = ta['own'] - tb['own']
        r = {'own': [round(ta['own'], 2), round(tb['own'], 2)], 'support': [round(ta['support'], 2), round(tb['support'], 2)],
             'interface': [round(ta['interface'], 2), round(tb['interface'], 2)], 'tower': [round(ta['tower'], 2), round(tb['tower'], 2)],
             'brim': [round(ta['brim'], 2), round(tb['brim'], 2)], 'layers_differ': bad[:40], 'n_layers_differ': len(bad),
             'level_faces_differ': {k: v[:20] for k, v in flags.items()}, 'n_level': {k: len(v) for k, v in flags.items()}}
        res['parts'][pa] = r
        print('   %-10s own %9.2f / %9.2f mm3 (%+.2f, %+.3f %%) | support %8.2f / %8.2f | interface %7.2f / %7.2f | tower %7.2f / %7.2f | brim %6.2f / %6.2f' % (
            pa, ta['own'], tb['own'], d_own, 100.0 * d_own / max(tb['own'], 1e-9), ta['support'], tb['support'], ta['interface'], tb['interface'],
            ta['tower'], tb['tower'], ta['brim'], tb['brim']))
        print('              layers whose own lines differ beyond %.2f mm3 or %.1f %%: %d %s' % (tl, 100 * tr, len(bad), bad[:12]))
        print('              level faces present in one and not the other: top %d, bottom %d, bridge %d, interface %d %s' % (
            len(flags['top']), len(flags['bottom']), len(flags['bridge']), len(flags['interface']),
            {k: v[:6] for k, v in flags.items() if v}))
    if a.get('out'):
        _wr(a['out'], res)


def cmd_holes(a):
    sys.path.insert(0, PC); import cgq
    O = json.load(open(a.get('orient', os.path.join(W, 'out', 'pf91_orient.json'))))
    H = json.load(open(a.get('holes_json', os.path.join(R91, 'out', 'r91_21_holes.json'))))
    ix = cgq.get_index(a['job']); nm = ix['names']
    S = []; Own = []
    for Ly in ix['layers']:
        hh = Ly['hm'] or Ly['hs'] or 0.2; zc = Ly['z'] - hh / 2
        for (x1, y1, x2, y2, w, f) in cgq.segs(Ly):
            k = nm[f]; p = ((x1 + x2) / 2, (y1 + y2) / 2, zc, math.hypot(x2 - x1, y2 - y1) * w * hh)
            if 'upport' in k:
                S.append(p)
            elif _own(k):
                Own.append(p)
    dmax = a.get('dmax', 8.5); rows = []
    todo = []
    for mesh, pos in a.get('parts', []):
        M = O[mesh]['M']
        for h in H.get(a.get('key', {}).get(mesh, mesh), []):
            if not h['hole'] or h['round_deg'] < 170 or h['d'] > dmax:
                continue
            todo.append((mesh, h['d'], h['ends'], h['A'], h['B'], cgq.w2b(M, pos, h['A']), cgq.w2b(M, pos, h['B'])))
    for (lab, A, B, d) in a.get('extra', []):
        todo.append((lab, d, ['given', 'given'], A, B, A, B))
    zmax = max((Ly['z'] for Ly in ix['layers']), default=0.0)
    G = 4.0; GS = {}; GO = {}                # the lines bucketed on a 4 mm grid in x and y, so that each hole reads only its neighbourhood
    for (pts, g) in ((S, GS), (Own, GO)):
        for p in pts:
            g.setdefault((int(p[0] // G), int(p[1] // G)), []).append(p)

    def near(g, A, B, pad):
        x0 = int((min(A[0], B[0]) - pad) // G); x1 = int((max(A[0], B[0]) + pad) // G)
        y0 = int((min(A[1], B[1]) - pad) // G); y1 = int((max(A[1], B[1]) + pad) // G)
        for i in range(x0, x1 + 1):
            for j in range(y0, y1 + 1):
                for p in g.get((i, j), ()):
                    yield p
    for (mesh, d, ends, wa, wb, A, B) in todo:
        ax = [B[i] - A[i] for i in range(3)]; La = math.sqrt(sum(c * c for c in ax)) or 1e-9; u = [c / La for c in ax]
        r = d / 2 - 0.05; v = 0.0; n = 0; own_ring = 0.0; tmin = None; tmax = None
        for (x, y, z, vol) in near(GS, A, B, d / 2 + 0.5):
            q = [x - A[0], y - A[1], z - A[2]]; t = sum(q[i] * u[i] for i in range(3))
            if t < 0 or t > La:
                continue
            rr = math.sqrt(max(0.0, sum(c * c for c in q) - t * t))
            if rr <= r:
                v += vol; n += 1; tmin = t if tmin is None else min(tmin, t); tmax = t if tmax is None else max(tmax, t)
        for (x, y, z, vol) in near(GO, A, B, d / 2 + 2.0):
            q = [x - A[0], y - A[1], z - A[2]]; t = sum(q[i] * u[i] for i in range(3))
            if t < 0 or t > La:
                continue
            rr = math.sqrt(max(0.0, sum(c * c for c in q) - t * t))
            if d / 2 <= rr <= d / 2 + 1.2:
                own_ring += vol
        inside = min(A[2], B[2]) <= zmax
        rows.append({'part': mesh, 'd': d, 'ends': ends, 'world': [wa, wb], 'bed': [[round(c, 2) for c in A], [round(c, 2) for c in B]], 'len': round(La, 2),
                     'support_mm3': round(v, 2), 'lines': n, 't_range': [round(tmin, 2), round(tmax, 2)] if tmin is not None else None,
                     'own_ring_mm3': round(own_ring, 1), 'in_print': inside})
    flag = [r for r in rows if r['support_mm3'] > 0.3]
    print('holes %s: %d support lines, %d own lines; %d holes read; support over 0.3 mm3 in %d' % (os.path.basename(a['job']), len(S), len(Own), len(rows), len(flag)))
    for r in rows:
        print('   %-11s d %.2f %-18s len %5.2f bed %s -> %s | support %6.2f mm3 (%d lines%s) | own lines in the ring %7.1f mm3%s' % (
            r['part'], r['d'], '/'.join(r['ends']), r['len'], r['bed'][0], r['bed'][1], r['support_mm3'], r['lines'],
            (', along the axis %.2f to %.2f' % tuple(r['t_range'])) if r['t_range'] else '', r['own_ring_mm3'], '' if r['in_print'] else ' (above the print)'))
    if a.get('out'):
        _wr(a['out'], rows)


def cmd_hprof(a):
    """One hole along its axis in bands of 'step': the support inside (radius less 0.05), the part's own lines in a ring 0 to 1.2
    outside, and how much of the ring's round they cover (of 12 sectors): a walled band has 10 or more. args: job, A, B (bed), d, step."""
    sys.path.insert(0, PC); import cgq
    ix = cgq.get_index(a['job']); nm = ix['names']; A = a['A']; B = a['B']; d = a['d']; st = a.get('step', 1.0)
    ax = [B[i] - A[i] for i in range(3)]; La = math.sqrt(sum(c * c for c in ax)); u = [c / La for c in ax]
    e1 = [1.0, 0.0, 0.0] if abs(u[0]) < 0.9 else [0.0, 1.0, 0.0]
    v1 = [e1[i] - u[i] * sum(e1[k] * u[k] for k in range(3)) for i in range(3)]; m = math.sqrt(sum(c * c for c in v1)); v1 = [c / m for c in v1]
    v2 = [u[1] * v1[2] - u[2] * v1[1], u[2] * v1[0] - u[0] * v1[2], u[0] * v1[1] - u[1] * v1[0]]
    nb = int(math.ceil(La / st)); sup = [0.0] * nb; ring = [0.0] * nb; sec = [set() for _ in range(nb)]
    for Ly in ix['layers']:
        hh = Ly['hm'] or Ly['hs'] or 0.2; zc = Ly['z'] - hh / 2
        for (x1, y1, x2, y2, w, f) in cgq.segs(Ly):
            k = nm[f]; x = (x1 + x2) / 2; y = (y1 + y2) / 2; vol = math.hypot(x2 - x1, y2 - y1) * w * hh
            q = [x - A[0], y - A[1], zc - A[2]]; t = sum(q[i] * u[i] for i in range(3))
            if t < 0 or t >= La:
                continue
            p1 = sum(q[i] * v1[i] for i in range(3)); p2 = sum(q[i] * v2[i] for i in range(3)); rr = math.hypot(p1, p2); b = min(nb - 1, int(t / st))
            if 'upport' in k and rr <= d / 2 - 0.05:
                sup[b] += vol
            elif _own(k) and d / 2 <= rr <= d / 2 + 1.2:
                ring[b] += vol; sec[b].add(int(((math.atan2(p2, p1) + math.pi) / (2 * math.pi)) * 12) % 12)
    print('hprof %s: hole d %.2f, bed %s -> %s, %.2f long, bands of %.2f' % (os.path.basename(a['job']), d, A, B, La, st))
    for b in range(nb):
        print('   t %5.2f..%5.2f  support %7.2f mm3 | own ring %7.2f mm3, %2d of 12 sectors %s' % (b * st, min(La, (b + 1) * st), sup[b], ring[b], len(sec[b]), 'walled' if len(sec[b]) >= 10 else 'OPEN'))


def cmd_hseg(a):
    """The support lines whose middle lies inside one hole (radius less 0.05): by kind and layer, and the first 'show' of them.
    args: job, A, B (bed), d, show."""
    sys.path.insert(0, PC); import cgq
    ix = cgq.get_index(a['job']); nm = ix['names']; A = a['A']; B = a['B']; d = a['d']
    ax = [B[i] - A[i] for i in range(3)]; La = math.sqrt(sum(c * c for c in ax)); u = [c / La for c in ax]; out = []; by = {}
    for Ly in ix['layers']:
        hh = Ly['hm'] or Ly['hs'] or 0.2; zc = Ly['z'] - hh / 2
        for (x1, y1, x2, y2, w, f) in cgq.segs(Ly):
            k = nm[f]
            if 'upport' not in k:
                continue
            x = (x1 + x2) / 2; y = (y1 + y2) / 2; q = [x - A[0], y - A[1], zc - A[2]]; t = sum(q[i] * u[i] for i in range(3))
            if t < 0 or t > La:
                continue
            rr = math.sqrt(max(0.0, sum(c * c for c in q) - t * t))
            if rr <= d / 2 - 0.05:
                vol = math.hypot(x2 - x1, y2 - y1) * w * hh; key = (k, round(Ly['z'], 2)); by[key] = by.get(key, 0.0) + vol
                out.append((round(Ly['z'], 2), k, round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2), round(w, 2), round(t, 2), round(rr, 2)))
    print('hseg %s: hole d %.2f bed %s -> %s: %d support lines inside' % (os.path.basename(a['job']), d, A, B, len(out)))
    for (k, z), v in sorted(by.items(), key=lambda kv: kv[0][1]):
        print('   layer top %6.2f  %-18s %6.2f mm3' % (z, k, v))
    for s in out[:a.get('show', 20)]:
        print('   z %.2f %-18s (%.2f, %.2f) -> (%.2f, %.2f) w %.2f | t %.2f, r %.2f' % s)
    if a.get('out'):
        _wr(a['out'], {'A': A, 'B': B, 'd': d, 'lines': out})


def cmd_png(a):
    """A plate seen from above: every extruding line of the slice (or of the layers between z0 and z1), drawn at ppm pixels a mm,
    coloured by kind (the part's own lines grey, the latest layer's darker; support red; interface orange; prime tower blue; brim and
    skirt green); the bed's edge and a 10 mm grid. args: job, out (png), ppm, z0, z1, x0, x1, y0, y1 (bed mm), title."""
    import zlib, struct
    ppm = a.get('ppm', 3.0); x0, x1, y0, y1 = a.get('x0', 0.0), a.get('x1', 350.0), a.get('y0', 0.0), a.get('y1', 320.0)
    z0, z1 = a.get('z0', -1.0), a.get('z1', 1e9)
    Wd = int((x1 - x0) * ppm) + 1; Hh = int((y1 - y0) * ppm) + 1
    img = bytearray(b'\xff' * (Wd * Hh * 3))
    def put(px, py, c):
        if 0 <= px < Wd and 0 <= py < Hh:
            i = ((Hh - 1 - py) * Wd + px) * 3; img[i:i + 3] = c
    for gx in range(int(x0 // 10) * 10, int(x1) + 1, 10):
        for py in range(Hh):
            put(int((gx - x0) * ppm), py, b'\xe4\xe4\xe4')
    for gy in range(int(y0 // 10) * 10, int(y1) + 1, 10):
        for px in range(Wd):
            put(px, int((gy - y0) * ppm), b'\xe4\xe4\xe4')
    COL = {'own': b'\x9a\x9a\x9a', 'sup': b'\xd0\x30\x30', 'if': b'\xf0\x90\x10', 'tower': b'\x30\x60\xd0', 'brim': b'\x20\xa0\x40'}
    feat = 'none'; z = 0.0; x = y = 0.0; n = 0
    with open(os.path.join(a['job'], 'plate_1.gcode'), errors='replace') as f:
        for ln in f:
            if ln.startswith(';'):
                if ln.startswith('; FEATURE: '):
                    feat = ln[11:].strip()
                elif ln.startswith('; Z_HEIGHT: '):
                    z = float(ln[12:])
                continue
            s = ln.split(';', 1)[0].strip()
            if s[:3] not in ('G1 ', 'G0 ', 'G2 ', 'G3 '):
                continue
            nx, ny, e = x, y, None
            for tok in s.split()[1:]:
                if tok[0] == 'X':
                    nx = float(tok[1:])
                elif tok[0] == 'Y':
                    ny = float(tok[1:])
                elif tok[0] == 'E':
                    e = float(tok[1:])
            if e is not None and e > 0 and z0 <= z <= z1:
                k = 'if' if feat == 'Support interface' else 'sup' if 'upport' in feat else 'tower' if ('Prime' in feat or 'Wipe' in feat) else 'brim' if ('Brim' in feat or 'Skirt' in feat) else 'own'
                c = COL[k]; L_ = max(1, int(math.hypot(nx - x, ny - y) * ppm))
                for i in range(L_ + 1):
                    t = i / L_; put(int((x + (nx - x) * t - x0) * ppm), int((y + (ny - y) * t - y0) * ppm), c)
                n += 1
            x, y = nx, ny
    raw = b''.join(b'\x00' + bytes(img[r * Wd * 3:(r + 1) * Wd * 3]) for r in range(Hh))
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', Wd, Hh, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')
    if not os.path.abspath(a['out']).startswith(W + os.sep):
        raise RuntimeError('refused, outside the work folder: ' + a['out'])
    open(a['out'], 'wb').write(png)
    print('png %s: %d lines drawn, %d x %d px, bed x %.0f..%.0f y %.0f..%.0f, z %.2f..%.2f' % (os.path.basename(a['out']), n, Wd, Hh, x0, x1, y0, y1, z0, min(z1, 999)))


if __name__ == '__main__':
    cmd = sys.argv[1]; arg = sys.argv[2]
    A = json.load(open(arg)) if os.path.exists(arg) else json.loads(arg)
    for a in (A if isinstance(A, list) else [A]):
        try:
            {'gsum': cmd_gsum, 'gcmp': cmd_gcmp, 'holes': cmd_holes, 'png': cmd_png, 'hprof': cmd_hprof, 'hseg': cmd_hseg}[a.get('cmd', cmd)](a)
        except Exception:
            import traceback
            print('ERROR', json.dumps(a)[:300]); traceback.print_exc()
        sys.stdout.flush()
# END pf91_tools.py
