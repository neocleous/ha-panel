# Print files of version 91: times and grams per plate and per set, from each slice's own result.json (Bambu Studio's estimates).
# No Fusion object. Times in minutes (printing; with the printer's preparation), masses in g by filament.
import os, json, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
J = runpy.run_path(os.path.join(D, 'pf91_20_jobs.py'))
HELD = ('T02_P1b', 'A06_P3a')


def main():
    sets = {'pla_cal': [], 'pla': [], 'abs_cal': [], 'abs_adh': [], 'abs': []}; rows = {}
    for p in J['PLATES']:
        job = p[0]; r = json.load(open(os.path.join(L['W'], 'slicer', 'out', job, 'result.json'))); pl = r['sliced_plates'][0]
        m = pl['main_predication'] / 60.0; t = pl['total_predication'] / 60.0; g = [f.get('total_used_g', 0.0) for f in pl['filaments']]
        rows[job] = {'min': round(m, 1), 'min_prep': round(t, 1), 'g': [round(x, 2) for x in g], 'held': job in HELD, 'warning': pl.get('warning_message', '')}
        k = 'pla_cal' if job == 'T00_cal' else 'abs_cal' if job == 'A00_cal' else 'abs_adh' if job == 'A00_adh' else 'pla' if job[0] == 'T' else 'abs'
        sets[k].append((job, m, t, g))
        print('%-8s %7.1f %7.1f  g %s%s' % (job, m, t, [round(x, 2) for x in g], '  HELD' if job in HELD else ''))
    out = {}
    for k, v in sets.items():
        m = sum(x[1] for x in v); t = sum(x[2] for x in v); g1 = sum(x[3][0] for x in v); g2 = sum(x[3][1] for x in v if len(x[3]) > 1)
        out[k] = {'plates': len(v), 'min': round(m, 1), 'h': round(m / 60, 1), 'min_prep': round(t, 1), 'h_prep': round(t / 60, 1), 'g1': round(g1, 2), 'g2': round(g2, 2)}
        print('%-8s %2d plates: %.1f min (%.1f h); %.1f with preparation (%.1f h); filament 1 %.2f g; Support for ABS %.2f g' % (
            k, len(v), m, m / 60, t, t / 60, g1, g2))
    L['jdump']('pf91_41_totals.json', {'rows': rows, 'sets': out})
# END pf91_41_totals.py
