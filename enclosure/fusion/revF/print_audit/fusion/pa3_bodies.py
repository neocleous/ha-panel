# HA panel print audit, block 2 (P9, printed-component fits): list every body of the design model with its visibility,
#   volume and world bounding box, and the bounding-box gap to each printed body (mm, design-frame boxes). Read-only apart
#   from activating the design document for reading and re-activating the document that was active before.
#   Writes print_audit/data/pa3_bodies.json; log print_audit/pa_log.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
PA3B_OUT = os.path.join(PA_DIR, 'data', 'pa3_bodies.json')


def pa3_gap(b1, b2):
    a, b = b1.boundingBox, b2.boundingBox
    d = [max(0.0, b.minPoint.x - a.maxPoint.x, a.minPoint.x - b.maxPoint.x),
         max(0.0, b.minPoint.y - a.maxPoint.y, a.minPoint.y - b.maxPoint.y),
         max(0.0, b.minPoint.z - a.maxPoint.z, a.minPoint.z - b.maxPoint.z)]
    return math.sqrt(sum(v * v for v in d)) * 10


def run(_context):
    app = adsk.core.Application.get(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    before = app.activeDocument.name; out['active_before'] = before
    try:
        tgt = [d for d in app.documents if d.name == PA_DOC]
        if app.activeDocument.name != PA_DOC:
            tgt[0].activate()
        X = Ctx(); pa_guard(X)
        printed = {bn: X.body(bn) for bn in PA_GUARD}
        rows = []
        for b in X.comp.bRepBodies:
            if b.name in printed:
                continue
            bb = b.boundingBox
            lo = pa_wpt(bb.minPoint); hi = pa_wpt(bb.maxPoint)
            gaps = {k: round(pa3_gap(p, b), 2) for k, p in printed.items()}
            near = sorted([k for k, g in gaps.items() if g < 1.0])
            rows.append([b.name, b.isLightBulbOn, round(b.volume, 4), b.isSolid, near,
                         [round(min(lo[i], hi[i]), 1) for i in range(3)] + [round(max(lo[i], hi[i]), 1) for i in range(3)]])
        out['rows'] = rows; out['n'] = len(rows)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        if app.activeDocument.name != before:
            [d for d in app.documents if d.name == before][0].activate()
        out['active_after'] = app.activeDocument.name
    except Exception:
        out['ACTIVATE_FAIL'] = traceback.format_exc().splitlines()[-1:]
    pa_out(PA3B_OUT, out)
    log('pa3_bodies', 'run', {'n': out.get('n'), 'FAIL': out.get('FAIL')})
    print(json.dumps({k: out.get(k) for k in ('n', 'active_before', 'active_after', 'FAIL', 'ACTIVATE_FAIL')}, separators=(',', ':')))
