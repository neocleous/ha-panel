# Print files of version 91, block 4: the holes read on each plate's own slice, summed up. No Fusion object.
#   main(): per plate, the holes read, those with support inside (over 0.3 mm3, the re-check's figure), and those the part's own lines
#           do not ring (a hole not found where the part is, or above the print); then every flagged row in full.
import os, json, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
S = runpy.run_path(os.path.join(D, 'pf91_30_stop.py'))
OUT = os.path.join(L['W'], 'out')


def main(thr=0.3):
    tot = {}
    for job in list(S['PAIRS']) + ['T00_cal', 'A00_cal']:
        p = os.path.join(OUT, 'holes_%s.json' % job)
        if not os.path.exists(p):
            print('%-8s NOT READ YET' % job); continue
        R = json.load(open(p)); sup = [r for r in R if r['support_mm3'] > thr]; lost = [r for r in R if r['own_ring_mm3'] <= 0.0 and r['in_print']]
        above = [r for r in R if not r['in_print']]
        tot[job] = (len(R), len(sup), len(lost), len(above))
        print('%-8s holes %3d | support inside over %.1f mm3: %d | not ringed by the part: %d | above the print: %d | most support in any other hole %.2f mm3' % (
            job, len(R), thr, len(sup), len(lost), len(above), max([r['support_mm3'] for r in R if r not in sup] or [0.0])))
        for r in sup + lost:
            print('      %-11s d %.2f %-14s len %5.2f bed %s -> %s | support %.2f mm3 (%d lines) along %s | ring %.1f mm3' % (
                r['part'], r['d'], '/'.join(r['ends']), r['len'], r['bed'][0], r['bed'][1], r['support_mm3'], r['lines'], r['t_range'], r['own_ring_mm3']))
    L['jdump']('pf91_33_hsum.json', tot)
# END pf91_33_hsum.py
