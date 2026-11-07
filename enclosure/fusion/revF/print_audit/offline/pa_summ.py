# HA panel print audit: summarise L_<tag>_<orient>.json - unsupported regions (60 deg) clustered across layers, islands, layer
#   areas, with world (x_rel, y, z) boxes. Usage: python3 pa_summ.py <tag> <orient> [min_cluster_area_mm2]
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_geom import b2w


def wbox(M, bb, z0, z1):
    xs = (bb[0], bb[1]); ys = (bb[2], bb[3]); zz = (z0, z1)
    pts = np.array([(x, y, z) for x in xs for y in ys for z in zz])
    w = b2w(np.array(M), pts)
    return [round(float(w[:, 0].min()), 1), round(float(w[:, 0].max()), 1), round(float(w[:, 1].min()), 1),
            round(float(w[:, 1].max()), 1), round(float(w[:, 2].min()), 1), round(float(w[:, 2].max()), 1)]


def clusters(regs, slack=0.3):
    par = list(range(len(regs)))

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    byk = {}
    for i, r in enumerate(regs):
        byk.setdefault(r['k'], []).append(i)
    for i, r in enumerate(regs):
        for j in byk.get(r['k'] + 1, []):
            a, b = r['bbox'], regs[j]['bbox']
            if a[0] - slack <= b[1] and b[0] - slack <= a[1] and a[2] - slack <= b[3] and b[2] - slack <= a[3]:
                par[f(j)] = f(i)
    cl = {}
    for i in range(len(regs)):
        cl.setdefault(f(i), []).append(regs[i])
    return list(cl.values())


def summarise(tag, okey, amin=1.0, show=True):
    d = json.load(open('/home/claude/pa/data/L_%s_%s.json' % (tag, okey)))
    M = d['M']
    out = {'tag': tag, 'orient': okey, 'height': round(d['height'], 2), 'n_layers': d['n_layers'],
           'first_layer_area': d.get('first_layer_area'), 'footprint': d['footprint'], 'normals': d['overhang_normals']}
    cls = []
    for c in clusters(d['regions']):
        A = sum(r['area'] for r in c)
        if A < amin:
            continue
        k0 = min(r['k'] for r in c); k1 = max(r['k'] for r in c)
        bb = [min(r['bbox'][0] for r in c), max(r['bbox'][1] for r in c), min(r['bbox'][2] for r in c), max(r['bbox'][3] for r in c)]
        z0 = min(r['z'] for r in c); z1 = max(r['z'] for r in c) + 0.2
        kinds = {}
        for r in c:
            kinds[r['kind']] = round(kinds.get(r['kind'], 0) + r['area'], 1)
        br = [r for r in c if r['kind'] == 'bridge']
        ca = [r for r in c if r['kind'] == 'cantilever']
        bedA = sum(r['area'] * r['bed_frac'] for r in c)
        cls.append({'z': [round(z0, 2), round(z1, 2)], 'layers': k1 - k0 + 1, 'area': round(A, 1), 'kinds': kinds,
                    'bridge_span_max': max([r['dmax'] * 2 for r in br if r['dmax'] is not None], default=None),
                    'bridge_width_max': max([r['width'] for r in br], default=None),
                    'cant_len_max': max([r['dmax'] for r in ca if r['dmax'] is not None], default=None),
                    'land': [min(r['land_min'] for r in c), max(r['land_max'] for r in c)],
                    'bed_frac': round(bedA / A, 2), 'bbox_build': [round(v, 1) for v in bb], 'world': wbox(M, bb, z0, z1)})
    cls.sort(key=lambda c: -c['area'])
    out['clusters'] = cls
    out['total_u60_layers'] = round(sum(L.get('u60', 0) for L in d['layers']), 1)
    out['total_u45_layers'] = round(sum(L.get('u45', 0) for L in d['layers']), 1)
    out['total_u70_layers'] = round(sum(L.get('u70', 0) for L in d['layers']), 1)
    isl = []
    for i in d['islands']:
        isl.append({'z0': i['z0'], 'area': i['area'], 'weak': i['weak'], 'overlap': i['overlap_mm2'], 'land': [i['land_min'], i['land_max']],
                    'bed_frac': i['bed_frac'], 'world': wbox(M, i['bbox'], i['z0'], i['z0'] + 0.2)})
    out['islands'] = isl
    if show:
        print('==', tag, okey, 'h', out['height'], 'layers', out['n_layers'], 'first', out['first_layer_area'], 'fp', out['footprint'])
        print('   normals', out['normals'], 'u45/60/70 sum', out['total_u45_layers'], out['total_u60_layers'], out['total_u70_layers'])
        for i in isl:
            print('   ISLAND', i)
        for c in cls:
            print('   CL', c)
    return out


if __name__ == '__main__':
    tag, okey = sys.argv[1], sys.argv[2]
    amin = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    o = summarise(tag, okey, amin)
    json.dump(o, open('/home/claude/pa/data/S_%s_%s.json' % (tag, okey), 'w'), indent=1)
