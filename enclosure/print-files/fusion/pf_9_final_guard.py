# pf_9_final_guard (block 4). READ-ONLY on the design (connector readOnly: true). Writes only under print_files/_work/.
#   At the end of the session: document, version, modified flag; body count, visible bodies, AUD_/NEW_ templates, the _v63 / _v64
#   backups; the unit's count; the nine guard volumes of the brief; scope B volumes; camera as found; open documents.


def run(_context):
    t0 = time.time(); X = R2Ctx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    df = X.doc.dataFile
    out['doc'] = [X.doc.name, df.versionNumber, df.latestVersionNumber, X.doc.isModified, X.des.designType]
    bodies = list(X.root.bRepBodies)
    names = [b.name for b in bodies]
    out['n_bodies'] = len(names)
    out['n_visible'] = sum(1 for b in bodies if b.isLightBulbOn)
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    out['backups'] = {k: len([b for b in bodies if b.name.endswith(k)]) for k in ('_v63', '_v64')}
    cur = r2_unit(X)
    out['unit'] = [len(cur), sum(1 for b in cur if b.name.startswith('LEAD_')), sum(1 for b in cur if b.name.startswith('KO_'))]
    rep, bad = r2_guard(X, strict=False)
    out['guard'] = {n: [rep.get(n, [None])[0], (round(rep[n][0] - v, 3) if n in rep else None)] for n, v in R2_GUARD.items()}
    out['guard_bad'] = bad
    out['scope_b'] = {}
    for n, v in R2_SCOPE_B.items():
        b = X.body(n)
        out['scope_b'][n] = None if b is None else [round(b.volume * 1000.0, 3), round(b.volume * 1000.0 - v, 3)]
    vp = X.app.activeViewport; cm = vp.camera
    out['camera'] = {'eye': [round(cm.eye.x, 3), round(cm.eye.y, 3), round(cm.eye.z, 3)],
                     'target': [round(cm.target.x, 3), round(cm.target.y, 3), round(cm.target.z, 3)], 'style': vp.visualStyle}
    out['docs_open'] = [[d.name, d.isModified] for d in X.app.documents]
    out['t_s'] = round(time.time() - t0, 1)
    r2_out(os.path.join(R2_DIR, 'data', 'pf_9_final_guard.json'), out)
    r2_log('pf_9_final_guard', 'run', {'bad': bad, 'n_bodies': out['n_bodies'], 'unit': out['unit'], 'n_visible': out['n_visible']})
    print(json.dumps(out, separators=(',', ':')))
