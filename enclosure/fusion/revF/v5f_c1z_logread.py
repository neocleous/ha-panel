# read-only helper (2026-11-05): print compact parts of a log entry (lesson 30). Set WANT = (script, step, keys).
import adsk.core, json, os
WANT = ('v5f_c1a_probe_top', 'probe', ('boxes', 'E_bodies_above_z160', 'C_back', 'D_sides'))


def run(_context):
    arr = json.load(open(os.path.expanduser('~/Documents/v5f_log.json')))
    e = [a for a in arr if a['script'] == WANT[0] and a['step'] == WANT[1]][-1]
    out = {'t': e['t']}
    for k in WANT[2]:
        out[k] = e['data'].get(k)
    print(json.dumps(out, separators=(',', ':'))[:30000])
