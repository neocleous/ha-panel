# Job specs for the print files of version 67 (2026-11-19): the PLA trial, the ABS calibration and adhesion test, the black ABS
#   set. The 2026-11-16 specs (print_files/slicer/specs.py, the settings of D181) with the changes of the re-check's hand-over §5
#   (D237 to D242, D247), each as the re-check sliced it (print_audit_recheck3/slicer/variants.json and r3_specs.py):
#   - calibration: the hole block with the pilot lug (cal_holes_v67.stl), printed solid (D242);
#   - adhesion test: the 8.0 cut of version 67, 4 walls, blockers = chin band + the two bottom hole cylinders (D241);
#   - P1: both boxes at 100 % zig-zag (D239);
#   - P3b: trees under the border, the two plate blockers; ABS: Support-for-ABS interface, top Z 0, dense, prime tower (D237),
#     a window project; PLA: plain trees (D247);
#   - P3a: 4 walls (D238), blockers v3 (D241);
#   - P4: thin-wall detection on the cap (D240); P6: thin-wall detection on (D240).
#   Common (mkjob.BASE_OPTS): X2D, both 0.4 High Flow; X-Y hole compensation 0.1; elephant foot 0.15; trees (auto) at 30 deg;
#   "don't support bridges"; Manual filament map. Shrinkage 100 % (the presets' own) until Daniel enters his.
# Usage: PF_MAC_WORK=<Mac print_files_v67/_work> PF_JOBS=<local jobs dir> python3 specs67.py [job ...]
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)
import mkjob

ABS = 'filament_BambuABS_black.json'
SFA = 'filament_SupportABS_white.json'
PLA = 'filament_BambuPLABasic_black.json'
P20 = 'process_0.20_Standard.json'
P12 = 'process_0.12_HQ.json'
TPEI = 'Textured PEI Plate'
ENG = 'Engineering Plate'
F_TRIAL = '1_PLA_trial'
F_ADH = '2_ABS_calibration_and_adhesion_test'
F_SET = '3_ABS_black_set'
BRIM3 = {'brim_type': 'outer_only', 'brim_width': '3', 'brim_object_gap': '0.1'}
SOLID = {'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag'}          # per object (assemble list)
SOL = {'sparse-infill-density': '100%', 'sparse-infill-pattern': 'zig-zag'}            # whole plate (command line)
W4 = {'wall-loops': '4'}                                                               # D238

# pos is a plain offset added to the mesh's own bed coordinates (the oriented meshes are centred on the bed, 128, 128).
P3A_POS = (0.0, -30.0, 0.0)            # the shell with a tower: 30 mm toward the front, leaving room behind it (D181)
CUT_POS = P3A_POS                      # the adhesion test lies exactly where it lies in P3a
TOWER_SHELL = {'wipe-tower-x': '110', 'wipe-tower-y': '205', 'prime-tower-width': '35'}   # D181 (lower-left corner)
TOWER_PLATE = dict(TOWER_SHELL)        # P3b: the same tower, behind the plate (plate y 65.65 to 190.35 on the bed)
TOWER_SLAB = {'wipe-tower-x': '30', 'wipe-tower-y': '110', 'prime-tower-width': '30'}     # D181
IF_SHELL = {'support-filament': '1', 'support-interface-filament': '2', 'support-top-z-distance': '0',
            'support-interface-spacing': '0', 'enable-prime-tower': '1', 'filament-map': '1,2'}   # D173, D181; P3b too (D237)
IF_SLAB = {'support-filament': '2', 'support-interface-filament': '2', 'support-top-z-distance': '0',
           'support-interface-spacing': '0', 'enable-prime-tower': '1', 'filament-map': '1,2'}    # D181
