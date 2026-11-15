# Joins r2_common.py and one call script into the text sent to the Fusion connector (calls/<name>.call.py).
# Usage: python3 build.py <name> [ro|rw] [KEY=VALUE ...]   (KEY=VALUE replaces __KEY__ in the call script)
import sys, os
here = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]
ro = (sys.argv[2] if len(sys.argv) > 2 else 'ro') == 'ro'
body = open(os.path.join(here, name + '.py')).read()
for kv in sys.argv[3:]:
    k, v = kv.split('=', 1)
    body = body.replace('__%s__' % k, v)
src = open(os.path.join(here, 'r2_common.py')).read() + '\n\n# ---- ' + name + ' ----\n' + body
compile(src, name, 'exec')
os.makedirs(os.path.join(here, 'calls'), exist_ok=True)
open(os.path.join(here, 'calls', name + '.call.py'), 'w').write(src)
print(len(src), 'chars; readOnly', ro)
