# ha-panel

Private repository for the Home Assistant touch panel software stack.

## Structure

- `sensor-daemon/` — I2C sensor polling service and MQTT publisher
- `provisioning-ui/` — Wi-Fi provisioning screens and backend
- `system/` — systemd service units and nightly update script

## Panels

| Panel | Hostname | Location |
|---|---|---|
| panel-01 | panel-01.local | — |

## Notes

- HA server: 192.168.1.145
- MQTT broker: 192.168.1.145:1883
- Display: Waveshare 8" DSI 1280×800 landscape
```

Commit the file.

---

Your repository structure now looks like this:
```
ha-panel/
├── README.md
├── sensor-daemon/
│   ├── requirements.txt
│   ├── config.py
│   └── sensors/
├── provisioning-ui/
└── system/
