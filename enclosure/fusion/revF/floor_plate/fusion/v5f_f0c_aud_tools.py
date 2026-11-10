# rev F f0c (2026-11-09): floor plate pass, block 0 - rebuild the assembly audit's tool templates for the self-checks.
#   Runs the audit's own ~/Documents/ha_asm_audit/aud_b0_tools.py main() unchanged (seven hidden AUD_* bodies parked at
#   x_rel 300 + 70 n, y -60, working end at z 0, axis world +z; idempotent, nothing joined), with its LOG redirected to
#   this pass's log ~/Documents/v5f_fp_log.json so the audit's evidence log stays as the audit left it.
#   Then reads back names, volumes, visibility. Writes ~/Documents/HA_panel_renders/fp/f0c_status.json.
#   Loader per README lesson 86 (modifying: no readOnly flag).
import adsk.core, adsk.fusion, json, os, time, traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp/f0c_status.json')
SRC = os.path.expanduser('~/Documents/ha_asm_audit/aud_b0_tools.py')


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S')}
    try:
        app = adsk.core.Application.get()
        doc = app.activeDocument
        st['active'] = doc.name
        st['before'] = [doc.dataFile.versionNumber, doc.isModified]
        if doc.name != 'HA Panel v5 - tapered':
            raise RuntimeError('active document is %r' % doc.name)
        ns = {'__name__': 'aud_b0_tools_fp'}
        exec(compile(open(SRC, encoding='utf-8').read(), SRC, 'exec'), ns)
        ns['LOG'] = os.path.expanduser('~/Documents/v5f_fp_log.json')
        ns['main']()
        des = adsk.fusion.Design.cast(app.activeProduct)
        st['AUD'] = {b.name: [round(b.volume, 3), b.isLightBulbOn, b.lumps.count]
                     for b in des.rootComponent.bRepBodies if b.name.startswith('AUD_')}
        st['n_bodies'] = des.rootComponent.bRepBodies.count
        st['after'] = [doc.dataFile.versionNumber, doc.isModified]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
