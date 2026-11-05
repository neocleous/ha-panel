# HA panel model audit (2026-11-05) block 0a: preflight. Read-only apart from switching the active document.
#   Activates "HA Panel v5 - tapered" (the exploded-view document stays open), then records: the open version
#   (number, description), body counts, printed-part guards and lumps, the visible list (audit start state), the camera
#   and visual style of both documents, `name (n)` / AUDIT_tmp_ bodies and the sha256 of the Mac helper copies.
#   Log: ~/Documents/v5f_audit_log.json (the design log is not written).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import hashlib, re, traceback
LOG = os.path.expanduser('~/Documents/v5f_audit_log.json')
DOC = 'HA Panel v5 - tapered'
GUARD = {'HOUSING_F_front': (236.6852, 0.0005), 'HOUSING_F_cap': (9.9147, 0.0005), 'HOUSING_F_door': (51.101, 0.0005),
         'SLAB_frame': (62.93, 0.006), 'SPKBOX_L': (25.62, 0.006), 'SPKBOX_R': (25.07, 0.006),
         'MAIN_BRACKET': (4.90, 0.006), 'RESP_CARRIER': (10.07, 0.006), 'CRADLE_5807': (2.16, 0.006),
         'GROMMET_usbc_F': (0.49, 0.006)}


def view_state(app):
    vp = app.activeViewport; c = vp.camera
    pt = lambda p: [round(p.x, 4), round(p.y, 4), round(p.z, 4)]
    return {'eye': pt(c.eye), 'target': pt(c.target), 'up': [round(c.upVector.x, 4), round(c.upVector.y, 4), round(c.upVector.z, 4)],
            'type': c.cameraType, 'extents': round(c.viewExtents, 4), 'fit': c.isFitView, 'style': vp.visualStyle}


def run(_context):
    app = adsk.core.Application.get(); out = {}
    try:
        out['active_before'] = app.activeDocument.name
        out['view_before'] = view_state(app)
        out['open_docs'] = [d.name for d in app.documents]
        tgt = [d for d in app.documents if d.name == DOC]
        if not tgt:
            raise RuntimeError('design document not open')
        tgt[0].activate()
        X = Ctx()
        df = X.doc.dataFile
        out['version'] = {'number': df.versionNumber, 'latest': df.latestVersionNumber, 'description': df.description,
                          'id': df.versionId, 'modified': df.dateModified, 'doc_isModified': X.doc.isModified,
                          'designType': X.des.designType}
        vs = []
        for i in range(df.versions.count):
            v = df.versions.item(i); vs.append([v.versionNumber, v.description[:60]])
        out['versions_last3'] = sorted(vs)[-3:]
        out['n_root'] = X.comp.bRepBodies.count
        out['n_all'] = sum(c.bRepBodies.count for c in X.des.allComponents)
        out['n_occ'] = X.comp.allOccurrences.count
        g = {}; bad = []
        for k, (v, tol) in GUARD.items():
            b = X.body(k)
            if b is None:
                g[k] = None; bad.append(k); continue
            g[k] = [round(b.volume, 4), b.lumps.count, round(b.volume - v, 4)]
            if abs(b.volume - v) > tol:
                bad.append(k)
        out['guard'] = g; out['guard_bad'] = bad
        out['visible'] = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
        out['visible_eff'] = sorted(b.name for b in X.comp.bRepBodies if b.isVisible)
        out['name_n'] = [[b.name, b.volume] for b in X.comp.bRepBodies if re.search(r' \(\d+\)$', b.name)]
        out['audit_tmp'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('AUDIT_tmp_')]
        out['view_design'] = view_state(app)
        out['sha256'] = {f: hashlib.sha256(open(os.path.expanduser('~/Documents/' + f), 'rb').read()).hexdigest()
                         for f in ('v5f_common.py', 'v5f_b5_common.py')}
        out['log_mtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(
            os.path.expanduser('~/Documents/v5f_log.json'))))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a0a_preflight', 'preflight', out)
    print(json.dumps({k: out.get(k) for k in ('active_before', 'open_docs', 'version', 'versions_last3', 'n_root', 'n_all',
                                               'n_occ', 'guard', 'guard_bad', 'name_n', 'audit_tmp', 'sha256', 'log_mtime',
                                               'view_before', 'view_design', 'FAIL')}))
    print('visible %d: %s' % (len(out.get('visible', [])), out.get('visible')))
    if out.get('visible') != out.get('visible_eff'):
        print('visible_eff differs: %s' % out.get('visible_eff'))
