# recheck2 block 2: summary of a sliced job from its G-code npz (r2_gparse.py) and result.json.
#   Usage: python3 r2_gsum.py <job> [<job> ...]  (reads /home/claude/r2/gc/<job>.npz and the staged out/<job>/result.json)
#   Part = every feature but support, brim, skirt and prime tower. Masses: Bambu ABS 1.04 g/cm3 (preset), Support for ABS 1.16.
import sys, json, math, numpy as np
A = math.pi * 0.875 ** 2
RHO = {0: 1.04, 1: 1.04}             # tool -> density; overridden per job for Support for ABS
OUT = {}
for job in sys.argv[1:]:
    z = np.load('/home/claude/r2/gc/%s.npz' % job, allow_pickle=True)
    S = z['seg']; F = z['feat']; names = list(z['names']); hdr = json.loads(str(z['header']))
    res = json.load(open('/mnt/user-data/uploads/print_audit_recheck2/slicer/out/%s/result.json' % job))
    pl = res['sliced_plates'][0]
    fil = {f['id']: round(f['total_used_g'], 2) for f in pl.get('filaments', [])}
    cls = {}
    for i, n in enumerate(names):
        c = 'support' if 'Support' in n else ('brim' if n in ('Brim', 'Skirt') else ('tower' if 'tower' in n.lower() else 'part'))
        for t in np.unique(S[F == i, 8]).astype(int):
            v = float(S[(F == i) & (S[:, 8] == t), 5].sum() * A)
            cls.setdefault(c, {}); cls[c]['T%d' % t] = cls[c].get('T%d' % t, 0.0) + v
    o = {'print_min': round(pl['main_predication'] / 60, 1), 'with_prep_min': round(pl['total_predication'] / 60, 1), 'filaments_g': fil,
         'changes': pl.get('filament_change_times'), 'layers': hdr.get('n_layers'),
         'vol_mm3': {c: {t: round(v, 1) for t, v in d.items()} for c, d in cls.items()}}
    part = sum(cls.get('part', {}).values())
    o['part_g_abs'] = round(part * 1.04 / 1000, 2)
    o['feat_mm3'] = {n: round(float(S[F == i, 5].sum() * A), 1) for i, n in enumerate(names)}
    OUT[job] = o
    print(job, json.dumps(o))
json.dump(OUT, open('/home/claude/r2/data/gsum_%s.json' % '_'.join(sys.argv[1:])[:80], 'w'), indent=1)
