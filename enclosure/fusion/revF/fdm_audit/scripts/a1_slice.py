"""Block 1: slice every printed part in its print orientation; check the layers against the volume."""
import sys, time, numpy as np
from fdm_lib import *
names = sys.argv[1:] or list(GUARD)
for name in names:
    t0 = time.time()
    p = Part(name)
    L = p.slice(cache=False)
    import pickle
    pickle.dump(L, open(os.path.join(DATA, 'layers_%s_%03d.pkl' % (name, round(p.lh*100))), 'wb'))
    areas = np.array([g.area for _, g in L])
    vol = areas.sum() * p.lh
    npoly = [len(polys_of(g)) for _, g in L]
    print('%-16s up_world (%.3f %.3f %.3f) layers %d height %.2f first-layer %.1f max %.1f sum*lh %.1f (mesh %.1f, %+.2f%%) empty %d dt %.0fs' % (
        name, p.up@XW, p.up@YW, p.up@ZW, len(L), p.height, areas[0], areas.max(), vol, p.m.volume, 100*(vol/p.m.volume-1), int((areas<1e-6).sum()), time.time()-t0), flush=True)
