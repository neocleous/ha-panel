# rev F m3c (2026-11-13): ribbon pass, block 3 - the connector calls as run, in order, with their results. All read-only; the model stays at
# version 62 (391 bodies, 36 visible, unmodified). Each function is the body of one call's run().
#   k = sys.modules['v5f_k'], m = sys.modules['v5f_m']; k4 = the namespace of v5f_k4a_unit_checks.py (sha256 12006d28...b0baf), k4b = of
#   v5f_k4b_addenda.py (8607cb4d...b600) with k4 in its globals, s3 = of v5f_m3b_unit_checks.py (240be32c...41fe) with k4 and k4b,
#   s3a = of v5f_m3a_usbc_reach.py (51539632...cc40e). Every call sets k.budget(40 to 45) first.
import adsk.core, adsk.fusion, sys, time


def setup(X, k, s3):
    print(s3['setup'](X))
    # the parts that ride with the display module: ribbon 576.1 mm3 (connector to crease 3 and 12 of the drop), cable 287.8 mm3 (run toward the
    # door, fold, 12 of the drop); the cable on the plate unit (roll, row, bottom fold, run to the plug) 1700.3 mm3. k.ST['USBA'] = ['USBA_plug_env'].
    # The fix pass's results for version 60 are still in this Fusion session under the tag 'v60' (k.c[('k4m', 'v60')]).


def ride(X, k, s3):
    print(s3['ride'](X))
    # 1035 results (45 moving pieces x 23 positions out to 60), nothing left, none not zero.


def ride_margins(X, k, m, k4):                       # nearest distance to the shell over the 23 positions
    shell = k4['pieces'](X, 62, 'HOUSING_F_front')
    for lab, p in (('plug', k.tcopy(X, 'RESP_usbc_plug_env')), ('cable part', k4['leadpart'](X, 62, 'LEAD_USB_RESP')),
                   ('ribbon part', k4['leadpart'](X, 62, 'LEAD_DSI'))):
        best = None
        for s in k4['STEPS']:
            t = X.move_n(X.tbm.copy(p), s); qt = m.bb6(t)
            for c in shell:
                if m.bgap(qt, m.bb6(c)) <= 6.0:
                    g = X.mm.measureMinimumDistance(t, c).value * 10.0
                    best = (s, round(g, 2)) if best is None or g < best[1] else best
        print(lab, best)
    # plug 7.36 (14 to 20 out; 11.27 at 0.5); cable part 1.22 at 0.5 out (0.81 home), 9.9 or more from 12 out; ribbon part 4.65 (home to 20 out).


def slide_way(X, k, s3):
    print(s3['slide'](X))                            # 34 results (left box and driver, 17 positions over 50), none not zero
    print(s3['way'](X))                              # called three times until nothing was left
    # way in: 840 results, one not zero: driver screw heads 0.011 mm3 in the shell at 1.05 behind and 7 up (the fix pass's known graze; the way in
    #   is 1.2 to 1.5 behind). The cable on the unit: 0 at every position.
    # way out (service): 672 results, none not zero. The cable on the unit on its way out: 32 positions, 0 against shell, display module, cap,
    #   touch board, radar, BME680 parts and the ribbon; it meets only the left speaker lead as drawn in place (0.03 to 24.7 mm3 at 7 to 20 down),
    #   which leaves with the plate unit.


def reach(X, k, s3):
    print(s3['reach5'](X))
    # Rounded fingertip 16 across, every plug in. Free directions against the bodies (leads left out), then what the leads of this pass add:
    #   Pi 2 x 3 housing   4 of 5 (back45, back60, back45 to-x25, back45 to+x25). The ribbon (19 mm3) and the left speaker lead (23) lie in
    #                      'back45 to+x25' only, with the Pi power cable's lap (834).
    #   ribbon's latch     0 of 5 (cooler, Pi power adapter, cradle, inlet board): tweezers, as before.
    #   speaker left       2 of 6 (up25, to-x25). In 'up25' the fingertip passes through the ribbon's drop (124 mm3) and the USB cable's drop (113);
    #                      in 'to-x25' through the ribbon's drop (73) and the Pi power cable's lap (399). No direction is free of leads.
    #   touch              6 of 6; its own lead only (ribbon 13 mm3 in 'down45').
    #   Pi power           3 of 6 (straight, up25, to-x25); its own cable only in those.


def matrix(X, k, s3):
    print(s3['matrix'](X))                           # 95 bodies, 4465 pairs, nothing left, 76 not zero
    sym = lambda d: {tuple(sorted(q)): v for q, v in d.items() if v}
    a = sym(k.c[('k4m', 'v60')]); b = sym(k.c[('k4m', 62)])
    print(sorted(q for q in a if q not in b), sorted(q for q in b if q not in a), sorted(q for q in a if q in b and abs(a[q] - b[q]) > 0.05))
    # version 60: 76 of 4560 pairs; version 62: 76 of 4465.
    # gone:    lower-left key path - ribbon 54.722; display's component blanket - ribbon 0.964; USB lead - USBA_cable_env 2.569;
    #          left driver - USBA_plug_env 20.801
    # new:     ribbon - Pi 13.892 (its end in the connector); USB cable - RESP_usbc_plug_env 0.151 and - USBA_plug_env 0.151 (its ends in the
    #          sleeves); ReSpeaker's top envelope - RESP_usbc_plug_env 122.760 (the plug's shell in its socket)
    # changed: display's DSI connector - ribbon 0.817 -> 19.328; ribbon - cooler's envelope 35.162 -> 23.974
    print(s3['leads'](X))
    # ribbon: Pi power cable 2.26, left speaker lead 2.58, fan's keep-out 2.84, lower-left key path 3.13, USB cable 5.12
    # USB cable: left speaker lead 0.66, upper-left key path 0.95, lower-left key path 1.29, ribbon 5.12
    # left speaker lead: USB cable 0.66, ribbon 2.58, lower-left key path 4.13. No lead of this pass lies in a key path.


def pliers_unit_down(X, k, s3a):                     # the jaws of v5f_m3a_usbc_reach.py from 45 degrees below, plate unit 1.3 back and 20 / 30 / 40 down
    PL = s3a['PL']; hn0, un0 = PL['hn'], PL['un']
    unit = ['SPKBOX_L', 'SPK_L', 'DRV_screw_heads_env', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'USBA_plug_env', 'TOUCH_CLIP_L']
    try:
        PL['hn'] = 3.7; PL['un'] = 47.10
        for down in (20.0, 30.0, 40.0):
            obs = [(n, [X.move(X.tbm.copy(k.tcopy(X, n)), 0.0, -1.3, -down)]) for n in unit]
            print(down, [s3a['jaws'](X, obs, th=th, wd=wd, shift=sh, w0=0.3)['down45'] for th, wd in ((2.5, 3.0), (1.5, 2.0)) for sh in (0.0, 3.6, 7.2)])
    finally:
        PL['hn'] = hn0; PL['un'] = un0
    # free at 20, 30 and 40 down, pliers and tweezers, plug seated, 3.6 and 7.2 out.


def run(_context):
    pass
