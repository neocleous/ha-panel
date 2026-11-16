# Per-project time and filament from the slicer's result.json files (print / with the printer's preparation), and the totals
#   per set. Usage: python3 totals.py <out dir with <job>/result.json>
import json, os, sys
OUT = sys.argv[1]


def res(job):
    r = json.load(open(os.path.join(OUT, job, 'result.json')))
    pl = r['sliced_plates'][0]
    return {'job': job, 'print_min': pl['main_predication'] / 60.0, 'prep_min': pl['total_predication'] / 60.0,
            'g': [f['total_used_g'] for f in pl['filaments']], 'warn': (pl.get('warning_message') or '').replace('\n', ' ')[:200],
            'changes': pl.get('filament_change_times')}


def hm(m):
    m = int(round(m)); return '%d h %02d' % (m // 60, m % 60) if m >= 60 else '%d min' % m


SETS = {'ABS set, sliced plates': ['A1_P1', 'A2_P2', 'A3_P3b', 'A6_P4', 'A7_P6'],
        'ABS calibration': ['A0_cal'],
        'one-material stand-ins of the window plates': ['A4s_P3a_1m', 'A5s_P5_1m', 'A0bs_adh_1m'],
        'PLA trial incl. calibration': ['T0_cal', 'T1_P1', 'T2_P2', 'T3_P3b', 'T4_P3a', 'T5_P5', 'T6_P4', 'T7_P6'],
        'control': ['Z1_P1_rc2mesh']}
allr = {}
for name, jobs in SETS.items():
    print('==', name)
    tp = tq = tg = 0.0
    for j in jobs:
        r = res(j); allr[j] = r
        tp += r['print_min']; tq += r['prep_min']; tg += sum(r['g'])
        print('  %-14s %8.1f %8.1f min  %-8s / %-8s  %s g  %s' % (j, r['print_min'], r['prep_min'], hm(r['print_min']), hm(r['prep_min']),
                                                          [round(g, 2) for g in r['g']], r['warn'][:90]))
    print('  TOTAL %8.1f %8.1f min  %s / %s  %.2f g' % (tp, tq, hm(tp), hm(tq), tg))
json.dump(allr, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'totals.json'), 'w'), indent=1)
