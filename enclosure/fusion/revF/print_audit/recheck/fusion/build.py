# Joins rc_common.py and one call script into the text sent to the Fusion connector; writes <name>.call.json for the tool input.
import sys, json, os
here = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]
ro = (sys.argv[2] if len(sys.argv) > 2 else 'ro') == 'ro'
src = open(os.path.join(here, 'rc_common.py')).read() + '\n\n# ---- ' + name + ' ----\n' + open(os.path.join(here, name + '.py')).read()
compile(src, name, 'exec')
os.makedirs(os.path.join(here, 'calls'), exist_ok=True)
open(os.path.join(here, 'calls', name + '.call.py'), 'w').write(src)
print(len(src), 'chars; readOnly', ro)