IFGEO = {'support-top-z-distance': '0', 'support-interface-spacing': '0'}   # the interface's geometry in one material (stand-ins)
SHELL_BRIM = {'enable-support': '1', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1'}
WIN = ('Slice in the window. Filament 1 black ABS on the main (left) nozzle, filament 2 Support for ABS on the auxiliary '
       '(right) nozzle from its external spool (D178). Shrinkage: your calibrated preset on filament 1.')


def cal(prefix, fil, label, folder, fname, plate_note):
    return {'job': prefix + '_cal', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim'},
            'title': label, 'desc': plate_note + ' Frame 120 outside and 108 inside, 5 tall: measure outside and inside, X and Y, '
            'at mid-height. Tower 20 x 20 x 30: its height, and its width at the first layer and at 15 mm. Hole block (solid): '
            'the 4.0 drill shank into both 4.0 holes, an M3 screw through both 3.4 holes, and an M3 screw driven into the '
            'sideways 2.7 pilot in the lug and removed three times, with no crack line.',
            'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'cal_frame.stl', 'pos': [128, 128, 0]},
                                                    {'stl': 'cal_tower.stl', 'pos': [98, 128, 0]},
                                                    {'stl': 'cal_holes_v67.stl', 'pos': [149, 128, 0], 'params': SOLID}]}]}


def p1(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P1', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '1', 'brim-type': 'no_brim'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'base_plan.stl', 'pos': [0, 75, 0], 'params': {'enable_support': '0', 'brim_type': 'no_brim'}},
                {'stl': 'spkbox_L_plan.stl', 'pos': [-50, -72, 0], 'params': dict(enable_support='1', **BRIM3, **SOLID)},
                {'stl': 'spkbox_R_plan.stl', 'pos': [50, -72, 0], 'params': dict(enable_support='1', **BRIM3, **SOLID)}]}]}


def p2(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P2', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'carrier_plan.stl', 'pos': [-38, 0, 0]},
                {'stl': 'cradle_plan.stl', 'pos': [47, -38, 0], 'params': {'enable_support': '1'}},
                {'stl': 'clip_L_plan.stl', 'pos': [37, 0, 0], 'params': BRIM3},
                {'stl': 'clip_R_plan.stl', 'pos': [57, 0, 0], 'params': BRIM3},
                {'stl': 'bme_hood_plan.stl', 'pos': [47, 42, 0]}]}]}


def p3b(prefix, fils, label, folder, fname, opts):
    return {'job': prefix + '_P3b', 'process': P20, 'filaments': fils, 'bed': TPEI,
            'opts': dict(SOL, **{'enable-support': '1', 'brim-type': 'no_brim'}, **opts), 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'screen_plan.stl', 'assemble': 1, 'pos': [0, 0, 0]},
                {'stl': 'screen_plan_blk.stl', 'assemble': 1, 'subtype': 'support_blocker', 'pos': [0, 0, 0]}]}]}


def p3a(prefix, fils, label, folder, fname, opts, pos):
    return {'job': prefix + '_P3a', 'process': P20, 'filaments': fils, 'bed': TPEI, 'opts': dict(SHELL_BRIM, **W4, **opts),
            'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'shell_plan.stl', 'assemble': 1, 'pos': list(pos)},
                {'stl': 'shell_plan_blk_v3.stl', 'assemble': 1, 'subtype': 'support_blocker', 'pos': list(pos)}]}]}


def p5(prefix, fils, label, folder, fname, opts, bed, pos):
    return {'job': prefix + '_P5', 'process': P12, 'filaments': fils, 'bed': bed,
            'opts': dict({'layer-height': '0.1', 'enable-support': '1', 'brim-type': 'outer_only', 'brim-width': '3',
                          'brim-object-gap': '0.1'}, **opts), 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'slab_plan.stl', 'pos': list(pos)}]}]}


def p4(prefix, fil, label, folder, fname, bed):
    return {'job': prefix + '_P4', 'process': P12, 'filaments': [fil], 'bed': bed,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim', 'initial-layer-print-height': '0.2'},
            'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'cap_plan.stl', 'pos': [0, -28, 0], 'params': {'brim_type': 'brim_ears', 'detect_thin_wall': '1'}},
                {'stl': 'grommet_plan.stl', 'pos': [0, 52, 0], 'params': dict(enable_support='1', **BRIM3)}]}]}


def p6(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P6', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1',
                     'detect-thin-wall': '1'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'door_plan.stl', 'pos': [0, 0, 0]}]}]}


