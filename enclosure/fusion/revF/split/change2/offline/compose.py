# change2/offline/compose.py - the question pictures: Fusion renders (img/fusion) set side by side with captions and labels.
import os, sys
from PIL import Image, ImageDraw, ImageFont
B = os.path.join(os.path.dirname(__file__), '..', 'img')
F = lambda s, w='Regular': ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-%s.otf' % w, s)
INK = (25, 25, 28); RED = (200, 30, 30)


def load(name, crop=None, size=None, bg=(255, 255, 255)):
    im = Image.open(os.path.join(B, 'fusion', name + '.png')).convert('RGBA')
    out = Image.new('RGBA', im.size, bg + (255,)); out.alpha_composite(im); out = out.convert('RGB')
    if crop:
        out = out.crop(crop)
    if size:
        out = out.resize(size, Image.LANCZOS)
    return out


def label(d, xy, text, to=None, fill=INK, font=None, bg=(255, 255, 255), pad=5, anchor='la'):
    font = font or F(24)
    l, t, r, b = d.textbbox(xy, text, font=font, anchor=anchor)
    if bg is not None:
        d.rectangle((l - pad, t - pad, r + pad, b + pad), fill=bg)
    d.text(xy, text, fill=fill, font=font, anchor=anchor)
    if to is not None:
        cx = min(max(to[0], l), r); cy = t - pad if to[1] < t else (b + pad if to[1] > b else (t + b) // 2)
        d.line((cx, cy, to[0], to[1]), fill=fill, width=3)
        d.ellipse((to[0] - 5, to[1] - 5, to[0] + 5, to[1] + 5), fill=fill)


def sheet(rows, titles, fname, cell, head=70, gap=16, title=None, foot=None, row_titles=None):
    ncol = max(len(r) for r in rows); w = ncol * cell[0] + (ncol + 1) * gap
    th = 80 if title else 0; fh = (36 * len(foot) + 24) if foot else 0
    rt = 44 if row_titles else 0
    h = th + head + len(rows) * (cell[1] + gap + rt) + fh + gap
    S = Image.new('RGB', (w, h), (255, 255, 255)); d = ImageDraw.Draw(S)
    if title:
        d.text((gap, 20), title, fill=INK, font=F(40, 'SemiBold'))
    for j, t in enumerate(titles):
        d.text((gap + j * (cell[0] + gap), th + 16), t, fill=INK, font=F(32, 'SemiBold'))
    y = th + head
    for i, r in enumerate(rows):
        if row_titles:
            d.text((gap, y + 6), row_titles[i], fill=(70, 70, 76), font=F(26, 'Medium')); y += rt
        for j, im in enumerate(r):
            x = gap + j * (cell[0] + gap)
            S.paste(im.resize(cell, Image.LANCZOS) if im.size != cell else im, (x, y))
            d.rectangle((x, y, x + cell[0] - 1, y + cell[1] - 1), outline=(190, 190, 195), width=2)
        y += cell[1] + gap
    if foot:
        for i, t in enumerate(foot):
            d.text((gap, y + 6 + 36 * i), t, fill=(60, 60, 66), font=F(25))
    S.save(os.path.join(B, fname)); return S
