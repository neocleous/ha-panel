import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
img = mpimg.imread('/mnt/user-data/uploads/ballast/ballast_3_rear34_raw.png')
h, w = img.shape[:2]
fig = plt.figure(figsize=(16, 12), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.axis('off')
BB = dict(facecolor='#fcfcfb', edgecolor='none', alpha=0.92, pad=4)
def lab(xy, txt, xytext, c):
    ax.annotate(txt, xy=xy, xytext=xytext, fontsize=15, color='#0b0b0b', weight='bold', bbox=BB,
                arrowprops=dict(arrowstyle='->', color=c, lw=2.2))
lab((850, 800), 'C  steel plate 10 thick behind the Pi, 44 g', (70, 1090), '#2a78d6')
lab((1300, 760), 'B  steel sheet 2.5 thick under the left box, 29 g', (980, 1110), '#eb6834')
lab((450, 395), 'B  under the right box, 11 g', (60, 240), '#eb6834')
for xy, t in (((560, 640), 'cradle'), ((1060, 640), 'USB roll'), ((700, 420), 'Pi with its cooler'), ((1070, 830), 'anchor')):
    ax.annotate(t, xy=xy, xytext=(xy[0], xy[1]), fontsize=12, color='#0b0b0b', bbox=dict(facecolor='#fcfcfb', edgecolor='none', alpha=0.8, pad=2), ha='center')
ax.text(30, 40, 'Plate unit from behind, door and shell off (version 65 + options B and C, drawn only)', fontsize=17, color='#fcfcfb', weight='bold')
ax.text(30, 80, 'Boxes see-through; the sheets lie in pockets in the floor under them.', fontsize=13, color='#e8e7e3')
plt.savefig('/home/claude/bal/out/ballast_3_rear34.png', dpi=100)
print('ok')
