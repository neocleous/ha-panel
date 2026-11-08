# rev F e4b (2026-11-08): the four M2 holes become pilots for M2 x 6 pan-head screws for plastic (Daniel 2026-11-08: the
#   ReSpeaker and the 5807 are screwed straight into the printed bosses; supersedes ruthex M2 x 4 + DIN912 M2 x 5).
#   Per hole: the D3.2 x 4.5 insert hole is filled (a D3.4 plug, flush with the boss face, 0.1 into the material under it),
#   then a D1.6 pilot (PT table: 0.80 d in ABS, 0.78 d in ASA) 5.5 deep, or through where a blind hole would leave less
#   than 1.2 under it (K8), with a 0.3 x 45 deg entry chamfer (D2.2 at the face). Gates: the plug fills only the old hole;
#   the pilot runs through material only (no other void in its path); volumes; one lump; probes. Cradle only (Daniel
#   2026-11-08, "slot the roof"): the bezel roof over the PCB's receptacle end (y -83.8...-81.6, z 24.95-26.7) overhangs the
#   rear of both screw heads, so a straight driver can't reach a pan head; a slot 4.6 wide through the roof over each screw,
#   back to the 0.8 back wall (y -83.8), lets a D4 driver and a D4.2 head pass. Gate: each slot removes only roof (4.6 x 2.2
#   x 1.75). Old bodies hidden as <name>_e4. Not saved here (e4d saves). Writes m2_e4/e4b_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT_DIR = os.path.expanduser('~/Documents/HA_panel_renders/m2_e4')
GUARD = {'RESP_CARRIER': 10.0716, 'CRADLE_5807': 2.1775, 'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633}
# hole mid-points (x_rel, y, z) from the audit's fastener table (S.1), 0.05 tolerance
HOLES = {'RESP_CARRIER': [(-35.11, -16.93, 127.0), (22.6, -10.92, 98.72)],
         'CRADLE_5807': [(-7.49, -81.16, 18.25), (7.75, -81.16, 18.25)]}
R_OLD, D_OLD = 1.6, 4.5
R_FILL = 1.7
R_P, DEPTH, CH = 0.8, 5.5, 0.3
SKIN_MIN = 1.2
SLOT = {'CRADLE_5807': {'half_w': 2.3, 'y': (-83.8, -81.0), 'z': (24.5, 27.2), 'roof': (-83.8, -81.6, 24.95, 26.7)}}
PI = math.pi
B = adsk.fusion.BooleanTypes


def w(p):
    return [round(p.x * 10 - XC, 3), round(wy(p), 3), round(wz(p), 3)]


def wv(v):
    return [round(v.x, 5), round(v.y * C - v.z * S, 5), round(v.y * S + v.z * C, 5)]


def at(o, a, t):
    return P3(o.x + a.x * t / 10, o.y + a.y * t / 10, o.z + a.z * t / 10)


def perp(a):
    r = V3(1, 0, 0) if abs(a.x) < 0.9 else V3(0, 1, 0)
    u = a.crossProduct(r); u.normalize(); v = a.crossProduct(u); v.normalize()
    return u, v


def shifted(o, q, r):
    return P3(o.x + q.x * r / 10, o.y + q.y * r / 10, o.z + q.z * r / 10)


def find_holes(body):
    res = []
    for f in body.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType():
            continue
        cy = adsk.core.Cylinder.cast(g)
        if abs(cy.radius * 10 - R_OLD) > 0.005:
            continue
        a = cy.axis.copy(); a.normalize(); o = cy.origin
        ts = []
        for e in f.edges:
            for vx in (e.startVertex, e.endVertex):
                q = vx.geometry
                ts.append(((q.x - o.x) * a.x + (q.y - o.y) * a.y + (q.z - o.z) * a.z) * 10)
        p = f.pointOnFace
        ok, n = f.evaluator.getNormalAtPoint(p)
        d = V3(p.x - o.x, p.y - o.y, p.z - o.z); t = d.dotProduct(a)
        if n.dotProduct(V3(d.x - a.x * t, d.y - a.y * t, d.z - a.z * t)) > 0:
            continue                                # convex: not a hole
        t0, t1 = min(ts), max(ts)
        if body.pointContainment(at(o, a, t1 + 0.05)) in INS:
            a = V3(-a.x, -a.y, -a.z); t_top, t_bot = -t0, -t1
        else:
            t_top, t_bot = t1, t0
        res.append({'o': o, 'a': a, 't_top': t_top, 't_bot': t_bot, 'mid': w(at(o, a, (t_top + t_bot) / 2))})
    return res


def vol_x(tbm, a_, b_):
    q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return q.volume * 1000


def exit_depth(body, h):
    """depth below the hole top where the material under the hole ends, on the axis and at r 0.8 x 4 (must agree)."""
    o, a = h['o'], h['a']; u, v = perp(a)
    lines = [o] + [shifted(o, q, s * R_P) for q in (u, v) for s in (1, -1)]
    res = []
    for base in lines:
        inside = lambda t: body.pointContainment(at(base, a, t)) in INS
        t = h['t_bot'] - 0.01; found = None
        while t > h['t_bot'] - 12.0:
            if not inside(t):
                lo, hi = t, t + 0.05
                for _ in range(12):
                    mid = (lo + hi) / 2
                    if inside(mid):
                        hi = mid
                    else:
                        lo = mid
                found = h['t_top'] - (lo + hi) / 2; break
            t -= 0.05
        res.append(None if found is None else round(found, 4))
    return res


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t00 = time.time()
    try:
        X = Ctx(); tbm = X.tbm
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        if X.doc.isModified:
            bad.append('document modified')
        if st['version'][0] != st['version'][1]:
            bad.append('not the latest version')
        clash = [b.name for b in X.comp.bRepBodies if b.name in ('RESP_CARRIER_e4', 'CRADLE_5807_e4')]
        if clash:
            bad.append('exists: %s' % clash)
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        plan = {}
        for name, mids in HOLES.items():
            body = X.body(name)
            found = []
            for h in find_holes(body):                # a bore split into two faces counts once
                if not any(max(abs(h['mid'][k] - g['mid'][k]) for k in range(3)) < 0.01 for g in found):
                    found.append(h)
            st[name + '_found'] = [h['mid'] for h in found]
            hs = []
            for m in mids:
                hit = [h for h in found if max(abs(h['mid'][k] - m[k]) for k in range(3)) < 0.05]
                if len(hit) != 1:
                    raise RuntimeError('%s hole at %s: %d matches' % (name, m, len(hit)))
                h = hit[0]
                if abs(h['t_top'] - h['t_bot'] - D_OLD) > 0.01:
                    raise RuntimeError('%s hole at %s: depth %.3f' % (name, m, h['t_top'] - h['t_bot']))
                ex = exit_depth(body, h)
                if None in ex or max(ex) - min(ex) > 0.01:
                    raise RuntimeError('%s hole at %s: exit depths %s' % (name, m, ex))
                h['exit'] = sum(ex) / len(ex)
                h['through'] = h['exit'] - DEPTH < SKIN_MIN
                hs.append(h)
            plan[name] = hs
        for name, hs in plan.items():
            old = X.body(name)
            tb = tbm.copy(old)
            v0 = tb.volume * 1000; rep = []
            for h in hs:
                o, a, t_top, t_bot = h['o'], h['a'], h['t_top'], h['t_bot']
                r = {'top_w': w(at(o, a, t_top)), 'axis_out_w': wv(a), 'old_depth': round(t_top - t_bot, 3),
                     'exit_depth': round(h['exit'], 3), 'through': h['through']}
                fill = tbm.createCylinderOrCone(at(o, a, t_bot - 0.1), R_FILL / 10, at(o, a, t_top), R_FILL / 10)
                ring = PI * (R_FILL ** 2 - R_OLD ** 2) * (t_top - t_bot) + PI * R_FILL ** 2 * 0.1
                r['fill_in_material'] = [round(vol_x(tbm, tb, fill), 4), round(ring, 4)]
                if abs(r['fill_in_material'][0] - ring) > 0.005:
                    raise RuntimeError('fill gate %s %s' % (name, r))
                va = tb.volume * 1000
                tbm.booleanOperation(tb, fill, B.UnionBooleanType)
                r['fill_added'] = [round(tb.volume * 1000 - va, 4), round(PI * R_OLD ** 2 * (t_top - t_bot), 4)]
                if abs(r['fill_added'][0] - r['fill_added'][1]) > 0.005:
                    raise RuntimeError('fill volume %s %s' % (name, r))
                L_mat = h['exit'] if h['through'] else DEPTH
                L = L_mat + 0.5 if h['through'] else DEPTH
                tool = tbm.createCylinderOrCone(at(o, a, t_top + 0.5), R_P / 10, at(o, a, t_top - L), R_P / 10)
                cone = tbm.createCylinderOrCone(at(o, a, t_top + 0.5), (R_P + CH + 0.5) / 10, at(o, a, t_top - CH - 0.1),
                                                (R_P - 0.1) / 10)
                tbm.booleanOperation(tool, cone, B.UnionBooleanType)
                rc = R_P + CH
                expect = PI * CH / 3 * (rc ** 2 + rc * R_P + R_P ** 2) + PI * R_P ** 2 * (L_mat - CH)
                r['pilot_in_material'] = [round(vol_x(tbm, tb, tool), 4), round(expect, 4)]
                if abs(r['pilot_in_material'][0] - expect) > 0.005:
                    raise RuntimeError('pilot gate %s %s' % (name, r))
                vb = tb.volume * 1000
                tbm.booleanOperation(tb, tool, B.DifferenceBooleanType)
                r['pilot_removed'] = round(vb - tb.volume * 1000, 4)
                r['L_material'] = round(L_mat, 3)
                r['skin_axial'] = None if h['through'] else round(h['exit'] - DEPTH, 3)
                u, v = perp(a)
                ins = lambda d_, rr, q=u: tb.pointContainment(at(shifted(o, q, rr), a, t_top - d_)) in INS
                pr = {'void_axis_0.1': not ins(0.1, 0), 'void_axis_1': not ins(1.0, 0), 'void_axis_3': not ins(3.0, 0),
                      'void_axis_end-0.05': not ins(L_mat - 0.05, 0), 'solid_r1.2_d2': ins(2.0, 1.2),
                      'solid_r1.2_d2_v': ins(2.0, 1.2, v), 'solid_r0.95_d0.35': ins(0.35, 0.95),
                      'void_r1.0_d0.05': not ins(0.05, 1.0), 'solid_r0.85_d4.4': ins(4.4, 0.85)}
                if h['through']:
                    pr['void_axis_exit+0.05'] = not ins(L_mat + 0.05, 0)
                else:
                    pr['solid_axis_depth+0.05'] = ins(DEPTH + 0.05, 0)
                r['probes'] = pr
                if not all(pr.values()):
                    raise RuntimeError('probes %s %s' % (name, pr))
                rep.append(r)
            slots = []
            for h in (hs if name in SLOT else []):
                sc = SLOT[name]; xr = w(at(h['o'], h['a'], h['t_top']))[0]; hw = sc['half_w']
                y0, y1, z0, z1 = sc['roof']
                box = X.wbox(XC + xr - hw, XC + xr + hw, sc['y'][0], sc['y'][1], sc['z'][0], sc['z'][1])
                expect = 2 * hw * (y1 - y0) * (z1 - z0)
                got = vol_x(tbm, tb, box)
                r = {'x_rel': xr, 'roof_in_slot': [round(got, 4), round(expect, 4)]}
                if abs(got - expect) > 0.05:
                    raise RuntimeError('slot gate %s %s' % (name, r))
                vb = tb.volume * 1000
                tbm.booleanOperation(tb, box, B.DifferenceBooleanType)
                r['removed'] = round(vb - tb.volume * 1000, 4)
                ins = lambda x_, y_, z_: tb.pointContainment(Dw(XC + x_, y_, z_)) in INS
                pr = {'void_slot': not ins(xr, -82.7, 25.8), 'void_slot_back': not ins(xr + hw - 0.1, -83.7, 26.6),
                      'solid_back_wall': ins(xr, -84.2, 25.8), 'solid_roof_centre': ins(0.0, -82.7, 25.8),
                      'solid_roof_beside': ins(xr - hw - 0.1 if xr > 0 else xr + hw + 0.1, -82.7, 25.8),
                      'solid_post_top': ins(xr + 2.0, -81.16, 20.4)}
                r['probes'] = pr
                if not all(pr.values()):
                    raise RuntimeError('slot probes %s %s' % (name, pr))
                slots.append(r)
            if tb.lumps.count != 1:
                raise RuntimeError('%s lumps %d' % (name, tb.lumps.count))
            vis = old.isLightBulbOn
            mat, app_ = old.material, old.appearance
            old.name = name + '_e4'; old.isLightBulbOn = False
            nb = X.add(tb, name); nb.isLightBulbOn = vis
            try:
                if mat:
                    nb.material = mat
                if app_:
                    nb.appearance = app_
            except Exception:
                pass
            st[name] = {'holes': rep, 'slots': slots, 'vol_old_cm3': round(v0 / 1000, 4), 'vol_new_cm3': round(nb.volume, 4),
                        'delta_mm3': round(nb.volume * 1000 - v0, 3), 'lumps': nb.lumps.count,
                        'faces_old_new': [old.faces.count, nb.faces.count], 'visible': vis}
        log('v5f_e4b_m2_pilots', 'done', {k: st[k] for k in HOLES})
        st['t_s'] = round(time.time() - t00, 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(os.path.join(OUT_DIR, 'e4b_status.json'), 'w'), indent=1)
    print(json.dumps(st))


run(None)
