import os, hashlib
D = os.path.expanduser('~/Documents/HA_panel_renders/print_files_v67/_work/lib/')
R2_ARGS = {'mode': 'start', 'jobs': ['X5_T4_dbg']}
for f, h in [('pflib67.py', '1e251d343296c1c94e944a343c6b931bd2152a6607ac0e4a79ca49f51f1d3290'), ('pfbs.py', '250dccf944d3c7a24d0c90653a040a8e65de945bb663394b3d66962bb4e702d9'), ('steps/pf_bs.py', '479ebe52692386f931a9111f79c403fbfb0d3fabaee79ca792a02c01239ef3cc')]:
    s = open(D + f, 'rb').read()
    if hashlib.sha256(s).hexdigest() != h:
        raise RuntimeError(f + ' on the Mac differs')
    exec(compile(s, D + f, 'exec'), globals())
