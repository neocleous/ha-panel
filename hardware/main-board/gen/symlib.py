"""Load KiCad library symbols (flattening 'extends') and report pin geometry."""
import copy
import os
from sexpr import parse, find, findall, Sym

SYS_DIR = '/usr/share/kicad/symbols'
_cache = {}
EXTRA_LIBS = {}   # nickname -> path (project libs)


def _lib(nick):
    if nick in _cache:
        return _cache[nick]
    path = EXTRA_LIBS.get(nick) or os.path.join(SYS_DIR, nick + '.kicad_sym')
    data = parse(open(path, encoding='utf-8').read())[0]
    syms = {}
    for e in data[1:]:
        if isinstance(e, list) and e and e[0] == 'symbol':
            syms[e[1]] = e
    _cache[nick] = syms
    return syms


def _rename_units(sym, old, new):
    for e in sym:
        if isinstance(e, list) and e and e[0] == 'symbol' and isinstance(e[1], str) and e[1].startswith(old + '_'):
            e[1] = new + e[1][len(old):]


def load(lib_id):
    """Return a flattened deep copy of the symbol, top-level named lib_id."""
    nick, name = lib_id.split(':', 1)
    syms = _lib(nick)
    s = copy.deepcopy(syms[name])
    ext = find(s, 'extends')
    if ext is not None:
        parent = load(nick + ':' + ext[1])
        pname = parent[1].split(':', 1)[1]
        derived_props = {p[1]: p for p in findall(s, 'property')}
        out = [Sym('symbol'), lib_id]
        for e in parent[2:]:
            if isinstance(e, list) and e and e[0] == 'property' and e[1] in derived_props:
                out.append(derived_props.pop(e[1]))
            else:
                out.append(copy.deepcopy(e))
        # properties only in derived
        insert_at = max(i for i, e in enumerate(out) if isinstance(e, list) and e and e[0] == 'property') + 1
        for p in derived_props.values():
            out.insert(insert_at, p)
            insert_at += 1
        _rename_units(out, pname, name)
        s = out
    s[1] = lib_id
    return s


def pins(sym, unit=1, body=1):
    """List of dicts: number, name, type, x, y, angle, length (lib coords, y up)."""
    out = []
    base = sym[1].split(':', 1)[1]
    for sub in findall(sym, 'symbol'):
        nm = sub[1]
        try:
            u, b = nm[len(base) + 1:].split('_')
            u, b = int(u), int(b)
        except ValueError:
            continue
        if u not in (0, unit) or b not in (0, body):
            continue
        for p in findall(sub, 'pin'):
            at = find(p, 'at')
            ln = find(p, 'length')
            name = find(p, 'name')
            num = find(p, 'number')
            hidden = any(isinstance(e, Sym) and e == 'hide' for e in p) or (
                find(p, 'hide') is not None and find(p, 'hide')[1] in ('yes', Sym('yes')))
            out.append(dict(number=num[1], name=name[1], type=str(p[1]), shape=str(p[2]),
                            x=float(at[1]), y=float(at[2]), angle=float(at[3]) if len(at) > 3 else 0.0,
                            length=float(ln[1]), hidden=hidden))
    return out


def is_power_symbol(sym):
    return find(sym, 'power') is not None


def body_bbox(sym, unit=1, body=1):
    """(minx, miny, maxx, maxy) of graphics + pins in lib coords (y up), or None."""
    xs, ys = [], []
    base = sym[1].split(':', 1)[1]
    import math
    for sub in findall(sym, 'symbol'):
        nm = sub[1]
        try:
            u, b = nm[len(base) + 1:].split('_')
            u, b = int(u), int(b)
        except ValueError:
            continue
        if u not in (0, unit) or b not in (0, body):
            continue
        for g in sub[2:]:
            if not isinstance(g, list) or not g:
                continue
            k = g[0]
            if k == 'rectangle':
                for key in ('start', 'end'):
                    e = find(g, key)
                    xs.append(float(e[1])); ys.append(float(e[2]))
            elif k == 'polyline' or k == 'bezier':
                pts = find(g, 'pts')
                for xy in findall(pts, 'xy'):
                    xs.append(float(xy[1])); ys.append(float(xy[2]))
            elif k == 'circle':
                c = find(g, 'center'); r = float(find(g, 'radius')[1])
                xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
            elif k == 'arc':
                for key in ('start', 'mid', 'end'):
                    e = find(g, key)
                    if e is not None:
                        xs.append(float(e[1])); ys.append(float(e[2]))
            elif k == 'pin':
                at = find(g, 'at'); ln = float(find(g, 'length')[1])
                a = math.radians(float(at[3]) if len(at) > 3 else 0.0)
                x0, y0 = float(at[1]), float(at[2])
                xs += [x0, x0 + ln * math.cos(a)]; ys += [y0, y0 + ln * math.sin(a)]
    if not xs:
        return None
    return (min(xs), min(ys), max(xs), max(ys))
