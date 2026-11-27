# Builds spec/full.json: every picture of the instructions page, in model
# coordinates (mm, world frame of version 91: x+ viewer's left, y+ toward the
# screen, the screen vertical; the unit's own up is UP).
import json, math
import numpy as np

S12, C12 = math.sin(math.radians(12)), math.cos(math.radians(12))
UP = np.array([0, S12, C12])
FWD = np.array([0, C12, -S12])
A = [226, 128, 24]; R = [214, 58, 58]; BL = [30, 96, 200]; DK = [70, 70, 76]; B2 = [190, 100, 20]

def v(a): return [round(float(x), 2) for x in a]
def add(p, o): return v(np.array(p) + np.array(o))
def up(d): return v(UP * d)
def fwd(d): return v(FWD * d)
def arrow(p0, d, length, r=1.8): return [v(p0), v(np.array(p0) + np.array(d) / np.linalg.norm(d) * length), BL, r]

UNIT = ["FLOOR_PLATE", "PI5_F", "PI5_F_cooler", "CRADLE_5807", "PD_5807_env"]
BOXES = ["SPKBOX_L", "SPKBOX_R", "SPK_L", "SPK_R", "DRV_screw_heads_env"]
SHELL = ["HOUSING_F_front", "HOUSING_F_plate"]
MODULE = ["SLAB_frame", "LCD_glass", "RESP_CARRIER", "RESP_pcb", "RESP_top_env", "MAIN_pcb", "MAIN_low",
          "MAIN_tall", "MAIN_conn", "MAIN_PS1"]
TOUCH = ["TOUCH_PCB", "TOUCH_CLIP_L", "TOUCH_CLIP_R"]
HOLD = ["RADAR_HOLDER", "LD2410C_env_F"]
CAP = ["HOUSING_F_cap", "MIC_CLAMP_L", "MIC_CLAMP_R"]
FI = [0.55, 0.75, 0.38]; FIR = [-0.55, 0.75, 0.38]; BI = [0.45, -0.8, 0.45]; BIR = [-0.45, -0.8, 0.45]
BACK = [0.05, -1, 0.2]; FRONT = [0.05, 1, 0.12]

def col(names, rgb=A, off=(0, 0, 0)):
    return [[n, rgb, list(off)] for n in names]

def lump(name, i, off=(0, 0, 0), rgb=R):
    return [name, rgb, list(off), i]

M2 = {0: [20.05, -21.81, -45.34], 4: [-37.66, -21.81, -16.42], 1: [-18.05, -28.28, 38.2], 3: [12.95, -28.28, 38.2],
      2: [-60.9, -58.6, -31.7], 5: [-10.04, -104.6, -103.8], 10: [5.2, -104.6, -103.8],
      7: [6.45, -105.1, -114.8], 8: [-11.55, -105.1, -114.8], 6: [19.95, -25.4, -108.1], 9: [37.95, -21.9, -91.5]}
DRV = {2: [85.7, -28.81, -129.9], 3: [50.2, -28.81, -129.9], 4: [50.2, -21.43, -95.17], 5: [85.7, -21.43, -95.17],
       0: [-90.8, -28.81, -129.9], 1: [-55.3, -28.81, -129.9], 6: [-55.3, -21.43, -95.17], 7: [-90.8, -21.43, -95.17]}
