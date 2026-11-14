# Writes the Fusion call text for a batch of Bambu Studio jobs (rc6_bs_batch.py), jobs from /mnt/user-data/outputs/rc/jobs/<job>/.
# Usage: python3 mkbatch.py start job1 job2 ...  |  python3 mkbatch.py poll
import sys, json, os
mode = sys.argv[1]; jobs = sys.argv[2:]
src = open('/home/claude/rc/fusion/rc6_bs_batch.py').read()
lst = []
for j in jobs:
    d = '/mnt/user-data/outputs/rc/jobs/' + j
    lst.append([j, json.load(open(d + '/assemble.json')), json.load(open(d + '/args.json'))])
src = src.replace('__MODE__', mode).replace('__JOBS__', repr(lst))
compile(src, 'rc6', 'exec')
name = '/home/claude/rc/fusion/calls/rc6_%s_%s.py' % (mode, '_'.join(jobs)[:60] if jobs else 'all')
open(name, 'w').write(src)
print(name, len(src))
