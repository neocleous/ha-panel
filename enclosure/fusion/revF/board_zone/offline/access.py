"""Reach check for plugging the main board's front-face XH leads after the board is mounted (assembly step 10: door, cap,
cradle, BME680 and LD2410C not fitted yet; Pi, Pi-power adapter/cable/plug, LCD + ReSpeaker, GPIO plugs, bracket, boxes,
touch board in). Voxels 1 mm, x_rel -75..75, z -5..190, y -100..20. Obstacles: the meshes listed below (column intervals
from bz.py), the board slab and its front parts (KiCad courtyards x MAIN_env heights); leads and keep-outs are not obstacles.
A finger is a ball of radius r; it is reachable where its centre can travel from outside (behind the open back, or down
through the cap opening) to a point touching the top of the target plug (y -53.6). The hand is a ball of radius rh; the
finger length needed is the geodesic distance (26-neighbour steps, mm) from the hand's reach to the target."""
import numpy as np, sys, json
sys.path.insert(0, '.')
import bz
from scipy import ndimage
sys.path.insert(0, '.'); from kpcb import parse, footprints
M = '/mnt/user-data/uploads/HA_panel_renders/board_zone/mesh/'
EXP = '/mnt/user-data/uploads/HA_panel_renders/print_audit/exports/'
BODIES = {'front_d22': EXP + 'front_d22.stl', 'slab': EXP + 'slab.stl'}
for n in ['SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'PI5_F', 'PI5_F_cooler',
          'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'RESP_CARRIER',
          'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'LCD_pcb_76x110', 'LCD_components_env_d8.8',
          'MAIN_BRACKET', 'CRADLE_5807', 'PD_5807_env']:
    BODIES[n] = M + n + '.stl'
X0, X1, Z0, Z1, Y0, Y1 = -75, 75, -5, 190, -100, 20
NX, NZ, NY = X1 - X0, Z1 - Z0, Y1 - Y0
HEIGHT = {'PS1': 27.5, 'C5': 16, 'C6': 16, 'C7': 12.5, 'J1': 9.8, 'J5': 9.8, 'J6': 9.8, 'J8': 9.8, 'J9': 9.8, 'L1': 6.5,
          'L100': 5.4, 'L101': 5.4, 'L102': 5.4, 'L103': 5.4, 'F1': 2.94, 'F2': 2.94, 'F3': 2.94, 'D1': 2.7, 'D2': 2.7,
          'F5': 1.8, 'J3': 4.0, 'J4': 4.0, 'J7': 4.0, 'J10': 4.0}

def occupancy(names):
    occ = np.zeros((NX, NZ, NY), bool)
    for nm in names:
        (c, y0, y1), bad, vol = bz.body_intervals(BODIES[nm], '../bz/cache')
        x, z = bz.cell_xz(c)
        ix = np.floor(x - X0).astype(int); iz = np.floor(z - Z0).astype(int)
        ok = (ix >= 0) & (ix < NX) & (iz >= 0) & (iz < NZ)
        ix, iz, y0, y1 = ix[ok], iz[ok], y0[ok], y1[ok]
        j0 = np.clip(np.floor(y0 - Y0).astype(int), 0, NY - 1); j1 = np.clip(np.ceil(y1 - Y0).astype(int), 0, NY)
        for a in range(len(ix)):
            occ[ix[a], iz[a], j0[a]:j1[a]] = True
    return occ

def add_box(occ, x0, x1, z0, z1, y0, y1):
    i0, i1 = int(np.floor(min(x0, x1) - X0)), int(np.ceil(max(x0, x1) - X0))
    k0, k1 = int(np.floor(min(z0, z1) - Z0)), int(np.ceil(max(z0, z1) - Z0))
    j0, j1 = int(np.floor(min(y0, y1) - Y0)), int(np.ceil(max(y0, y1) - Y0))
    occ[max(i0, 0):min(i1, NX), max(k0, 0):min(k1, NZ), max(j0, 0):min(j1, NY)] = True

