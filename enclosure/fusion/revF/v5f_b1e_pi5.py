# rev F block 1e (2026-11-03): Raspberry Pi 5 from Daniel's RaspberryPi5.step (imported by v5f_b1e-1 into an unsaved doc)
# placed at the K10 pose: GPIO edge front, USB-C/HDMI/DSI edge back, SD at -x, USB/RJ45 at +x, PCB bottom on the door
# lands at z 8.0. STEP frame: X long edge (centre origin), Y board normal (PCB Y 0.1..1.5 = 1.4 thick), Z short edge with the
# GPIO at Z -28. Board frame (Pi drawing): X_b = X_s + 42.5, Y_b = 28 - Z_s; world = (-45 + X_b, -58 + Y_b, 7.9 + Y_s).
# Bodies: PI5_F (union of all STEP solids that union cleanly; others PI5_F_part_k), PI5_F_cooler (Active Cooler envelope from
# the official drawing: board X 0.7-64.2, Y 7.9-50.4, z 13.6 (above the MIPI tops) -> PCB top + 13.7), KO_K7_fan (hidden: fan footprint z cooler top -> 35.8),
# GPIO_plugA_env / GPIO_plugB_env (2-row Dupont housings, header base top -> header top + 14; E0 envelope).
# --- paste v5f_common.py above this line ---


def run(_context):
    app = adsk.core.Application.get()
    panel = [app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name == 'HA Panel v5 - tapered'][0]
    if app.activeDocument != panel:
        panel.activate()          # the STEP import left its own document active
    X = Ctx()
    pidoc = [app.documents.item(i) for i in range(app.documents.count) if app.documents.item(i).name.startswith('Untitled')][0]
    pdes = adsk.fusion.Design.cast(pidoc.products.itemByProductType('DesignProductType'))
    m = adsk.core.Matrix3D.create()
    tx = -0.25; ty = (-30 * C + (7.9 - H) * S) / 10; tz = (30 * S + (7.9 - H) * C) / 10
    m.setWithArray([1, 0, 0, tx, 0, S, -C, ty, 0, C, S, tz, 0, 0, 0, 1])
    acc = None; extra = []; n = 0
    for o in pdes.rootComponent.allOccurrences:
        for b in o.bRepBodies:
            tb = X.tbm.copy(b); X.tbm.transform(tb, m); n += 1
            if acc is None:
                acc = tb; continue
            ok = X.tbm.booleanOperation(acc, tb, adsk.fusion.BooleanTypes.UnionBooleanType)
            if not ok:
                extra.append((o.name + '/' + b.name, tb))
    out = {'copied': n, 'union_failures': [e[0] for e in extra]}
    pi = X.add(acc, 'PI5_F')
    for k, (nm, tb) in enumerate(extra):
        X.add(tb, 'PI5_F_part_%d' % k)
    pidoc.close(False)
    if app.activeDocument != X.doc:
        X.doc.activate()
    # check the placement: PCB corner probe and hole axes
    out['pcb_probe'] = {'inside_(-44,-57,8.7)': X.inside(pi, -44.0, -57.0, 8.7), 'below_(-44,-57,7.9)_open': not X.inside(pi, -44.0, -57.0, 7.9),
                        'above_(-44,-57,9.5)_open': not X.inside(pi, -44.0, -57.0, 9.5),
                        'holes_open': [not X.inside(pi, x, y, 8.7) for (x, y) in ((-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5))]}
    # envelopes
    zt = 9.4
    cool = X.add(X.wbox(-44.3, 19.2, -50.1, -7.6, 13.6, zt + 13.7), 'PI5_F_cooler')   # above the tallest under-cooler parts (MIPI top z 13.5)
    ko = X.add(X.wbox(-17.6, 12.4, -38.7, -7.6, zt + 13.7, 35.8), 'KO_K7_fan'); ko.isLightBulbOn = False
    pa = X.add(X.wbox(-37.9, -17.6, -8.0, -2.9, zt + 2.5, zt + 8.6 + 14.0), 'GPIO_plugA_env')
    pb = X.add(X.wbox(5.3, 12.9, -8.0, -2.9, zt + 2.5, zt + 8.6 + 14.0), 'GPIO_plugB_env')
    others = [X.body(nm) for nm in ('DOOR_F', 'HOUSING_E', 'SLAB_frame', 'LCD_glass', 'LCD_panel_body', 'LCD_pcb_76x110')]
    out['interf_PI5_F'] = X.interference(pi, others)
    out['interf_cooler'] = X.interference(cool, others + [pi])
    out['interf_plugs'] = {pa.name: X.interference(pa, [pi, cool, X.body('HOUSING_E')]), pb.name: X.interference(pb, [pi, cool, X.body('HOUSING_E'), ko])}
    out['vol_cm3'] = {b.name: round(b.volume, 2) for b in (pi, cool, ko, pa, pb)}
    log('v5f_b1e_pi5', 'PI5 placed', out)
    print(json.dumps(out))
