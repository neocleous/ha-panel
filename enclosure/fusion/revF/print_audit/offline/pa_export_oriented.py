import sys
sys.path.insert(0, '/home/claude/pa')
from pa_geom import *
for tag, okey in [(t, 'plan') for t in ORIENT] + [('slab', 'side+x')]:
    mw = load_world(tag); mb, M = to_build(mw, ORIENT[tag][okey])
    mb.export('/home/claude/pa/slice/orient/%s_%s.stl' % (tag, okey))
    print(tag, okey, [round(float(v), 2) for v in mb.extents])
