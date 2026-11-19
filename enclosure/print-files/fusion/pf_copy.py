# pf_copy. Touches no Fusion object. Copies files named in R2_ARGS['files'] (paths under ~/Documents/HA_panel_renders/, given
#   relative to it) into print_files/_work/cmp/<flat name>, so that the session can stage them for reading. Reads only.
import shutil


def run(_context):
    base = os.path.expanduser('~/Documents/HA_panel_renders/'); dst = os.path.join(R2_DIR, 'cmp'); os.makedirs(dst, exist_ok=True)
    out = {}
    for rel in R2_ARGS['files']:
        src = os.path.join(base, rel)
        name = rel.replace('/', '__')
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(dst, name)); out[rel] = os.path.getsize(src)
        else:
            out[rel] = None
    print(json.dumps(out))
