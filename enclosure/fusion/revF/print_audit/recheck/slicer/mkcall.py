# Writes the Fusion call text for one Bambu Studio job: rc5_bs_run.py with the job's assemble list and args inlined.
# Usage: python3 mkcall.py <job> start|poll   (after mkjob.py wrote /mnt/user-data/outputs/rc/jobs/<job>/)
import sys, json, os
job, mode = sys.argv[1], sys.argv[2]
d = '/mnt/user-data/outputs/rc/jobs/' + job
src = open('/home/claude/rc/fusion/rc5_bs_run.py').read()
asm = json.load(open(d + '/assemble.json')) if mode == 'start' else None
args = json.load(open(d + '/args.json')) if mode == 'start' else None
src = src.replace('__JOB__', job).replace('__MODE__', mode).replace('__ASSEMBLE__', repr(asm)).replace('__ARGS__', repr(args))
compile(src, 'rc5', 'exec')
os.makedirs('/home/claude/rc/fusion/calls', exist_ok=True)
open('/home/claude/rc/fusion/calls/rc5_%s_%s.py' % (job, mode), 'w').write(src)
print(json.dumps({'readOnly': True, 'script': src}))
