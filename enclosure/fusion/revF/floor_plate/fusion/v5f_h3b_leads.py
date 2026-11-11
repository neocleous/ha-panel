# rev F h3b (2026-11-11): step 3, block 3 - every lead routed to main board rev 3 at its site behind the display.
#   Each lead is a chain of cylinders and spheres through its nodes (as f3c). Node frames: B = board frame (u, v, w; w = 0 the door-side
#   face), S = slab (x_rel, depth, Zd), W = world (x_rel, y, z). ROUTES comes from the routes file fp/step3/h3_routes.json
#   ({name: [radius, [nodes]]}), so the routes are data and this script does not change when a node moves.
#   The bodies are added to the model (hidden, as the leads always were) and then measured by h3c: booleans of every lead against the
#   shell, door and plate on temporary bodies took about 15 s a lead, distances on model bodies take 0.1 s a pair.
#   First run for a name: the present LEAD_<name> -> LEAD_<name>_v49 (hidden backup), the new body added. Later runs (a node moved):
#   this pass's body of that name is deleted and replaced; the _v49 backup stays. Names in RETIRE are retired without a successor
#   (LEAD_GPIO_A: the nine Pi signal wires are now two bundles, LEAD_GPIO_A1 with three and LEAD_GPIO_A2 with six).
#   ONLY (global) restricts the leads built.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
ONLY = globals().get('ONLY', None)
RETIRE = globals().get('RETIRE', ['LEAD_GPIO_A'])
ORIG = ('LEAD_PIGTAIL_20V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_RADAR', 'LEAD_TOUCH', 'LEAD_BME680', 'LEAD_VEML', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V',
        'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_DSI', 'LEAD_PI_POWER', 'LEAD_USB_RESP')
ROUTES = json.load(open(os.path.join(S3, 'h3_routes.json')))


def pt(n):
    return Bp(n[1], n[2], n[3]) if n[0] == 'B' else (Dp(n[1], n[2], n[3]) if n[0] == 'S' else Wp(n[1], n[2], n[3]))


def rope(X, r, ps):
    body = None
    for i in range(len(ps) - 1):
        c = X.tbm.createCylinderOrCone(ps[i], r / 10.0, ps[i + 1], r / 10.0)
        body = c if body is None else X.uni(body, c)
        if i > 0:
            X.uni(body, X.tbm.createSphere(ps[i], (r + 0.05) / 10.0))
    return body


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        names = [n for n in ROUTES if (ONLY is None or n in ONLY)]
        out = {}; done = []
        like = X.body('LEAD_MIC_L') or X.body('LEAD_USB_RESP')
        for name in names:
            r, nodes = ROUTES[name]
            ps = [pt(n) for n in nodes]
            L = sum(ps[i].distanceTo(ps[i + 1]) for i in range(len(ps) - 1)) * 10.0
            body = rope(X, r, ps)
            old = X.body(name)
            b = X.root.bRepBodies.add(body); b.name = 'NEW_' + name
            try:
                b.appearance = (old or like).appearance
            except Exception:
                pass
            if old is not None:
                if name in ORIG and X.body(name + '_v49') is None:
                    X.retire(old, '_v49')
                else:
                    old.deleteMe()
            b.name = name; b.isLightBulbOn = False
            out[name[5:]] = round(L, 1); done.append(name)
        for n in RETIRE:
            old = X.body(n)
            if old is not None and n not in ROUTES and X.body(n + '_v49') is None:
                X.retire(old, '_v49')
        st['L'] = out
        st['added'] = {'names': done, 'dups': X.dups(), 'bodies': X.root.bRepBodies.count, 'leads now': sorted(b.name for b in X.root.bRepBodies if b.name.startswith('LEAD_') and not BACK.search(b.name))}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h3b', st)


run(None)
