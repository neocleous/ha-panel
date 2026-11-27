# Print files of version 91, blocks 2 and 3: the jobs. No Fusion object.
# Every plate of both sets is the re-check's own job for that plate, replayed: the same process, filaments, bed, options, places,
# blockers and enforcers (its spec.json, read where it is), with this step's meshes (block 1: the same bytes as the re-check's) and
# a print file's title, description, plate name and place to be delivered. What differs from the re-check's job is listed in CHG.
#   jobs(which): writes the jobs ('pla', 'abs' or both).   start(names): starts them in the slicer's queue.   status(): one line a job.
import os, json, runpy, io, contextlib, time
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
H = L['HOME']; SL = '02.09.02.62'
PLA = ['filament_BambuPLABasic_black.json']; ABS = ['filament_BambuABS_black.json']; SFA = 'filament_SupportABS_white.json'
STD = 'process_0.20_Standard.json'
F1 = '1_PLA_trial'; F2 = '2_ABS_calibration_and_adhesion_test'; F3 = '3_ABS_black_set'
SOLID = {'sparse_infill_density': '100%', 'sparse_infill_pattern': 'zig-zag'}
CAL_OBJS = [{'stl': '../cal/cal_frame.stl', 'pos': [128, 128, 0]}, {'stl': '../cal/cal_tower.stl', 'pos': [98, 128, 0]},
            {'stl': '../cal/cal_holes_v67.stl', 'pos': [149, 128, 0], 'params': SOLID},
            {'stl': '../cal/cal_add_v91.stl', 'pos': [128, 100, 0], 'params': SOLID}]
CAL_DESC = ('Frame 120 outside and 108 inside, 5 tall. Tower 20 x 20 x 30. Hole block of version 67 (solid) with the lying 2.7 pilot in its lug. '
            'Block of version 91 (solid): two upright and one lying 1.6 pilots, a lying 2.7 pilot 9.0 deep, a 2.0 hole from the first layer, '
            'a 4.0 insert hole with 1.6 of wall. Measure as the print sheet of version 91 says.')
