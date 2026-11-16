# pf_bs: sets the slicer queue's mode and jobs from R2_ARGS for lib/pfbs.py (loaded before this file; its run() is the entry).
#   Touches no Fusion object.
R2_MODE = R2_ARGS['mode']; R2_JOBS = R2_ARGS.get('jobs', []); R2_ONLY = R2_ARGS.get('only', 'ALL')
