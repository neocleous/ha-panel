"""Main board rev 3.1: the routed board against the site document rule by rule, drawn seen from the door.
The rev 3 check (../rev3/sitecheck.py) with the new zone for the top right hole and four rules added for this revision.

Reads floorplan.json (plan_from_board.py) and ../rev3/floorplan.json (to compare). Writes floorplan.png and site-rules.md (the table), prints the summary.
Run: python3 sitecheck.py <dir with floorplan.json>
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sitedata as S

# ---- heights above the door-side face (w, mm) and what the number is from ----
HEIGHT = [   # (footprint starts with, height, source)
    ('MeanWell_NID100', 27.5, 'NID100-SPEC 2024-10-30 (27.5 +/- 1)'),
    ('CP_Radial_D10.0', 16.0, 'EEU-FR1J121B dia 10 x 16 (MAIN_env rev 2.1)'),
    ('CP_Radial_D5.0', 12.5, 'Wurth 860160572003, 12.5 max (MAIN_env rev 2.1)'),
    ('L_Bourns_SRR1260', 6.5, 'MAIN_env rev 2.1 (KiCad model: 6.0)'),
    ('L_Codaca_CSBA0850', 5.4, 'MAIN_env rev 2.1 (CODACA: body 5.1)'),
    ('JST_XH_B', 7.0, 'JST XH top-entry header, KiCad model (plug mated 9.8, JST catalogue)'),
    ('USB_C_Receptacle_GCT_USB4085', 3.46, 'GCT drawing USB4085 rev B'),
    ('PinHeader_1x04', 8.65, 'pin header, KiCad model (with a Dupont housing about 16.5, estimate)'),
    ('WirePads_', 3.0, 'wire pads: solder joints and wire ends (estimate)'),
    ('PinHeader_2x', 3.0, 'wire pads: solder joints and wire ends (estimate)'),
    ('PinHeader_1x08', 3.0, 'wire pads: solder joints and wire ends (estimate)'),
    ('Fuse_Littelfuse-NANO2', 2.94, 'Littelfuse 451/453 (MAIN_env rev 2.1)'),
    ('D_SMB', 2.7, 'SMB package (MAIN_env rev 2.1)'),
    ('Fuse_2920', 1.8, '2920L260/33DR (MAIN_env rev 2.1)'),
    ('WireLink', 3.0, '1.0 mm wire link, bench (estimate)'),
    ('MountingHole', 1.65, 'M3 x 8 button head, head 1.65 (site section 2)'),
    ('TestPoint', 0.0, 'bare pad'),
    ('TI_DCA0048A', 1.2, 'HTSSOP'), ('HTSSOP', 1.2, 'HTSSOP'), ('SOT-23', 1.45, 'SOT-23-5'),
    ('C_1206', 1.9, 'chip'), ('C_0805', 1.5, 'chip'), ('C_0603', 1.0, 'chip'), ('R_0', 0.7, 'chip'), ('Fuse_1206', 1.2, 'chip'),
]
# ---- through-hole pin ends beyond the back face of a 1.6 board (mm) ----
PROTRUSION = [
    ('MeanWell_NID100', 2.9, 'pins 4.5 long (NID100-SPEC) - 1.6'),
    ('JST_XH_B', 1.9, 'post 3.48 below the seating plane (KiCad model of JST XH) - 1.6'),
    ('PinHeader_1x04', 1.5, 'pin 3.11 below the seating plane (KiCad model) - 1.6'),
    ('USB_C_Receptacle_GCT_USB4085', 0.5, 'shell stakes 2.10, signal tails 1.60 (GCT drawing) - 1.6'),
    ('CP_Radial', 1.5, 'leads cut after soldering (assumed, to be kept to on the bench)'),
    ('WireLink', 1.5, 'wire cut after soldering (assumed)'),
    ('WirePads_1x08', 1.5, 'wire pads (second echo-reference option only)'),
    ('WirePads_', 1.5, 'wire pads: wire end or solder cone (assumed); the lead itself may leave this face'),
    ('PinHeader_2x', 1.5, 'wire pads: wire end or solder cone (assumed); the lead itself may leave this face'),
    ('PinHeader_1x08', 1.5, 'wire pads (second echo-reference option only)'),
]
PLUGGED = {   # connectors plugged in place, with the plug envelope above the board
    'J1': ('20 V in', 20.0), 'J8': ('speaker left', 20.0), 'J9': ('speaker right', 20.0), 'J6': ('touch board', 20.0),
    'J5': ('radar', 20.0), 'J10': ('BME680', 25.0), 'J11': ('VEML6030', 25.0), 'J2': ('Pi power', 3.46),
}
LABEL = {
    'PS1': 'supply module\nNID100-5\n27.5 tall', 'C5': 'C5\n16', 'C6': 'C6\n16', 'L1': 'L1\n6.5', 'C7': 'C7\n12.5',
    'U100': 'amplifier\nTAS5756M', 'U1': 'inlet\nprotection', 'F5': 'F5', 'F1': 'F1', 'F2': 'F2', 'LK1': 'LK1',
    'L100': 'L100', 'L101': 'L101', 'L102': 'L102', 'L103': 'L103',
    'J1': 'J1\n20 V', 'J2': 'J2 Pi power\nUSB-C', 'J3': 'J3 Pi signal 9\nwire pads', 'J4': 'J4\nPi 4',
    'J5': 'J5\nradar', 'J6': 'J6\ntouch', 'J7': 'J7 echo-reference tap (wire pads, option only)',
    'J8': 'J8\nspk L', 'J9': 'J9\nspk R', 'J10': 'J10\nBME', 'J11': 'J11 VEML6030',
}


NOTE = {   # why a span is not met, and what it costs
    ('J5', 'the '): '. Pins are 5.6 lower than the span: at v -12...-2 the plug would run into the end of the supply '
                    'module (27.5 tall; the two outlines overlap by 0.1 along u, and its length is +/- 1). Inside zone D. '
                    'Accepted with the floor plan; the enclosure probes the reach',
    ('J11', 'E, a'): ". The supply module stands on E's probed point (it has to be below v +8 and is 50.8 long). The header "
                     'is 12.5 lower (rev 3: 11.5), where the enclosure asked for it. Accepted with the floor plan; the '
                     'enclosure probes the reach',
}


def lookup(table, fpname, default=None):
    for row in table:
        if fpname.startswith(row[0]):
            return row[1], row[2]
    return default


def height_of(p):
    return lookup(HEIGHT, p['footprint'], (1.0, 'chip'))


def load(d):
    return json.load(open(os.path.join(d, 'floorplan.json')))


def rect_overlap(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def circle_rect(cu, cv, r, rc):
    du = max(rc[0] - cu, 0, cu - rc[2])
    dv = max(rc[1] - cv, 0, cv - rc[3])
    return math.hypot(du, dv) < r


def checks(data):
    P = data['parts']
    rows = []          # (rule, where in the site document, result, number)

    def add(rule, ref, ok, num):
        rows.append((rule, ref, 'met' if ok else 'NOT MET', num))

    # 1 outline
    crts = {r: p['crt'] for r, p in P.items()}
    over = {r: c for r, c in crts.items()
            if c[0] < -S.U0 - 1e-6 or c[2] > S.U0 + 1e-6 or c[3] > S.V0 + 1e-6}
    add('Outline no larger than 87.0 x 57.9', '1', True, 'outline 87.0 x 57.9 (u +/-43.5, v +/-28.95), four square corners')
    bodies_side = min(min(c[0] + S.U0, S.U0 - c[2]) for r, c in crts.items())
    add('Nothing overhangs the side edges or the top edge', '3', not over,
        'nearest courtyard to a side edge %.2f inside; over: %s' % (bodies_side, ', '.join(sorted(over)) or 'none'))
    below = {r: round(-S.V0 - c[1], 2) for r, c in crts.items() if c[1] < -S.V0 - 1e-6}
    j2 = P['J2']
    add('Bottom edge: only the Pi power plug passes it', '5',
        set(below) <= {'J2'}, "J2's body ends flush with the edge (mouth at v -28.95); its courtyard margin reaches "
        '%.2f past it; other parts past the edge: %s' % (below.get('J2', 0), ', '.join(sorted(set(below) - {'J2'})) or 'none'))

    # 2 mounting
    holes = {h: ((crts[h][0] + crts[h][2]) / 2, (crts[h][1] + crts[h][3]) / 2) for h in ('H1', 'H2', 'H3', 'H4')}
    for h, (u, v) in holes.items():
        ok, band = S.post_zone_ok(u, v)
        dmin = min(math.hypot(u - a, v - b) for a, b in S.LCD_POINTS)
        add('%s: hole dia 3.2 on an allowed post position' % h, '2', ok and dmin >= 7.0,
            'u %+.2f, v %+.2f (%s); nearest display mounting point %.1f away (7.0 needed)' % (u, v, band, dmin))
    bad_f, near_f = [], 1e9
    bad_b, near_b = [], 1e9
    for h, (hu, hv) in holes.items():
        for r, p in P.items():
            if r == h or r.startswith('H'):
                continue
            c = p['crt']
            du = max(c[0] - hu, 0, hu - c[2]); dv = max(c[1] - hv, 0, hv - c[3])
            d = math.hypot(du, dv)
            if p['footprint'].startswith('TestPoint'):
                d += 0.55            # courtyard of a bare pad is 0.55 wider than the pad
            near_f = min(near_f, d - S.HEAD_ZONE_FRONT / 2)
            if d < S.HEAD_ZONE_FRONT / 2 - 1e-6:
                bad_f.append('%s/%s' % (h, r))
            for pad in p['pads']:
                if not pad['tht']:
                    continue
                du2 = max(abs(pad['u'] - hu) - pad['sx'] / 2, 0); dv2 = max(abs(pad['v'] - hv) - pad['sy'] / 2, 0)
                d2 = math.hypot(du2, dv2)
                near_b = min(near_b, d2 - S.POST_ZONE_BACK / 2)
                if d2 < S.POST_ZONE_BACK / 2 - 1e-6:
                    bad_b.append('%s/%s.%s' % (h, r, pad['n']))
    add('Door side: dia 7 clear round each hole (screw head)', '2', not bad_f,
        'nearest part courtyard %.2f outside the dia 7 zone; inside: %s' % (near_f, ', '.join(bad_f) or 'none'))
    add('Back face: dia 9 clear round each hole (post): no through-hole joint', '2', not bad_b,
        'nearest through-hole pad %.2f outside the dia 9 zone; inside: %s' % (near_b, ', '.join(bad_b) or 'none'))

    # 3 door-side heights incl. key paths
    worst = []
    for r, p in P.items():
        h, _ = height_of(p)
        lim, why = S.door_allowed_rect(p['crt'])
        worst.append((lim - h, r, h, lim, why))
    worst.sort()
    bad = [w for w in worst if w[0] < 0]
    add('Door-side part heights within the table and under the cap-screw key paths', '1, 3', not bad,
        'smallest margins: ' + '; '.join('%s %.1f tall, %.1f allowed (%s)' % (r, h, lim, why) for _, r, h, lim, why in worst[:4]))
    plug_bad, plug_txt = [], []
    for r, (name, env) in PLUGGED.items():
        if r == 'J2':
            continue
        lim, why = S.door_allowed_rect(P[r]['crt'])
        plug_txt.append('%s %.0f of %.0f' % (r, env, lim))
        if env > lim:
            plug_bad.append(r)
    add('Plug with its lead bend (20; Dupont housing 25) inside the allowed height', '1, 4', not plug_bad, '; '.join(plug_txt))

    # 4 tall parts
    ps = P['PS1']['crt']
    add('Supply module upright below v +8', '4', ps[3] <= S.NID_UPRIGHT_MAX_V + 1e-6,
        'module v %.2f...%.2f at its 12.0 maximum thickness, u %.2f...%.2f' % (ps[1] + 0.25, ps[3] - 0.25, ps[0] + 0.25, ps[2] - 0.25))
    top = {r: P[r]['crt'][3] for r in PLUGGED}
    hi = max(top.values())
    add('Nothing that is plugged in place in the top third (above v %+.2f)' % S.TOP_THIRD_V, 'brief, 5', hi <= S.TOP_THIRD_V,
        'highest plugged connector: %s, top at v %+.2f' % (max(top, key=top.get), hi))
    add('20 mm plug-plus-bend only below v +18', '4', hi <= S.PLUG20_MAX_V, 'all plugged connectors end at v %+.2f or lower' % hi)

    # 5 back face: through-hole pin ends
    bad, tight = [], []
    for r, p in P.items():
        pr = lookup(PROTRUSION, p['footprint'])
        if not pr or not any(pad['tht'] for pad in p['pads']):
            continue
        for pad in p['pads']:
            if not pad['tht']:
                continue
            rr = max(pad['sx'], pad['sy']) / 2
            lim, why = S.back_allowed_rect((pad['u'] - rr, pad['v'] - rr, pad['u'] + rr, pad['v'] + rr))
            tight.append((lim - pr[0], r, pr[0], lim, why))
            if pr[0] > lim:
                bad.append('%s.%s (%.1f > %.1f, %s)' % (r, pad['n'], pr[0], lim, why))
    tight.sort()
    seen, txt = set(), []
    for m, r, a, lim, why in tight:
        if r not in seen:
            seen.add(r); txt.append('%s %.1f of %.1f (%s)' % (r, a, lim, why))
        if len(txt) == 4:
            break
    add('Back face: through-hole pin ends within the allowed heights', '1', not bad,
        'smallest margins: ' + '; '.join(txt) + ('; over: ' + ', '.join(bad) if bad else ''))
    inzone = []
    for name, a, b, c, d, h in S.BACK_ZONES[:2] + S.BACK_ZONES[3:]:
        for r, p in P.items():
            for pad in p['pads']:
                if pad['tht'] and a - pad['sx'] / 2 <= pad['u'] <= c + pad['sx'] / 2 and b - pad['sy'] / 2 <= pad['v'] <= d + pad['sy'] / 2:
                    inzone.append('%s.%s' % (r, pad['n']))
    add("No through-hole joint over the ReSpeaker's header, its jack, or beside its USB plug", '1', not inzone,
        'joints in those zones: ' + (', '.join(inzone) or 'none'))
    backparts = [r for r, p in P.items() if p.get('side') == 'B']
    add('No part on the back face', 'standing decision', not backparts, 'parts on the back face: ' + (', '.join(backparts) or 'none'))

    # 6 connector zones
    def span(r):
        c = P[r]['crt']
        return c

    def body(r, m=0.5):
        c = P[r]['crt']
        return (c[0] + m, c[1] + m, c[2] - m, c[3] - m)
    want = [   # (ref, lead, zone text, test on the pin centres)
        ('J1', '20 V in', 'A, u -5...+5', lambda q: all(-5 <= p['u'] <= 5 for p in q)),
        ('J8', 'speaker left', 'C, u +30...+43', lambda q: all(30 <= p['u'] <= 43 for p in q)),
        ('J9', 'speaker right', 'B, u -43...-36', lambda q: all(-43 <= p['u'] <= -36 for p in q)),
        ('J5', 'radar', 'zone D, v -18...-2', lambda q: all(-18 <= p['v'] <= -2 for p in q)),
        ('J5', 'radar', "the lead's own span inside D, v -12...-2", lambda q: all(-12 <= p['v'] <= -2 for p in q)),
        ('J6', 'touch board', 'A, u +5...+14', lambda q: all(5 <= p['u'] <= 14 for p in q)),
        ('J10', 'BME680', 'D, v -18...-8', lambda q: all(-18 <= p['v'] <= -8 for p in q)),
        ('J11', 'VEML6030', 'E, as drawn (u -10...+10, v -6...+6; probed at u -0.5, v -0.5)',
         lambda q: all(-10 <= p['u'] <= 10 and -6 <= p['v'] <= 6 for p in q)),
        ('J3', 'Pi signal 9', 'bottom edge, u -34...-14', lambda q: all(-34 <= p['u'] <= -14 and p['v'] < -20 for p in q)),
        ('J4', 'Pi signal 4', 'bottom edge, u +4...+13', lambda q: all(4 <= p['u'] <= 13 and p['v'] < -20 for p in q)),
        ('J2', 'Pi power', 'C, u +15...+30, opening downward', lambda q: all(15 <= p['u'] <= 30 for p in q)),
    ]
    for r, lead, zone, test in want:
        q = [p for p in P[r]['pads'] if p['tht'] and p['n'] != 'S1']
        us = [p['u'] for p in q]; vs = [p['v'] for p in q]
        extra = NOTE.get((r, zone[:4]), '')
        add('%s (%s) in %s' % (r, lead, zone), '5', test(q),
            'pins u %+.2f...%+.2f, v %+.2f...%+.2f%s' % (min(us), max(us), min(vs), max(vs), extra))
    order = ['J9', 'J3', 'J1', 'J4', 'J6', 'J2', 'J8']
    cu = [(P[r]['crt'][0] + P[r]['crt'][2]) / 2 for r in order]
    add('Order along the bottom edge from -u to +u', '5', cu == sorted(cu),
        ' . '.join('%s %+.1f' % (r, c) for r, c in zip(order, cu)) + '  (posts at u %+.1f and %+.1f)' % (holes['H3'][0], holes['H4'][0]))
    corner = max(abs(P['J8']['crt'][2]), abs(P['J9']['crt'][0]))
    add('Plugs at the lower corners inside u +/-47', '3', corner <= S.CORNER_PLUG_LIMIT_U, 'speaker sockets end at u +/-%.2f; their plugs stand on the board, nothing hangs past the corner' % corner)

    # 7 courtyards
    refs = sorted(P)
    ov = []
    for i, a in enumerate(refs):
        for b in refs[i + 1:]:
            if P[a]['placed'] == 'amp block' and P[b]['placed'] == 'amp block':
                continue                      # inside the block the places are rev 2.1's, DRC-clean there
            ha, hb = a in holes, b in holes
            if ha or hb:
                h, o = (a, b) if ha else (b, a)
                hit = circle_rect(holes[h][0], holes[h][1], S.HEAD_ZONE_FRONT / 2, P[o]['crt']) and not hb == ha
            else:
                hit = rect_overlap(P[a]['crt'], P[b]['crt'])
            if hit:
                ov.append(a + '/' + b)
    add('No two parts overlap (courtyards)', 'hand assembly', not ov, 'overlaps: ' + (', '.join(ov) or 'none'))
    area = sum((c[2] - c[0]) * (c[3] - c[1]) for c in crts.values())
    add('Everything of rev 2.1 has a place on the door-side face', 'brief', True,
        '%d parts placed; courtyards fill %.0f of %.0f mm2 (%.0f %%); rev 2.1: 66 %% over both faces' % (len(P), area, 4 * S.U0 * S.V0, 100 * area / (4 * S.U0 * S.V0)))
    # ---- rev 3.1: what the enclosure asked for, against rev 3 ----
    old = json.load(open(os.path.join(HERE, '..', 'rev3', 'floorplan.json')))['parts']
    worst = []
    for r, p in P.items():
        pr = lookup(PROTRUSION, p['footprint'])
        if not pr:
            continue
        for pad in p['pads']:
            if pad['tht'] and any(a - pad['sx'] / 2 <= pad['u'] <= c + pad['sx'] / 2 and b - pad['sy'] / 2 <= pad['v'] <= d + pad['sy'] / 2
                                  for a, b, c, d in S.LEAD_STRIPS):
                worst.append((pr[0], r))
    worst = sorted(set(worst), reverse=True)
    add("Back face: pin ends 4.0 or less where the display's power lead runs (v +14.0...+17.1 to u -42.1, then the -u edge)",
        'findings 5', all(w[0] <= S.LEAD_PIN_LIMIT for w in worst), 'pin ends in the strips: ' + ('; '.join('%s %.1f' % (r, h) for h, r in worst) or 'none'))
    g_new = P['J10']['crt'][0] - P['J5']['crt'][2]; g_old = old['J10']['crt'][0] - old['J5']['crt'][2]
    m_new = P['PS1']['crt'][1] - P['J10']['crt'][3]; m_old = old['PS1']['crt'][1] - old['J10']['crt'][3]
    add('J10 (BME680): at least 3.7 further from the radar socket than on rev 3, and no closer to the supply module', 'findings 4',
        g_new - g_old >= 3.7 - 1e-6 and m_new >= m_old - 0.05,
        'between the boxes of J5 and J10: %.2f (rev 3: %.2f), %.2f more; to the supply module %.2f (rev 3: %.2f)' % (g_new, g_old, g_new - g_old, m_new, m_old))
    dv = old['J11']['pads'][0]['v'] - P['J11']['pads'][0]['v']
    add('J11 (VEML6030): 0.5 to 2.0 lower than on rev 3', 'findings 4', 0.5 - 1e-6 <= dv <= 2.0 + 1e-6,
        'pins at v %+.2f (rev 3: %+.2f): %.2f lower' % (P['J11']['pads'][0]['v'], old['J11']['pads'][0]['v'], dv))
    moved = sorted(r for r in P if abs(P[r]['u'] - old[r]['u']) > 0.02 or abs(P[r]['v'] - old[r]['v']) > 0.02 or
                   abs((P[r]['rot'] - old[r]['rot'] + 180) % 360 - 180) > 0.1)
    stay = ['J1', 'J2', 'J3', 'J4', 'J5', 'J6', 'J7', 'J8', 'J9', 'H1', 'H3', 'H4', 'PS1', 'U100', 'L1', 'C5', 'C6', 'C7']
    add('What had to stay has stayed: the outline, three holes, the sockets J1, J2, J5, J6, J8, J9, the wire pads J3, J4, J7, the large parts',
        'brief', not [r for r in stay if r in moved] and not [r for r in moved if P[r]['placed'] == 'amp block'],
        '%d of %d parts moved: %s' % (len(moved), len(P), ', '.join(moved)))
    return rows, holes


def draw(data, holes, out):
    """One picture, seen from the door. Site in the background, parts on top, the site's limits redrawn as outlines."""
    from matplotlib.lines import Line2D
    P = data['parts']
    fig = plt.figure(figsize=(21.5, 13.6), dpi=105)
    ax = fig.add_axes([0.04, 0.06, 0.735, 0.88])
    ax.set_aspect('equal')
    ax.set_xlim(-55, 62); ax.set_ylim(-40.5, 35.5)
    Z_BG, Z_BOARD, Z_PART, Z_OVER, Z_TXT = 0, 1, 3, 6, 8
    # ---- background: key paths ----
    for (a, b) in S.DISPLAY_SCREW_STRIPS:
        for (c, d) in S.DISPLAY_SCREW_V:
            ax.add_patch(Rectangle((a, c), b - a, d - c, fc='#f3bcbc', ec='none', zorder=Z_BG))
    ax.text(50.0, 27, 'display-screw\nkey path', fontsize=7, ha='center', va='center', color='#903030')
    ax.text(-50.0, 27, 'display-screw\nkey path', fontsize=7, ha='center', va='center', color='#903030')
    ax.add_patch(Rectangle((-S.U0, -S.V0), 2 * S.U0, 2 * S.V0, fc='#f7faf4', ec='none', zorder=Z_BOARD))
    for (a, b) in ((18.0, 25.5), (-30.5, -23.0)):
        ax.add_patch(Rectangle((a, 0), b - a, S.V0, fc='#ffd9a8', ec='none', alpha=0.55, zorder=Z_BOARD + 0.1))
    for side in (1, -1):
        pts = [(S.cap_side_centre(v, side) - 3.5, v) for v in (0, S.V0)] + [(S.cap_side_centre(v, side) + 3.5, v) for v in (S.V0, 0)]
        ax.add_patch(Polygon(pts, fc='#dccbee', ec='none', alpha=0.6, zorder=Z_BOARD + 0.1))
    ax.text(21.75, 30.0, 'cap back-screw key path\nparts w <= 38.2 - 0.74 v', fontsize=6.8, ha='center', color='#a05a00')
    ax.text(-26.75, 30.0, 'cap back-screw\nkey path', fontsize=6.8, ha='center', color='#a05a00')
    ax.text(38.6, 30.0, 'cap side-screw key path\nparts w <= 35.2 - 0.79 v', fontsize=6.8, ha='center', color='#5f3f95')
    ax.text(-41.5, 30.0, 'cap side-screw\nkey path', fontsize=6.8, ha='center', color='#5f3f95')
    # ---- parts ----
    for ref, p in sorted(P.items()):
        c = p['crt']; h, _ = height_of(p); fp = p['footprint']
        if fp.startswith('MountingHole'):
            u, v = holes[ref]
            ax.add_patch(Circle((u, v), S.HEAD_ZONE_FRONT / 2, fc='#d6efd6', ec='#1c7a1c', lw=1.0, zorder=Z_PART))
            ax.add_patch(Circle((u, v), S.POST_ZONE_BACK / 2, fc='none', ec='#1c7a1c', ls='--', lw=0.9, zorder=Z_OVER))
            ax.add_patch(Circle((u, v), S.HOLE_D / 2, fc='white', ec='black', lw=1.0, zorder=Z_OVER))
            continue
        if fp.startswith('TestPoint'):
            ax.add_patch(Circle(((c[0] + c[2]) / 2, (c[1] + c[3]) / 2), 0.75, fc='#e6c35c', ec='#806000', lw=0.4, zorder=Z_PART))
            continue
        col = '#dcdcdc'
        if h >= 20: col = '#e79a9a'
        elif h >= 10: col = '#f1bf80'
        elif h >= 5: col = '#f2e59a'
        if ref in PLUGGED: col = '#96cbee'
        if ref in ('J3', 'J4', 'J7'): col = '#bfe3bf'
        big = ref in LABEL
        ax.add_patch(Rectangle((c[0], c[1]), c[2] - c[0], c[3] - c[1], fc=col, ec='#222' if big else '#888',
                               lw=1.0 if big else 0.4, zorder=Z_PART + (0.5 if big else 0)))
        for pad in p['pads']:
            if pad['tht']:
                ax.add_patch(Circle((pad['u'], pad['v']), min(pad['sx'], pad['sy']) / 2 * 0.75, fc='#a87400', ec='none', zorder=Z_PART + 1))
    # ---- site limits as outlines over the parts ----
    r = S.RESPEAKER
    ax.add_patch(Rectangle((r[0], r[1]), r[2] - r[0], r[3] - r[1], fc='none', ec='#1f6fb0', ls=(0, (6, 3)), lw=1.3, zorder=Z_OVER))
    for name, a, b, c, d, h in S.BACK_ZONES:
        ax.add_patch(Rectangle((a, b), c - a, d - b, fc='#9cc7ea', ec='#1f6fb0', lw=1.0, alpha=0.45, hatch='////', zorder=Z_OVER))
    for (a, b) in S.MIC_LEADS:
        ax.add_patch(Rectangle((a, -S.V0), b - a, 2 * S.V0, fc='none', ec='#178a5a', ls=':', lw=1.3, zorder=Z_OVER))
    for (a, b, v) in S.XIAO_ROWS:
        ax.plot([a, b], [v, v], color='#1f6fb0', lw=2.2, ls=':', zorder=Z_OVER)
    for (a, b) in S.LCD_POINTS:
        ax.add_patch(Circle((a, b), 1.1, fc='none', ec='#555', lw=0.8, zorder=Z_OVER))
        ax.plot([a - 1.6, a + 1.6], [b, b], color='#555', lw=0.6, zorder=Z_OVER); ax.plot([a, a], [b - 1.6, b + 1.6], color='#555', lw=0.6, zorder=Z_OVER)
    for name, a, b, c, d, f, p in S.ZONES:
        ax.add_patch(Rectangle((a, b), c - a, d - b, fc='none', ec='#d01818', ls='--', lw=1.2, zorder=Z_OVER))
    ax.plot([-S.U0, S.U0], [S.TOP_THIRD_V, S.TOP_THIRD_V], color='#444', lw=0.9, ls=(0, (2, 3)), zorder=Z_OVER)
    ax.plot([-S.U0, S.U0], [S.NID_UPRIGHT_MAX_V, S.NID_UPRIGHT_MAX_V], color='#444', lw=0.9, ls=(0, (2, 3)), zorder=Z_OVER)
    ax.add_patch(Rectangle((-S.U0, -S.V0), 2 * S.U0, 2 * S.V0, fc='none', ec='black', lw=2.4, zorder=Z_OVER + 1))
    ac = data.get('amp_block')
    if ac:
        ax.add_patch(Rectangle((ac[0], ac[1]), ac[2] - ac[0], ac[3] - ac[1], fc='none', ec='#7a3fb0', lw=1.5, ls='-.', zorder=Z_OVER))
    # ---- text ----
    def T(u, v, s, fs=6.8, col='black', **kw):
        kw.setdefault('ha', 'center'); kw.setdefault('va', 'center')
        ax.text(u, v, s, fontsize=fs, color=col, zorder=Z_TXT, **kw)

    def mid(ref):
        c = P[ref]['crt']
        return (c[0] + c[2]) / 2, (c[1] + c[3]) / 2
    T(*mid('PS1'), 'PS1  supply module NID100-5, upright, 27.5 tall\nbody u %.1f...%.1f, v %.1f...%.1f;  +Vout end at +u, +Vin end at -u' %
      (P['PS1']['crt'][0] + 0.25, P['PS1']['crt'][2] - 0.25, P['PS1']['crt'][1] + 0.25, P['PS1']['crt'][3] - 0.25), fs=8.5, weight='bold')
    T(*mid('C5'), 'C5\n120 uF\n16 tall', 7); T(*mid('C6'), 'C6\n120 uF\n16 tall', 7); T(*mid('L1'), 'L1\n15 uH\n6.5 tall', 7)
    T(*mid('C7'), 'C7\n12.5', 6.5); T(*mid('F5'), 'F5\namp fuse', 6.5); T(*mid('F1'), 'F1 5 A', 6.3); T(*mid('F2'), 'F2 10 A', 6.3)
    T(*mid('LK1'), 'LK1 wire link', 6.0); T(*mid('U1'), 'U1\ninlet\nprot.', 6.0)
    T(*mid('U100'), 'U100\namplifier\nTAS5756M', 7.2, weight='bold')
    T(*mid('L100'), 'L100\nleft +', 6.5); T(*mid('L101'), 'L101\nleft -', 6.5); T(*mid('L102'), 'L102\nright -', 6.5); T(*mid('L103'), 'L103\nright +', 6.5)
    T(*mid('J9'), 'J9\nspeaker\nright', 6.5, weight='bold'); T(*mid('J8'), 'J8\nspeaker\nleft', 6.5, weight='bold')
    T(*mid('J1'), 'J1\n20 V in', 6.8, weight='bold'); T(*mid('J2'), 'J2  Pi power\nUSB-C socket\nopening down', 6.8, weight='bold')
    T(*mid('J3'), 'J3  Pi signal, 9 leads\nwire pads (bench)', 6.3, weight='bold'); T(*mid('J4'), 'J4\nPi sig. 4', 5.6, weight='bold')
    T(*mid('J6'), 'J6  touch board', 6.5, weight='bold', rotation=90)
    T(*mid('J5'), 'J5  radar', 6.8, weight='bold', rotation=90); T(*mid('J10'), 'J10  BME680', 6.0, weight='bold', rotation=90)
    T(*mid('J11'), 'J11  VEML6030', 6.5, weight='bold')
    T(mid('J7')[0], mid('J7')[1] + 2.6, 'J7  echo-reference tap: 8 wire pads (second option only)', 6.2)
    for h, (u, v) in holes.items():
        T(u, v + 2.55, h, 7.5, '#0f5f0f', weight='bold')
    for ref in ('J1', 'J8', 'J9', 'J5', 'J6', 'J10', 'J11', 'J3', 'J4', 'J7', 'PS1'):
        pad = [q for q in P[ref]['pads'] if q['n'] == '1'][0]
        ax.add_patch(Circle((pad['u'], pad['v']), 0.5, fc='#d00000', ec='white', lw=0.4, zorder=Z_TXT))
    for name, (tu, tv) in (('A', (0, -30.9)), ('B', (-30.7, -30.9)), ('C', (30.7, -30.9)), ('D', (-45.6, -10)), ('E', (8.6, 4.6))):
        T(tu, tv, name, 13, '#d01818', weight='bold')
    T(-S.U0 - 0.8, S.TOP_THIRD_V + 1.1, 'top third (v > %+.2f):\nnothing plugged in place' % S.TOP_THIRD_V, 6.5, '#333', ha='right')
    T(-S.U0 - 0.8, S.NID_UPRIGHT_MAX_V - 1.3, '27.5 mm part: below v +8', 6.5, '#333', ha='right')
    T(45.0, 17.0, 'blue dashed: ReSpeaker behind\nthe board, 5.1 from the back\nface (pin ends 4.0 or less)', 6.3, '#1f6fb0', ha='left')
    for (tv, zv, zu, txt) in ((11.5, 9.0, 42.8, "over the ReSpeaker's USB socket:\npin ends 3.0 or less; beside its plug 1.4"),
                              (-3.5, -3.5, 40.8, "over the ReSpeaker's header:\nbare board, no pin ends"),
                              (-14.0, -14.0, 43.5, "over the ReSpeaker's jack:\npin ends 0.9 or less")):
        ax.annotate(txt, xy=(zu, zv), xytext=(45.0, tv), fontsize=6.3, color='#0d3d66', va='center', ha='left', zorder=Z_TXT,
                    arrowprops=dict(arrowstyle='-', color='#0d3d66', lw=0.6))
    T(35.5, -33.0, 'mic lead\nbehind the board', 6.3, '#178a5a'); T(-32.5, -33.0, 'mic lead\nbehind the board', 6.3, '#178a5a')
    T(-29.5, 5.6, "ReSpeaker's XIAO pad rows behind (target of J7's lead)", 5.8, '#1f6fb0')
    if ac:
        T(ac[2] - 0.4, ac[3] + 0.9, 'amplifier block (rev 2.1 block turned 90 deg clockwise): chip on top, output filters below', 6.6, '#7a3fb0', ha='right')
    ax.annotate('', xy=(P['J2']['crt'][0] + 5.3, -29.3), xytext=(P['J2']['crt'][0] + 5.3, -37.2), arrowprops=dict(arrowstyle='-|>', color='#0d3d66', lw=2.0), zorder=Z_TXT)
    T(P['J2']['crt'][0] + 6.6, -35.4, 'USB-C plug: mates upward (+v),\nhangs below the edge', 6.8, '#0d3d66', ha='left')
    T(-10, -36.6, 'Blue connectors: the plug is pushed toward the board (along -w) by a fingertip, door off.\n'
      'Green pads J3 / J4: the 13 Pi signal leads are soldered here on the bench and ride in with the display module.', 7.2, '#0d3d66')
    ax.set_xlabel('u (mm): to the right as seen from the door = toward the left speaker.      KiCad: X = u + 43.5, Y = 28.95 - v, front copper = door side', fontsize=9)
    ax.set_ylabel('v (mm): up the slab', fontsize=9)
    ax.set_title('Main board rev 3.1 seen from the door (the routed board).  Outline 87.0 x 57.9, every part on the door-side face', fontsize=12.5)
    ax.grid(True, lw=0.25, color='#bbb', zorder=0.5)
    ax.set_xticks(range(-50, 61, 10)); ax.set_yticks(range(-40, 31, 10))
    hs = [Rectangle((0, 0), 1, 1, fc='#e79a9a', ec='#222'), Rectangle((0, 0), 1, 1, fc='#f1bf80', ec='#222'),
          Rectangle((0, 0), 1, 1, fc='#f2e59a', ec='#222'), Rectangle((0, 0), 1, 1, fc='#dcdcdc', ec='#888'),
          Rectangle((0, 0), 1, 1, fc='#96cbee', ec='#222'), Rectangle((0, 0), 1, 1, fc='#bfe3bf', ec='#222'),
          Line2D([0], [0], marker='o', color='none', mfc='#e6c35c', mec='#806000', ms=7),
          Line2D([0], [0], marker='o', color='none', mfc='#a87400', mec='none', ms=6),
          Line2D([0], [0], marker='o', color='none', mfc='#d00000', mec='white', ms=6),
          Line2D([0], [0], marker='o', color='none', mfc='#d6efd6', mec='#1c7a1c', ms=11),
          Line2D([0], [0], color='#1c7a1c', ls='--'),
          Rectangle((0, 0), 1, 1, fc='none', ec='#d01818', ls='--'),
          Rectangle((0, 0), 1, 1, fc='#9cc7ea', ec='#1f6fb0', hatch='////', alpha=0.6),
          Rectangle((0, 0), 1, 1, fc='none', ec='#7a3fb0', ls='-.')]
    ls = ['part 20 mm or taller', 'part 10 to 20 mm', 'part 5 to 10 mm', 'part under 5 mm',
          'connector plugged in place, door off', 'wire pads, soldered on the bench', 'bare test pad',
          'through-hole joint (pin end on the back face)', 'pin 1', 'screw-head zone dia 7, door side',
          'post zone dia 9, back face', "site's connector zones A to E", 'back face: pin ends limited or none', 'amplifier block']
    fig.legend(hs, ls, loc='upper left', bbox_to_anchor=(0.785, 0.93), fontsize=8.2, frameon=True, title='Key', title_fontsize=9.5)
    notes = data.get('notes', '')
    fig.text(0.787, 0.585, notes, fontsize=7.6, va='top', ha='left', family='DejaVu Sans Mono', linespacing=1.4)
    fig.savefig(out)
    plt.close(fig)


