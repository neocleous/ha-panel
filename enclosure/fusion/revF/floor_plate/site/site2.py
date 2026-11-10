import json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
U0, V0, W0 = 2.5, -27.45, 32.7
u = lambda x: x - U0; v = lambda z: z - V0
fig = plt.figure(figsize=(18, 11.5))
ax = fig.add_axes([0.045, 0.27, 0.56, 0.68]); ax2 = fig.add_axes([0.655, 0.27, 0.33, 0.68])
def R(a, x0, x1, y0, y1, **k):
    a.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, **k))
# LCD opening and notch
R(ax, u(-57.45), u(55.55), v(-57.43), v(2.57), fill=False, ec='0.35', lw=1.3)
R(ax, u(55.55), u(79.0), v(-29.3), v(-11.2), fill=False, ec='0.35', lw=1.0)
ax.text(u(67.3), v(-20.3), 'notch for the\nReSpeaker\nUSB plug', ha='center', va='center', fontsize=7.5, color='0.3')
ax.text(u(-57.45), v(-57.43) - 2.6, 'LCD opening 113.0 x 60.0: everything on the display module passes through it', fontsize=8, color='0.3')
# display-screw key paths
for xc in (50.0, -45.0):
    R(ax, u(xc - 3.5), u(xc + 3.5), v(-64), v(9), fc='#f4c7c3', ec='none', alpha=0.7)
# ReSpeaker behind
R(ax, u(-37.6), u(44.42), v(-48.0), v(-13.99), fill=False, ec='#1f77b4', lw=1.1, ls='--')
R(ax, u(36.34), u(43.34), v(-34.96), v(-27.01), fc='#1f77b4', alpha=0.30, ec='#1f77b4', lw=0.6)
R(ax, u(31.4), u(46.0), v(-45.82), v(-37.17), fc='#1f77b4', alpha=0.15, ec='#1f77b4', lw=0.6)
ax.text(u(39.8), v(-31), '0.6', ha='center', va='center', fontsize=7, color='#0b3d63')
ax.text(u(38.7), v(-41.5), '1.9', ha='center', va='center', fontsize=7, color='#0b3d63')
# outline
R(ax, -43.5, 43.5, -28.95, 28.95, fill=False, ec='k', lw=2.4)
ax.plot([0], [0], marker='+', ms=16, color='k', mew=1.5)
ax.text(1.5, -2.6, 'origin', fontsize=7.5)
# height lines
ax.plot([-43.5, 43.5], [8, 8], color='#444', lw=0.9, ls=':'); ax.text(-43, 8.5, '27.5 mm parts: below this line', fontsize=7.5, color='#222')
ax.plot([-43.5, 43.5], [18, 18], color='#444', lw=0.9, ls=':'); ax.text(-43, 18.5, '20 mm plugs: below this line', fontsize=7.5, color='#222')
# display mounting points
for (x, z) in ((-16.45, -51.93), (41.55, -51.93), (-16.45, -2.93), (41.55, -2.93)):
    ax.add_patch(Circle((u(x), v(z)), 2.25, fc='0.15', ec='k', zorder=5)); ax.add_patch(Circle((u(x), v(z)), 6.5, fill=False, ec='0.35', ls=':', lw=0.9))
# post zones
for (x0, x1, z0, z1) in ((-37.5, -23.0, -53.4, -52.1), (-9.9, 35.0, -53.4, -52.1), (-37.5, -23.0, -9.5, -1.3), (-9.9, 25.2, -9.5, -1.3)):
    R(ax, u(x0), u(x1), v(z0), v(z1), fc='#2ca02c', alpha=0.40, ec='#2ca02c')
# cap key paths
vv = np.linspace(-2, 28.95, 30)
for sgn in (1, -1):
    ub = sgn * (23.0 + 0.0491 * (vv - 27.45 + 29.9)) - U0
    ax.fill_betweenx(vv, ub - 3.5, ub + 3.5, color='#ff7f0e', alpha=0.30, lw=0)
    us = sgn * (31.7 + 0.1958 * (vv + 2.95)) - U0
    ax.fill_betweenx(vv, us - 3.5, us + 3.5, color='#9467bd', alpha=0.30, lw=0)
# door opening edge
arch = [(-52, -55), (-50, -40), (-46, -30), (-44, -20), (-37, -15), (-31, -10), (-21, -5), (-10, 0), (5, 0), (17, -5), (31, -10), (37, -15), (42, -20), (44, -30), (50, -40), (52, -55)]
ax.plot([u(a) for a, b in arch], [v(b) for a, b in arch], color='#555', lw=1.4, ls='-.')
# connector zones
zones = [(-14, 14, -28.95, -20.5, 'A'), (-43.5, -18, -28.95, -20.5, 'B'), (18, 43.5, -28.95, -20.5, 'C'), (-43.5, -33.5, -18, -2, 'D'), (-10, 10, -6, 6, 'E')]
for (a, b, c, d, t) in zones:
    R(ax, a, b, c, d, fill=False, ec='#d62728', lw=1.3, ls='--')
    ax.text((a + b) / 2, (c + d) / 2 + (2.2 if t in 'ABC' else 0), t, ha='center', va='center', fontsize=15, color='#b00000', weight='bold')
