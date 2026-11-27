# Print files of version 91 (register 5d-3; brief claude/brief-print-files-v91-2026-11-27.md): shared helpers.
# Ported from the print re-check's r91_lib.py (third look). READ-ONLY on the design: nothing here creates, changes or deletes a
# body in the document; no version is saved. No time.sleep().
# Writes only under ~/Documents/HA_panel_renders/print_files_v91/ (work in _work/, print files in the set folders).
# Reads, never writes, the re-check's folders print_recheck_v79/, _v85/, _v91/ and print_files_v67/.
#   go(script, func, outname, ...)  runs W/script's func with its printed text caught into W/out/outname; the script must end with
#                                   the line '# END <script>' (the check that it arrived whole on the Mac).
#   guard(), world_mesh(), write_stl(), apply_M()   the re-check's own code, version 91's guard volumes (both readings).
#   tools(), poll()                 background offline tools (pf91_tools.py, r91_lin.py) with output in W/out.
#   mkjob(), slicer()               a Bambu Studio command-line job as the re-check builds it; the chain's queue (pfbs.py, read
#                                   where it is) pointed at W.
import os, sys, re, json, math, time, struct, hashlib, io, contextlib, traceback, runpy, subprocess

HOME = os.path.expanduser('~/Documents/HA_panel_renders')
OUTDIR = os.path.join(HOME, 'print_files_v91')
W = os.path.join(OUTDIR, '_work')
RD = W
RD91 = os.path.join(HOME, 'print_recheck_v91')       # the third look: read only
RD85 = os.path.join(HOME, 'print_recheck_v85')       # the second look: read only
RD79 = os.path.join(HOME, 'print_recheck_v79')       # the first look: read only
PC = os.path.join(HOME, 'adversarial_audit_v69', 'c')
PF67 = os.path.join(HOME, 'print_files_v67', '_work')
FLAT = os.path.join(PF67, 'slicer', 'flat')
PFBS = os.path.join(PF67, 'lib', 'pfbs.py')
CGQ = os.path.join(PC, 'cgq.py')
PY = '/opt/homebrew/bin/python3'
BS_APP = '/Applications/BambuStudio.app'
WORLD = os.path.join(W, 'stl', 'world'); BED = os.path.join(W, 'stl', 'bed')
DOC = 'HA Panel v5 - tapered'; VERSION = 91
C12 = math.cos(math.radians(12.0)); S12 = math.sin(math.radians(12.0)); H0 = 143.3; XC = -2.55
# claude/brief-print-recheck-v91-2026-11-27.md (the six) and claude/brief-print-recheck-v85-2026-11-26.md (the eleven), as the
# re-check's r91_lib.py has them: body -> (preflight method BRepBody.volume, very high accuracy), mm3
GUARD = {'HOUSING_F_front': (111268.594, 111278.861), 'HOUSING_F_plate': (66415.924, 66415.279), 'SLAB_frame': (63006.012, 63005.760),
         'HOUSING_F_door': (50841.493, 50843.240), 'FLOOR_PLATE': (31504.631, 31507.029), 'SPKBOX_R': (26929.045, 26925.087),
         'SPKBOX_L': (26604.775, 26603.551), 'RESP_CARRIER': (13588.334, 13588.334), 'HOUSING_F_cap': (10131.026, 10129.650),
         'CRADLE_5807': (1771.219, 1771.228), 'RADAR_HOLDER': (1120.921, 1120.921), 'BME_HOOD': (946.741, 946.544),
         'GROMMET_usbc_F': (863.410, 863.403), 'MIC_CLAMP_L': (743.091, 743.091), 'MIC_CLAMP_R': (743.091, 743.091),
         'TOUCH_CLIP_L': (727.322, 727.322), 'TOUCH_CLIP_R': (727.322, 727.322)}
TOL = {'HOUSING_F_front': 15.0}          # D228: two reads of the shell can differ by up to 15 (preflight method)
PRINTS = [('shell', 'HOUSING_F_front'), ('screen', 'HOUSING_F_plate'), ('slab', 'SLAB_frame'), ('door', 'HOUSING_F_door'),
          ('base', 'FLOOR_PLATE'), ('spkbox_L', 'SPKBOX_L'), ('spkbox_R', 'SPKBOX_R'), ('carrier', 'RESP_CARRIER'),
          ('cradle', 'CRADLE_5807'), ('cap', 'HOUSING_F_cap'), ('grommet', 'GROMMET_usbc_F'), ('bme_hood', 'BME_HOOD'),
          ('clamp_L', 'MIC_CLAMP_L'), ('clamp_R', 'MIC_CLAMP_R'), ('clip_L', 'TOUCH_CLIP_L'), ('clip_R', 'TOUCH_CLIP_R'),
          ('holder', 'RADAR_HOLDER')]
