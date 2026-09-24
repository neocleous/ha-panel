# Panel Setup

Graphical tool that prepares the SD card for a new HA touch panel. Opens a
browser UI, pre-fills everything it can, tests your MQTT credentials against
the broker before writing anything, and writes `userconf.txt`, `firstrun.sh` and
the first-boot hook in `cmdline.txt` straight to a freshly flashed Pi OS Lite
boot partition. Flash, run this, insert, power on — about 10–15 minutes and two
reboots later the panel boots into your dashboard.

Single static binary per platform, no runtime dependencies. Your answers
(except passwords) are remembered between runs.

## Download

Grab the latest build from the [Releases page](../../../releases).

| Platform | File | First run |
|---|---|---|
| macOS (Apple Silicon + Intel) | `PanelSetup-mac.zip` | Unzip, double-click. macOS will block the unsigned app: click **Done**, then System Settings → Privacy & Security → **Open Anyway**. Once per machine. Terminal alternative: `xattr -cr "Panel Setup.app"` |
| Windows x64 | `PanelSetup-windows.exe` | Double-click. SmartScreen: **More info → Run anyway**. Once per file. |
| Linux | `PanelSetup-linux-*.tar.gz` | Extract, run `./PanelSetup-linux` |

The binaries are unsigned (this is a hobby project — no paid signing
certificates). The source is right here; build it yourself if you prefer:

```
cd tools/panel-setup && go build -o panel-setup .
```

## Usage

1. Flash Raspberry Pi OS Lite (64-bit) with Raspberry Pi Imager — **no** Imager customisation
2. Leave the SD card mounted, run Panel Setup
3. Fill the form (it scans your network for existing panels and pre-selects the next free number; the write button unlocks after the MQTT test passes and the card is detected)
4. Write, eject, insert into the panel, power on

## What the first boot does

The first boot runs in two parts, because the step that runs a script on a
fresh card (`systemd.run=` in `cmdline.txt`, the same mechanism Raspberry Pi
Imager uses) runs it early, before the network is up.

| Boot | What runs | Takes | Log on the boot partition |
|---|---|---|---|
| 1 | **Part 1** — `firstrun.sh`, no network: renames Pi OS's first user to yours, hostname, SSH, Wi-Fi connection + country, timezone/locale, turns on the DSI display (overlay + portrait console) for the next boot, writes `/opt/ha-panel/config` and `sensor-config.py` (mode 600), arms part 2, removes its `cmdline.txt` hook and deletes itself and `userconf.txt` | ~1 min, then reboots — the screen stays dark this boot | `firstrun.log` |
| 2 | **Part 2** — `panel-firstboot.service`, after the network is up: installs git, clones the repo, runs `system/install.sh --unattended`, disables itself | 5–15 min (progress on the panel's screen), then reboots | `firstboot.log` |
| 3 | The kiosk: TTY1 autologin → labwc → Chromium on your dashboard | — | — |

`firstrun.log` ends with `Part 1 done — rebooting` (or `WITH ERRORS`, listing
them). `firstboot.log` ends with `Installed — rebooting into the kiosk`.

If part 2 fails (no network, clone or install error) it says why in
`firstboot.log` and **stays armed**: fix the cause (e.g. the Ethernet cable) and
power-cycle — it runs again. The full installer output is in
`/var/log/ha-panel-install.log` on the panel.

Part 2 installs from `main` of the repository, so a new panel always gets the
current installer — the binary only carries the panel's own settings.

## Building releases

Pushing a tag matching `setup-v*` (e.g. `setup-v1.0.0`) triggers the GitHub
Actions workflow, which builds all platforms and attaches them to a Release.
The workflow can also be run manually from the Actions tab (artifacts only,
no Release).
