# rev F rework block R1b-1 (2026-11-04): inner skins of INNER_E for the rear-door lap joint (kept hidden as tools).
# TOOL_inner_skin_1p2 = INNER_E copy hollowed by shellFeatures with insideThickness 1.2 -> the front shell's lip band;
# TOOL_inner_skin_1p4 = same with 1.4 -> the door's rebate (0.2 clearance over the lip). Expected volume ≈ area x t.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    try:
        for t, nm in ((1.2, 'TOOL_inner_skin_1p2'), (1.4, 'TOOL_inner_skin_1p4')):
            if X.body(nm) is not None:
                out[nm] = 'exists'; continue
            t0 = time.time()
            b = X.add(X.tbm.copy(X.body('INNER_E')), nm)
            coll = adsk.core.ObjectCollection.create(); coll.add(b)
            si = X.feats.shellFeatures.createInput(coll, False)
            si.insideThickness = VI(t / 10)
            X.feats.shellFeatures.add(si)
            b = X.body(nm); b.isLightBulbOn = False
            out[nm] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 's': round(time.time() - t0, 1)}
            log('v5f_r1b1_inner_skins', nm, out[nm])
        sk = X.body('TOOL_inner_skin_1p2')
        out['probe_1p2'] = {'wall_+0.6_in': X.inside(sk, XC, -81.18 + 0.6, 40.0) if sk else None,
                            'void_+1.5_in': (not X.inside(sk, XC, -81.18 + 1.5, 40.0)) if sk else None}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1b1_inner_skins', 'done', out)
    print(json.dumps(out))
