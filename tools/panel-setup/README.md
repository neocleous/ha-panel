# Panel Setup

Graphical tool that prepares the SD card for a new HA touch panel. Opens a
browser UI, pre-fills everything it can, tests your MQTT credentials against
the broker before writing anything, and writes `userconf.txt` + `firstrun.sh`
straight to a freshly flashed Pi OS Lite boot partition. Flash, run this,
insert, power on — about 10 minutes later the panel boots into your dashboard.

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

If first boot fails, reinsert the SD card into your computer and read
`firstrun.log` on the boot partition.

## Building releases

Pushing a tag matching `setup-v*` (e.g. `setup-v1.0.0`) triggers the GitHub
Actions workflow, which builds all platforms and attaches them to a Release.
The workflow can also be run manually from the Actions tab (artifacts only,
no Release).
