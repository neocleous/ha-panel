# Job specs for the print files (2026-11-16): the black ABS set, the ABS adhesion test, the PLA trial, the two calibrations.
#   Every plate follows the print plan of the Architect's log 2026-11-16 §5 (and the re-check's job specs at docs 89d06d7:
#   P1_base_boxes, P2_small, Y_screen_solid100, A_shell_v3, B_slab, P5_cap_grommet, B_door), with the decisions D154, D164-D166
#   and D173 (Support-for-ABS interface on the shell). Common: X2D, both 0.4 High Flow; X-Y hole compensation 0.1; elephant foot
#   0.15; trees (auto) at 30 deg; "don't support bridges" (mkjob.BASE_OPTS).
# Usage: python3 specs.py  -> writes specs/<job>.json and builds jobs/<job>/ with mkjob.build
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

# pos is a plain offset added to the mesh's own bed coordinates (the oriented meshes are centred on the bed, 128, 128; the CLI's
#   first test put the calibration meshes, made round 0, 0, off the bed). The shell's first 8 mm keeps the shell's own bed frame,
#   so it takes P3a's offset and lies exactly where it lies in P3a.
P3A_POS = (0.0, -30.0, 0.0)
CUT_POS = P3A_POS
# prime towers (lower-left corner, mm on the bed): reachable by both nozzles (the right one covers x 20.5 to 256)
TOWER_SHELL = {'wipe-tower-x': '110', 'wipe-tower-y': '205', 'prime-tower-width': '35'}
TOWER_SLAB = {'wipe-tower-x': '30', 'wipe-tower-y': '110', 'prime-tower-width': '30'}
IF_SHELL = {'support-filament': '1', 'support-interface-filament': '2', 'support-top-z-distance': '0',
            'support-interface-spacing': '0', 'enable-prime-tower': '1', 'filament-map': '1,2'}
IF_SLAB = {'support-filament': '2', 'support-interface-filament': '2', 'support-top-z-distance': '0',
           'support-interface-spacing': '0', 'enable-prime-tower': '1', 'filament-map': '1,2'}
SHELL_BRIM = {'enable-support': '1', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1'}


def cal(prefix, fil, plate_label, folder, fname, glue):
    return {'job': prefix + '_cal', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim'},
            'title': plate_label, 'desc': 'Textured PEI%s. Frame 120 outside and 108 inside, 5 tall: measure outside and inside, '
            'X and Y, at mid-height. Tower 20 x 20 x 30: its height, and its width at the first layer and at 15 mm. Hole block: '
            'the 4.0 drill shank into both 4.0 holes, an M3 screw through both 3.4 holes.' % glue,
            'deliver': [folder, fname],
            'plates': [{'name': plate_label, 'objects': [{'stl': 'cal_frame.stl', 'pos': [128, 128, 0]},
                                                          {'stl': 'cal_tower.stl', 'pos': [98, 128, 0]},
                                                          {'stl': 'cal_holes.stl', 'pos': [153, 128, 0]}]}]}


def p1(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P1', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '1', 'brim-type': 'no_brim'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'base_plan.stl', 'pos': [0, 75, 0], 'params': {'enable_support': '0', 'brim_type': 'no_brim'}},
                {'stl': 'spkbox_L_plan.stl', 'pos': [-50, -72, 0], 'params': dict(enable_support='1', **BRIM3)},
                {'stl': 'spkbox_R_plan.stl', 'pos': [50, -72, 0], 'params': dict(enable_support='1', **BRIM3)}]}]}


def p2(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P2', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'carrier_plan.stl', 'pos': [-38, 0, 0]},
                {'stl': 'cradle_plan.stl', 'pos': [47, -38, 0], 'params': {'enable_support': '1'}},
                {'stl': 'clip_L_plan.stl', 'pos': [37, 0, 0], 'params': BRIM3},
                {'stl': 'clip_R_plan.stl', 'pos': [57, 0, 0], 'params': BRIM3},
                {'stl': 'bme_hood_plan.stl', 'pos': [47, 42, 0]}]}]}


def p3b(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P3b', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim', 'sparse-infill-density': '100%',
                     'sparse-infill-pattern': 'zig-zag'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'screen_plan.stl', 'pos': [0, 0, 0]}]}]}


def p3a_plain(prefix, fil, label, folder, fname, pos=(0, 0, 0)):
    return {'job': prefix + '_P3a', 'process': P20, 'filaments': [fil], 'bed': TPEI, 'opts': dict(SHELL_BRIM),
            'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'shell_plan.stl', 'assemble': 1, 'pos': list(pos)},
                                                    {'stl': 'shell_plan_blk_v2.stl', 'assemble': 1, 'subtype': 'support_blocker',
                                                     'pos': list(pos)}]}]}


