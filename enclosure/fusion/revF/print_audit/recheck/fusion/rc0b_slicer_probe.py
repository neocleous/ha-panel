# HA panel print audit re-check (2026-11-14), block 0: which slicer. READ-ONLY (connector readOnly: true); reads file names only.
#   Lists Bambu Studio's and OrcaSlicer's X2D machine/process presets and the generic ABS/ASA and Support for ABS filament presets
#   in their system profile folders, the profile set version, and the NAMES of the user's own presets (no contents). Writes nothing.
import os, re, json, time


def rc_ls(d, pat):
    if not os.path.isdir(d):
        return None
    return sorted(f for f in os.listdir(d) if re.search(pat, f, re.I))


def run(_context):
    t0 = time.time(); out = {}
    for app, sup in (('bambu', '~/Library/Application Support/BambuStudio'), ('orca', '~/Library/Application Support/OrcaSlicer')):
        s = os.path.expanduser(sup); o = {'support': os.path.isdir(s)}
        sysd = os.path.join(s, 'system')
        o['system'] = sorted(os.listdir(sysd)) if os.path.isdir(sysd) else None
        for vend in ('BBL',):
            b = os.path.join(sysd, vend)
            o['machine_x2d'] = rc_ls(os.path.join(b, 'machine'), r'X2D')
            o['process_x2d'] = rc_ls(os.path.join(b, 'process'), r'X2D')
            o['fil_abs_asa_x2d'] = rc_ls(os.path.join(b, 'filament'), r'(ABS|ASA).*X2D|X2D.*(ABS|ASA)')
            o['fil_support_abs'] = rc_ls(os.path.join(b, 'filament'), r'Support.*ABS')
            vj = os.path.join(sysd, vend + '.json')
            if os.path.exists(vj):
                o['bbl_json_version'] = json.load(open(vj)).get('version')
        ud = os.path.join(s, 'user')
        if os.path.isdir(ud):
            u = {}
            for uid in sorted(os.listdir(ud)):
                p = os.path.join(ud, uid)
                if os.path.isdir(p):
                    u[uid[:4] + '…'] = {kind: rc_ls(os.path.join(p, kind), r'\.json$') for kind in ('machine', 'process', 'filament')}
            o['user'] = u
        out[app] = o
    a = '/Applications/BambuStudio.app/Contents/Resources/profiles/BBL'
    out['bundled_bbl'] = {'machine_x2d': rc_ls(os.path.join(a, 'machine'), r'X2D'), 'process_x2d_n': len(rc_ls(os.path.join(a, 'process'), r'X2D') or [])}
    out['bin'] = [p for p in ('/Applications/BambuStudio.app/Contents/MacOS/BambuStudio', '/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer')
                  if os.path.exists(p)]
    out['t_s'] = round(time.time() - t0, 2)
    print(json.dumps(out, separators=(',', ':')))