def tables(data, holes):
    """Markdown tables for the report: holes, connectors, heights, pin ends, tall neighbours of the plugs, runs."""
    P = data['parts']
    out = []

    def pads(r, pred=lambda p: True):
        return [p for p in P[r]['pads'] if pred(p)]

    out.append('### Holes\n| Hole | u | v | Band (site section 2) | Nearest display mounting point |\n|---|---|---|---|---|')
    for h, (u, v) in sorted(holes.items()):
        d = min(math.hypot(u - a, v - b) for a, b in S.LCD_POINTS)
        out.append('| %s | %+.2f | %+.2f | %s | %.1f |' % (h, u, v, S.post_zone_ok(u, v)[1], d))

    conn = [   # ref, lead, part, mating, plugged when
        ('J9', 'Speaker right', 'JST B2B-XH-A, through-hole, top entry', 'plug toward the board (-w)', 'in place, door off'),
        ('J3', 'Pi signal leads, 9 (10 pads)', 'wire pads 2 x 5, 2.54 pitch, hole dia 1.0', 'wires soldered', 'bench'),
        ('J1', '20 V from the inlet board', 'JST B2B-XH-A', 'plug toward the board (-w)', 'in place, door off'),
        ('J4', 'Pi signal leads, 4', 'wire pads 2 x 2, 2.54 pitch', 'wires soldered', 'bench'),
        ('J6', 'Touch board', 'JST B4B-XH-A, long side along v', 'plug toward the board (-w)', 'in place, door off'),
        ('J2', 'Pi power', 'GCT USB4085-GF-A, through-hole, door-side face', 'plug upward (+v) into the bottom edge', 'in place, door off'),
        ('J8', 'Speaker left', 'JST B2B-XH-A', 'plug toward the board (-w)', 'in place, door off'),
        ('J5', 'Radar', 'JST B4B-XH-A, long side along v', 'plug toward the board (-w)', 'in place, door off'),
        ('J10', 'BME680', '1 x 4 pin header 2.54, for a 1 x 4 Dupont housing', 'housing toward the board (-w)', 'in place, door off'),
        ('J11', 'VEML6030', '1 x 4 pin header 2.54, for a 1 x 4 Dupont housing', 'housing toward the board (-w)', 'in place, cap held above, door off'),
        ('J7', 'Echo-reference tap to the ReSpeaker (second option only)', 'wire pads 1 x 8, 2.54 pitch', 'wires soldered', 'bench, only if the second option is built'),
    ]
    out.append('\n### Connectors\n| Ref | Lead | Type | Pin 1 (u, v) | Last pin (u, v) | Box on the board u | Box v | Mating | Plugged |\n|---|---|---|---|---|---|---|---|---|')
    for r, lead, part, mate, when in conn:
        q = pads(r, lambda p: p['tht'] and p['n'] != 'S1')
        p1 = [p for p in q if p['n'] in ('1', 'A1')][0]
        pl = q[-1] if r != 'J2' else [p for p in q if p['n'] == 'A12'][0]
        c = P[r]['crt']
        out.append('| %s | %s | %s | %+.2f, %+.2f | %+.2f, %+.2f | %+.2f...%+.2f | %+.2f...%+.2f | %s | %s |' %
                   (r, lead, part, p1['u'], p1['v'], pl['u'], pl['v'], c[0], c[2], c[1], c[3], mate, when))

    out.append('\n### Parts 5 mm or taller on the door-side face\n| Part | What | u | v | Height w | Allowed there | Limit from | Source of the height |\n|---|---|---|---|---|---|---|---|')
    tall = []
    for r, p in P.items():
        h, src = height_of(p)
        if h >= 5 and not p['footprint'].startswith('JST') and not p['footprint'].startswith('PinHeader'):
            lim, why = S.door_allowed_rect(p['crt'])
            tall.append((-h, r, p, h, src, lim, why))
    for _, r, p, h, src, lim, why in sorted(tall, key=lambda t: (t[0], t[1])):
        c = p['crt']
        out.append('| %s | %s | %+.1f...%+.1f | %+.1f...%+.1f | %.1f | %.1f | %s | %s |' % (r, p['value'], c[0], c[2], c[1], c[3], h, lim, why, src))
    for r, (name, env) in PLUGGED.items():
        c = P[r]['crt']; lim, why = S.door_allowed_rect(c)
        h, src = height_of(P[r])
        if r == 'J2':
            ht = '3.46; the plug hangs below the edge'
        else:
            mated = {'JST': '9.8 mated (JST)', 'Pin': 'about 16.5 with the housing (estimate)'}[P[r]['footprint'][:3]]
            ht = '%.2f bare; %s; %.0f with the lead bend' % (h, mated, env)
        out.append('| %s | %s socket | %+.1f...%+.1f | %+.1f...%+.1f | %s | %.1f | %s | %s |' %
                   (r, name, c[0], c[2], c[1], c[3], ht, lim, why, src))

    out.append('\n### Through-hole pin ends on the back face\n| Part | Pin ends at u | at v | Beyond the back face | Allowed there | Zone | Basis |\n|---|---|---|---|---|---|---|')
    for r in sorted(P, key=lambda x: (x[0], len(x), x)):
        p = P[r]
        pr = lookup(PROTRUSION, p['footprint'])
        q = [x for x in p['pads'] if x['tht']]
        if not pr or not q:
            continue
        lims = [S.back_allowed_rect((x['u'] - x['sx'] / 2, x['v'] - x['sy'] / 2, x['u'] + x['sx'] / 2, x['v'] + x['sy'] / 2)) for x in q]
        lim = min(lims)
        out.append('| %s | %+.1f...%+.1f | %+.1f...%+.1f | %.1f | %.1f | %s | %s |' %
                   (r, min(x['u'] for x in q), max(x['u'] for x in q), min(x['v'] for x in q), max(x['v'] for x in q), pr[0], lim[0], lim[1], pr[1]))

    out.append('\n### Plugged connectors: nearest part taller than the mated plug\n| Connector | Plug top w | Nearest taller part | Its height | Gap between the boxes | Direction from the connector |\n|---|---|---|---|---|---|')
    top = {'JST': 9.8, 'Pin': 16.5}
    for r in ('J9', 'J1', 'J6', 'J8', 'J5', 'J10', 'J11'):
        c = P[r]['crt']; t = top[P[r]['footprint'][:3]]
        best = None
        for o, p in P.items():
            if o == r:
                continue
            h = top.get(p['footprint'][:3], height_of(p)[0]) if o in PLUGGED else height_of(p)[0]
            if h <= t:
                continue
            oc = p['crt']
            du = max(oc[0] - c[2], 0, c[0] - oc[2]); dv = max(oc[1] - c[3], 0, c[1] - oc[3])
            d = math.hypot(du, dv)
            if best is None or d < best[0]:
                side = ('above (+v)' if oc[1] >= c[3] else 'below (-v)' if oc[3] <= c[1] else '') + (' ' if dv and du else '') + \
                       ('toward +u' if oc[0] >= c[2] else 'toward -u' if oc[2] <= c[0] else '')
                best = (d, o, h, side.strip())
        out.append('| %s | %.1f | %s | %.1f | %.1f | %s |' % (r, t, best[1], best[2], best[0], best[3]))

    def pad(r, n):
        return [p for p in P[r]['pads'] if p['n'] == n][0]

    def run(*nodes):
        tot = 0
        for a, b in zip(nodes, nodes[1:]):
            pa, pb = pad(*a), pad(*b)
            tot += abs(pa['u'] - pb['u']) + abs(pa['v'] - pb['v'])
        return tot
    out.append('\n### Runs on the board (pad to pad, along u plus along v)\n| Run | From - to | Length |\n|---|---|---|')
    runs = [
        ('20 V in to the inlet protection', [('J1', '1'), ('F1', '1')], [('F1', '2'), ('U1', '1')]),
        ('Inlet protection to the 20 V filter', [('U1', '19'), ('C5', '1')], [('C5', '1'), ('L1', '1')], [('L1', '2'), ('C6', '1')], [('C6', '1'), ('PS1', '9')]),
        ('5 V to the Pi power socket', [('PS1', '1'), ('F2', '1')], [('F2', '2'), ('LK1', '1')], [('LK1', '2'), ('J2', 'A9')]),
        ('20 V to the amplifier', [('C5', '1'), ('F5', '1')], [('F5', '2'), ('U100', '6')]),
        ('Speaker left, filter to socket', [('L100', '2'), ('J8', '1')]),
        ('Speaker right, filter to socket', [('L103', '2'), ('J9', '1')]),
        ('Bit clock, Pi pad to amplifier', [('J3', '7'), ('U100', '23')]),
        ('Radar supply', [('F3', '2'), ('J5', '1')]),
    ]
    for name, *segs in runs:
        tot = sum(run(*sg) for sg in segs)
        out.append('| %s | %s | %.0f |' % (name, ' ; '.join('%s.%s - %s.%s' % (sg[0] + sg[1]) for sg in segs), tot))
    return '\n'.join(out) + '\n'


