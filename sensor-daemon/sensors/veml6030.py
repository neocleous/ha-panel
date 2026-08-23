import adafruit_veml7700
import busio
import board

# The VEML6030's I2C address is strap-selectable: 0x48 (ADDR high — how the
# panel's breakout is wired) or 0x10 (ADDR low, the VEML7700-compatible
# default). The Adafruit VEML7700 driver defaults to 0x10, which fails
# against a 0x48-strapped board — try both, and say so in the journal
# instead of failing silently.
ADDRESSES = (0x48, 0x10)


class VEML6030:
    def __init__(self):
        self.sensor = None
        self._available = False
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
        except Exception as e:
            print(f"VEML6030: I2C bus init failed: {e}", flush=True)
            return
        for addr in ADDRESSES:
            try:
                self.sensor = adafruit_veml7700.VEML7700(i2c, address=addr)
                self._available = True
                print(f"VEML6030: initialised at 0x{addr:02x}", flush=True)
                return
            except Exception as e:
                print(f"VEML6030: init at 0x{addr:02x} failed: {e}", flush=True)
        print("VEML6030: not found — light sensor disabled", flush=True)

    def read(self):
        if not self._available:
            return None
        try:
            return round(self.sensor.lux, 1)
        except Exception:
            return None
