# rc8_leads_export (block 3, point 5): meshes (0.01 mm, world mm) of the four lead bodies whose parts ride in with the display module
#   (LEAD_GPIO_A1, LEAD_GPIO_A2, LEAD_GPIO_B, LEAD_LCD_5V) and of MAIN_pcb, to find where the ride-in's 0.08 (10 out) lies.
#   READ-ONLY on the design: no volumes read beyond the 8 guard bodies (lesson 135). Writes exports/comp/<name>.stl, data/rc8_leads.json.
RC_NAMES = ['LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'MAIN_pcb']


def run(_context):
    X = RcCtx(); t0 = time.time(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    out['guard'] = rc_guard(X)[0]
    d = os.path.join(RC_DIR, 'exports', 'comp'); os.makedirs(d, exist_ok=True)
    out['comp'] = {}
    for n in RC_NAMES:
        b = X.body(n)
        if b is None:
            out['comp'][n] = None; continue
        P, T = rc_world_mesh(b, 0.01)
        out['comp'][n] = [rc_write_stl(os.path.join(d, n + '.stl'), P, T, n), b.isLightBulbOn]
    out['t_s'] = round(time.time() - t0, 1)
    rc_out(os.path.join(RC_DIR, 'data', 'rc8_leads.json'), out)
    rc_log('rc8_leads_export', 'run', {'comp': out['comp'], 't_s': out['t_s']})
    print(json.dumps({'comp': out['comp'], 't_s': out['t_s'], 'guard': out['guard']}, separators=(',', ':')))
