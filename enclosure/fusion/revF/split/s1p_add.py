# Block 1 picture: add AUD_ templates (exploded concept view). Changes the open document (templates only, deleted afterwards).
import adsk.core, adsk.fusion, sys, time
APP = {'grey': 'Plastic - Matte (Gray)', 'blue': 'Paint - Enamel Glossy (Blue)', 'red': 'Paint - Enamel Glossy (Red)',
       'yellow': 'Plastic - Matte (Yellow)', 'white': 'Plastic - Matte (White)'}
EXPL = 55.0                       # plate moved forward along the screen normal for the picture


def aud(X, tb, name, colour):
    b = X.root.bRepBodies.add(tb)
    b.name = 'AUD_' + name
    a = X.des.appearances.itemByName(APP[colour])
    if a is not None:
        b.appearance = a
    b.isLightBulbOn = True
    return b


def run(_context):
    t0 = time.time()
    k = sys.modules['v5f_k']; L = sys.modules['split_lib']; X = k.K()
    st = sys.modules.setdefault('split_state', type(sys)('split_state'))
    if not hasattr(st, 'vis0'):
        st.vis0 = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
    rs = X.tbm.copy(L.c['pic_rest'])
    X.dif(rs, X.dbox(50.0, 67.5, 14.0, 18.5, -70.0, -52.0))       # the two old box-top bosses, left floating by the cut
    X.dif(rs, X.dbox(-67.5, -50.0, 14.0, 18.5, -70.0, -52.0))
    pl = X.move_n(X.tbm.copy(L.c['pic_plate']), EXPL)
    made = [aud(X, rs, 'pic_rest', 'grey'), aud(X, pl, 'pic_plate', 'blue')]
    pos = {'TL': (70.0, 27.0), 'TR': (-70.0, 27.0), 'BL': (85.0, -82.0), 'BR': (-85.0, -82.0)}
    for tag, (x, up) in pos.items():
        made.append(aud(X, X.cyld(x, up, 4.0, 13.1, 19.4), 'pic_boss_' + tag, 'grey'))
        sc = X.cyld(x, up, 2.85, 7.35 - EXPL, 9.0 - EXPL)
        X.uni(sc, X.cyld(x, up, 1.5, 9.0 - EXPL, 17.0 - EXPL))
        made.append(aud(X, sc, 'pic_screw_' + tag, 'red'))
    for tag, x0, x1, xs in (('L', 54.6, 62.6, 58.6), ('R', -62.6, -54.6, -58.6)):
        tb = X.wbox(x0, x1, -7.5, -0.8, 76.0, 84.0)
        made.append(aud(X, tb, 'pic_tab_' + tag, 'yellow'))
        g = 1.0 if xs > 0 else -1.0                                  # the 10 deg line: nearer the middle toward the back
        sc = X.cyl((xs - g * 1.75, -9.5, 80.0), (xs + g * 0.6, 4.0, 80.0), 1.5)
        X.uni(sc, X.cyl((xs - g * 2.1, -11.5, 80.0), (xs - g * 1.75, -9.5, 80.0), 2.85))
        made.append(aud(X, sc, 'pic_tabscrew_' + tag, 'red'))
    keep = set(b.name for b in made) | {'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE'}
    for b in X.root.bRepBodies:
        on = b.name in keep
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    k.cam(X, (430.0, 560.0, 420.0), (0.0, 10.0, 95.0), ext=33.0, up=(0, 0, 1))
    print('added', len(made), 't', round(time.time() - t0, 1))
