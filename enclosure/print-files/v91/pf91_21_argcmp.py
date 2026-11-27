# Print files of version 91: each job's slicer arguments and assembly against the re-check's job it replays. No Fusion object.
# Paths are compared by file name and by content (sha256 of the mesh each names); the title, description, output folder, 3MF name
# and data folder are a print file's own and are listed, not compared.
import os, json, runpy
D = os.path.dirname(os.path.abspath(__file__))
L = runpy.run_path(os.path.join(D, 'pf91_lib.py'))
J = runpy.run_path(os.path.join(D, 'pf91_20_jobs.py'))
OWN = ('--metadata-value', '--outputdir', '--export-3mf', '--datadir', '--load-assemble-list')


def _norm(args):
    out = []; skip = False
    for a in args:
        if skip:
            skip = False; continue
        if a in OWN:
            skip = True; continue
        out.append(a)
    return out


def main():
    for p in J['PLATES']:
        job, st, look, sj = p[0], p[1], p[2], p[3]
        if sj is None:
            continue
        a = json.load(open(os.path.join(L['W'], 'slicer', 'jobs', job, 'args.json')))
        b = json.load(open(os.path.join(L['HOME'], look, 'slicer', 'jobs', sj, 'args.json')))
        A = _norm(a); B = _norm(b)
        da = [x for x in A if x not in B]; db = [x for x in B if x not in A]
        aa = json.load(open(os.path.join(L['W'], 'slicer', 'jobs', job, 'assemble.json')))['plates'][0]['objects']
        ab = json.load(open(os.path.join(L['HOME'], look, 'slicer', 'jobs', sj, 'assemble.json')))['plates'][0]['objects']
        diffs = []
        if len(aa) != len(ab):
            diffs.append('objects %d / %d' % (len(aa), len(ab)))
        for x, y in zip(aa, ab):
            for k in ('count', 'filaments', 'subtype', 'pos_x', 'pos_y', 'pos_z', 'assemble_index', 'print_params'):
                if x.get(k) != y.get(k):
                    diffs.append('%s %s: %s / %s' % (os.path.basename(x['path']), k, x.get(k), y.get(k)))
            if os.path.basename(x['path']) != os.path.basename(y['path']):
                diffs.append('mesh %s / %s' % (os.path.basename(x['path']), os.path.basename(y['path'])))
            elif L['sha'](x['path']) != L['sha'](y['path']):
                A80 = open(x['path'], 'rb').read()[80:]; B80 = open(y['path'], 'rb').read()[80:]
                if A80 != B80:
                    diffs.append('mesh %s: content differs' % os.path.basename(x['path']))
        print('%-8s <- %s/%-20s args: only mine %s | only theirs %s | assembly: %s' % (job, look, sj, da or '-', db or '-', diffs or 'same'))
# END pf91_21_argcmp.py
