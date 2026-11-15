# change1/c1_calls.py - change pass after the split's audit (2026-11-15), block 1: the five changes, save g20, archive.
# Each function is the body of one connector call's run(_context), in order. lib_entry.py is in sys.modules['cp1e'].
# Only change_* , save and export change the model; compare_leadins is read-only (temporary bodies).
import adsk.core, adsk.fusion, sys, time, math, os


def compare_leadins(_context):                       # read-only: version 64, F44 alone, F44 + lead-in A (round the pocket's axis), F44 + B (square to the face)
    k = sys.modules['cp1k']; m = sys.modules['cp1e']; X = k.K(); k.budget(65)
    lugs = {}
    for var in ('v64', 'F44', 'A', 'B'):
        lugs[var] = {}
        for side in ('left', 'right'):
            c = m.crop(X, side)
            if var != 'v64':
                m.fill44(X, side, c)                 # left +3.2923, right +3.4119 mm3
            if var == 'A':
                m.leadA(X, side, c)                  # -2.5447 / -2.6966
            if var == 'B':
                m.leadB(X, side, c)                  # -1.6131 / -1.5506
            lugs[var][side] = c
    m.R['lugs'] = lugs
    res = m.R.setdefault('sim2', {})
    for var in ('v64', 'A', 'B'):
        for i in range(21):
            e = round(-0.5 + 0.05 * i, 2)
            res[(var, e)] = m.sim2(X, var, e)        # split over calls with a time check
    # v64: home from -0.45 to +0.50 (clean -0.25..+0.25); stops at -0.50: right insert on the flat face (0 deg) 0.94 before home
    # A:   stops from |e| 0.40 (contact at 29-32 deg, no sideways way within the step): no bevel on the deep side
    # B:   clean -0.30..+0.35; every other offset to +-0.50 guided home (45 deg lead-in or 80 deg wall); none stops


def change_boxes(_context):                           # F44 + F45 (variant B) on both boxes
    k = sys.modules['cp1k']; m = sys.modules['cp1e']; X = k.K()
    st = X.state()
    if st['version'] != 64 or st['modified'] or st['bodies'] != 397:
        raise RuntimeError('unexpected state %s' % st)
    for side, name in (('left', 'SPKBOX_L'), ('right', 'SPKBOX_R')):
        b = X.cp(X.body(name))
        m.fill44(X, side, b); m.leadB(X, side, b)
        if b.lumps.count != 1:
            raise RuntimeError(name)
        X.swap(name, b, '_v64')
    # SPKBOX_L 26086.635: fill +3.2925, lead-in -1.6055 -> 26088.32; SPKBOX_R 26807.965: +3.4118, -1.5521 -> 26809.82


def change_shell(_context):                           # F46: the bottom posts' pegs 7.0 -> 7.2
    k = sys.modules['cp1k']; X = k.K()
    b = X.cp(X.body('HOUSING_F_front'))
    add = X.cyld(85.0, -82.0, 3.6, 11.6, 12.8); X.uni(add, X.cyld(-85.0, -82.0, 3.6, 11.6, 12.8))
    X.uni(b, add)
    cut = X.cyld(85.0, -82.0, 2.0, 11.1, 17.95); X.uni(cut, X.cyld(-85.0, -82.0, 2.0, 11.1, 17.95))     # the insert holes as before
    X.dif(b, cut)
    X.swap('HOUSING_F_front', b, '_v64')             # +35.5126 -30.1593 = +5.3533 -> 104433.98; 1 lump


def change_plate(_context):                           # F46: the screen plate's pocket and slot 0.2 larger
    k = sys.modules['cp1k']; X = k.K()
    b = X.cp(X.body('HOUSING_F_plate'))
    cut = X.cyld(85.0, -82.0, 3.725, 11.4, 14.0)
    X.uni(cut, X.dbox(-89.475, -80.525, 11.4, 14.0, -85.725, -78.275))
    X.dif(b, cut)
    X.swap('HOUSING_F_plate', b, '_v64')             # -7.7687 -> 68247.71; 1 lump; black appearance kept


YNEW = -70.6                                          # D153: the flat underside ends where the rim's blend starts: at x +-30 the recess stops at y -70.68


def change_feet_keepouts(_context):                   # D153 and F50
    k = sys.modules['cp1k']; X = k.K()
    b = X.cp(X.body('FLOOR_PLATE'))
    fill = X.cyl((30.0, -69.0, 0.0), (30.0, -69.0, 0.5), 6.52); X.uni(fill, X.cyl((-30.0, -69.0, 0.0), (-30.0, -69.0, 0.5), 6.52))
    X.uni(b, fill)                                    # +132.7323
    cut = X.cyl((30.0, YNEW, -0.1), (30.0, YNEW, 0.5), 6.5); X.uni(cut, X.cyl((-30.0, YNEW, -0.1), (-30.0, YNEW, 0.5), 6.5))
    X.dif(b, cut)                                     # -132.9926 by whole-body volume; volume-neutral on a crop (lesson 198)
    X.swap('FLOOR_PLATE', b, '_v64')
    for n in ('FOOT_RL', 'FOOT_RR'):
        t = X.cp(X.body(n)); X.move(t, 0.0, YNEW + 69.0, 0.0)
        X.swap(n, t, '_v64')
    for n in ('KO_K5_UL', 'KO_K5_LL', 'KO_K5_UR', 'KO_K5_LR'):
        t = X.cp(X.body(n)); X.move_n(t, 1.0)        # 1.0 toward the viewer along the screen's normal: start d 16.8 -> 15.8
        X.swap(n, t, '_v64')
    # state: 408 bodies (397 + 11 hidden _v64), 96 in the unit, 37 visible, no AUD_*


def save_g20(_context):
    doc = adsk.core.Application.get().activeDocument
    doc.save("rev F WIP 2026-11-15 g20: change pass after the split's audit (F44, F45, F46, F50, rear feet) — not for print")   # -> version 65


def export_g20(_context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    path = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g20.f3d')
    em = des.exportManager
    print(em.execute(em.createFusionArchiveExportOptions(path)), os.path.getsize(path))    # True 187535895
