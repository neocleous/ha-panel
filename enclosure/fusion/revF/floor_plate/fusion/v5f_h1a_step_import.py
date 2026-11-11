# rev F h1a (2026-11-11): step 3, block 1 - the rev 3 STEP files into temporary bodies (no change to the panel document).
#   Imports main-board-rev3.step and main-board-rev3-plug-envelopes.step (repo docs 03ad1f9, copied to fp/step3/, sha256 checked)
#   into new documents, copies every solid, closes the documents without saving and re-activates the panel document. The copies are
#   kept in the cache of v5f_h_lib.py (they live until Fusion is closed) with their boxes in the STEP frame (mm) for h1b.
#   STEP frame: X = u, Y = v, Z = 0 at the board's back face, door-side face at Z 1.6.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
FILES = {'board': 'main-board-rev3.step', 'plugs': 'main-board-rev3-plug-envelopes.step'}


def run(_context):
    st = {}
    t0 = time.time()
    app = adsk.core.Application.get()
    tbm = adsk.fusion.TemporaryBRepManager.get()
    c = cache()
    for key, fn in FILES.items():
        opts = app.importManager.createSTEPImportOptions(os.path.join(S3, fn))
        doc = app.importManager.importToNewDocument(opts)
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        srcs = [(root.name, b) for b in root.bRepBodies]
        for o in root.allOccurrences:
            for b in o.bRepBodies:
                srcs.append((o.fullPathName, b))
        items = []
        for path, b in srcs:
            tb = tbm.copy(b)
            bb = tb.boundingBox
            box = [round(q * 10, 3) for q in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)]
            items.append([path + '/' + b.name, box, tb])
        c['step_' + key] = items
        st[key] = {'solids': len(items), 'overall': [min(i[1][0] for i in items), max(i[1][1] for i in items), min(i[1][2] for i in items),
                                                     max(i[1][3] for i in items), min(i[1][4] for i in items), max(i[1][5] for i in items)],
                   'occurrences': root.allOccurrences.count, 't': round(time.time() - t0, 1),
                   'rows': [[i[0][-40:], i[1]] for i in items]}
        doc.close(False)
    panel = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
    if app.activeDocument != panel:
        panel.activate()
    st['active'] = app.activeDocument.name
    st['docs'] = [d.name for d in app.documents]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1a', st)


run(None)
