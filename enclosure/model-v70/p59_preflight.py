# Rest of the pass (brief claude/brief-enclosure-audit-fixes-rest-2026-11-25.md), preflight point 3, for the record of the shell's
# way down (D429). READ-ONLY: temporary bodies only (needles), nothing added to the model.
#   tongues: the base plate's tongue faces to the chin lips' rear faces, at home (z 2.9..4.1, x at the lips +-23.5..36.5)
#   heads:   the four outer driver screw heads (DRV_screw_heads_env, axes along y at x +-88.25, z 10.25 / 45.75) to their
#            pockets' floors in the shell, along each head's axis and 1.0 / 2.0 off it
#   noses:   the base plate's noses over the lips: nose front (largest y of the plate above the lip's top, z 4.3..5.0) less the
#            lip's rear face at the same x
# Needles 0.02 wide; each stretch is [from, to] in mm along the needle. Run: runpy.run_path(D + 'p59_preflight.py')['main']()
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def crop(X, name, box):
    t = X.wbox(*box); X.sec(t, X.tbm.copy(X.body(name))); return t


def ny(k, X, c, x, z, y0=-3.0, y1=8.0):
    return [(round(y0 + a, 2), round(y0 + b, 2)) for a, b in k.needle_t(X, [c], (x, y0, z), (x, y1, z), 0.02)]


def _main():
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    sh = crop(X, 'HOUSING_F_front', (-40, 40, -3, 8, 2, 6)); pl = crop(X, 'FLOOR_PLATE', (-40, 40, -3, 8, 2, 6))
    print('-- tongues to the lips, at home: shell (lip) and base plate along y; gap = lip rear face - plate front')
    gaps = []; ov = []
    for x in (-35.0, -30.0, -25.0, 25.0, 30.0, 35.0):
        for z in (2.9, 3.3, 3.7, 4.1):
            s = ny(k, X, sh, x, z); p = ny(k, X, pl, x, z)
            lip = [a for a, b in s if a > 0.5]; pf = [b for a, b in p if b < 3.0]
            g = round(min(lip) - max(pf), 3) if lip and pf else None
            if g is not None:
                gaps.append(g)
            print('   x %+5.1f z %.1f  shell %s  plate %s  gap %s' % (x, z, s, p, g))
        lip_r = [a for a, b in ny(k, X, sh, x, 4.0) if a > 0.5]
        for z in (4.3, 4.4, 4.6, 4.8, 5.0):
            p = ny(k, X, pl, x, z)
            if p and lip_r:
                o = round(max(b for a, b in p) - min(lip_r), 3); ov.append(o)
                print('   nose x %+5.1f z %.1f  plate %s  over the lip (rear face %.2f) by %s' % (x, z, p, min(lip_r), o))
    print('TONGUES: gap min %s max %s' % (min(gaps) if gaps else None, max(gaps) if gaps else None))
    print('NOSES: overlap min %s max %s' % (min(ov) if ov else None, max(ov) if ov else None))
    print('-- the outer driver screw heads to their pockets in the shell, along y')
    hd = []
    for sx in (1, -1):
        x0 = sx * 88.25
        for zc in (10.25, 45.75):
            hc = crop(X, 'DRV_screw_heads_env', (x0 - 4, x0 + 4, -3, 4, zc - 4, zc + 4))
            sc = crop(X, 'HOUSING_F_front', (x0 - 4, x0 + 4, -3, 8, zc - 4, zc + 4))
            for dx, dz in ((0, 0), (1.0, 0), (-1.0, 0), (0, 1.0), (0, -1.0), (2.0, 0), (0, 2.0)):
                h = ny(k, X, hc, x0 + dx, zc + dz); s = ny(k, X, sc, x0 + dx, zc + dz)
                hf = max(b for a, b in h) if h else None; sf = [a for a, b in s if hf is not None and a > hf - 0.01]
                g = round(min(sf) - hf, 3) if hf is not None and sf else None
                if g is not None and dx == 0 and dz == 0:
                    hd.append(g)
                print('   head x %+.2f z %.2f (off %+.1f, %+.1f)  head %s  shell %s  gap %s' % (x0, zc, dx, dz, h, s, g))
    print('HEADS on axis: %s' % hd)
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p59_preflight.txt', _main)
