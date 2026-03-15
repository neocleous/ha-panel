import os
from config import BACKLIGHT_PATH, BACKLIGHT_ON, BACKLIGHT_OFF

def set_backlight(state):
    try:
        value = BACKLIGHT_ON if state else BACKLIGHT_OFF
        with open(BACKLIGHT_PATH, 'w') as f:
            f.write(str(value))
    except Exception as e:
        pass

def set_brightness(level):
    try:
        level = max(0, min(255, int(level)))
        with open(BACKLIGHT_PATH, 'w') as f:
            f.write(str(level))
    except Exception as e:
        pass

def is_on():
    try:
        with open(BACKLIGHT_PATH, 'r') as f:
            return int(f.read().strip()) > 0
    except Exception as e:
        return True
