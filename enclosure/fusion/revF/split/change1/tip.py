# change1/tip.py - change pass after the split's audit (2026-11-15): the tipping figures as in the table of 2026-11-12 (close report 5.4),
# for version 64 and version 65 (g20). The masses and centroids come from v5f_k2a_tip.py's lists (RHO, COMP, MAGS) run on the model's bodies,
# version 64 by its hidden _v64 bodies; the screen plate is added to the printed parts. Pushes as v5f_j5d_tip.py.
import math
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0))
GT = (-6.67, 174.67); SC = (5.70, 116.47); DOORY = -84.0              # glass's top front edge, screen centre (y, z); the door's foot


def figs(m, cog, yr, yf=-5.5, r=6.35, zp=-3.0):
    Wn = m / 1000.0 * 9.81; out = {}
    for lab, yp in (('rear centres', yr), ('rear edges', yr - r)):
        M = Wn * (cog[1] - yp) / 1000.0
        out['backward, ' + lab] = {'top edge horizontal N': M / ((GT[1] - zp) / 1000.0),
                                   'top edge normal N': M / (((GT[1] - zp) * C - (GT[0] - yp) * S) / 1000.0),
                                   'screen centre normal N': M / (((SC[1] - zp) * C - (SC[0] - yp) * S) / 1000.0)}
    for lab, yp in (('front centres', yf), ('front edges', yf + r)):
        M = Wn * (yp - cog[1]) / 1000.0
        out['forward, ' + lab] = {'tips at deg': math.degrees(math.atan2(yp - cog[1], cog[2] - zp)), 'pull at the top edge N': M / ((GT[1] - zp) / 1000.0),
                                  'lift at the door foot N': M / ((yp - DOORY) / 1000.0)}
    out['rear feet share %'] = 100.0 * (yf - cog[1]) / (yf - yr)
    return out


# The split's D9, rebuilt: version 63's 1,080.5 g at (-0.83, -17.57, 80.34); the one-piece shell 210.4 g at (-2.681, -15.669, 97.632) out;
# plate 71.7 g at (-1.704, -5.231, 116.333) and shell 109.7 g at (-3.590, -24.923, 82.360) in; 3.6 g of new screws and inserts at the plate's
# centroid -> 1,055.10 g at (-0.810, -17.833, 79.671): 2.981 N backward, 8.48 / 12.73 deg forward (D9: 2.98 N, 8.5 / 12.7).
# This pass on that base: + the k2a model's own difference g20 - v64 (feet 1.6 back; boxes, shell, plate by their volumes): +0.0009 g,
# centroid y -0.003 -> 1,055.10 g at (-0.810, -17.836, 79.671).
# k2a on today's bodies: v64 1,050.608 g at (-0.551, -18.076, 79.349); g20 1,050.609 g at (-0.551, -18.079, 79.349); + 3.6 g as above.
#
# Results (N unless deg):                                       v64 (D9 base)   g20 (D9 base)   v64 direct   g20 direct
#  backward, rear centres: top edge horizontal                     2.981           3.074          2.967        3.060
#                          top edge normal                         3.293           3.403          3.277        3.387
#                          screen centre normal                    5.227           5.408          5.202        5.383
#  backward, rear edges:   top edge horizontal                     3.351           3.444          3.336        3.429
#                          top edge normal                         3.732           3.844          3.716        3.828
#                          screen centre normal                    5.953           6.139          5.927        6.113
#  forward, front centres: tips at deg                             8.48            8.49           8.64         8.64
#                          pull at the top edge / lift at the door foot   0.718 / 1.626   0.719 / 1.627   0.729 / 1.651   0.730 / 1.651
#  forward, front edges:   tips at deg                             12.73           12.74          12.90        12.90
#                          pull / lift                             1.088 / 2.279   1.089 / 2.279   1.099 / 2.301   1.099 / 2.302
#  rear feet share %                                               19.42           18.95          19.74        19.26
# Ceiling with these feet at x +-30: rear edge on the plate's edge (y about -81.3, centre -74.95): 3.33 N (centres) / 3.70 N (edges).