def p5_plain(prefix, fil, label, folder, fname, bed=TPEI):
    return {'job': prefix + '_P5', 'process': P12, 'filaments': [fil], 'bed': bed,
            'opts': {'layer-height': '0.1', 'enable-support': '1', 'support-top-z-distance': '0.2', 'brim-type': 'outer_only',
                     'brim-width': '3', 'brim-object-gap': '0.1'}, 'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'slab_plan.stl', 'pos': [0, 0, 0]}]}]}


def p4(prefix, fil, label, folder, fname, bed):
    return {'job': prefix + '_P4', 'process': P12, 'filaments': [fil], 'bed': bed,
            'opts': {'enable-support': '0', 'brim-type': 'no_brim', 'initial-layer-print-height': '0.2'},
            'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [
                {'stl': 'cap_plan.stl', 'pos': [0, -28, 0], 'params': {'brim_type': 'brim_ears'}},
                {'stl': 'grommet_plan.stl', 'pos': [0, 52, 0], 'params': dict(enable_support='1', **BRIM3)}]}]}


def p6(prefix, fil, label, folder, fname):
    return {'job': prefix + '_P6', 'process': P20, 'filaments': [fil], 'bed': TPEI,
            'opts': {'enable-support': '0', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1'},
            'title': label, 'deliver': [folder, fname],
            'plates': [{'name': label, 'objects': [{'stl': 'door_plan.stl', 'pos': [0, 0, 0]}]}]}


S = []
# ---- black ABS: calibration, adhesion test, the set (first-print order) ----
G = ' with glue'
S.append(cal('A0', ABS, 'ABS calibration | TPEI + glue', F_ADH, 'ABS_0a_calibration.3mf', G))
adh = {'job': 'A0_adh', 'process': P20, 'filaments': [ABS, SFA], 'bed': TPEI, 'slice': False,
       'opts': dict(SHELL_BRIM, **IF_SHELL, **TOWER_SHELL),
       'title': 'ABS adhesion test - shell first 8 mm', 'deliver': [F_ADH, 'ABS_0b_adhesion_test_shell_8mm_WINDOW.3mf'],
       'desc': 'The shell P3a first 8.0 mm, placed where it lies in P3a. Textured PEI with glue. Chin face down, blockers along '
               'the chin edges, 5 mm brim, tree supports in black ABS with the Support for ABS interface, prime tower. Slice in '
               'the window. Filament 1 black ABS on the left nozzle, filament 2 Support for ABS on the right.',
       'plates': [{'name': 'ABS adhesion test: shell first 8 mm + SfA | TPEI + glue', 'objects': [
           {'stl': 'shell_chin8_plan.stl', 'assemble': 1, 'pos': list(CUT_POS)},
           {'stl': 'shell_chin8_blk.stl', 'assemble': 1, 'subtype': 'support_blocker', 'pos': list(CUT_POS)}]}]}
S.append(adh)
S.append(p1('A1', ABS, 'ABS P1 base plate + boxes | TPEI + glue', F_SET, 'ABS_1_P1_base_plate_and_boxes.3mf'))
S.append(p2('A2', ABS, 'ABS P2 carrier, cradle, clips, hood | TPEI + glue', F_SET, 'ABS_2_P2_carrier_cradle_clips_hood.3mf'))
S.append(p3b('A3', ABS, 'ABS P3b screen plate, solid | TPEI + glue', F_SET, 'ABS_3_P3b_screen_plate.3mf'))
a4 = p3a_plain('A4', ABS, 'ABS P3a shell + SfA interface | TPEI + glue', F_SET, 'ABS_4_P3a_shell_WINDOW.3mf', P3A_POS)
a4['filaments'] = [ABS, SFA]; a4['slice'] = False; a4['opts'].update(IF_SHELL); a4['opts'].update(TOWER_SHELL)
a4['desc'] = ('Textured PEI with glue. Chin face down, settled blockers and the band along the chin edges, 5 mm brim, tree '
              'supports in black ABS with the Support for ABS interface (D173), prime tower. Slice in the window. Filament 1 '
              'black ABS on the left nozzle, filament 2 Support for ABS on the right.')
S.append(a4)
a5 = p5_plain('A5', ABS, 'ABS P5 slab + SfA | Engineering + glue', F_SET, 'ABS_5_P5_slab_WINDOW.3mf', ENG)
a5['filaments'] = [ABS, SFA]; a5['slice'] = False
a5['opts'].update(IF_SLAB); a5['opts'].update(TOWER_SLAB); a5['plates'][0]['objects'][0]['pos'] = [34, 0, 0]
a5['desc'] = ('Engineering plate with glue. 0.10 layers. All support in Support for ABS, top Z distance 0, prime tower, 3 mm '
              'brim. Slice in the window. Filament 1 black ABS on the left nozzle, filament 2 Support for ABS on the right.')
S.append(a5)
S.append(p4('A6', ABS, 'ABS P4 cap + grommet | Engineering + glue', F_SET, 'ABS_6_P4_cap_and_grommet.3mf', ENG))
S.append(p6('A7', ABS, 'ABS P6 door | TPEI + glue', F_SET, 'ABS_7_P6_door.3mf'))
for s in S:
    if s['job'] not in ('A0_cal', 'A0_adh', 'A4_P3a', 'A5_P5'):
        s['desc'] = 'Textured PEI with glue.' if s['bed'] == TPEI else 'Engineering plate with glue.'
# ---- one-material stand-ins of the three window plates (work files only, for reference figures) ----
st = json.loads(json.dumps(a4)); st['job'] = 'A4s_P3a_1m'; st['filaments'] = [ABS]; st['slice'] = True; st.pop('deliver')
st['opts'] = dict(SHELL_BRIM, **{'support-top-z-distance': '0', 'support-interface-spacing': '0'})
S.append(st)
st = json.loads(json.dumps(a5)); st['job'] = 'A5s_P5_1m'; st['filaments'] = [ABS]; st['slice'] = True; st.pop('deliver')
st['opts'] = {'layer-height': '0.1', 'enable-support': '1', 'support-top-z-distance': '0', 'support-interface-spacing': '0',
              'brim-type': 'outer_only', 'brim-width': '3', 'brim-object-gap': '0.1'}
S.append(st)
st = json.loads(json.dumps(adh)); st['job'] = 'A0bs_adh_1m'; st['filaments'] = [ABS]; st['slice'] = True; st.pop('deliver')
st['opts'] = dict(SHELL_BRIM, **{'support-top-z-distance': '0', 'support-interface-spacing': '0'})
S.append(st)
# ---- the PLA trial: the same plates in Bambu PLA Basic, plain tree supports, Textured PEI, no glue ----
NG = ', no glue'
S.append(cal('T0', PLA, 'TRIAL PLA calibration | TPEI', F_TRIAL, 'TRIAL_PLA_0_calibration.3mf', NG))
S.append(p1('T1', PLA, 'TRIAL PLA P1 base plate + boxes | TPEI', F_TRIAL, 'TRIAL_PLA_1_P1_base_plate_and_boxes.3mf'))
S.append(p2('T2', PLA, 'TRIAL PLA P2 carrier, cradle, clips, hood | TPEI', F_TRIAL, 'TRIAL_PLA_2_P2_carrier_cradle_clips_hood.3mf'))
S.append(p3b('T3', PLA, 'TRIAL PLA P3b screen plate, solid | TPEI', F_TRIAL, 'TRIAL_PLA_3_P3b_screen_plate.3mf'))
S.append(p3a_plain('T4', PLA, 'TRIAL PLA P3a shell, plain trees | TPEI', F_TRIAL, 'TRIAL_PLA_4_P3a_shell.3mf'))
S.append(p5_plain('T5', PLA, 'TRIAL PLA P5 slab, plain trees | TPEI', F_TRIAL, 'TRIAL_PLA_5_P5_slab.3mf'))
S.append(p4('T6', PLA, 'TRIAL PLA P4 cap + grommet | TPEI', F_TRIAL, 'TRIAL_PLA_6_P4_cap_and_grommet.3mf', TPEI))
S.append(p6('T7', PLA, 'TRIAL PLA P6 door | TPEI', F_TRIAL, 'TRIAL_PLA_7_P6_door.3mf'))
for s in S:
    if s['job'].startswith('T') and s['job'] != 'T0_cal':
        s['desc'] = 'PLA TRIAL. Textured PEI, no glue. Plain tree supports.'
        s['title'] = 'TRIAL ' + s['title'] if not s['title'].startswith('TRIAL') else s['title']

if __name__ == '__main__':
    os.makedirs(os.path.join(here, 'specs'), exist_ok=True)
    for s in S:
        json.dump(s, open(os.path.join(here, 'specs', s['job'] + '.json'), 'w'), indent=1)
        d, args = mkjob.build(s)
        print('%-12s %-6s %2d args  %s' % (s['job'], 'slice' if s.get('slice', True) else 'WINDOW', len(args),
                                         '/'.join(s.get('deliver', ['(work only)']))))
