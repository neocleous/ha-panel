# rev F i4a (2026-11-11): step 3 repeated, block 4 - read-only: what stands round the BME680 lead's last nodes (the lead is 0.03 from
#   the shell there). Needles 0.04 x 0.04 along the world y axis (y -60..-25) on a grid of world x and z; for each needle the y ranges
#   in which it is inside the shell (cropped), the right speaker box, the hood, the sensor's envelope and its foam.
#   XS, ZS (world mm) from the loader.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
XS = globals().get('XS', (-78, -76, -74, -72, -70, -68, -66, -64))
ZS = globals().get('ZS', (83, 85, 87, 89, 91, 93, 95))
YR = globals().get('YR', (-60.0, -25.0))
BODIES = globals().get('BODIES', ('shell', 'SPKBOX_R', 'BME_HOOD', 'BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door'))
TAG = globals().get('TAG', '')


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        c = cache()
        if 'crop_front_rear' not in c:
            t = X.cp(tcopy(X, 'HOUSING_F_front')); X.sec(t, X.dbox(-110, 110, 18, 140, -115, 35)); c['crop_front_rear'] = t
        if 'crop_bme_end' not in c:                      # the shell round the lead's end only: needles against it are quick
            t = X.cp(c['crop_front_rear']); X.sec(t, X.wbox(-90, -55, -62, -22, 76, 102)); c['crop_bme_end'] = t
        src = {'shell': c['crop_bme_end']}
        for n in BODIES:
            if n != 'shell':
                src[n] = tcopy(X, n)
        out = {}
        for z in ZS:
            for x in XS:
                nd = X.wbox(x - 0.02, x + 0.02, YR[0], YR[1], z - 0.02, z + 0.02)
                row = {}
                for n, f in src.items():
                    if not nd.boundingBox.intersects(f.boundingBox):
                        continue
                    t = X.cp(nd)
                    try:
                        X.tbm.booleanOperation(t, f, BT.IntersectionBooleanType)
                    except Exception:
                        row[n] = 'fail'; continue
                    iv = []
                    for l in t.lumps:
                        ys = [W(v.geometry)[1] for v in l.vertices]
                        iv.append([round(min(ys), 1), round(max(ys), 1)])
                    if iv:
                        row[n.replace('HOUSING_F_', '').replace('_env', '')] = sorted(iv)
                out['z%g x%g' % (z, x)] = row
        st['needles'] = out
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('i4a' + TAG, st)


run(None)
