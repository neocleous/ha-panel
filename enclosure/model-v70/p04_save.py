# Saves the open document as a new version with the given description (brief: a version at the end of each block that
# changes the model, named as the last pass named its versions, "not for print"). CHANGES THE DOCUMENT'S HISTORY.
# Run: runpy.run_path(D + 'p04_save.py')['main'](description)  -> appends to p04_save.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def main(desc):
    k = L['load']()
    X = k.K()
    before = X.state()
    ok = X.doc.save(desc)
    line = '%s  save(%r) -> %s; before %s' % (L['stamp'](), desc, ok, before)
    open(D + 'p04_save.txt', 'a').write(line + '\n')
    print(line)


def check():
    k = L['load']()
    X = k.K()
    df = X.doc.dataFile
    line = '%s  check: version %d of %d, modified %s, description %r' % (L['stamp'](), df.versionNumber, df.latestVersionNumber,
                                                                          X.doc.isModified, df.description)
    open(D + 'p04_save.txt', 'a').write(line + '\n')
    print(line)
