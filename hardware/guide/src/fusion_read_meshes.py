"""Run inside Fusion (read-only script) on "HA Panel v5 - tapered", version 91.

It reads each named body's low-quality mesh and reports it, zlib-compressed and base64-encoded, in the text of a raised
RuntimeError (the tool's output channel for a read-only script). Nothing in the design is created, changed or saved.
Decode with tools: decode the text to {body: {xyz, idx}} JSON, then run model_outlines.py on it.
"""
import adsk.core, adsk.fusion, struct, zlib, base64

NAMES = ['MAIN_pcb', 'MAIN_PS1', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'RESP_pcb', 'RESP_top_env', 'TOUCH_PCB',
         'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env', 'BME680_env', 'LD2410C_env_F', 'PI5_F', 'PI5_F_cooler',
         'GPIO_plugA_env', 'GPIO_plugB_env', 'PD_5807_env', 'SPK_L', 'SPK_R', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE',
         'LCD_glass', 'RADAR_HOLDER', 'CRADLE_5807', 'BME_HOOD', 'RESP_CARRIER', 'HOUSING_F_cap', 'SLAB_frame',
         'LEAD_PIGTAIL_20V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_RADAR', 'LEAD_TOUCH', 'LEAD_BME680', 'LEAD_VEML',
         'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_DSI', 'LEAD_MIC_L', 'LEAD_MIC_R',
         'LEAD_PI_POWER', 'LEAD_USB_RESP', 'MAIN_J2_plug_env', 'RESP_usbc_plug_env']


def run(_context: str):
    app = adsk.core.Application.get()
    r = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    out, missing = bytearray(), []
    for name in NAMES:
        b = r.bRepBodies.itemByName(name)
        if b is None:
            missing.append(name); continue
        calc = b.meshManager.createMeshCalculator()
        calc.setQuality(adsk.fusion.TriangleMeshQualityOptions.LowQualityTriangleMesh)
        m = calc.calculate()
        xyz, idx = m.nodeCoordinatesAsFloat, m.nodeIndices
        nb = name.encode()
        out += struct.pack('<H', len(nb)) + nb + struct.pack('<II', len(xyz) // 3, len(idx))
        out += struct.pack('<%dh' % len(xyz), *[int(round(v * 100)) for v in xyz])  # 0.1 mm
        out += struct.pack('<%dH' % len(idx), *idx)
    z = base64.b64encode(zlib.compress(bytes(out), 9)).decode()
    raise RuntimeError('READOUT missing=%s len=%d\n%s' % (','.join(missing), len(z), z))