# (job, set, re-check look, re-check job, folder, file, plate name, what the plate holds, changes against the re-check's job)
PLATES = [
    ('T00_cal', 'pla', None, None, F1, 'TRIAL_PLA_00_calibration_v91.3mf', 'v91 TRIAL PLA calibration | TPEI', 'calibration plate', {}),
    ('T01_P1a', 'pla', 'print_recheck_v85', 'pl_base', F1, 'TRIAL_PLA_01_P1a_base_plate_v91.3mf', 'v91 TRIAL PLA P1a base plate | TPEI', 'base plate', {}),
    ('T02_P1b', 'pla', 'print_recheck_v91', 'p_P1b_clips_pla', F1, 'TRIAL_PLA_02_P1b_boxes_and_clips_v91.3mf', 'v91 TRIAL PLA P1b boxes and clips | TPEI', 'both speaker boxes and both touch clips, solid', {}),
    ('T03_P2', 'pla', 'print_recheck_v85', 'p_P2_noclip_pla', F1, 'TRIAL_PLA_03_P2_carrier_cradle_hood_v91.3mf', 'v91 TRIAL PLA P2 carrier cradle hood | TPEI', 'ReSpeaker carrier, 5807 cradle, BME680 hood', {}),
    ('T04_P7', 'pla', 'print_recheck_v91', 'p_P7_clamps_holder', F1, 'TRIAL_PLA_04_P7_clamps_and_holder_v91.3mf', 'v91 TRIAL PLA P7 clamps and holder | TPEI', 'both microphone clamps and the radar holder', {'pla_from_abs': True}),
    ('T05_P3b', 'pla', 'print_recheck_v79', 'pl_screen', F1, 'TRIAL_PLA_05_P3b_screen_plate_v91.3mf', 'v91 TRIAL PLA P3b screen plate | TPEI', 'screen plate, solid', {}),
    ('T06_P3a', 'pla', 'print_recheck_v91', 'pl_shell', F1, 'TRIAL_PLA_06_P3a_shell_v91.3mf', 'v91 TRIAL PLA P3a shell | TPEI', 'front shell, chin down', {}),
    ('T07_P5', 'pla', 'print_recheck_v79', 'pl_slab', F1, 'TRIAL_PLA_07_P5_slab_v91.3mf', 'v91 TRIAL PLA P5 slab | TPEI', 'slab, glass side down', {'bed': 'Textured PEI Plate'}),
    ('T08_P4a', 'pla', 'print_recheck_v79', 'pl_cap', F1, 'TRIAL_PLA_08_P4a_cap_v91.3mf', 'v91 TRIAL PLA P4a cap | TPEI', 'top cap, top face down, 0.10 layers', {'bed': 'Textured PEI Plate'}),
    ('T09_P4b', 'pla', 'print_recheck_v79', 'pl_grommet', F1, 'TRIAL_PLA_09_P4b_grommet_v91.3mf', 'v91 TRIAL PLA P4b grommet | TPEI', 'USB-C grommet', {'bed': 'Textured PEI Plate'}),
    ('T10_P6', 'pla', 'print_recheck_v91', 'pl_door', F1, 'TRIAL_PLA_10_P6_door_v91.3mf', 'v91 TRIAL PLA P6 door | TPEI', 'rear door, standing', {}),
    ('A00_cal', 'abs', None, None, F2, 'ABS_00_calibration_v91.3mf', 'v91 ABS calibration | TPEI + glue', 'calibration plate', {}),
    ('A00_adh', 'abs', 'print_recheck_v91', 'f2_chin8', F2, 'ABS_00b_adhesion_test_v91.3mf', 'v91 ABS adhesion test shell 8 mm | TPEI + glue', "the shell's first 8.0 mm", {}),
    ('A01_P1a', 'abs', 'print_recheck_v85', 'f2_base', F3, 'ABS_01_P1a_base_plate_v91.3mf', 'v91 ABS P1a base plate | TPEI + glue', 'base plate, all support in Support for ABS', {}),
    ('A02_P1b', 'abs', 'print_recheck_v91', 'p_P1b_clips', F3, 'ABS_02_P1b_boxes_and_clips_v91.3mf', 'v91 ABS P1b boxes and clips | TPEI + glue', 'both speaker boxes and both touch clips, solid', {}),
    ('A03_P2', 'abs', 'print_recheck_v85', 'p_P2_noclip', F3, 'ABS_03_P2_carrier_cradle_hood_v91.3mf', 'v91 ABS P2 carrier cradle hood | TPEI + glue', 'ReSpeaker carrier, 5807 cradle, BME680 hood, one material', {}),
    ('A04_P7', 'abs', 'print_recheck_v91', 'p_P7_clamps_holder', F3, 'ABS_04_P7_clamps_and_holder_v91.3mf', 'v91 ABS P7 clamps and holder | TPEI + glue', 'both microphone clamps and the radar holder', {}),
    ('A05_P3b', 'abs', 'print_recheck_v79', 'f2_screen', F3, 'ABS_05_P3b_screen_plate_v91.3mf', 'v91 ABS P3b screen plate | TPEI + glue', 'screen plate, solid', {}),
    ('A06_P3a', 'abs', 'print_recheck_v91', 'f2_shell', F3, 'ABS_06_P3a_shell_v91.3mf', 'v91 ABS P3a shell | TPEI + glue', 'front shell, chin down', {}),
    ('A07_P5', 'abs', 'print_recheck_v79', 'f2_slab', F3, 'ABS_07_P5_slab_v91.3mf', 'v91 ABS P5 slab | Engineering + glue', 'slab, glass side down, all support in Support for ABS', {}),
    ('A08_P4a', 'abs', 'print_recheck_v79', 'f2_cap', F3, 'ABS_08_P4a_cap_v91.3mf', 'v91 ABS P4a cap | Engineering + glue', 'top cap, top face down, 0.10 layers, one material', {}),
    ('A09_P4b', 'abs', 'print_recheck_v79', 'f2_grommet', F3, 'ABS_09_P4b_grommet_v91.3mf', 'v91 ABS P4b grommet | Engineering + glue', 'USB-C grommet', {}),
    ('A10_P6', 'abs', 'print_recheck_v91', 'f2_door', F3, 'ABS_10_P6_door_v91.3mf', 'v91 ABS P6 door | TPEI + glue', 'rear door, standing', {}),
]
PLAIN = {'support-top-z-distance': '0.2', 'support-interface-spacing': '0.5'}


