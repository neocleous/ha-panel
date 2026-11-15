# Builds a Fusion call: a loader that checks r2lib.py on the Mac by sha256 and execs it into the call's globals, then one step.
# Usage: python3 mk.py <step> [KEY=VALUE ...]   (KEY=VALUE replaces __KEY__ in the step). Output: fusion/calls/<step>.call.py
import sys, os, hashlib
here = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]
body = open(os.path.join(here, 'fusion', name + '.py')).read()
for kv in sys.argv[2:]:
    k, v = kv.split('=', 1); body = body.replace('__%s__' % k, v)
h = hashlib.sha256(open(os.path.join(here, 'lib', 'r2lib.py'), 'rb').read()).hexdigest()
loader = ("import os, hashlib\n"
          "R2L = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck2/lib/r2lib.py')\n"
          "_s = open(R2L, 'rb').read()\n"
          "if hashlib.sha256(_s).hexdigest() != '%s':\n"
          "    raise RuntimeError('r2lib.py on the Mac differs from the session copy')\n"
          "exec(compile(_s, R2L, 'exec'), globals())\n" % h)
src = loader + '\n# ---- ' + name + ' ----\n' + body
compile(src, name, 'exec')
os.makedirs(os.path.join(here, 'fusion', 'calls'), exist_ok=True)
out = os.path.join(here, 'fusion', 'calls', name + '.call.py')
open(out, 'w').write(src)
print(out, len(src), h[:12])
