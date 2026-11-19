import os, hashlib
D = os.path.expanduser('~/Documents/HA_panel_renders/print_files_v67/_work/lib/')
R2_ARGS = {'files': ['shell_plan_blk_v2.stl']}
for f, h in [('pflib67.py', '1e251d343296c1c94e944a343c6b931bd2152a6607ac0e4a79ca49f51f1d3290'), ('steps/pf67_4_copy.py', '04ea36ca010d9dd37f2bfb6988f41b8bd56e00ca35a3a8fe4ddade0e5b236ec7')]:
    s = open(D + f, 'rb').read()
    if hashlib.sha256(s).hexdigest() != h:
        raise RuntimeError(f + ' on the Mac differs')
    exec(compile(s, D + f, 'exec'), globals())
