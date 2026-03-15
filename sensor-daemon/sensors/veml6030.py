import adafruit_veml7700
import busio
import board
import digitalio

class VEML6030:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_veml7700.VEML7700(i2c)

    def read(self):
        try:
            return round(self.sensor.lux, 1)
        except Exception as e:
            return None
