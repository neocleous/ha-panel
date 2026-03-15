import smbus2
import time

AT42QT1070_ADDR = 0x1B
REG_DETECTION_STATUS = 0x02
REG_KEY_STATUS = 0x03

class AT42QT1070:
    def __init__(self, bus):
        self.bus = bus
        self._last_state = [False] * 4

    def read(self):
        try:
            detection = self.bus.read_byte_data(AT42QT1070_ADDR, REG_DETECTION_STATUS)
            key_status = self.bus.read_byte_data(AT42QT1070_ADDR, REG_KEY_STATUS)
            events = []
            for i in range(4):
                pressed = bool(key_status & (1 << i))
                if pressed != self._last_state[i]:
                    self._last_state[i] = pressed
                    events.append({
                        "button": i,
                        "state": "pressed" if pressed else "released"
                    })
            return events
        except Exception as e:
            return []
