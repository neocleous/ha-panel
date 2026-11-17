# change2/offline/make_pics.py - the three question pictures for block 1.
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from compose import *


def gap():
    t = load('gap_today_cut'); d = ImageDraw.Draw(t); f = F(30)
    label(d, (980, 380), 'bezel', fill=(255, 255, 255), bg=None, font=F(34, 'Medium'))
    label(d, (40, 120), 'glass', to=(230, 205), font=f)
    label(d, (30, 575), 'screen plate (black; drawn grey here)', fill=(255, 255, 255), bg=None, font=f)
    label(d, (800, 780), "plate's edge: 0.8 behind the bezel's back", to=(945, 650), font=f)
    label(d, (800, 860), 'then a 0.2 slit to the shell', to=(660, 672), font=f)
    label(d, (860, 960), 'shell wall (cloth outside)', to=(760, 860), font=f)
    a = load('gap_a_cut'); d = ImageDraw.Draw(a)
    label(d, (980, 380), 'bezel', fill=(255, 255, 255), bg=None, font=F(34, 'Medium'))
    label(d, (40, 120), 'glass', to=(230, 205), font=f)
    label(d, (30, 575), 'screen plate', fill=(255, 255, 255), bg=None, font=f)
    label(d, (700, 430), "border 3.0 thick: level with the bezel's back", to=(880, 632), font=f)
    label(d, (30, 960), 'full thickness (3.8) only inside the shell', to=(520, 664), font=f)
    label(d, (850, 790), 'shadow gap: 1.0 wide, about 1.6 deep', to=(745, 652), font=f, fill=RED)
    label(d, (860, 960), 'shell wall (cloth outside)', to=(760, 860), font=f)
    s1 = load('gap_today_side_close'); d = ImageDraw.Draw(s1)
    label(d, (60, 60), 'shell (cloth)', to=(300, 300), font=f)
    label(d, (560, 900), "plate's back, 0.8 proud of the bezel", to=(640, 560), font=f)
    label(d, (900, 60), 'bezel', fill=(255, 255, 255), bg=None, font=F(34, 'Medium'))
    s2 = load('gap_a_side_close'); d = ImageDraw.Draw(s2)
    label(d, (60, 60), 'shell (cloth)', to=(300, 300), font=f)
    label(d, (120, 760), 'shadow gap', to=(642, 560), font=f, fill=RED)
    label(d, (560, 900), "plate's border, level with the bezel", to=(690, 700), font=f)
    label(d, (900, 60), 'bezel', fill=(255, 255, 255), bg=None, font=F(34, 'Medium'))
    rows = [[load('gap_today_cut3d'), load('gap_a_cut3d')], [t, a], [s1, s2]]
    sheet(rows, ['Today (version 65)', 'a.  Border stepped down to the bezel (your words)'], 'q1_shadow_gap.png', (1000, 750),
          title='Question 1 - the shadow gap between screen and shell (left side, 20 below mid-screen)',
          row_titles=['Cut open and seen from above and behind', 'The same cut, straight from above', 'Whole, seen from the side at eye level (8 degrees behind square-on)'],
          foot=['The plate is drawn grey so that it can be told from the bezel; both are black. The shell is shown without its cloth (0.7, wrapped round the rounded edge).',
                'With the cloth on, the gap is 0.3 at its tightest and about 1 where the edge rounds away.',
                'Top and bottom edges do not change: there the bezel already stands 1.0 in front of the top band and the rail.',
                'Option b (not drawn: it looks the same from outside): the plate 3.0 thick everywhere with a flat back, and the step moved onto the shell.'])


