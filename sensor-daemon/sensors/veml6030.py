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
                break
            except Exception as e:
                print(f"VEML6030: init at 0x{addr:02x} failed: {e}", flush=True)
        if not self._available:
            print("VEML6030: not found — light sensor disabled", flush=True)
            return
        # The sensor sits shaded at the column base and typically reads
        # single-digit lux indoors. The driver default (gain 1/8, 100 ms) has
        # ~0.46 lx/count resolution — hopeless down there. Gain 2 + 200 ms
        # gives ~0.0144 lx/count, saturating around 940 lx, which the shaded
        # aperture will not reach (and clipping just means max brightness).
        try:
            self.sensor.light_gain = adafruit_veml7700.VEML7700.ALS_GAIN_2
            self.sensor.light_integration_time = adafruit_veml7700.VEML7700.ALS_200MS
        except Exception as e:
            print(f"VEML6030: gain config failed (using defaults): {e}", flush=True)

    def read(self):
        if not self._available:
            return None
        try:
            return round(self.sensor.lux, 1)
        except Exception:
            return None
