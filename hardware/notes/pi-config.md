# HA panel V2 — Raspberry Pi 5 configuration for the new hardware (block 3, part 3, 2026-11-09)

What the main board, the radar and the landscape LCD need from the Pi. The changes are written as a diff against
`system/install.sh` on `main` @ 62ea4d8 (2026-11-08). **Nothing here is applied to `main`:** the software session makes
the change and tests it.

## Settings
| # | Setting | Where | Why | Source |
|---|---|---|---|---|
| 1 | `PSU_MAX_CURRENT=5000` | Bootloader EEPROM (once per Pi) | The Pi takes 5 V from the main board's USB4085, with no USB PD. The CC pull-ups (10 kΩ Rp) only advertise 3 A. This setting makes the firmware skip PD negotiation and assume a 5 A supply. The Pi branch on the main board is fused at 10 A (0453010.MR) from the 55 W NID100-5. | Raspberry Pi white paper RP-009856-WP-1 "USB Power Delivery on Raspberry Pi 5" |
| 2 | `usb_max_current_enable=1` | `config.txt` | Allows 1.6 A on the USB ports instead of 600 mA. The white paper says it is set automatically once `PSU_MAX_CURRENT=5000`. It is kept so a reset EEPROM doesn't silently cap the ReSpeaker's USB port. | same |
| 3 | `dtoverlay=rpi-digiampplus,auto_mute_amp` | `config.txt` | TAS5756M at I²C1 0x4C, I²S with the Pi as clock producer, mute on GPIO22: the DigiAMP+ wiring (`gpio-leads.md`). `auto_mute_amp` unmutes when an ALSA device opens and mutes 5 s after it closes. R17 (100 kΩ) holds the amp muted until the driver takes GPIO22. | Raspberry Pi audio documentation (DigiAMP+ mute); overlay sources read 2026-11-07 (`gpio-leads.md`) |
| 4 | `dtparam=uart0=on` | `config.txt` | LD2410C on GPIO14/15 (J5 → plug A pins 8/10) at 256000 8N1, device **`/dev/ttyAMA0`**. On the Pi 5, `serial0` points to the debug header's UART (`/dev/ttyAMA10`), so the radar must use `/dev/ttyAMA0`. **Do not** add `dtparam=uart0_console`, which moves the console onto these pins. `enable_uart=1` concerns the debug UART on the Pi 5 and isn't needed. | Raspberry Pi documentation issue #3239; documentation PR #3294 (Pi 5 UARTs); pinout.xyz GPIO15 |
| 5 | `dtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch` | `config.txt` | **Unchanged.** Same panel, same DSI connector as V1 (default DSI1; `dsi0` only if the SC1132 cable goes to the other connector). | `install.sh` on `main` |
| 6 | Landscape | `cmdline.txt`, `startup.sh` | The V2 panel is landscape: the 8" DSI LCD's native 1280 × 800, so there is no rotation. Remove V1's portrait console rotation (`fbcon=rotate:3`) and the wlr-randr portrait transform in `startup.sh`. If the rev F mounting shows the image upside down, use 180: `fbcon=rotate:2`, `wlr-randr --transform 180`, and invert the touch in x and y (`dtoverlay -h vc4-kms-dsi-waveshare-panel` on the Pi lists the overlay's touch parameters). Check this at first boot. | Waveshare 8inch DSI LCD (C): 1280 × 800 hardware resolution |
| 7 | I²C1 on (`raspi-config nonint do_i2c 0`) | `install.sh` | **Unchanged.** One bus for the amp and every sensor: AT42QT1070 0x1B (touch rev D), VEML6030 0x48, TAS5756M 0x4C, BME680 0x77 (V1 addresses). Pull-ups are the Pi's 1.8 kΩ. | `gpio-leads.md`; runbook 2026-11-08 |
| 8 | `dtoverlay=disable-bt` | `config.txt` | **Unchanged.** Bluetooth isn't used. | `install.sh` on `main` |

