# rev E interior clearance model (world frame, mm). Mirrors the Fusion generator in v5e_p17 (outer) minus WALL 2.5.
import math
C=math.cos(math.radians(12)); S=math.sin(math.radians(12)); T=math.tan(math.radians(12)); H=143.3; XC=-2.55
ZT=180.0; DTOP=28.0; WALL=2.5
def yfront(d,z): return -d/C-(z-H)*T
YTOP=yfront(13.0,ZT)-DTOP
YF_LOFT=14.03
def hwE(z): return 100-10*(z/ZT)**1.7
def ybE(z): return -85+(YTOP+85)*(z/ZT)**2.2
def nE(z): return 2.6-0.6*(z/ZT)
def yF(z): return min(1.8, yfront(12.3,z))           # front face after chin + slot cuts
def inner_D(z,N=400):
    """inner superellipse half-region boundary (loft generator) at height z: ai,bi, boundary polyline in (x,y) world, x relative to XC"""
    hw=hwE(z); dep=YF_LOFT-ybE(z); rc=12.0; ai=hw-rc; bi=dep-2*rc; n=nE(z); y0=YF_LOFT-rc
    pts=[]
    for i in range(N+1):
        t=math.pi*i/N; c=math.cos(t); s=math.sin(t)
        x=ai*(1 if c>=0 else -1)*abs(c)**(2/n); v=bi*abs(s)**(2/n)
        pts.append((x,y0-v))
    return ai,bi,y0,pts
def dist_to_D(x,y,ai,bi,y0,pts,n):
    """distance from (x,y) to the inner D region (0 if inside)"""
    v=y0-y
    if v>=0 and ai>0 and bi>0 and (abs(x/ai))**n+(abs(v/bi))**n<=1: return 0.0
    if v<0 and abs(x)<=ai: return -v           # in front of the flat side: distance to the segment
    d=min(math.hypot(x-px,y-py) for px,py in pts)
    if abs(x)<=ai: d=min(d,abs(v)) if v<0 else d
    return d
_cache={}
def section(z):
    zq=round(z,1)
    if zq not in _cache: _cache[zq]=inner_D(z)+(nE(z),)
    return _cache[zq]
def clearance(xw,y,z):
    """signed clearance of a world point to the rev E INTERIOR surface (positive = inside, mm).
       x world absolute (XC applied here)."""
    x=xw-XC
    ai,bi,y0,pts,n=section(min(max(z,0.0),ZT))
    d=dist_to_D(x,y,ai,bi,y0,pts,n)
    c_outline=(12.0-WALL)-d                      # plan outline offset
    c_front=(yF(z)-WALL)-y                       # chin / slot face wall
    c_floor=z-WALL; c_top=(ZT-WALL)-z
    c=min(c_outline,c_front,c_floor,c_top)
    # top-front roll R10 (inner R7.5) centred (y_c, 170) where y_c = yF(180)-10
    yc=yfront(12.3,ZT)-10.0; zc=ZT-10.0
    if y>yc and z>zc: c=min(c,7.5-math.hypot(y-yc,z-zc))
    return c
def box_clear(x0,x1,y0,y1,z0,z1,step=3.0):
    """min clearance over the surface of an axis-aligned world box (sampled)"""
    def rng(a,b):
        k=max(1,int(math.ceil((b-a)/step))); return [a+(b-a)*i/k for i in range(k+1)]
    best=(1e9,None)
    for x in rng(x0,x1):
        for y in rng(y0,y1):
            for z in rng(z0,z1):
                on_face=(x in (x0,x1)) or (y in (y0,y1)) or (z in (z0,z1))
                if not on_face: continue
                c=clearance(x,y,z)
                if c<best[0]: best=(c,(round(x,1),round(y,1),round(z,1)))
    return best
def half_width_interior(y,z):
    """interior half-width (world x from XC) at depth y, height z"""
    lo,hi=0.0,110.0
    for _ in range(40):
        m=(lo+hi)/2
        if clearance(XC+m,y,z)>0: lo=m
        else: hi=m
    return lo
if __name__=='__main__':
    for y in (-5,-50,-70,-80): print(y, round(half_width_interior(y,3.0),1))   # 97 / 84 / 62 / 33 at the floor
