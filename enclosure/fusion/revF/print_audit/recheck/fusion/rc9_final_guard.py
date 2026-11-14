# rc9_final_guard (block 5): the closing check. Version 63 of 63, unmodified; the eight guard volumes; body count, visible bodies,
#   no AUD_ / NEW_ / RENDER_TMP templates; camera and visual style as they are now (no rc call ever set them). READ-ONLY.
def run(_context):
    X = RcCtx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    rep, bad = rc_guard(X, strict=False)
    out['guard'] = rep; out['bad'] = bad
    names = [b.name for b in X.root.bRepBodies]
    out['n_bodies'] = len(names)
    vis = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
    out['n_visible'] = len(vis); out['visible_sha'] = hashlib.sha256('\n'.join(vis).encode()).hexdigest()[:16]
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    vp = X.app.activeViewport; cm = vp.camera
    out['camera'] = {'eye': [round(cm.eye.x, 3), round(cm.eye.y, 3), round(cm.eye.z, 3)],
                     'target': [round(cm.target.x, 3), round(cm.target.y, 3), round(cm.target.z, 3)],
                     'up': [round(cm.upVector.x, 3), round(cm.upVector.y, 3), round(cm.upVector.z, 3)],
                     'type': cm.cameraType, 'style': vp.visualStyle}
    out['docs_open'] = [d.name for d in X.app.documents]
    rc_out(os.path.join(RC_DIR, 'data', 'rc9_final_guard.json'), out)
    rc_log('rc9_final_guard', 'run', {'bad': bad, 'n_bodies': out['n_bodies'], 'n_visible': out['n_visible']})
    print(json.dumps(out, separators=(',', ':')))