PI_POSTS = [[-42.2, -82.12, -124.19], [15.8, -82.12, -124.19], [-42.2, -34.19, -134.38], [15.8, -34.19, -134.38]]
CRADLE_POSTS = [[3.95, -98.7, -115.66], [-4.05, -98.7, -115.66]]
BOX_FLOOR_HOLES = [[48.45, -42.99, -134.91], [61.45, -73.31, -128.46], [-53.55, -42.99, -134.91], [-74.55, -66.46, -129.92]]
DOOR_HOLES = [[47.45, -94.93, -124.38], [16.45, -102.27, -122.82], [-21.55, -104.72, -122.3], [-52.55, -94.93, -124.38]]
SHELL_INS = [[67.45, -15.97, 27.0], [-72.55, -15.97, 27.0], [82.45, -15.07, -82.0], [-87.55, -15.07, -82.0]]
PLATE_LEAN = [[56.49, -10.9, -62.4], [-61.63, -10.9, -62.4]]
PLATE_HOLES = [[82.45, -8.0, -82.0], [-87.55, -8.0, -82.0], [67.45, -8.0, 27.0], [-72.55, -8.0, 27.0]]
DISP_HOLES = [[47.5, -8.0, 6.57], [-47.5, -8.0, 6.57], [47.5, -8.0, -61.43], [-47.5, -8.0, -61.43]]
CARRIER_POSTS = [[19.15, -27.1, -2.45], [-37.05, -27.1, -5.45], [30.95, -27.1, -52.7], [-31.05, -27.1, -52.7]]
CARRIER_DISP = [[39.0, -16.2, -2.93], [-19.0, -16.2, -2.93], [39.0, -16.2, -51.93], [-19.0, -16.2, -51.93]]
CAP_INS = [[40.81, -25.43, 38.38], [23.36, -30.27, 39.4], [-28.46, -30.27, 39.4], [-45.91, -25.43, 38.38]]
DOOR_BOSS = [[47.45, -93.94, -119.68], [16.45, -101.27, -118.13], [-21.55, -103.72, -117.61], [-52.55, -93.94, -119.68]]
TABS = [[56.72, -14.8, -61.58], [-61.84, -14.8, -61.58]]
HOOD_PILOT = [-62.86, -57.54, -32.04]
SHELL_MAG = [[-18.37, -53.97, 15.89], [-60.25, -66.74, -35.92], [-73.66, -82.2, -103.7], [36.67, -58.1, -0.74],
             [63.84, -74.62, -69.73], [68.56, -82.2, -103.7], [55.2, -66.75, -35.93], [13.26, -53.96, 15.9],
             [-68.94, -74.61, -69.73], [-41.81, -58.1, -0.75]]

def capmatrix(beta=20.0, yb=-26.0, s=-30.0, xb=-2.55):
    # the cap's pose on its way up: long axis along dup, depth along world x
    c0 = np.array([-0.255, -2.875, 3.990])
    b = math.radians(beta)
    dup = np.array([0, math.sin(b), math.cos(b)])
    e2 = np.array([1.0, 0, 0])
    e3 = np.cross(dup, e2)
    Rm = np.column_stack([dup, e2, e3])
    tgt = np.array([xb / 10, yb / 10, 3.6]) + dup * s / 10
    t = tgt - Rm @ c0
    M = np.eye(4); M[:3, :3] = Rm; M[:3, 3] = t
    return [round(float(x), 6) for x in M.flatten()], dup

shots = []
def shot(name, grey=(), color=(), arrows=(), marks=(), view=None, **kw):
    d = {"name": name, "grey": list(grey), "color": list(color), "arrows": list(arrows),
         "marks": [[l, v(p)] for l, p in marks], "view": view}
    d.update(kw); shots.append(d)

# 1 inserts in the loose parts
o70 = up(70)
shot("s01_a_inserts", color=col(["FLOOR_PLATE"]) + col(["SPKBOX_L", "SPKBOX_R"], A, o70),
     marks=[("P", p) for p in PI_POSTS] + [("C", p) for p in CRADLE_POSTS] +
     [("S", add(DRV[i], o70)) for i in (2, 3, 4, 5, 0, 1, 6, 7)],
     view={"dir": FIR, "pad": 1.05})
shot("s01_b_inserts", color=col(["HOUSING_F_door", "HOUSING_F_cap", "RESP_CARRIER"]),
     marks=[("D", p) for p in DOOR_BOSS] + [("K", p) for p in CAP_INS] + [("C", p) for p in CARRIER_POSTS],
     view={"dir": BI, "pad": 1.05})
# 2 inserts in the screen plate and the shell
o45 = [0, 45, 0]
shot("s02_inserts", color=col(["HOUSING_F_front"]) + col(["HOUSING_F_plate"], B2, o45),
     marks=[("S", p) for p in SHELL_INS] + [("P", add(p, o45)) for p in PLATE_LEAN], view={"dir": FI, "pad": 1.05})
# 3 pilots
shot("s03_a_pilots", color=col(["CRADLE_5807", "RADAR_HOLDER"]),
     marks=[("C", [5.2, -105.57, -106.32]), ("C", [-10.04, -105.57, -106.32]),
            ("H", [37.95, -20.47, -92.26]), ("H", [19.95, -24.05, -109.08])], view={"dir": BI, "pad": 1.1})
