# pf67_0_preflight (block 0). READ-ONLY on the design (connector readOnly: true). Writes only under print_files_v67/.
#   Records: document, version, description, modified flag; body count, visible bodies, AUD_/NEW_ templates, the _v63.._v66
#   backups; the unit's count (16 leads, 13 keep-outs expected); the 14 guard volumes of D228 with lumps; camera as found; open
#   documents; Bambu Studio's version; the system presets against the copies of 2026-11-14; the X2D 0.4 PLA and ABS presets;
#   the flat presets of 2026-11-16 against the re-check's copies; the re-check's bed meshes, blockers and calibration meshes
#   (bytes, sha256); the print files of 2026-11-16 (every file: bytes, mtime, sha256 for the projects; the _work tree counted),
#   for the closing check that they are untouched; the Bambu Studio processes running.
#   Then, only if the guard passes, makes the new folder's tree and copies the flat presets the jobs load.
import plistlib, shutil, subprocess

R2_BS_APP = '/Applications/BambuStudio.app'
R2_BS_SYS = os.path.expanduser('~/Library/Application Support/BambuStudio/system/BBL')
R2_FLAT = ('machine_X2D_0.4.json', 'process_0.20_Standard.json', 'process_0.12_HQ.json', 'filament_BambuABS.json',
           'filament_BambuABS_black.json', 'filament_SupportABS.json', 'filament_SupportABS_white.json',
           'filament_BambuPLABasic.json', 'filament_BambuPLABasic_black.json')
R2_RC3_FILES = ('shell_plan_blk_v2.stl', 'shell_plan_blk_v3.stl', 'shell_chin8_blk.stl', 'shell_chin8_blk_v3.stl',
                'screen_plan_blk.stl', 'cal_frame.stl', 'cal_tower.stl', 'cal_holes_v67.stl', 'shell_plan.stl',
                'shell_chin8_plan.stl', 'screen_plan.stl', 'spkbox_L_plan.stl', 'spkbox_R_plan.stl', 'base_plan.stl',
                'carrier_plan.stl', 'cradle_plan.stl', 'clip_L_plan.stl', 'clip_R_plan.stl', 'bme_hood_plan.stl', 'cap_plan.stl',
                'grommet_plan.stl', 'slab_plan.stl', 'door_plan.stl')
R2_TREE = ('1_PLA_trial', '2_ABS_calibration_and_adhesion_test', '3_ABS_black_set', '_work/lib/steps', '_work/data',
           '_work/exports', '_work/orient', '_work/slicer/flat', '_work/slicer/jobs', '_work/slicer/out', '_work/slicer/bsdata')


