# pf67_1b_cmp (block 1). Touches no Fusion object. Compares each fresh bed mesh (print_files_v67/_work/orient/<tag>_plan.stl)
#   with the re-check's print-file-grade bed mesh of version 67 (print_audit_recheck3/orient_hr/<tag>_plan.stl):
#   - in file order: the largest vertex difference and how many triangles differ by more than 0.001 mm;
#   - regardless of order: whether the sets of triangles (vertices rounded to 0.001 mm, each triangle's vertices rotated to
#     start at its smallest) are equal;
#   - mesh volume and bounds of both. Pure Python (struct). Stops after about 35 s; the next call continues.


def r2_tris(p):
    b = open(p, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]
    return b, n


def r2_key(f):
    a = (round(f[3], 3), round(f[4], 3), round(f[5], 3)); b = (round(f[6], 3), round(f[7], 3), round(f[8], 3))
    c = (round(f[9], 3), round(f[10], 3), round(f[11], 3))
    m = min(a, b, c)
    return (a, b, c) if m == a else ((b, c, a) if m == b else (c, a, b))


def run(_context):
    t0 = time.time()
    recp = os.path.join(R2_DIR, 'data', 'pf67_1b_cmp.json')
    out = json.load(open(recp)) if os.path.exists(recp) else {}
    tags = [t for t, _ in R2_PRINTS] + ['shell_chin8']
    for tag in tags:
        if tag in out:
            continue
        if time.time() - t0 > 35:
            break
        p = os.path.join(R2_DIR, 'orient', tag + '_plan.stl'); q = os.path.join(R2_RC3, 'orient_hr', tag + '_plan.stl')
        if not (os.path.exists(p) and os.path.exists(q)):
            continue
        b1, n1 = r2_tris(p); b2, n2 = r2_tris(q)
        r = {'tris': [n1, n2]}
        if n1 == n2:
            dm = 0.0; nd = 0; k1 = []; k2 = []
            for t in range(n1):
                f1 = struct.unpack_from('<12f', b1, 84 + 50 * t); f2 = struct.unpack_from('<12f', b2, 84 + 50 * t)
                d = max(abs(f1[k] - f2[k]) for k in range(3, 12))
                if d > dm: dm = d
                if d > 0.001: nd += 1
                k1.append(r2_key(f1)); k2.append(r2_key(f2))
            k1.sort(); k2.sort()
            r['in_order_dmax'] = round(dm, 6); r['in_order_tris_differing'] = nd
            r['same_set'] = (k1 == k2)
        out[tag] = r
        r2_out(recp, out)
    left = [t for t in tags if t not in out]
    print(json.dumps({'left': left, 's': round(time.time() - t0, 1), 'cmp': out}, separators=(',', ':')))
