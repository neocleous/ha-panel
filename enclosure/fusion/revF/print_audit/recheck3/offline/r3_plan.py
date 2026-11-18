"""recheck3: the print plan's totals from the recommended slices, and the estimate of the two-material plates (the command line cannot slice them: PR10, PR17).
   Estimate, as PR17: the interface lines of the one-material stand-in become Support for ABS (1.16 g/cm3); two nozzle changes per layer that carries interface
   (support for the slab: all of it is Support for ABS); the X2D profile's 5 s and 45 mm3 of prime per change, the tower half of each material. ABS 1.04 g/cm3."""
import json, numpy as np
from r3_gq import G
GD = '/mnt/user-data/uploads/HA_panel_renders/print_audit_recheck3/slicer/out'
PLAN = [('P1', 'H1s_P1_solid', None), ('P2', 'H2_P2', None), ('P3b', 'F3_P3b', 'interface'), ('P3a', 'F4_P3a', 'interface'), ('P5', 'H5_P5s', 'all'), ('P4', 'H6_P4_capthin', None), ('P6', 'H7_P6_thin', None)]
EXTRA = [('Calibration', 'H0_cal_solid', None), ('Adhesion test', 'F0_adh', 'interface')]
def hm(m): m = int(round(m)); return '%d h %02d' % (m // 60, m % 60) if m >= 60 else '%d min' % m
def row(lab, job, two):
    gs = json.load(open('%s/%s/gsum.json' % (GD, job))); t, tp, gabs = gs['print_min'], gs['with_prep_min'], gs['g'][0]; sfa = 0.0; note = ''
    if two:
        g = G(job); S = g.S; names = ('Support interface',) if two == 'interface' else ('Support', 'Support interface', 'Support transition')
        m = np.isin(g.F, [i for i, n in enumerate(g.names) if n in names]); nl = len(np.unique(S[m, 4]))
        vol = sum(o['feat_mm3'].get(n, 0.0) for o in gs['objects'].values() for n in names)
        ch = 2 * nl; tower = ch * 45.0; dt = ch * 5.0 / 60.0
        sfa = (vol + tower / 2) * 1.16 / 1000.0; gabs2 = gabs - vol * 1.04 / 1000.0 + tower / 2 * 1.04 / 1000.0
        note = '%s in Support for ABS %.0f mm3 on %d layers, %d nozzle changes, tower %.1f cm3 | stand-in %.1f / %.1f min, %.2f g' % (two, vol, nl, ch, tower / 1000, t, tp, gabs)
        t += dt; tp += dt; gabs = gabs2
    return dict(lab=lab, job=job, t=t, tp=tp, abs=gabs, sfa=sfa, note=note)
R = [row(*p) for p in PLAN]; X = [row(*p) for p in EXTRA]
for r in R + X: print('%-14s %-14s %7.1f / %7.1f min (%s / %s)  ABS %7.2f g  SfA %5.2f g  %s' % (r['lab'], r['job'], r['t'], r['tp'], hm(r['t']), hm(r['tp']), r['abs'], r['sfa'], r['note']))
T = sum(r['t'] for r in R); TP = sum(r['tp'] for r in R); A = sum(r['abs'] for r in R); SF = sum(r['sfa'] for r in R)
print('set: %.1f / %.1f min (%s / %s), ABS %.1f g, SfA %.1f g' % (T, TP, hm(T), hm(TP), A, SF))
print('with calibration and adhesion test: ABS %.1f g, SfA %.1f g; + a reprint of shell and screen plate: ABS %.1f g' % (A + sum(r['abs'] for r in X), SF + sum(r['sfa'] for r in X), A + sum(r['abs'] for r in X) + R[2]['abs'] + R[3]['abs']))
st = [json.load(open('%s/%s/gsum.json' % (GD, p[1]))) for p in PLAN]
print('stand-ins (one material): %.1f / %.1f min, %.2f g' % (sum(s['print_min'] for s in st), sum(s['with_prep_min'] for s in st), sum(s['g'][0] for s in st)))
json.dump(dict(plan=R, extra=X), open('/home/claude/r3/data/plan_v67.json', 'w'), indent=1)
