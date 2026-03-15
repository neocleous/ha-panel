import adafruit_vl53l0x
import busio
import board

class VL53L0X:
    def __init__(self):
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.sensor = adafruit_vl53l0x.VL53L0X(i2c)
            self._available = True
        except Exception as e:
            self._available = False
            self.sensor = None

    def read(self):
        if not self._available:
            return None
        try:
            distance = self.sensor.range
            if distance >= 8190:
                return None
            return distance
        except Exception as e:
            return None
