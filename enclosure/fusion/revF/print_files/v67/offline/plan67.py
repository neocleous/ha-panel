"""Print files of version 67: per-project figures and totals per set, and the estimate for the four window projects from this
run's one-material stand-ins, by the re-check's method (recheck3/offline/r3_plan.py, PR17): the interface lines of the stand-in
become Support for ABS (1.16 g/cm3; for the slab all its support); two nozzle changes per layer that carries it; the X2D profile's
5 s and 45 mm3 of prime per change, the tower half of each material; Bambu ABS 1.04 g/cm3.
Usage: python3 plan67.py <out dir>   -> prints the tables and writes plan67.json beside this file"""
import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check67 import parse
A = math.pi * 0.875 ** 2
OUT = sys.argv[1]
SETS = {'PLA trial': ['T0_cal', 'T1_P1', 'T2_P2', 'T3_P3b', 'T4_P3a', 'T5_P5', 'T6_P4', 'T7_P6'],
        'ABS calibration': ['A0_cal'], 'ABS one-material plates': ['A1_P1', 'A2_P2', 'A6_P4', 'A7_P6']}
WINDOW = [('Adhesion test', 'A0s_adh_1m', 'interface'), ('P3b', 'A3s_P3b_1m', 'interface'), ('P3a', 'A4s_P3a_1m', 'interface'),
          ('P5', 'A5s_P5_1m', 'all')]


def hm(m):
    m = int(round(m)); return '%d h %02d' % (m // 60, m % 60) if m >= 60 else '%d min' % m


def res(job):
    r = json.load(open(os.path.join(OUT, job, 'result.json'))); pl = r['sliced_plates'][0]
    return {'t': pl['main_predication'] / 60.0, 'tp': pl['total_predication'] / 60.0, 'g': sum(f['total_used_g'] for f in pl['filaments']),
            'warn': (pl.get('warning_message') or '').replace('\n', ' ')}


def window(job, two):
    r = res(job); S, F, names, L, hdr = parse(os.path.join(OUT, job, 'plate_1.gcode'))
    nm = ('Support interface',) if two == 'interface' else ('Support', 'Support interface', 'Support transition')
    m = np.isin(F, [i for i, n in enumerate(names) if n in nm])
    vol = float(S[m, 5].sum() * A); nl = len(np.unique(np.round(S[m, 4], 3)))
    ch = 2 * nl; tower = ch * 45.0; dt = ch * 5.0 / 60.0
    sfa = (vol + tower / 2) * 1.16 / 1000.0; gabs = r['g'] - vol * 1.04 / 1000.0 + tower / 2 * 1.04 / 1000.0
    return {'stand_in': r, 'sfa_mm3': round(vol, 1), 'layers': nl, 'changes': ch, 'tower_cm3': round(tower / 1000, 2),
            't': r['t'] + dt, 'tp': r['tp'] + dt, 'abs_g': gabs, 'sfa_g': sfa}


if __name__ == '__main__':
    out = {}
    for name, jobs in SETS.items():
        rows = {j: res(j) for j in jobs}; out[name] = rows
        print('==', name)
        for j, r in rows.items():
            print('  %-8s %6.1f / %6.1f min  %-8s / %-8s %7.2f g  %s' % (j, r['t'], r['tp'], hm(r['t']), hm(r['tp']), r['g'], r['warn'][:70]))
        print('  total %s / %s, %.2f g' % (hm(sum(r['t'] for r in rows.values())), hm(sum(r['tp'] for r in rows.values())), sum(r['g'] for r in rows.values())))
    W = {lab: window(job, two) for lab, job, two in WINDOW}; out['window'] = W
    print('== window projects: one-material stand-in, and the two-material estimate')
    for lab, w in W.items():
        s = w['stand_in']
        print('  %-14s stand-in %6.1f / %6.1f min, %6.2f g | Support for ABS %5.0f mm3 on %3d layers, %3d changes, tower %.2f cm3 | about %s / %s, ABS %.1f g, SfA %.2f g'
              % (lab, s['t'], s['tp'], s['g'], w['sfa_mm3'], w['layers'], w['changes'], w['tower_cm3'], hm(w['t']), hm(w['tp']), w['abs_g'], w['sfa_g']))
    set_rows = [out['ABS one-material plates']['A1_P1'], out['ABS one-material plates']['A2_P2']]
    est = [W['P3b'], W['P3a'], W['P5']]
    T = sum(r['t'] for r in set_rows) + sum(w['t'] for w in est) + out['ABS one-material plates']['A6_P4']['t'] + out['ABS one-material plates']['A7_P6']['t']
    TP = sum(r['tp'] for r in set_rows) + sum(w['tp'] for w in est) + out['ABS one-material plates']['A6_P4']['tp'] + out['ABS one-material plates']['A7_P6']['tp']
    G = sum(r['g'] for r in out['ABS one-material plates'].values()) + sum(w['abs_g'] for w in est)
    SF = sum(w['sfa_g'] for w in est)
    print('== black ABS set (plates 1 to 7), with the window plates estimated: about %s / %s, about %.0f g black ABS, about %.1f g Support for ABS' % (hm(T), hm(TP), G, SF))
    G2 = G + out['ABS calibration']['A0_cal']['g'] + W['Adhesion test']['abs_g']; SF2 = SF + W['Adhesion test']['sfa_g']
    print('   with the calibration and the adhesion test: about %.0f g black ABS, about %.1f g Support for ABS; + a reprint of the shell and the screen plate: about %.0f g'
          % (G2, SF2, G2 + W['P3a']['abs_g'] + W['P3b']['abs_g']))
    out['abs_set'] = {'t': T, 'tp': TP, 'abs_g': G, 'sfa_g': SF, 'with_cal_adh_abs_g': G2, 'with_cal_adh_sfa_g': SF2}
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plan67.json'), 'w'), indent=1)
