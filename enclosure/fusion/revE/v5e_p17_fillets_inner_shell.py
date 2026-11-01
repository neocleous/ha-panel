# HA Panel rev E - p17 (2026-11-01, Claude): rebuild outer body as BODY_E (same generator as p16), fillets (floor R6, top rear R10,
# top front R3), INNER_E loft (wall 2.5), inner chin/slot cuts + R9.5 corners, then shell: REF_E_outer copy, HOUSING_E = BODY_E - INNER_E.
# As run in the session the copy used TemporaryBRepManager (copyPasteBodies failed in direct modelling); this file carries that fix.
# Result in session: HOUSING_E 200.1 cm3, INNER_E 1787.7, REF_E_outer 1972.9.
import adsk.core, adsk.fusion, json, math, traceback, os
C=math.cos(math.radians(12.0)); S=math.sin(math.radians(12.0)); T=math.tan(math.radians(12.0)); H=143.3; XC=-2.55; G=0.7
def run(context):
    app=adsk.core.Application.get(); des=adsk.fusion.Design.cast(app.activeProduct); comp=des.rootComponent; feats=comp.features
    V=adsk.core.ValueInput.createByReal; P3=adsk.core.Point3D.create; V3=adsk.core.Vector3D.create
    NEW=adsk.fusion.FeatureOperations.NewBodyFeatureOperation
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
    def sk_on(pl):
        sk=comp.sketches.add(pl); sk.isLightBulbOn=False; return sk
    def level_plane(z,name):
        ex=plane(name)
        if ex: return ex
        for off in (z/10,-z/10):
            cpi=comp.constructionPlanes.createInput(); cpi.setByOffset(fl,V(off)); p=comp.constructionPlanes.add(cpi)
            o=p.geometry.origin
            if abs(wz(o)-z)<0.05: p.name=name; p.isLightBulbOn=False; return p
            p.deleteMe()
    def show(names):
        for b in comp.bRepBodies: b.isLightBulbOn=b.name in names
    def finish(extra=None):
        for i in range(comp.sketches.count): comp.sketches.item(i).isLightBulbOn=False
        out=json.dumps(log+(extra or [])); flush(); print(out); return out
    # ---- rev E: slab slid down the ramp, chin recessed under the slab so the screen floats ----
    ZT=180.0
    def moveslab():
        # 1) home pose (glass front on Y=0, Z centred), 2) slide down the 12-deg plane so the slab's top-back corner sits on the crest (z = ZT)
        sb0=body('SLAB_frame').boundingBox
        dy=-sb0.maxPoint.y; dz0=-(sb0.minPoint.z+sb0.maxPoint.z)/2.0            # cm, back to home
        ztb_home=wz(P3(0,sb0.minPoint.y+dy,sb0.maxPoint.z+dz0))                   # world z of the top-back corner at home (206.8)
        dZ=(ZT-ztb_home)/C/10.0                                                    # cm along design Z (negative = down the ramp)
        coll=adsk.core.ObjectCollection.create()
        for b in comp.bRepBodies:
            if b.name.startswith('SLAB_') or b.name.startswith('LCD_'): coll.add(b)
        tr=adsk.core.Matrix3D.create(); tr.translation=V3(0.0,dy,dz0+dZ)
        if tr.translation.length<0.0002: return ('already placed',round(ztb_home,1))
        mf=feats.moveFeatures
        try:
            inp=mf.createInput2(coll); inp.defineAsFreeMove(tr); mf.add(inp); how='createInput2'
        except Exception:
            inp=mf.createInput(coll,tr); mf.add(inp); how='createInput'
        return (round(dy*10,2),round(dz0*10,2),round(dZ*10,2),coll.count,how)
    step('place slab',moveslab)
    sb=body('SLAB_frame').boundingBox
    log.append(f'slab bbox mm: x {round(sb.minPoint.x*10,1)}..{round(sb.maxPoint.x*10,1)} y {round(sb.minPoint.y*10,1)}..{round(sb.maxPoint.y*10,1)} z {round(sb.minPoint.z*10,1)}..{round(sb.maxPoint.z*10,1)}')
    def wy(p): return p.y*10*C-p.z*10*S
    YBK=wy(P3(0,sb.minPoint.y,sb.minPoint.z))   # world y of the slab bottom-back corner (8.0 after the slide)
    YC=YBK-0.5                                   # recessed chin face, 0.5 behind the slab's back edge
    ZBK=wz(P3(0,sb.minPoint.y,sb.minPoint.z))    # its height (48.0 after the slide)
    log.append({'slab_bottom_back':(round(YBK,2),round(ZBK,2)),'slab_bottom_front':(round(-sb.minPoint.z*10*S,2),round(wz(P3(0,sb.maxPoint.y,sb.minPoint.z)),2)),'slab_top_back_z':round(wz(P3(0,sb.minPoint.y,sb.maxPoint.z)),2),'glass_top_z':round(wz(P3(0,sb.maxPoint.y,sb.maxPoint.z)),2)})
    SLABTOP=max(wz(P3(x,y,zz)) for x in (sb.minPoint.x,sb.maxPoint.x) for y in (sb.minPoint.y,sb.maxPoint.y) for zz in (sb.minPoint.z,sb.maxPoint.z))
    PW=2.2; PWW=1.7; DTOP=28.0; YTOP=yfront(13.0,ZT)-DTOP; HWT=90.0   # crest = slab top-back corner after the slide
    EMB=0.0; YF=-sb.minPoint.z*10*S+EMB   # vertical front face: flush with slab bottom-front corner (+EMB forward)
    def hwE(z): return 100-(100-HWT)*(z/ZT)**PWW
    def ybE(z): return -85+(YTOP+85)*(z/ZT)**PW
    def depE(z): return YF-ybE(z)
    def nE(z): return 2.6-0.6*(z/ZT)
    def rcE(z): return min(12.0,0.5*depE(z)-2.0)
    def section_pts(hw,dep,n,rc,N=241):
        # offset-of-inner-D construction: inner superellipse (ai,bi) centred (0,-rc), offset outward by rc.
        ai=hw-rc; bi=dep-2*rc
        th=[math.pi*i/(N-1) for i in range(N)]
        def sp(t):
            c=math.cos(t); s=math.sin(t)
            return (ai*(1 if c>=0 else -1)*abs(c)**(2.0/n), -rc-bi*abs(s)**(2.0/n))
        P=[sp(t) for t in th]
        Q=[]
        for i in range(N):
            a=P[max(i-1,0)]; b=P[min(i+1,N-1)]; tu=b[0]-a[0]; tv=b[1]-a[1]; L=math.hypot(tu,tv) or 1e-9
            nu,nv=-tv/L,tu/L
            Q.append((P[i][0]+rc*nu,P[i][1]+rc*nv))
        Q[0]=(hw,-rc); Q[-1]=(-hw,-rc)
        # thin by arc length: >=3 mm spacing, none within that of the end points
        tot=sum(math.hypot(Q[i+1][0]-Q[i][0],Q[i+1][1]-Q[i][1]) for i in range(N-1)); dmin=max(3.0,tot/64.0)
        inner=[]; last=Q[0]; acc=0.0
        for i in range(1,N-1):
            acc+=math.hypot(Q[i][0]-last[0],Q[i][1]-last[1]); last=Q[i]
            if acc>=dmin and math.hypot(Q[i][0]-Q[-1][0],Q[i][1]-Q[-1][1])>=dmin: inner.append(Q[i]); acc=0.0
        return ai, inner
    def build():
        for nm in ('PREVIEW_E','PREVIEW_E2','PREVIEW_E3','BODY_E','INNER_E','HOUSING_E'):
            old=body(nm)
            if old: old.deleteMe()
        for i in range(comp.sketches.count-1,-1,-1):
            s=comp.sketches.item(i)
            if s.name.startswith('skE_'): s.deleteMe()
            elif s.sketchCurves.count==4 and s.profiles.count==1:
                bb=s.boundingBox
                if abs(bb.minPoint.y)<1e-3 and abs(bb.maxPoint.y)<1e-3 and abs(bb.minPoint.x*10-(sb.minPoint.x*10-0.3))<0.1 and abs(bb.maxPoint.x*10-(sb.maxPoint.x*10+0.3))<0.1: s.deleteMe()
        secs=[0,20,40,60,80,100,120,140,155,165,172,ZT]
        li=feats.loftFeatures.createInput(NEW); info=[]
        for z in secs:
            pl=fl if z==0 else level_plane(z,f'level_{int(z)}')
            sk=sk_on(pl); sk.name=f'skE_{int(z)}'
            yf=YF; hw=hwE(z); dep=depE(z); n=nE(z); rc=rcE(z)
            cu,mid=section_pts(hw,dep,n,rc)
            Q=lambda x,y: sk.modelToSketchSpace(Dw(x,y,z))
            L=sk.sketchCurves.sketchLines; A=sk.sketchCurves.sketchArcs; k=math.sqrt(0.5)
            ln=L.addByTwoPoints(Q(XC-cu,yf),Q(XC+cu,yf)); ln.isFixed=True
            aR=A.addByThreePoints(ln.endSketchPoint,Q(XC+cu+rc*k,yf-rc+rc*k),Q(XC+hw,yf-rc)); aR.isFixed=True
            aL=A.addByThreePoints(Q(XC-hw,yf-rc),Q(XC-cu-rc*k,yf-rc+rc*k),ln.startSketchPoint); aL.isFixed=True
            cps=[aR.endSketchPoint,Q(XC+hw,yf-rc-2.0)]+[Q(XC+u,yf+v) for (u,v) in mid]+[Q(XC-hw,yf-rc-2.0),aL.startSketchPoint]
            spl=sk.sketchCurves.sketchControlPointSplines.add(cps,adsk.fusion.SplineDegrees.SplineDegreeThree)
            tang='CP'
            if sk.profiles.count<1: raise Exception(f'no profile at z{z}')
            pr=max((sk.profiles.item(i) for i in range(sk.profiles.count)),key=lambda p:p.areaProperties().area)
            li.loftSections.add(pr); sk.isLightBulbOn=False
            info.append((z,round(hw,1),round(dep,1),round(rc,1),round(cu,1),sk.profiles.count,tang))
        li.isSolid=True
        f=feats.loftFeatures.add(li); b=f.bodies.item(0); b.name='BODY_E'
        return (ZT,round(SLABTOP,1),round(YF,2),round(YC,2),round(ZBK,1),info)
    step('loft',build)
    def chincut():
        b=body('BODY_E')
        sk=sk_on(fl); sk.name='skE_chin'; Q=lambda x,y: sk.modelToSketchSpace(Dw(x,y,0.0))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(-130.0,YC),Q(130.0,60.0))
        n=sk.xDirection.crossProduct(sk.yDirection); up=V3(0.0,S,C); s=1.0 if n.dotProduct(up)>0 else -1.0
        coll=adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): coll.add(sk.profiles.item(i))
        inp=feats.extrudeFeatures.createInput(coll,adsk.fusion.FeatureOperations.CutFeatureOperation)
        z0=-5.0; z1=ZBK+6.0   # from below the floor to just above the slab's bottom-back edge (above that the slot already cut it)
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(s*z0/10)); inp.setDistanceExtent(False,V(s*(z1-z0)/10))
        inp.participantBodies=[b]
        feats.extrudeFeatures.add(inp); sk.isLightBulbOn=False
        return (round(YC,2),round(z0,1),round(z1,1))
    def corners():
        b=body('BODY_E'); res=[]
        front=None
        for f in b.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wy(f.centroid)-YC)<0.5: front=f
        if front is None: return 'no chin face'
        coll=adsk.core.ObjectCollection.create()
        for e in front.edges:
            if abs(wz(e.startVertex.geometry)-wz(e.endVertex.geometry))>30: coll.add(e)
        for r in (12.0,10.0,8.0,6.0):
            try:
                fi=feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(coll,V(r/10),True); feats.filletFeatures.add(fi)
                res.append(f'corner R{r} n{coll.count}'); break
            except Exception as ex: res.append(f'corner R{r} fail '+str(ex).splitlines()[-1][:60])
        return res
    def slabcut():
        b=body('BODY_E')
        sk=sk_on(comp.xZConstructionPlane); sk.name='skE_slot'; Q=lambda x,z: sk.modelToSketchSpace(P3(x/10,0,z/10))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(sb.minPoint.x*10-0.3,sb.minPoint.z*10-0.3),Q(sb.maxPoint.x*10+0.3,sb.maxPoint.z*10+0.3))
        n=sk.xDirection.crossProduct(sk.yDirection); s=1.0 if n.dotProduct(V3(0,-1,0))>0 else -1.0
        coll=adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): coll.add(sk.profiles.item(i))
        inp=feats.extrudeFeatures.createInput(coll,adsk.fusion.FeatureOperations.CutFeatureOperation)
        d0=-60.0; d1=-sb.minPoint.y*10+0.3   # from 60 mm in front of glass to 0.3 behind slab back
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(s*d0/10)); inp.setDistanceExtent(False,V(s*(d1-d0)/10))
        inp.participantBodies=[b]
        feats.extrudeFeatures.add(inp); sk.isLightBulbOn=False
        return (round(d0,1),round(d1,1),b.faces.count)
    def fil(bname='BODY_E',rf=6.0,rtop=10.0,rfront=3.0):
        b=body(bname); res=[]
        def planar_face_at(z):
            best=None
            for f in b.faces:
                if f.geometry.objectType.endswith('Plane'):
                    c=f.centroid
                    if abs(wz(c)-z)<1.0: best=f
            return best
        f=planar_face_at(0)
        if f is None: res.append('z0 noface')
        else:
            for r in (rf,rf-1,rf-2):
                try:
                    coll=adsk.core.ObjectCollection.create()
                    for e in f.edges: coll.add(e)
                    fi=feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(coll,V(r/10),True); feats.filletFeatures.add(fi)
                    res.append(f'z0 R{r} n{coll.count}'); break
                except Exception as ex: res.append(f'z0 R{r} fail '+str(ex).splitlines()[-1][:60])
        f=planar_face_at(ZT)
        if f is None: res.append('top noface')
        else:
            front=adsk.core.ObjectCollection.create(); rest=adsk.core.ObjectCollection.create()
            for e in f.edges:
                (front if e.geometry.objectType.endswith('Line3D') else rest).add(e)
            for r in (rtop,rtop-1,rtop-2,rtop-3):
                try:
                    fi=feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(rest,V(r/10),True); feats.filletFeatures.add(fi)
                    res.append(f'top rear R{r} n{rest.count}'); break
                except Exception as ex: res.append(f'top rear R{r} fail '+str(ex).splitlines()[-1][:60])
            # re-find the straight front edge of the top face after the rear fillet
            f=planar_face_at(ZT); front=adsk.core.ObjectCollection.create()
            if f:
                for e in f.edges:
                    if e.geometry.objectType.endswith('Line3D'): front.add(e)
            for r in (rfront,rfront-1):
                try:
                    fi=feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(front,V(r/10),True); feats.filletFeatures.add(fi)
                    res.append(f'top front R{r} n{front.count}'); break
                except Exception as ex: res.append(f'top front R{r} fail '+str(ex).splitlines()[-1][:60])
        return res
    step('slab cut',slabcut)
    step('chin cut',chincut)
    step('corner fillets',corners)
    step('fillets',fil)
    WALL=2.5
    def build_inner():
        secs=[-1,20,40,60,80,100,120,140,155,165,172,ZT-WALL]
        li=feats.loftFeatures.createInput(NEW); info=[]
        for z in secs:
            zs=max(z,0.0)
            pl=fl if z==0 else level_plane(z,f'level_{z:g}'.replace('-','m').replace('.','p'))
            sk=sk_on(pl); sk.name=f'skE_in_{z:g}'
            yf=YF-WALL; hw=hwE(zs)-WALL; dep=(YF-ybE(zs))-2*WALL; n=nE(zs); rc=12.0-WALL
            cu,mid=section_pts(hw,dep,n,rc)
            Q=lambda x,y: sk.modelToSketchSpace(Dw(x,y,z))
            L=sk.sketchCurves.sketchLines; A=sk.sketchCurves.sketchArcs; k=math.sqrt(0.5)
            ln=L.addByTwoPoints(Q(XC-cu,yf),Q(XC+cu,yf)); ln.isFixed=True
            aR=A.addByThreePoints(ln.endSketchPoint,Q(XC+cu+rc*k,yf-rc+rc*k),Q(XC+hw,yf-rc)); aR.isFixed=True
            aL=A.addByThreePoints(Q(XC-hw,yf-rc),Q(XC-cu-rc*k,yf-rc+rc*k),ln.startSketchPoint); aL.isFixed=True
            cps=[aR.endSketchPoint,Q(XC+hw,yf-rc-2.0)]+[Q(XC+u,yf+v) for (u,v) in mid]+[Q(XC-hw,yf-rc-2.0),aL.startSketchPoint]
            sk.sketchCurves.sketchControlPointSplines.add(cps,adsk.fusion.SplineDegrees.SplineDegreeThree)
            if sk.profiles.count<1: raise Exception(f'no inner profile at z{z}')
            pr=max((sk.profiles.item(i) for i in range(sk.profiles.count)),key=lambda p:p.areaProperties().area)
            li.loftSections.add(pr); sk.isLightBulbOn=False
            info.append((z,round(hw,1),round(dep,1)))
        li.isSolid=True
        f=feats.loftFeatures.add(li); b=f.bodies.item(0); b.name='INNER_E'
        return info
    step('inner loft',build_inner)
    def inner_cuts():
        b=body('INNER_E'); out=[]
        # chin: remove y > YC-WALL below z 60
        sk=sk_on(fl); sk.name='skE_in_chin'; Q=lambda x,y: sk.modelToSketchSpace(Dw(x,y,0.0))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(-130.0,YC-WALL),Q(130.0,60.0))
        n=sk.xDirection.crossProduct(sk.yDirection); up=V3(0.0,S,C); s=1.0 if n.dotProduct(up)>0 else -1.0
        coll=adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): coll.add(sk.profiles.item(i))
        inp=feats.extrudeFeatures.createInput(coll,adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(s*-5.0/10)); inp.setDistanceExtent(False,V(s*65.0/10))
        inp.participantBodies=[b]; feats.extrudeFeatures.add(inp); sk.isLightBulbOn=False; out.append('chin ok')
        # slot: remove in front of d 12.3+WALL within the slab Z range +-5
        sk=sk_on(comp.xZConstructionPlane); sk.name='skE_in_slot'; Q=lambda x,z: sk.modelToSketchSpace(P3(x/10,0,z/10))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(sb.minPoint.x*10-5,sb.minPoint.z*10-5),Q(sb.maxPoint.x*10+5,sb.maxPoint.z*10+5))
        n=sk.xDirection.crossProduct(sk.yDirection); s=1.0 if n.dotProduct(V3(0,-1,0))>0 else -1.0
        coll=adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): coll.add(sk.profiles.item(i))
        inp=feats.extrudeFeatures.createInput(coll,adsk.fusion.FeatureOperations.CutFeatureOperation)
        d0=-60.0; d1=-sb.minPoint.y*10+0.3+WALL
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(s*d0/10)); inp.setDistanceExtent(False,V(s*(d1-d0)/10))
        inp.participantBodies=[b]; feats.extrudeFeatures.add(inp); sk.isLightBulbOn=False; out.append(f'slot ok d{d1:.1f}')
        # inner chin corner fillets R9.5 (match the outer R12)
        front=None
        for f in b.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wy(f.centroid)-(YC-WALL))<0.5: front=f
        if front is not None:
            ec=adsk.core.ObjectCollection.create()
            for e in front.edges:
                if abs(wz(e.startVertex.geometry)-wz(e.endVertex.geometry))>30: ec.add(e)
            for r in (9.5,8.0,6.0):
                try:
                    fi=feats.filletFeatures.createInput(); fi.edgeSetInputs.addConstantRadiusEdgeSet(ec,V(r/10),True); feats.filletFeatures.add(fi); out.append(f'inner corners R{r} n{ec.count}'); break
                except Exception as ex: out.append(f'inner corner R{r} fail '+str(ex).splitlines()[-1][:60])
        else: out.append('no inner chin face')
        return out
    step('inner cuts',inner_cuts)
    def make_shell():
        # copyPasteBodies is NOT supported in direct modelling -> TemporaryBRepManager copy.
        # Keeps REF_E_outer (unshelled reference of the final outer body); HOUSING_E = REF_E_outer - INNER_E.
        src_b=body('BODY_E'); inner=body('INNER_E')
        tmp=adsk.fusion.TemporaryBRepManager.get()
        ref=comp.bRepBodies.add(tmp.copy(src_b)); ref.name='REF_E_outer'; ref.isLightBulbOn=False
        hb=src_b; hb.name='HOUSING_E'
        tools=adsk.core.ObjectCollection.create(); tools.add(inner)
        ci=feats.combineFeatures.createInput(hb,tools); ci.operation=adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies=True
        feats.combineFeatures.add(ci)
        hb=body('HOUSING_E'); inner.isLightBulbOn=False
        return {'ref_vol':round(ref.volume,1),'inner_vol':round(inner.volume,1),'housing_vol':round(hb.volume,1),'housing_faces':hb.faces.count,'mass_g_petgcf':round(hb.volume*1.27,0)}
    step('shell',make_shell)
    def look():
        b=body('HOUSING_E')
        for i in range(des.appearances.count):
            if des.appearances.item(i).name=='FAB_mock': b.appearance=des.appearances.item(i); break
        out={'valid':b.isValid,'faces':b.faces.count}
        try: out['vol']=round(b.volume,1)
        except Exception as ex: out['vol']='ERR'
        return out
    step('appearance',look)
    def clear():
        # inner top (ZT-2.5) vs tallest LCD protrusion behind the slab back
        hi=[]
        for nm in ('LCD_pins_d16.0','LCD_2x2_header_d15.4','LCD_Pi_standoff_d15.2','LCD_Pi_standoff_d15.2 (1)','LCD_pogo_header_d14.1','LCD_pcb_76x110'):
            e=body(nm)
            if not e: continue
            bb=e.boundingBox; cs=[P3(x,y,zz) for x in (bb.minPoint.x,bb.maxPoint.x) for y in (bb.minPoint.y,bb.maxPoint.y) for zz in (bb.minPoint.z,bb.maxPoint.z)]
            hi.append((nm,round(max(wz(c) for c in cs),1)))
        return {'ZT':ZT,'inner_top':ZT-2.5,'protrusions_wz':hi}
    step('clearance',clear)
    def shots():
        vp=app.activeViewport; show(('HOUSING_E','SLAB_frame','LCD_glass'))
        vp.visualStyle=adsk.core.VisualStyles.ShadedVisualStyle
        b=body('HOUSING_E'); bb=b.boundingBox; tgt=P3((bb.minPoint.x+bb.maxPoint.x)/2,(bb.minPoint.y+bb.maxPoint.y)/2,(bb.minPoint.z+bb.maxPoint.z)/2+1.5)
        docs=os.path.expanduser('~/Documents'); names=[]
        for nm,dv in (('front34',(-0.6,0.744,0.30)),('under',(-0.5,0.5,-0.75)),('rear34',(-0.5,-0.78,0.38))):
            d=V3(*dv); d.normalize(); cam=vp.camera; cam.cameraType=adsk.core.CameraTypes.PerspectiveCameraType
            cam.target=tgt; cam.eye=P3(tgt.x+d.x*90,tgt.y+d.y*90,tgt.z+d.z*90); cam.upVector=V3(0,S,C); cam.isFitView=True; vp.camera=cam; vp.refresh()
            p=os.path.join(docs,f'HA_v5e17_{nm}.png'); vp.saveAsImageFile(p,900,600); names.append(p)
        return names
    step('screenshots',shots)
    return finish()
