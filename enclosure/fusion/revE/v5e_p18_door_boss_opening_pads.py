# HA Panel rev E - p18 (2026-11-01, Claude): DOOR_plate (floor door, outline offset 2.8, 2.5 thick), slab boss on the slot wall
# (d 9 -> 12.8), LCD opening/pin notch/4x dia2.7 holes, 3 support pads (d 9.2 -> 6.4), interference check.
# This file carries the post-mortem fix for the boss step (NEW body + interference check + combine JOIN). See README.
import adsk.core, adsk.fusion, json, math, traceback, os
C=math.cos(math.radians(12.0)); S=math.sin(math.radians(12.0)); T=math.tan(math.radians(12.0)); H=143.3; XC=-2.55
def run(context):
    app=adsk.core.Application.get(); des=adsk.fusion.Design.cast(app.activeProduct); comp=des.rootComponent; feats=comp.features
    V=adsk.core.ValueInput.createByReal; P3=adsk.core.Point3D.create; V3=adsk.core.Vector3D.create
    NEW=adsk.fusion.FeatureOperations.NewBodyFeatureOperation; CUT=adsk.fusion.FeatureOperations.CutFeatureOperation; JOIN=adsk.fusion.FeatureOperations.JoinFeatureOperation
    log=[]; LOGF=os.path.expanduser('~/Documents/v5d_log.json')
    def flush():
        try:
            with open(LOGF,'w') as f: json.dump(log,f)
        except Exception: pass
    def step(name,fn):
        try:
            r=fn(); log.append(f'{name}: ok {r if r is not None else ""}')
        except Exception:
            log.append(f'{name}: FAIL '+traceback.format_exc().splitlines()[-1]); r=None
        flush(); return r
    def body(name):
        for b in comp.bRepBodies:
            if b.name==name: return b
    def plane(name):
        for i in range(comp.constructionPlanes.count):
            if comp.constructionPlanes.item(i).name==name: return comp.constructionPlanes.item(i)
    fl=plane('FLOOR_plane')
    def Dw(x,y,z=0.0): return P3(x/10,(y*C+(z-H)*S)/10,(-y*S+(z-H)*C)/10)
    def yfront(d,z): return -d/C-(z-H)*T
    def wz(p): return H+p.y*10*S+p.z*10*C
    def wy(p): return p.y*10*C-p.z*10*S
    def sk_on(pl):
        sk=comp.sketches.add(pl); sk.isLightBulbOn=False; return sk
    def yplane(d,name):
        # construction plane parallel to XZ at design depth d (Y=-d)
        ex=plane(name)
        if ex: return ex
        for off in (-d/10,d/10):
            cpi=comp.constructionPlanes.createInput(); cpi.setByOffset(comp.xZConstructionPlane,V(off)); p=comp.constructionPlanes.add(cpi)
            if abs(p.geometry.origin.y*10+d)<0.05: p.name=name; p.isLightBulbOn=False; return p
            p.deleteMe()
    def sign_toward(sk,vec):
        n=sk.xDirection.crossProduct(sk.yDirection); return 1.0 if n.dotProduct(vec)>0 else -1.0
    def profiles(sk):
        coll=adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): coll.add(sk.profiles.item(i))
        return coll
    def extrude(sk,op,start,dist,vec,bodies=None,name=None):
        s=sign_toward(sk,vec); inp=feats.extrudeFeatures.createInput(profiles(sk),op)
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(s*start/10)); inp.setDistanceExtent(False,V(s*dist/10))
        if bodies: inp.participantBodies=bodies
        f=feats.extrudeFeatures.add(inp); sk.isLightBulbOn=False
        if name and f.bodies.count>0: f.bodies.item(0).name=name
        return f
    sb=body('SLAB_frame').boundingBox
    ZT=180.0; YBK=wy(P3(0,sb.minPoint.y,sb.minPoint.z)); YC=YBK-0.5; YF=-sb.minPoint.z*10*S
    ZS=(sb.minPoint.z+sb.maxPoint.z)/2*10      # slab centre design Z (-27.4)
    PW=2.2; PWW=1.7; DTOP=28.0; YTOP=yfront(13.0,ZT)-DTOP; HWT=90.0
    def hwE(z): return 100-(100-HWT)*(z/ZT)**PWW
    def ybE(z): return -85+(YTOP+85)*(z/ZT)**PW
    def nE(z): return 2.6-0.6*(z/ZT)
    def section_pts(hw,dep,n,rc,N=241):
        ai=hw-rc; bi=dep-2*rc
        th=[math.pi*i/(N-1) for i in range(N)]
        def sp(t):
            c=math.cos(t); s=math.sin(t)
            return (ai*(1 if c>=0 else -1)*abs(c)**(2.0/n), -rc-bi*abs(s)**(2.0/n))
        P=[sp(t) for t in th]; Q=[]
        for i in range(N):
            a=P[max(i-1,0)]; b=P[min(i+1,N-1)]; tu=b[0]-a[0]; tv=b[1]-a[1]; L=math.hypot(tu,tv) or 1e-9
            Q.append((P[i][0]+rc*(-tv/L),P[i][1]+rc*(tu/L)))
        Q[0]=(hw,-rc); Q[-1]=(-hw,-rc)
        tot=sum(math.hypot(Q[i+1][0]-Q[i][0],Q[i+1][1]-Q[i][1]) for i in range(N-1)); dmin=max(3.0,tot/64.0)
        inner=[]; last=Q[0]; acc=0.0
        for i in range(1,N-1):
            acc+=math.hypot(Q[i][0]-last[0],Q[i][1]-last[1]); last=Q[i]
            if acc>=dmin and math.hypot(Q[i][0]-Q[-1][0],Q[i][1]-Q[-1][1])>=dmin: inner.append(Q[i]); acc=0.0
        return ai, inner
    def draw_section(sk,z,yf,hw,dep,n,rc):
        cu,mid=section_pts(hw,dep,n,rc)
        Q=lambda x,y: sk.modelToSketchSpace(Dw(x,y,z))
        L=sk.sketchCurves.sketchLines; A=sk.sketchCurves.sketchArcs; k=math.sqrt(0.5)
        ln=L.addByTwoPoints(Q(XC-cu,yf),Q(XC+cu,yf)); ln.isFixed=True
        aR=A.addByThreePoints(ln.endSketchPoint,Q(XC+cu+rc*k,yf-rc+rc*k),Q(XC+hw,yf-rc)); aR.isFixed=True
        aL=A.addByThreePoints(Q(XC-hw,yf-rc),Q(XC-cu-rc*k,yf-rc+rc*k),ln.startSketchPoint); aL.isFixed=True
        cps=[aR.endSketchPoint,Q(XC+hw,yf-rc-2.0)]+[Q(XC+u,yf+v) for (u,v) in mid]+[Q(XC-hw,yf-rc-2.0),aL.startSketchPoint]
        sk.sketchCurves.sketchControlPointSplines.add(cps,adsk.fusion.SplineDegrees.SplineDegreeThree)
        if sk.profiles.count<1: raise Exception(f'no profile at z{z}')
        return max((sk.profiles.item(i) for i in range(sk.profiles.count)),key=lambda p:p.areaProperties().area), cu
    def corners(bname,yc,rads,minh=0.5):
        b=body(bname); res=[]; front=None
        for f in b.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wy(f.centroid)-yc)<0.5: front=f
        if front is None: return 'no front face'
        coll=adsk.core.ObjectCollection.create()
        for e in front.edges:
            if abs(wz(e.startVertex.geometry)-wz(e.endVertex.geometry))>minh: coll.add(e)
        for r in rads:
            try:
                fi=feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(coll,V(r/10),True); feats.filletFeatures.add(fi)
                res.append(f'R{r} n{coll.count}'); break
            except Exception as ex: res.append(f'R{r} fail '+str(ex).splitlines()[-1][:60])
        return res
    WALL=2.5; GAP=0.3; up=V3(0.0,S,C)
    # ---------------- door plate ----------------
    def door():
        old=body('DOOR_plate')
        if old: old.deleteMe()
        for i in range(comp.sketches.count-1,-1,-1):
            s=comp.sketches.item(i)
            if s.name.startswith('skD_'): s.deleteMe()
        off=WALL+GAP
        sk=sk_on(fl); sk.name='skD_plate'
        pr,cu=draw_section(sk,0.0,YF-off,hwE(0)-off,(YF-ybE(0))-2*off,nE(0),12.0-off)
        inp=feats.extrudeFeatures.createInput(pr,NEW); s=sign_toward(sk,up)
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(0.0)); inp.setDistanceExtent(False,V(s*WALL/10))
        f=feats.extrudeFeatures.add(inp); b=f.bodies.item(0); b.name='DOOR_plate'; sk.isLightBulbOn=False
        # chin cut at y > YC-off
        sk2=sk_on(fl); sk2.name='skD_chin'; Q=lambda x,y: sk2.modelToSketchSpace(Dw(x,y,0.0))
        sk2.sketchCurves.sketchLines.addTwoPointRectangle(Q(-130.0,YC-off),Q(130.0,60.0))
        extrude(sk2,CUT,-5.0,15.0,up,[b])
        c=corners('DOOR_plate',YC-off,(12.0-off,8.0,6.0),0.5)
        bb=b.boundingBox
        return {'vol':round(b.volume,1),'corners':c,'front_y':round(YC-off,2),'hw':round(hwE(0)-off,1)}
    step('door plate',door)
    # ---------------- slab plate boss on the slot wall ----------------
    D_BOSS=9.0; D_WALL=12.3
    def boss():
        # Build the boss as a NEW body, verify zero interference with SLAB_frame, then combine JOIN into HOUSING_E.
        # (The original run used extrude JOIN with participantBodies=[hb]; Fusion still merged the overlapping SLAB_frame
        #  into HOUSING_E and the slab had to be recovered from revD.f3d. Never JOIN-extrude near other bodies.)
        hb=body('HOUSING_E'); slab=body('SLAB_frame')
        for i in range(comp.sketches.count-1,-1,-1):
            s=comp.sketches.item(i)
            if s.name.startswith('skB_'): s.deleteMe()
        pl=yplane(D_BOSS,'D9_plane')
        sk=sk_on(pl); sk.name='skB_boss'; Q=lambda x,Z: sk.modelToSketchSpace(P3(x/10,-D_BOSS/10,Z/10))
        X0,X1=XC-98.7,XC+98.7; Z0,Z1=ZS-62.5,ZS+62.2
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(X0,Z0),Q(X1,Z1))
        f=extrude(sk,NEW,0.0,(D_WALL-D_BOSS)+0.5,V3(0,-1,0),None,'BOSS_tmp')
        bt=body('BOSS_tmp')
        coll=adsk.core.ObjectCollection.create(); coll.add(bt); coll.add(slab)
        r=des.analyzeInterference(des.createInterferenceInput(coll))
        iv=round(sum(r.item(i).interferenceBody.volume for i in range(r.count))*1000,2) if r else 0.0
        if iv>0: raise Exception(f'BOSS_tmp interferes with SLAB_frame: {iv} mm3')
        tools=adsk.core.ObjectCollection.create(); tools.add(bt)
        ci=feats.combineFeatures.createInput(hb,tools); ci.operation=JOIN; ci.isKeepToolBodies=False; feats.combineFeatures.add(ci)
        return {'X':(round(X0,1),round(X1,1)),'Z':(round(Z0,1),round(Z1,1)),'d':(D_BOSS,D_WALL+0.5),'boss_vs_slab_mm3':iv,'housing_vol':round(body('HOUSING_E').volume,1)}
    step('boss',boss)
    def opening():
        hb=body('HOUSING_E'); pl=plane('D9_plane')
        sk=sk_on(pl); sk.name='skB_open'; Q=lambda x,Z: sk.modelToSketchSpace(P3(x/10,-D_BOSS/10,Z/10))
        L=sk.sketchCurves.sketchLines
        # main opening -60..53 x (ZS-30..ZS+30)
        L.addTwoPointRectangle(Q(-60.0,ZS-30.0),Q(53.0,ZS+30.0))
        f1=extrude(sk,CUT,-1.0,8.0,V3(0,-1,0),[hb])          # d 8 -> 16
        # notch for the 2-pin header pins (x 26..34.5, Z ZS+29 .. ZS+36)
        sk2=sk_on(pl); sk2.name='skB_notch'; Q2=lambda x,Z: sk2.modelToSketchSpace(P3(x/10,-D_BOSS/10,Z/10))
        sk2.sketchCurves.sketchLines.addTwoPointRectangle(Q2(26.0,ZS+29.0),Q2(34.5,ZS+36.0))
        extrude(sk2,CUT,-1.0,8.0,V3(0,-1,0),[hb])
        # 4 x dia 2.7 screw holes at glass-relative (+-47.5, +-34)
        sk3=sk_on(pl); sk3.name='skB_holes'; Q3=lambda x,Z: sk3.modelToSketchSpace(P3(x/10,-D_BOSS/10,Z/10))
        for x in (-47.5,47.5):
            for dz in (-34.0,34.0):
                sk3.sketchCurves.sketchCircles.addByCenterRadius(Q3(x,ZS+dz),0.135)
        extrude(sk3,CUT,-1.0,8.0,V3(0,-1,0),[hb])
        return {'opening':(-60,53,round(ZS-30,1),round(ZS+30,1)),'holes_Z':(round(ZS-34,1),round(ZS+34,1)),'housing_vol':round(body('HOUSING_E').volume,1)}
    step('opening',opening)
    def pads():
        hb=body('HOUSING_E'); pl=plane('D9_plane')
        sk=sk_on(pl); sk.name='skB_pads'; Q=lambda x,Z: sk.modelToSketchSpace(P3(x/10,-D_BOSS/10,Z/10))
        Zp0,Zp1=ZS+40.0,ZS+48.0
        for x0,x1 in ((-90.0,-30.0),(-30.0,30.0),(30.0,90.0)):
            sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(x0,Zp0),Q(x1,Zp1))
        f=extrude(sk,JOIN,-0.2,2.8,V3(0,1,0),[hb])          # from d 9.2 (inside boss) forward to d 6.4 (JOIN ok here: no other body overlaps the pads)
        return {'Z':(round(Zp0,1),round(Zp1,1)),'bodies':[f.bodies.item(i).name for i in range(f.bodies.count)],'housing_vol':round(body('HOUSING_E').volume,1)}
    step('pads',pads)
    def check():
        out={}
        hb=body('HOUSING_E'); out['housing_faces']=hb.faces.count
        # interference housing vs LCD parts and slab
        names=['SLAB_frame','LCD_glass','LCD_pcb_76x110','LCD_pogo_header_d14.1','LCD_2x2_header_d15.4','LCD_pins_d16.0','LCD_panelFPC_conn_d9.5']
        res=[]
        for nm in names:
            b=body(nm)
            if not b: continue
            try:
                coll=adsk.core.ObjectCollection.create(); coll.add(hb); coll.add(b)
                ii=des.createInterferenceInput(coll); r=des.analyzeInterference(ii)
                vol=sum(r.item(i).interferenceBody.volume for i in range(r.count)) if r else 0.0
                res.append((nm,round(vol*1000,2)))
            except Exception as ex: res.append((nm,'ERR '+str(ex)[:40]))
        out['interference_mm3']=res
        d=body('DOOR_plate')
        if d:
            coll=adsk.core.ObjectCollection.create(); coll.add(hb); coll.add(d)
            try:
                ii=des.createInterferenceInput(coll); r=des.analyzeInterference(ii)
                out['door_vs_housing_mm3']=round(sum(r.item(i).interferenceBody.volume for i in range(r.count))*1000,2) if r else 0.0
            except Exception as ex: out['door_vs_housing']='ERR'
        return out
    step('check',check)
    for i in range(comp.sketches.count): comp.sketches.item(i).isLightBulbOn=False
    out=json.dumps(log); print(out); return out