BASE_OPTS = {'nozzle-volume-type': 'High Flow,High Flow', 'filament-map-mode': 'Manual', 'xy-hole-compensation': '0.1',
             'elefant-foot-compensation': '0.15', 'bridge-no-support': '1', 'support-type': 'tree(auto)',
             'support-threshold-angle': '30'}


def stamp():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def whole(path):
    """True when the file ends with its own '# END <name>' line."""
    s = open(path).read().rstrip('\n')
    return s.split('\n')[-1].strip() == '# END ' + os.path.basename(path)


def go(script, func, outname, *a, **k):
    p = script if script.startswith('/') else os.path.join(W, script)
    os.makedirs(os.path.join(W, 'out'), exist_ok=True)
    buf = io.StringIO(); t0 = time.time()
    try:
        if not whole(p):
            raise RuntimeError('script did not arrive whole: ' + p)
        buf.write('[%s  %s  sha256 %s]\n' % (stamp(), os.path.basename(p), hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]))
        with contextlib.redirect_stdout(buf):
            ns = runpy.run_path(p)
            ns[func](*a, **k)
    except Exception:
        buf.write('\nEXCEPTION\n' + traceback.format_exc())
    finally:
        buf.write('\n[%s  elapsed %.1f s]\n' % (stamp(), time.time() - t0))
        open(os.path.join(W, 'out', outname), 'w').write(buf.getvalue())
    print(buf.getvalue())


# ------------------------------------------------------------------ the model (read only)
def ctx():
    import adsk.core, adsk.fusion
    app = adsk.core.Application.get(); doc = app.activeDocument
    des = adsk.fusion.Design.cast(app.activeProduct)
    return app, doc, des, des.rootComponent


def guard(strict=True, very_high=False):
    """Document, version 91 of 91, not modified; counts; the 17 guard volumes (preflight method; very high when asked)."""
    import adsk.core, adsk.fusion
    app, doc, des, root = ctx(); df = doc.dataFile; bad = []
    rep = {'t': stamp(), 'doc': doc.name, 'version': [df.versionNumber, df.latestVersionNumber], 'modified': doc.isModified}
    if doc.name != DOC:
        bad.append('document %r' % doc.name)
    if df.versionNumber != VERSION or df.latestVersionNumber != VERSION:
        bad.append('version %s of %s' % (df.versionNumber, df.latestVersionNumber))
    if doc.isModified:
        bad.append('document modified')
    names = [b.name for b in root.bRepBodies]
    rep.update({'bodies': len(names), 'visible': sum(1 for b in root.bRepBodies if b.isVisible),
                'copies_v79': sorted(n for n in names if n.endswith('_v79')), 'copies_v85': sorted(n for n in names if n.endswith('_v85')),
                'copies_v88': sorted(n for n in names if n.endswith('_v88')),
                'older': len([n for n in names if re.search(r'_v\d+$', n) and not n.endswith(('_v79', '_v85', '_v88'))]),
                'AUD': [n for n in names if n.startswith(('AUD_', 'AUDIT_'))], 'TMP': [n for n in names if n.startswith(('TMP_', 'NEW_', 'R91_', 'PF91_'))],
                'dups': sorted(set(n for n in names if names.count(n) > 1))})
    vols = {}
    for nm, (vp, vh) in GUARD.items():
        b = root.bRepBodies.itemByName(nm)
        if b is None:
            bad.append(nm + ' missing'); continue
        v = b.volume * 1000.0
        r = {'pre': round(v, 3), 'lumps': b.lumps.count, 'pre_ok': abs(v - vp) <= TOL.get(nm, 0.001)}
        if very_high:
            w = b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0
            r['vh'] = round(w, 3); r['vh_ok'] = abs(w - vh) <= 0.001
        vols[nm] = r
        if not r['pre_ok'] or b.lumps.count != 1 or (very_high and not r['vh_ok']):
            bad.append(nm)
    rep['vols'] = vols; rep['bad'] = bad
    if bad and strict:
        raise RuntimeError('GUARD: %s' % bad)
    return rep, root


