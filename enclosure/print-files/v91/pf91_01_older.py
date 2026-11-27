# Print files of version 91: the older print files, recorded at the start and compared at the end (they stay untouched).
# Reads only. inv(tag): every file under print_files/ and print_files_v67/ with its size and modification time -> out/pf91_older_<tag>.json
#   cmp(): the end's inventory against the start's.
import os, json, runpy, time
L = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pf91_lib.py'))
DIRS = ('print_files', 'print_files_v67')


def inv(tag='start'):
    rec = {}
    for d in DIRS:
        p = os.path.join(L['HOME'], d)
        for a, b, fs in os.walk(p):
            for f in fs:
                q = os.path.join(a, f); s = os.stat(q)
                rec[os.path.relpath(q, L['HOME'])] = [s.st_size, round(s.st_mtime, 3)]
    L['jdump']('pf91_older_%s.json' % tag, rec)
    print('%s: %d files, %d bytes, newest %s' % (tag, len(rec), sum(v[0] for v in rec.values()),
                                                time.strftime('%Y-%m-%d %H:%M', time.localtime(max(v[1] for v in rec.values())))))


def cmp():
    a = L['jload']('pf91_older_start.json'); inv('end'); b = L['jload']('pf91_older_end.json')
    gone = sorted(set(a) - set(b)); new = sorted(set(b) - set(a)); ch = sorted(k for k in a if k in b and a[k] != b[k])
    print('gone %d, new %d, changed %d' % (len(gone), len(new), len(ch)))
    for k in (gone + new + ch)[:40]:
        print('   ', k, a.get(k), b.get(k))
# END pf91_01_older.py
