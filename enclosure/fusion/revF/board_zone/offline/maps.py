"""Column maps around the main board plane (world x_rel / z grid from bz.py).

For a board whose front face is at YF and back face at YB = YF - 1.6:
  front[x,z]  = free height in front of YF to the first fixed body or keep-out (and which body)
  back[x,z]   = free depth behind YB to the first fixed body, and to the door's material (door comes off along -y)
  slab[x,z]   = True if no fixed body, keep-out or door material crosses [YB, YF]
"""
import numpy as np, bz

M = '/mnt/user-data/uploads/HA_panel_renders/board_zone/mesh/'
FRONT = '/mnt/user-data/uploads/HA_panel_renders/print_audit/exports/front_d22.stl'

# fixed when the board goes in (assembly step 10) or after it, and staying when the door is off
FIXED = ['front_d22', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R',
         'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'PIPWR_a_env',
         'LEAD_PI_POWER', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env',
         'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'BME_HOOD', 'BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env',
         'LD2410C_env_F', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail']
KEEPOUT = ['KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL',
           'KO_capkey_SR', 'KO_K7_fan', 'KO_touch_back']
BRACKET = ['MAIN_BRACKET']
DOOR = ['HOUSING_F_door']
LEADS = ['LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_RADAR',
         'LEAD_USB_RESP', 'LEAD_DSI', 'LEAD_VEML', 'LEAD_BME680', 'LEAD_PIGTAIL_20V']
NC = bz.NX * bz.NZ


def load(names):
    out = {}
    for nm in names:
        p = FRONT if nm == 'front_d22' else M + nm + '.stl'
        (c, y0, y1), bad, vol = bz.body_intervals(p, 'cache')
        assert len(bad) == 0, nm
        out[nm] = (c, y0, y1)
    return out


def first_in_front(B, yf, eps=1e-6):
    """Per cell: lowest y0 >= yf - eps among the bodies' intervals (inf if none) and the body index."""
    best = np.full(NC, np.inf); who = np.full(NC, -1)
    for k, (nm, (c, y0, y1)) in enumerate(B.items()):
        m = y0 >= yf - eps
        v = np.full(NC, np.inf); np.minimum.at(v, c[m], y0[m])
        sel = v < best; best[sel] = v[sel]; who[sel] = k
    return best, who


def last_behind(B, yb, eps=1e-6):
    best = np.full(NC, -np.inf); who = np.full(NC, -1)
    for k, (nm, (c, y0, y1)) in enumerate(B.items()):
        m = y1 <= yb + eps
        v = np.full(NC, -np.inf); np.maximum.at(v, c[m], y1[m])
        sel = v > best; best[sel] = v[sel]; who[sel] = k
    return best, who


def overlap(B, ya, yb):
    """Per cell: True where any interval overlaps [ya, yb]; and which body (last one found)."""
    hit = np.zeros(NC, bool); who = np.full(NC, -1)
    for k, (nm, (c, y0, y1)) in enumerate(B.items()):
        m = (y0 < yb) & (y1 > ya)
        hit[c[m]] = True; who[c[m]] = k
    return hit, who


def max_out(B):
    v = np.full(NC, -np.inf)
    for nm, (c, y0, y1) in B.items():
        np.maximum.at(v, c, y1)
    return v


def grid(a):
    return a.reshape(bz.NZ, bz.NX)
