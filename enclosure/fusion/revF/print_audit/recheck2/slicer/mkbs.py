# Writes the Fusion call text for r2_bs.py: python3 mkbs.py start job1 job2 ...  |  python3 mkbs.py poll [job1,job2|ALL]
# Jobs are read from $R2_JOBS/<job>/ (mkjob.py). Output: /home/claude/r2/fusion/calls/r2_bs_<mode>.call.py (+ prints its size).
import sys, json, os
here = os.path.dirname(os.path.abspath(__file__)); fus = os.path.join(here, '..', 'fusion')
JOBS = os.environ.get('R2_JOBS', '/home/claude/r2/jobs')
mode = sys.argv[1]
if mode == 'start':
    jobs = sys.argv[2:]; only = 'ALL'
else:
    jobs = []; only = sys.argv[2] if len(sys.argv) > 2 else 'ALL'
lst = [[j, json.load(open(os.path.join(JOBS, j, 'assemble.json'))), json.load(open(os.path.join(JOBS, j, 'args.json')))] for j in jobs]
body = open(os.path.join(fus, 'r2_bs.py')).read().replace('__MODE__', mode).replace('__JOBS__', repr(lst)).replace('__ONLY__', only)
src = open(os.path.join(fus, 'r2_common.py')).read() + '\n\n# ---- r2_bs ----\n' + body
compile(src, 'r2_bs', 'exec')
os.makedirs(os.path.join(fus, 'calls'), exist_ok=True)
out = os.path.join(fus, 'calls', 'r2_bs_%s.call.py' % mode)
open(out, 'w').write(src)
print(out, len(src))
