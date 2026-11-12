# rev F k3b (2026-11-12): fix pass, block 3 - the leads' record and their checks. Run through k.step(sha, name, h256, kl=...).
#   The library is the global k, the lead tools kl (the namespace of v5f_k3a_leads.py).
#   The routes of all 16 leads are data, in k3_routes.json beside this file: {name: [radius, [nodes]]}, node frames as in k3a.
#   load()     the routes of a commit into k.c['routes']; returns the names whose route differs from the one in memory
#   rebuild()  a lead's body made again from its route (replaced in place; the lead of version 55 stays as <name>_v55)
#   scan()     every lead against every other current body within a distance: the distance, where, and the overlap if they touch
#   pairs()    the rows of a scan for some kinds of body, nearest first, each pair of leads once
import json
import adsk.core

PLUGS = ('PIPWR_a_env', 'USBA_cable_env', 'MAIN_conn', 'LCD_2x2_header_d15.4', 'LCD_DSI_conn_d9.3', 'LCD_pogo_header_d14.1',
         'LCD_panelFPC_conn_d9.5', 'LCD_touchFPC_conn_d9.3')


def kind(n):
    if n.startswith('LEAD_'):
        return 'lead'
    if n.startswith(('KO_', 'AUD_key')):
        return 'key'
    if 'plug' in n.lower() or n in PLUGS:
        return 'plug'
    return 'body'


def same(a, b):                                      # two routes equal to 0.005
    if abs(a[0] - b[0]) > 1e-9 or len(a[1]) != len(b[1]):
        return False
    return all(p[0] == q[0] and all(abs(p[i] - q[i]) < 0.005 for i in (1, 2, 3)) for p, q in zip(a[1], b[1]))


def load(sha, h256=None):
    new = json.loads(k.fetch(sha, 'k3_routes.json', h256))
    old = k.c.get('routes') or {}
    diff = sorted(n for n in set(new) | set(old) if n not in new or n not in old or not same(new[n], old[n]))
    k.c['routes'] = new
    return diff


def rebuild(X, name, suffix='_v55'):
    r, nodes = k.c['routes'][name]
    old = X.body(name)
    if old is None:
        raise RuntimeError('no lead ' + name)
    t = kl['rope'](X, r, nodes)
    if X.body(name + suffix) is None:
        b = X.swap(name, t, suffix, show=False)
    else:
        old.name = name + '_out'
        b = X.add(t, name, like=old, show=False)
        old.deleteMe()
    return b, round(kl['length'](nodes), 1), round(b.volume * 1000.0, 1)


def scan(X, lim=3.0, extra=('AUD_keyL', 'AUD_keyR'), only=None):
    cur = k.current(X, leads=True) + [b for b in (X.body(n) for n in extra) if b is not None]
    res = k.c.setdefault('k3b', {})
    e = lim / 10.0
    for a in sorted((b for b in cur if b.name.startswith('LEAD_')), key=lambda b: b.name):
        key = (a.name, round(a.volume, 6), lim)
        if (only and a.name not in only) or key in res:
            continue
        if k.late():
            return None
        q = a.boundingBox
        box = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e),
                                             k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
        rows = []
        for o in cur:
            if o.name == a.name or not box.intersects(o.boundingBox):
                continue
            m = X.mm.measureMinimumDistance(a, o); d = m.value * 10.0
            if d > lim:
                continue
            v = 0.0; at = None
            if d < 0.005:
                if o.name in k.BIG:
                    v = k.xvol(X, X.tbm.copy(a), o.name)
                else:
                    t = X.tbm.copy(a)
                    X.tbm.booleanOperation(t, k.tcopy(X, o.name), k.BT.IntersectionBooleanType)
                    v = X.vol(t)
                    L = X.lumps(t) if v > 0.0005 else []
                    at = L[0][1] if L else None
            else:
                at = k.r2(k.W(m.positionOne), 1)
            rows.append([round(d, 2), round(v, 2), o.name, kind(o.name), at])
        res[key] = sorted(rows, key=lambda t: (t[0], -t[1]))
    out = {}
    for q in res:
        b = X.body(q[0])
        if q[2] == lim and b is not None and round(b.volume, 6) == q[1] and (not only or q[0] in only):
            out[q[0]] = res[q]
    return out


def pairs(res, kinds):
    out = []
    for a in sorted(res):
        for d, v, o, kd, at in res[a]:
            if kd not in kinds or (kd == 'lead' and o < a):
                continue
            out.append((d, v, a, o, at))
    return sorted(out, key=lambda t: (t[0], -t[1]))
