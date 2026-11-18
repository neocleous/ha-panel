# prints the connector call text: python3 mkbs.py start job1,job2 | poll [job1,job2|ALL]
import sys, os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'r3_bs.py')).read()
mode = sys.argv[1]; arg = sys.argv[2] if len(sys.argv) > 2 else 'ALL'
jobs = arg.split(',') if mode == 'start' else []
src = 'import adsk.core\n' + src.replace("'__MODE__'", repr(mode)).replace('__JOBS__', repr(jobs)).replace("'__ONLY__'", repr(arg if mode == 'poll' else ''))
compile(src, 'r3_bs', 'exec'); print(src)
