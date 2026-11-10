# rev F g2d (2026-11-10): step 1, blocks 2 and 3 - read-only: tool access with the audit's method (aud_common.Aud.line: stations every 5 mm
# along the tool axis, minimum distance to every body present, margin = distance - tool radius; "grip" = with the hand on the handle).
# GROUP (exec global): 'cap', 'box', 'under', 'clip', 'bench', 'inplace'. Results: fp/g2d_<group>_status.json.
# Tools: 2.0 key = 2.4 x 101 + short-arm swing dia 34.4; 2.5 key = 3.0 x 112 + swing dia 39; precision screwdriver 3 x 60 + 13 x 97.
import os, json, math, time, traceback
exec(compile(open(os.path.expanduser('~/Documents/ha_asm_audit/aud_common.py'), encoding='utf-8').read(), 'aud_common', 'exec'))
FP = os.path.expanduser('~/Documents/HA_panel_renders/fp')
GROUP = globals().get('GROUP', 'cap')
KEY20 = [(2.4, 101.0), (34.4, 4.0)]; KEY20G = [(2.4, 101.0), (55.0, 4.0)]
KEY25 = [(3.0, 112.0), (39.0, 4.0)]; KEY25G = [(3.0, 112.0), (60.0, 4.0)]
MICRO = [(3.0, 60.0), (13.0, 97.0)]; MICROG = [(3.0, 60.0), (40.0, 97.0)]
rad = math.radians
UNIT = ['FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env',
        'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
CRAD = ['CRADLE_5807']; PD = ['PD_5807_env', 'PIPWR_a_env']
SHELL = ['HOUSING_F_front']
TOUCH = ['TOUCH_PCB', 'KO_touch_back', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R']
MODULE = ['SLAB_frame', 'LCD_*', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env']
GPIO = ['GPIO_plugA_env', 'GPIO_plugB_env']
SENS = ['BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'BME_HOOD', 'LD2410C_env_F']
CAPS = ['HOUSING_F_cap', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env']
DOOR = ['HOUSING_F_door', 'GROMMET_usbc_F']


def main():
    st = {}; t0 = time.time()
    try:
        A = Aud()
        import re
        back = re.compile(r'(_v42|_[a-e]\d+[a-z0-9]*| \(\d+\))$')
        leads = [n for n in A.cur if n.startswith('LEAD_') and not back.search(n)]
        st['n_leads'] = len(leads)
        ALLIN = SHELL + UNIT + CRAD + PD + TOUCH + MODULE + GPIO + SENS + CAPS

        def probe(o, u, secs, gsecs, names, with_leads=True):
            bods = A.present(names + (leads if with_leads else []))
            r = A.line(o, u, secs, bods, st0=2.0, step=5.0)
            total = sum(q[1] for q in secs)
            out = {'tool': [round(r['free'], 0) if r['free'] < total else 'free', r['min'][0], r['min'][1], r['min'][2]]}
            if gsecs:
                g = A.line(o, u, gsecs, bods, st0=2.0, step=5.0)
                out['hand'] = [g['min'][0], g['min'][1], g['min'][2]]
            if with_leads:
                uu = unit(u); best = (99.0, 0, '')
                bounds = []; s = 0.0
                for dia, L in secs:
                    bounds.append((s, s + L, dia / 2.0)); s += L
                sx = 2.0
                while sx <= total + 0.01:
                    rr = [q for q in bounds if q[0] <= sx <= q[1] + 0.01][-1][2]
                    d, n, pt = A.near(Dr(o[0] + uu[0] * sx, o[1] + uu[1] * sx, o[2] + uu[2] * sx), bods, leads=True)
                    if d - rr < best[0]:
                        best = (round(d - rr, 1), sx, n)
                    sx += 5.0
                out['lead'] = list(best) if best[0] < 20 else 'none within 20'
            return out

        res = {}
        if GROUP == 'cap':
            lanes = {'SR': ((-43.36, -32.85), (0.152, -0.437, -0.886)), 'BR': ((-25.91, -37.8), (0.039, -0.415, -0.909)),
                     'BL': ((25.91, -37.8), (-0.039, -0.415, -0.909)), 'SL': ((43.36, -32.85), (-0.152, -0.437, -0.886))}
            for n, ((x, y), u) in lanes.items():
                res['cap %s lane, 2.0 key, button head' % n] = probe((x, y, 167.85), u, KEY20, KEY20G, ALLIN)
                res['cap %s lane, 2.5 key, cap head' % n] = probe((x, y, 166.5), u, KEY25, KEY25G, ALLIN)
                st['res'] = res; json.dump(st, open(os.path.join(FP, 'g2d_%s_status.json' % GROUP), 'w'), separators=(',', ':'))
            for name, x, sgn in (('SR', -43.36, 1), ('SL', 43.36, -1)):
                for th in (23.0, 25.0):
                    for ps in (0, 10, 20):
                        u = (sgn * math.sin(rad(th)) * math.sin(rad(ps)), -math.sin(rad(th)) * math.cos(rad(ps)), -math.cos(rad(th)))
                        res['cap %s at %d deg, %d deg inboard, 2.0 key' % (name, th, ps)] = probe((x, -32.85, 167.85), u, KEY20, KEY20G, ALLIN)
                st['res'] = res; json.dump(st, open(os.path.join(FP, 'g2d_%s_status.json' % GROUP), 'w'), separators=(',', ':'))
        elif GROUP == 'box':
            for sx in (1, -1):
                res['box top x%+d, 2.0 key, button head' % (58 * sx)] = probe((58.0 * sx, -8.25, 79.5), (0, -1, 0), KEY20, KEY20G, ALLIN)
                res['box top x%+d, 2.5 key, cap head' % (58 * sx)] = probe((58.0 * sx, -9.6, 79.5), (0, -1, 0), KEY25, KEY25G, ALLIN)
                for ps in (2, 4, 6, 8, 10, 14):
                    for dz in (-5, 0, 5):
                        u = (-sx * math.sin(rad(ps)) * math.cos(rad(dz)), -math.cos(rad(ps)) * math.cos(rad(dz)), math.sin(rad(dz)))
                        res['box top x%+d, 2.0 key %d deg inboard, %d deg up' % (58 * sx, ps, dz)] = probe((58.0 * sx, -8.25, 79.5), u, KEY20, KEY20G, ALLIN)
                st['res'] = res; json.dump(st, open(os.path.join(FP, 'g2d_%s_status.json' % GROUP), 'w'), separators=(',', ':'))
        elif GROUP == 'under':
            for x, y in ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0)):
                res['door (%g, %g), 2.0 key from below' % (x, y)] = probe((x, y, -0.65), (0, 0, -1), KEY20, KEY20G, ALLIN + DOOR, False)
            for x, y in ((51.0, -14.0), (64.0, -45.0), (-51.0, -14.0), (-72.0, -38.0)):
                res['box floor (%g, %g), 2.0 key from below' % (x, y)] = probe((x, y, -0.65), (0, 0, -1), KEY20, KEY20G, UNIT, False)
        elif GROUP == 'clip':
            states = {'unit in, touch board and clips, nothing else': SHELL + UNIT + CRAD + PD + TOUCH,
                      'plus Pi header plugs': SHELL + UNIT + CRAD + PD + TOUCH + GPIO,
                      'everything in, door off': ALLIN}
            for sn, names in states.items():
                for sx in (1, -1):
                    side = 'left' if sx > 0 else 'right'
                    k = '%s | %s clip' % (sn, side)
                    res[k + ' | short arm in the screw'] = probe((38.85 * sx, -6.1, 38.0), (-sx, 0, 0), [(2.4, 16.0)], None, names, sn.startswith('every'))
                    for ph in (0, 30, 60, 90):
                        res[k + ' | lever %d (0 = back, 90 = up)' % ph] = probe((22.85 * sx, -6.1, 38.0), (0, -math.cos(rad(ph)), math.sin(rad(ph))), [(2.4, 101.0)], None,
                                                                             names, sn.startswith('every'))
                    for th in (15, 25):
                        for nm, (ay, az) in (('up', (0, 1)), ('back', (-1, 0)), ('up-back', (-0.7071, 0.7071))):
                            u = (-sx * math.cos(rad(th)), ay * math.sin(rad(th)), az * math.sin(rad(th)))
                            res[k + ' | ball end %d deg %s' % (th, nm)] = probe((38.85 * sx, -6.1, 38.0), u, KEY20, None, names, sn.startswith('every'))
                st['res'] = res; json.dump(st, open(os.path.join(FP, 'g2d_%s_status.json' % GROUP), 'w'), separators=(',', ':'))
        elif GROUP in ('bench', 'inplace'):
            base = UNIT + CRAD if GROUP == 'bench' else ALLIN
            wl = GROUP == 'inplace'
            for x in (6.5, -1.5):
                nm = [n for n in base if n not in ('PD_5807_env',)]
                res['cradle screw x%g, 2.0 key, upright' % x] = probe((x, -72.5, 17.65), (0, 0, 1), KEY20, KEY20G, nm, wl)
                res['cradle screw x%g, 2.0 key, 10 deg back' % x] = probe((x, -72.5, 17.65), (0, -math.sin(rad(10)), math.cos(rad(10))), KEY20, KEY20G, nm, wl)
            for x, y in ((-39.65, -5.5), (18.35, -5.5), (-39.65, -54.5), (18.35, -54.5)):
                res['Pi screw (%g, %g), 2.0 key, upright' % (x, y)] = probe((x, y, 12.5), (0, 0, 1), KEY20, KEY20G, base, wl)
                if GROUP == 'inplace':
                    res['Pi screw (%g, %g), 2.0 key, 20 deg back' % (x, y)] = probe((x, y, 12.5), (0, -math.sin(rad(20)), math.cos(rad(20))), KEY20, KEY20G, base, wl)
            for x in (-7.49, 7.75):
                res['inlet board screw x%g, screwdriver through the roof slot' % x] = probe((x, -81.16, 23.9), (0, 0, 1), MICRO, MICROG, base + PD, wl)
            if GROUP == 'bench':
                for sx in (1, -1):
                    for x in (52.75, 88.25):
                        for z in (10.25, 45.75):
                            res['driver screw (%g, z %g), 2.0 key from the front' % (sx * x, z)] = probe((sx * x, 1.65, z), (0, 1, 0), KEY20, KEY20G, UNIT, False)
        st['res'] = res
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(FP, 'g2d_%s_status.json' % GROUP), 'w'), separators=(',', ':'))


main()
