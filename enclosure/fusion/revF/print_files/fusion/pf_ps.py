# pf_ps: lists the Bambu Studio processes (pid, start time, command) and, when R2_ARGS['term'] names a pid that is a
#   BambuStudio process started by this session's pf_open call (its start time must begin with R2_ARGS['lstart']), sends it
#   SIGTERM. Touches no Fusion object and no file.
import subprocess, signal


def run(_context):
    r = subprocess.run(['/bin/ps', '-axo', 'pid=,lstart=,comm='], capture_output=True, text=True, timeout=20)
    rows = [l for l in r.stdout.splitlines() if 'BambuStudio' in l]
    out = {'bambu': rows}
    t = R2_ARGS.get('term')
    if t:
        e = subprocess.run(['/bin/ps', '-p', str(t), '-o', 'lstart=,comm='], capture_output=True, text=True, timeout=20).stdout.strip()
        out['target'] = e
        if 'BambuStudio' in e and e.startswith(R2_ARGS['lstart']):
            os.kill(int(t), signal.SIGTERM); out['sent'] = 'SIGTERM'
        else:
            out['sent'] = 'no (not the session-started instance)'
    print(json.dumps(out))
