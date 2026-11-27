# Block 2: where the render-only bodies are (RENDER_*), and the frame of the unit's component. READ-ONLY.
# Run: runpy.run_path(D + 'p21_probe.py')['main']()
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def main():
    def body():
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)
        root = des.rootComponent
        print(L['stamp'](), des.parentDocument.name, 'version', des.parentDocument.dataFile.versionNumber,
              'modified', des.parentDocument.isModified)
        for c in des.allComponents:
            names = [b.name for b in c.bRepBodies]
            ren = [n for n in names if n.upper().startswith('RENDER') or 'FABRIC' in n.upper() or n.startswith('REF_')]
            occs = root.allOccurrencesByComponent(c) if c != root else None
            print('component', c.name, 'bodies', len(names), 'occurrences', (occs.count if occs else 'root'))
            if occs:
                for i in range(occs.count):
                    m = occs.item(i).transform2.asArray()
                    print('   occ', occs.item(i).fullPathName, ['%.4f' % v for v in m])
            for n in ren:
                b = c.bRepBodies.itemByName(n)
                bb = b.boundingBox
                print('   ', n, 'visible', b.isLightBulbOn, 'faces', b.faces.count,
                      'box cm', ['%.2f' % v for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                                      bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)])
            if 'HOUSING_F_door' in names:
                print('    (HOUSING_F_door is in this component)')
    L['out']('p21_probe.txt', body)
