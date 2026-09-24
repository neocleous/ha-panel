package main

// Host-side tests of everything the tool itself does: the arithmetic, the
// form's validation, the files it writes (rendered, parsed by bash, checked by
// shellcheck when installed), the cmdline.txt hook, and the handlers the page
// calls. What a host test cannot show — that Pi OS runs part 1 under
// systemd.run=, then part 2, then the kiosk — is covered by booting the real
// Pi OS Lite image (see the PR) and by one real card before a setup-v* tag.

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"
	"testing"
	"time"
)

func goodForm() formData {
	return formData{
		"panel_num": "2", "hostname": "panel-02", "username": "panel", "pi_pass": "a panel pass",
		"ha_base": "http://homeassistant.local:8123", "ha_url": "http://homeassistant.local:8123/panel-02/0",
		"mqtt_host": "192.168.1.145", "mqtt_port": "1883", "mqtt_user": "mqtt-panels", "mqtt_pass": `it's "quoted" \ $HOME`,
		"wifi_ssid": "Home Net", "wifi_pass": "wifi pass 123", "wifi_country": "CH",
		"timezone": "Europe/Zurich", "locale": "en_GB.UTF-8", "repo_url": "https://github.com/neocleous/ha-panel.git",
	}
}

func render(t *testing.T, f formData) map[string]string {
	t.Helper()
	files, err := buildFiles(f, time.Date(2026, 9, 24, 12, 0, 0, 0, time.UTC))
	if err != nil {
		t.Fatal(err)
	}
	return files
}

// part2 is firstboot.sh as part 1 writes it: the text between its heredoc markers.
func part2(t *testing.T, firstrun string) string {
	t.Helper()
	m := regexp.MustCompile(`(?s)<< 'FIRSTBOOT'\n(.*?\n)FIRSTBOOT\n`).FindStringSubmatch(firstrun)
	if m == nil {
		t.Fatal("firstrun.sh does not write firstboot.sh")
	}
	return m[1]
}

func TestSha512CryptVector(t *testing.T) {
	// Drepper's SHA-crypt specification, "Hello world!" / saltstring
	want := "$6$saltstring$svn8UoSVapNtMuq1ukKS4tPQd8iKwSMHWjl/O817G3uBnIFNjnQJuesI68u4OTLiBFdcbYEdFCoEOfaS35inz1"
	if got := sha512Crypt("Hello world!", "saltstring"); got != want {
		t.Errorf("sha512Crypt = %s", got)
	}
}

func TestWpaPSKVectors(t *testing.T) {
	// IEEE 802.11i-2004 H.4.3
	for _, c := range []struct{ pass, ssid, want string }{
		{"password", "IEEE", "f42c6fc52df0ebef9ebb4b90b38a5f902e83fe1b135a70e23aed762e9710a12e"},
		{"ThisIsAPassword", "ThisIsASSID", "0dc0d6eb90555ed6419756b9a15ec3e3209b63df707dd508d14581f8982721af"},
	} {
		if got := wpaPSK(c.pass, c.ssid); got != c.want {
			t.Errorf("wpaPSK(%q, %q) = %s", c.pass, c.ssid, got)
		}
	}
}

func TestNmSSID(t *testing.T) {
	if got := nmSSID("Home Net"); got != "Home Net" {
		t.Errorf("plain SSID: %q", got)
	}
	if got := nmSSID("café;x"); got != "99;97;102;195;169;59;120;" {
		t.Errorf("SSID with ; and UTF-8 goes as bytes: %q", got)
	}
}

func TestValidateRefusesWhatWouldBreakTheCard(t *testing.T) {
	if err := validate(goodForm()); err != nil {
		t.Fatalf("good form refused: %v", err)
	}
	for field, bad := range map[string]string{
		"username": "Panel", "hostname": "panel_02", "pi_pass": "", "mqtt_port": "1883; rm -rf /",
		"mqtt_pass": "two\nlines", "wifi_pass": "short", "wifi_country": "ch", "timezone": "Zurich",
		"locale": "en_GB", "repo_url": "https://x/y.git'; reboot; '", "ha_url": "http://x/ y",
	} {
		f := goodForm()
		f[field] = bad
		if validate(f) == nil {
			t.Errorf("%s=%q accepted", field, bad)
		}
	}
	f := goodForm()
	f["username"] = "root"
	if validate(f) == nil {
		t.Error("username root accepted")
	}
	f = goodForm()
	f["wifi_ssid"], f["wifi_pass"] = "", "" // Ethernet
	if err := validate(f); err != nil {
		t.Errorf("Ethernet-only refused: %v", err)
	}
}