ax.set_xlim(-62, 82); ax.set_ylim(-36, 37); ax.set_aspect('equal')
ax.set_xlabel("u (mm)  -  right as seen from the door = +x_rel = the left speaker's side"); ax.set_ylabel('v (mm)  -  up the slab')
ax.set_title('Main board site seen from the door: outline 87.0 x 57.9 (u -43.5..+43.5, v -28.95..+28.95), origin at x_rel 2.5, Zd -27.45', fontsize=10.5)
ax.grid(True, lw=0.3, color='0.87')
# ---------- section ----------
Z = [0, -5, -10, -15, -20, -25, -30, -35, -40, -45, -50, -55, -60]; D = [65.5, 68, 71, 73, 75, 78, 80, 82, 84, 86, 88, 90, 92]
ax2.plot(D, [v(z) for z in Z], color='k', lw=2.2); ax2.text(88.5, v(-44), "door's inner face", rotation=-65, fontsize=8)
ax2.plot([58, 61, 65.5], [v(10), v(5), v(0)], color='0.4', lw=2.2); ax2.text(72, 33, 'shell above the door', fontsize=7.5, color='0.3', ha='left')
R(ax2, 0, 7.4, v(-62), v(8), fc='0.86', ec='0.5'); ax2.text(3.7, 0, 'display', rotation=90, ha='center', va='center', fontsize=8)
R(ax2, 7.4, 9.0, v(-57.4), v(2.6), fc='#7fbf7f', ec='0.4'); ax2.text(8.2, 32, 'display\nboard', fontsize=7, ha='center')
R(ax2, 15.2, 17.2, v(-56.9), v(2.2), fc='#c8a2c8', ec='0.4'); ax2.text(16.2, 32, 'carrier', fontsize=7, ha='center')
R(ax2, 22.2, 23.71, v(-48), v(-13.99), fc='#1f77b4', alpha=0.65, ec='0.3'); R(ax2, 23.71, 26.0, v(-48), v(-13.99), fc='#1f77b4', alpha=0.2, ec='none')
ax2.text(24, 15.2, 'ReSpeaker', fontsize=7, ha='center', color='#1f77b4')
R(ax2, 31.1, 32.7, -28.95, 28.95, fc='#2e8b57', ec='k'); ax2.text(31.9, 31, 'main board', fontsize=7.5, ha='center')
zz = np.linspace(-37.8, 2, 40)
ax2.fill_betweenx([v(z) for z in zz], [76.8 - 0.7412 * (z + 29.9) - 3.11 for z in zz], [76.8 - 0.7412 * (z + 29.9) + 3.11 for z in zz], color='#ff7f0e', alpha=0.32)
ax2.text(48, 22.5, 'cap back-screw key path\n(only at u +19..+25, -30..-24)', fontsize=7, color='#b85c00', ha='center')
ax2.plot([d - 2.0 for d in D], [v(z) for z in Z], color='#d62728', lw=1, ls='--')
for z, lab in ((-50, '55'), (-40, '51'), (-30, '47'), (-20, '42'), (-10, '38'), (0, '32')):
    dv = dict(zip(Z, D))[z]; ax2.annotate('', xy=(dv, v(z)), xytext=(32.7, v(z)), arrowprops=dict(arrowstyle='<->', lw=0.6, color='0.3')); ax2.text(40, v(z) + 0.7, lab, fontsize=7.5, ha='center')
R(ax2, 32.7, 60.2, -19, -6.5, fill=False, ec='#444', lw=1, ls='--'); ax2.text(47, -15.8, 'example: supply module\nupright, 27.5 tall', fontsize=7, ha='center', va='center')
ax2.annotate('', xy=(22.2, -24), xytext=(17.2, -24), arrowprops=dict(arrowstyle='<->', lw=0.6)); ax2.text(19.7, -27, '5.0', fontsize=7, ha='center')
ax2.annotate('', xy=(31.1, 9), xytext=(26.0, 9), arrowprops=dict(arrowstyle='<->', lw=0.6)); ax2.text(28.5, 10.2, '5.1', fontsize=7, ha='center')
ax2.annotate('', xy=(31.1, -25), xytext=(17.2, -25), arrowprops=dict(arrowstyle='<->', lw=0.6)); ax2.text(25.5, -27.7, '13.9', fontsize=7, ha='center')
ax2.set_xlim(-2, 100); ax2.set_ylim(-36, 37); ax2.set_aspect('equal')
ax2.set_xlabel('depth behind the glass front d (mm);  w = d - 32.7 (door side of the board)'); ax2.set_ylabel('v (mm)')
ax2.set_title('Section through the middle (u = 0): free depth from the board to the door', fontsize=10.5, pad=14); ax2.grid(True, lw=0.3, color='0.87')
key = [
 'Thick black: largest outline.  Grey: LCD opening and the USB-plug notch.  Dash-dot: edge of the door opening behind the board (limits what a hand reaches).',
 "Pink strips: display-screw key paths (dia 7), outside the outline.  Orange / purple strips: cap back-screw / side-screw key paths: parts under them no taller than 38.2 - 0.74 v / 35.2 - 0.79 v.",
 "Black dots: the display's four mounting points; no post within the dotted circle (6.5).  Green: where post centres may stand.  Blue dashed: ReSpeaker behind the board; numbers = gap to the board's back face at its header and jack (5.1 elsewhere).",
 'Connector zones (red):  A bottom edge, middle: 20 V lead, touch, Pi signal plug B - fingertip and pinch reach.   B bottom edge, right-speaker side: speaker R, Pi signal plug A - fingertip.',
 '   C bottom edge, left-speaker side: speaker L, Pi power socket (plug hangs below the edge) - fingertip; pinch on the power plug.   D side edge, lower half: radar, BME680 - fingertip.   E middle: VEML6030 - fingertip and pinch.',
 'Reach probed with the module in and the door off: a fingertip does not reach the side edges at v +15 or the top edge at v +21 (centre: only at 45 degrees from below). Nothing that is plugged in place goes in the upper third.',
]
for i, t in enumerate(key):
    fig.text(0.045, 0.205 - i * 0.031, t, fontsize=9.2)
plt.savefig('main_board_site.png', dpi=120)
