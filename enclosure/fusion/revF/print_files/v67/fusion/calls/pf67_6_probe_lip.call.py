import os, hashlib
D = os.path.expanduser('~/Documents/HA_panel_renders/print_files_v67/_work/lib/')
R2_ARGS = {}
for f, h in [('pflib67.py', '1e251d343296c1c94e944a343c6b931bd2152a6607ac0e4a79ca49f51f1d3290'), ('steps/pf67_6_probe_lip.py', 'fc334a8ff672569740b8697303854d530597502698d87e3ff6eabcee4fef91b2')]:
    s = open(D + f, 'rb').read()
    if hashlib.sha256(s).hexdigest() != h:
        raise RuntimeError(f + ' on the Mac differs')
    exec(compile(s, D + f, 'exec'), globals())