func TestTheHookIsAppendedOnceAndPart1RemovesExactlyIt(t *testing.T) {
	stock := "console=serial0,115200 console=tty1 root=PARTUUID=4d8fd085-02 rootfstype=ext4 fsck.repair=yes rootwait resize\n"
	once := withHook(stock)
	if strings.Count(once, "\n") != 1 || once != strings.TrimSpace(stock)+" "+hookArgs+"\n" {
		t.Fatalf("hooked: %q", once)
	}
	if twice := withHook(once); twice != once {
		t.Fatalf("second write doubled the hook: %q", twice)
	}
	if withHook("a b\r\n") != "a b "+hookArgs+"\n" {
		t.Error("CRLF not normalised")
	}
	// part 1's own sed, run on the hooked line plus what raspi-config appends after it
	fr := render(t, goodForm())["firstrun.sh"]
	sedExpr := regexp.MustCompile(`sed -i -E '([^']+)' "\$FW/cmdline.txt"`).FindStringSubmatch(fr)
	if sedExpr == nil {
		t.Fatal("part 1 does not remove the hook")
	}
	cmd := exec.Command("sed", "-E", sedExpr[1])
	cmd.Stdin = strings.NewReader(strings.TrimSpace(once) + " cfg80211.ieee80211_regdom=CH\n")
	out, err := cmd.Output()
	if err != nil {
		t.Fatal(err)
	}
	if string(out) != strings.TrimSpace(stock)+" cfg80211.ieee80211_regdom=CH\n" {
		t.Errorf("after part 1: %q", out)
	}
}

func TestTheFilesAreComplete(t *testing.T) {
	f := goodForm()
	files := render(t, f)
	if !regexp.MustCompile(`^panel:\$6\$[./0-9A-Za-z]{16}\$[./0-9A-Za-z]{86}\n$`).MatchString(files["userconf.txt"]) {
		t.Errorf("userconf.txt: %q", files["userconf.txt"])
	}
	fr := files["firstrun.sh"]
	if m := regexp.MustCompile(`@[A-Z0-9_]+@`).FindString(fr); m != "" {
		t.Fatalf("marker left in firstrun.sh: %s", m)
	}
	for _, want := range []string{
		"/usr/lib/userconf-pi/userconf \"$PANEL_USER\" \"$PWHASH\"",
		"PANEL_USER='panel'", "PANEL_ID='panel-02'", `MQTT_PASS='it'\''s "quoted" \ $HOME'`,
		`MQTT_PASSWORD = "it's \"quoted\" \\ $HOME"`, "MQTT_PORT     = 1883",
		"ssid=Home Net", "psk=" + wpaPSK(f["wifi_pass"], f["wifi_ssid"]), "cfg80211.ieee80211_regdom=CH",
		"set_timezone Europe/Zurich", "panel-firstboot.service", `rm -f "$FW/firstrun.sh"`, "exit 0",
	} {
		if !strings.Contains(fr, want) {
			t.Errorf("firstrun.sh lacks %q", want)
		}
	}
	p2 := part2(t, fr)
	for _, want := range []string{"PANEL_USER='panel'", "REPO_URL='https://github.com/neocleous/ha-panel.git'",
		"install.sh\" --unattended --user \"$PANEL_USER\"", "systemctl disable panel-firstboot.service"} {
		if !strings.Contains(p2, want) {
			t.Errorf("firstboot.sh lacks %q", want)
		}
	}
	if !strings.Contains(fr, firstbootUnit) {
		t.Error("the unit is not written verbatim")
	}
}

// Part 1 runs before the network exists and must always end in its reboot.
func TestPart1NeedsNoNetworkAndCannotStopTheBoot(t *testing.T) {
	fr := render(t, goodForm())["firstrun.sh"]
	body := strings.Replace(fr, part2(t, fr), "", 1) // part 2's text is only written, not run
	for _, bad := range []string{"curl ", "wget ", "git clone", "apt-get", "nmcli ", "set -e", "exit 1"} {
		if strings.Contains(body, bad) {
			t.Errorf("part 1 contains %q", bad)
		}
	}
	if m := regexp.MustCompile(`(?m)^\s*(systemctl\s+(--no-block\s+)?)?(reboot|poweroff|shutdown)\b`).FindString(body); m != "" {
		t.Errorf("part 1 reboots by itself (%q) — the success action does that", m)
	}
	if !strings.HasSuffix(strings.TrimSpace(body), "exit 0   # systemd.run_success_action=reboot takes it from here") {
		t.Error("part 1 does not end in exit 0")
	}
	if strings.Contains(body, "useradd -m -u 1000") {
		t.Error("uid 1000 is Pi OS's own first user — useradd -u 1000 collides with it")
	}
}

