# Labels on Fusion screenshots: text boxes with leader lines.
import sys, json
from PIL import Image, ImageDraw, ImageFont
import matplotlib
FD = matplotlib.get_data_path() + '/fonts/ttf/'
F = ImageFont.truetype(FD + 'DejaVuSans.ttf', 17); FB = ImageFont.truetype(FD + 'DejaVuSans-Bold.ttf', 19)


def label(src, dst, items, title=None, crop=None, foot=None):
    im = Image.open(src).convert('RGB')
    if crop:
        im = im.crop(crop)
        items = [dict(it, at=[(x - crop[0], y - crop[1]) for (x, y) in it['at']], xy=(it['xy'][0] - crop[0], it['xy'][1] - crop[1])) for it in items]
    pad_top = 44 if title else 0; pad_bot = 34 if foot else 0
    W, H = im.size
    out = Image.new('RGB', (W, H + pad_top + pad_bot), (45, 50, 64)); out.paste(im, (0, pad_top))
    d = ImageDraw.Draw(out)
    if title:
        d.text((14, 11), title, font=FB, fill=(255, 255, 255))
    if foot:
        d.text((14, H + pad_top + 8), foot, font=F, fill=(220, 220, 220))
    for it in items:
        tx, ty = it['xy']; ty += pad_top
        lines = it['text'].split('\n')
        w = max(d.textlength(l, font=F) for l in lines) + 16; h = 22 * len(lines) + 10
        box = (tx, ty, tx + w, ty + h)
        for (ax, ay) in it['at']:
            ay += pad_top
            cx = min(max(ax, box[0]), box[2]); cy = min(max(ay, box[1]), box[3])
            d.line([(cx, cy), (ax, ay)], fill=(255, 255, 255), width=2)
            d.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=(255, 255, 255))
        d.rounded_rectangle(box, radius=6, fill=(255, 255, 255), outline=(30, 30, 30))
        for i, l in enumerate(lines):
            d.text((tx + 8, ty + 5 + 22 * i), l, font=F, fill=(20, 20, 20))
    out.save(dst)
    return out.size


if __name__ == '__main__':
    spec = json.load(open(sys.argv[1]))
    print(label(spec['src'], spec['dst'], spec['items'], spec.get('title'), spec.get('crop'), spec.get('foot')))
