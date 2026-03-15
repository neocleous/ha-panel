import adafruit_veml7700
import busio
import board

class VEML6030:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_veml7700.VEML7700(i2c)

    def read(self):
        try:
            return round(self.sensor.lux, 1)
        except Exception as e:
            return None
```

---

### File 5 — `sensor-daemon/sensors/__init__.py`

This file is required to make the sensors folder a Python module. It is intentionally empty — just create the file with no content and commit it.

Filename:
```
sensor-daemon/sensors/__init__.py
