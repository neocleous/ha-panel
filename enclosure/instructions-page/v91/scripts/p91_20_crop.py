# Crop each picture to its drawn content (alpha), keep marks in % of the crop,
# and write a preview sheet with the marks drawn on.
import json, sys, os
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]
names = sys.argv[3:]
os.makedirs(dst, exist_ok=True)
thumbs = []
for n in names:
    im = Image.open(os.path.join(src, n + ".png")).convert("RGBA")
    meta = json.load(open(os.path.join(src, n + ".json")))
    W, H = im.size
    bb = im.split()[3].point(lambda a: 255 if a > 8 else 0).getbbox()
    pts = [(m["x"] * W / 100, m["y"] * H / 100) for m in meta["marks"]]
    x0, y0, x1, y1 = bb
    for (x, y) in pts:
        x0, y0, x1, y1 = min(x0, x - 30), min(y0, y - 30), max(x1, x + 30), max(y1, y + 30)
    m = 24
    x0, y0 = max(0, int(x0) - m), max(0, int(y0) - m)
    x1, y1 = min(W, int(x1) + m), min(H, int(y1) + m)
    c = im.crop((x0, y0, x1, y1))
    cw, ch = c.size
    if cw > 1400:
        s = 1400 / cw
        c = c.resize((1400, int(ch * s)), Image.LANCZOS)
    marks = [{"label": mm["label"], "x": round(100 * (px - x0) / (x1 - x0), 2), "y": round(100 * (py - y0) / (y1 - y0), 2)}
             for mm, (px, py) in zip(meta["marks"], pts)]
    c.save(os.path.join(dst, n + ".png"), optimize=True)
    json.dump({"name": n, "w": c.size[0], "h": c.size[1], "marks": marks}, open(os.path.join(dst, n + ".json"), "w"))
    t = Image.new("RGBA", c.size, (255, 255, 255, 255))
    t.alpha_composite(c)
    d = ImageDraw.Draw(t)
    for mm in marks:
        x, y = mm["x"] * c.size[0] / 100, mm["y"] * c.size[1] / 100
        d.ellipse((x - 14, y - 14, x + 14, y + 14), outline=(0, 0, 0, 255), width=4)
        d.text((x + 16, y - 10), mm["label"], fill=(0, 0, 0, 255))
    t.thumbnail((700, 500))
    thumbs.append(t)
sheet = Image.new("RGB", (1400, 500 * ((len(thumbs) + 1) // 2)), "white")
for i, t in enumerate(thumbs):
    sheet.paste(t, ((i % 2) * 700, (i // 2) * 500))
sheet.save(os.path.join(dst, "_sheet.png"))
print("ok", [os.path.getsize(os.path.join(dst, n + ".png")) for n in names])
