# change2/offline/chan.py - the data channel Fusion -> workspace: a payload packed into a grey PNG by cp2.send() on the Mac,
# read here with the Filesystem connector's read_media_file (which leaves the file under /tmp/claude-tool-results).
import sys, zlib, struct, json, glob, os
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def recv(path):
    im = Image.open(path); a = np.asarray(im.convert('L')).tobytes()
    n = struct.unpack('>Q', a[:8])[0]
    return zlib.decompress(a[8:8 + n])


def latest(pattern='/tmp/claude-tool-results/*/*.png'):
    return max(glob.glob(pattern), key=os.path.getmtime)


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '-' else latest()
    out = sys.argv[2]
    raw = recv(src)
    open(out, 'wb').write(raw)
    print(src, '->', out, len(raw))
