import time
import threading
import json
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
mqtt_client = mqtt.Client(client_id=PANEL_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)

DEVICE = {
    "identifiers": [PANEL_ID],
    "name": f"Panel {PANEL_ID.split('-')[1] if '-' in PANEL_ID else PANEL_ID}",
    "model": "HA Touch Panel",
    "manufacturer": "Custom"
}

DISCOVERY_ENTITIES = [
    {
        "component": "sensor",
        "object_id": f"{PANEL_ID}_temperature",
        "config": {
            "name": "Temperature",
            "state_topic": f"{MQTT_TOPIC_ROOT}/sensor/temperature",
            "unit_of_measurement": "°C",
            "device_class": "temperature",
            "state_class": "measurement",
            "unique_id": f"{PANEL_ID}_temperature",
            "device": DEVICE
        }
    },
    {
        "component": "sensor",
        "object_id": f"{PANEL_ID}_humidity",
        "config": {
            "name": "Humidity",
            "state_topic": f"{MQTT_TOPIC_ROOT}/sensor/humidity",
            "unit_of_measurement": "%",
            "device_class": "humidity",
            "state_class": "measurement",
            "unique_id": f"{PANEL_ID}_humidity",
            "device": DEVICE
        }
    },
    {
        "component": "sensor",
        "object_id": f"{PANEL_ID}_pressure",
        "config": {
            "name": "Pressure",
            "state_topic": f"{MQTT_TOPIC_ROOT}/sensor/pressure",
            "unit_of_measurement": "hPa",
            "device_class": "atmospheric_pressure",
            "state_class": "measurement",
            "unique_id": f"{PANEL_ID}_pressure",
            "device": DEVICE
        }
    },
    {
        "component": "sensor",
        "object_id": f"{PANEL_ID}_voc",
        "config": {
            "name": "VOC",
            "state_topic": f"{MQTT_TOPIC_ROOT}/sensor/voc",
            "unit_of_measurement": "Ω",
            "state_class": "measurement",
            "unique_id": f"{PANEL_ID}_voc",
            "device": DEVICE
        }
    },
    {
        "component": "sensor",
        "object_id": f"{PANEL_ID}_light",
        "config": {
            "name": "Light",
            "state_topic": f"{MQTT_TOPIC_ROOT}/sensor/light",
            "unit_of_measurement": "lx",
            "device_class": "illuminance",
            "state_class": "measurement",
            "unique_id": f"{PANEL_ID}_light",
            "device": DEVICE
        }
    },
    {
        "component": "sensor",
        "object_id": f"{PANEL_ID}_proximity",
        "config": {
            "name": "Proximity",
            "state_topic": f"{MQTT_TOPIC_ROOT}/sensor/proximity",
            "unit_of_measurement": "mm",
            "state_class": "measurement",
            "unique_id": f"{PANEL_ID}_proximity",
            "device": DEVICE
        }
    },
    {
        "component": "binary_sensor",
        "object_id": f"{PANEL_ID}_button0",
        "config": {
            "name": "Button 0",
            "state_topic": f"{MQTT_TOPIC_ROOT}/touch/button0",
            "payload_on": "pressed",
            "payload_off": "released",
            "unique_id": f"{PANEL_ID}_button0",
            "device": DEVICE
        }
    },
    {
        "component": "binary_sensor",
        "object_id": f"{PANEL_ID}_button1",
        "config": {
            "name": "Button 1",
            "state_topic": f"{MQTT_TOPIC_ROOT}/touch/button1",
            "payload_on": "pressed",
            "payload_off": "released",
            "unique_id": f"{PANEL_ID}_button1",
            "device": DEVICE
        }
    },
    {
        "component": "binary_sensor",
        "object_id": f"{PANEL_ID}_button2",
        "config": {
            "name": "Button 2",
            "state_topic": f"{MQTT_TOPIC_ROOT}/touch/button2",
            "payload_on": "pressed",
            "payload_off": "released",
            "unique_id": f"{PANEL_ID}_button2",
            "device": DEVICE
        }
    },
    {
        "component": "binary_sensor",
        "object_id": f"{PANEL_ID}_button3",
        "config": {
            "name": "Button 3",
            "state_topic": f"{MQTT_TOPIC_ROOT}/touch/button3",
            "payload_on": "pressed",
            "payload_off": "released",
            "unique_id": f"{PANEL_ID}_button3",
            "device": DEVICE
        }
    },
    {
        "component": "switch",
        "object_id": f"{PANEL_ID}_backlight",
        "config": {
            "name": "Backlight",
            "command_topic": f"{MQTT_TOPIC_ROOT}/backlight/set",
            "state_topic": f"{MQTT_TOPIC_ROOT}/backlight/state",
            "payload_on": "on",
            "payload_off": "off",
            "unique_id": f"{PANEL_ID}_backlight",
            "device": DEVICE
        }
    }
]

def publish_discovery():
    for entity in DISCOVERY_ENTITIES:
        topic = f"homeassistant/{entity['component']}/{PANEL_ID}/{entity['object_id']}/config"
        mqtt_client.publish(topic, json.dumps(entity['config']), retain=True)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        publish_discovery()
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
            mqtt_client.publish(f"{MQTT_TOPIC_ROOT}/backlight/state", "on", retain=True)
        elif payload == "off":
            set_backlight(False)
            screen_on = False
            mqtt_client.publish(f"{MQTT_TOPIC_ROOT}/backlight/state", "off", retain=True)

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
                    mqtt_client.publish(f"{MQTT_TOPIC_ROOT}/backlight/state", "on", retain=True)
        if screen_on:
            if time.time() - last_proximity_trigger > SCREEN_TIMEOUT:
                set_backlight(False)
                screen_on = False
                mqtt_client.publish(f"{MQTT_TOPIC_ROOT}/backlight/state", "off", retain=True)
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

    try:
        touch = AT42QT1070(bus)
    except Exception:
        touch = None

    try:
        proximity = VL53L0X()
    except Exception:
        proximity = None

    try:
        environment = BME680()
    except Exception:
        environment = None

    try:
        light = VEML6030()
    except Exception:
        light = None

    threads = []
    if touch is not None:
        threads.append(threading.Thread(target=touch_loop, args=(touch,), daemon=True))
    if proximity is not None:
        threads.append(threading.Thread(target=proximity_loop, args=(proximity,), daemon=True))
    if environment is not None:
        threads.append(threading.Thread(target=environment_loop, args=(environment,), daemon=True))
    if light is not None:
        threads.append(threading.Thread(target=light_loop, args=(light,), daemon=True))

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
