import os, hashlib
D = os.path.expanduser('~/Documents/HA_panel_renders/print_files_v67/_work/lib/')
R2_ARGS = {}
for f, h in [('pflib67.py', '1e251d343296c1c94e944a343c6b931bd2152a6607ac0e4a79ca49f51f1d3290'), ('steps/pf67_1_export.py', '003e66d33174895feea4d246ae0532468b3890b215f425c1cac8bcc60cf901fa')]:
    s = open(D + f, 'rb').read()
    if hashlib.sha256(s).hexdigest() != h:
        raise RuntimeError(f + ' on the Mac differs')
    exec(compile(s, D + f, 'exec'), globals())