def world_mesh(body, tol_mm=0.01, max_dev_deg=10.0):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    mc.maxNormalDeviation = math.radians(max_dev_deg)
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - XC, (c[i + 1] * C12 - c[i + 2] * S12) * 10, H0 + (c[i + 1] * S12 + c[i + 2] * C12) * 10)
         for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def write_stl(path, P, T, name='mesh'):
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel print files v91 %s world mm' % name).encode()[:80]
    buf[0:len(hdr)] = hdr
    struct.pack_into('<I', buf, 80, len(T))
    off = 84
    for (a, b_, c_) in T:
        pa, pb, pc = P[a], P[b_], P[c_]
        u = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); v = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        struct.pack_into('<12fH', buf, off, n[0] / L, n[1] / L, n[2] / L, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2],
                         pc[0], pc[1], pc[2], 0)
        off += 50
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(buf)
    return len(T)


def apply_M(src, dst, M, label):
    """world STL -> bed STL by a 3x4 matrix; returns triangles, low, high, mesh volume."""
    b = open(src, 'rb').read(); n = struct.unpack_from('<I', b, 80)[0]; o = bytearray(84 + 50 * n)
    o[0:80] = ('HA panel print files v91 %s bed mm' % label).encode().ljust(80, b' ')[:80]
    struct.pack_into('<I', o, 80, n)
    lo = [1e9] * 3; hi = [-1e9] * 3; vol = 0.0; a = M
    for t in range(n):
        f = struct.unpack_from('<12f', b, 84 + 50 * t); v = []
        for k0 in (3, 6, 9):
            x, y, z = f[k0], f[k0 + 1], f[k0 + 2]
            q = [a[r][0] * x + a[r][1] * y + a[r][2] * z + a[r][3] for r in range(3)]
            for k in range(3):
                if q[k] < lo[k]: lo[k] = q[k]
                if q[k] > hi[k]: hi[k] = q[k]
            v += q
        vol += (v[0] * (v[4] * v[8] - v[5] * v[7]) - v[1] * (v[3] * v[8] - v[5] * v[6]) + v[2] * (v[3] * v[7] - v[4] * v[6])) / 6.0
        N = [a[r][0] * f[0] + a[r][1] * f[1] + a[r][2] * f[2] for r in range(3)]
        struct.pack_into('<12fH', o, 84 + 50 * t, N[0], N[1], N[2], *v, 0)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, 'wb').write(o)
    return n, [round(c, 4) for c in lo], [round(c, 4) for c in hi], round(vol, 3)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None


def jdump(fn, obj):
    p = fn if fn.startswith('/') else os.path.join(W, 'out', fn)
    if not os.path.abspath(p).startswith(OUTDIR + os.sep):
        raise RuntimeError('refused: writing outside print_files_v91: ' + p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, 'w'), indent=1, default=str)


def jload(fn):
    return json.load(open(fn if fn.startswith('/') else os.path.join(W, 'out', fn)))


# ------------------------------------------------------------------ offline tools and the slicer (no Fusion object touched)
def _env():
    e = dict(os.environ)
    for k in ('PYTHONHOME', 'PYTHONPATH', 'PYTHONEXECUTABLE', '__PYVENV_LAUNCHER__'):
        e.pop(k, None)
    return e


def _alive(pid):
    try:
        wp, _st = os.waitpid(pid, os.WNOHANG)
        if wp == pid:
            return False
    except (ChildProcessError, OSError):
        pass
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def tools(lst, wait=0, prog=None):
    """lst: [(name, cmd, args)]; starts every tool in the background (pf91_tools.py unless prog), then waits up to wait seconds."""
    ps = []; od = os.path.join(W, 'out'); os.makedirs(od, exist_ok=True)
    for (name, cmd, args) in lst:
        ap = os.path.join(od, name + '.args.json'); json.dump(args, open(ap, 'w'))
        pg = prog or os.path.join(W, 'pf91_tools.py')
        so = open(os.path.join(od, name + '.txt'), 'w')
        p = subprocess.Popen([PY, pg, cmd, ap], stdout=so, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             cwd=W, env=_env(), start_new_session=True)
        json.dump({'pid': p.pid, 't0': time.time()}, open(os.path.join(od, name + '.pid.json'), 'w'))
        ps.append((name, p))
    t0 = time.time()
    for (name, p) in ps:
        left = wait - (time.time() - t0)
        if left <= 0:
            print(name, 'running'); continue
        try:
            p.wait(timeout=left); print(name, 'done rc', p.returncode)
        except subprocess.TimeoutExpired:
            print(name, 'running')


