# HA panel model audit (2026-11-05) block 6a: numbers for the doc-vs-model check (D.1), read-only.
#   Lane axes: every cylindrical face of KO_capkey_* and KO_K5_* -> world direction (nw_of), angle from world vertical and
#   from the LCD screw axis (design Y), radius. Plus the document facts (version, modified, open documents).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def ang(a, b):
    d = sum(a[i] * b[i] for i in range(3)) / math.sqrt(sum(q * q for q in a) * sum(q * q for q in b))
    return math.degrees(math.acos(max(-1.0, min(1.0, abs(d)))))


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        scr = (0.0, C, S)                                   # design +Y in world
        lanes = {}
        for b in X.comp.bRepBodies:
            if not (b.name.startswith('KO_capkey_') or b.name.startswith('KO_K5_')):
                continue
            cyl = []
            for f in b.faces:
                g = f.geometry
                if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                    w = nw_of(g.axis)
                    cyl.append({'r_mm': round(g.radius * 10, 3), 'from_vertical_deg': round(ang(w, (0, 0, 1)), 2),
                                'from_screw_axis_deg': round(ang(w, scr), 2), 'dir': [round(q, 4) for q in w], 'area_mm2': round(f.area * 100, 1)})
            lanes[b.name] = sorted(cyl, key=lambda c: -c['area_mm2'])[:2]
        out['lanes'] = lanes
        out['doc'] = {'name': X.doc.name, 'version': X.doc.dataFile.versionNumber, 'latest': X.doc.dataFile.latestVersionNumber,
                      'modified': X.doc.isModified, 'description': X.doc.dataFile.description[:60]}
        out['open_docs'] = [[d.name, d.isModified, d.isActive] for d in adsk.core.Application.get().documents]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a6a_doc_checks', 'run', out)
    print(json.dumps(out))
