import sys, json
from render import *
spec = json.load(open(sys.argv[1]))
for s in spec:
    items = []
    for nm in s['parts']:
        if nm in s.get('thick', [s['parts'][0]]):
            m, cols = thickness_colours(nm, maxcls=s.get('maxcls', 4))
        else:
            m = world_mesh(nm); cols = hexrgb(s.get('col', {}).get(nm, '#e3d9c6'))
        items.append((m, cols))
    img, cam = render(items, s['d'], s['c'], s['w'], s['h'], ppm=s.get('ppm', 8), clip=[(c[:3], c[3:]) for c in s.get('clip', [])])
    save(img, s['out'], title=s.get('title', ''), cam=cam, centre=s['c'], width=s['w'], height=s['h'], notes=[(n[:3], n[3]) for n in s.get('notes', [])], maxcls=s.get('maxcls', 4))
    print(s['out'], img.shape)
