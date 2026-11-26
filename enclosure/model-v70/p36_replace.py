# Block 3: puts p33-p35's bodies into the model. CHANGES THE DOCUMENT:
#   GROMMET_usbc_F, HOUSING_F_door, FLOOR_PLATE replaced by k.c['b3_grommet'], ['b3_door'], ['b3_plate'] (same name, appearance,
#   material and visibility; the old body deleted: its hidden copy <name>_v69 was made in block 0, p03_backups);
#   SCREWS_M2x6_env: the grommet's two screws moved to the new seats (x +-9.0, through (+-9.0, -79.3, 10.0), leaning 18 deg,
#   handle away from the wall), seated in the countersink; the other five unchanged (its copy SCREWS_M2x6_env_v69 exists).
# Then the volumes of the new bodies at very high accuracy, and of their _v69 copies.
# Run: runpy.run_path(D + 'p36_replace.py')['main']()  -> p36_replace.txt;  ['main']('door'): the door alone again
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]
# the screw envelope as the library's (SCREWS_M2x6_env): head top, cylinder r 1.9 x 0.3, 90 deg cone to r 1.0, shank r 1.0;
# 6.0 from the head's top to the tip. Seated: the head's cone 0.1 inside the countersink's (r 1.1 at t 0.93, 90 deg):
T_CONE0, T_HEAD0, T_TOP = 0.83, 1.73, 2.03     # along the axis from the bed (z 10.0): cone's small end, cone's large end, top
T_TIP = T_TOP - 6.0


def at(P, t):
    return (P[0] + U[0] * t, P[1] + U[1] * t, P[2] + U[2] * t)


def vhi(b):
    return b.getPhysicalProperties(adsk.fusion.CalculationAccuracy.VeryHighCalculationAccuracy).volume * 1000.0


def replace(X, name, tb):
    old = X.body(name)
    if X.body(name + '_v69') is None:
        raise RuntimeError('no copy ' + name + '_v69')
    vis = old.isLightBulbOn
    nb = X.add(tb, name + '_new', like=old, show=vis)
    old.deleteMe()
    nb.name = name
    return nb


def _main(only=None):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    if only == 'door':       # the door again, after p34 stage 2 was run again (the pockets' teardrops, from the floor)
        nb = replace(X, 'HOUSING_F_door', X.tbm.copy(k.c['b3_door']))
        print('%-18s v69 copy %11.3f  new %11.3f  lumps %d faces %d' % ('HOUSING_F_door', vhi(X.body('HOUSING_F_door_v69')), vhi(nb),
                                                                     nb.lumps.count, nb.faces.count))
        k.purge(('HOUSING_F_door',))
        print(L['stamp'](), 'after', X.state())
        return
    for key in ('b3_grommet', 'b3_door', 'b3_plate'):
        if k.c.get(key) is None:
            raise RuntimeError('missing ' + key)
    # the screws' body
    s = X.tbm.copy(X.body('SCREWS_M2x6_env'))
    n0 = s.lumps.count
    for sx in (1, -1):
        X.dif(s, X.wbox(sx * 4.5, sx * 10.5, -83.5, -78.0, 6.5, 15.0))
    n1 = s.lumps.count
    for P in SCREWS:
        X.uni(s, X.cyl(at(P, T_HEAD0), at(P, T_TOP), 1.9))
        X.uni(s, X.cyl(at(P, T_CONE0), at(P, T_HEAD0), 1.0, 1.9))
        X.uni(s, X.cyl(at(P, T_TIP), at(P, T_CONE0), 1.0))
    print('screws: lumps %d -> %d without the grommet pair -> %d; volume %.3f' % (n0, n1, s.lumps.count, X.vol(s)))
    out = {}
    for name, tb in (('GROMMET_usbc_F', X.tbm.copy(k.c['b3_grommet'])), ('HOUSING_F_door', X.tbm.copy(k.c['b3_door'])),
                     ('FLOOR_PLATE', X.tbm.copy(k.c['b3_plate'])), ('SCREWS_M2x6_env', s)):
        nb = replace(X, name, tb)
        out[name] = (vhi(X.body(name + '_v69')), vhi(nb), nb.lumps.count, nb.faces.count)
    for name, (a, b, nl, nf) in out.items():
        print('%-18s v69 copy %11.3f  new %11.3f  (%+9.3f)  lumps %d faces %d' % (name, a, b, b - a, nl, nf))
    # the library's cached copies of these bodies are keyed by name and volume: drop them
    k.purge(('GROMMET_usbc_F', 'HOUSING_F_door', 'FLOOR_PLATE', 'SCREWS_M2x6_env'))
    print(L['stamp'](), 'after', X.state())


def main(only=None):
    L['out']('p36_replace%s.txt' % ('' if only is None else '_' + only), _main, only)
