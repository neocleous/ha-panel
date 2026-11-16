# pf_open: opens one print-files project in the Mac's Bambu Studio window without bringing it to the front (open -g), so the
#   session can check the two-material setup in the window. Touches no Fusion object and no file.
#   R2_ARGS: {'file': path relative to print_files/}.
import subprocess


def run(_context):
    p = os.path.join(R2_OUTDIR, R2_ARGS['file'])
    if not os.path.exists(p):
        raise RuntimeError('missing: ' + p)
    r = subprocess.run(['/usr/bin/open', '-g', '-a', 'BambuStudio', p], capture_output=True, text=True, timeout=30)
    print(json.dumps({'file': p, 'rc': r.returncode, 'err': r.stderr[-300:]}))
