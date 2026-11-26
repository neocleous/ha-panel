# Block 1a: the list of screw holes read by m10 'stack', taken from m10_holes_a.txt and m10_holes_b.txt (version 85):
# (label, part, mouth, far end, far end closed?, needle offset). Offsets: M3 button head 5.7 across over a clearance hole of
# 3.4 to 3.6 or a counterbore of 6.5: 2.3; the Pi's M2.5 (head 4.5 across, the Pi's hole 2.7): 1.8.
M3 = 2.3; M25 = 1.8
H = {
 'drv_L1': ('SPKBOX_L', (52.75, -4.0, 10.25), (52.75, -10.7, 10.25), True, M3),
 'drv_L2': ('SPKBOX_L', (52.75, -4.0, 45.75), (52.75, -10.7, 45.75), True, M3),
 'drv_L3': ('SPKBOX_L', (88.25, -4.0, 10.25), (88.25, -10.7, 10.25), True, M3),
 'drv_L4': ('SPKBOX_L', (88.25, -4.0, 45.75), (88.25, -10.7, 45.75), True, M3),
 'drv_R1': ('SPKBOX_R', (-52.75, -4.0, 10.25), (-52.75, -10.7, 10.25), True, M3),
 'drv_R2': ('SPKBOX_R', (-52.75, -4.0, 45.75), (-52.75, -10.7, 45.75), True, M3),
 'drv_R3': ('SPKBOX_R', (-88.25, -4.0, 10.25), (-88.25, -10.7, 10.25), True, M3),
 'drv_R4': ('SPKBOX_R', (-88.25, -4.0, 45.75), (-88.25, -10.7, 45.75), True, M3),
 'flo_L1': ('SPKBOX_L', (51.0, -14.0, 3.8), (51.0, -14.0, 10.2), True, M3),
 'flo_L2': ('SPKBOX_L', (64.0, -45.0, 3.8), (64.0, -45.0, 10.2), True, M3),
 'flo_R1': ('SPKBOX_R', (-51.0, -14.0, 3.8), (-51.0, -14.0, 10.2), True, M3),
 'flo_R2': ('SPKBOX_R', (-72.0, -38.0, 3.8), (-72.0, -38.0, 10.2), True, M3),
 'car_1': ('RESP_CARRIER', (-34.5, -29.39, 131.48), (-34.5, -21.37, 133.18), True, M3),
 'car_2': ('RESP_CARRIER', (-28.5, -19.56, 85.27), (-28.5, -11.54, 86.97), True, M3),
 'car_3': ('RESP_CARRIER', (21.7, -30.01, 134.42), (21.7, -21.99, 136.12), True, M3),
 'car_4': ('RESP_CARRIER', (33.5, -19.56, 85.27), (33.5, -11.54, 86.97), True, M3),
 'cap_SL': ('HOUSING_F_cap', (43.36, -32.85, 172.6), (43.36, -32.85, 178.5), True, M3),
 'cap_BL': ('HOUSING_F_cap', (25.91, -37.8, 172.6), (25.91, -37.8, 178.5), True, M3),
 'cap_BR': ('HOUSING_F_cap', (-25.91, -37.8, 172.6), (-25.91, -37.8, 178.5), True, M3),
 'cap_SR': ('HOUSING_F_cap', (-43.36, -32.85, 172.6), (-43.36, -32.85, 178.5), True, M3),
 'door_1': ('HOUSING_F_door', (50.0, -67.0, 2.8), (50.0, -67.0, 10.0), True, M3),
 'door_2': ('HOUSING_F_door', (19.0, -74.5, 2.8), (19.0, -74.5, 10.0), True, M3),
 'door_3': ('HOUSING_F_door', (-19.0, -77.0, 2.8), (-19.0, -77.0, 10.0), True, M3),
 'door_4': ('HOUSING_F_door', (-50.0, -67.0, 2.8), (-50.0, -67.0, 10.0), True, M3),
 'cra_1': ('FLOOR_PLATE', (6.5, -72.5, 13.0), (6.5, -72.5, 6.3), True, M3),
 'cra_2': ('FLOOR_PLATE', (-1.5, -72.5, 13.0), (-1.5, -72.5, 6.3), True, M3),
 'sp_L1': ('HOUSING_F_front', (85.0, 5.7, 60.68), (85.0, -0.51, 59.36), True, M3),
 'sp_R1': ('HOUSING_F_front', (-85.0, 5.7, 60.68), (-85.0, -0.51, 59.36), True, M3),
 'sp_L2': ('HOUSING_F_front', (70.0, -18.13, 167.05), (70.0, -24.35, 165.73), True, M3),
 'sp_R2': ('HOUSING_F_front', (-70.0, -18.13, 167.05), (-70.0, -24.35, 165.73), True, M3),
 'tab_L': ('HOUSING_F_plate', (58.67, -0.06, 80.0), (59.52, 4.8, 80.0), False, M3),
 'tab_R': ('HOUSING_F_plate', (-58.67, -0.06, 80.0), (-59.52, 4.8, 80.0), False, M3),
 'clip_L': ('SPKBOX_L', (43.5, -9.45, 35.0), (49.25, -9.45, 35.0), True, M3),
 'clip_R': ('SPKBOX_R', (-43.5, -9.45, 41.0), (-49.25, -9.45, 41.0), True, M3),
 'hold_L': ('SPKBOX_L', (40.0, -7.35, 57.6), (45.35, -7.35, 57.6), True, M3),
 'pi_1': ('FLOOR_PLATE', (-39.65, -54.5, 8.0), (-39.65, -54.5, 1.5), True, M25),
 'pi_2': ('FLOOR_PLATE', (-39.65, -5.5, 8.0), (-39.65, -5.5, 1.5), True, M25),
 'pi_3': ('FLOOR_PLATE', (18.35, -54.5, 8.0), (18.35, -54.5, 1.5), True, M25),
 'pi_4': ('FLOOR_PLATE', (18.35, -5.5, 8.0), (18.35, -5.5, 1.5), True, M25),
}


def rows(names):
    return [(n,) + H[n] for n in names]
# END
