import os, json, time, subprocess
# rc6_bs_batch (block 2; Daniel 2026-11-14 14:41: Bambu Studio headless from a Fusion script). READ-ONLY on the design: it never
#   touches the Fusion document. RC_MODE 'start': for each job, writes its assemble list and arguments (inline, from mkjob.py) to
#   print_audit_recheck/slicer/jobs/<job>/ and starts Bambu Studio's command-line slicer in the background (at most RC_PAR at once;
#   the rest wait in a queue file that each later 'poll' call advances). RC_MODE 'poll': reports every job's state and result.
#   Writes only in slicer/jobs/, slicer/out/ and slicer/bsdata/.
RC_DIR = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck')
RC_BS_BIN = '/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'
RC_MODE = '__MODE__'
RC_PAR = 3
RC_JOBS = __JOBS__          # list of [job, assemble, args] ('start'); ignored for 'poll'
RC_Q = os.path.join(RC_DIR, 'slicer', 'queue.json')


def rc_alive(pid):
    # Bambu Studio children of the Fusion process stay as zombies until reaped; os.kill(pid, 0) still succeeds on a zombie,
    #   so reap first (waitpid WNOHANG) and only then probe.
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


def rc_launch(job):
    jd = os.path.join(RC_DIR, 'slicer', 'jobs', job)
    a = json.load(open(os.path.join(jd, 'args.json')))
    outd = os.path.join(RC_DIR, 'slicer', 'out', job); os.makedirs(outd, exist_ok=True)
    for f in os.listdir(outd):
        if f in ('result.json', 'started.json') or f.endswith(('.3mf', '.gcode')):
            os.rename(os.path.join(outd, f), os.path.join(outd, f + '.old'))
    so = open(os.path.join(outd, 'stdout.txt'), 'w'); se = open(os.path.join(outd, 'stderr.txt'), 'w')
    p = subprocess.Popen([RC_BS_BIN] + a, stdout=so, stderr=se, stdin=subprocess.DEVNULL, cwd=outd, start_new_session=True)
    json.dump({'pid': p.pid, 't0': time.time(), 'args': a}, open(os.path.join(outd, 'started.json'), 'w'))
    return p.pid


def rc_state(job):
    outd = os.path.join(RC_DIR, 'slicer', 'out', job)
    sp = os.path.join(outd, 'started.json')
    if not os.path.exists(sp):
        return {'job': job, 'state': 'queued'}
    st = json.load(open(sp)); alive = rc_alive(st['pid'])
    r = {'job': job, 'state': 'running' if alive else 'done', 'elapsed_s': round(time.time() - st['t0'], 1)}
    rp = os.path.join(outd, 'result.json')
    if not alive and os.path.exists(rp):
        try:
            res = json.load(open(rp))
            pl = (res.get('sliced_plates') or [{}])[0]
            r.update({'rc': res.get('return_code'), 'err': res.get('error_string'), 'main_s': pl.get('main_predication'),
                      'total_s': pl.get('total_predication'), 'g': [round(f.get('total_used_g', 0), 2) for f in pl.get('filaments', [])],
                      'warn': (pl.get('warning_message') or '')[:200]})
        except Exception as e:
            r['result_err'] = str(e)[:100]
    return r


def run(_context):
    os.makedirs(os.path.join(RC_DIR, 'slicer', 'bsdata'), exist_ok=True)
    q = json.load(open(RC_Q)) if os.path.exists(RC_Q) else {'pending': [], 'all': []}
    if RC_MODE == 'start':
        for job, asm, args in RC_JOBS:
            jd = os.path.join(RC_DIR, 'slicer', 'jobs', job); os.makedirs(jd, exist_ok=True)
            json.dump(asm, open(os.path.join(jd, 'assemble.json'), 'w'), indent=1)
            json.dump(args, open(os.path.join(jd, 'args.json'), 'w'), indent=1)
            sp = os.path.join(RC_DIR, 'slicer', 'out', job, 'started.json')
            if os.path.exists(sp):
                os.rename(sp, sp + '.old')
            q['pending'].append(job)
            if job not in q['all']:
                q['all'].append(job)
    running = [j for j in q['all'] if rc_state(j)['state'] == 'running']
    while q['pending'] and len(running) < RC_PAR:
        j = q['pending'].pop(0); rc_launch(j); running.append(j)
    json.dump(q, open(RC_Q, 'w'), indent=1)
    print(json.dumps({'states': [rc_state(j) for j in q['all']], 'pending': q['pending']}, separators=(',', ':')))