def board(occ, top, fps):
    add_box(occ, -45, 45, 34, top, -65.0, -63.4)
    for f in fps:
        if f['layer'] != 'F.Cu' or not f['crt'] or (f['ref'] or '').startswith('H'):
            continue
        h = HEIGHT.get(f['ref'], 1.8)
        xs = [45 - p[0] for p in f['crt']]; zs = [84 - p[1] for p in f['crt']]
        add_box(occ, min(xs), max(xs), min(zs), max(zs), -63.4, -63.4 + h)

def targets(fps):
    out = {}
    for f in fps:
        if f['ref'] in ('J1', 'J5', 'J6', 'J8', 'J9'):
            xs = [45 - p[0] for p in f['crt']]; zs = [84 - p[1] for p in f['crt']]
            out[f['ref']] = (min(xs) + 0.75, max(xs) - 0.75, min(zs) + 0.75, max(zs) - 0.75)    # plug top, inside the courtyard
    return out

def run(top, with_cradle, r, rh, fps, base_occ):
    occ = base_occ.copy()
    board(occ, top, fps)
    if not with_cradle:
        pass
    free = ~occ
    edt = ndimage.distance_transform_edt(np.pad(free, 1, constant_values=True))[1:-1, 1:-1, 1:-1]
    seed = (int(0 - X0), int(60 - Z0), int(-97 - Y0))                     # behind the open back
    res = {}
    for rad, key in ((r, 'finger'), (rh, 'hand')):
        cs = edt >= rad
        lab, n = ndimage.label(cs, structure=np.ones((3, 3, 3)))
        res[key] = lab == lab[seed]
    fin, hand = res['finger'], res['hand']
    # geodesic steps from the hand set inside the finger space
    dist = np.full(fin.shape, -1, np.int32); dist[hand & fin] = 0
    front = hand & fin; reached = front.copy(); step = 0
    st = np.ones((3, 3, 3), bool)
    tg = targets(fps); out = {}
    tmask = {}
    for k, (xa, xb, za, zb) in tg.items():
        m = np.zeros(fin.shape, bool)
        jc = int(round(-53.6 + r - Y0))
        m[int(np.ceil(xa - X0)):int(np.floor(xb - X0)) + 1, int(np.ceil(za - Z0)):int(np.floor(zb - Z0)) + 1, jc - 1:jc + 2] = True
        tmask[k] = m
        out[k] = {'touch_cells': int(m.sum()), 'reachable': bool((m & fin).any())}
    pending = {k for k in tmask if out[k]['reachable']}
    while pending and step < 400:
        step += 1
        nxt = ndimage.binary_dilation(front, st) & fin & ~reached
        if not nxt.any(): break
        reached |= nxt; front = nxt
        for k in list(pending):
            if (tmask[k] & nxt).any():
                out[k]['finger_beyond_hand_mm'] = step; pending.discard(k)
    return out

if __name__ == '__main__':
    t = parse(open('/home/claude/ha-panel/hardware/main-board/main-board.kicad_pcb').read())
    fps = footprints(t)
    names_10 = [n for n in BODIES if n not in ('CRADLE_5807', 'PD_5807_env')]
    occ10 = occupancy(names_10)
    occ11 = occupancy(list(BODIES))
    rows = []
    for top in (84, 89):
        for r, rh in ((7, 15), (8, 15), (7, 20)):
            for label, occ in (('step 10 (no cradle)', occ10), ('step 11 (cradle in)', occ11)):
                o = run(top, label.startswith('step 11'), r, rh, fps, occ)
                rows.append([top, r, rh, label, o])
                print('top %d  finger r %d  hand r %d  %-20s' % (top, r, rh, label),
                      '  '.join('%s %s%s' % (k, 'yes' if v['reachable'] else 'NO', (' +%d' % v['finger_beyond_hand_mm']) if 'finger_beyond_hand_mm' in v else '') for k, v in sorted(o.items())))
    json.dump(rows, open('access_results.json', 'w'), indent=1)