## Diff against `system/install.sh` (main @ 62ea4d8), Step 3 "Boot configuration"
```diff
@@ Step 3: Boot configuration @@
 # I2C bus 1
 raspi-config nonint do_i2c 0
 info "I2C enabled"
 
+# Main-board amplifier (TAS5756M, DigiAMP+ wiring): I2S, I2C1 0x4C, mute on GPIO22
+if ! grep -q "^dtoverlay=rpi-digiampplus" "${CONFIG_TXT}" 2>/dev/null; then
+  echo "dtoverlay=rpi-digiampplus,auto_mute_amp" >> "${CONFIG_TXT}"
+  info "Amplifier overlay added"
+fi
+
+# LD2410C radar on UART0 (GPIO14/15) -> /dev/ttyAMA0. Pi 5: the console stays on the debug header.
+if ! grep -q "^dtparam=uart0=on" "${CONFIG_TXT}" 2>/dev/null; then
+  echo "dtparam=uart0=on" >> "${CONFIG_TXT}"
+  info "UART0 enabled for the radar"
+fi
+
+# Pi 5 is powered by the main board's 5 V (no USB PD): full USB current, and a 5 A supply in the EEPROM
+if ! grep -q "^usb_max_current_enable=1" "${CONFIG_TXT}" 2>/dev/null; then
+  echo "usb_max_current_enable=1" >> "${CONFIG_TXT}"
+fi
+if ! rpi-eeprom-config | grep -q "^PSU_MAX_CURRENT=5000"; then
+  rpi-eeprom-config > /tmp/ha-panel-boot.conf
+  sed -i '/^PSU_MAX_CURRENT=/d' /tmp/ha-panel-boot.conf
+  echo "PSU_MAX_CURRENT=5000" >> /tmp/ha-panel-boot.conf
+  rpi-eeprom-config --apply /tmp/ha-panel-boot.conf
+  info "EEPROM: PSU_MAX_CURRENT=5000 (written at the next reboot)"
+fi
+
 # Disable Bluetooth (not used, saves power)
 if ! grep -q "dtoverlay=disable-bt" "${CONFIG_TXT}" 2>/dev/null; then
   echo "dtoverlay=disable-bt" >> "${CONFIG_TXT}"
   info "Bluetooth disabled"
 fi
 
-# Console rotation to portrait — matches the panel's mounted orientation.
-# (Wayland rotation is handled separately by wlr-randr in startup.sh;
-#  fbcon=rotate:3 covers the text console before/without the compositor.)
-if ! grep -q "fbcon=rotate:" "${CMDLINE_TXT}" 2>/dev/null; then
-  sed -i 's/$/ fbcon=rotate:3/' "${CMDLINE_TXT}"
-  info "Console rotated to portrait (fbcon=rotate:3)"
-fi
+# V2 panel is landscape: the LCD's native 1280 x 800, no console rotation.
+# Remove a portrait rotation left by a V1 install. (startup.sh: drop the wlr-randr portrait transform.)
+sed -i 's/ fbcon=rotate:3//' "${CMDLINE_TXT}"
```
- The lines are appended like the existing ones, so they land in the last `config.txt` section, which is `[all]` in
  Pi OS. The same caveat already applies to the overlay and `disable-bt` lines.
- `rpi-eeprom-config --apply` writes the configuration into the latest EEPROM image and schedules the update for the
  next reboot. The installer's existing reboot at the end covers it. The interactive alternative is
  `sudo rpi-eeprom-config --edit`.
- Header comment "4. Configure: …": becomes "display overlay, I2C, amp overlay, UART0, USB current / EEPROM, Bluetooth
  off, TTY1 autologin".

## Checks after the first boot (bench and the software session)
```
rpi-eeprom-config | grep PSU_MAX_CURRENT          # PSU_MAX_CURRENT=5000
vcgencmd get_config usb_max_current_enable        # usb_max_current_enable=1
aplay -l                                          # the DigiAMP+ card (TAS5756M as pcm512x)
i2cdetect -y 1                                    # 1b, 48, UU at 4c (driver bound), 77
ls -l /dev/ttyAMA0 /dev/serial0                   # ttyAMA0 present; serial0 -> ttyAMA10
cat /boot/firmware/cmdline.txt                    # no fbcon=rotate:3
```
No low-power warning should appear on the desktop or in `dmesg`. The software session's own items are unchanged:
- the LD2410C in `sensor-daemon` on `/dev/ttyAMA0`;
- the at42qt1070 key map: rev D keeps KEY0…KEY3 left to right as rev C;
- the amp ceiling −4.0 dBFS;
- landscape layout of the dashboard.

## Sources (read 2026-11-09 unless noted)
- `system/install.sh` on `main` @ 62ea4d8 (2026-11-08), Step 3.
- Raspberry Pi white paper RP-009856-WP-1, "USB Power Delivery on Raspberry Pi 5":
  https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009856-WP-1-USB%20Power%20delivery%20on%20Raspberry%20Pi%205.pdf
  (PSU_MAX_CURRENT skips PD and assumes the given rating; `usb_max_current_enable=1` allows 1.6 A and is set
  automatically with PSU_MAX_CURRENT=5000).
- `rpi-eeprom-config --apply`: Raspberry Pi bootloader EEPROM documentation (copy at
  https://github.qingwei-s.workers.dev/dbussert/documentation/blob/master/hardware/raspberrypi/booteeprom.md).
- DigiAMP+ mute parameters: raspberrypi/documentation `accessories/audio/configuration.adoc`,
  https://github.com/raspberrypi/documentation/blob/4ef432ca21ffe4c0aa3da3276ad39665f7e6a95b/documentation/asciidoc/accessories/audio/configuration.adoc
  (`unmute_amp`, `auto_mute_amp`, GPIO22).
- Pi 5 UARTs:
  - https://github.com/raspberrypi/documentation/issues/3239 (`dtparam=uart0=on`, ttyAMA0);
  - https://github.com/raspberrypi/documentation/pull/3294 (Pi 5 primary UART on the debug header, four PL011s off
    by default);
  - https://pinout.xyz/pinout/pin10_gpio15 (GPIO14/15 carry a PL011 on the Pi 5; the console is on the debug
    header).
- LCD: Waveshare 8inch DSI LCD (C), https://waveshare.com/wiki/8inch_DSI_LCD_(C) (1280 × 800 hardware resolution).
- `hardware/main-board/gpio-leads.md` (overlay sources read 2026-11-07); `claude/runbook-panel-01-rebuild-2026-11-08.md`
  (V1 I²C addresses).
