# Print files of version 91, block 4: plate P7 in PLA. The re-check never sliced it as a plate; its PLA slices of the clamps were
# each alone with classic walls (print_recheck_v91 pl_clampL, pl_clampR), its holder's with Arachne (print_recheck_v79 pl_holder).
# The brief and D470 put Arachne on the whole of P7 in both sets. No Fusion object.
#   flows(): each filament's flow ratio in the flat presets (the scale between a PLA slice's volumes and an ABS slice's).
#   alt():   job T04b_P7: the same plate with Arachne on the holder only (classic walls on the clamps), sliced for the comparison.
#   cmp():   T04 against the ABS plate A04 (identical to the re-check's ABS P7) scaled by the flows; T04b against the re-check's
#            PLA slices of the clamps and the holder.
import os, json, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
OUT = os.path.join(L['W'], 'out'); SO = os.path.join(L['W'], 'slicer', 'out')
P7 = [['clamp_L', 'clamp_L', [-20, 60, 0]], ['clamp_R', 'clamp_R', [20, 60, 0]], ['holder', 'holder', [0, -60, 0]]]


def _flow(f):
    d = json.load(open(os.path.join(L['FLAT'], f))); v = d.get('filament_flow_ratio')
    return float(v[0] if isinstance(v, list) else v)


def flows():
    a = _flow('filament_BambuPLABasic_black.json'); b = _flow('filament_BambuABS_black.json')
    print('flow ratio: PLA Basic black %.4f, ABS black %.4f, PLA / ABS %.4f' % (a, b, a / b))
    return a / b


def alt(start=True):
    s = json.load(open(os.path.join(L['W'], 'slicer', 'jobs', 'T04_P7', 'spec.json')))
    s['job'] = 'T04b_P7'; s.pop('deliver', None)
    s['opts'] = {k: v for k, v in s['opts'].items() if k != 'wall-generator'}
    for o in s['plates'][0]['objects']:
        if o['stl'] == 'holder.stl':
            o.setdefault('params', {})['wall_generator'] = 'arachne'
    s['title'] = 'v91 TRIAL PLA P7 clamps and holder - alternative - Arachne on the holder only'
    s['desc'] = 'work slice for the comparison - not a print file'
    L['mkjob'](s)
    if start:
        L['slicer']('start', ['T04b_P7'])


def cmp(wait=40):
    sc = flows(); lst = []
    lst.append({'cmd': 'gsum', 'job': os.path.join(SO, 'T04b_P7'), 'out': os.path.join(OUT, 'gsum_T04b_P7.json'), 'parts': P7})
    lst.append({'cmd': 'gcmp', 'a': os.path.join(OUT, 'gsum_T04_P7.json'), 'b': os.path.join(OUT, 'gsum_A04_P7.json'), 'scale': sc,
                'label': 'PLA P7 against ABS P7, scaled', 'parts': [['clamp_L', 'clamp_L'], ['clamp_R', 'clamp_R'], ['holder', 'holder']],
                'out': os.path.join(OUT, 'gcmp_T04_vs_A04.json')})
    for (lab, look, r, mp) in (('T04b clamp L', 'v91', 'pl_clampL', 'clamp_L'), ('T04b clamp R', 'v91', 'pl_clampR', 'clamp_R'), ('T04b holder', 'v79', 'pl_holder', 'holder')):
        lst.append({'cmd': 'gcmp', 'a': os.path.join(OUT, 'gsum_T04b_P7.json'), 'b': os.path.join(OUT, 'gsum_ref_%s_%s.json' % (look, r)),
                    'label': lab, 'parts': [[mp, '_plate']], 'out': os.path.join(OUT, 'gcmp_T04b_%s.json' % mp)})
    L['tools']([('pf91_p7cmp', 'gcmp', lst)], wait)
    print(open(os.path.join(OUT, 'pf91_p7cmp.txt')).read())
# END pf91_32_p7.py
