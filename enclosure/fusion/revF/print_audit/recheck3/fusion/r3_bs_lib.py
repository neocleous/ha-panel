# recheck3: Bambu Studio 02.09.01.70 headless from Fusion's Python (D139) - recheck2's r2bs.py with this run's folder. It never touches
#   the Fusion document. MODE 'start': queue the jobs (their assemble.json and args.json are in slicer/jobs/<job>/) and start up to
#   R3_PAR at once; 'poll': report every job's state and start queued ones. No time.sleep() (lesson 215).
import adsk.core, subprocess, os, json, time
R3_DIR = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck3')
R3_BS_BIN = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
R3_PAR = 3
R3_Q = os.path.join(R3_DIR, 'slicer', 'queue.json')

def r3_alive(pid):
    try:
        wp, _st = os.waitpid(pid, os.WNOHANG)
        if wp == pid:
            return False
    except ChildProcessError:
        pass
    except OSError:
        pass
    try:
        os.kill(pid, 0); return True
    except OSError:
        return False

def r3_launch(job):
    jd = os.path.join(R3_DIR, 'slicer', 'jobs', job)
    a = json.load(open(os.path.join(jd, 'args.json')))
    outd = os.path.join(R3_DIR, 'slicer', 'out', job); os.makedirs(outd, exist_ok=True)
    for f in os.listdir(outd):
        if f in ('result.json', 'started.json') or f.endswith(('.3mf', '.gcode')):
            os.replace(os.path.join(outd, f), os.path.join(outd, f + '.old'))
    so = open(os.path.join(outd, 'stdout.txt'), 'w'); se = open(os.path.join(outd, 'stderr.txt'), 'w')
    p = subprocess.Popen([R3_BS_BIN] + a, stdout=so, stderr=se, stdin=subprocess.DEVNULL, cwd=outd, start_new_session=True)
    json.dump({'pid': p.pid, 't0': time.time(), 'args': a}, open(os.path.join(outd, 'started.json'), 'w'))
    return p.pid

def r3_state(job):
    outd = os.path.join(R3_DIR, 'slicer', 'out', job)
    sp = os.path.join(outd, 'started.json')
    if not os.path.exists(sp):
        return {'job': job, 'state': 'queued'}
    st = json.load(open(sp)); alive = r3_alive(st['pid'])
    r = {'job': job, 'state': 'running' if alive else 'done', 's': round(time.time() - st['t0'])}
    rp = os.path.join(outd, 'result.json')
    if not alive and os.path.exists(rp):
        try:
            res = json.load(open(rp)); pls = res.get('sliced_plates') or [{}]
            r.update({'rc': res.get('return_code'), 'err': res.get('error_string'),
                      'plates': [[round(pl.get('main_predication', 0) / 60.0, 1), round(pl.get('total_predication', 0) / 60.0, 1),
                                  [round(f.get('total_used_g', 0), 2) for f in pl.get('filaments', [])], (pl.get('warning_message') or '')[:200]] for pl in pls]})
            r['gcode'] = [f for f in os.listdir(outd) if f.endswith('.gcode')]
        except Exception as e:
            r['result_err'] = str(e)[:100]
    elif not alive:
        try:
            r['stdout_tail'] = open(os.path.join(outd, 'stdout.txt')).read()[-300:]
        except Exception:
            pass
    return r

def run(_context: str):
    os.makedirs(os.path.join(R3_DIR, 'slicer', 'bsdata'), exist_ok=True)
    q = json.load(open(R3_Q)) if os.path.exists(R3_Q) else {'pending': [], 'all': []}
    if R3_MODE == 'start':
        for job in R3_JOBS:
            jd = os.path.join(R3_DIR, 'slicer', 'jobs', job)
            if not (os.path.exists(os.path.join(jd, 'assemble.json')) and os.path.exists(os.path.join(jd, 'args.json'))):
                raise RuntimeError('job files missing: ' + job)
            sp = os.path.join(R3_DIR, 'slicer', 'out', job, 'started.json')
            if os.path.exists(sp):
                os.replace(sp, sp + '.old')
            if job in q['pending']:
                q['pending'].remove(job)
            q['pending'].append(job)
            if job not in q['all']:
                q['all'].append(job)
    running = [j for j in q['all'] if r3_state(j)['state'] == 'running']
    while q['pending'] and len(running) < R3_PAR:
        j = q['pending'].pop(0); r3_launch(j); running.append(j)
    json.dump(q, open(R3_Q, 'w'), indent=1)
    want = list(R3_JOBS) if R3_MODE == 'start' else (R3_ONLY.split(',') if R3_ONLY not in ('', 'ALL') else q['all'])
    app = adsk.core.Application.get()
    print(json.dumps({'t': time.strftime('%H:%M:%S'), 'doc_modified': app.activeDocument.isModified, 'states': [r3_state(j) for j in want], 'pending': q['pending']}, separators=(',', ':')))
