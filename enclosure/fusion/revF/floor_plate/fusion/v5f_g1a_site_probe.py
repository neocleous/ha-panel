# rev F g1a (2026-11-10): step 1, block 1 - read-only probe of the main board's site behind the display.
#   A  the key paths (KO_K5_*, KO_capkey_*) as axes in the slab frame (x_rel, depth d behind the glass, Zd)
#   B  free depth behind the plane d 28: first face of a fixed body met going toward the door, on a 5 mm grid (x -55..55, Zd -75..10)
#   C  what stands in front of the plane d 31 (ReSpeaker, carrier, display parts, wall): the last face met going toward the display
# Rays answer for every body on the line (lesson 89): only the named bodies are read.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
REAR = {'HOUSING_F_door': 'D', 'HOUSING_F_front': 'F', 'HOUSING_F_cap': 'C', 'SPKBOX_L': 'L', 'SPKBOX_R': 'R', 'BME_HOOD': 'B', 'BME680_env': 'B',
        'FOAM_bme_env': 'B', 'FOAM_bme_top_env': 'B', 'LD2410C_env_F': 'r', 'VEML_env': 'V', 'MIC_strip_L_env': 'M', 'MIC_strip_R_env': 'M',
        'SENSOR_strip_L': 'M', 'SENSOR_strip_R': 'M', 'CRADLE_5807': 'c', 'PD_5807_env': 'P', 'PI5_F': 'p', 'PI5_F_cooler': 'k', 'GPIO_plugA_env': 'g',
        'GPIO_plugB_env': 'g', 'PIPWR_a_env': 'w', 'USBA_plug_env': 'u', 'USBA_cable_env': 'u', 'FLOOR_PLATE': 'f', 'GROMMET_usbc_F': 'G', 'KO_K7_fan': 'K'}
FRONT = {'RESP_pcb': 'r', 'RESP_top_env': 't', 'RESP_mic_env': 'm', 'RESP_CARRIER': 'c', 'RESP_usbc_plug_env': 'u', 'HOUSING_F_front': 'F',
         'LCD_pcb_76x110': 'l', 'LCD_components_env_d8.8': 'l', 'LCD_2x2_header_d15.4': 'h', 'LCD_pins_d16.0': 'h', 'LCD_pogo_header_d14.1': 'h',
         'LCD_Pi_standoff_d15.2': 's', 'LCD_DSI_conn_d9.3': 'l', 'LCD_touchFPC_conn_d9.3': 'l', 'LCD_panelFPC_conn_d9.5': 'l'}
XS = list(range(-55, 56, 5)); ZS = list(range(10, -76, -5))


def slab(p):
    return (p.x * 10 - XC, -p.y * 10, p.z * 10)


def run(_context):
    st = {'x': XS}
    t0 = time.time()
    try:
        X = K()
        ko = {}
        for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR'):
            b = X.body(n)
            for f in b.faces:
                g = f.geometry
                if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
                    o = slab(g.origin); a = g.axis
                    vs = [slab(v.geometry) for v in b.vertices]
                    ds = [v[1] for v in vs]
                    ko[n] = {'r': round(g.radius * 10, 2), 'p': [round(q, 1) for q in o], 'dir': [round(a.x, 4), round(-a.y, 4), round(a.z, 4)],
                             'd_range': [round(min(ds), 1), round(max(ds), 1)], 'zd_range': [round(min(v[2] for v in vs), 1), round(max(v[2] for v in vs), 1)]}
                    break
        st['KO[r, point, dir(x,d,Zd), d range, Zd range]'] = ko
        status('g1a', st)

        def first(x, d0, zd, sgn, names):
            hp = adsk.core.ObjectCollection.create()
            ents = X.root.findBRepUsingRay(Dp(x, d0, zd), V3(0, -sgn, 0), adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
            best = None
            for i in range(ents.count):
                nm = ents.item(i).body.name
                if nm in names:
                    dd = -hp.item(i).y * 10
                    if best is None or (dd - best[0]) * sgn < 0:
                        best = (dd, names[nm])
            return best
        rear = {}; front = {}
        for zd in ZS:
            r1 = []; r2 = []
            for x in XS:
                h = first(x + 0.3, 28.0, zd + 0.2, 1, REAR)
                r1.append('%.0f%s' % (h[0], h[1]) if h else '-')
                h = first(x + 0.3, 31.0, zd + 0.2, -1, FRONT)
                r2.append('%.0f%s' % (h[0], h[1]) if h else '-')
            rear['%d' % zd] = ' '.join(r1); front['%d' % zd] = ' '.join(r2)
            st['rear'] = rear; st['front'] = front; st['t'] = round(time.time() - t0, 1); status('g1a', st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g1a', st)


run(None)
