# Print files of version 91, block 1: the adhesion piece's meshes against the re-check's as sets of triangles (any order), by the
# re-check's own tool (r91_tools.py cmpset, read where it is). No Fusion object.
import os, runpy
L = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pf91_lib.py'))


def main(wait=60):
    W = L['W']; R = L['RD91']
    pairs = [['world chin8', W + '/stl/world/shell_chin8.stl', R + '/stl/world/shell_chin8.stl'],
             ['bed chin8', W + '/stl/bed/shell_chin8.stl', R + '/stl/bed/shell_chin8.stl']]
    L['tools']([('pf91_cmp_chin8', 'cmpset', {'pairs': pairs})], wait, prog=os.path.join(R, 'r91_tools.py'))
    L['poll'](['pf91_cmp_chin8'], 800)
# END pf91_11_cmpset.py