shot("s03_b_hood_pilot", grey=["HOUSING_F_front"], cut={"axis": "x", "at": -40.0, "keep": "<"},
     marks=[("P", HOOD_PILOT)], arrows=[arrow([-40, -48, -28], [-1, -0.4, -0.15], 20)],
     view={"dir": [1, -0.25, 0.25], "box": [[-101, -90, -70], [-40, -12, 10]], "pad": 1.0})
# 4 magnets
ob = [0, -50, 0]
shot("s04_magnets", grey=["HOUSING_F_front"], color=col(["HOUSING_F_door"], A, ob),
     marks=[("M", p) for p in SHELL_MAG], view={"dir": BI, "pad": 1.03})
# 5 cloth
shot("s05_a_cloth", color=col(["HOUSING_F_front"]),
     marks=[("L", [67.45, -12.8, 27.0]), ("L", [-72.55, -12.8, 27.0]), ("L", [82.45, -12.8, -82.0]),
            ("L", [-87.55, -12.8, -82.0]), ("S", [-101.5, -53.0, -30.0])], view={"dir": FIR, "pad": 1.05})
shot("s05_b_cloth_door", color=col(["HOUSING_F_door"]), marks=[("G", [-2.55, -111.5, -100.0])],
     view={"dir": BACK, "pad": 1.08})
# 6 grommet onto the door
og = [0, -25, 0]
shot("s06_grommet", grey=["HOUSING_F_door"], color=col(["GROMMET_usbc_F"], A, og) + [lump("SCREWS_M2x6_env", 7), lump("SCREWS_M2x6_env", 8)],
     arrows=[arrow([-2.55, -140, -100], [0, 1, 0], 20)],
     marks=[("1", M2[7]), ("2", M2[8])], view={"dir": [0.3, 0.9, 0.45], "pad": 1.1, "focus": ["GROMMET_usbc_F"]}, width=1800)
# 7 cap: strips, light sensor, clamps (cap upside down)
oc = up(-14); os_ = up(-26)
shot("s07_cap", grey=["HOUSING_F_cap"],
     color=col(["MIC_strip_L_env", "MIC_strip_R_env", "VEML_env"], B2, oc) + col(["MIC_CLAMP_L", "MIC_CLAMP_R"], A, oc) +
     [lump("SCREWS_M2x6_env", 1, os_), lump("SCREWS_M2x6_env", 3, os_)],
     marks=[("1", add(M2[1], os_)), ("2", add(M2[3], os_)), ("V", add([-2.5, -26.0, 38.0], oc))],
     view={"dir": [0.15, 0.35, -1.0], "up": [0, 1, 0], "pad": 1.05})
# 8 carrier onto the display
ob30 = [0, -30, 0]
shot("s08_carrier", grey=["SLAB_frame", "LCD_glass"], color=col(["RESP_CARRIER"], A, ob30),
     arrows=[arrow([-55, -40, -27], [0, 1, 0], 25)],
     marks=[(str(i + 1), add(p, ob30)) for i, p in enumerate(CARRIER_DISP)], view={"dir": BI, "pad": 1.05})
# 9 ReSpeaker onto the carrier
o25 = [0, -25, 0]; o40 = [0, -40, 0]
shot("s09_respeaker", grey=["SLAB_frame", "LCD_glass", "RESP_CARRIER"],
     color=col(["RESP_pcb", "RESP_top_env", "RESP_mic_env"], A, o25) + [lump("SCREWS_M2x6_env", 0, o40), lump("SCREWS_M2x6_env", 4, o40)],
     marks=[("1", add(M2[0], o40)), ("2", add(M2[4], o40))], view={"dir": BI, "pad": 1.05})
# 10 the display's leads
shot("s10_leads", grey=["SLAB_frame", "LCD_glass", "RESP_CARRIER", "RESP_pcb", "RESP_top_env"],
     color=col(["LEAD_LCD_5V"]) + col(["LEAD_DSI"], BL), view={"dir": BACK, "pad": 1.05})
# 11 main board onto the carrier
shot("s11_main_board", grey=["SLAB_frame", "LCD_glass", "RESP_CARRIER", "RESP_pcb", "RESP_top_env"],
     color=col(["MAIN_pcb", "MAIN_low", "MAIN_tall", "MAIN_conn", "MAIN_PS1"], A, ob30),
     arrows=[arrow([-55, -55, -27], [0, 1, 0], 22)],
     marks=[(str(i + 1), add(p, ob30)) for i, p in enumerate(CARRIER_POSTS)], view={"dir": BI, "pad": 1.05})
