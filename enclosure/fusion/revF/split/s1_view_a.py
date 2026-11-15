# Block 1: set visibility and camera for a screenshot (no geometry change). MODE: 'set' or 'restore'.
import adsk.core, adsk.fusion, sys, json
MODE = 'set'
SHOW = ['HOUSING_F_front']
EYE = (330.0, 260.0, 10.0)
TGT = (0.0, 0.0, 95.0)
EXT = None


def run(_context):
    k = sys.modules['v5f_k']; X = k.K()
    st = sys.modules.setdefault('split_state', type(sys)('split_state'))
    if MODE == 'set':
        if not hasattr(st, 'vis0'):
            st.vis0 = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
        k.show(X, SHOW)
        k.cam(X, EYE, TGT, ext=EXT, angle=None if EXT else 0.35, up=(0, 0, 1))
        print('shown', len(SHOW))
    else:
        k.show(X, st.vis0)
        print('restored', len(st.vis0), sum(1 for b in X.root.bRepBodies if b.isLightBulbOn))