def _src(look, job):
    return json.load(open(os.path.join(H, look, 'slicer', 'jobs', job, 'spec.json')))


def make(p):
    job, st, look, sj, folder, fn, pname, what, chg = p
    glue = 'with glue' if st == 'abs' else 'no glue'
    if sj is None:                                                   # the calibration plate
        fil = PLA if st == 'pla' else ABS
        s = {'job': job, 'process': STD, 'filaments': fil, 'bed': 'Textured PEI Plate', 'opts': {'enable-support': '0', 'brim-type': 'no_brim'},
             'plates': [{'name': pname, 'objects': [dict(o) for o in CAL_OBJS]}]}
        src = 'version 67 T0_cal / A0_cal with the block of version 91'
    else:
        r = _src(look, sj); src = '%s/%s' % (look, sj)
        s = {'job': job, 'process': r['process'], 'filaments': list(r['filaments']), 'bed': r['bed'], 'opts': dict(r['opts']),
             'plates': [{'name': pname, 'objects': [dict(o) for o in r['plates'][0]['objects']]}]}
        if r.get('map'):
            s['map'] = r['map']
        if chg.get('pla_from_abs'):                                  # P7 in PLA: the ABS plate's parts and places, one material, plain trees
            s['filaments'] = list(PLA)
            o = {k: v for k, v in s['opts'].items() if k not in ('support-interface-filament', 'enable-prime-tower', 'filament-map', 'wipe-tower-x', 'wipe-tower-y', 'prime-tower-width')}
            o.update(PLAIN); s['opts'] = o
        if chg.get('bed'):
            s['bed'] = chg['bed']
    for o in s['plates'][0]['objects']:
        o['stl'] = o['stl'] if o['stl'].startswith('../') else o['stl']
    s['title'] = pname
    s['desc'] = ('HA panel version 91 print file - %s. %s - %s - %s. Sliced headless on Bambu Studio %s. Enter your calibrated Shrinkage '
                 'in the filament settings and slice again before printing.' % (what, 'PLA trial' if st == 'pla' else 'black ABS',
                                                                                 s['bed'].replace(' Plate', ''), glue, SL))
    if st == 'pla' and job == 'T00_cal' or job == 'A00_cal':
        s['desc'] += ' ' + CAL_DESC
    s['deliver'] = [folder, fn]; s['source'] = src; s['changes'] = chg
    L['mkjob'](s)
    return job


def jobs(which=('pla', 'abs')):
    names = [make(p) for p in PLATES if p[1] in which]
    print(names)
    return names


def start(names=None, which=('pla', 'abs')):
    names = names or [p[0] for p in PLATES if p[1] in which]
    L['slicer']('start', names)


def status():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        L['slicer']('poll')
    j = json.loads(buf.getvalue().split('\n')[0]); lines = [time.strftime('%Y-%m-%d %H:%M:%S') + ' pending %d' % len(j['pending'])]
    for x in j['states']:
        pl = (x.get('plates') or [[None, 0, 0, [0], 0, '']])[0]
        lines.append('%-9s %-7s rc %-4s %7.1f min %7.1f with prep  g %-16s changes %-3s %s' % (
            x['job'], x['state'], x.get('rc'), pl[1], pl[2], pl[3], pl[4], (pl[5] or x.get('err') or '')[:90]))
    open(os.path.join(L['W'], 'out', 'status.txt'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
# END pf91_20_jobs.py
