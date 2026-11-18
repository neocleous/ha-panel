"""recheck3 (D218): every printed part's mass as sliced (version 67, the recommended settings) and the tipping figures restated on the D9 base (D156).
   Base: version 65, 1,055.101 g at (-0.810, -17.836, 79.671) with every printed part solid at 1.05 g/cm3 (ballast hand-over B5; recheck2/offline/r2_tip.py).
   Step 1: take the version-65 printed parts out (B-rep volume x 1.05 at their version-65 centres, r2_tip.PARTS).
   Step 2: put the version-67 parts in at their version-67 centres (Fusion's centre of mass of each body, data/export.json):
           'solid'  = B-rep volume x 1.05;   'sliced' = the slicer's mass of the part's own lines (supports, brims and towers excluded; Bambu ABS 1.04 g/cm3).
   Formulas: r2_tip.figs() unchanged (feet: rear y -70.6, front y -5.5, r 6.35, contact z -3.0; glass top edge (y -6.67, z 174.67); screen centre (5.70, 116.47); door foot y -84.0)."""
import json, sys
sys.path.insert(0, '/home/claude/repo/enclosure/fusion/revF/print_audit/recheck2/offline')
import r2_tip
GD = '/mnt/user-data/uploads/HA_panel_renders/print_audit_recheck3/slicer/out'
EXP = json.load(open('/mnt/user-data/uploads/HA_panel_renders/print_audit_recheck3/data/export.json'))['bodies']
BODY = {'shell': 'HOUSING_F_front', 'screen': 'HOUSING_F_plate', 'spkbox_L': 'SPKBOX_L', 'spkbox_R': 'SPKBOX_R', 'base': 'FLOOR_PLATE', 'carrier': 'RESP_CARRIER', 'cradle': 'CRADLE_5807',
        'door': 'HOUSING_F_door', 'cap': 'HOUSING_F_cap', 'slab': 'SLAB_frame', 'grommet': 'GROMMET_usbc_F', 'clip_L': 'TOUCH_CLIP_L', 'clip_R': 'TOUCH_CLIP_R', 'bme_hood': 'BME_HOOD'}
# part -> (job, object index in the job's label order or None for a one-object job)
REC = {'shell': ('F4_P3a', None), 'screen': ('F3_P3b', None), 'base': ('H1s_P1_solid', 0), 'spkbox_L': ('H1s_P1_solid', 1), 'spkbox_R': ('H1s_P1_solid', 2),
       'carrier': ('H2_P2', 0), 'cradle': ('H2_P2', 1), 'clip_L': ('H2_P2', 2), 'clip_R': ('H2_P2', 3), 'bme_hood': ('H2_P2', 4), 'slab': ('H5_P5s', None),
       'cap': ('H6_P4_capthin', 0), 'grommet': ('H6_P4_capthin', 1), 'door': ('H7_P6_thin', None)}
def sliced_g(job, k):
    gs = json.load(open('%s/%s/gsum.json' % (GD, job))); objs = list(gs['objects'].values())
    o = objs[0] if k is None else objs[k]; return o['part_g'], o.get('support_g', 0.0), o['cls_mm3'].get('part', 0.0)
def restate(masses):
    """masses: part -> grams put in at the version-67 centre."""
    m = r2_tip.BASE['m']; s = [m * c for c in r2_tip.BASE['cog']]
    for k, (v, c) in r2_tip.PARTS.items():
        d = v * 1.05 / 1000.0; m -= d; s = [s[i] - d * c[i] for i in range(3)]
    rest = (m, tuple(x / m for x in s))
    for k, g in masses.items():
        c = EXP[BODY[k]]['com_world']; m += g; s = [s[i] + g * c[i] for i in range(3)]
    cog = tuple(x / m for x in s); return m, cog, r2_tip.figs(m, cog), rest
if __name__ == '__main__':
    solid = {k: EXP[BODY[k]]['vol_mm3'] * 1.05 / 1000.0 for k in BODY}
    sl = {}; rows = []
    for k in BODY:
        g, sup, vol = sliced_g(*REC[k]); sl[k] = g; rows.append((k, EXP[BODY[k]]['vol_mm3'], solid[k], g, 100 * vol / EXP[BODY[k]]['vol_mm3'], REC[k][0]))
    print('%-10s %12s %9s %10s %7s  %s' % ('part', 'B-rep mm3', 'solid g', 'sliced g', 'fill %', 'job'))
    for r in rows: print('%-10s %12.3f %9.2f %10.2f %7.1f  %s' % r)
    print('%-10s %12.3f %9.2f %10.2f' % ('total', sum(r[1] for r in rows), sum(solid.values()), sum(sl.values())))
    v65 = sum(v * 1.05 / 1000.0 for v, c in r2_tip.PARTS.values()); print('version 65 printed parts solid: %.2f g' % v65)
    out = {}
    for lab, ms in (('solid v67', solid), ('as sliced v67', sl), ('as sliced v67, shell with 2 walls', dict(sl, shell=89.67)), ('as sliced v67, screen plate without solid infill n/a', None)):
        if ms is None: continue
        m, cog, f, rest = restate(ms); out[lab] = (m, cog, f)
        print('\n%s: unit %.1f g at (%.2f, %.2f, %.2f) | rest of the unit without printed parts %.1f g at (%.2f, %.2f, %.2f)' % ((lab, m) + tuple(cog) + (rest[0],) + tuple(rest[1])))
        for k in ('back top horizontal', 'back top normal', 'back centre normal', 'back tips at deg', 'fwd tips at deg', 'fwd pull top', 'fwd lift door foot'):
            print('   %-22s %.2f (%.2f)' % (k, f[k + ' centres'], f[k + ' edges']))
        print('   rear share %.1f %%' % f['rear share %'])
    b = r2_tip.figs(r2_tip.BASE['m'], r2_tip.BASE['cog']); print('\nD9 base (version 65 solid):', {k: round(v, 2) for k, v in b.items()})
    json.dump({k: dict(m=v[0], cog=v[1], figs=v[2]) for k, v in out.items()}, open('/home/claude/r3/data/tip_v67.json', 'w'), indent=1)
