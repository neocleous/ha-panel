# HA panel model audit (2026-11-05) block 6c: summary of the audit log for the README (runs and runtimes per script).
#   Reads ~/Documents/v5f_audit_log.json (never the design log) and writes ~/Documents/audit/data/log_summary.json:
#   per script the number of entries, first / last time and the t_s values logged. No Fusion data is touched.
import os, json
from collections import OrderedDict


def run(_context):
    L = json.load(open(os.path.expanduser('~/Documents/v5f_audit_log.json')))
    s = OrderedDict()
    for e in L:
        k = e.get('script', '?')
        d = s.setdefault(k, {'n': 0, 'first': e.get('t'), 'last': e.get('t'), 't_s': []})
        d['n'] += 1; d['last'] = e.get('t')
        t = e.get('data', {}).get('t_s') if isinstance(e.get('data'), dict) else None
        if t is not None:
            d['t_s'].append(t)
    json.dump(s, open(os.path.expanduser('~/Documents/audit/data/log_summary.json'), 'w'), indent=1)
    print(json.dumps({k: [v['n'], v['first'], v['last'], (min(v['t_s']), max(v['t_s'])) if v['t_s'] else None] for k, v in s.items()}))
