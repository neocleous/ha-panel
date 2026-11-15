"""Shared loaders for the ballast study (sections of version 65, world mm)."""
import json, math
import shapely
from shapely.geometry import Polygon, box, LineString, Point
from shapely.ops import unary_union, polygonize

DATA = '/mnt/user-data/uploads/ballast'
_secs = None; _floor = None

def region(edges):
    polys = list(polygonize(unary_union([LineString(p) for p in edges if len(p) >= 2])))
    return unary_union(polys).buffer(0) if polys else Polygon()

def secs():
    global _secs
    if _secs is None:
        S = json.load(open(DATA + '/sections_v65.json'))
        _secs = {float(lv): {n: region(e) for n, e in d.items()} for lv, d in S['levels'].items()}
    return _secs

def floor():
    global _floor
    if _floor is None:
        F = json.load(open(DATA + '/plate_faces_v65.json'))
        _floor = region(F['2.50'][0]['edges'])
    return _floor

def filled(g):
    gs = g.geoms if hasattr(g, 'geoms') else [g]
    return unary_union([Polygon(p.exterior) for p in gs if p.geom_type == 'Polygon'])

KEEP = {
    'intake field': box(-43.25, -59.7, 41.75, -4.7),
    'microSD finger channel': box(-64.0, -84.0, -44.0, -24.0),
    'anchor and its tie': box(53.0, -61.0, 64.0, -52.0),
}

def obstacles(z):
    d = secs()[z]
    return unary_union([filled(g) if n.startswith('SPKBOX') else g for n, g in d.items()])

def free_col(z0, z1, clear=0.3, keep=True, exclude=()):
    """Floor area free of every body over the whole height z0..z1 (levels inside, plus the next one up)."""
    lv = sorted(secs())
    use = [z for z in lv if z0 < z <= z1]
    above = [z for z in lv if z > z1]
    if above:
        use.append(above[0])
    obs = [obstacles(z) for z in use]
    if keep:
        obs += [g for n, g in KEEP.items() if n not in exclude]
    free = floor().difference(unary_union(obs))
    return free.buffer(-clear).buffer(clear * 0.999) if clear > 0 else free

# tipping on the D9 base (D156), version 65
BASE = dict(m=1055.101, cog=(-0.810, -17.836, 79.671))
C12, S12 = math.cos(math.radians(12.0)), math.sin(math.radians(12.0))
GT = (-6.67, 174.67); SC = (5.70, 116.47); DOORY = -84.0
FEET = dict(yr=-70.6, yf=-5.5, r=6.35, zp=-3.0)

def add(parts, base=BASE):
    m = base['m']; s = [base['m'] * c for c in base['cog']]
    for g, (x, y, z) in parts:
        m += g; s[0] += g * x; s[1] += g * y; s[2] += g * z
    return m, [v / m for v in s]

def figs(m, cog, feet=FEET):
    yr, yf, r, zp = feet['yr'], feet['yf'], feet['r'], feet['zp']
    Wn = m / 1000.0 * 9.81; o = {}
    for lab, yp in (('centres', yr), ('edges', yr - r)):
        M = Wn * (cog[1] - yp) / 1000.0
        o['back top horizontal ' + lab] = M / ((GT[1] - zp) / 1000.0)
        o['back top normal ' + lab] = M / (((GT[1] - zp) * C12 - (GT[0] - yp) * S12) / 1000.0)
        o['back centre normal ' + lab] = M / (((SC[1] - zp) * C12 - (SC[0] - yp) * S12) / 1000.0)
        o['back tips at deg ' + lab] = math.degrees(math.atan2(cog[1] - yp, cog[2] - zp))
    for lab, yp in (('centres', yf), ('edges', yf + r)):
        M = Wn * (yp - cog[1]) / 1000.0
        o['fwd tips at deg ' + lab] = math.degrees(math.atan2(yp - cog[1], cog[2] - zp))
        o['fwd pull top ' + lab] = M / ((GT[1] - zp) / 1000.0)
        o['fwd lift door foot ' + lab] = M / ((yp - DOORY) / 1000.0)
    o['rear share %'] = 100.0 * (yf - cog[1]) / (yf - yr)
    return o

if __name__ == '__main__':
    for kk, v in figs(BASE['m'], BASE['cog']).items():
        print('%-32s %.3f' % (kk, v))
