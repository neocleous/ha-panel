# rev F block 3d (2026-11-04): wall ≥ 2.5 at the top (z > 165).
#   B3c left 1.77 mm at the inner top-front corners (x_rel ±74.5, y −22.2, z 176.7: the top's front line meets the side
#   curve next to the slot, three R3 rounds meet on the outside). Generic fix and check:
#   1. TOOL_outer_skin_2p5_F = copy of REF_F_outer hollowed by shellFeatures insideThickness 2.5 (the 2.5 layer inside the
#      outer surface), hidden.
#   2. Deficit = (skin ∩ region) − HOUSING_F_front, region x_rel ±120, y −55.3…30, z 165…190 (front shell only; no
#      openings are planned in the skin there before block 3's ports, which are cut afterwards).
#   3. JOIN deficit ∪ (HOUSING_F_front ∩ the same region) [overlap] into HOUSING_F_front; deficit again (should be 0).
#   4. INNER_F vs INNER_E (B3c's R1 copy grew by 89.8 mm³ instead of shrinking): lumps, for the record.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 240.258, 'REF_F_outer': 1974.145, 'HOUSING_F_door': 55.484}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm; feats = X.feats

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        return [round(min(c.x * 10 - XC for c in cs), 1), round(max(c.x * 10 - XC for c in cs), 1), round(min(wy(c) for c in cs), 1),
                round(max(wy(c) for c in cs), 1), round(min(wz(c) for c in cs), 1), round(max(wz(c) for c in cs), 1)]

    def lumps(t, n=8):
        return sorted([[round(t.lumps.item(i).volume * 1000, 2)] + bbw(t.lumps.item(i).boundingBox) for i in range(t.lumps.count)], key=lambda r: -r[0])[:n]
    try:
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        for a, c, k in (('INNER_F', 'INNER_E', 'F_minus_E'), ('INNER_E', 'INNER_F', 'E_minus_F')):
            t = tbm.copy(X.body(a)); tbm.booleanOperation(t, tbm.copy(X.body(c)), B.DifferenceBooleanType)
            out['inner_' + k] = {'mm3': round(t.volume * 1000, 2), 'lumps': lumps(t, 6)}
        nm = 'TOOL_outer_skin_2p5_F'
        if X.body(nm) is None:
            sk = X.add(tbm.copy(X.body('REF_F_outer')), nm)
            coll = adsk.core.ObjectCollection.create(); coll.add(sk)
            si = feats.shellFeatures.createInput(coll, False); si.insideThickness = VI(0.25)
            feats.shellFeatures.add(si)
        skb = X.body(nm); skb.isLightBulbOn = False
        out['skin_cm3'] = round(skb.volume, 3)
        reg = X.wbox(XC - 120, XC + 120, -55.3, 30, 165, 190)
        sr = tbm.copy(skb); tbm.booleanOperation(sr, reg, B.IntersectionBooleanType)
        fb = X.body('HOUSING_F_front')
        d = tbm.copy(sr); tbm.booleanOperation(d, tbm.copy(fb), B.DifferenceBooleanType)
        out['deficit_before'] = {'mm3': round(d.volume * 1000, 2), 'lumps': lumps(d)}
        log('v5f_b3d_top_wall_fill', 'deficit', out)
        if d.volume * 1000 > 0.01:
            ov = tbm.copy(fb); tbm.booleanOperation(ov, X.wbox(XC - 120, XC + 120, -55.3, 30, 165, 190), B.IntersectionBooleanType)
            tool = X.union(d, ov)
            v0 = fb.volume
            X.combine(fb, [X.add(tool, 'B3D_fill_tmp')])
            fb = X.body('HOUSING_F_front')
            out['front_cm3'] = [round(v0, 3), round(fb.volume, 3)]; out['added_mm3'] = round((fb.volume - v0) * 1000, 2); out['front_lumps'] = fb.lumps.count
            d2 = tbm.copy(sr); tbm.booleanOperation(d2, tbm.copy(fb), B.DifferenceBooleanType)
            out['deficit_after'] = {'mm3': round(d2.volume * 1000, 3), 'lumps': lumps(d2, 4)}
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B3D_'))]
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in ['SLAB_frame', 'LCD_glass', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR']
                  + [n for n in names if n.startswith('LCD_') and n != 'LCD_glass']]
        r = X.interference(fb, others)
        out['interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d bodies)' % len(r)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3d_top_wall_fill', 'fill', out)
    print(json.dumps(out))
