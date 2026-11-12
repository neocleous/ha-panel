# rev F k4b (2026-11-12): fix pass, block 4 - corrections and additions to k4a. Run through k.step(sha, name, h256, k4=<k4a's namespace>).
#   1. LEADPART: the parts of the leads that ride in with the display module. k4a's boxes reached 6 past the opening's edges and so
#      took in lead that hangs free at that step, and the lowest turn of the microphone leads' coils. The boxes here end at the
#      notch floors (v -32.9 and +32.9), take only the first run of each microphone lead, the DSI ribbon above the lower edge,
#      and the USB lead's first 6 behind its plug. apply() puts them into k4a's table and drops the cached parts and results.
#   2. way_out(): the plate unit with the touch clips on its boxes, on its way out for service, with the display module, the cap
#      and the touch board in the shell.
LOW = (-60.0, 60.0, -32.9, 36.0, -14.0, -1.0)
LEADPART = {'LEAD_GPIO_A1': LOW, 'LEAD_GPIO_A2': LOW, 'LEAD_GPIO_B': LOW, 'LEAD_LCD_5V': LOW,
            'LEAD_MIC_R': (-36.0, -26.5, -36.0, 32.9, -14.0, -1.0), 'LEAD_MIC_L': (31.0, 39.0, -36.0, 32.9, -14.0, -1.0),
            'LEAD_DSI': (40.0, 62.0, -29.0, 36.0, -16.0, 10.0), 'LEAD_USB_RESP': (60.0, 95.0, -36.0, 36.0, -16.0, -1.0)}      # board frame


def apply(tag):
    k4['LEADPART'].clear(); k4['LEADPART'].update(LEADPART)
    for q in [q for q in k.c if isinstance(q, tuple) and q[0] == 'k4lp']:
        del k.c[q]
    res = k.c.setdefault(('k4ride', tag), {})
    for q in [q for q in res if q[0].startswith('part of')]:
        del res[q]


def way_out(X, tag, slide=(0.25, 0.5, 0.75, 1.0, 1.3, 1.5), behind=(1.3, 1.5), lift=(0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30, 40, 60, 80)):
    res = k.c.setdefault(('k4out', tag), {})
    moving = k4['names_of'](X, 'UNIT', 'USBA') + ['TOUCH_CLIP_L', 'TOUCH_CLIP_R']
    fixed = [n for n in k4['names_of'](X, 'SHELL', 'RADAR', 'BME', 'MODULE', 'CAP') if n not in ('SLAB_frame', 'LCD_glass', 'LCD_panel_body')]
    fixed += ['TOUCH_PCB', 'TOUCH_components_env']
    pos = [(b, 0.0) for b in slide] + [(b, float(h)) for b in behind for h in lift]
    left = 0
    for n in moving:
        for i, p in enumerate(k4['pieces'](X, tag, n)):
            todo = [q for q in pos if (n, i) + q not in res]
            if not todo:
                continue
            if k.late():
                left += len(todo); continue
            qb = ('k4wb', tag, n, i)
            if qb not in k.c:
                k.c[qb] = k.wbb(X, p)
            wb = k.c[qb]
            box = (wb[0] - 1.0, wb[1] + 1.0, wb[2] - 2.6, wb[3] + 1.0, wb[4] - 81.0, wb[5] + 1.0)
            for b, h in todo:
                if k.late():
                    left += 1; continue
                t = X.move(X.tbm.copy(p), 0.0, -b, -h)
                hit = {}
                for f in fixed:
                    v = sum(X.xv(t, c) for c in k4['crop'](X, tag, f, box))
                    if abs(v) > 0.0005:
                        hit[f] = round(v, 3)
                res[(n, i, b, h)] = hit
    return res, left
