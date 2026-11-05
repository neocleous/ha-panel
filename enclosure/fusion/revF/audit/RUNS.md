# Audit runs (loader parameters), 2026-11-05/06

Each Fusion run is a one-line loader that sets the parameters below and then `exec`s the named script from `~/Documents/audit/scripts/` (copies of this folder at the commit given in README.md). Listed in the order run; repeated identical loaders are listed once.

## 1. v5f_a0a_preflight
```python
# run as an inline copy of v5f_a0a_preflight.py (same code as the committed file)
```

## 2. v5f_a1a_validity
```python
SEL = ['HOUSING_F_cap', 'HOUSING_F_door', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'RESP_CARRIER', 'CRADLE_5807', 'GROMMET_usbc_F']
```

## 3. v5f_a1a_validity
```python
SEL = ['HOUSING_F_front']
```

## 4. v5f_a1b_meshes
```python
SEL = ['HOUSING_F_cap', 'HOUSING_F_door', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'RESP_CARRIER', 'CRADLE_5807', 'GROMMET_usbc_F']
TOL = 0.01
```

## 5. v5f_a1b_meshes
```python
SEL = ['HOUSING_F_front']
TOL = 0.01
```

## 6. v5f_a1c_holes
```python
# (no parameters)
```

## 7. v5f_a1d_sections
```python
SECS = [
 ['door_bottom_x7.7', 'HOUSING_F_door', (7.74, -86.0, 2.6), (0, 1, 0), (0, 0, 1), 60, 13, 0.2],
 ['front_rim_x7.7', 'HOUSING_F_front', (7.74, -86.0, 0.0), (0, 1, 0), (0, 0, 1), 60, 26, 0.2],
 ['door_pin_y-83', 'HOUSING_F_door', (11.0, -83.0, 19.0), (1, 0, 0), (0, 0, 1), 50, 33, 0.1],
 ['cap_lip_x0', 'HOUSING_F_cap', (0.0, -46.0, 172.4), (0, 1, 0), (0, 0, 1), 80, 46, 0.1],
 ['front_lipend_x0', 'HOUSING_F_front', (0.0, -66.0, 112.0), (0, 1, 0), (0, 0, 1), 70, 40, 0.4],
]
```

## 8. v5f_a1b_meshes
```python
SEL = ['REF_F_outer']
TOL = 0.01
SUBDIR = 'mesh_ref'
```

## 9. v5f_a2a_matrix
```python
MODE = 'list'
```

## 10. v5f_a2a_matrix
```python
MODE = 'run'
I0 = 0
I1 = 407
```

## 11. v5f_a2b_nearmiss
```python
I0 = 0
I1 = 100000
```

## 12. v5f_a2c_bbox
```python
TAG = 'all'
SEL = ['KO_*', 'PI5_F', 'PI5_F_cooler', 'GPIO_*', 'MAIN_*', 'LEAD_*', 'PD_5807_env', 'PIPWR_a_env', 'USBA_*', 'RESP_*', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'LD2410C_env_F', 'BME680_env', 'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'FOOT_*', 'LCD_*', 'SLAB_frame', 'HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'MAIN_BRACKET', 'RESP_CARRIER', 'CRADLE_5807', 'GROMMET_usbc_F', 'RENDER_*', 'REF_F_outer', 'INNER_E']
```

