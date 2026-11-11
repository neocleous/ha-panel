# rev F i2a (2026-11-11): step 3 repeated, block 2 - the fourth post at the board's moved hole H2 (u +19.2, v +25.0), before and after
#   the carrier is rebuilt. Nothing stays in the model: three AUD_* bodies are added hidden for measureMinimumDistance and deleted.
#   A  post dia 8 and dia 9 (0.5 clear), from the carrier plate's display side (depth 15.2) to the board's back face (31.1), against
#      every current body and lead except the board and the carrier: overlap in mm3
#   B  how much of the plate (depth 15.2..17.2) lies under the post's foot (dia 8 = 100.5 mm3)
#   C  smallest distance from the post (dia 8, depth 17.2..31.1) to every current body and lead within 12, with both points (u, v, depth),
#      and to the plug assumed on the display's power header (the header's footprint plus 0.5: u 27.25..33.45, v 21.42..27.62, standing
#      from the header's base at depth 9.9 to 23.9)
#   D  the screw head on the door side (dia 5.7 x 1.65): nearest board parts and key paths
#   E  a straight key on the board's normal over each of the four screws (dia 5 x 70 from the head, door off): what it meets
#   F  the same key tilted down (toward the bottom edge) by 5..25 degrees over the two top screws, dia 5 and dia 3: mm3 in the way
#      (for the audit: the board is screwed on at the bench, so this matters only for taking the board off in place)
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
P4 = (19.2, 25.0)
HOLES = {'top left': (-37.0, 22.0), 'top right': (19.2, 25.0), 'bottom left': (-31.0, -25.25), 'bottom right': (31.0, -25.25)}
PLUG = (27.25, 33.45, 21.42, 27.62, 9.9, 23.9)
KEYFIX = ('HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_tall', 'MAIN_conn', 'MAIN_low', 'BME_HOOD', 'LD2410C_env_F')


def near(a, b, r):
    p, q = a.boundingBox, b.boundingBox
    r = r / 10.0
    return not (p.minPoint.x - r > q.maxPoint.x or q.minPoint.x - r > p.maxPoint.x or p.minPoint.y - r > q.maxPoint.y or q.minPoint.y - r > p.maxPoint.y
                or p.minPoint.z - r > q.maxPoint.z or q.minPoint.z - r > p.maxPoint.z)


def pd(p):
    q = Bf(p)
    return [round(q[0], 1), round(q[1], 1), round(D0 + q[2], 1)]


def run(_context):
    st = {}
    t0 = time.time()
    X = K()
    made = []
    try:
        c = cache()
        others = [b for b in current(X, leads=True) if not b.name.startswith('MAIN_') and b.name != 'RESP_CARRIER']
        A = {}
        for r in (4.0, 4.5):
            cyl = X.cyld(U0 + P4[0], V0 + P4[1], r, 15.2, 31.1)
            row = {}
            for b in others:
                if not cyl.boundingBox.intersects(b.boundingBox):
                    continue
                big = c['crop_front_site'] if (b.name == 'HOUSING_F_front' and 'crop_front_site' in c) else tcopy(X, b.name)
                a = xvol(X, cyl, big)
                if abs(a) > 0.005:
                    row[b.name] = round(a, 2)
            A['dia %.0f' % (2 * r)] = row
        st['A'] = A
        foot = X.cyld(U0 + P4[0], V0 + P4[1], 4.0, 15.2, 17.2)
        st['B'] = [round(xvol(X, foot, tcopy(X, 'RESP_CARRIER')), 1), round(X.vol(foot), 1)]
        post = X.add(X.cyld(U0 + P4[0], V0 + P4[1], 4.0, 17.2, 31.1), 'AUD_post_H2', show=False); made.append(post)
        plug = X.add(X.dbox(U0 + PLUG[0], U0 + PLUG[1], PLUG[4], PLUG[5], V0 + PLUG[2], V0 + PLUG[3]), 'AUD_plug_lcd5v', show=False); made.append(plug)
        head = X.add(cyl_b(X, P4[0], P4[1], 2.85, 0.0, 1.65), 'AUD_head_H2', show=False); made.append(head)
        mm = X.app.measureManager
        Cc = {}
        for b in current(X, leads=True) + [plug]:
            if b.name == 'RESP_CARRIER' or not near(post, b, 12.0):
                continue
            m = mm.measureMinimumDistance(post, b)
            if m.value * 10.0 <= 12.0:
                Cc[b.name] = [round(m.value * 10.0, 2), pd(m.positionOne), pd(m.positionTwo)]
        st['C'] = dict(sorted(Cc.items(), key=lambda kv: kv[1][0]))
        Dd = {}
        for b in current(X):
            if b.name in ('MAIN_pcb', 'RESP_CARRIER') or not near(head, b, 10.0):
                continue
            m = mm.measureMinimumDistance(head, b)
            if m.value * 10.0 <= 10.0:
                Dd[b.name] = [round(m.value * 10.0, 2), pd(m.positionOne), pd(m.positionTwo)]
        st['D'] = dict(sorted(Dd.items(), key=lambda kv: kv[1][0]))
        m = mm.measureMinimumDistance(plug, X.body('LEAD_LCD_5V'))
        st['plug box to the display power lead'] = round(m.value * 10.0, 2)
        if 'crop_front_rear' not in c:
            t = X.cp(tcopy(X, 'HOUSING_F_front')); X.sec(t, X.dbox(-110, 110, 18, 140, -115, 35)); c['crop_front_rear'] = t
        fix = {'shell': c['crop_front_rear']}
        for n in KEYFIX:
            fix[n] = tcopy(X, n)
        E = {}
        for h, (u, v) in HOLES.items():
            key = cyl_b(X, u, v, 2.5, 1.65, 71.65)
            row = {}
            for n, f in fix.items():
                a = xvol(X, key, f)
                if abs(a) > 0.05:
                    row[n] = round(a, 1)
            E[h] = row
        st['E'] = E
        F = {}
        for h in ('top left', 'top right'):
            u, v = HOLES[h]
            tip = Bp(u, v, 1.65)
            for r in (2.5, 1.5):
                row = {}
                for deg in (0, 5, 10, 15, 20, 25):
                    a = math.radians(deg)
                    end = P3(tip.x, tip.y - 7.0 * math.cos(a), tip.z - 7.0 * math.sin(a))
                    key = X.tbm.createCylinderOrCone(tip, r / 10.0, end, r / 10.0)
                    hit = {}
                    for n, f in fix.items():
                        q = xvol(X, key, f)
                        if abs(q) > 0.05:
                            hit[n.replace('HOUSING_F_', '').replace('MAIN_', '')] = round(q, 1)
                    row['%d' % deg] = hit
                F['%s dia %.0f' % (h, 2 * r)] = row
        st['F'] = F
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    for b in made:
        try:
            b.deleteMe()
        except Exception:
            st.setdefault('CLEANUP_FAIL', []).append(b.name)
    st['left'] = [n for n in X.names() if n.startswith(('AUD_', 'NEW_'))]
    st['bodies'] = X.root.bRepBodies.count
    st['t_end'] = round(time.time() - t0, 1)
    status3('i2a' + globals().get('TAG', ''), st)


run(None)
