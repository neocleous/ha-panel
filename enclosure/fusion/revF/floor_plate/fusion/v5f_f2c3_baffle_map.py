# rev F f2c3 (2026-11-10): read-only - where the front shell's rear surface is behind the +x speaker (first shell face met going
# toward the viewer from y -3.6), on a grid. Decides whether a driver already screwed to its box can rise into place from below.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
XS = [44.0, 46.6, 47.2, 47.8, 50.0, 55.0, 62.0, 70.5, 80.0, 90.0, 93.2, 93.8, 94.6, 95.6]
ZS = [3.0, 3.6, 4.4, 4.9, 5.2, 6.5, 8.0, 12.0, 28.0, 45.0, 50.7, 51.3, 52.5, 55.0, 60.0, 68.0, 75.0, 78.0, 82.0, 86.0]


def run(_context):
    st = {'x': XS}
    try:
        X = K()
        F = X.body('HOUSING_F_front')
        PC = adsk.fusion.PointContainment
        for z in ZS:
            row = []
            for x in XS:
                p = Wp(x, -3.6, z)
                if F.pointContainment(p) != PC.PointOutsidePointContainment:
                    row.append('in'); continue
                hp = adsk.core.ObjectCollection.create()
                ents = X.root.findBRepUsingRay(p, V3(0, C, -S), adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
                ys = [W(hp.item(i))[1] for i in range(ents.count) if ents.item(i).body.name == 'HOUSING_F_front']
                row.append(round(min(ys), 2) if ys else None)
            st['z%g' % z] = row
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    status('f2c3', st)


run(None)
