# rev F h3f (2026-11-11): step 3, block 3 - read-only: lead against lead (overlap in mm3 where two leads' bodies share space), each
#   lead's length from its body (volume / cross-section, a check on the node sum), and for every lead the three smallest clearances to
#   bodies it does not end in (from h3c's cache).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
RAD = {'LEAD_PIGTAIL_20V': 1.6, 'LEAD_SPK_L': 1.6, 'LEAD_SPK_R': 1.6, 'LEAD_RADAR': 1.3, 'LEAD_TOUCH': 1.2, 'LEAD_BME680': 1.5, 'LEAD_VEML': 1.5, 'LEAD_GPIO_A1': 1.5,
       'LEAD_GPIO_A2': 2.0, 'LEAD_GPIO_B': 1.7, 'LEAD_LCD_5V': 1.5, 'LEAD_MIC_L': 1.0, 'LEAD_MIC_R': 1.0, 'LEAD_DSI': 1.5, 'LEAD_PI_POWER': 2.5, 'LEAD_USB_RESP': 1.7}


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        leads = [b for b in current(X, leads=True) if b.name.startswith('LEAD_')]
        st['n'] = len(leads)
        st['len_from_volume'] = {b.name[5:]: round(X.vol(b) / (math.pi * RAD[b.name] ** 2), 1) for b in leads}
        pairs = {}
        for i, a in enumerate(leads):
            for b in leads[i + 1:]:
                if not a.boundingBox.intersects(b.boundingBox):
                    continue
                v = xvol(X, X.cp(a), X.cp(b))
                if abs(v) > 0.05:
                    pairs[a.name[5:] + '~' + b.name[5:]] = round(v, 1)
        st['pairs'] = pairs
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h3f', st)


run(None)
