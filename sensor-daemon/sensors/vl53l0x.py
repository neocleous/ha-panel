import smbus2

VL53L0X_ADDR = 0x29
REG_IDENTIFICATION_MODEL_ID = 0xC0

class VL53L0X:
    def __init__(self, bus):
        self.bus = bus
        self._available = False
        try:
            model_id = self.bus.read_byte_data(VL53L0X_ADDR, REG_IDENTIFICATION_MODEL_ID)
            if model_id == 0xEE:
                self._available = True
        except Exception:
            self._available = False

    def read(self):
        if not self._available:
            return None
        try:
            import adafruit_vl53l0x
            import busio
            import board
            i2c = busio.I2C(board.SCL, board.SDA)
            sensor = adafruit_vl53l0x.VL53L0X(i2c)
            distance = sensor.range
            if distance >= 8190:
                return None
            return distance
        except Exception:
            return None
