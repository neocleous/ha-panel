# rc4_bs_probe (block 2 prep): lists the flattened presets Bambu Studio's command line reads (Resources/profiles/BBL/*_full) for the
#   X2D 0.4, ABS / ASA / Support for ABS, and the 0.20 / 0.16 / 0.12 / 0.08 / 0.10 processes. Reads file names only. READ-ONLY.
RC_RES = '/Applications/BambuStudio.app/Contents/Resources/profiles/BBL'


def run(_context):
    out = {'dirs': sorted(d for d in os.listdir(RC_RES) if os.path.isdir(os.path.join(RC_RES, d)))}
    for d, pat in (('machine_full', r'X2D'), ('process_full', r'X2D'), ('filament_full', r'(ABS|ASA|Support for ABS).*X2D 0\.4')):
        p = os.path.join(RC_RES, d)
        out[d] = sorted(f for f in os.listdir(p) if re.search(pat, f)) if os.path.isdir(p) else None
    print(json.dumps(out, separators=(',', ':')))
