# HA panel model audit (2026-11-05) block 6b: end-state check, read-only.
#   Guards, body count 214, no AUDIT_tmp_ bodies, visible list = the block 0 start list, document version / modified flag,
#   open documents. If REACTIVATE (loader) names a document, it is activated at the end (the exploded-view document was the
#   active one at the start); activation changes no design data.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def run(_context):
    X = Ctx(); out = {}
    try:
        g = {}
        for k, (v, tol) in GUARD.items():
            b = X.body(k); g[k] = [round(b.volume, 4), abs(b.volume - v) <= tol] if b else None
        out['guards'] = g
        out['end_state'] = end_state(X)
        out['visible_now'] = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
        app = adsk.core.Application.get()
        out['open_docs_before'] = [[d.name, d.isModified, d.isActive] for d in app.documents]
        rn = globals().get('REACTIVATE')
        if rn:
            for d in app.documents:
                if d.name == rn:
                    d.activate()
            out['open_docs_after'] = [[d.name, d.isModified, d.isActive] for d in app.documents]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a6b_end_state', 'run', out)
    print(json.dumps(out))