def r2_tree_state(root, hash_ext=('.3mf',), skip=('_work',)):
    files = {}; work = {'n': 0, 'bytes': 0, 'mtime_max': 0.0}
    for dp, dn, fn in os.walk(root):
        rel = os.path.relpath(dp, root)
        top = rel.split(os.sep)[0]
        for f in fn:
            p = os.path.join(dp, f); st = os.stat(p)
            if top in skip:
                work['n'] += 1; work['bytes'] += st.st_size; work['mtime_max'] = max(work['mtime_max'], st.st_mtime)
                continue
            r = os.path.normpath(os.path.join(rel, f))
            files[r] = [st.st_size, round(st.st_mtime, 3), r2_sha(p) if f.endswith(hash_ext) else None]
    work['mtime_max'] = round(work['mtime_max'], 3)
    return files, work


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
    out['backups'] = {k: len([n for n in names if n.endswith(k)]) for k in R2_BACKUPS}
    cur = r2_unit(X)
    out['unit'] = [len(cur), sum(1 for b in cur if b.name.startswith('LEAD_')), sum(1 for b in cur if b.name.startswith('KO_'))]
    out['dups'] = sorted(set(n for n in names if names.count(n) > 1))
    rep, bad = r2_guard(X, strict=False)
    out['guard'] = {n: [rep.get(n, [None])[0], (round(rep[n][0] - v, 3) if n in rep else None), rep.get(n, [None, None])[1]]
                    for n, v in R2_GUARD.items()}
    out['guard_bad'] = bad
    vp = X.app.activeViewport; cm = vp.camera
    out['camera'] = {'eye': [round(cm.eye.x, 4), round(cm.eye.y, 4), round(cm.eye.z, 4)],
                     'target': [round(cm.target.x, 4), round(cm.target.y, 4), round(cm.target.z, 4)], 'style': vp.visualStyle}
    out['docs_open'] = [[d.name, d.isModified] for d in X.app.documents]
    # slicer
    q = os.path.join(R2_BS_APP, 'Contents', 'Info.plist')
    out['bambu_studio'] = None
    if os.path.exists(q):
        d = plistlib.load(open(q, 'rb'))
        out['bambu_studio'] = [d.get('CFBundleShortVersionString'), d.get('CFBundleVersion')]
    prof = os.path.join(R2_RC1, 'slicer', 'profiles'); cmp_ = {}
    if os.path.isdir(prof):
        for kind in sorted(os.listdir(prof)):
            kd = os.path.join(prof, kind)
            if not os.path.isdir(kd):
                continue
            for f in sorted(os.listdir(kd)):
                a = r2_sha(os.path.join(kd, f)); s = r2_sha(os.path.join(R2_BS_SYS, kind, f))
                cmp_['%s/%s' % (kind, f)] = 'equal' if (a and a == s) else ('system missing' if s is None else 'DIFFERS')
    out['presets_vs_system_1114'] = cmp_
    fd = os.path.join(R2_BS_SYS, 'filament')
    out['pla_x2d'] = sorted(f for f in os.listdir(fd) if 'PLA Basic' in f and 'X2D 0.4' in f) if os.path.isdir(fd) else None
    out['abs_x2d'] = sorted(f for f in os.listdir(fd) if 'ABS' in f and 'X2D 0.4' in f) if os.path.isdir(fd) else None
    # flat presets: 2026-11-16 (print_files) against the re-check's copies
    fl = {}
    for f in R2_FLAT:
        a = r2_sha(os.path.join(R2_PF65W, 'slicer', 'flat', f)); b = r2_sha(os.path.join(R2_RC3, 'slicer', 'flat', f))
        fl[f] = [a[:16] if a else None, 'same' if (a and a == b) else ('rc3 missing' if b is None else 'DIFFERS')]
    out['flat_pf65_vs_rc3'] = fl
    # the re-check's meshes, blockers and calibration meshes (print-file grade, orient_hr)
    rc = {}
    for f in R2_RC3_FILES:
        p = os.path.join(R2_RC3, 'orient_hr', f)
        rc[f] = [os.path.getsize(p), r2_sha(p)[:16]] if os.path.exists(p) else None
    out['rc3_orient_hr'] = rc
    out['pf65_orient_json'] = os.path.exists(os.path.join(R2_PF65W, 'data', 'pf_2_orient.json'))
    # the print files of 2026-11-16: state for the closing check
    files, work = r2_tree_state(R2_PF65)
    out['pf65_files'] = files; out['pf65_work'] = work
    out['pf65_n_3mf'] = sum(1 for k in files if k.endswith('.3mf'))
    # Bambu Studio processes (read only)
    r = subprocess.run(['/bin/ps', '-axo', 'pid=,lstart=,comm='], capture_output=True, text=True, timeout=20)
    out['bambu_ps'] = [' '.join(l.split()) for l in r.stdout.splitlines() if 'BambuStudio' in l]
    # the new folder, only with the guard passed
    out['made'] = []
    if not bad:
        for sub in R2_TREE:
            p = os.path.join(R2_OUTDIR, sub)
            if not os.path.isdir(p):
                os.makedirs(p); out['made'].append(sub)
        cp = {}
        for f in R2_FLAT:
            src = os.path.join(R2_PF65W, 'slicer', 'flat', f); dst = os.path.join(R2_DIR, 'slicer', 'flat', f)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)
            cp[f] = (r2_sha(dst) == r2_sha(src))
        out['flat_copied_same'] = cp
    out['t_s'] = round(time.time() - t0, 1)
    if not bad:
        r2_out(os.path.join(R2_DIR, 'data', 'pf67_0_preflight.json'), out)
        r2_log('pf67_0_preflight', 'run', {'bad': bad, 'n_bodies': out['n_bodies'], 'unit': out['unit'], 'n_visible': out['n_visible']})
    o2 = dict(out); o2.pop('visible'); o2.pop('pf65_files')
    o2['pf65_files_n'] = len(files)
    print(json.dumps(o2, separators=(',', ':')))
