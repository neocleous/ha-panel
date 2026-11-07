# HA panel print audit, block 2 (P9, printed-component fits): minimum distance from each printed body to each current
#   component body whose box comes within 1 mm, with Fusion's measure manager (B-rep, exact); components closer than
#   PA3_EXPORT_MM are also meshed (0.01 mm chordal) and written as world-mm STLs for the face-pair analysis offline.
#   Read-only: the design document is read WITHOUT being activated (no change of the active document, view or visibility).
#   Component list: the model audit brief's current parts (Pi, main board, ReSpeaker, power/USB, speakers, touch PCB,
#   radar, sensors, feet, LCD module bodies), superseded copies, leads (flexible), keep-outs, tools and references excluded.
#   Writes print_audit/data/pa3_compfits.json after every pair (partial results survive) and exports/comp/<name>.stl.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
PA3_OUT = os.path.join(PA_DIR, 'data', 'pa3_compfits.json')
PA3_EXPORT_MM = 0.6
PA3_EXACT = ['PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env',
             'RESP_pcb', 'RESP_mic_env', 'RESP_top_env', 'RESP_usbc_plug_env', 'PD_5807_env', 'PIPWR_a_env',
             'USBA_plug_env', 'USBA_cable_env', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'LD2410C_env_F', 'BME680_env',
             'FOAM_bme_env', 'FOAM_bme_top_env', 'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env',
             'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
PA3_PREFIX = ['LCD_']                       # LCD module bodies (glass, panel, PCB, connectors, standoffs, headers)


def pa3_gap(a, b):
    d = [max(0.0, b.minPoint.x - a.maxPoint.x, a.minPoint.x - b.maxPoint.x),
         max(0.0, b.minPoint.y - a.maxPoint.y, a.minPoint.y - b.maxPoint.y),
         max(0.0, b.minPoint.z - a.maxPoint.z, a.minPoint.z - b.maxPoint.z)]
    return math.sqrt(sum(v * v for v in d)) * 10


def run(_context):
    app = adsk.core.Application.get(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'active_before': app.activeDocument.name}
    t0 = time.time()
    try:
        doc = [d for d in app.documents if d.name == PA_DOC][0]
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        allb = [root.bRepBodies.item(i) for i in range(root.bRepBodies.count)]
        byname = {}
        for b in allb:
            byname.setdefault(b.name, b)
        # guard (same rule as pa_guard, without Ctx)
        bad = []
        for k, v in PA_GUARD.items():
            b = byname.get(k)
            if b is None or abs(b.volume - v) > PA_TOL:
                bad.append(k)
        if byname['MAIN_BRACKET'].lumps.count != 2:
            bad.append('MAIN_BRACKET lumps')
        if doc.isModified:
            bad.append('document modified')
        out['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD: %s - stop' % bad)
        comps = [b for b in allb if b.name in PA3_EXACT or any(b.name.startswith(p) for p in PA3_PREFIX)]
        out['components'] = [[b.name, round(b.volume, 4), b.isLightBulbOn] for b in comps]
        printed = [(k, byname[k]) for k in PA_GUARD]
        mm = app.measureManager
        rows = []; out['rows'] = rows
        for (pn, pb) in printed:
            pbb = pb.boundingBox
            for cb in comps:
                g = pa3_gap(pbb, cb.boundingBox)
                if g >= 1.0:
                    continue
                t1 = time.time()
                try:
                    r = mm.measureMinimumDistance(pb, cb)
                    d = r.value * 10
                    p1 = [round(v, 2) for v in pa_wpt(r.positionOne)]; p2 = [round(v, 2) for v in pa_wpt(r.positionTwo)]
                    rows.append([pn, cb.name, round(d, 3), p1, p2, round(time.time() - t1, 1)])
                except Exception:
                    rows.append([pn, cb.name, None, traceback.format_exc().splitlines()[-1][:120], None, round(time.time() - t1, 1)])
                out['t_s'] = round(time.time() - t0, 1)
                pa_out(PA3_OUT, out)
        # meshes of the components that come closer than PA3_EXPORT_MM to any printed body
        os.makedirs(os.path.join(PA_DIR, 'exports', 'comp'), exist_ok=True)
        near = sorted(set(r[1] for r in rows if r[2] is not None and r[2] < PA3_EXPORT_MM))
        out['exported'] = {}
        for cb in comps:
            if cb.name not in near:
                continue
            P, T = pa_world_mesh(cb, 0.01)
            safe = re.sub(r'[^A-Za-z0-9_.-]+', '_', cb.name).strip('_')
            path = os.path.join(PA_DIR, 'exports', 'comp', safe + '.stl')
            out['exported'][cb.name] = [safe, pa_write_stl(path, P, T, safe)]
            pa_out(PA3_OUT, out)
        out['t_s'] = round(time.time() - t0, 1)
        out['done'] = True
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    out['active_after'] = app.activeDocument.name
    pa_out(PA3_OUT, out)
    log('pa3_compfits', 'run', {'n': len(out.get('rows', [])), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({k: out.get(k) for k in ('t_s', 'guard_bad', 'done', 'FAIL', 'active_before', 'active_after')},
                     separators=(',', ':')))
