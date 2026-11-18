"""recheck3: thickness of named features of version 67 from the ray scan (a4_ray.py's samples): for each world box, the samples whose
thickness is under tcap: area (one face), thickness p2 / median / p98, and how the feature stands in the print (wall / skin / slope)."""
import sys, json, numpy as np
from fdm_lib import *
FEATS = {
 'HOUSING_F_front': [
  ('lip round the door opening, sides (x 60..82)', [60, 82, -63.3, -56.5, 8, 150], 2.6),
  ('lip, viewer-left top arch (x 10..60, z 100..160)', [10, 60, -63.3, -56.5, 100, 160], 2.6),
  ('lip, whole (y -63.4..-56.0)', [-85, 85, -63.4, -56.0, 4, 160], 2.6),
  ('cloth groove web under the screen', [-48.5, 48.5, 4.4, 6.7, 48.5, 50.7], 1.4),
  ('cloth groove rail outside x 48', [48.5, 92, 4.2, 6.9, 47.5, 52.5], 2.6),
  ('toe of the chin bottom edge, middle', [-23.5, 23.5, 1.2, 3.2, 2.7, 3.8], 1.4),
  ('toe, x 36..87', [36.5, 87.0, 1.2, 3.2, 2.7, 3.8], 1.4),
  ('toe, x -87..-36', [-87.0, -36.5, 1.2, 3.2, 2.7, 3.8], 1.4),
  ('toe at the corner faces, x 87.5..94', [87.5, 94, 0.3, 3.6, 2.7, 3.8], 1.4),
  ('toe at the corner faces, x -94..-87.5', [-94, -87.5, 0.3, 3.6, 2.7, 3.8], 1.4),
  ('chin lip over the noses (x 24..36)', [24, 36, 0.9, 2.6, 2.7, 4.2], 2.0),
  ('lip magnet seats (skins, y -57..-56)', [-80, 80, -57.6, -55.9, 15, 156], 0.8),
  ('speaker lattice left', [45, 92, 4.0, 7.0, 6, 48], 0.85),
  ('seat floor ring y -55.2', [-85, 85, -55.6, -54.6, 4, 160], 2.0),
 ],
 'HOUSING_F_door': [('magnet seats', [-80, 80, -64, -55, 15, 156], 0.8), ('vent bars', [-23, 23, -90, -70, 62, 113], 5.0), ('bottom flange', [-80, 80, -90, -50, 2.7, 3.8], 1.2)],
 'FLOOR_PLATE': [('noses', [-36, 36, 0.5, 2.6, 4.2, 5.7], 1.6), ('intake webs', [-60, 60, -60, -10, -0.1, 2.6], 1.3)],
 'HOUSING_F_cap': [('mic pocket front walls', [-39, 39, -23.5, -22.4, 177.4, 178.4], 1.0), ('mic pocket end walls', [-8.6, 8.6, -30.5, -25.3, 177.4, 178.4], 1.0)],
 'CRADLE_5807': [('cheeks', [-11.2, 11.2, -84, -81.4, 20, 25.5], 0.85), ('rear frame', [-11.2, 11.2, -84.7, -83.6, 15, 27], 1.0)],
 'TOUCH_CLIP_L': [('tongue', [37, 43, -34, -3, 30, 46], 1.6)],
 'GROMMET_usbc_F': [('sleeve walls', [-20, 20, -95, -70, 10, 35], 0.95)],
 'HOUSING_F_plate': [('left box-top insert beside the notch', [-200, 200, -200, 200, -200, 400], 1.3)],
}
for name in sys.argv[1:] or FEATS:
    p = Part(name); z = np.load(os.path.join(DATA, 'ray_%s.npz' % name)); pts = z['pts'].astype(float); t = z['t'].astype(float); fi = z['fi']
    W = to_world(pts); nrm = p.m.face_normals[fi]; upc = np.abs(nrm @ p.up); a_s = p.m.area / len(pts)
    print(name)
    for label, b, tcap in FEATS[name]:
        s = (W[:, 0] >= b[0]) & (W[:, 0] <= b[1]) & (W[:, 1] >= b[2]) & (W[:, 1] <= b[3]) & (W[:, 2] >= b[4]) & (W[:, 2] <= b[5]) & (t < tcap)
        if s.sum() < 20: print('   %-52s (no samples under %.2f)' % (label, tcap)); continue
        q = np.percentile(t[s], [2, 50, 98]); u = upc[s].mean(); kind = 'wall' if u < 0.35 else ('skin' if u > 0.87 else 'slope')
        ww = W[s]
        print('   %-52s area %7.1f | t p2 %.2f med %.2f p98 %.2f | %s | x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (label, s.sum() * a_s / 2, q[0], q[1], q[2], kind,
              ww[:, 0].min(), ww[:, 0].max(), ww[:, 1].min(), ww[:, 1].max(), ww[:, 2].min(), ww[:, 2].max()))
