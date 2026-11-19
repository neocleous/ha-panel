# Short Fusion call: loads pflib.py, any extra lib files and one step file from the Mac's work folder (each sha256-checked),
#   with R2_ARGS set first, then execs them into the call's globals (the step defines run()).
# Usage: python3 mkcall.py <step> '<json args>' [extra_lib.py ...]  -> prints the call text (also fusion/calls/<step>.call.py)
import sys, os, hashlib, json
here = os.path.dirname(os.path.abspath(__file__))
step = sys.argv[1]; args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
extra = sys.argv[3:]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


files = [('pflib.py', sha(os.path.join(here, 'lib', 'pflib.py')))]
files += [(e, sha(os.path.join(here, 'lib', e))) for e in extra]
files += [('steps/%s.py' % step, sha(os.path.join(here, 'fusion', step + '.py')))]
src = ("import os, hashlib\n"
       "D = os.path.expanduser('~/Documents/HA_panel_renders/print_files/_work/lib/')\n"
       "R2_ARGS = %r\n"
       "for f, h in %r:\n"
       "    s = open(D + f, 'rb').read()\n"
       "    if hashlib.sha256(s).hexdigest() != h:\n"
       "        raise RuntimeError(f + ' on the Mac differs')\n"
       "    exec(compile(s, D + f, 'exec'), globals())\n") % (args, files)
compile(src, 'run', 'exec')
os.makedirs(os.path.join(here, 'fusion', 'calls'), exist_ok=True)
open(os.path.join(here, 'fusion', 'calls', step + '.call.py'), 'w').write(src)
print(src)
