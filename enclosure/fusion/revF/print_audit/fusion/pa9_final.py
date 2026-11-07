# HA panel print audit, block 4: final check. Read-only apart from switching the active document back to the one that
#   was active at the start (the exploded-prints copy). Records: open documents and modified flags, the design model's
#   version, guard volumes and lumps, body counts, the visible list and the view, and compares them with the preflight
#   record (data/pa0_preflight.json); the exploded copy's components and volumes against the preflight; then re-activates
#   the exploded copy. Writes print_audit/data/pa9_final.json; log print_audit/pa_log.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
PA9_OUT = os.path.join(PA_DIR, 'data', 'pa9_final.json')
PA9_PRE = os.path.join(PA_DIR, 'data', 'pa0_preflight.json')


def run(_context):
    app = adsk.core.Application.get(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    try:
        pre = json.load(open(PA9_PRE))
        out['active_now'] = app.activeDocument.name
        out['open_docs'] = [[d.name, d.isModified] for d in app.documents]
        tgt = [d for d in app.documents if d.name == PA_DOC]
        if not tgt:
            raise RuntimeError('design document not open')
        if app.activeDocument.name != PA_DOC:
            tgt[0].activate()
        X = Ctx()
        df = X.doc.dataFile
        out['version'] = {'number': df.versionNumber, 'latest': df.latestVersionNumber, 'description_ok':
                          (df.description or '').strip() == PA_VERSION, 'doc_isModified': X.doc.isModified}
        out['version_same_as_preflight'] = (df.versionNumber == pre['version']['number'] and
                                            df.latestVersionNumber == pre['version']['latest'])
        rep, bad = pa_guard(X, strict=False)
        out['guard'] = rep; out['guard_bad'] = bad
        out['n_root'] = X.comp.bRepBodies.count
        out['n_all'] = sum(c.bRepBodies.count for c in X.des.allComponents)
        out['counts_same'] = (out['n_root'] == pre['n_root'] and out['n_all'] == pre['n_all'])
        vis = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
        out['visible_same'] = vis == pre['visible']
        out['visible_diff'] = [sorted(set(vis) - set(pre['visible'])), sorted(set(pre['visible']) - set(vis))]
        out['view_design'] = pa_view(app)
        out['view_design_preflight'] = pre.get('view_design')
        ex = [d for d in app.documents if d.name == PA_EXPL]
        if ex:
            d2 = ex[0]
            des2 = adsk.fusion.Design.cast(d2.products.itemByProductType('DesignProductType'))
            comps = []
            for i in range(des2.rootComponent.occurrences.count):
                o = des2.rootComponent.occurrences.item(i)
                comps.append([o.component.name, [round(bb.volume, 4) for bb in o.component.bRepBodies]])
            out['exploded'] = {'isModified': d2.isModified, 'same_as_preflight': comps == pre['exploded']['components']}
            d2.activate()
            out['active_after'] = app.activeDocument.name
            out['view_exploded_after'] = pa_view(app)
            out['view_exploded_preflight'] = pre.get('view_active_before')
        else:
            out['exploded'] = None
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        pa_out(PA9_OUT, out)
    except Exception:
        out['WRITE_FAIL'] = traceback.format_exc().splitlines()[-1:]
    log('pa9_final', 'run', {'guard_bad': out.get('guard_bad'), 'FAIL': out.get('FAIL')})
    print(json.dumps({k: out.get(k) for k in ('active_now', 'open_docs', 'version', 'version_same_as_preflight',
                                               'guard_bad', 'counts_same', 'visible_same', 'visible_diff', 'exploded',
                                               'active_after', 'FAIL', 'WRITE_FAIL')}, separators=(',', ':')))
