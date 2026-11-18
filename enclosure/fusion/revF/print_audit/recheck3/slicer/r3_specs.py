# recheck3 (print re-check of version 67, 2026-11-18): audit slices. One material (black ABS), headless (D139). Built on the
#   print files' specs (print_files/slicer/specs.py, D181) with the bed meshes of version 67 (r3_orient.py). Not print files.
#   Usage: PF_MAC_WORK=<Mac recheck3 folder> PF_JOBS=<jobs folder> python3 r3_specs.py [job ...]
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here)
import mkjob
ABS = 'filament_BambuABS_black.json'
P20 = 'process_0.20_Standard.json'; P12 = 'process_0.12_HQ.json'
TPEI = 'Textured PEI Plate'; ENG = 'Engineering Plate'
BRIM3 = {'brim_type': 'outer_only', 'brim_width': '3', 'brim_object_gap': '0.1'}
SOLID = {'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag'}
P3A_POS = (0.0, -30.0, 0.0)
SHELL_BRIM = {'enable-support': '1', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1'}
IFGEO = {'support-top-z-distance': '0', 'support-interface-spacing': '0'}        # the Support-for-ABS interface's geometry in one material
S = []

PREFIX = os.environ.get('R3_PREFIX', 'R')

def add(job, process, opts, objects, bed=TPEI):
    job = PREFIX + job[1:]
    S.append({'job': job, 'process': process, 'filaments': [ABS], 'bed': bed, 'opts': opts, 'title': job, 'desc': 'recheck3 audit slice of version 67 - not a print file',
              'plates': [{'name': job, 'objects': objects}]})

def p1(job, box_params):
    add(job, P20, {'enable-support': '1', 'brim-type': 'no_brim'}, [
        {'stl': 'base_plan.stl', 'pos': [0, 75, 0], 'params': {'enable_support': '0', 'brim_type': 'no_brim'}},
        {'stl': 'spkbox_L_plan.stl', 'pos': [-50, -72, 0], 'params': dict(enable_support='1', **BRIM3, **box_params)},
        {'stl': 'spkbox_R_plan.stl', 'pos': [50, -72, 0], 'params': dict(enable_support='1', **BRIM3, **box_params)}])

p1('R1_P1', {})                                   # as the print files (D181)
p1('R1s_P1_solid', SOLID)                         # FDM9: both boxes at 100 % infill
p1('R1w_P1_w4', {'wall_loops': '4'})              # FDM9 alternative: 4 walls on the boxes
add('R2_P2', P20, {'enable-support': '0', 'brim-type': 'no_brim'}, [
    {'stl': 'carrier_plan.stl', 'pos': [-38, 0, 0]},
    {'stl': 'cradle_plan.stl', 'pos': [47, -38, 0], 'params': {'enable_support': '1'}},
    {'stl': 'clip_L_plan.stl', 'pos': [37, 0, 0], 'params': BRIM3},
    {'stl': 'clip_R_plan.stl', 'pos': [57, 0, 0], 'params': BRIM3},
    {'stl': 'bme_hood_plan.stl', 'pos': [47, 42, 0]}])
SOL = {'sparse-infill-density': '100%', 'sparse-infill-pattern': 'zig-zag'}
scr = [{'stl': 'screen_plan.stl', 'pos': [0, 0, 0]}]
add('R3_P3b_nosup', P20, dict(SOL, **{'enable-support': '0', 'brim-type': 'no_brim'}), scr)
add('R3_P3b_tree', P20, dict(SOL, **{'enable-support': '1', 'brim-type': 'no_brim'}), scr)                                   # plain trees, the profile's top Z distance
add('R3_P3b_tree_if', P20, dict(SOL, **IFGEO, **{'enable-support': '1', 'brim-type': 'no_brim'}), scr)                       # trees, interface geometry
add('R3_P3b_norm_if', P20, dict(SOL, **IFGEO, **{'enable-support': '1', 'brim-type': 'no_brim', 'support-type': 'normal(auto)'}), scr)   # normal support, interface geometry
add('R3_P3b_norm', P20, dict(SOL, **{'enable-support': '1', 'brim-type': 'no_brim', 'support-type': 'normal(auto)'}), scr)
shell = [{'stl': 'shell_plan.stl', 'assemble': 1, 'pos': list(P3A_POS)},
         {'stl': 'shell_plan_blk_v2.stl', 'assemble': 1, 'subtype': 'support_blocker', 'pos': list(P3A_POS)}]
add('R4_P3a_w2', P20, dict(SHELL_BRIM, **IFGEO), shell)                              # as the print files' stand-in A4s_P3a_1m
add('R4_P3a_w3', P20, dict(SHELL_BRIM, **IFGEO, **{'wall-loops': '3'}), shell)
add('R4_P3a_w4', P20, dict(SHELL_BRIM, **IFGEO, **{'wall-loops': '4'}), shell)
add('R4_P3a_w2_nosup', P20, {'enable-support': '0', 'brim-type': 'no_brim'}, [shell[0]])     # for the regions that start in mid-air
adh = [{'stl': 'shell_chin8_plan.stl', 'assemble': 1, 'pos': list(P3A_POS)},
       {'stl': 'shell_chin8_blk.stl', 'assemble': 1, 'subtype': 'support_blocker', 'pos': list(P3A_POS)}]
add('R0_adh_w2', P20, dict(SHELL_BRIM, **IFGEO), adh)
add('R0_adh_w4', P20, dict(SHELL_BRIM, **IFGEO, **{'wall-loops': '4'}), adh)
add('R5_P5s', P12, {'layer-height': '0.1', 'enable-support': '1', 'support-top-z-distance': '0', 'support-interface-spacing': '0', 'brim-type': 'outer_only',
                    'brim-width': '3', 'brim-object-gap': '0.1'}, [{'stl': 'slab_plan.stl', 'pos': [34, 0, 0]}], bed=ENG)
add('R6_P4', P12, {'enable-support': '0', 'brim-type': 'no_brim', 'initial-layer-print-height': '0.2'}, [
    {'stl': 'cap_plan.stl', 'pos': [0, -28, 0], 'params': {'brim_type': 'brim_ears'}},
    {'stl': 'grommet_plan.stl', 'pos': [0, 52, 0], 'params': dict(enable_support='1', **BRIM3)}], bed=ENG)
add('R7_P6', P20, {'enable-support': '0', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1'}, [{'stl': 'door_plan.stl', 'pos': [0, 0, 0]}])
add('R7_P6_trees', P20, {'enable-support': '1', 'brim-type': 'outer_only', 'brim-width': '5', 'brim-object-gap': '0.1'}, [{'stl': 'door_plan.stl', 'pos': [0, 0, 0]}])   # where would support go
cal = [{'stl': 'cal_frame.stl', 'pos': [128, 128, 0]}, {'stl': 'cal_tower.stl', 'pos': [98, 128, 0]}]
add('R0_cal', P20, {'enable-support': '0', 'brim-type': 'no_brim'}, cal + [{'stl': 'cal_holes_v67.stl', 'pos': [149, 128, 0]}])
add('R0_cal_solid', P20, {'enable-support': '0', 'brim-type': 'no_brim'}, cal + [{'stl': 'cal_holes_v67.stl', 'pos': [149, 128, 0], 'params': SOLID}])

if __name__ == '__main__':
    want = sys.argv[1:]
    os.makedirs(os.path.join(here, 'specs'), exist_ok=True)
    for s in S:
        if want and s['job'] not in want: continue
        json.dump(s, open(os.path.join(here, 'specs', s['job'] + '.json'), 'w'), indent=1)
        d, args = mkjob.build(s)
        print('%-18s %2d args' % (s['job'], len(args)))
