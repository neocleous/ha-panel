import adafruit_vl53l0x
import busio
import board

class VL53L0X:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_vl53l0x.VL53L0X(i2c)

    def read(self):
        try:
            distance = self.sensor.range
            if distance >= 8190:
                return None
            return distance
        except Exception as e:
            return None