S = []
# ---- the PLA trial: Bambu PLA Basic, Textured PEI without glue, plain trees, no tower (D181, D247) ----
NG = 'PLA TRIAL, version 67. Textured PEI, no glue.'
S.append(cal('T0', PLA, 'v67 TRIAL PLA calibration | TPEI', F_TRIAL, 'TRIAL_PLA_0_calibration_v67.3mf', NG))
S.append(p1('T1', PLA, 'v67 TRIAL PLA P1 base plate + boxes | TPEI', F_TRIAL, 'TRIAL_PLA_1_P1_base_plate_and_boxes_v67.3mf'))
S.append(p2('T2', PLA, 'v67 TRIAL PLA P2 carrier, cradle, clips, hood | TPEI', F_TRIAL, 'TRIAL_PLA_2_P2_carrier_cradle_clips_hood_v67.3mf'))
S.append(p3b('T3', [PLA], 'v67 TRIAL PLA P3b screen plate, solid, plain trees | TPEI', F_TRIAL, 'TRIAL_PLA_3_P3b_screen_plate_v67.3mf', {}))
S.append(p3a('T4', [PLA], 'v67 TRIAL PLA P3a shell, plain trees | TPEI', F_TRIAL, 'TRIAL_PLA_4_P3a_shell_v67.3mf', {}, (0, 0, 0)))
S.append(p5('T5', [PLA], 'v67 TRIAL PLA P5 slab, plain trees | TPEI', F_TRIAL, 'TRIAL_PLA_5_P5_slab_v67.3mf',
            {'support-top-z-distance': '0.2'}, TPEI, (0, 0, 0)))
S.append(p4('T6', PLA, 'v67 TRIAL PLA P4 cap + grommet | TPEI', F_TRIAL, 'TRIAL_PLA_6_P4_cap_and_grommet_v67.3mf', TPEI))
S.append(p6('T7', PLA, 'v67 TRIAL PLA P6 door | TPEI', F_TRIAL, 'TRIAL_PLA_7_P6_door_v67.3mf'))
for s in S:
    if s['job'] != 'T0_cal':
        s['desc'] = NG + ' Plain tree supports.'
# ---- black ABS: calibration and adhesion test ----
G = 'Black ABS, version 67. Textured PEI with glue.'
S.append(cal('A0', ABS, 'v67 ABS calibration | TPEI + glue', F_ADH, 'ABS_0a_calibration_v67.3mf', G))
adh = {'job': 'A0_adh', 'process': P20, 'filaments': [ABS, SFA], 'bed': TPEI, 'slice': False,
       'opts': dict(SHELL_BRIM, **W4, **IF_SHELL, **TOWER_SHELL),
       'title': 'v67 ABS adhesion test - shell first 8 mm', 'deliver': [F_ADH, 'ABS_0b_adhesion_test_shell_8mm_WINDOW_v67.3mf'],
       'desc': 'Black ABS, version 67. The shell P3a first 8.0 mm, placed where it lies in P3a. Textured PEI with glue. Chin face '
               'down, 4 walls, blockers along the chin edges and in the two bottom insert holes, 5 mm brim, tree supports in black '
               'ABS with the Support for ABS interface, prime tower behind the part. ' + WIN,
       'plates': [{'name': 'v67 ABS adhesion test: shell first 8 mm + SfA | TPEI + glue', 'objects': [
           {'stl': 'shell_chin8_plan.stl', 'assemble': 1, 'pos': list(CUT_POS)},
           {'stl': 'shell_chin8_blk_v3.stl', 'assemble': 1, 'subtype': 'support_blocker', 'pos': list(CUT_POS)}]}]}
S.append(adh)
# ---- the black ABS set, in the first-print order ----
S.append(p1('A1', ABS, 'v67 ABS P1 base plate + boxes | TPEI + glue', F_SET, 'ABS_1_P1_base_plate_and_boxes_v67.3mf'))
S.append(p2('A2', ABS, 'v67 ABS P2 carrier, cradle, clips, hood | TPEI + glue', F_SET, 'ABS_2_P2_carrier_cradle_clips_hood_v67.3mf'))
a3 = p3b('A3', [ABS, SFA], 'v67 ABS P3b screen plate + SfA interface | TPEI + glue', F_SET, 'ABS_3_P3b_screen_plate_WINDOW_v67.3mf',
         dict(IF_SHELL, **TOWER_PLATE))
