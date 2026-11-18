"""recheck3: layer pictures in world windows. usage in code: view(out, job, tag, pos, world_axis_window, bed_z list, title)"""
import numpy as np
from r3_gq import *
_cache = {}
def getg(job):
    if job not in _cache: _cache[job] = G(job)
    return _cache[job]
_bp = {}
def getbp(tag, pos):
    k = (tag, tuple(pos))
    if k not in _bp: _bp[k] = BedPart(tag, pos)
    return _bp[k]
def bedwin(bp, wlo, whi):
    c = bp.to_bed([wlo, whi]); lo = c.min(0); hi = c.max(0); return (lo[0], hi[0], lo[1], hi[1]), (lo[2], hi[2])
def view(out, job, tag, pos, wlo, whi, zs, title='', ncol=4, size=3.6):
    g = getg(job); bp = getbp(tag, pos); win, zr = bedwin(bp, wlo, whi)
    specs = [(g, g.layer_at(z), win, bp, title) for z in zs]
    sheet(out, specs, ncol=ncol, size=size); return win, zr