// Part 1's display step, run for real against a stock boot partition — twice,
// as a re-run would — and then install.sh's own checks, which must skip both.
func TestPart1TurnsOnTheDisplayOnce(t *testing.T) {
	fr := render(t, goodForm())["firstrun.sh"]
	m := regexp.MustCompile(`(?s)# ── 6\. Display.*?\n(if ! grep.*?)\n# ── 7\.`).FindStringSubmatch(fr)
	if m == nil {
		t.Fatal("part 1 has no display step")
	}
	fw := t.TempDir()
	stockConfig := "dtparam=audio=on\n\n[pi5]\ndtoverlay=nospi10\n\n[cm5]\ndtoverlay=dwc2,dr_mode=host"
	stockCmdline := "console=serial0,115200 console=tty1 root=PARTUUID=4d8fd085-02 rootwait " + hookArgs + "\n"
	if err := os.WriteFile(filepath.Join(fw, "config.txt"), []byte(stockConfig), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(fw, "cmdline.txt"), []byte(stockCmdline), 0o644); err != nil {
		t.Fatal(err)
	}
	script := "FW=" + fw + "\nlog() { :; }\nfail() { echo \"FAIL $*\"; }\n" + m[1] + "\n"
	for i := 0; i < 2; i++ {
		if out, err := exec.Command("bash", "-c", script).CombinedOutput(); err != nil || len(out) > 0 {
			t.Fatalf("run %d: %v %s", i+1, err, out)
		}
	}
	cfg, _ := os.ReadFile(filepath.Join(fw, "config.txt"))
	cmd, _ := os.ReadFile(filepath.Join(fw, "cmdline.txt"))
	// the overlay lands under [all], never inside a model-specific section
	if !strings.HasSuffix(string(cfg), "dtoverlay=dwc2,dr_mode=host\n[all]\ndtoverlay=vc4-kms-dsi-waveshare-panel,8_0_inch\n") {
		t.Errorf("config.txt: %q", cfg)
	}
	if strings.Count(string(cmd), "fbcon=rotate:3") != 1 || strings.Count(string(cmd), "\n") != 1 {
		t.Errorf("cmdline.txt: %q", cmd)
	}
	// install.sh's checks (grep for the overlay name and for fbcon=rotate:) find them
	if !strings.Contains(string(cfg), "vc4-kms-dsi-waveshare-panel") || !strings.Contains(string(cmd), "fbcon=rotate:") {
		t.Error("install.sh would add them a second time")
	}
}

func TestNoSecretIsLogged(t *testing.T) {
	f := goodForm()
	f["mqtt_pass"] = "S3cretMqtt"
	fr := render(t, f)["firstrun.sh"]
	for _, line := range strings.Split(fr, "\n") {
		if !strings.Contains(line, "log ") && !strings.Contains(line, "echo ") {
			continue
		}
		for _, k := range []string{"pi_pass", "wifi_pass", "mqtt_pass"} {
			if strings.Contains(line, f[k]) {
				t.Errorf("%s on a logging line: %s", k, line)
			}
		}
	}
	if strings.Contains(fr, "set -x") {
		t.Error("xtrace would log every secret")
	}
}

func TestEthernetOnlyHasNoWiFiStep(t *testing.T) {
	f := goodForm()
	f["wifi_ssid"], f["wifi_pass"] = "", ""
	fr := render(t, f)["firstrun.sh"]
	if strings.Contains(fr, "nmconnection") || strings.Contains(fr, "regdom") {
		t.Error("Ethernet-only card writes a Wi-Fi connection")
	}
}

func TestPart2ProbesTheRepoItWillClone(t *testing.T) {
	p2 := part2(t, render(t, goodForm())["firstrun.sh"])
	probe := regexp.MustCompile(`sed -E '([^']+)'\)"`).FindStringSubmatch(p2)
	if probe == nil {
		t.Fatal("part 2 has no ORIGIN probe")
	}
	for u, want := range map[string]string{
		"https://github.com/neocleous/ha-panel.git": "https://github.com",
		"http://10.0.2.2:18080/ha-panel.git":        "http://10.0.2.2:18080",
		"https://user:tok@github.com/o/r.git":       "https://github.com",
	} {
		cmd := exec.Command("sed", "-E", probe[1])
		cmd.Stdin = strings.NewReader(u)
		got, err := cmd.Output()
		if err != nil || strings.TrimSpace(string(got)) != want {
			t.Errorf("%s -> %q (%v), want %s", u, got, err, want)
		}
	}
}

