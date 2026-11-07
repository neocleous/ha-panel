import sys
sys.path.insert(0, '/home/claude/pa')
from pa_img import render
from PIL import Image
def montage(items, out, cols=2, size=(4.6, 3.4), dpi=90):
    paths = []
    for i, (tag, okey, zb, crop, title) in enumerate(items):
        p = '/home/claude/pa/img/_m%d.png' % i
        render(tag, okey, zb, crop, p, title=title, size=size, dpi=dpi); paths.append(p)
    ims = [Image.open(p) for p in paths]
    w, h = ims[0].size; rows = (len(ims) + cols - 1) // cols
    M = Image.new('RGB', (w * cols, h * rows), 'white')
    for i, im in enumerate(ims):
        M.paste(im, ((i % cols) * w, (i // cols) * h))
    M.save(out); print(out, M.size)
if __name__ == '__main__':
    pass
