# rev F close of the enclosure work (2026-11-12) - helpers for the j scripts (part 2 of the brief of 2026-11-11: measurements and
# pictures, the complete unit checked as a whole, hand-over for the assembly audit).
# The i library (h library + purge() + run_h()) with this pass's data folder fp/close, the list of printed parts and small probes.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
S3 = os.path.join(FP, 'close')
PRINTED = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'FLOOR_PLATE', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'CRADLE_5807',
           'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'GROMMET_usbc_F']


def run_j(name, repl=(), g=None):       # exec an earlier script (f, g, h or i) with this library in place of its own and the replacements given
    src = open(os.path.join(SCR, name), encoding='utf-8').read()
    for lib in ("'v5f_fp_lib.py'", "'v5f_h_lib.py'", "'v5f_i_lib.py'"):
        src = src.replace(lib, "'v5f_j_lib.py'")
    for a, b in repl:
        if a not in src:
            raise RuntimeError('replacement not found in %s: %s' % (name, a))
        src = src.replace(a, b)
    ns = {'__name__': 'v5f_run_j'}
    ns.update(g or {})
    exec(compile(src, name, 'exec'), ns)
    return ns


def crop(X, key, name, box, frame='W'):         # cached crop of a model body to a box (world x0,x1,y0,y1,z0,z1 or slab x,d,Zd)
    c = cache()
    b = X.body(name)
    k = ('crop', key, round(b.volume, 6))
    if k not in c:
        t = X.cp(tcopy(X, name))
        X.sec(t, X.wbox(*box) if frame == 'W' else X.dbox(*box))
        c[k] = t
    return c[k]


def ivals(X, needle, body, axis):               # sorted [lo, hi] intervals (world axis 0, 1 or 2) in which a needle is inside a body
    t = X.cp(needle)
    try:
        X.tbm.booleanOperation(t, body, BT.IntersectionBooleanType)
    except Exception:
        return None
    out = []
    for l in t.lumps:
        q = [W(v.geometry)[axis] for v in l.vertices]
        out.append([round(min(q), 2), round(max(q), 2)])
    return sorted(out)


def wext(b):                                    # world box of a body from its vertices: [x0, x1, y0, y1, z0, z1]
    q = [W(v.geometry) for v in b.vertices]
    return [round(f(p[i] for p in q), 2) for i in range(3) for f in (min, max)]


def solid(X, box, body):                        # mm3 of a temporary box inside a body (the body is the tool: it is not copied)
    t = X.cp(box)
    try:
        X.tbm.booleanOperation(t, body, BT.IntersectionBooleanType)
    except Exception:
        return -1.0
    return X.vol(t)