a3['slice'] = False
a3['desc'] = ('Black ABS, version 67. Textured PEI with glue. Back face down, solid (100 % zig-zag), no brim. Tree supports under '
              'the raised border with the Support for ABS interface (top Z distance 0, dense), two blockers over the peg pocket '
              'and the peg slot, prime tower behind the part. ' + WIN)
S.append(a3)
a4 = p3a('A4', [ABS, SFA], 'v67 ABS P3a shell + SfA interface | TPEI + glue', F_SET, 'ABS_4_P3a_shell_WINDOW_v67.3mf',
         dict(IF_SHELL, **TOWER_SHELL), P3A_POS)
a4['slice'] = False
a4['desc'] = ('Black ABS, version 67. Textured PEI with glue. Chin face down, 4 walls, blockers v3 (the settled boxes, the band '
              'along the chin edges and one cylinder in each post insert hole), 5 mm brim, tree supports in black ABS with the '
              'Support for ABS interface (D173), prime tower behind the part. ' + WIN)
S.append(a4)
a5 = p5('A5', [ABS, SFA], 'v67 ABS P5 slab + SfA | Engineering + glue', F_SET, 'ABS_5_P5_slab_WINDOW_v67.3mf',
        dict(IF_SLAB, **TOWER_SLAB), ENG, (34, 0, 0))
a5['slice'] = False
a5['desc'] = ('Black ABS, version 67. Engineering plate with glue. 0.10 layers. All support in Support for ABS, top Z distance 0, '
              'dense interface, prime tower on the left of the slab, 3 mm brim. ' + WIN)
S.append(a5)
S.append(p4('A6', ABS, 'v67 ABS P4 cap + grommet | Engineering + glue', F_SET, 'ABS_6_P4_cap_and_grommet_v67.3mf', ENG))
S.append(p6('A7', ABS, 'v67 ABS P6 door | TPEI + glue', F_SET, 'ABS_7_P6_door_v67.3mf'))
for s in S:
    if s['job'] in ('A1_P1', 'A2_P2', 'A6_P4', 'A7_P6'):
        s['desc'] = 'Black ABS, version 67. ' + ('Textured PEI with glue.' if s['bed'] == TPEI else 'Engineering plate with glue.')
# ---- one-material stand-ins of the four window plates (work files only, reference figures; as the re-check's F0_adh, F3_P3b,
#      F4_P3a, H5_P5s: the interface's geometry printed in black ABS, no tower) ----
for src, job, opts in ((adh, 'A0s_adh_1m', dict(SHELL_BRIM, **W4, **IFGEO)),
                       (a3, 'A3s_P3b_1m', dict(SOL, **{'enable-support': '1', 'brim-type': 'no_brim'}, **IFGEO)),
                       (a4, 'A4s_P3a_1m', dict(SHELL_BRIM, **W4, **IFGEO)),
                       (a5, 'A5s_P5_1m', {'layer-height': '0.1', 'enable-support': '1', 'brim-type': 'outer_only', 'brim-width': '3',
                                          'brim-object-gap': '0.1', **IFGEO})):
    st = json.loads(json.dumps(src)); st['job'] = job; st['filaments'] = [ABS]; st['slice'] = True; st.pop('deliver')
    st['opts'] = opts; st['title'] = job; st['desc'] = 'one-material stand-in of a window project, version 67 - not a print file'
    S.append(st)

if __name__ == '__main__':
    want = sys.argv[1:]
    os.makedirs(os.path.join(here, 'specs'), exist_ok=True)
    for s in S:
        if want and s['job'] not in want:
            continue
        json.dump(s, open(os.path.join(here, 'specs', s['job'] + '.json'), 'w'), indent=1)
        d, args = mkjob.build(s)
        print('%-12s %-6s %2d args  %s' % (s['job'], 'slice' if s.get('slice', True) else 'WINDOW', len(args),
                                         '/'.join(s.get('deliver', ['(work only)']))))