# 12 Pi onto the base plate; USB cable and adapter
o35 = up(35)
shot("s12_pi", grey=["FLOOR_PLATE"], color=col(["PI5_F", "PI5_F_cooler", "USBA_plug_env", "PIPWR_a_env"], A, o35),
     arrows=[arrow(add([-60, -60, -100], o35), -UP, 30)],
     marks=[(str(i + 1), p) for i, p in enumerate(PI_POSTS)], view={"dir": BI, "pad": 1.05})
# 13 cradle, then inlet board
o25u = up(25); o45u = up(45); o55u = up(58)
shot("s13_cradle_inlet", grey=["FLOOR_PLATE", "PI5_F", "PI5_F_cooler"],
     color=col(["CRADLE_5807"], A, o25u) + col(["PD_5807_env"], B2, o45u) + [lump("SCREWS_M2x6_env", 5, o55u), lump("SCREWS_M2x6_env", 10, o55u)],
     marks=[("C", p) for p in CRADLE_POSTS] + [("1", add(M2[5], o55u)), ("2", add(M2[10], o55u))],
     view={"dir": BI, "pad": 1.1, "box": [[-50, -115, -140], [50, -70, -40]]})
# 14 drivers into the boxes (as the sample)
od = [0, 45, 0]; osw = [0, 70, 0]
shot("s14_a_driver_in", grey=["SPKBOX_L"], color=col(["SPK_L"], A, od) + col(["FOAM_spk_L_env"], DK, od) +
     [lump("DRV_screw_heads_env", i, osw) for i in (2, 3, 4, 5)], arrows=[[[99, 42, -112], [99, 4, -112], BL, 1.8]],
     marks=[("1", add(DRV[5], osw)), ("2", add(DRV[4], osw)), ("3", add(DRV[2], osw)), ("4", add(DRV[3], osw))],
     view={"dir": FI, "pad": 1.08})
shot("s14_b_driver_screws", grey=["SPKBOX_L"], color=col(["SPK_L"]) + [lump("DRV_screw_heads_env", i) for i in (2, 3, 4, 5)],
     marks=[("1", DRV[5]), ("2", DRV[4]), ("3", DRV[2]), ("4", DRV[3]), ("F", [68.0, -20.0, -93.5])],
     view={"dir": [0.12, 1.0, 0.12], "pad": 1.12, "focus": ["SPKBOX_L"]})
# 15 boxes onto the base plate
o50u = up(55); o50f = fwd(50)
shot("s15_boxes", grey=UNIT, color=col(["SPKBOX_R", "SPK_R"], A, o50u) + col(["SPKBOX_L", "SPK_L"], A, o50f),
     arrows=[arrow(add([-72, -50, -40], o50u), -UP, 35), arrow(add([66, -50, -40], o50f), -FWD, 35)],
     marks=[(str(i + 1), p) for i, p in enumerate(BOX_FLOOR_HOLES)], view={"dir": FI, "pad": 1.04})
# 16 leads on the sensor boards; radar onto its holder
orad = [0, 20, 0]; osc = [0, -15, 0]
shot("s16_a_radar_holder", grey=["RADAR_HOLDER"], color=col(["LD2410C_env_F"], A, orad) + col(["LEAD_RADAR"], BL) +
     [lump("SCREWS_M2x6_env", 6, osc), lump("SCREWS_M2x6_env", 9, osc)],
     marks=[("1", add(M2[6], osc)), ("2", add(M2[9], osc))], view={"dir": BI, "pad": 1.1, "focus": ["RADAR_HOLDER"]})
shot("s16_b_touch", color=col(["TOUCH_PCB"]) + col(["LEAD_TOUCH"], BL), view={"dir": BACK, "pad": 1.05})
# 17 BME680, foam, hood
shot("s17_bme_hood", grey=["HOUSING_F_front"], cut={"axis": "x", "at": -40.0, "keep": "<"},
     color=col(["BME680_env"], B2) + col(["FOAM_bme_env", "FOAM_bme_top_env"], DK) + col(["BME_HOOD"]) + col(["LEAD_BME680"], BL) +
     [lump("SCREWS_M2x6_env", 2)], marks=[("1", M2[2])],
     view={"dir": [1, -0.3, 0.3], "box": [[-101, -80, -60], [-40, -20, 0]], "pad": 1.0})
