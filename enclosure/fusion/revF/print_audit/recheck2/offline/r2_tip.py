# recheck2 (D162): tipping figures restated from the printed parts' masses as sliced, on the D9 base (D156).
#   Base: version 65, 1,055.101 g at (-0.810, -17.836, 79.671) with every printed part solid at 1.05 g/cm3 (ballast hand-over B5).
#   Each part's solid mass (its B-rep volume x 1.05) is replaced by fill x solid mass at the same centre (Fusion's centre of mass of
#   the body); fill = extruded volume in the G-code (part features only; flow ratio included) / B-rep volume.
#   Formulas: the ballast pass's analysis/geo.py figs() (feet: rear y -70.6, front y -5.5, radius 6.35, contact z -3.0; glass top
#   edge (y -6.67, z 174.67); screen centre (y 5.70, z 116.47); door foot y -84.0).
import json, math, sys
C12, S12 = math.cos(math.radians(12.0)), math.sin(math.radians(12.0))
BASE = dict(m=1055.101, cog=(-0.810, -17.836, 79.671))
GT = (-6.67, 174.67); SC = (5.70, 116.47); DOORY = -84.0
FEET = dict(yr=-70.6, yf=-5.5, r=6.35, zp=-3.0)
def figs(m, cog, feet=FEET):
    yr, yf, r, zp = feet['yr'], feet['yf'], feet['r'], feet['zp']
    Wn = m / 1000.0 * 9.81; o = {}
    for lab, yp in (('centres', yr), ('edges', yr - r)):
        M = Wn * (cog[1] - yp) / 1000.0
        o['back top horizontal ' + lab] = M / ((GT[1] - zp) / 1000.0)
        o['back top normal ' + lab] = M / (((GT[1] - zp) * C12 - (GT[0] - yp) * S12) / 1000.0)
        o['back centre normal ' + lab] = M / (((SC[1] - zp) * C12 - (SC[0] - yp) * S12) / 1000.0)
        o['back tips at deg ' + lab] = math.degrees(math.atan2(cog[1] - yp, cog[2] - zp))
    for lab, yp in (('centres', yf), ('edges', yf + r)):
        M = Wn * (yp - cog[1]) / 1000.0
        o['fwd tips at deg ' + lab] = math.degrees(math.atan2(yp - cog[1], cog[2] - zp))
        o['fwd pull top ' + lab] = M / ((GT[1] - zp) / 1000.0)
        o['fwd lift door foot ' + lab] = M / ((yp - DOORY) / 1000.0)
    o['rear share %'] = 100.0 * (yf - cog[1]) / (yf - yr)
    return o
# B-rep volumes (mm3) and centres of mass (world) of the printed bodies, version 65 (r2_1_export)
PARTS = {
 'shell':    (104433.975, (-3.603, -24.916, 82.36)),   'screen': (68247.712, (-1.703, -5.232, 116.339)),
 'spkbox_L': (26088.322, (66.638, -25.82, 38.861)),    'spkbox_R': (26809.825, (-67.564, -25.236, 42.286)),
 'base':     (32450.309, (0.053, -34.83, 1.563)),       'carrier': (12404.264, (1.196, -11.558, 112.349)),
 'cradle':   (1770.951, (0.909, -75.447, 16.915)),      'door': (47019.774, (-0.643, -70.768, 64.786)),
 'cap':      (9944.056, (0.013, -35.156, 177.88)),      'slab': (62932.407, (-1.129, 0.075, 115.273)),
 'grommet':  (506.176, (-0.006, -84.062, 21.609)),      'clip_L': (489.562, (42.616, -3.434, 38.0)),
 'clip_R':   (489.562, (-42.616, -3.434, 38.0)),        'bme_hood': (802.884, (-68.537, -37.772, 103.448))}
def restate(fill):
    m = BASE['m']; s = [BASE['m'] * c for c in BASE['cog']]; rows = {}
    for k, (v, c) in PARTS.items():
        solid = v * 1.05 / 1000.0; f = fill.get(k, 1.0); dm = solid * (1.0 - f)
        m -= dm; s = [s[i] - dm * c[i] for i in range(3)]
        rows[k] = (round(solid, 1), round(f, 3), round(solid * f, 1))
    cog = tuple(v / m for v in s)
    return m, cog, rows, figs(m, cog)
if __name__ == '__main__':
    print(json.dumps(figs(BASE['m'], BASE['cog']), indent=0))
