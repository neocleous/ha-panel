# rc3_slicer_setup (block 2 prep; Daniel 2026-11-14 14:41: Bambu Studio headless from a Fusion script). READ-ONLY on the design.
#   Copies Bambu Studio's system presets needed for the X2D (machine, processes, filaments) with their whole "inherits" chains
#   from ~/Library/Application Support/BambuStudio/system/BBL into print_audit_recheck/slicer/profiles/ (copies, the originals
#   untouched), and writes Bambu Studio's command-line help to slicer/bs_help.txt. Starts nothing but "BambuStudio --help".
import shutil, subprocess

RC_BS_BIN = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
RC_BS_SYS = os.path.expanduser('~/Library/Application Support/BambuStudio/system/BBL')
RC_WANT = {'machine': ['Bambu Lab X2D 0.4 nozzle'],
           'process': ['0.20mm Standard @BBL X2D', '0.16mm Standard @BBL X2D', '0.12mm High Quality @BBL X2D',
                       '0.08mm High Quality @BBL X2D', '0.20mm High Quality @BBL X2D', '0.16mm High Quality @BBL X2D'],
           'filament': ['Bambu ABS @BBL X2D 0.4 nozzle', 'Bambu ASA @BBL X2D 0.4 nozzle', 'Bambu Support for ABS @BBL X2D 0.4 nozzle',
                        'Generic ABS @BBL X2D 0.4 nozzle', 'Generic ASA @BBL X2D 0.4 nozzle']}


def run(_context):
    t0 = time.time(); out = {'copied': {}, 'missing': []}
    dst = os.path.join(RC_DIR, 'slicer', 'profiles')
    for kind, names in RC_WANT.items():
        os.makedirs(os.path.join(dst, kind), exist_ok=True)
        todo = list(names); seen = set()
        while todo:
            n = todo.pop()
            if n in seen:
                continue
            seen.add(n)
            src = os.path.join(RC_BS_SYS, kind, n + '.json')
            if not os.path.exists(src):
                out['missing'].append([kind, n]); continue
            shutil.copy2(src, os.path.join(dst, kind, n + '.json'))
            d = json.load(open(src))
            out['copied'].setdefault(kind, []).append([n, d.get('inherits', ''), d.get('from', ''), d.get('instantiation', '')])
            if d.get('inherits'):
                todo.append(d['inherits'])
    vj = os.path.join(RC_BS_SYS, '..', 'BBL.json')
    if os.path.exists(vj):
        shutil.copy2(vj, os.path.join(dst, 'BBL.json'))
    r = subprocess.run([RC_BS_BIN, '--help'], capture_output=True, text=True, timeout=40)
    open(os.path.join(RC_DIR, 'slicer', 'bs_help.txt'), 'w').write('rc=%s\n--stdout--\n%s\n--stderr--\n%s\n' % (r.returncode, r.stdout, r.stderr))
    out['help_rc'] = r.returncode; out['help_len'] = [len(r.stdout), len(r.stderr)]
    out['t_s'] = round(time.time() - t0, 1)
    rc_out(os.path.join(RC_DIR, 'data', 'rc3_slicer_setup.json'), out)
    rc_log('rc3_slicer_setup', 'run', {'t_s': out['t_s'], 'help_rc': r.returncode})
    print(json.dumps(out, separators=(',', ':')))
