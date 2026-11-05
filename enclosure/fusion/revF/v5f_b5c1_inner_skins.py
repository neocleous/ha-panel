# rev F block 5c-1 (2026-11-05): inner skin tools for the fabric block (hidden, no part changed).
#   INNER_E copies hollowed with shellFeatures (insideThickness) -> layers inside the cavity along the inner surface (lesson 16):
#   TOOL_inner_skin_0p7   D1 inner layer (s -0.7...0, s = normal distance from INNER_E's surface, + into the wall)
#   TOOL_inner_skin_0p9   lip inner bound (0.2 clearance under the door's new inner surface)
#   TOOL_inner_skin_2p1   lip outer bound / root band (lip 1.2 thick, s -0.9...-2.1)
#   TOOL_inner_skin_2p5   removal tool for the R1 lip, root band and pads (all within s 0...-2.3)
#   TOOL_inner_cup_2p1    same 2.1 shell with INNER_E's top cap removed -> wall band only, for the top-groove rail
#   (TOOL_inner_skin_0p2 / _1p2 / _1p4 from R1 stay as they are.)
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SKINS = ((0.7, 'TOOL_inner_skin_0p7'), (0.9, 'TOOL_inner_skin_0p9'), (2.1, 'TOOL_inner_skin_2p1'), (2.5, 'TOOL_inner_skin_2p5'))


def run(_context):
    X = Ctx(); out = {}
    try:
        ie = X.body('INNER_E')
        out['INNER_E_cm3'] = round(ie.volume, 3)
        for t, nm in SKINS + ((2.1, 'TOOL_inner_cup_2p1'),):
            if X.body(nm) is not None:
                out[nm] = 'exists'; continue
            t0 = time.time()
            b = X.add(X.tbm.copy(ie), nm)
            coll = adsk.core.ObjectCollection.create()
            if nm.startswith('TOOL_inner_cup'):
                top = None
                for f in b.faces:
                    if not f.geometry.objectType.endswith('Plane'):
                        continue
                    ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
                    if n.y * S + n.z * C > 0.99 and (top is None or wz(f.pointOnFace) > wz(top.pointOnFace)):
                        top = f
                if top is None:
                    raise RuntimeError('INNER_E top cap not found')
                out['cup_top_face'] = {'z': round(wz(top.pointOnFace), 2), 'area_mm2': round(top.area * 100, 0)}
                coll.add(top)
            else:
                coll.add(b)
            si = X.feats.shellFeatures.createInput(coll, False)
            si.insideThickness = VI(t / 10)
            X.feats.shellFeatures.add(si)
            b = X.body(nm); b.isLightBulbOn = False
            out[nm] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 's': round(time.time() - t0, 1)}
            log('v5f_b5c1_inner_skins', nm, out[nm])
        # probes on the 0.7 skin at the chin (inner face y 5.0 at z 25, x_rel 0) and the back (door zone, z 40)
        sk = X.body('TOOL_inner_skin_0p7')
        out['probe_0p7'] = {'chin_y4.65_in': X.inside(sk, XC, 4.65, 25.0), 'chin_y4.2_out': not X.inside(sk, XC, 4.2, 25.0),
                            'chin_y5.2_out': not X.inside(sk, XC, 5.2, 25.0)}
        cup = X.body('TOOL_inner_cup_2p1')
        out['probe_cup'] = {'top_layer_absent_x0_z176.5': not X.inside(cup, XC, -35.0, 176.5)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5c1_inner_skins', 'done', out)
    print(json.dumps(out))
