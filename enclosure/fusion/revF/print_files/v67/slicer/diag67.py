# Diagnostic jobs (work files only, not print files): where do the PLA shell's two "overhang regions that could not get support"
#   come from? Each is the PLA trial's T4_P3a (or the ABS stand-in A4s_P3a_1m) with one thing changed.
#   X1_T4_blkv2   : T4_P3a with the settled blockers v2 (no hole cylinders)
#   X2_A4s_plain  : A4s_P3a_1m (ABS, 4 walls, blockers v3, pos 0,-30) with plain trees (the profile's top Z distance 0.2 and
#                   interface spacing 0.5), i.e. T4's support settings in ABS
#   X3_T4_pos30   : T4_P3a placed as the ABS shell (pos 0,-30)
#   X4_T4_w2      : T4_P3a with 2 walls (as 2026-11-16)
# Usage: PF_MAC_WORK=... PF_JOBS=... python3 diag67.py [job ...]
import json, os, sys, copy
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import mkjob
import specs67 as sp
by = {s['job']: s for s in sp.S}
D = []
x = copy.deepcopy(by['T4_P3a']); x['job'] = 'X1_T4_blkv2'; x.pop('deliver'); x['title'] = x['job']; x['desc'] = 'diagnostic, not a print file'
x['plates'][0]['objects'][1]['stl'] = 'shell_plan_blk_v2.stl'; D.append(x)
x = copy.deepcopy(by['A4s_P3a_1m']); x['job'] = 'X2_A4s_plain'; x['title'] = x['job']; x['desc'] = 'diagnostic, not a print file'
for k in ('support-top-z-distance', 'support-interface-spacing'):
    x['opts'].pop(k)
D.append(x)
x = copy.deepcopy(by['T4_P3a']); x['job'] = 'X3_T4_pos30'; x.pop('deliver'); x['title'] = x['job']; x['desc'] = 'diagnostic, not a print file'
for o in x['plates'][0]['objects']:
    o['pos'] = [0, -30, 0]
D.append(x)
x = copy.deepcopy(by['T4_P3a']); x['job'] = 'X4_T4_w2'; x.pop('deliver'); x['title'] = x['job']; x['desc'] = 'diagnostic, not a print file'
x['opts'].pop('wall-loops'); D.append(x)

if __name__ == '__main__':
    want = sys.argv[1:]
    os.makedirs(os.path.join(here, 'specs'), exist_ok=True)
    for s in D:
        if want and s['job'] not in want:
            continue
        json.dump(s, open(os.path.join(here, 'specs', s['job'] + '.json'), 'w'), indent=1)
        d, args = mkjob.build(s)
        print('%-14s %2d args' % (s['job'], len(args)))

# X5_T4_dbg: T4_P3a with the slicer's debug log at level 5 (trace), to find where the two unsupported overhang regions are
x = copy.deepcopy(by['T4_P3a']); x['job'] = 'X5_T4_dbg'; x.pop('deliver'); x['title'] = x['job']; x['desc'] = 'diagnostic, not a print file'
x['debug'] = 5
if __name__ == '__main__' and (not sys.argv[1:] or 'X5_T4_dbg' in sys.argv[1:]):
    json.dump(x, open(os.path.join(here, 'specs', x['job'] + '.json'), 'w'), indent=1)
    d, args = mkjob.build(x); print('%-14s %2d args' % (x['job'], len(args)))

# X6_T4_thin: T4_P3a with thin-wall detection on: does the warning change when the groove lip's 0.48 first layer is printed?
x6 = copy.deepcopy(by['T4_P3a']); x6['job'] = 'X6_T4_thin'; x6.pop('deliver'); x6['title'] = x6['job']; x6['desc'] = 'diagnostic, not a print file'
x6['opts']['detect-thin-wall'] = '1'; x6['debug'] = 4
if __name__ == '__main__' and (not sys.argv[1:] or 'X6_T4_thin' in sys.argv[1:]):
    json.dump(x6, open(os.path.join(here, 'specs', x6['job'] + '.json'), 'w'), indent=1)
    d, args = mkjob.build(x6); print('%-14s %2d args' % (x6['job'], len(args)))

# X7_T4_lipfill: T4_P3a with a box part (x 36 to 220, y 87.15 to 89.35, z 0 to 0.45, bed frame) joined to the shell, filling the
#   gap under the band along the chin's top edge (between the cloth groove and the screen), so that the band stands on the bed.
#   Diagnostic only: does the warning go away?
x7 = copy.deepcopy(by['T4_P3a']); x7['job'] = 'X7_T4_lipfill'; x7.pop('deliver'); x7['title'] = x7['job']; x7['desc'] = 'diagnostic, not a print file'
x7['debug'] = 4
x7['plates'][0]['objects'].insert(1, {'stl': 'diag_lipfill_box.stl', 'assemble': 1, 'pos': [0, 0, 0]})
if __name__ == '__main__' and (not sys.argv[1:] or 'X7_T4_lipfill' in sys.argv[1:]):
    json.dump(x7, open(os.path.join(here, 'specs', x7['job'] + '.json'), 'w'), indent=1)
    d, args = mkjob.build(x7); print('%-14s %2d args' % (x7['job'], len(args)))
