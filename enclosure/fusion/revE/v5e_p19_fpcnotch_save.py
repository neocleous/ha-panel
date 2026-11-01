# rev E p19 (2026-11-01): notch HOUSING_E boss front face for LCD panel FPC connector, interference check, f3d export, save.
# Run via Fusion MCP fusion_mcp_execute (featureType=script). Result: interf 0.0 mm3, housing 246.4 cm3, f3d+save ok.
import adsk.core, adsk.fusion, json, traceback
def run(context):
    app=adsk.core.Application.get(); des=adsk.fusion.Design.cast(app.activeProduct); comp=des.rootComponent; feats=comp.features
    V=adsk.core.ValueInput.createByReal; P3=adsk.core.Point3D.create; V3=adsk.core.Vector3D.create
    out={}
    try:
        def body(n):
            for b in comp.bRepBodies:
                if b.name==n: return b
        def plane(n):
            for i in range(comp.constructionPlanes.count):
                if comp.constructionPlanes.item(i).name==n: return comp.constructionPlanes.item(i)
        hb=body('HOUSING_E'); c=body('LCD_panelFPC_conn_d9.5'); bb=c.boundingBox
        out['conn_bbox_mm']=[round(bb.minPoint.x*10,1),round(bb.maxPoint.x*10,1),round(bb.minPoint.y*10,1),round(bb.maxPoint.y*10,1),round(bb.minPoint.z*10,1),round(bb.maxPoint.z*10,1)]
        pl=plane('D9_plane'); sk=comp.sketches.add(pl); sk.name='skB_fpcnotch'; sk.isLightBulbOn=False
        Q=lambda x,Z: sk.modelToSketchSpace(P3(x/10,-0.9,Z/10))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(Q(bb.minPoint.x*10-1.0,bb.minPoint.z*10-1.0),Q(bb.maxPoint.x*10+1.0,bb.maxPoint.z*10+1.0))
        n=sk.xDirection.crossProduct(sk.yDirection); s=1.0 if n.dotProduct(V3(0,-1,0))>0 else -1.0
        coll=adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count): coll.add(sk.profiles.item(i))
        inp=feats.extrudeFeatures.createInput(coll,adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.startExtent=adsk.fusion.OffsetStartDefinition.create(V(s*-0.1)); inp.setDistanceExtent(False,V(s*0.2))   # d 8 -> 10
        inp.participantBodies=[hb]; feats.extrudeFeatures.add(inp); sk.isLightBulbOn=False
        cc=adsk.core.ObjectCollection.create(); cc.add(hb); cc.add(c)
        r=des.analyzeInterference(des.createInterferenceInput(cc))
        out['interf_after_mm3']=round(sum(r.item(i).interferenceBody.volume for i in range(r.count))*1000,2) if r else 0.0
        out['housing_vol']=round(body('HOUSING_E').volume,1)
        doc=app.activeDocument
        docs='/Users/danielneocleous/Documents'; p=docs+'/HA Panel v5 - tapered revE-wip 2026-11-01.f3d'
        em=des.exportManager; eo=em.createFusionArchiveExportOptions(p); out['f3d']=em.execute(eo)
        out['saved']=doc.save('rev E WIP 2026-11-01 b: slab restored, HOUSING_E rebuilt, boss/opening/pads, DOOR_plate (Claude)')
    except Exception:
        out['FAIL']=traceback.format_exc().splitlines()[-1]
    s=json.dumps(out); print(s); return s
