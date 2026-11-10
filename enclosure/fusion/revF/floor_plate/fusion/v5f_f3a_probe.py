# rev F f3a (2026-11-10): read-only probe for block 3.
#   A  the notch for the ReSpeaker's USB-C plug in the wall beside the LCD opening: what a tool x 55..79, Zd -29.3..-11.2 through the
#      wall removes, where the wall ends, and which other bodies reach into the tool
#   B  the leads as modelled in version 42: path nodes (centres of the circular edges), to re-route from
#   C  where the main board's connectors are now (world mm)
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
XCB, ZCB, DF = 2.55, -28.5, 32.7
CONN = {'J1': (45.0, 45.3), 'J2': (20.0, 50.0), 'J3': (59.5, 36.25), 'J4': (46.3, 36.25), 'J5': (75.7, 4.0), 'J6': (41.0, 24.0), 'J8': (11.5, 44.0),
        'J9': (78.0, 44.0), 'J10': (64.7, 6.5)}


def slab(p):                              # design point -> (x_rel, d, Zd)
    return (p.x * 10 - XC, -p.y * 10, p.z * 10)


def sl_lumps(X, tb):
    out = []
    for l in tb.lumps:
        vs = [slab(v.geometry) for v in l.vertices]
        out.append([round(l.volume * 1000, 1)] + [round(f(v[i] for v in vs), 1) for i in range(3) for f in (min, max)])
    return sorted(out, key=lambda t: -t[0])[:5]


def run(_context):
    st = {}
    try:
        X = K()
        F = X.body('HOUSING_F_front')
        piece = X.cp(F); X.sec(piece, X.dbox(40.0, 105.0, 0.0, 40.0, -45.0, 5.0))
        t = X.cp(piece); X.sec(t, X.dbox(55.0, 79.0, 8.5, 15.3, -29.3, -11.2)); st['A_notch[vol,x0,x1,d0,d1,z0,z1]'] = sl_lumps(X, t)
        t = X.cp(piece); X.sec(t, X.dbox(55.0, 105.0, 0.0, 40.0, -21.0, -19.0)); st['A_slice_Zd-20'] = sl_lumps(X, t)
        tool = X.dbox(55.0, 79.0, 8.5, 15.3, -29.3, -11.2); hit = {}
        for b in X.root.bRepBodies:
            n = b.name
            if n.endswith('_v42') or n.startswith(('REF_', 'TOOL_', 'INNER', 'RENDER_', 'HOUSING_F_front', 'HOUSING_E', 'HOUSING_shell', 'HOUSING_F_wip')):
                continue
            if b.boundingBox.intersects(tool.boundingBox):
                v = X.clash(tool, b)
                if abs(v) > 0.05:
                    hit[n] = round(v, 1)
        st['A_in_tool'] = hit
        # B lead nodes
        leads = {}
        for b in X.root.bRepBodies:
            n = b.name
            if not n.startswith('LEAD_') or n.count('_') > (2 if n.startswith(('LEAD_PI_', 'LEAD_GPIO_', 'LEAD_USB_', 'LEAD_MIC_', 'LEAD_SPK_', 'LEAD_LCD_', 'LEAD_PIGTAIL_')) else 1):
                continue
            pts = set(); rad = set()
            for e in b.edges:
                g = e.geometry
                if g.curveType in (adsk.core.Curve3DTypes.Circle3DCurveType, adsk.core.Curve3DTypes.Arc3DCurveType):
                    w = W(g.center); pts.add((round(w[0]), round(w[1]), round(w[2]))); rad.add(round(g.radius * 10, 1))
            leads[n] = {'r': sorted(rad)[:3], 'n': len(pts), 'pts': sorted(pts, key=lambda q: (q[2], q[1]))[:40]}
        st['B'] = leads
        # C connectors (plug top, 19.8 above the component face; J2 at the board's bottom edge)
        cc = {}
        for k, (kx, ky) in CONN.items():
            xr = XCB - 45.0 + kx; zd = ZCB + 22.5 - ky
            w0 = W(Dp(xr, DF, zd)); w1 = W(Dp(xr, DF + 19.8, zd))
            cc[k] = [round(xr, 1), round(zd, 1)] + [round(v, 1) for v in w0] + [round(v, 1) for v in w1[1:]]
        st['C[x,Zd, x,y,z at board, y,z at plug top]'] = cc
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    status('f3a', st)


run(None)
