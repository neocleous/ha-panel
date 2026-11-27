# The close (brief block 10): helpers.
#   state()            the document's version, whether it is modified, the counts
#   export(g)          exports the open document as a Fusion archive to ~/Documents/HA Panel v5 - tapered revF-g<g>.f3d (as the
#                      last pass's v68_commit.export did). Refuses if the document is modified or holds TMP_/AUD_ bodies.
#   rerun(specs, cap)  runs earlier check scripts of this pass again and reports what changed in their outputs. Each spec is
#                      (script, sha256, output file, args, kwargs): the output file as it stood is copied to
#                      close_before/<file> (once), the script's main(*args, **kwargs) is run, and the new output is compared with
#                      the copy line by line, leaving out the time-stamp lines. Prints, per output: lines, changed lines, and the
#                      changed lines themselves up to 'cap' (old lines marked '-', new '+').
# Run: runpy.run_path(D + 'p94_close.py')['rerun']([...])
import runpy, hashlib, difflib, io, contextlib, os, shutil
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def state():
    k = L['load'](); X = k.K()
    df = X.doc.dataFile
    names = X.names()
    print('%s  version %d of %d, modified %s, %s; TMP_ %d, AUD_ %d' % (L['stamp'](), df.versionNumber, df.latestVersionNumber, X.doc.isModified, X.state(),
          sum(1 for n in names if n.startswith('TMP_')), sum(1 for n in names if n.startswith('AUD_'))))
    print('description: %s' % df.description)


def export(g):
    k = L['load'](); X = k.K()
    names = X.names()
    if X.doc.isModified or any(n.startswith(('TMP_', 'AUD_')) for n in names):
        raise RuntimeError('the document is modified or holds temporary bodies: not exported')
    path = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g%d.f3d' % g)
    if os.path.exists(path):
        raise RuntimeError('there is already a file at ' + path)
    em = X.des.exportManager
    ok = em.execute(em.createFusionArchiveExportOptions(path))
    df = X.doc.dataFile
    line = '%s  export -> %s: %s, %d bytes, sha256 %s; version %d of %d, modified %s' % (L['stamp'](), path, ok, os.path.getsize(path),
           hashlib.sha256(open(path, 'rb').read()).hexdigest(), df.versionNumber, df.latestVersionNumber, X.doc.isModified)
    open(D + 'p94_export.txt', 'a').write(line + '\n')
    print(line)


def body(t):
    return [l for l in t.splitlines() if not l[:5] in ('2026-',) and 'before {' not in l and 'after {' not in l]


def rerun(specs, cap=40):
    os.makedirs(D + 'close_before', exist_ok=True)
    for script, sha, outfile, args, kwargs in specs:
        got = hashlib.sha256(open(D + script, 'rb').read()).hexdigest()
        if got != sha:
            raise RuntimeError('sha256 of %s is %s' % (script, got))
        old = open(D + outfile).read() if os.path.exists(D + outfile) else ''
        keep = D + 'close_before/' + outfile
        if old and not os.path.exists(keep):
            shutil.copyfile(D + outfile, keep)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            runpy.run_path(D + script)['main'](*args, **kwargs)
        new = open(D + outfile).read()
        a = body(old); b = body(new)
        d = [l for l in difflib.unified_diff(a, b, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---')]
        print('%s %s %s -> %s: %d lines (%d before), changed lines %d%s' % (script, args, kwargs or '', outfile, len(b), len(a), len(d), '' if old else ' (no earlier output)'))
        for l in d[:cap]:
            print('   ' + l[:420])
        if len(d) > cap:
            print('   ... %d more' % (len(d) - cap))
