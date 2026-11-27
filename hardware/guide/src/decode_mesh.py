import sys, json, re, zlib, base64, struct
raw = open(sys.argv[1]).read()
try:
    raw = json.loads(raw)["error"]
except Exception:
    pass
m = re.search(r"READOUT missing=([^ ]*) len=(\d+)\\?n?\s*([A-Za-z0-9+/=]+)", raw)
missing, n, b64 = m.group(1), int(m.group(2)), m.group(3)
assert len(b64) == n, (len(b64), n)
data = zlib.decompress(base64.b64decode(b64))
i = 0; bodies = {}
while i < len(data):
    (ln,) = struct.unpack_from('<H', data, i); i += 2
    name = data[i:i+ln].decode(); i += ln
    nn, ni = struct.unpack_from('<II', data, i); i += 8
    xyz = struct.unpack_from('<%dh' % (nn*3), data, i); i += nn*3*2
    idx = struct.unpack_from('<%dH' % ni, data, i); i += ni*2
    bodies[name] = {"xyz": [round(v/10, 2) for v in xyz], "idx": list(idx)}  # mm
print("missing:", missing, "bodies:", len(bodies), {k: len(v["idx"])//3 for k, v in bodies.items()})
json.dump(bodies, open(sys.argv[2], "w"))
