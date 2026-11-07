"""python3 gndcheck.py <board> [net]: union-find over zone fills / pads / tracks / vias of one net; prints the
components that are not joined to the largest one (approximate: pad contact by bounding box)."""
import sys
import pcbnew

T = 1e-6
b = pcbnew.LoadBoard(sys.argv[1])
net = sys.argv[2] if len(sys.argv) > 2 else 'GND'
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
par = {}


def find(a):
    while par.setdefault(a, a) != a:
        par[a] = par[par[a]]
        a = par[a]
    return a


def union(a, c):
    par[find(a)] = find(c)


outl = []          # (key, layer, polyset, index, bbox)
for zi, z in enumerate(b.Zones()):
    if z.GetNetname() != net or z.GetIsRuleArea():
        continue
    for lay in CU:
        if not z.IsOnLayer(lay):
            continue
        ps = z.GetFilledPolysList(lay)
        for i in range(ps.OutlineCount()):
            bb = ps.Outline(i).BBox()
            outl.append((('Z', zi, lay, i), lay, ps, i, bb))
            find(('Z', zi, lay, i))


def touch(lay, pos):
    return [k for k, l, ps, i, bb in outl if l == lay and bb.Contains(pos) and ps.Outline(i).PointInside(pos)]


items = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.GetNetname() != net:
            continue
        key = ('P', fp.GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y)
        find(key)
        bbp = p.GetBoundingBox()
        cx, cy = p.GetPosition().x, p.GetPosition().y
        hx, hy = bbp.GetWidth() // 2 + 550000, bbp.GetHeight() // 2 + 550000
        ring = [pcbnew.VECTOR2I(cx, cy)] + [pcbnew.VECTOR2I(cx + dx * hx, cy + dy * hy)
                                            for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy]
        for lay in CU:
            if p.IsOnLayer(lay):
                for q in ring:
                    for k in touch(lay, q):
                        union(key, k)
        items.append((key, p.GetBoundingBox(), [l for l in CU if p.IsOnLayer(l)]))
ends = {}
for t in b.GetTracks():
    if t.GetNetname() != net:
        continue
    if t.GetClass() == 'PCB_VIA':
        key = ('V', t.GetPosition().x, t.GetPosition().y)
        find(key)
        for lay in CU:
            for k in touch(lay, t.GetPosition()):
                union(key, k)
        ends.setdefault(('all', t.GetPosition().x // 1000, t.GetPosition().y // 1000), []).append(key)
        continue
    key = ('T', t.m_Uuid.AsString())
    find(key)
    for q in (t.GetStart(), t.GetEnd()):
        for k in touch(t.GetLayer(), q):
            union(key, k)
        ends.setdefault((t.GetLayer(), q.x // 1000, q.y // 1000), []).append(key)
        ends.setdefault(('all', q.x // 1000, q.y // 1000), []).append(key)
        for pk, bb, lays in items:
            if t.GetLayer() in lays and bb.Contains(q):
                union(key, pk)
for k, lst in ends.items():
    for a in lst[1:]:
        union(lst[0], a)
comps = {}
for k in list(par):
    comps.setdefault(find(k), []).append(k)
big = max(comps.values(), key=len)
for c in comps.values():
    if c is big:
        continue
    pads = [k for k in c if k[0] == 'P']
    zs = [k for k in c if k[0] == 'Z']
    desc = ', '.join('%s.%s' % (k[1], k[2]) for k in pads[:6])
    zb = ''
    for k in zs[:2]:
        for kk, l, ps, i, bb in outl:
            if kk == k:
                zb += ' %s %.1f,%.1f-%.1f,%.1f' % (b.GetLayerName(l), bb.GetX() * T, bb.GetY() * T, bb.GetRight() * T, bb.GetBottom() * T)
    print('island: %d items; pads %s;%s' % (len(c), desc, zb))
