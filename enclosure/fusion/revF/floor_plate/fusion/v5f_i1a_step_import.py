# rev F i1a (2026-11-11): step 3 repeated, block 1 - the rev 3.1 STEP files into temporary bodies (no change to the panel document).
#   main-board-rev3.1.step and main-board-rev3.1-plug-envelopes.step are fetched from the repo's docs branch at 110497a to fp/step3r
#   (sha256 checked) and imported by h1a unchanged apart from the two file names. The cache keys step_board / step_plugs then hold
#   rev 3.1. The solids are compared with rev 3's (fp/step3/h1a_status.json): every solid whose box differs is listed.
import os, hashlib, urllib.request
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/110497a358fcf0e7d222e1cc588d09d83ec699a5/hardware/main-board/'
SHA = {'main-board-rev3.1.step': '8f3bf046220684c60a6ffec04ccc1511b2f9a880f559c5cfad54911609107fc9',
       'main-board-rev3.1-plug-envelopes.step': '5519ffea17b24ce4bed7ba4259f3f9cdbd4570a4bcf1f7046dff59e083e54462'}


def fetch():
    os.makedirs(S3, exist_ok=True)
    out = {}
    for fn, want in SHA.items():
        p = os.path.join(S3, fn)
        if not (os.path.exists(p) and hashlib.sha256(open(p, 'rb').read()).hexdigest() == want):
            data = urllib.request.urlopen(RAW + fn, timeout=30).read()
            if hashlib.sha256(data).hexdigest() != want:
                raise RuntimeError('sha256 ' + fn)
            open(p, 'wb').write(data)
        out[fn] = os.path.getsize(p)
    return out


def compare():
    old = json.load(open(os.path.join(FP, 'step3', 'h1a_status.json')))
    new = json.load(open(os.path.join(S3, 'i1a_status.json')))
    res = {}
    for key in ('board', 'plugs'):
        a = [(r[0], tuple(r[1])) for r in old[key]['rows']]
        b = [(r[0], tuple(r[1])) for r in new[key]['rows']]
        gone = list(a)
        added = []
        for r in b:
            if r in gone:
                gone.remove(r)
            else:
                added.append(r)
        res[key] = {'rev3 only': [[n, list(q)] for n, q in gone], 'rev3.1 only': [[n, list(q)] for n, q in added], 'same': len(b) - len(added)}
    return res


got = fetch()
purged = purge()
run_h('v5f_h1a_step_import.py', repl=(("'main-board-rev3.step'", "'main-board-rev3.1.step'"),
                                      ("'main-board-rev3-plug-envelopes.step'", "'main-board-rev3.1-plug-envelopes.step'"),
                                      ("status3('h1a', st)", "status3('i1a', st)")))
status3('i1a_compare', {'files': got, 'purged': purged, 'diff': compare()})
