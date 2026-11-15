# aud5p_pictures.py - assembly audit of the front shell split (2026-11-15): the three pictures of the new issue of the instructions.
# NOT read-only: template bodies AUD_* (never joined, deleted after each picture), visibility and camera (put back), picture files on the
# Mac in ~/Documents/HA_panel_renders/audit-split/. The design itself is not changed; the document is closed without saving afterwards
# and version 64 is opened again. Exec'd into sys.modules['aud5p']; uses aud5k (v5f_k_lib), aud5 (aud4_lib), aud5x (aud5x_lib) and the
# fix pass's picture helpers v5f_k_pic.py (blob 2efbc86, loaded as a namespace with k = aud5k).
import adsk.core, adsk.fusion, math, os, sys, shutil, time
k = sys.modules['aud5k']; a5 = sys.modules['aud5']; x = sys.modules['aud5x']
R = a5.R
OUT = os.path.expanduser('~/Documents/HA_panel_renders/audit-split')
POS = {'TL': (70.0, 27.0), 'TR': (-70.0, 27.0), 'BL': (85.0, -82.0), 'BR': (-85.0, -82.0)}
P = {}


def setup(X, pic_ns):
    P.update(pic_ns)
    if 'vis0' not in R:
        R['vis0'] = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
        R['cam0'] = X.app.activeViewport.camera
    os.makedirs(OUT, exist_ok=True)


def tidy(X):                                          # templates gone, visible set as at the start
    n = X.wipe('AUD_')
    P['restore'](X, R['vis0'])
    return n


def finish(X):
    n = tidy(X)
    vp = X.app.activeViewport; vp.camera = R['cam0']; vp.refresh()
    return n


def save(X, name, w=1600, h=1200):
    adsk.doEvents()
    path = os.path.join(OUT, name)
    ok = X.app.activeViewport.saveAsImageFile(path, w, h)
    return ok, path, (os.path.getsize(path) if os.path.exists(path) else 0)


def nrm():                                            # the screen's normal toward the viewer, world
    return a5.wdir((0.0, -1.0, 0.0))


def upw():                                            # up the screen, world
    return a5.wdir((0.0, 0.0, 1.0))


def pic_step19(X):                                    # the screen plate drawn 35 out along its normal over the shell, screws in its holes
    n = nrm(); off = 35.0
    pl = X.body('HOUSING_F_plate')
    t = X.tbm.copy(k.tcopy(X, 'HOUSING_F_plate')); X.move_n(t, off)
    b = P['aud'](X, t, 'plate_out', 'grey'); b.appearance = pl.appearance
    for side in ('left', 'right'):
        ti = X.tbm.copy(R[('ins', side)]); X.move_n(ti, off); P['aud'](X, ti, 'plate_insert_' + side, 'steel')
    for tag, (xx, up) in POS.items():
        seat = k.W(k.Dp(xx, 9.0 - off, up))
        P['aud'](X, P['screw'](X, seat, n), 'screw_' + tag, 'red')
        r0 = 2.0 if tag[0] == 'T' else 3.5
        land = X.cyld(xx, up, 4.5, 12.55, 12.85); X.dif(land, X.cyld(xx, up, r0, 12.0, 13.5))
        P['aud'](X, land, 'land_' + tag, 'yellow')
        d0 = 12.8 if tag[0] == 'T' else 11.6
        P['aud'](X, X.cyld(xx, up, 2.3, d0 - 0.02, d0 + 5.7), 'post_insert_' + tag, 'steel')
    P['only'](X, ['HOUSING_F_front'])
    tgt = k.W(k.Dp(0.0, 10.0, -25.0))
    eye = tuple(tgt[i] + n[i] * 600.0 + (1.0, 0.0, 0.0)[i] * 260.0 + upw()[i] * 200.0 for i in range(3))
    k.cam(X, eye, tgt, ext=26.0, up=upw())
    return save(X, 'step19_plate.png')


def pic_step21(X):                                    # from above: boxes, screen plate and its inserts, box-top screws, the 2.0 key on the 10 deg lines
    for side in ('left', 'right'):
        P['aud'](X, X.tbm.copy(R[('ins', side)]), 'plate_insert_' + side, 'steel')
        g, p0, u, sb = x.bt_line(side)
        seat = x.bt_point(side, sb + 3.168)
        P['aud'](X, P['screw'](X, seat, (-u[0], -u[1], 0.0)), 'screw_' + side, 'red')
        top = x.bt_head_top(side)
        P['aud'](X, P['tool'](X, top, x.bt_key_dir(side, 10.0), [(2.4, 101.0)]), 'key_' + side, 'steel')
    rim = []
    for j, p in enumerate(k.region(X, 'HOUSING_F_front', 'pic21rim', (-100.0, 100.0, -66.0, -40.0, 70.0, 90.0))):
        rim.append(P['aud'](X, X.cp(p), 'rim_%d' % j, 'white'))
    usb = X.tbm.copy(k.tcopy(X, 'LEAD_USB_RESP')); P['aud'](X, usb, 'usb_lead', 'blue')
    bme = X.tbm.copy(k.tcopy(X, 'LEAD_BME680')); P['aud'](X, bme, 'bme_lead', 'green')
    P['only'](X, ['SPKBOX_L', 'SPKBOX_R', 'HOUSING_F_plate'])
    tgt = (0.0, -38.0, 80.0); eye = (0.0, -38.0, 600.0)
    k.cam(X, eye, tgt, ext=15.0, up=(0.0, 1.0, 0.0))
    return save(X, 'step21_key.png')


def pic_step23(X):                                    # the plate's LCD opening from the front, module home, display/carrier/ReSpeaker hidden
    leads_red = ['LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R']
    for nme in leads_red:
        P['aud'](X, X.tbm.copy(k.tcopy(X, nme)), 'lead_' + nme, 'red')
    P['aud'](X, X.tbm.copy(k.tcopy(X, 'LEAD_DSI')), 'ribbon', 'yellow')
    P['aud'](X, X.tbm.copy(k.tcopy(X, 'LEAD_USB_RESP')), 'usb_lead', 'blue')
    P['aud'](X, X.tbm.copy(k.tcopy(X, 'RESP_usbc_plug_env')), 'usb_plug', 'blue')
    P['only'](X, ['HOUSING_F_plate', 'MAIN_pcb', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'MAIN_PS1'])
    n = nrm(); tgt = k.B2W(5.0, 0.0, -10.0)
    eye = tuple(tgt[i] + n[i] * 400.0 for i in range(3))
    k.cam(X, eye, tgt, ext=14.0, up=upw())
    return save(X, 'step23_notches.png')


OLD = [('audit-recheck/step10_power_lead.png', 'step10_power_lead.png'), ('audit-recheck/step19_stops.png', 'step20_stops.png'),
       ('audit-recheck/step23_cap_way_up.png', 'step24_cap_way_up.png'), ('audit-recheck/step24_25_plugs.png', 'step25_26_plugs.png'),
       ('audit-followup/step23_26_spare_lengths.png', 'step24_27_spare_lengths.png')]


def copy_old():                                       # the unchanged pictures, copied under their new step numbers (originals stay)
    base = os.path.expanduser('~/Documents/HA_panel_renders')
    out = []
    for src, dst in OLD:
        s = os.path.join(base, src); d = os.path.join(OUT, dst)
        if os.path.exists(s):
            shutil.copy2(s, d); out.append((dst, os.path.getsize(d)))
        else:
            out.append((dst, 'missing: ' + src))
    return out
