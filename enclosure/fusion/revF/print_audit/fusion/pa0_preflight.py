# HA panel print audit, block 0: preflight. Read-only apart from switching the active document to the design model.
#   Records: open documents and which is active, the active view before and after, the design model's version (number,
#   description), guard volumes and lumps, body counts, the visible list (start state), `name (n)` bodies, the 14 prints'
#   world bounding boxes (bracket halves by lump), the exploded-prints document's components (read only), sha256 of the
#   Mac helper copies. Writes print_audit/data/pa0_preflight.json; log print_audit/pa_log.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
PA0_OUT = os.path.join(PA_DIR, 'data', 'pa0_preflight.json')


def run(_context):
    app = adsk.core.Application.get(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    try:
        out['active_before'] = app.activeDocument.name
        out['view_active_before'] = pa_view(app)
        out['open_docs'] = [[d.name, d.isModified] for d in app.documents]
        tgt = [d for d in app.documents if d.name == PA_DOC]
        if not tgt:
            raise RuntimeError('design document not open')
        if app.activeDocument.name != PA_DOC:
            tgt[0].activate()
        X = Ctx()
        df = X.doc.dataFile
        out['version'] = {'number': df.versionNumber, 'latest': df.latestVersionNumber, 'description': df.description,
                          'id': df.versionId, 'doc_isModified': X.doc.isModified, 'designType': X.des.designType}
        out['version_ok'] = (df.description or '').strip() == PA_VERSION
        rep, bad = pa_guard(X, strict=False)
        out['guard'] = rep; out['guard_bad'] = bad
        out['n_root'] = X.comp.bRepBodies.count
        out['n_all'] = sum(c.bRepBodies.count for c in X.des.allComponents)
        out['n_occ'] = X.comp.allOccurrences.count
        out['visible'] = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
        out['name_n'] = [[b.name, round(b.volume, 6)] for b in X.comp.bRepBodies if re.search(r' \(\d+\)$', b.name)]
        out['view_design'] = pa_view(app)
        prints = []
        for (tag, bn, side) in PA_PRINTS:
            b = X.body(bn)
            if side is None:
                prints.append([tag, bn, round(b.volume, 4), b.lumps.count, [round(v, 2) for v in wbb(X, b)]])
            else:
                for L in b.lumps:
                    t = X.tbm.copy(L); bb = wbb(X, t)
                    if (bb[0] + bb[1]) * side > 0:
                        prints.append([tag, bn, round(t.volume, 4), 1, [round(v, 2) for v in bb]])
        out['prints'] = prints
        ex = [d for d in app.documents if d.name == PA_EXPL]
        if ex:
            d2 = ex[0]
            des2 = adsk.fusion.Design.cast(d2.products.itemByProductType('DesignProductType'))
            comps = []
            for i in range(des2.rootComponent.occurrences.count):
                o = des2.rootComponent.occurrences.item(i)
                vols = [round(bb.volume, 4) for bb in o.component.bRepBodies]
                comps.append([o.component.name, vols])
            out['exploded'] = {'isModified': d2.isModified, 'components': comps}
        else:
            out['exploded'] = None
        out['sha256'] = {f: hashlib.sha256(open(os.path.expanduser('~/Documents/' + f), 'rb').read()).hexdigest()
                         for f in ('v5f_common.py', 'v5f_b5_common.py')}
        out['design_log_mtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(
            os.path.expanduser('~/Documents/v5f_log.json'))))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        pa_out(PA0_OUT, out)
    except Exception:
        out['WRITE_FAIL'] = traceback.format_exc().splitlines()[-1:]
    log('pa0_preflight', 'run', {'version_ok': out.get('version_ok'), 'guard_bad': out.get('guard_bad'), 'FAIL': out.get('FAIL')})
    print(json.dumps({k: out.get(k) for k in ('active_before', 'open_docs', 'version', 'version_ok', 'guard_bad', 'n_root',
                                               'n_all', 'n_occ', 'name_n', 'sha256', 'FAIL', 'WRITE_FAIL')}, separators=(',', ':')))
