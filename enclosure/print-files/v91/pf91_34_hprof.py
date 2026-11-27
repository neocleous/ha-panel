# Print files of version 91, block 4: the left box's lower screw bore (6.2 across, from its rear face at bed 0 to its seat at bed 33)
# on plate P1b, band by band: where along it the support stands and where the bore has its wall all round. No Fusion object.
import os, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
SO = os.path.join(L['W'], 'slicer', 'out')


def main(wait=60):
    lst = [{'cmd': 'hprof', 'job': os.path.join(SO, j), 'A': [61.03, 141.6, 0.0], 'B': [61.03, 141.6, 33.0], 'd': 6.2, 'step': 1.0} for j in ('A02_P1b', 'T02_P1b')]
    L['tools']([('pf91_hprof_boxL_bore', 'hprof', lst)], wait)
    print(open(os.path.join(L['W'], 'out', 'pf91_hprof_boxL_bore.txt')).read())
# END pf91_34_hprof.py
