# rev F h1g (2026-11-11): step 3, block 1 - colours for the rev 3 board's bodies so that pictures can be read: board green, supply
#   module black, connectors white, tall parts blue, low parts grey, plug envelopes yellow, tolerance cap red, Pi power plug black.
#   Appearances are copied from Fusion's library into the design by name (first name found).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
WANT = globals().get('WANT', {
    'MAIN_pcb': ('Plastic - Matte (Green)', 'Paint - Enamel Glossy (Green)'),
    'MAIN_PS1': ('Plastic - Matte (Black)', 'BLK_mock'), 'MAIN_J2_plug_env': ('Plastic - Matte (Black)', 'BLK_mock'),
    'MAIN_conn': ('Plastic - Matte (White)', 'Paint - Enamel Glossy (White)'),
    'MAIN_tall': ('Plastic - Matte (Blue)', 'Paint - Enamel Glossy (Blue)'),
    'MAIN_low': ('Plastic - Matte (Gray)', 'Plastic - Matte (Grey)', 'Aluminum - Satin'),
    'MAIN_plug_env': ('Plastic - Matte (Yellow)', 'Paint - Enamel Glossy (Yellow)'),
    'MAIN_PS1_tol': ('Plastic - Matte (Red)', 'Paint - Enamel Glossy (Red)')})


def find_ap(X, names):
    for nm in names:
        a = X.des.appearances.itemByName(nm)
        if a:
            return a
    for i in range(X.app.materialLibraries.count):
        lib = X.app.materialLibraries.item(i)
        if 'Appearance' not in lib.name:
            continue
        for nm in names:
            try:
                a = lib.appearances.itemByName(nm)
            except Exception:
                a = None
            if a:
                return X.des.appearances.addByCopy(a, nm)
    return None


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        out = {}
        for n, names in WANT.items():
            b = X.body(n)
            a = find_ap(X, names)
            if b is not None and a is not None:
                b.appearance = a
            out[n] = a.name if a else None
        st['set'] = out
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1g', st)


run(None)
