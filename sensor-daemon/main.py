import time
import threading
import smbus2
import paho.mqtt.client as mqtt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    PANEL_ID, MQTT_BROKER, MQTT_PORT, MQTT_USERNAME, MQTT_PASSWORD,
    MQTT_TOPIC_ROOT, I2C_BUS, POLL_INTERVAL_TOUCH, POLL_INTERVAL_PROXIMITY,
    POLL_INTERVAL_LIGHT, POLL_INTERVAL_ENV, PROXIMITY_WAKE_THRESHOLD_MM,
    SCREEN_TIMEOUT
)
from sensors.at42qt1070 import AT42QT1070
from sensors.bme680 import BME680
from sensors.vl53l0x import VL53L0X
from sensors.veml6030 import VEML6030
from backlight import set_backlight

screen_on = True
last_proximity_trigger = time.time()
mqtt_client = mqtt.Client(client_id=PANEL_ID)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(f"{MQTT_TOPIC_ROOT}/backlight/set")
    else:
        print(f"MQTT connection failed: {rc}")

def on_message(client, userdata, msg):
    global screen_on
    payload = msg.payload.decode().strip().lower()
    if msg.topic == f"{MQTT_TOPIC_ROOT}/backlight/set":
        if payload == "on":
            set_backlight(True)
            screen_on = True
        elif payload == "off":
            set_backlight(False)
            screen_on = False

def publish(topic, payload):
    mqtt_client.publish(f"{MQTT_TOPIC_ROOT}/{topic}", payload, retain=True)

def touch_loop(sensor):
    while True:
        events = sensor.read()
        for event in events:
            publish(
                f"touch/button{event['button']}",
                event['state']
            )
        time.sleep(POLL_INTERVAL_TOUCH)

def proximity_loop(sensor):
    global screen_on, last_proximity_trigger
    while True:
        distance = sensor.read()
        if distance is not None:
            publish("sensor/proximity", distance)
            if distance <= PROXIMITY_WAKE_THRESHOLD_MM:
                last_proximity_trigger = time.time()
                if not screen_on:
                    set_backlight(True)
                    screen_on = True
        if screen_on:
            if time.time() - last_proximity_trigger > SCREEN_TIMEOUT:
                set_backlight(False)
                screen_on = False
        time.sleep(POLL_INTERVAL_PROXIMITY)

def environment_loop(sensor):
    while True:
        data = sensor.read()
        if data:
            publish("sensor/temperature", data["temperature"])
            publish("sensor/humidity", data["humidity"])
            publish("sensor/pressure", data["pressure"])
            publish("sensor/voc", data["voc"])
        time.sleep(POLL_INTERVAL_ENV)

def light_loop(sensor):
    while True:
        lux = sensor.read()
        if lux is not None:
            publish("sensor/light", lux)
        time.sleep(POLL_INTERVAL_LIGHT)

def main():
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    bus = smbus2.SMBus(I2C_BUS)
    touch = AT42QT1070(bus)
    proximity = VL53L0X()
    environment = BME680()
    light = VEML6030()

    threads = [
        threading.Thread(target=touch_loop, args=(touch,), daemon=True),
        threading.Thread(target=proximity_loop, args=(proximity,), daemon=True),
        threading.Thread(target=environment_loop, args=(environment,), daemon=True),
        threading.Thread(target=light_loop, args=(light,), daemon=True),
    ]

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        bus.close()

if __name__ == "__main__":
    main()