def vents():
    # letters as put to Daniel (recommended first); the layouts' keys in cp2.VENTS are in brackets
    cap = {'today': 'Today: 12 slots 3.0 wide, off centre.  1,504 mm2.  Nearest slot to the sensor: 52',
           'b': 'a (recommended).  9 slots, taller, centred.  1,508 mm2 (100 %).  Nearest slot: 52, as today',
           'a': 'b.  The same 12 slots, centred.  1,546 mm2 (103 %).  Nearest slot: 43',
           'c': 'c.  9 slots 4.0 wide, centred.  1,553 mm2 (103 %).  Nearest slot: 48'}
    ims = {}
    for q, text in cap.items():
        im = load('vent_' + q); d = ImageDraw.Draw(im)
        d.rectangle((0, 1218, 1400, 1300), fill=(255, 255, 255)); d.text((24, 1238), text, fill=INK, font=F(29, 'Medium'))
        label(d, (20, 590), "BME680's slits", to=(170, 528), fill=RED, font=F(28))
        ims[q] = im
    sheet([[ims['today'], ims['b']], [ims['a'], ims['c']]], ['', ''], 'q2_door_vents.png', (1000, 929), head=10,
          title='Question 2 - the rear door\'s vents, seen from behind (door bare, before its cloth)',
          foot=['Red: the BME680\'s two slits in the back wall. Distances are straight lines from the nearest slot edge to the slits, in mm.',
                'All three keep at least today\'s open area. Only a keeps today\'s distance from the sensor as well.'])


def posts():
    def tag(name, text):
        im = load(name); d = ImageDraw.Draw(im); label(d, (30, 30), text, font=F(34, 'Medium')); return im
    f = F(40)
    t = load('fin_today_front'); d = ImageDraw.Draw(t)
    label(d, (40, 40), 'top left corner, seen from the screen side and below', font=F(46, 'Medium'))
    label(d, (60, 880), 'top post: a plain column, joined along one flank', to=(330, 400), font=f)
    label(d, (400, 250), "triangular fin: hangs from the cap's seat by a neck 3.5 x 1.6", to=(850, 420), font=f)
    label(d, (700, 1060), "gussets under the cap's seat, 2.0 thick", to=(860, 760), font=f)
    n = load('fin_new_front'); d = ImageDraw.Draw(n)
    label(d, (40, 40), 'proposed', font=F(46, 'Medium'))
    label(d, (60, 880), 'cone into the wall, two gussets 2.6 thick', to=(300, 560), font=f)
    label(d, (700, 250), 'fin removed (question 3)', to=(850, 480), font=f, fill=RED)
    label(d, (700, 1060), 'gussets 2.6 thick (not drawn)', to=(860, 760), font=f)
    rows = [[tag('skin_today', 'outside, top left corner: the lump'), tag('skin_new', 'outside: smooth')],
            [t, n],
            [tag('post_bot_back_today', 'bottom post, seen from inside'), tag('post_bot_back_new', 'cone, buttress to the wall, strut onto the chin')]]
    sheet(rows, ['Today (version 65)', 'Proposed'], 'q0_posts.png', (1000, 750),
          title='Question 3 - the posts and the fin beside them (left side shown; the right is its mirror)',
          foot=['Nothing of this shows once the unit is built, except that the two lumps on the outside go.',
                'The fin tied the cap\'s side pad to the wall behind the screen. That wall became the screen plate, so the fin\'s front edge is free now.'])


if __name__ == '__main__':
    gap(); vents(); posts(); print('done')


def built():                                          # the review's fixes as built (version 66), four renders from the scratch document
    def tag(name, text, size):
        im = load(name).resize(size, Image.LANCZOS); d = ImageDraw.Draw(im); label(d, (24, 24), text, font=F(30, 'Medium')); return im
    rows = [[tag('g21_door_bosses', 'door from inside: each boss runs into the wall', (1000, 714)),
             tag('g21_carrier', 'carrier from behind: the four posts are cones', (1000, 714))],
            [tag('g21_cradle_posts', 'base plate: the two posts under the USB-C board', (1000, 714)),
             tag('g21_clip_block', 'left box and touch clip: screw hole 0.85 back', (1000, 714))]]
    sheet(rows, ['', ''], 'g21_fixes_as_built.png', (1000, 714), head=10, title='Version 66 - four of the strength fixes as built (all inside the unit)')


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'built':
    built(); print('built')
