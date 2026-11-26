# Block 9: the screw bodies of the model and today's two radar screws' shape (the lumps of SCREWS_M2x6_env beside the radar).
# READ-ONLY. Run: runpy.run_path(D + 'p77_b9_probe.py')['main']()  -> p77_b9_probe.txt
import runpy
D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(60)
    print(L['stamp'](), 'before', X.state())
    for b in X.root.bRepBodies:
        if 'SCREW' in b.name.upper() and not k.BACK.search(b.name):
            print('%-28s vis %-5s vol %9.3f lumps %d box %s' % (b.name, b.isLightBulbOn, b.volume * 1000, b.lumps.count, [round(v, 1) for v in k.wbb(X, b)]))
    S = X.body('SCREWS_M2x6_env')
    for i, lb in enumerate(S.lumps):
        if i not in (2, 3):
            continue
        print('lump %d: %.3f mm3' % (i, lb.volume * 1000))
        for sh in lb.shells:
            for f in sh.faces:
                g = f.geometry
                if f.geometry.surfaceType == k.CYL:
                    ok, o, ax, r = g.getData()
                    print('   cyl r %.3f axis %s origin %s area %.2f' % (r * 10, k.r2(k.wv(ax), 4), k.r2(k.W(o)), f.area * 100))
                elif f.geometry.surfaceType == k.PLN:
                    ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
                    print('   plane n %s at %s area %.2f' % (k.r2(k.wv(nv), 4), k.r2(k.W(f.pointOnFace)), f.area * 100))
                else:
                    print('   other type %s area %.2f at %s' % (f.geometry.surfaceType, f.area * 100, k.r2(k.W(f.pointOnFace))))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p77_b9_probe.txt', _main)
