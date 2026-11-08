"""Write purchase fields (MPN, Manufacturer, DigiKey) into existing KiCad 9 schematic symbols by reference, in place.
Keeps every UUID; replaces a field's value if it exists, else inserts a hidden property after the last property.
Usage: python3 inject_fields.py <file.kicad_sch> <json map ref -> {field: value}>"""
import json, re, sys

def inject(path, fmap):
    s = open(path).read()
    out, pos, changed = [], 0, []
    for m in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id "[^"]+"\)[\s\S]*?\n\t\)', s):
        block = m.group(0)
        ref = re.search(r'\(property "Reference" "([^"]+)"', block)
        if not ref or ref.group(1) not in fmap:
            continue
        r = ref.group(1)
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+) [-\d.]+\)', block)
        x, y = at.group(1), at.group(2)
        nb = block
        for k, v in fmap[r].items():
            pat = re.compile(r'(\(property "%s" ")([^"]*)(")' % re.escape(k))
            if pat.search(nb):
                nb = pat.sub(lambda mm: mm.group(1) + v.replace('"', '\\"') + mm.group(3), nb, count=1)
            else:
                props = list(re.finditer(r'\n\t\t\(property "[^"]+"[\s\S]*?\n\t\t\)', nb))
                last = props[-1]
                new = ('\n\t\t(property "%s" "%s"\n\t\t\t(at %s %s 0)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n'
                       '\t\t\t\t)\n\t\t\t\t(hide yes)\n\t\t\t)\n\t\t)') % (k, v.replace('"', '\\"'), x, y)
                nb = nb[:last.end()] + new + nb[last.end():]
        out.append((m.start(), m.end(), nb)); changed.append(r)
    for a, b, nb in reversed(out):
        s = s[:a] + nb + s[b:]
    open(path, 'w').write(s)
    return changed

if __name__ == '__main__':
    print(inject(sys.argv[1], json.load(open(sys.argv[2]))))
