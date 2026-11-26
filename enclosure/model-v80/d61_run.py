# A runner for the close: several jobs in one Fusion call, each job's printed output and any error caught into one file in
# this pass's folder. A job is (script, function, args, kwargs) of a script of this folder. A job is not begun once 'limit'
# seconds of the call are used; it is then listed as NOT RUN. Changes nothing itself.
# get(sha, fn, sha256) fetches a script of this pass from the branch and checks it arrived whole.
# Run: runpy.run_path(D + 'd61_run.py')['go'](jobs, outfile, limit)
import runpy, io, contextlib, traceback, time, hashlib, urllib.request, os

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'


U = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/enclosure/model-v80/%s'


def get(sha, fn, h256):
    """A script of this pass fetched from the branch at a commit into this folder, unless the file here already has that
    sha256; refused when what arrives has another sha256 or does not end with its END line."""
    p = D + fn
    if not (os.path.exists(p) and hashlib.sha256(open(p, 'rb').read()).hexdigest() == h256):
        src = urllib.request.urlopen(U % (sha, fn), timeout=25).read()
        if hashlib.sha256(src).hexdigest() != h256 or not src.rstrip().endswith(b'# END'):
            raise RuntimeError(fn + ' did not arrive whole')
        open(p, 'wb').write(src)
    return p


def go(jobs, outfile, limit=55):
    b = io.StringIO(); t0 = time.time(); mods = {}
    for script, func, args, kw in jobs:
        if time.time() - t0 > limit:
            b.write('NOT RUN (time): %s %s %s %s\n' % (script, func, args, kw)); continue
        t1 = time.time()
        try:
            if script not in mods:
                mods[script] = runpy.run_path(D + script)
            with contextlib.redirect_stdout(b):
                mods[script][func](*args, **kw)
        except Exception:
            b.write('%s %s %s: %s\n' % (script, func, args, traceback.format_exc()[-800:]))
        b.write('   [%s %s %s: %.1f s]\n' % (script, func, args, time.time() - t1))
    open(D + outfile, 'w').write('call took %.1f s\n' % (time.time() - t0) + b.getvalue())
# END