# 18 screen plate onto the shell
o40f = [0, 40, 0]
shot("s18_screen_plate", grey=["HOUSING_F_front"], color=col(["HOUSING_F_plate"], A, o40f),
     arrows=[arrow([0, 75, -30], [0, -1, 0], 28)],
     marks=[(str(i + 1), add(p, o40f)) for i, p in enumerate(PLATE_HOLES)], view={"dir": FI, "pad": 1.05})
# 19 shell down (as the sample)
o19 = v(UP * 80 + np.array([0, 1.6, 0]))
def down(p0, l=55): return [v(p0), v(np.array(p0) - l * UP), BL, 2.2]
shot("s19_a_shell_down", grey=UNIT + BOXES, color=col(["HOUSING_F_front"], A, o19) + col(["HOUSING_F_plate"], B2, o19),
     arrows=[down([112, -40, 30]), down([-118, -40, 30])], marks=[("A", [66, -81, -112]), ("B", [-72, -81, -112])],
     view={"dir": [-0.55, -0.75, 0.45], "pad": 1.06})
shot("s19_b_boxes_backs", grey=UNIT + ["SPKBOX_L", "SPKBOX_R", "SPK_L", "SPK_R"], color=col(["HOUSING_F_front"]),
     cut={"axis": "z", "at": -72.0, "keep": "<"}, cutcolor=True, marks=[("A", [66, -81, -108]), ("B", [-72, -81, -108])],
     view={"dir": [0.1, -0.9, 1.0], "pad": 1.04, "box": [[-102, -112, -142], [98, -20, -72]]})
# 20 box tops to the screen plate
tabax = np.array([0.174, 0.963, -0.205])
shot("s20_box_tops", grey=UNIT + BOXES + SHELL,
     arrows=[[v(np.array(TABS[0]) - tabax * 30), v(np.array(TABS[0]) - tabax * 4), BL, 1.6],
             [v(np.array(TABS[1]) - np.array([-0.174, 0.963, -0.205]) * 30), v(np.array(TABS[1]) - np.array([-0.174, 0.963, -0.205]) * 4), BL, 1.6]],
     marks=[("1", TABS[0]), ("2", TABS[1])], view={"dir": [0.1, -1.0, 0.35], "pad": 1.03})
# 21 touch board and clips
CUTZ = {"axis": "z", "at": -60.0, "keep": "<"}
shot("s21_touch_clips", grey=UNIT + BOXES + ["HOUSING_F_front"], cut=CUTZ, color=col(TOUCH),
     marks=[("1", [-44.55, -30.5, -98.1]), ("2", [39.45, -31.8, -104.0])],
     view={"dir": BI, "pad": 1.03, "box": [[-102, -112, -142], [98, -10, -60]]})
# 22 the radar on its holder
shot("s22_holder", grey=UNIT + BOXES + TOUCH + ["HOUSING_F_front"], cut=CUTZ, color=col(HOLD),
     marks=[("1", [35.75, -25.0, -82.3])], view={"dir": [0.15, -0.55, 1.0], "pad": 1.03, "box": [[-60, -90, -142], [98, -10, -60]]})
# 23 the cap, before the display module
m23, dup = capmatrix(20.0, -26.0, -30.0)
shot("s23_a_cap_way_up", grey=UNIT + BOXES + TOUCH + HOLD + SHELL, cut={"axis": "x", "at": 20.0, "keep": "<"},
     color=[[n, A, [0, 0, 0], None, m23] for n in CAP],
     arrows=[[v(np.array([-2.55, -26, 36]) + dup * 20), v(np.array([-2.55, -26, 36]) + dup * 70), BL, 2.2]],
     view={"dir": [1, 0.05, 0.12], "pad": 1.03, "box": [[20, -112, -142], [20, 0, 130]]})
shot("s23_b_cap_seated", grey=SHELL, color=col(CAP), marks=[(str(i + 1), p) for i, p in enumerate(CAP_INS)],
     view={"dir": [0.25, -0.55, 0.8], "pad": 1.05, "box": [[-90, -60, 10], [85, -10, 50]]})
# 24 display module
o60 = [0, 60, 0]
shot("s24_display_module", grey=UNIT + BOXES + SHELL + CAP + TOUCH + HOLD, color=col(MODULE, A, o60),
     arrows=[arrow([0, 95, 50], [0, -1, 0], 30)], marks=[(str(i + 1), p) for i, p in enumerate(DISP_HOLES)],
     view={"dir": FI, "pad": 1.03})
