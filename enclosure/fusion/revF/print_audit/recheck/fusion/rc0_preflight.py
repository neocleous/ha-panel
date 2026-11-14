# HA panel print audit re-check (2026-11-14), block 0: preflight. READ-ONLY on the design (connector readOnly: true).
#   Brief: claude/brief-print-audit-recheck-2026-11-14.md. Model "HA Panel v5 - tapered", version 63 expected.
#   Records: document, version, description, modified flag; body count, visible list, templates, duplicate names; the unit as
#   the enclosure chat counts it (v5f_k_lib.current(leads=True), loaded by commit from the repo with its git blob checked);
#   the 8 guard volumes of the brief (mm3) and lumps; scope B volumes against the first audit; retired bracket; spline/cloth
#   bodies; the camera and visual style as found; slicers installed on the Mac; the first audit's Mac script copies (sha256
#   against the repo at docs 2170c7a). Writes nothing. Prints one JSON line.
import adsk.core, adsk.fusion, os, sys, re, json, time, types, hashlib, plistlib, urllib.request

RC_RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
RC_HEAD = '2170c7a32f3b34ab5daa428d89de4dddad558b62'
RC_KLIB = ('enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py', 'ba8588482cd63f378ce5b98547aa702716f4855c')
RC_GUARD = {'HOUSING_F_front': 200363.57, 'SPKBOX_L': 26051.89, 'SPKBOX_R': 26769.41, 'RESP_CARRIER': 12404.26,
            'FLOOR_PLATE': 32452.33, 'CRADLE_5807': 1770.95, 'HOUSING_F_door': 47019.77, 'HOUSING_F_cap': 9944.06}
RC_SCOPE_B = {'SLAB_frame': 62932.4, 'GROMMET_usbc_F': 506.2, 'TOUCH_CLIP_L': 489.6, 'TOUCH_CLIP_R': 489.6, 'BME_HOOD': 802.9}
RC_REPO_SHA = {'pa0_preflight.py': '40958cfd0938340240ad624b2cdb8e2d95b11b6618acd3ef974fe94fd1d26ec3',
               'pa1_export.py': '186eca44bdda7572c255aa1441eeed99fcfbadc22bc438f458938bd9753ead64',
               'pa2_holes.py': 'e11b70bbaf5a7d3be278b962ea6aae818387550042b7dac3213fa4425e36aadf',
               'pa3_bodies.py': '520646b05e368ab7f33bfef10a99a44b4f35af72518ab094d2db8272eb2d8c6f',
               'pa3_compfits.py': '43e7e3aeac9309c362288c8a26f8677e3270d9bb86438ba0d999901431e67a46',
               'pa9_final.py': '60845274c334a4b95590b0b716d8ef500344204157cd82e383e2cd0fce449266',
               'pa_common.py': '3aaac54dcace28ea361600e3433fa3668fea1310b20be3fdeeb825487b2708ae',
               'v5f_common.py': '9ca152037b482aeaf928a55ff14dfe204a5f5876b19b826b5de07a6e7b888e69',
               'v5f_b5_common.py': '0a7ca558a6e4cdb91c5f3d575027e0d9a58180886b295445d32a490120861e38'}


def rc_blob(src):
    return hashlib.sha1(b'blob %d\0' % len(src) + src).hexdigest()


def rc_load_k():
    src = urllib.request.urlopen(RC_RAW % (RC_HEAD, RC_KLIB[0]), timeout=25).read()
    if rc_blob(src) != RC_KLIB[1]:
        raise RuntimeError('blob of v5f_k_lib.py is %s' % rc_blob(src))
    m = types.ModuleType('rc_k')
    exec(compile(src.decode('utf-8'), 'v5f_k_lib.py', 'exec'), m.__dict__)
    sys.modules['rc_k'] = m
    return m


def rc_sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def rc_app_version(p):
    q = os.path.join(p, 'Contents', 'Info.plist')
    if not os.path.exists(q):
        return None
    d = plistlib.load(open(q, 'rb'))
    return [d.get('CFBundleShortVersionString'), d.get('CFBundleVersion')]


def run(_context):
    t0 = time.time(); out = {}
    app = adsk.core.Application.get(); doc = app.activeDocument; df = doc.dataFile
    des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    out['doc'] = [doc.name, df.versionNumber, df.latestVersionNumber, df.description, doc.isModified, des.designType]
    names = [b.name for b in root.bRepBodies]
    out['bodies'] = len(names)
    out['visible'] = sorted(b.name for b in root.bRepBodies if b.isLightBulbOn)
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    vp = app.activeViewport; cm = vp.camera
    pt = lambda p: [round(p.x, 4), round(p.y, 4), round(p.z, 4)]
    out['view'] = {'eye': pt(cm.eye), 'target': pt(cm.target), 'up': [round(cm.upVector.x, 4), round(cm.upVector.y, 4), round(cm.upVector.z, 4)],
                   'type': cm.cameraType, 'ext': round(cm.viewExtents, 4), 'fit': cm.isFitView, 'style': vp.visualStyle}
    k = rc_load_k(); X = k.K()
    cur = k.current(X, leads=True)
    out['unit'] = [len(cur), sum(1 for q in cur if q.name.startswith('LEAD_')), sum(1 for q in cur if q.name.startswith('KO_'))]
    out['dups'] = X.dups()
    out['guard'] = {}
    for n, v in RC_GUARD.items():
        b = X.body(n); vol = b.volume * 1000.0
        out['guard'][n] = [round(vol, 2), round(vol - v, 3), b.lumps.count, b.isLightBulbOn]
    out['scope_b'] = {}
    for n, v in RC_SCOPE_B.items():
        b = X.body(n); vol = b.volume * 1000.0
        out['scope_b'][n] = [round(vol, 2), round(vol - v, 2), b.lumps.count, b.isLightBulbOn]
    out['printed_in_k'] = k.PRINTED
    out['bracket'] = [[b.name, b.isLightBulbOn, b in cur] for b in root.bRepBodies if b.name.startswith('MAIN_BRACKET')]
    out['spline_like'] = [[b.name, round(b.volume * 1000.0, 2), b.isLightBulbOn] for b in root.bRepBodies
                          if re.search(r'SPLINE|CLOTH|TPU|CORD|FABRIC', b.name, re.I)]
    out['cur_names'] = sorted(q.name for q in cur)
    apps = {}
    for p in ('/Applications/BambuStudio.app', '/Applications/Bambu Studio.app', '/Applications/OrcaSlicer.app',
              '/Applications/PrusaSlicer.app', os.path.expanduser('~/Applications/BambuStudio.app')):
        if os.path.exists(p):
            apps[p] = rc_app_version(p)
    out['slicers'] = apps
    bs = os.path.expanduser('~/Library/Application Support/BambuStudio')
    out['bs_support'] = sorted(os.listdir(bs)) if os.path.isdir(bs) else None
    sc = os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts')
    macs = {}
    for f, h in RC_REPO_SHA.items():
        p = os.path.join(sc, f) if f.startswith('pa') else os.path.expanduser('~/Documents/' + f)
        s = rc_sha(p)
        macs[f] = 'missing' if s is None else ('equal' if s == h else 'DIFFERS ' + s[:12])
    out['mac_scripts'] = macs
    rd = os.path.expanduser('~/Documents/HA_panel_renders')
    out['renders_dirs'] = sorted(os.listdir(rd)) if os.path.isdir(rd) else None
    out['recheck_dir'] = os.path.isdir(os.path.join(rd, 'print_audit_recheck'))
    out['t_s'] = round(time.time() - t0, 1)
    print(json.dumps(out, separators=(',', ':')))
