# Block 3: does the temporary-body face delete heal a solid (like the Delete Face command), on copies only? READ-ONLY
# for the document: everything happens on temporary copies.
# Run: runpy.run_path(D + 'p31_try_delete.py')['main']()  -> p31_try_delete.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _faces_in(k, tb, box, kinds=None):
    out = []
    for f in tb.faces:
        c = k.W(f.pointOnFace)
        if box[0] <= c[0] <= box[1] and box[2] <= c[1] <= box[3] and box[4] <= c[2] <= box[5]:
            out.append(f)
    return out


def _try(k, X, name, box, label):
    t = X.tbm.copy(X.body(name))
    v0 = X.vol(t); n0 = t.faces.count
    fs = _faces_in(k, t, box)
    ok = None
    try:
        ok = X.tbm.deleteFaces(fs, True)
    except Exception as e:
        ok = 'error: %s' % e
    v1 = X.vol(t)
    print('%-28s faces picked %2d  ok %s  solid %s  lumps %d  faces %d -> %d  volume %.3f -> %.3f (%+.3f)' % (
        label, len(fs), ok, t.isSolid, t.lumps.count, n0, t.faces.count, v0, v1, v1 - v0))
    return t


def _main():
    k = L['load'](); X = k.K()
    # the door's two peg holes (cylinders r 0.85 at (+-13.85, 20.6)), one at a time
    _try(k, X, 'HOUSING_F_door', [13.0, 14.7, -83.8, -81.0, 19.7, 21.5], 'door: peg hole +x')
    # the door's +x lug seat with its pilot: the block's faces between x 4.5 and 10.5, y -82.6..-77.9, z 4.4..12.3
    _try(k, X, 'HOUSING_F_door', [4.49, 10.51, -82.6, -77.9, 4.4, 12.35], 'door: lug seat +x')
    # the grommet's two pegs
    _try(k, X, 'GROMMET_usbc_F', [13.0, 14.7, -84.3, -79.4, 19.7, 21.5], 'grommet: peg +x')


def main():
    L['out']('p31_try_delete.txt', _main)