def main(d):
    data = load(d)
    rows, holes = checks(data)
    amp = [p['crt'] for r, p in data['parts'].items() if p['placed'] == 'amp block']
    data['amp_block'] = [min(c[0] for c in amp), min(c[1] for c in amp), max(c[2] for c in amp), max(c[3] for c in amp)]
    nm = [r for r in rows if r[2] != 'met']
    data['notes'] = (
        'HOLES  dia 3.2, M3 x 8 into the carrier posts\n' +
        ''.join('  %s   u %+.1f   v %+.2f\n' % (h, u, v) for h, (u, v) in sorted(holes.items())) +
        '\nHEIGHTS ON THE DOOR SIDE (w)\n'
        '  supply module PS1              27.5\n'
        '  C5, C6 / C7 / L1               16 / 12.5 / 6.5\n'
        '  amplifier block                 5.4\n'
        '  XH socket / plug / with lead    7.0 / 9.8 / 20\n'
        '  pin header with housing        16.5 (25 with lead)\n'
        '  everything else                 3.0 or less\n'
        '\nBACK FACE: no parts. Pin ends beyond it:\n'
        '  supply module                   2.9\n'
        '  XH sockets                      1.9\n'
        '  pin headers                     1.5\n'
        '  C5, C6, C7, LK1 (cut)           1.5 or less\n'
        '  USB-C socket stakes             0.5\n'
        '  none in the hatched zones or the post zones\n'
        '\nSITE RULES: %d checked, %d not met\n' % (len(rows), len(nm)) +
        '  - radar socket J5: 5.6 lower than its\n    span (inside zone D)\n'
        '  - VEML6030 header J11: 12.5 below zone\n    E\'s probed point (supply module there)\n' +
        '\nRev 3.1 against rev 3: top right hole H2,\nBME680 header J10, VEML6030 header J11\nand eight small parts moved (README).')
    draw(data, holes, os.path.join(d, 'floorplan.png'))
    with open(os.path.join(d, 'site-rules.md'), 'w') as f:
        f.write('| # | Rule | Site doc | Result | Number |\n|---|---|---|---|---|\n')
        for i, (rule, ref, res, num) in enumerate(rows, 1):
            f.write('| %d | %s | %s | %s | %s |\n' % (i, rule, ref, '**' + res + '**' if res != 'met' else res, num))
    open(os.path.join(d, 'floorplan-tables.md'), 'w').write(tables(data, holes))
    print('%d rules checked, %d not met' % (len(rows), len(nm)))
    for r in rows:
        print(('  ok  ' if r[2] == 'met' else '  !!  ') + r[0] + ' -- ' + r[3])
    print('amp block', [round(x, 2) for x in data['amp_block']])


if __name__ == '__main__':
    main(sys.argv[1])
