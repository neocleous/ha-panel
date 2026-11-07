"""Minimal KiCad .kicad_pcb reader: footprints (ref, lib name, layer, position, rotation, courtyard points) and Edge.Cuts."""
import re, math
def tokenize(s):
    for m in re.finditer(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s):
        yield m.group(0)
def parse(s):
    stack = [[]]
    for t in tokenize(s):
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t[1:-1] if t.startswith('"') else t)
    return stack[0][0]
def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]
def first(node, key):
    r = find(node, key); return r[0] if r else None
def rot(u, v, deg):
    a = math.radians(deg)
    return (u * math.cos(a) + v * math.sin(a), -u * math.sin(a) + v * math.cos(a))
def footprints(tree):
    out = []
    for fp in find(tree, 'footprint'):
        name = fp[1]; layer = first(fp, 'layer')[1]
        at = first(fp, 'at'); x, y = float(at[1]), float(at[2]); r = float(at[3]) if len(at) > 3 else 0.0
        ref = None
        for p in find(fp, 'property'):
            if p[1] == 'Reference': ref = p[2]
        pts = []
        for kind in ('fp_line', 'fp_rect', 'fp_poly', 'fp_circle', 'fp_arc'):
            for g in find(fp, kind):
                lay = first(g, 'layer')
                if lay is None or not lay[1].endswith('CrtYd'): continue
                if kind == 'fp_poly':
                    for xy in find(first(g, 'pts'), 'xy'): pts.append((float(xy[1]), float(xy[2])))
                elif kind == 'fp_circle':
                    c = first(g, 'center'); e = first(g, 'end'); cx, cy = float(c[1]), float(c[2]); R = math.hypot(float(e[1]) - cx, float(e[2]) - cy)
                    pts += [(cx + R * math.cos(t), cy + R * math.sin(t)) for t in [i * math.pi / 8 for i in range(16)]]
                else:
                    for k in ('start', 'end', 'mid'):
                        q = first(g, k)
                        if q is not None: pts.append((float(q[1]), float(q[2])))
        gpts = [(x + a, y + b) for (a, b) in (rot(u, v, r) for (u, v) in pts)]
        pads = []
        for pd in find(fp, 'pad'):
            pa = first(pd, 'at'); u, v = float(pa[1]), float(pa[2]); a, b = rot(u, v, r)
            pads.append((pd[1], pd[2], x + a, y + b))
        out.append(dict(ref=ref, name=name, layer=layer, x=x, y=y, r=r, crt=gpts, pads=pads))
    return out
def edge_cuts(tree):
    segs = []
    for kind in ('gr_line', 'gr_rect', 'gr_poly', 'gr_arc'):
        for g in find(tree, kind):
            lay = first(g, 'layer')
            if lay and lay[1] == 'Edge.Cuts':
                if kind == 'gr_poly':
                    segs.append(('poly', [(float(p[1]), float(p[2])) for p in find(first(g, 'pts'), 'xy')]))
                else:
                    segs.append((kind, [(float(first(g, k)[1]), float(first(g, k)[2])) for k in ('start', 'end') if first(g, k)]))
    return segs