def poll(names, tail=200):
    od = os.path.join(W, 'out')
    for n in names:
        pp = os.path.join(od, n + '.pid.json')
        if not os.path.exists(pp):
            print(n, 'unknown'); continue
        st = json.load(open(pp)); al = _alive(st['pid'])
        try:
            tl = open(os.path.join(od, n + '.txt')).read()[-tail:].replace('\n', ' | ')
        except Exception:
            tl = ''
        print(n, 'RUNNING' if al else 'done', '%.0f s' % (time.time() - st['t0']), '::', tl)


def mkjob(spec):
    """spec: job, process, filaments, bed, opts, title, desc, plates [{name, objects [{stl|path, pos, fil, subtype, params}]}],
    deliver [folder, file name] (a print file) or none (a work slice). Every object of a plate is one assembled object, as the
    re-check's jobs."""
    job = spec['job']; mac = os.path.join(W, 'slicer'); d = os.path.join(mac, 'jobs', job); os.makedirs(d, exist_ok=True)
    plates = []
    for p in spec['plates']:
        objs = []
        for o in p['objects']:
            pos = o.get('pos', (0.0, 0.0, 0.0))
            j = {'path': o.get('path') or os.path.join(BED, o['stl']), 'count': 1, 'filaments': [o.get('fil', 1)],
                 'subtype': o.get('subtype', 'normal_part'), 'pos_x': [float(pos[0])], 'pos_y': [float(pos[1])], 'pos_z': [float(pos[2])]}
            if not os.path.exists(j['path']):
                raise RuntimeError('missing ' + j['path'])
            if o.get('assemble'):
                j['assemble_index'] = [o['assemble']]
            if o.get('params'):
                j['print_params'] = {k: str(v) for k, v in o['params'].items()}
            objs.append(j)
        plates.append({'plate_name': p.get('name', job), 'need_arrange': False, 'objects': objs})
    json.dump({'plates': plates}, open(os.path.join(d, 'assemble.json'), 'w'), indent=1)
    opts = dict(BASE_OPTS); opts.update({k: str(v) for k, v in (spec.get('opts') or {}).items()})
    opts.setdefault('curr-bed-type', spec.get('bed', 'Textured PEI Plate'))
    opts.setdefault('filament-map', ','.join(str(i + 1) for i in range(len(spec['filaments']))) if len(spec['filaments']) > 1 else '1')
    desc = spec.get('desc', 'print files of version 91 - work slice')
    if ';' in desc or ';' in spec.get('title', job):
        raise RuntimeError('a semicolon in the title or description splits the metadata: ' + job)
    args = ['--debug=%s' % spec.get('debug', 2), '--datadir', mac + '/bsdata',
            '--load-settings', '%s/%s;%s/%s' % (FLAT, spec.get('machine', 'machine_X2D_0.4.json'), FLAT, spec['process']),
            '--load-filaments', ';'.join('%s/%s' % (FLAT, f) for f in spec['filaments']),
            '--load-assemble-list', '%s/jobs/%s/assemble.json' % (mac, job)]
    for k, v in opts.items():
        args += ['--%s=%s' % (k, v)]
    args += ['--metadata-name', 'Title;Description', '--metadata-value', '%s;%s' % (spec.get('title', job), desc)]
    if spec.get('slice', True):
        args += ['--slice', '0']
    args += ['--outputdir', '%s/out/%s' % (mac, job), '--export-3mf', job + '.3mf']
    json.dump(args, open(os.path.join(d, 'args.json'), 'w'), indent=1)
    json.dump(spec, open(os.path.join(d, 'spec.json'), 'w'), indent=1)
    od = os.path.join(mac, 'out', job); os.makedirs(od, exist_ok=True)
    if spec.get('map'):
        json.dump(spec['map'], open(os.path.join(od, 'map.json'), 'w'), indent=1)
    print('job', job, len(args), 'args')


def slicer(mode, jobs=(), only='ALL'):
    g = {'R2_DIR': W, 'R2_MODE': mode, 'R2_JOBS': list(jobs), 'R2_ONLY': only, '__name__': 'pfbs'}
    exec(compile(open(PFBS).read(), PFBS, 'exec'), g)
    g['run'](None)
# END pf91_lib.py
