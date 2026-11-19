# pf67_9_final_guard (block 6). READ-ONLY on the design (connector readOnly: true). Writes only under print_files_v67/_work/.
#   The closing check: document, version, description, modified flag; body count, visible bodies, AUD_/NEW_ templates, the
#   _v63.._v66 backups; the unit's count; the 14 guard volumes of D228 with lumps; camera as found (against the preflight's);
#   open documents. Then the files: the print files of 2026-11-16 (print_files/) against the preflight's record (every
#   project's bytes, mtime and sha256; the _work tree's count, bytes and last change), and the 17 new projects against their
#   publish record (bytes, sha256). Bambu Studio processes (read only).
import subprocess


def run(_context):
    t0 = time.time(); X = R2Ctx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    df = X.doc.dataFile
    out['doc'] = [X.doc.name, df.versionNumber, df.latestVersionNumber, df.description, X.doc.isModified, X.des.designType]
    bodies = list(X.root.bRepBodies); names = [b.name for b in bodies]
    out['n_bodies'] = len(names)
    out['n_visible'] = sum(1 for b in bodies if b.isLightBulbOn)
    out['templates'] = [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))]
    out['backups'] = {k: len([n for n in names if n.endswith(k)]) for k in R2_BACKUPS}
    cur = r2_unit(X)
    out['unit'] = [len(cur), sum(1 for b in cur if b.name.startswith('LEAD_')), sum(1 for b in cur if b.name.startswith('KO_'))]
    rep, bad = r2_guard(X, strict=False)
    out['guard'] = {n: [rep.get(n, [None])[0], (round(rep[n][0] - v, 3) if n in rep else None), rep.get(n, [None, None])[1]]
                    for n, v in R2_GUARD.items()}
    out['guard_bad'] = bad
    pre = json.load(open(os.path.join(R2_DIR, 'data', 'pf67_0_preflight.json')))
    vp = X.app.activeViewport; cm = vp.camera
    cam = {'eye': [round(cm.eye.x, 4), round(cm.eye.y, 4), round(cm.eye.z, 4)],
           'target': [round(cm.target.x, 4), round(cm.target.y, 4), round(cm.target.z, 4)], 'style': vp.visualStyle}
    out['camera_as_found'] = (cam == pre['camera'])
    vis = sorted(b.name for b in bodies if b.isLightBulbOn)
    out['visible_as_found'] = (vis == pre['visible'])
    out['docs_open'] = [[d.name, d.isModified] for d in X.app.documents]
    # the print files of 2026-11-16: untouched?
    files, work = {}, {'n': 0, 'bytes': 0, 'mtime_max': 0.0}
    for dp, dn, fn in os.walk(R2_PF65):
        rel = os.path.relpath(dp, R2_PF65); top = rel.split(os.sep)[0]
        for f in fn:
            p = os.path.join(dp, f); st = os.stat(p)
            if top == '_work':
                work['n'] += 1; work['bytes'] += st.st_size; work['mtime_max'] = max(work['mtime_max'], st.st_mtime); continue
            r = os.path.normpath(os.path.join(rel, f))
            files[r] = [st.st_size, round(st.st_mtime, 3), r2_sha(p) if f.endswith('.3mf') else None]
    work['mtime_max'] = round(work['mtime_max'], 3)
    out['pf65_files_same'] = (files == pre['pf65_files']); out['pf65_work_same'] = (work == pre['pf65_work'])
    out['pf65_n'] = len(files)
    # the new projects against their publish record
    pub = json.load(open(os.path.join(R2_DIR, 'data', 'pf67_5_publish.json')))
    chk = {}
    for job, r in pub.items():
        p = os.path.join(R2_OUTDIR, r['file'])
        chk[job] = os.path.exists(p) and os.path.getsize(p) == r['bytes'] and r2_sha(p) == r['sha256']
    out['v67_projects_ok'] = chk
    out['v67_project_files'] = sorted(os.path.relpath(os.path.join(dp, f), R2_OUTDIR) for dp, dn, fn in os.walk(R2_OUTDIR)
                                      for f in fn if not os.path.relpath(dp, R2_OUTDIR).startswith('_work'))
    r = subprocess.run(['/bin/ps', '-axo', 'pid=,lstart=,comm='], capture_output=True, text=True, timeout=20)
    out['bambu_ps'] = [' '.join(l.split()) for l in r.stdout.splitlines() if 'BambuStudio' in l]
    out['t_s'] = round(time.time() - t0, 1)
    r2_out(os.path.join(R2_DIR, 'data', 'pf67_9_final_guard.json'), out)
    r2_log('pf67_9_final_guard', 'run', {'bad': bad, 'n_bodies': out['n_bodies'], 'unit': out['unit'], 'n_visible': out['n_visible'],
                                         'pf65_same': [out['pf65_files_same'], out['pf65_work_same']]})
    print(json.dumps(out, separators=(',', ':')))
