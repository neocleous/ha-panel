# rev F block 3i (2026-11-04): LD2410C cradle, viewer's-right front corner (−x), board centre z 127.5 (brief z 115–140).
#   B3h: at z 115–140 the slot face (normal +y) meets the side wall (normal 106–118° from +y toward −x) in a sharp inner
#   corner (apex ≈ x_rel −89.6, y −11.8 at z 127.5) – there is no ≈ 40° surface. Run 1 at the brief's 40° failed (the air box
#   still hit the side wall 20 mm back along −n: the wedge between the slot face and the side wall is ≈ 63°, its bisector
#   points 56° / 59° / 61° from +y toward −x at z 115 / 127.5 / 140). Run 2: antenna normal on the bisector, 59°.
#   Board LD2410C_env 16 (along t) × 22 (z) × 3.0 (n, est.) – envelope sheet. Placement: the 2.0 air box in front of the
#   antenna face (16 × 22 × 2.0) touches neither wall (bisection on the distance s from the apex along −n).
#   Cradle: frame ring 2.0 wide around the board (0.15 clearance), from the antenna face back 4.0; stop lips 1.0 thick in front
#   of the face, 0.85 over the board edges (opening 14.3 × 20.3); skirt continuing the lip ring forward until it meets the
#   walls (prism 12 long ∩ cavity, plus the housing's own wall inside the prism so the join overlaps). Board pushed in from
#   inside (along +n) to the lips.
#   Checks: board and core air (14.3 × 20.3 × 2.0) vs housing 0 after the join; cradle vs slab / LCD / lanes 0; a plan fan of
#   rays from the antenna centre (n ± 60°): bodies hit (housing / slab / LCD) – the beam's RF path.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 240.111, 'HOUSING_F_door': 55.484}
ANG = 59.0; Z0 = 127.5; BT, BW, BH = 3.0, 16.0, 22.0; AIR = 2.0
CL, RAIL, LIP_T, LIP_OV, DEPTH, SKIRT = 0.15, 2.0, 1.0, 0.85, 4.0, 12.0
APEX = (-89.6, -11.8)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm; comp = X.comp
    a = math.radians(ANG); n = (-math.sin(a), math.cos(a)); t = (math.cos(a), math.sin(a))
    nd = V3(n[0], n[1] * C, -n[1] * S); td = V3(t[0], t[1] * C, -t[1] * S)

    def ob(f, off_n, ln, lt, lz):
        # box centred at (front-face centre f) + off_n * n, sizes along n / t / z (world mm)
        cx = f[0] + off_n * n[0]; cy = f[1] + off_n * n[1]
        return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(cx, cy, Z0), nd, td, ln / 10, lt / 10, lz / 10))

    def ring(f, n0, n1, wo, ho, wi, hi):
        r = ob(f, (n0 + n1) / 2, n1 - n0, wo, ho); X.diff(r, ob(f, (n0 + n1) / 2, n1 - n0 + 2, wi, hi)); return r

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return q.volume * 1000
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('LD2410C_env_F') is not None:
            raise RuntimeError('LD2410C_env_F exists already')
        fb = X.body('HOUSING_F_front')
        A = (XC + APEX[0], APEX[1])
        F = lambda s: (A[0] - s * n[0], A[1] - s * n[1])
        lo, hi = 0.5, 20.0
        if vol_x(ob(F(hi), AIR / 2, AIR, BW, BH), fb) > 0:
            raise RuntimeError('air box still hits the wall at s %s' % hi)
        for _ in range(10):
            mid = (lo + hi) / 2
            if vol_x(ob(F(mid), AIR / 2, AIR, BW, BH), fb) > 0:
                lo = mid
            else:
                hi = mid
        s = round(hi + 0.1, 2); f = F(s)
        out['placement'] = {'s_from_apex': s, 'antenna_face_centre_x_rel_y_z': [round(f[0] - XC, 2), round(f[1], 2), Z0], 'n': [round(n[0], 3), round(n[1], 3)]}
        env = X.add(ob(f, -BT / 2, BT, BW, BH), 'LD2410C_env_F'); env.isLightBulbOn = False
        wi, hi_ = BW + 2 * CL, BH + 2 * CL; wo, ho = wi + 2 * RAIL, hi_ + 2 * RAIL
        frame = ring(f, -DEPTH, 0.0, wo, ho, wi, hi_)
        lips = ring(f, 0.0, LIP_T, wo, ho, BW - 2 * LIP_OV, BH - 2 * LIP_OV)
        pr = ring(f, LIP_T, LIP_T + SKIRT, wo, ho, BW - 2 * LIP_OV, BH - 2 * LIP_OV)
        sk_c = tbm.copy(pr); tbm.booleanOperation(sk_c, tbm.copy(X.body('INNER_E')), B.IntersectionBooleanType)
        sk_w = tbm.copy(pr); tbm.booleanOperation(sk_w, tbm.copy(fb), B.IntersectionBooleanType)
        tool = X.union(X.union(X.union(frame, lips), sk_c), sk_w)
        out['tool_cm3'] = round(tool.volume, 3); out['tool_lumps'] = tool.lumps.count
        v0 = fb.volume
        X.combine(fb, [X.add(tool, 'B3I_cradle_tmp')])
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B3I_', 'LD2410C'))]
        out['board_x_front_mm3'] = round(vol_x(X.body('LD2410C_env_F'), fb), 3)
        out['core_air_x_front_mm3'] = round(vol_x(ob(f, AIR / 2, AIR, BW - 2 * LIP_OV - 0.1, BH - 2 * LIP_OV - 0.1), fb), 3)
        out['insertion_path_x_front_mm3'] = [[u, round(vol_x(ob(f, -BT / 2 - u, BT, BW, BH), fb), 3)] for u in (2.0, 5.0, 10.0, 20.0)]
        log('v5f_b3i_ld2410c_cradle', 'built', out)
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(k) for k in ['SLAB_frame', 'LCD_glass', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
                                     'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env']
                  + [k for k in names if k.startswith('LCD_') and k != 'LCD_glass']]
        r = X.interference(fb, others)
        out['interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d bodies)' % len(r)
        fan = []
        o = Dw(f[0] + 0.05 * n[0], f[1] + 0.05 * n[1], Z0)
        for ph in (-60, -45, -30, -15, 0, 15, 30, 45, 60):
            b_ = a + math.radians(ph); dx, dy = -math.sin(b_), math.cos(b_)
            d = V3(dx, dy * C, -dy * S); d.normalize()
            hp = adsk.core.ObjectCollection.create()
            fs = comp.findBRepUsingRay(o, d, adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
            hits = []
            for i in range(fs.count):
                nm = fs.item(i).body.name
                if nm == 'HOUSING_F_front' or nm == 'SLAB_frame' or nm.startswith('LCD_'):
                    p = hp.item(i)
                    hits.append((round(math.sqrt((p.x - o.x) ** 2 + (p.y - o.y) ** 2 + (p.z - o.z) ** 2) * 10, 1), nm))
            hits.sort()
            fan.append([ANG + ph, hits[:8]])
        out['ray_fan_deg_from_+y'] = fan
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3i_ld2410c_cradle', 'checks', out)
    print(json.dumps(out))
