# Print files of version 91, block 0: the preflight. READ-ONLY on the design.
#   main(tag): document, version, counts, the 17 guard volumes by both readings, one lump each.
#   env():     the slicer's version; the chain's files (sha256); the offline Python; the re-check's slices this step compares with.
import os, re, json, runpy, plistlib, subprocess
L = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pf91_lib.py'))

# the re-check's own slice of each plate, as its reports have them (block 5 of the third look; D509, D545)
REF = {'adhesion': ('print_recheck_v91', 'f2_chin8'), 'P1a': ('print_recheck_v85', 'f2_base'), 'P1b': ('print_recheck_v91', 'p_P1b_clips'),
       'P2': ('print_recheck_v85', 'p_P2_noclip'), 'P7': ('print_recheck_v91', 'p_P7_clamps_holder'), 'P3b': ('print_recheck_v79', 'f2_screen'),
       'P3a': ('print_recheck_v91', 'f2_shell'), 'P5': ('print_recheck_v79', 'f2_slab'), 'P4a': ('print_recheck_v79', 'f2_cap'),
       'P4b': ('print_recheck_v79', 'f2_grommet'), 'P6': ('print_recheck_v91', 'f2_door'),
       'PLA P1a': ('print_recheck_v85', 'pl_base'), 'PLA P1b': ('print_recheck_v91', 'p_P1b_clips_pla'), 'PLA P2': ('print_recheck_v85', 'p_P2_noclip_pla'),
       'PLA clamps': ('print_recheck_v91', 'pl_clampL'), 'PLA clampR': ('print_recheck_v91', 'pl_clampR'), 'PLA holder': ('print_recheck_v79', 'pl_holder'),
       'PLA P3b': ('print_recheck_v79', 'pl_screen'), 'PLA P3a': ('print_recheck_v91', 'pl_shell'), 'PLA P5': ('print_recheck_v79', 'pl_slab'),
       'PLA P4a': ('print_recheck_v79', 'pl_cap'), 'PLA P4b': ('print_recheck_v79', 'pl_grommet'), 'PLA P6': ('print_recheck_v91', 'pl_door')}


def main(tag='start'):
    rep, root = L['guard'](strict=False, very_high=True)
    print('read at', rep['t'])
    print('document %r, version %d of %d, modified %s' % (rep['doc'], rep['version'][0], rep['version'][1], rep['modified']))
    try:
        app, doc, des, _r = L['ctx'](); print('version description: %r' % (doc.dataFile.description,))
    except Exception as e:
        print('version description: NOT READ (%s)' % str(e)[:120])
    print('bodies %d, visible %d, _v79 %d, _v85 %d, _v88 %d, older copies %d, AUD_ %s, TMP_/NEW_/R91_/PF91_ %s, duplicate names %s' % (
        rep['bodies'], rep['visible'], len(rep['copies_v79']), len(rep['copies_v85']), len(rep['copies_v88']), rep['older'], rep['AUD'], rep['TMP'], rep['dups']))
    print('%-16s %13s %13s %13s %13s  lumps' % ('body', 'preflight', 'brief', 'very high', 'brief'))
    for n, (vp, vh) in L['GUARD'].items():
        r = rep['vols'].get(n)
        if not r:
            print('%-16s MISSING' % n); continue
        ok = abs(r['pre'] - vp) <= 0.001 and abs(r['vh'] - vh) <= 0.001 and r['lumps'] == 1
        print('%-16s %13.3f %13.3f %13.3f %13.3f  %d  %s' % (n, r['pre'], vp, r['vh'], vh, r['lumps'], 'equal' if ok else 'DIFFERS by %+.3f / %+.3f' % (r['pre'] - vp, r['vh'] - vh)))
    print('guard:', 'AS THE BRIEF' if not rep['bad'] else 'DIFFERS %s' % rep['bad'])
    app, doc, des, _r = L['ctx']()
    print('document modified after the reading:', doc.isModified)
    L['jdump']('pf91_00_preflight_%s.json' % tag, rep)


def env():
    pl = plistlib.load(open(os.path.join(L['BS_APP'], 'Contents', 'Info.plist'), 'rb'))
    print('Bambu Studio: CFBundleShortVersionString %s, CFBundleVersion %s; bundle modified %s' % (
        pl.get('CFBundleShortVersionString'), pl.get('CFBundleVersion'),
        __import__('time').strftime('%Y-%m-%d %H:%M', __import__('time').localtime(os.path.getmtime(L['BS_APP'])))))
    apps = [a for a in os.listdir('/Applications') if 'bambu' in a.lower()]
    print('copies in /Applications:', apps)
    r = subprocess.run([L['PY'], '--version'], capture_output=True, text=True, timeout=10, env=L['_env']())
    print('offline python:', L['PY'], (r.stdout + r.stderr).strip())
    for p in (L['PFBS'], L['CGQ'], os.path.join(L['RD91'], 'r91_lin.py'), os.path.join(L['RD91'], 'r91_tools.py'), os.path.join(L['RD91'], 'r91_26_blk.py'),
              os.path.join(L['RD91'], 'out', 'r91_orient.json'), os.path.join(L['RD91'], 'out', 'r91_21_holes.json')):
        print('sha256 %s  %s' % ((L['sha'](p) or 'MISSING')[:16], p.replace(L['HOME'] + '/', '')))
    for f in sorted(os.listdir(L['FLAT'])):
        print('flat preset  %s  %s' % (L['sha'](os.path.join(L['FLAT'], f))[:16], f))
    print('the re-check\'s slices this step compares with:')
    for k, (d, j) in REF.items():
        od = os.path.join(L['HOME'], d, 'slicer', 'out', j)
        rp = os.path.join(od, 'result.json'); res = json.load(open(rp)) if os.path.exists(rp) else {}
        g = os.path.join(od, 'plate_1.gcode'); ver = None
        if os.path.exists(g):
            with open(g, errors='replace') as f:
                for i, ln in enumerate(f):
                    m = re.search(r'BambuStudio\s+([0-9.]+)', ln)
                    if m:
                        ver = m.group(1); break
                    if i > 40:
                        break
        pls = res.get('sliced_plates') or [{}]
        print('   %-11s %s/%-20s rc %s | gcode %s | slicer %s | %.1f min | g %s' % (
            k, d, j, res.get('return_code'), os.path.exists(g), ver, pls[0].get('main_predication', 0) / 60.0,
            [round(f.get('total_used_g', 0), 2) for f in pls[0].get('filaments', [])]))
    for d in ('stl/bed', 'stl/world'):
        p = os.path.join(L['RD91'], d); print('print_recheck_v91/%s: %d files' % (d, len(os.listdir(p))))
    for d in ('print_files', 'print_files_v67'):
        p = os.path.join(L['HOME'], d); n = 0; tot = 0
        for a, b, fs in os.walk(p):
            for f in fs:
                if f.endswith('.3mf'):
                    n += 1; tot += os.path.getsize(os.path.join(a, f))
        print('older print files untouched check: %s: %d .3mf, %d bytes' % (d, n, tot))
# END pf91_00_preflight.py
