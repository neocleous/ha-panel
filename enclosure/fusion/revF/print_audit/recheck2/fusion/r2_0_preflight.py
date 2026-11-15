# r2_0_preflight (block 0). READ-ONLY on the design (connector readOnly: true). Writes only under print_audit_recheck2/.
#   Records: document, version, description, modified flag; body count, visible bodies, templates, the _v63 / _v64 backups;
#   the unit as the enclosure chat counts it (16 leads, 13 keep-outs expected); the nine guard volumes of the brief and lumps;
#   scope B volumes against the re-check of 2026-11-14; camera and visual style as found (not changed); Bambu Studio installed
#   (version) and whether its system presets still equal the copies the 11-14 run flattened; the 11-14 folder's flat presets.
import plistlib, shutil

R2_BS_APP = '/Applications/BambuStudio.app'
R2_BS_SYS = os.path.expanduser('~/Library/Application Support/BambuStudio/system/BBL')


def r2_sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def run(_context):
    t0 = time.time(); X = R2Ctx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    df = X.doc.dataFile
    out['doc'] = [X.doc.name, df.versionNumber, df.latestVersionNumber, df.description, X.doc.isModified, X.des.designType]
    bodies = list(X.root.bRepBodies)
    names = [b.name for b in bodies]
    out['n_bodies'] = len(names)
    vis = sorted(b.name for b in bodies if b.isLightBulbOn)
    out['n_visible'] = len(vis); out['visible'] = vis
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    out['backups'] = {k: sorted([b.name, b.isLightBulbOn] for b in bodies if b.name.endswith(k)) for k in ('_v63', '_v64')}
    cur = r2_unit(X)
    out['unit'] = [len(cur), sum(1 for b in cur if b.name.startswith('LEAD_')), sum(1 for b in cur if b.name.startswith('KO_'))]
    out['dups'] = sorted(set(n for n in names if names.count(n) > 1))
    rep, bad = r2_guard(X, strict=False)
    out['guard'] = {n: [rep.get(n, [None])[0], (round(rep[n][0] - v, 3) if n in rep else None), rep.get(n, [None, None])[1],
                        X.body(n).isLightBulbOn if X.body(n) else None] for n, v in R2_GUARD.items()}
    out['guard_bad'] = bad
    out['scope_b'] = {}
    for n, v in R2_SCOPE_B.items():
        b = X.body(n)
        out['scope_b'][n] = None if b is None else [round(b.volume * 1000.0, 3), round(b.volume * 1000.0 - v, 3), b.lumps.count, b.isLightBulbOn]
    vp = X.app.activeViewport; cm = vp.camera
    out['camera'] = {'eye': [round(cm.eye.x, 3), round(cm.eye.y, 3), round(cm.eye.z, 3)],
                     'target': [round(cm.target.x, 3), round(cm.target.y, 3), round(cm.target.z, 3)],
                     'up': [round(cm.upVector.x, 3), round(cm.upVector.y, 3), round(cm.upVector.z, 3)], 'type': cm.cameraType,
                     'style': vp.visualStyle}
    out['docs_open'] = [[d.name, d.isModified] for d in X.app.documents]
    # slicer
    q = os.path.join(R2_BS_APP, 'Contents', 'Info.plist')
    out['bambu_studio'] = None
    if os.path.exists(q):
        d = plistlib.load(open(q, 'rb'))
        out['bambu_studio'] = [d.get('CFBundleShortVersionString'), d.get('CFBundleVersion')]
    prof = os.path.join(R2_OLD, 'slicer', 'profiles')
    cmp_ = {}
    if os.path.isdir(prof):
        for kind in sorted(os.listdir(prof)):
            kd = os.path.join(prof, kind)
            if not os.path.isdir(kd):
                continue
            for f in sorted(os.listdir(kd)):
                a = r2_sha(os.path.join(kd, f)); s = r2_sha(os.path.join(R2_BS_SYS, kind, f))
                cmp_['%s/%s' % (kind, f)] = 'equal' if (a and a == s) else ('system missing' if s is None else 'DIFFERS')
    out['presets_vs_system'] = cmp_
    fl = os.path.join(R2_OLD, 'slicer', 'flat')
    out['old_flat'] = sorted(os.listdir(fl)) if os.path.isdir(fl) else None
    out['old_dirs'] = sorted(os.listdir(R2_OLD)) if os.path.isdir(R2_OLD) else None
    for sub in ('exports', 'data', 'img', 'slicer/flat', 'slicer/orient', 'slicer/jobs', 'slicer/out', 'slicer/bsdata'):
        os.makedirs(os.path.join(R2_DIR, sub), exist_ok=True)
    copied = []
    if os.path.isdir(fl):
        for f in sorted(os.listdir(fl)):
            if f.endswith('.json') and not os.path.exists(os.path.join(R2_DIR, 'slicer', 'flat', f)):
                shutil.copy2(os.path.join(fl, f), os.path.join(R2_DIR, 'slicer', 'flat', f)); copied.append(f)
    out['flat_copied'] = copied
    out['t_s'] = round(time.time() - t0, 1)
    r2_out(os.path.join(R2_DIR, 'data', 'r2_0_preflight.json'), out)
    r2_log('r2_0_preflight', 'run', {'bad': bad, 'n_bodies': out['n_bodies'], 'unit': out['unit'], 'n_visible': out['n_visible']})
    o2 = dict(out); o2.pop('visible')
    print(json.dumps(o2, separators=(',', ':')))
