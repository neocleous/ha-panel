# Short Fusion call: loads r2lib.py and one step file from the Mac's lib folder (both sha256-checked), with R2_ARGS set first.
# Usage: python3 mkrun.py <step> '<json args>'  -> prints the call text; copies the step to /mnt/user-data/outputs/r2/lib/steps/
import sys, os, hashlib, json, shutil
here = os.path.dirname(os.path.abspath(__file__))
step = sys.argv[1]; args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
os.makedirs('/mnt/user-data/outputs/r2/lib/steps', exist_ok=True)
shutil.copy(os.path.join(here, 'fusion', step + '.py'), '/mnt/user-data/outputs/r2/lib/steps/' + step + '.py')
h1 = hashlib.sha256(open(os.path.join(here, 'lib', 'r2lib.py'), 'rb').read()).hexdigest()
h2 = hashlib.sha256(open(os.path.join(here, 'fusion', step + '.py'), 'rb').read()).hexdigest()
src = ("import os, hashlib\n"
       "D = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck2/lib/')\n"
       "R2_ARGS = %r\n"
       "for f, h in (('r2lib.py', '%s'), ('steps/%s.py', '%s')):\n"
       "    s = open(D + f, 'rb').read()\n"
       "    if hashlib.sha256(s).hexdigest() != h:\n"
       "        raise RuntimeError(f + ' on the Mac differs')\n"
       "    exec(compile(s, D + f, 'exec'), globals())\n") % (args, h1, step, h2)
compile(src, 'run', 'exec')
print(src)
