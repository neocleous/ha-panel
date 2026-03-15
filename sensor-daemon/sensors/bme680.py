import adafruit_bme680
import busio
import board

class BME680:
    def __init__(self):
        i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)
        self.sensor.sea_level_pressure = 1013.25

    def read(self):
        try:
            return {
                "temperature": round(self.sensor.temperature, 1),
                "humidity": round(self.sensor.relative_humidity, 1),
                "pressure": round(self.sensor.pressure, 1),
                "voc": round(self.sensor.gas, 0)
            }
        except Exception as e:
            return None
