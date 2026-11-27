# Print files of version 91: stops background runs of this step that are still going (by the pid each recorded) and starts the hole
# reading again for the plates not yet read, with the bucketed reader. Touches nothing outside print_files_v91/_work/. No Fusion object.
import os, json, signal, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
S = runpy.run_path(os.path.join(D, 'pf91_30_stop.py'))
OUT = os.path.join(L['W'], 'out')


def kill(names):
    for n in names:
        p = os.path.join(OUT, n + '.pid.json')
        if not os.path.exists(p):
            print(n, 'no pid'); continue
        pid = json.load(open(p))['pid']
        if L['_alive'](pid):
            os.killpg(pid, signal.SIGTERM); print(n, 'stopped', pid)
        else:
            print(n, 'had ended')


def holes(wait=0):
    todo = [j for j in list(S['PAIRS']) + ['T00_cal', 'A00_cal'] if not os.path.exists(os.path.join(OUT, 'holes_%s.json' % j))]
    lst = []
    for job in todo:
        if job.endswith('_cal'):
            lst.append({'cmd': 'holes', 'job': os.path.join(S['SO'], job), 'parts': [], 'extra': S['CAL'], 'out': os.path.join(OUT, 'holes_%s.json' % job)}); continue
        parts, pairs = S['PAIRS'][job]
        a = {'cmd': 'holes', 'job': os.path.join(S['SO'], job), 'out': os.path.join(OUT, 'holes_%s.json' % job)}
        if parts:
            a['parts'] = [[p[1], p[2]] for p in parts]
        else:
            m, pos = S['SINGLE'][job]; a['parts'] = [[m, pos]]
            if m == 'shell_chin8':
                a['key'] = {'shell_chin8': 'shell'}
        lst.append(a)
    print('to read:', todo)
    L['tools']([('pf91_holesB_%s' % x['job'].split('/')[-1], 'holes', [x]) for x in lst], wait)
# END pf91_35_rerun.py
