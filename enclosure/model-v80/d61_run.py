# A runner for the close: several jobs in one Fusion call, each job's printed output and any error caught into one file in
# this pass's folder. A job is (script, function, args, kwargs) of a script of this folder. A job is not begun once 'limit'
# seconds of the call are used; it is then listed as NOT RUN. Changes nothing itself.
# Run: runpy.run_path(D + 'd61_run.py')['go'](jobs, outfile, limit)
import runpy, io, contextlib, traceback, time

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'


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