# 25 the four housings at the Pi
o15 = up(15)
shot("s25_pi_housings", grey=["FLOOR_PLATE", "PI5_F", "PI5_F_cooler"], color=col(["GPIO_plugA_env", "GPIO_plugB_env"], A, o15),
     view={"dir": BI, "pad": 1.05, "box": [[-50, -90, -140], [45, -20, -80]]})
# 26 plugs on the main board
shot("s26_plugs", grey=["SLAB_frame", "LCD_glass", "RESP_CARRIER", "MAIN_pcb", "MAIN_low", "MAIN_tall", "MAIN_conn", "MAIN_PS1"],
     color=col(["MAIN_plug_env"]) + col(["LEAD_SPK_L", "LEAD_SPK_R", "LEAD_PIGTAIL_20V", "LEAD_RADAR", "LEAD_TOUCH",
                                          "LEAD_BME680", "LEAD_VEML", "LEAD_PI_POWER"], BL),
     view={"dir": BACK, "pad": 1.05, "box": [[-50, -70, -110], [50, -30, 10]]})
# 27 the USB cable's spare
shot("s27_usb_spare", grey=["FLOOR_PLATE", "SPKBOX_L", "PI5_F", "PI5_F_cooler"], color=col(["LEAD_USB_RESP"]) + col(["LEAD_SPK_L"], BL),
     view={"dir": [0.55, -0.8, 0.3], "pad": 1.08, "box": [[20, -112, -142], [100, -20, -15]]})
# 28 door and feet
odr = [0, -40, 0]; oft = up(-22)
shot("s28_door_feet", grey=UNIT + BOXES + SHELL, color=col(["HOUSING_F_door"], A, odr) + col(["FOOT_FL", "FOOT_FR", "FOOT_RL", "FOOT_RR"], DK, oft),
     arrows=[arrow([-2.55, -175, -60], [0, 1, 0], 30)], marks=[(str(i + 1), p) for i, p in enumerate(DOOR_HOLES)],
     view={"dir": [0.45, -0.8, -0.35], "pad": 1.03})
# after the print: the places
shot("ap_p1a_base_plate", color=col(["FLOOR_PLATE"]), marks=[("c", p) for p in BOX_FLOOR_HOLES + DOOR_HOLES],
     view={"dir": [0.3, 0.25, -1.0], "pad": 1.05})
shot("ap_p1b_boxes", color=col(["SPKBOX_L", "SPKBOX_R"]),
     marks=[("W", [59.45, -73.69, -100.17]), ("W", [-64.55, -73.69, -100.17]), ("B", [50.2, -79.9, -121.0]), ("U", [46.0, -79.9, -119.0])],
     view={"dir": [0.15, -1.0, 0.2], "pad": 1.06})
shot("ap_p2_carrier_cradle", color=col(["RESP_CARRIER", "CRADLE_5807", "BME_HOOD"]),
     marks=[("N", [20.05, -19.25, -45.34]), ("N", [-37.66, -19.25, -16.42]), ("R", [5.2, -105.57, -106.32]), ("R", [-10.04, -105.57, -106.32])],
     view={"dir": BI, "pad": 1.05})
shot("ap_p7_holder_clamps", color=col(["RADAR_HOLDER"]), marks=[("H", [37.95, -20.47, -92.26]), ("H", [19.95, -24.05, -109.08])],
     view={"dir": BI, "pad": 1.1})
shot("ap_p3b_screen_plate", color=col(["HOUSING_F_plate"]), marks=[("W", [94.0, -12.8, -27.0]), ("W", [-99.0, -12.8, -27.0])],
     view={"dir": [0.1, -1.0, 0.1], "pad": 1.05})
shot("ap_p3a_shell", color=col(["HOUSING_F_front"]), marks=[("G", [68.0, -13.0, -112.0]), ("G", [-72.0, -13.0, -112.0]), ("P", HOOD_PILOT)],
     view={"dir": FIR, "pad": 1.05})
shot("ap_p6_door", color=col(["HOUSING_F_door"]), marks=[("F", [-2.55, -100.0, -126.0])], view={"dir": [0.4, -0.8, -0.3], "pad": 1.05})
json.dump(shots, open("/mnt/user-data/outputs/spec/full.json", "w"), indent=0)
print(len(shots), "shots")
