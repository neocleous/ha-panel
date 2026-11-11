"""Read a KiCad 9 board file into plain Python structures (read-only analysis)."""
import re, sys, math, json

def parse(text):
    tok = re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+')
    stack = [[]]
    for m in tok.finditer(text):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        elif t[0] == '"':
            stack[-1].append(('S', t[1:-1].replace('\\"', '"').replace('\\\\', '\\')))
        else:
            stack[-1].append(t)
    return stack[0][0]

def s(x):
    return x[1] if isinstance(x, tuple) else x

def find(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]

def first(node, name):
    r = find(node, name)
    return r[0] if r else None

def load(path):
    root = parse(open(path).read())
    nets = {}
    for n in find(root, 'net'):
        nets[int(n[1])] = s(n[2])
    segs = []
    for sg in find(root, 'segment') + find(root, 'arc'):
        a = first(sg, 'start'); b = first(sg, 'end')
        segs.append(dict(x1=float(a[1]), y1=float(a[2]), x2=float(b[1]), y2=float(b[2]),
                         w=float(first(sg, 'width')[1]), layer=s(first(sg, 'layer')[1]),
                         net=nets[int(first(sg, 'net')[1])]))
    vias = []
    for v in find(root, 'via'):
        a = first(v, 'at')
        vias.append(dict(x=float(a[1]), y=float(a[2]), size=float(first(v, 'size')[1]),
                         drill=float(first(v, 'drill')[1]), layers=[s(l) for l in first(v, 'layers')[1:]],
                         net=nets[int(first(v, 'net')[1])]))
    fps = {}
    for fp in find(root, 'footprint'):
        at = first(fp, 'at'); x, y = float(at[1]), float(at[2]); rot = float(at[3]) if len(at) > 3 else 0.0
        ref = val = None
        for p in find(fp, 'property'):
            if s(p[1]) == 'Reference': ref = s(p[2])
            if s(p[1]) == 'Value': val = s(p[2])
        layer = s(first(fp, 'layer')[1])
        pads = []
        th = math.radians(rot)
        for pd in find(fp, 'pad'):
            pat = first(pd, 'at'); px, py = float(pat[1]), float(pat[2])
            prot = float(pat[3]) if len(pat) > 3 else 0.0
            # KiCad: footprint-local to board: rotate by -rot (y down)
            gx = x + px * math.cos(th) + py * math.sin(th)
            gy = y - px * math.sin(th) + py * math.cos(th)
            sz = first(pd, 'size'); net = first(pd, 'net'); dr = first(pd, 'drill')
            drill = None
            if dr:
                nums = [float(t) for t in dr[1:] if isinstance(t, str) and re.match(r'^-?[\d.]+$', t)]
                drill = nums
            sx, sy = float(sz[1]), float(sz[2])
            rel = (prot - rot) % 180
            if abs(prot % 180 - 90) < 1e-6:   # pad rotation is absolute in file (includes fp rot)
                sx, sy = sy, sx
            pads.append(dict(n=s(pd[1]), type=s(pd[2]), shape=s(pd[3]), x=gx, y=gy, sx=sx, sy=sy,
                             drill=drill, net=(s(net[2]) if net else None),
                             layers=[s(l) for l in first(pd, 'layers')[1:]]))
        # courtyard
        cx = []
        for g in find(fp, 'fp_line') + find(fp, 'fp_rect') + find(fp, 'fp_poly') + find(fp, 'fp_circle'):
            lay = first(g, 'layer')
            if not lay or 'CrtYd' not in s(lay[1]): continue
            pts = []
            for key in ('start', 'end'):
                q = first(g, key)
                if q: pts.append((float(q[1]), float(q[2])))
            pp = first(g, 'pts')
            if pp:
                for q in find(pp, 'xy'): pts.append((float(q[1]), float(q[2])))
            if g[0] == 'fp_circle':
                c = first(g, 'center'); e = first(g, 'end')
                r = math.hypot(float(e[1]) - float(c[1]), float(e[2]) - float(c[2]))
                cxx, cyy = float(c[1]), float(c[2])
                pts = [(cxx - r, cyy - r), (cxx + r, cyy + r), (cxx - r, cyy + r), (cxx + r, cyy - r)]
            for (px, py) in pts:
                cx.append((x + px * math.cos(th) + py * math.sin(th), y - px * math.sin(th) + py * math.cos(th)))
        crt = None
        if cx:
            crt = (min(p[0] for p in cx), min(p[1] for p in cx), max(p[0] for p in cx), max(p[1] for p in cx))
        fps[ref] = dict(ref=ref, value=val, fp=s(fp[1]), x=x, y=y, rot=rot, layer=layer, pads=pads, crt=crt)
    zones = []
    for z in find(root, 'zone'):
        net = int(first(z, 'net')[1]); nm = s(first(z, 'net_name')[1])
        lay = first(z, 'layer'); lays = first(z, 'layers')
        ls = [s(lay[1])] if lay else [s(l) for l in lays[1:]]
        poly = first(z, 'polygon'); pts = [(float(q[1]), float(q[2])) for q in find(first(poly, 'pts'), 'xy')]
        fills = []
        for fpoly in find(z, 'filled_polygon'):
            fl = s(first(fpoly, 'layer')[1])
            fp_pts = [(float(q[1]), float(q[2])) for q in find(first(fpoly, 'pts'), 'xy')]
            fills.append((fl, fp_pts))
        ko = first(z, 'keepout')
        zones.append(dict(net=nm, layers=ls, outline=pts, fills=fills, keepout=bool(ko), name=(s(first(z,'name')[1]) if first(z,'name') else '')))
    edge = []
    for g in find(root, 'gr_line') + find(root, 'gr_rect'):
        lay = first(g, 'layer')
        if lay and s(lay[1]) == 'Edge.Cuts':
            a = first(g, 'start'); b = first(g, 'end')
            edge.append((float(a[1]), float(a[2]), float(b[1]), float(b[2])))
    return dict(nets=nets, segs=segs, vias=vias, fps=fps, zones=zones, edge=edge, root=root)

U0, V0 = 43.5, 28.95
def uv(x, y):
    return (x - U0, V0 - y)