func TestTheScriptsParseAndPassShellcheck(t *testing.T) {
	dir := t.TempDir()
	fr := render(t, goodForm())["firstrun.sh"]
	paths := map[string]string{"firstrun.sh": fr, "firstboot.sh": part2(t, fr)}
	for name, body := range paths {
		p := filepath.Join(dir, name)
		if err := os.WriteFile(p, []byte(body), 0o755); err != nil {
			t.Fatal(err)
		}
		if out, err := exec.Command("bash", "-n", p).CombinedOutput(); err != nil {
			t.Errorf("bash -n %s: %v\n%s", name, err, out)
		}
		if sc, err := exec.LookPath("shellcheck"); err == nil {
			if out, err := exec.Command(sc, "-s", "bash", p).CombinedOutput(); err != nil {
				t.Errorf("shellcheck %s:\n%s", name, out)
			}
		} else {
			t.Log("shellcheck not installed: parsed by bash only")
		}
	}
}

func fakeCard(t *testing.T) string {
	t.Helper()
	d := t.TempDir()
	if err := os.WriteFile(filepath.Join(d, "config.txt"), []byte("[all]\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(d, "cmdline.txt"), []byte("console=tty1 root=PARTUUID=abcd-02 rootwait\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	return d
}

func TestWriteCard(t *testing.T) {
	card := fakeCard(t)
	for i := 0; i < 2; i++ { // a second write over the first: still one hook
		if err := writeCard(card, goodForm(), time.Now()); err != nil {
			t.Fatal(err)
		}
	}
	for _, n := range []string{"userconf.txt", "firstrun.sh", "cmdline.txt"} {
		b, err := os.ReadFile(filepath.Join(card, n))
		if err != nil {
			t.Fatal(err)
		}
		if bytes.Contains(b, []byte("\r")) {
			t.Errorf("%s has a CR", n)
		}
	}
	cmd, _ := os.ReadFile(filepath.Join(card, "cmdline.txt"))
	if string(cmd) != "console=tty1 root=PARTUUID=abcd-02 rootwait "+hookArgs+"\n" {
		t.Errorf("cmdline.txt: %q", cmd)
	}
	bad := goodForm()
	bad["mqtt_port"] = "x"
	empty := fakeCard(t)
	if writeCard(empty, bad, time.Now()) == nil {
		t.Fatal("invalid form written")
	}
	if _, err := os.Stat(filepath.Join(empty, "firstrun.sh")); err == nil {
		t.Fatal("a refused form left a file on the card")
	}
}

func post(t *testing.T, srv *httptest.Server, path string, body any) map[string]any {
	t.Helper()
	b, _ := json.Marshal(body)
	resp, err := http.Post(srv.URL+path, "application/json", bytes.NewReader(b))
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()
	var out map[string]any
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		t.Fatal(err)
	}
	return out
}

func TestTheWriteHandler(t *testing.T) {
	card := fakeCard(t)
	t.Setenv("PANEL_SETUP_BOOTFS", card)
	t.Setenv("HOME", t.TempDir())
	t.Setenv("XDG_CONFIG_HOME", t.TempDir())
	t.Setenv("AppData", t.TempDir())
	srv := httptest.NewServer(routes())
	defer srv.Close()
	if r := post(t, srv, "/api/write", goodForm()); r["ok"] != true {
		t.Fatalf("/api/write: %v", r)
	}
	cmd, _ := os.ReadFile(filepath.Join(card, "cmdline.txt"))
	if !strings.Contains(string(cmd), hookArgs) {
		t.Error("the handler did not write the hook")
	}
	prefs, _ := os.ReadFile(prefsPath())
	for _, k := range []string{"pi_pass", "wifi_pass", "mqtt_pass"} {
		if bytes.Contains(prefs, []byte(goodForm()[k])) {
			t.Fatalf("%s in the prefs file", k)
		}
	}
	t.Setenv("PANEL_SETUP_BOOTFS", t.TempDir()) // not a boot partition
	if r := post(t, srv, "/api/write", goodForm()); r["ok"] == true {
		t.Fatal("written with no card")
	}
}

// Every field the page posts is one the tool reads, and vice versa.
func TestThePageSendsEveryField(t *testing.T) {
	for k := range goodForm() {
		if !strings.Contains(servedPage, k+":") {
			t.Errorf("the page does not send %s", k)
		}
	}
}
