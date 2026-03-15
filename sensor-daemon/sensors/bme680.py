import bme680
import smbus2

class BME680:
    def __init__(self):
        self.sensor = bme680.BME680(i2c_addr=0x76, i2c_device=smbus2.SMBus(1))
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)

    def read(self):
        try:
            if self.sensor.get_sensor_data():
                return {
                    "temperature": round(self.sensor.data.temperature, 1),
                    "humidity": round(self.sensor.data.humidity, 1),
                    "pressure": round(self.sensor.data.pressure, 1),
                    "voc": round(self.sensor.data.gas_resistance, 0)
                }
            return None
        except Exception as e:
            return None
