# r2_bs (block 2; D139: Bambu Studio 02.09.01.70 headless from Fusion's Python). READ-ONLY on the design: it never touches the
#   Fusion document. MODE 'start': for each job, writes its assemble list and arguments (inline, from mkjob.py) to
#   print_audit_recheck2/slicer/jobs/<job>/ and starts Bambu Studio's command-line slicer in the background (at most R2_PAR at once;
#   the rest wait in a queue file that each later 'poll' call advances). MODE 'poll': reports every job's state and result.
#   Writes only in slicer/jobs/, slicer/out/, slicer/bsdata/ and slicer/queue.json of the recheck2 folder.
import subprocess, os, json, time
R2_BS_BIN = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
R2_PAR = 3
# R2_MODE ('start' | 'poll'), R2_JOBS (job names; their assemble.json and args.json are already in slicer/jobs/<job>/) and
#   R2_ONLY ('ALL' or 'job1,job2') are set by the call before this file is executed.
R2_Q = os.path.join(R2_DIR, 'slicer', 'queue.json')


def r2_alive(pid):
    # children of the Fusion process stay zombies until reaped: waitpid(WNOHANG) first, then kill(pid, 0)
    try:
        wp, _st = os.waitpid(pid, os.WNOHANG)
        if wp == pid:
            return False
    except ChildProcessError:
        pass
    except OSError:
        pass
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def r2_launch(job):
    jd = os.path.join(R2_DIR, 'slicer', 'jobs', job)
    a = json.load(open(os.path.join(jd, 'args.json')))
    outd = os.path.join(R2_DIR, 'slicer', 'out', job); os.makedirs(outd, exist_ok=True)
    for f in os.listdir(outd):
        if f in ('result.json', 'started.json') or f.endswith(('.3mf', '.gcode')):
            os.replace(os.path.join(outd, f), os.path.join(outd, f + '.old'))
    so = open(os.path.join(outd, 'stdout.txt'), 'w'); se = open(os.path.join(outd, 'stderr.txt'), 'w')
    p = subprocess.Popen([R2_BS_BIN] + a, stdout=so, stderr=se, stdin=subprocess.DEVNULL, cwd=outd, start_new_session=True)
    json.dump({'pid': p.pid, 't0': time.time(), 'args': a}, open(os.path.join(outd, 'started.json'), 'w'))
    return p.pid


def r2_state(job):
    outd = os.path.join(R2_DIR, 'slicer', 'out', job)
    sp = os.path.join(outd, 'started.json')
    if not os.path.exists(sp):
        return {'job': job, 'state': 'queued'}
    st = json.load(open(sp)); alive = r2_alive(st['pid'])
    r = {'job': job, 'state': 'running' if alive else 'done', 'elapsed_s': round(time.time() - st['t0'], 1)}
    rp = os.path.join(outd, 'result.json')
    if not alive and os.path.exists(rp):
        try:
            res = json.load(open(rp))
            pls = res.get('sliced_plates') or [{}]
            r.update({'rc': res.get('return_code'), 'err': res.get('error_string'),
                      'plates': [[pl.get('id'), round(pl.get('main_predication', 0) / 60.0, 1), round(pl.get('total_predication', 0) / 60.0, 1),
                                  [round(f.get('total_used_g', 0), 2) for f in pl.get('filaments', [])], pl.get('filament_change_times'),
                                  (pl.get('warning_message') or '')[:160]] for pl in pls]})
        except Exception as e:
            r['result_err'] = str(e)[:100]
    elif not alive:
        try:
            r['stdout_tail'] = open(os.path.join(outd, 'stdout.txt')).read()[-300:]
        except Exception:
            pass
    return r


def run(_context):
    os.makedirs(os.path.join(R2_DIR, 'slicer', 'bsdata'), exist_ok=True)
    q = json.load(open(R2_Q)) if os.path.exists(R2_Q) else {'pending': [], 'all': []}
    if R2_MODE == 'start':
        for job in R2_JOBS:
            jd = os.path.join(R2_DIR, 'slicer', 'jobs', job)
            if not (os.path.exists(os.path.join(jd, 'assemble.json')) and os.path.exists(os.path.join(jd, 'args.json'))):
                raise RuntimeError('job files missing: ' + job)
            sp = os.path.join(R2_DIR, 'slicer', 'out', job, 'started.json')
            if os.path.exists(sp):
                os.replace(sp, sp + '.old')
            if job in q['pending']:
                q['pending'].remove(job)
            q['pending'].append(job)
            if job not in q['all']:
                q['all'].append(job)
    running = [j for j in q['all'] if r2_state(j)['state'] == 'running']
    while q['pending'] and len(running) < R2_PAR:
        j = q['pending'].pop(0); r2_launch(j); running.append(j)
    json.dump(q, open(R2_Q, 'w'), indent=1)
    want = list(R2_JOBS) if R2_MODE == 'start' else (R2_ONLY.split(',') if R2_ONLY not in ('', 'ALL') else q['all'])
    print(json.dumps({'states': [r2_state(j) for j in want], 'pending': q['pending']}, separators=(',', ':')))
