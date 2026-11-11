# rev F step 3 repeated (2026-11-11) - helpers for the i scripts (main board rev 3.1 placed, fourth post, reach, two leads).
# The h library with this pass's data folder (fp/step3r) and a cache purge. The i scripts are either new (i0, i1b, i1d, i2a, i2d, i4c)
# or run an h script unchanged apart from the names given in their header (run_h).
# A temporary copy in the cache is keyed by name and volume only: a body that moved without changing its volume (the board's connector
# group, a lead with a moved node of equal length) would be answered from the old copy. purge() after every change to the model.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
S3 = os.path.join(FP, 'step3r')
SCR = os.path.join(FP, 'scripts')


def purge(prefixes=('MAIN_', 'RESP_CARRIER', 'LEAD_'), tables=('h1b_clash', 'h1c', 'h1e_C', 'h3c', 'h3e', 'i1b_clash')):
    c = cache(); n = 0
    for k in list(c.keys()):
        if (isinstance(k, tuple) and len(k) > 1 and str(k[1]).startswith(tuple(prefixes))) or k in tables:
            del c[k]; n += 1
    return n


def run_h(name, repl=(), g=None):       # exec an h script with this library in place of the h library and the replacements given
    src = open(os.path.join(SCR, name), encoding='utf-8').read().replace("'v5f_h_lib.py'", "'v5f_i_lib.py'")
    for a, b in repl:
        if a not in src:
            raise RuntimeError('replacement not found in %s: %s' % (name, a))
        src = src.replace(a, b)
    ns = {'__name__': 'v5f_run_h'}
    ns.update(g or {})
    exec(compile(src, name, 'exec'), ns)
    return ns
