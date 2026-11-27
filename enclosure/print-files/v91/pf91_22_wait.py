# Print files of version 91: advances the slicer's queue and waits on it for up to maxs seconds, by waiting on a child process
# (/bin/sleep), not time.sleep(); then one line a job. No Fusion object.
import os, json, runpy, io, contextlib, subprocess, time
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
J = runpy.run_path(os.path.join(D, 'pf91_20_jobs.py'))


def wait(maxs=60):
    t0 = time.time()
    while True:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            L['slicer']('poll')
        st = json.loads(buf.getvalue().split('\n')[0])
        busy = st['pending'] or any(s['state'] == 'running' for s in st['states'])
        if not busy or time.time() - t0 > maxs:
            break
        subprocess.run(['/bin/sleep', '5'])
    J['status']()
    print('wait: %.0f s, %s' % (time.time() - t0, 'still busy' if busy else 'idle'))
# END pf91_22_wait.py
