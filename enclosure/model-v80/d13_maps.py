# Block 1: maps and face lists. READ-ONLY.
#   map(y, side)       which body holds each point of a grid in the plane y = const, seen from the front (x across, z up the page)
#   xmap(x, side)      the same in a plane x = const (y across from -34 to +8, z up the page)
#   zmap(z, side)      the same in a plane z = const (x across, y up the page: the front first)
#   faces(name, box)   the flat and round faces of a body whose sample point lies in a world box: normal or axis, place, area, extents
# Run: runpy.run_path(D + 'd13_maps.py')['main'](stage, ...)  -> d13_<tag>.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
IN = (adsk.fusion.PointContainment.PointInsidePointContainment, adsk.fusion.PointContainment.PointOnPointContainment)
MARK = [('SPKBOX_', 'B'), ('SPK_', 'd'), ('DRV_screw_heads_env', 'k'), ('TOUCH_CLIP_', 'c'), ('RADAR_HOLDER', 'h'), ('HOUSING_F_front', 's'), ('HOUSING_F_plate', 'p'),
        ('FLOOR_PLATE', 'f'), ('USBA_plug_env', 'u'), ('TOUCH_PCB', 't'), ('LD2410C_env_F', 'r')]


def bodies(k, X, side, box):
    out = []
    for n, ch in MARK:
        nm = n + side if n.endswith('_') else n
        b = X.body(nm)
        if b is None:
            continue
        out.append((ch, L['crop'](X, nm, box)))
    return out


def at(k, bs, p):
    for ch, t in bs:
        if t.faces.count and t.pointContainment(k.Wp(*p)) in IN:
            return ch
    return '.'


def st_map(k, X, y=-3.75, side='L', x0=39.0, x1=97.0, dx=1.0, z0=3.0, z1=85.0, dz=1.5):
    sx = 1 if side == 'L' else -1
    a, b = sorted((sx * x0, sx * x1))
    bs = bodies(k, X, side, (a - 1, b + 1, y - 0.5, y + 0.5, z0 - 1, z1 + 1))
    nx = int(round((x1 - x0) / dx)) + 1; nz = int(round((z1 - z0) / dz)) + 1
    print('plane y %.2f, side %s; columns x %.1f..%.1f step %.2f (the box\'s inboard side at the left); rows z, top first' % (y, side, sx * x0, sx * x1, dx))
    print('B box, d driver, k screw heads, c clip, h holder, s shell, p screen plate, f base plate, u USB-A plug, t touch board, r radar')
    for j in range(nz - 1, -1, -1):
        z = z0 + j * dz
        print('%5.1f %s' % (z, ''.join(at(k, bs, (sx * (x0 + i * dx), y, z)) for i in range(nx))))


def st_xmap(k, X, x=70.5, side='L', y0=-34.0, y1=8.0, dy=0.5, z0=1.0, z1=60.0, dz=1.0):
    sx = 1 if side == 'L' else -1
    bs = bodies(k, X, side, (sx * x - 0.5, sx * x + 0.5, y0 - 1, y1 + 1, z0 - 1, z1 + 1))
    ny = int(round((y1 - y0) / dy)) + 1; nz = int(round((z1 - z0) / dz)) + 1
    print('plane x %.2f, side %s; columns y %.1f..%.1f step %.2f (the rear at the left); rows z, top first' % (sx * x, side, y0, y1, dy))
    for j in range(nz - 1, -1, -1):
        z = z0 + j * dz
        print('%5.1f %s' % (z, ''.join(at(k, bs, (sx * x, y0 + i * dy, z)) for i in range(ny))))


def st_zmap(k, X, z=38.0, side='L', x0=36.0, x1=60.0, dx=0.5, y0=-14.0, y1=5.0, dy=0.5):
    sx = 1 if side == 'L' else -1
    a, b = sorted((sx * x0, sx * x1))
    bs = bodies(k, X, side, (a - 1, b + 1, y0 - 1, y1 + 1, z - 0.5, z + 0.5))
    nx = int(round((x1 - x0) / dx)) + 1; ny = int(round((y1 - y0) / dy)) + 1
    print('plane z %.2f, side %s; columns x %.1f..%.1f step %.2f (inboard at the left); rows y, the front (toward the screen) first' % (z, side, sx * x0, sx * x1, dx))
    for j in range(ny - 1, -1, -1):
        y = y0 + j * dy
        print('%6.1f %s' % (y, ''.join(at(k, bs, (sx * (x0 + i * dx), y, z)) for i in range(nx))))


def st_faces(k, X, name='SPKBOX_L', box=(44, 60, -53, -19, 3, 25), amin=0.3):
    b = k.c[name[2:]] if name.startswith('c:') else X.body(name)
    rows = k.faces(X, b, box, ('p', 'c'), amin)
    print('%s: faces with their sample point in %s (%d)' % (name, box, len(rows)))
    for r in sorted(rows, key=lambda q: str(q[:3])):
        print('   ', r)


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'map': st_map, 'xmap': st_xmap, 'zmap': st_zmap, 'faces': st_faces}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag=None, **kw):
    L['out']('d13_%s.txt' % (tag or stage), _main, stage, **kw)
# END
