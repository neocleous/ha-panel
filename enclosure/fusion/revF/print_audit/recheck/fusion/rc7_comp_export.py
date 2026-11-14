# rc7_comp_export (block 1/3): meshes (0.01 mm) of the component bodies that the window, fits and ride-in checks need, in world mm,
#   and the names of all 392 bodies with their visibility (to find magnets, inserts, envelopes). READ-ONLY on the design.
#   Writes print_audit_recheck/exports/comp/<name>.stl and data/rc7_comp.json.
RC_COMP = ['DRV_screw_heads_env', 'SPK_L', 'SPK_R', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'PI5_F', 'PD_5807_env', 'RESP_pcb',
           'MAIN_pcb', 'LCD_pcb_76x110', 'LCD_glass', 'TOUCH_PCB', 'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B', 'LEAD_LCD_5V',
           'LEAD_USB_RESP', 'LEAD_DSI', 'LEAD_MIC_L', 'LEAD_MIC_R', 'RESP_usbc_plug_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
           'LCD_M2.5_standoff_d9.0', 'LCD_Pi_standoff_d15.2', 'LD2410C_env_F', 'BME680_env', 'USBA_plug_env']


def run(_context):
    X = RcCtx(); t0 = time.time(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    out['guard'] = rc_guard(X)[0]
    d = os.path.join(RC_DIR, 'exports', 'comp'); os.makedirs(d, exist_ok=True)
    out['all'] = [[b.name, b.isLightBulbOn, round(b.volume * 1000.0, 2)] for b in X.root.bRepBodies]
    out['comp'] = {}
    for n in RC_COMP:
        b = X.body(n)
        if b is None:
            out['comp'][n] = None; continue
        P, T = rc_world_mesh(b, 0.01)
        nt = rc_write_stl(os.path.join(d, n + '.stl'), P, T, n)
        out['comp'][n] = [nt, round(b.volume * 1000.0, 3)]
        if time.time() - t0 > 40:
            out['stopped_after'] = n; break
    out['t_s'] = round(time.time() - t0, 1)
    rc_out(os.path.join(RC_DIR, 'data', 'rc7_comp.json'), out)
    print(json.dumps({'n_all': len(out['all']), 'comp': out['comp'], 't_s': out['t_s'], 'stopped': out.get('stopped_after')}, separators=(',', ':')))