## 13. v5f_a3a_sweep
```python
LABEL = 'pi'
MOVE = ['PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env']
FIXED = ['HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'TOUCH_PCB', 'KO_touch_back', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env']
PATH = [(0, -85, 2.0), (0, 0, 2.0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 14. v5f_a3a_sweep
```python
LABEL = 'pi_nobracket'
MOVE = ['PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env']
FIXED = ['HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'KO_touch_back', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env']
PATH = [(0, -85, 2.0), (0, 0, 2.0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 15. v5f_a3a_sweep
```python
LABEL = 'bracket_after_pi'
MOVE = ['MAIN_BRACKET']
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'GPIO_plugA_env', 'GPIO_plugB_env']
PATH = [(0, -30, 2.0), (0, 0, 2.0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 16. v5f_a1d_sections
```python
SECS = [
 ['front_x50_bracket', 'HOUSING_F_front', (50.0, -66.0, 78.0), (0, 1, 0), (0, 0, 1), 18, 22, 0.5],
 ['front_y63_bracket', 'HOUSING_F_front', (36.0, -63.2, 78.0), (1, 0, 0), (0, 0, 1), 36, 22, 0.5],
]
```

## 17. v5f_a3a_sweep
```python
LABEL = 'bracketL_inboard'
MOVE = ['MAIN_BRACKET']
MOVE_CROP = {'MAIN_BRACKET': [30, 60, -70, -50, 0, 90]}
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'SPKBOX_L', 'SPK_L', 'TOUCH_PCB', 'GPIO_plugA_env', 'GPIO_plugB_env']
PATH = [(-1.5, -30, 0.5), (-1.5, 0, 0.5), (0, 0, 0.5), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 18. v5f_a3a_sweep
```python
LABEL = 'bracketR_inboard'
MOVE = ['MAIN_BRACKET']
MOVE_CROP = {'MAIN_BRACKET': [-60, -30, -70, -50, 0, 90]}
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'SPKBOX_R', 'SPK_R', 'TOUCH_PCB', 'GPIO_plugA_env', 'GPIO_plugB_env', 'PIPWR_a_env', 'LEAD_PI_POWER']
PATH = [(1.5, -30, 0.5), (1.5, 0, 0.5), (0, 0, 0.5), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 19. v5f_a3a_sweep
```python
LABEL = 'mainboard'
MOVE = ['MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env']
FIXED = ['HOUSING_F_front', 'MAIN_BRACKET', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'PIPWR_a_env', 'GPIO_plugA_env', 'GPIO_plugB_env']
PATH = [(0, -40, 0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 20. v5f_a3a_sweep
```python
LABEL = 'mainboard_pcb'
MOVE = ['MAIN_pcb', 'MAIN_back_env']
FIXED = ['HOUSING_F_front', 'MAIN_BRACKET', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'RESP_CARRIER', 'PIPWR_a_env', 'GPIO_plugA_env', 'GPIO_plugB_env']
PATH = [(0, -40, 0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 21. v5f_a3a_sweep
```python
LABEL = 'boxL'
MOVE = ['SPKBOX_L', 'SPK_L']
FIXED = ['HOUSING_F_front', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_DSI_conn_d9.3', 'LCD_pogo_header_d14.1', 'LCD_panelFPC_conn_d9.5', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'SPKBOX_R', 'SPK_R']
PATH = [(-42, -70, 6), (-42, -1, 6), (-1, -1, 6), (-1, -1, 0), (0, -1, 0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 22. v5f_a3a_sweep
```python
LABEL = 'boxR'
MOVE = ['SPKBOX_R', 'SPK_R']
FIXED = ['HOUSING_F_front', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_DSI_conn_d9.3', 'LCD_pogo_header_d14.1', 'LCD_panelFPC_conn_d9.5', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'SPKBOX_L', 'SPK_L']
PATH = [(42, -70, 6), (42, -1, 6), (1, -1, 6), (1, -1, 0), (0, -1, 0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 23. v5f_a3a_sweep
```python
LABEL = 'lcdmodule'
MOVE = ['SLAB_frame', 'LCD_glass', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_DSI_conn_d9.3', 'LCD_panelFPC_conn_d9.5', 'LCD_touchFPC_conn_d9.3', 'LCD_pogo_header_d14.1', 'LCD_2x2_header_d15.4', 'LCD_pins_d16.0', 'LCD_M2.5_standoff_d9.0', 'LCD_M2.5_standoff_d9.0 (1)', 'LCD_M2.5_standoff_d9.0 (2)', 'LCD_M2.5_standoff_d9.0 (3)', 'LCD_Pi_standoff_d15.2', 'LCD_Pi_standoff_d15.2 (1)', 'LCD_Pi_standoff_d15.2 (2)', 'LCD_Pi_standoff_d15.2 (3)', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env']
FIXED = ['HOUSING_F_front']
PATH = [(0, 44.01, 9.36), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 24. v5f_a3a_sweep
```python
LABEL = 'touch'
MOVE = ['TOUCH_PCB']
FIXED = ['HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_panelFPC_conn_d9.5', 'LCD_pogo_header_d14.1']
PATH = [(0, -3.0, 0.9), (0, 0, 0.9), (0, 0, 0)]
STEP = 0.25
K0 = 0
```

## 25. v5f_a1d_sections
```python
SECS = [
 ['touch_top_x46', 'HOUSING_F_front', (46.0, -1.0, 41.0), (0, 1, 0), (0, 0, 1), 14, 22, 0.5],
 ['touch_bot_x46', 'HOUSING_F_front', (46.0, -1.0, 3.5), (0, 1, 0), (0, 0, 1), 14, 10, 0.5],
 ['touch_top_x30', 'HOUSING_F_front', (30.0, -1.0, 41.0), (0, 1, 0), (0, 0, 1), 14, 22, 0.5],
]
```

## 26. v5f_a3a_sweep
```python
LABEL = 'ld2410c'
MOVE = ['LD2410C_env_F']
FIXED = ['HOUSING_F_front', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_touchFPC_conn_d9.3', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'SPKBOX_R', 'BME680_env']
PATH = [(8.572, -5.150, 0), (0, 0, 0)]
STEP = 0.25
K0 = 0
```

## 27. v5f_a3a_sweep
```python
LABEL = 'pipwr_adapter'
MOVE = ['PIPWR_a_env']
MOVE_CROP = {'PIPWR_a_env': [-40, 0, -75, -55, 0, 40]}
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'MAIN_front_env', 'SPKBOX_R', 'SPK_R']
PATH = [(0, -15, 0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 28. v5f_a3a_sweep
```python
LABEL = 'pipwr_plug'
MOVE = ['PIPWR_a_env']
MOVE_CROP = {'PIPWR_a_env': [15, 35, -75, -55, 0, 40]}
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'MAIN_front_env']
PATH = [(0, 0, -8), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 29. v5f_a3a_sweep
```python
LABEL = 'cradle'
MOVE = ['CRADLE_5807', 'PD_5807_env']
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'LEAD_PI_POWER', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'MAIN_front_env']
PATH = [(0, -30, 0.5), (0, 0, 0.5), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 30. v5f_a3a_sweep
```python
LABEL = 'cap'
MOVE = ['HOUSING_F_cap', 'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env']
FIXED = ['HOUSING_F_front', 'SLAB_frame', 'LCD_glass', 'LCD_panel_body', 'RESP_CARRIER', 'RESP_top_env', 'LCD_pcb_76x110']
PATH = [(0, 0, 4.0), (0, 0, 0)]
STEP = 0.25
K0 = 0
```

## 31. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 32. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 94
```

## 33. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 112
```

## 34. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 125
```

## 35. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 136
```

## 36. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 146
```

## 37. v5f_a3a_sweep
```python
LABEL = 'door'
MOVE = ['HOUSING_F_door', 'GROMMET_usbc_F']
FIXED = ['HOUSING_F_front', 'HOUSING_F_cap', 'CRADLE_5807', 'PD_5807_env', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_back_env', 'PI5_F', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_PIGTAIL_20V', 'SPKBOX_L', 'SPKBOX_R', 'BME680_env', 'LD2410C_env_F']
PATH = [(0, -80, 0), (0, 0, 0)]
STEP = 0.5
K0 = 155
```

## 38. v5f_a3b_tools
```python
LABEL = 'pi_screws_before_mainboard'
D = [(0.0, -0.0, 1.0), (0.0, -0.0872, 0.9962), (0.0, -0.1392, 0.9903), (0.0, -0.1736, 0.9848), (0.0, -0.2079, 0.9781), (0.0, -0.2588, 0.9659), (0.0, -0.309, 0.9511), (0.0, -0.342, 0.9397), (0.0, -0.4226, 0.9063)]
TOOLS = [['pi_FL', (18.35, -5.5, 11.9), D, 200, 2.5], ['pi_FR', (-39.65, -5.5, 11.9), D, 200, 2.5], ['pi_RL', (18.35, -54.5, 11.9), D, 200, 2.5], ['pi_RR', (-39.65, -54.5, 11.9), D, 200, 2.5]]
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'SLAB_frame', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_DSI_conn_d9.3', 'LCD_pogo_header_d14.1', 'LCD_panelFPC_conn_d9.5', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'SPKBOX_L', 'SPKBOX_R', 'TOUCH_PCB']
```

## 39. v5f_a3b_tools
```python
LABEL = 'pi_front_screws_pi_first'
D = [(0.0, 0.0, 1.0), (0.0, 0.0872, 0.9962), (0.0, 0.1736, 0.9848), (0.0, 0.2588, 0.9659), (0.0, 0.342, 0.9397), (0.0, 0.4226, 0.9063)]
TOOLS = [['pi_FL', (18.35, -5.5, 11.9), D, 200, 2.5], ['pi_FR', (-39.65, -5.5, 11.9), D, 200, 2.5]]
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'GPIO_plugA_env', 'GPIO_plugB_env']
REGION = [-55, 35, -40, 30, 10, 200]
```

## 40. v5f_a3b_tools
```python
LABEL = 'pi_rear_screws_with_mainboard'
D = [(0.0, -0.0, 1.0), (0.0, -0.0872, 0.9962), (0.0, -0.1736, 0.9848), (0.0, -0.2588, 0.9659), (0.0, -0.342, 0.9397), (0.0, -0.4226, 0.9063)]
TOOLS = [['pi_RL', (18.35, -54.5, 11.9), D, 200, 2.5], ['pi_RR', (-39.65, -54.5, 11.9), D, 200, 2.5]]
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'PIPWR_a_env']
REGION = [-55, 35, -95, -40, 10, 200]
```

## 41. v5f_a3b_tools
```python
LABEL = 'pi_rear_screws_no_mainboard'
D = [(0.0, -0.0, 1.0), (0.0, -0.1736, 0.9848), (0.0, -0.2588, 0.9659), (0.0, -0.342, 0.9397), (0.0, -0.4226, 0.9063)]
TOOLS = [['pi_RL', (18.35, -54.5, 11.9), D, 200, 2.5], ['pi_RR', (-39.65, -54.5, 11.9), D, 200, 2.5]]
FIXED = ['HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'SPKBOX_L', 'SPKBOX_R', 'USBA_plug_env', 'USBA_cable_env']
REGION = [-55, 35, -100, -40, 10, 220]
```

## 42. v5f_a3a_sweep
```python
LABEL = 'lcdmodule_after_pi'
MOVE = ['SLAB_frame', 'LCD_glass', 'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_DSI_conn_d9.3', 'LCD_panelFPC_conn_d9.5', 'LCD_touchFPC_conn_d9.3', 'LCD_pogo_header_d14.1', 'LCD_2x2_header_d15.4', 'LCD_pins_d16.0', 'LCD_M2.5_standoff_d9.0', 'LCD_M2.5_standoff_d9.0 (1)', 'LCD_M2.5_standoff_d9.0 (2)', 'LCD_M2.5_standoff_d9.0 (3)', 'LCD_Pi_standoff_d15.2', 'LCD_Pi_standoff_d15.2 (1)', 'LCD_Pi_standoff_d15.2 (2)', 'LCD_Pi_standoff_d15.2 (3)', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env']
FIXED = ['PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'KO_touch_back', 'PIPWR_a_env', 'GPIO_plugA_env', 'GPIO_plugB_env']
PATH = [(0, 44.01, 9.36), (0, 0, 0)]
STEP = 0.5
K0 = 0
```

## 43. v5f_a3b_tools
```python
LABEL = 'tabs_cradle_screws'
D = [(0.0, -0.0, 1.0), (0.0, -0.1736, 0.9848), (0.0, -0.2588, 0.9659), (0.0, -0.342, 0.9397), (0.0, -0.4226, 0.9063)]
TOOLS = [['tab_L', (49.5, -58.0, 15.0), D, 200, 3.0], ['tab_R', (-49.5, -58.0, 15.0), D, 200, 3.0], ['cradle_L', (6.5, -72.5, 19.0), D, 200, 3.0], ['cradle_R', (-1.5, -72.5, 19.0), D, 200, 3.0]]
FIXED = ['HOUSING_F_front', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'PI5_F', 'PI5_F_cooler', 'SPKBOX_L', 'SPKBOX_R', 'PIPWR_a_env', 'LEAD_PI_POWER', 'USBA_cable_env', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail']
REGION = [-60, 60, -100, -40, 12, 220]
```

## 44. v5f_a1d_sections
```python
SECS = [
 ['bracket_x49.5', 'MAIN_BRACKET', (49.5, -64.0, 7.5), (0, 1, 0), (0, 0, 1), 26, 26, 0.5],
 ['bracket_z13', 'MAIN_BRACKET', (43.0, -64.0, 13.0), (1, 0, 0), (0, 1, 0), 26, 26, 0.5],
]
```

## 45. v5f_a3a_sweep
```python
LABEL = 'touch_slide_down'
MOVE = ['TOUCH_PCB']
FIXED = ['HOUSING_F_front']
PATH = [(0, 0, 20.0), (0, 0, 0)]
STEP = 0.5
CROP = 3.0
K0 = 0
```

## 46. v5f_a1d_sections
```python
SECS = [
 ['touch_tab_x44', 'HOUSING_F_front', (44.0, -1.0, 40.0), (0, 1, 0), (0, 0, 1), 13, 23, 0.5],
 ['touch_lip_x44', 'HOUSING_F_front', (44.0, -1.0, 3.5), (0, 1, 0), (0, 0, 1), 13, 9, 0.5],
 ['touch_lip_x0', 'HOUSING_F_front', (0.0, -1.0, 3.5), (0, 1, 0), (0, 0, 1), 13, 9, 0.5],
]
```

## 47. v5f_a3a_sweep
```python
LABEL = 'usba_plug_after_pi'
MOVE = ['USBA_plug_env', 'USBA_cable_env']
FIXED = ['SPKBOX_L', 'SPK_L', 'MAIN_BRACKET', 'HOUSING_F_front', 'PI5_F', 'PI5_F_cooler', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env']
PATH = [(12.0, 0, 0), (0, 0, 0)]
STEP = 0.5
CROP = 2.0
K0 = 0
```

## 48. v5f_a1d_sections
```python
SECS = [
 ['touch_tabP_y2.1_z45.5', 'HOUSING_F_front', (40.0, 2.1, 45.5), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
 ['touch_tabP_y2.1_z44.0', 'HOUSING_F_front', (40.0, 2.1, 44.0), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
 ['touch_tabN_y2.1_z45.5', 'HOUSING_F_front', (-46.0, 2.1, 45.5), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
 ['touch_lipP_y2.35_z6.4', 'HOUSING_F_front', (40.0, 2.35, 6.4), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
 ['touch_lipN_y2.35_z6.4', 'HOUSING_F_front', (-46.0, 2.35, 6.4), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
 ['touch_ledgeP_y3.5_z5.5', 'HOUSING_F_front', (40.0, 3.5, 5.5), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
 ['touch_chanP_y3.5_z45.5', 'HOUSING_F_front', (40.0, 3.5, 45.5), (1, 0, 0), (0, 0, 1), 25, 1, 0.25],
]
```

## 49. v5f_a3b_tools
```python
LABEL = 'box_screws_installed_Lside'
D = [(0.0, -1.0, 0.0)]
TOOLS = [['boxL_low', (52.75, -8.7, 10.25), D, 130, 3.0], ['boxL_up', (52.75, -8.7, 45.75), D, 130, 3.0]]
FIXED = ['SPKBOX_L', 'SPK_L', 'HOUSING_F_front', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'LEAD_USB_RESP', 'LEAD_SPK_L', 'LEAD_SPK_R', 'PIPWR_a_env', 'LEAD_PI_POWER', 'CRADLE_5807', 'PD_5807_env', 'GPIO_plugA_env', 'GPIO_plugB_env']
REGION = [45, 61, -140, -2, 0, 60]
```

## 50. v5f_a3b_tools
```python
LABEL = 'box_screws_installed_Rside'
D = [(0.0, -1.0, 0.0)]
TOOLS = [['boxR_low', (-52.75, -8.7, 10.25), D, 130, 3.0], ['boxR_up', (-52.75, -8.7, 45.75), D, 130, 3.0]]
FIXED = ['SPKBOX_R', 'SPK_R', 'HOUSING_F_front', 'MAIN_BRACKET', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'PI5_F', 'PI5_F_cooler', 'USBA_plug_env', 'USBA_cable_env', 'LEAD_USB_RESP', 'LEAD_SPK_L', 'LEAD_SPK_R', 'PIPWR_a_env', 'LEAD_PI_POWER', 'CRADLE_5807', 'PD_5807_env', 'GPIO_plugA_env', 'GPIO_plugB_env', 'BME680_env', 'LEAD_BME']
REGION = [-61, -45, -140, -2, 0, 60]
```

## 51. v5f_a3b_tools
```python
LABEL = 'boxL_low_tilts_box_only'
D = [(0.0, -math.cos(math.radians(a)), math.sin(math.radians(a))) for a in (0, 3, 5, 7, 9, 11, 13, 15, 18, 21, 24)]
TOOLS = [['boxL_low', (52.75, -8.7, 10.25), D, 130, 3.0]]
FIXED = ['SPKBOX_L', 'SPK_L', 'HOUSING_F_front']
REGION = [40, 65, -140, -2, 0, 70]
```

## 52. v5f_a1d_sections
```python
SECS = [
 ['boxL_tube_low_x52.75', 'SPKBOX_L', (52.75, -55.0, 6.0), (0, 1, 0), (0, 0, 1), 51, 15, 1.0],
]
```

## 53. v5f_a3a_sweep
```python
LABEL = 'cap_strips_veml'
MOVE = ['MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env']
FIXED = ['HOUSING_F_cap']
PATH = [(0, 0, -10.0), (0, 0, 0)]
STEP = 0.5
CROP = 2.0
K0 = 0
```

## 54. v5f_a3a_sweep
```python
LABEL = 'feet'
MOVE = ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
FIXED = ['HOUSING_F_front', 'HOUSING_F_door']
PATH = [(0, 0, -6.0), (0, 0, 0)]
STEP = 0.5
CROP = 2.0
K0 = 0
```

## 55. v5f_a1d_sections
```python
SECS = [
 ['bracket_M25_boss_x41.5_z37.5_along_y', 'MAIN_BRACKET', (41.5, -64.5, 37.5), (0, 1, 0), (0, 0, 1), 41, 1, 0.25],
 ['bracket_M25_boss_x41.5_z37.5_off2', 'MAIN_BRACKET', (43.5, -64.5, 37.5), (0, 1, 0), (0, 0, 1), 41, 1, 0.25],
 ['cradle_M2_post_x-7.49_along_z', 'CRADLE_5807', (-7.49, -81.16, 13.0), (0, 0, 1), (1, 0, 0), 37, 1, 0.25],
 ['carrier_M2_boss_dummy', 'RESP_CARRIER', (-35.11, -16.93, 127.0), (0, 1, 0), (0, 0, 1), 1, 1, 0.25],
 ['door_bottom_edge_x0', 'HOUSING_F_door', (0.0, -84.0, 2.0), (0, 0, 1), (0, 1, 0), 9, 1, 0.25],
]
```

## 56. v5f_a1d_sections
```python
SECS = [
 ['grommet_x0_y-85.5_z', 'GROMMET_usbc_F', (0.0, -85.5, 12.0), (0, 0, 1), (1, 0, 0), 91, 1, 0.2],
 ['grommet_z23.7_y-85.5_x', 'GROMMET_usbc_F', (-13.0, -85.5, 23.7), (1, 0, 0), (0, 0, 1), 131, 1, 0.2],
 ['door_x0_y-84.0_z', 'HOUSING_F_door', (0.0, -84.0, 12.0), (0, 0, 1), (1, 0, 0), 91, 1, 0.2],
 ['cradle_x0_y-84.5_z', 'CRADLE_5807', (0.0, -84.5, 12.0), (0, 0, 1), (1, 0, 0), 91, 1, 0.2],
 ['grommet_x0_z26.0_y', 'GROMMET_usbc_F', (0.0, -86.5, 27.2), (0, 1, 0), (0, 0, 1), 41, 1, 0.2],
]
```

## 57. v5f_a1d_sections
```python
SECS = [
 ['front_floor_rim_x0_y-82_z', 'HOUSING_F_front', (0.0, -82.0, 1.5), (0, 0, 1), (1, 0, 0), 21, 1, 0.1],
 ['door_bottom_x0_y-83_z', 'HOUSING_F_door', (0.0, -83.0, 1.5), (0, 0, 1), (1, 0, 0), 31, 1, 0.1],
 ['front_side_y-40_z175.0_x', 'HOUSING_F_front', (84.0, -40.0, 175.0), (1, 0, 0), (0, 0, 1), 81, 1, 0.1],
 ['cap_side_y-40_z175.0_x', 'HOUSING_F_cap', (84.0, -40.0, 175.0), (1, 0, 0), (0, 0, 1), 81, 1, 0.1],
 ['front_side_y-40_z173.6_x', 'HOUSING_F_front', (84.0, -40.0, 173.6), (1, 0, 0), (0, 0, 1), 81, 1, 0.1],
 ['cap_side_y-40_z173.6_x', 'HOUSING_F_cap', (84.0, -40.0, 173.6), (1, 0, 0), (0, 0, 1), 81, 1, 0.1],
 ['front_shelf_x0_y-23.0_z', 'HOUSING_F_front', (0.0, -23.0, 176.6), (0, 0, 1), (1, 0, 0), 21, 1, 0.1],
 ['cap_front_x0_y-23.0_z', 'HOUSING_F_cap', (0.0, -23.0, 176.6), (0, 0, 1), (1, 0, 0), 21, 1, 0.1],
]
```

## 58. v5f_a1d_sections
```python
SECS = [
 ['front_side_y-40_z175.1_x', 'HOUSING_F_front', (66.0, -40.0, 175.1), (1, 0, 0), (0, 0, 1), 141, 1, 0.1],
 ['cap_side_y-40_z175.1_x', 'HOUSING_F_cap', (66.0, -40.0, 175.1), (1, 0, 0), (0, 0, 1), 141, 1, 0.1],
 ['front_side_y-40_z173.5_x', 'HOUSING_F_front', (66.0, -40.0, 173.5), (1, 0, 0), (0, 0, 1), 141, 1, 0.1],
 ['cap_side_y-40_z173.5_x', 'HOUSING_F_cap', (66.0, -40.0, 173.5), (1, 0, 0), (0, 0, 1), 141, 1, 0.1],
 ['front_side_y-40_z174.0_x', 'HOUSING_F_front', (66.0, -40.0, 174.0), (1, 0, 0), (0, 0, 1), 141, 1, 0.1],
]
```

## 59. v5f_a5b_mass
```python
# (no parameters)
```

## 60. v5f_a5a_box_air
```python
# (no parameters)
```

## 61. v5f_a5a_box_air
```python
PLUG_WIRE = False
BOXES = [['SPKBOX_L', 'SPK_L', 1]]
```

## 62. v5f_a2c_bbox
```python
SEL = ['*']
TAG = 'every'
```

## 63. v5f_a1d_sections
```python
SECS = [
 ['cap_mic_pocket_x20_y-26.5_z', 'HOUSING_F_cap', (20.0, -26.5, 174.5), (0, 0, 1), (1, 0, 0), 61, 1, 0.1],
 ['cap_mic_pocket_x35.5_y-26.5_z', 'HOUSING_F_cap', (35.5, -26.5, 174.5), (0, 0, 1), (1, 0, 0), 61, 1, 0.1],
 ['cap_veml_pocket_x3_y-33.7_z', 'HOUSING_F_cap', (3.0, -33.7, 171.5), (0, 0, 1), (1, 0, 0), 91, 1, 0.1],
 ['cap_mic_pocket_y_x20_z177', 'HOUSING_F_cap', (20.0, -31.0, 177.0), (0, 1, 0), (0, 0, 1), 91, 1, 0.1],
]
```

## 64. v5f_a1d_sections
```python
SECS = [
 ['bme_surround_inboard_x', 'HOUSING_F_front', (-64.0, -42.0, 91.0), (1, 0, 0), (0, 0, 1), 21, 1, 0.5],
 ['bme_surround_front_y', 'HOUSING_F_front', (-73.0, -32.0, 91.0), (0, 1, 0), (0, 0, 1), 21, 1, 0.5],
 ['bme_surround_below_z', 'HOUSING_F_front', (-73.0, -42.0, 73.0), (0, 0, 1), (1, 0, 0), 21, 1, 0.5],
 ['bme_surround_above_z', 'HOUSING_F_front', (-73.0, -42.0, 99.5), (0, 0, 1), (1, 0, 0), 21, 1, 0.5],
 ['ld_normal_line', 'HOUSING_F_front', (-72.5, -22.1, 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 61, 1, 0.1],
 ['exhaust_wall_x0_z164_y', 'HOUSING_F_front', (0.0, -90.0, 164.0), (0, 1, 0), (0, 0, 1), 71, 1, 0.5],
]
```

## 65. v5f_a1d_sections
```python
SECS = [
 ['ld_normal_line_40', 'HOUSING_F_front', (-72.5, -22.1, 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 161, 1, 0.25],
 ['ld_normal_line_40_rev', 'HOUSING_F_front', (-72.5, -22.1, 127.5), (0.857167, -0.515038, 0.0), (0, 0, 1), 41, 1, 0.25],
 ['ld_env_normal_line', 'LD2410C_env_F', (-72.5, -22.1, 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 41, 1, 0.25],
 ['ld_env_normal_line_rev', 'LD2410C_env_F', (-72.5, -22.1, 127.5), (0.857167, -0.515038, 0.0), (0, 0, 1), 41, 1, 0.25],
]
```

## 66. v5f_a1d_sections
```python
SECS = [
 ['ld_line_minus_x', 'HOUSING_F_front', (-72.5, -22.1, 127.5), (-1, 0, 0), (0, 0, 1), 121, 1, 0.25],
 ['ld_line_plus_y', 'HOUSING_F_front', (-72.5, -22.1, 127.5), (0, 1, 0), (0, 0, 1), 161, 1, 0.25],
 ['ld_line_n_slab', 'SLAB_frame', (-72.5, -22.1, 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 161, 1, 0.25],
 ['ld_line_n_lcd', 'LCD_panel_body', (-72.5, -22.1, 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 161, 1, 0.25],
]
```

## 67. v5f_a1d_sections
```python
h = (0.515038, 0.857167, 0.0)
c = (-72.5, -22.1, 127.5)
SECS = [
 ['ld_n_from_c_plus5h', 'HOUSING_F_front', (c[0] + 5 * h[0], c[1] + 5 * h[1], 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 141, 1, 0.25],
 ['ld_n_from_c_minus5h', 'HOUSING_F_front', (c[0] - 5 * h[0], c[1] - 5 * h[1], 127.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 141, 1, 0.25],
 ['ld_n_from_c_up8', 'HOUSING_F_front', (c[0], c[1], 135.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 141, 1, 0.25],
 ['ld_n_from_c_down8', 'HOUSING_F_front', (c[0], c[1], 119.5), (-0.857167, 0.515038, 0.0), (0, 0, 1), 141, 1, 0.25],
]
```

## 68. v5f_a1d_sections
```python
SECS = [
 ['exhaust_web_x0_z166.25_y', 'HOUSING_F_front', (0.0, -90.0, 166.25), (0, 1, 0), (0, 0, 1), 141, 1, 0.25],
 ['exhaust_rib_x25.9_z164_y', 'HOUSING_F_front', (25.91, -90.0, 164.0), (0, 1, 0), (0, 0, 1), 141, 1, 0.25],
]
```

## 69. v5f_a1d_sections
```python
SECS = [
 ['exhaust_web_x0_z166.25_y2', 'HOUSING_F_front', (0.0, -56.0, 166.25), (0, 1, 0), (0, 0, 1), 141, 1, 0.25],
]
```

## 70. v5f_a1d_sections
```python
SECS = [
 ['exhaust_z_x0_y-52.75', 'HOUSING_F_front', (0.0, -52.75, 160.0), (0, 0, 1), (1, 0, 0), 121, 1, 0.1],
 ['exhaust_row1_x_z164_y-52.75', 'HOUSING_F_front', (-50.0, -52.75, 164.0), (1, 0, 0), (0, 0, 1), 201, 1, 0.5],
 ['exhaust_row2_x_z168.5_y-52.75', 'HOUSING_F_front', (-50.0, -52.75, 168.5), (1, 0, 0), (0, 0, 1), 201, 1, 0.5],
]
```

## 71. v5f_a6a_doc
```python
# (no parameters)
```

## 72. v5f_a6c_log
```python
# (no parameters)
```

## 73. v5f_a6b_end
```python
REACTIVATE = 'HA Panel v5 - exploded view (rev F c2)'
```

