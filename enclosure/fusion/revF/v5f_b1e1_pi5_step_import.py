# rev F block 1e-1 (2026-11-03): import Daniel's Raspberry Pi 5 STEP into a separate, unsaved document for v5f_b1e_pi5.py.
# Re-written for the repo after the run (same import call; the run itself was not logged). Run it, then v5f_b1e_pi5.py,
# which copies every solid into the panel document at the K10 pose and closes this document without saving.
# importToNewDocument() leaves the NEW document active -> v5f_b1e_pi5.py re-activates 'HA Panel v5 - tapered' first.
# STEP frame (probed in v5f_b1e_pi5.py): X = long edge (centre origin), Y = board normal (PCB Y 0.1..1.5), Z = short edge,
# GPIO header at Z -28.
import adsk.core, adsk.fusion, json, os, time

STEP = os.path.expanduser('~/Documents/Maker/HA Panel/Datasheets/RaspberryPi5.step')


def run(_context):
    app = adsk.core.Application.get()
    t0 = time.time()
    opts = app.importManager.createSTEPImportOptions(STEP)
    doc = app.importManager.importToNewDocument(opts)
    des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    n = sum(o.bRepBodies.count for o in des.rootComponent.allOccurrences) + des.rootComponent.bRepBodies.count
    print(json.dumps({'doc': doc.name, 'bodies': n, 's': round(time.time() - t0, 1)}))
