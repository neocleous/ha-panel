# rev F audit-response d4f (2026-11-06), read-only: checks after d4c / d4e. Writes ~/Documents/HA_panel_renders/d4f_sections.json.
#   1. overlap of every changed region with every current part (visible bodies + the hidden envelopes): new grommet, cradle,
#      the door's bottom band (z 2.0–3.8) and pin region, the front's floor web + boss pads;
#   2. leftover small cylinders of the door round the old / new pin holes; grommet against the cloth render body;
#   3. section loops for the checkpoint pictures.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d4f_sections.json')
GUARD = {'HOUSING_F_door': 51.1616, 'HOUSING_F_front': 236.2249, 'GROMMET_usbc_F': 0.5062, 'CRADLE_5807': 2.1709}
SKIP_PREFIX = ('REF_', 'INNER_', 'TOOL_', 'RENDER_', 'sk_', 'HOUSING_E', 'V11')
ALWAYS = ('PD_5807_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'KO_5807_pigtail', 'LEAD_PIGTAIL_20V', 'MAIN_front_env', 'MAIN_back_env')
BOSSES = ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0))
G = ['HOUSING_F_door', 'GROMMET_usbc_F', 'CRADLE_5807', 'PD_5807_env', 'HOUSING_F_front']
PLANES2 = {
    'K_x0': ('x', 0.0, (-90.0, -74.0, 8.0, 36.0), G),
    'K_y-84': ('y', -84.0, (-20.0, 20.0, 8.0, 36.0), ['GROMMET_usbc_F', 'HOUSING_F_door', 'CRADLE_5807']),
    'K_y-85': ('y', -85.0, (-20.0, 20.0, 8.0, 36.0), ['GROMMET_usbc_F', 'CRADLE_5807']),
    'K_x13.85': ('x', 13.85, (-90.0, -76.0, 8.0, 36.0), ['HOUSING_F_door', 'GROMMET_usbc_F']),
    'K_z20.6': ('z', 20.6, (-20.0, 20.0, -90.0, -74.0), ['HOUSING_F_door', 'GROMMET_usbc_F', 'CRADLE_5807']),
    'K_x0_low': ('x', 0.0, (-86.0, -66.0, 0.0, 10.0), ['HOUSING_F_door', 'HOUSING_F_front', 'CRADLE_5807']),
    'K_x-19': ('x', -19.0, (-86.0, -68.0, 0.0, 12.0), ['HOUSING_F_door', 'HOUSING_F_front']),
    'K_z3.4': ('z', 3.4, (-90.0, 90.0, -92.0, -50.0), ['HOUSING_F_door', 'HOUSING_F_front']),
    'K_z11': ('z', 11.0, (-14.0, 14.0, -86.0, -62.0), ['CRADLE_5807', 'HOUSING_F_front']),
    'K_z5': ('z', 5.0, (-14.0, 14.0, -86.0, -62.0), ['HOUSING_F_front']),
    'K_z16.8': ('z', 16.8, (-14.0, 14.0, -86.0, -56.0), ['CRADLE_5807']),
}


def parts(X, skip=()):
    res = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n in skip or n.startswith(SKIP_PREFIX) or n.endswith('_tmp'):
            continue
        if b.isLightBulbOn or n in ALWAYS:
            res.append(b)
    return res


def bb_hit(a, b):
    return not (a.maxPoint.x < b.minPoint.x or b.maxPoint.x < a.minPoint.x or a.maxPoint.y < b.minPoint.y or
                b.maxPoint.y < a.minPoint.y or a.maxPoint.z < b.minPoint.z or b.maxPoint.z < a.minPoint.z)


def overlaps(X, t, skip=()):
    res = {}
    for b in parts(X, skip):
        if not bb_hit(t.boundingBox, b.boundingBox):
            continue
        v = vol_x(X, t, X.tbm.copy(b))
        if v > 0:
            res[b.name] = v
    return res or 'all 0'


def small_cyls(b, box):
    rows = []
    for f in b.faces:
        g = f.geometry
        if g.objectType != adsk.core.Cylinder.classType() or g.radius * 10 > 1.3:
            continue
        o = g.origin; ax = g.axis; ax.normalize()
        ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices] or [0.0]
        tm = (min(ts) + max(ts)) / 2; c = P3(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
        cw = (c.x * 10 - XC, wy(c), wz(c))
        if box[0] <= cw[0] <= box[1] and box[2] <= cw[1] <= box[3] and box[4] <= cw[2] <= box[5]:
            rows.append([round(2 * g.radius * 10, 3), [round(v, 2) for v in cw], round(max(ts) - min(ts), 3), round(f.area * 100, 3)])
    return rows


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        ov = {}
        ov['grommet'] = overlaps(X, tb_copy(X, 'GROMMET_usbc_F'), ('GROMMET_usbc_F',))
        ov['cradle'] = overlaps(X, tb_copy(X, 'CRADLE_5807'), ('CRADLE_5807',))
        band = tb_copy(X, 'HOUSING_F_door'); inter(X, band, X.wbox(XC - 100, XC + 100, -100, -40, 2.0, 3.8))
        ov['door_band'] = overlaps(X, band, ('HOUSING_F_door',))
        pinr = tb_copy(X, 'HOUSING_F_door'); inter(X, pinr, X.wbox(XC - 16.5, XC + 16.5, -86.0, -78.0, 18.0, 23.5))
        ov['door_pins'] = overlaps(X, pinr, ('HOUSING_F_door',))
        reg = X.wbox(XC + 0.5, XC + 4.5, -74.7, -70.3, 2.3, 8.1)
        for (x, y) in BOSSES:
            X.union(reg, X.wcyl_z(XC + x, y, 4.3, 2.3, 2.9))
        fr = tb_copy(X, 'HOUSING_F_front'); inter(X, fr, reg)
        ov['front_web_pads'] = overlaps(X, fr, ('HOUSING_F_front',))
        out['overlaps'] = ov
        out['t_ov'] = round(time.time() - t0, 1)
        out['door_small_cyls_pin_region'] = small_cyls(X.body('HOUSING_F_door'), (-16.0, 16.0, -86.0, -78.0, 18.0, 23.5))
        out['grommet_small_cyls'] = small_cyls(X.body('GROMMET_usbc_F'), (-16.0, 16.0, -90.0, -70.0, 10.0, 34.0))
        fd = X.body('RENDER_FABRIC_door')
        out['fabric_door'] = None if fd is None else {'visible': fd.isLightBulbOn, 'x_grommet_mm3': vol_x(X, tb_copy(X, 'RENDER_FABRIC_door'), tb_copy(X, 'GROMMET_usbc_F')),
                                                      'x_door_mm3': vol_x(X, tb_copy(X, 'RENDER_FABRIC_door'), tb_copy(X, 'HOUSING_F_door'))}
        out['t_misc'] = round(time.time() - t0, 1)
        sec = sections(X, PLANES2)
        json.dump(sec, open(OUTF, 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d4f_checks', 'checks', out)
    print(json.dumps(out, separators=(',', ':')))
