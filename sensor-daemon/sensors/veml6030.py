import adafruit_veml7700
import busio
import board

class VEML6030:
    def __init__(self):
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_veml7700.VEML7700(i2c)
            self._available = True
        except Exception as e:
            self._available = False
            self.sensor = None

    def read(self):
        if not self._available:
            return None
        try:
            return round(self.sensor.lux, 1)
        except Exception as e:
            return None
