# Print files of version 91: plates seen from above (pf91_tools png), into _work/png/. No Fusion object.
#   pics(): P1b in ABS and in PLA, every layer and the first layer alone (D509: the clips' places checked on a picture); P7 in ABS.
import os, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
SO = os.path.join(L['W'], 'slicer', 'out'); PNG = os.path.join(L['W'], 'png')


def pics(wait=0):
    os.makedirs(PNG, exist_ok=True)
    lst = []
    for job in ('A02_P1b', 'T02_P1b'):
        lst.append({'cmd': 'png', 'job': os.path.join(SO, job), 'out': os.path.join(PNG, job + '_all.png'), 'ppm': 3.0})
        lst.append({'cmd': 'png', 'job': os.path.join(SO, job), 'out': os.path.join(PNG, job + '_first.png'), 'ppm': 3.0, 'z0': 0.0, 'z1': 0.25})
    lst.append({'cmd': 'png', 'job': os.path.join(SO, 'A04_P7'), 'out': os.path.join(PNG, 'A04_P7_all.png'), 'ppm': 3.0})
    L['tools']([('pf91_png_%d' % i, 'png', [x]) for i, x in enumerate(lst)], wait)
# END pf91_31_pic.py
