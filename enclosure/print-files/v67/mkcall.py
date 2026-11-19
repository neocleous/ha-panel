# Short Fusion call for the print files of version 67: loads pflib67.py, any extra lib files and one step file from the Mac's
#   work folder (print_files_v67/_work/lib/, each sha256-checked), with R2_ARGS set first, then execs them into the call's
#   globals (the step defines run()). Every call text is also written to fusion/calls/<step>[_<tag>].call.py, so each call sent
#   is kept as a file (recheck3 lesson 8).
# Usage: python3 mkcall.py <step> '<json args>' [extra_lib.py ...] [--tag=<tag>]  -> prints the call text
import sys, os, hashlib, json
here = os.path.dirname(os.path.abspath(__file__))
argv = [a for a in sys.argv[1:] if not a.startswith('--tag=')]
tag = ([a[6:] for a in sys.argv[1:] if a.startswith('--tag=')] or [''])[0]
step = argv[0]; args = json.loads(argv[1]) if len(argv) > 1 else {}
extra = argv[2:]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


files = [('pflib67.py', sha(os.path.join(here, 'lib', 'pflib67.py')))]
files += [(e, sha(os.path.join(here, 'lib', e))) for e in extra]
files += [('steps/%s.py' % step, sha(os.path.join(here, 'fusion', step + '.py')))]
src = ("import os, hashlib\n"
       "D = os.path.expanduser('~/Documents/HA_panel_renders/print_files_v67/_work/lib/')\n"
       "R2_ARGS = %r\n"
       "for f, h in %r:\n"
       "    s = open(D + f, 'rb').read()\n"
       "    if hashlib.sha256(s).hexdigest() != h:\n"
       "        raise RuntimeError(f + ' on the Mac differs')\n"
       "    exec(compile(s, D + f, 'exec'), globals())\n") % (args, files)
compile(src, 'run', 'exec')
os.makedirs(os.path.join(here, 'fusion', 'calls'), exist_ok=True)
open(os.path.join(here, 'fusion', 'calls', step + ('_' + tag if tag else '') + '.call.py'), 'w').write(src)
print(src)
