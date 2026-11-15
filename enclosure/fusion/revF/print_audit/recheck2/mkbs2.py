# Short Fusion call for the slicer queue: loads r2lib.py and r2bs.py from the Mac (sha256-checked), sets mode and jobs, runs.
# Usage: python3 mkbs2.py start job1 job2 ... | python3 mkbs2.py poll [job1,job2|ALL]
import sys, os, hashlib
here = os.path.dirname(os.path.abspath(__file__))
h1 = hashlib.sha256(open(os.path.join(here, 'lib', 'r2lib.py'), 'rb').read()).hexdigest()
h2 = hashlib.sha256(open(os.path.join(here, 'lib', 'r2bs.py'), 'rb').read()).hexdigest()
mode = sys.argv[1]
jobs = sys.argv[2:] if mode == 'start' else []
only = 'ALL' if mode == 'start' else (sys.argv[2] if len(sys.argv) > 2 else 'ALL')
src = ("import os, hashlib\n"
       "D = os.path.expanduser('~/Documents/HA_panel_renders/print_audit_recheck2/lib/')\n"
       "for f, h in (('r2lib.py', '%s'), ('r2bs.py', '%s')):\n"
       "    s = open(D + f, 'rb').read()\n"
       "    if hashlib.sha256(s).hexdigest() != h:\n"
       "        raise RuntimeError(f + ' on the Mac differs')\n"
       "    if f == 'r2bs.py':\n"
       "        R2_MODE = %r; R2_JOBS = %r; R2_ONLY = %r\n"
       "    exec(compile(s, D + f, 'exec'), globals())\n") % (h1, h2, mode, jobs, only)
compile(src, 'bs', 'exec')
print(src)
