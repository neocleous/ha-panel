// HA Panel Setup — self-contained SD-card preparation tool.
// Single static binary, no runtime dependencies. Serves a browser UI on
// http://127.0.0.1:8377 and writes three things to a freshly flashed Pi OS
// Lite boot partition: userconf.txt, firstrun.sh, and the systemd.run= hook in
// cmdline.txt that makes the first boot run firstrun.sh.
//
// The first boot has two parts (templates.go):
//   - part 1, firstrun.sh, runs once under systemd.run= — early, with NO
//     network. It writes the panel's own files and arms part 2, removes the
//     hook and itself, and reboots.
//   - part 2, panel-firstboot.service, runs on the next boot after
//     network-online.target: clone, system/install.sh --unattended, reboot
//     into the kiosk. On a failure it stays armed and retries next boot.
package main

import (
	"context"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha1"
	"crypto/sha512"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

const port = "8377"

// ── Preferences ──────────────────────────────────────────────────────────────

var factoryDefaults = map[string]string{
	"username":     "panel",
	"ha_base":      "http://homeassistant.local:8123",
	"mqtt_port":    "1883",
	"mqtt_user":    "mqtt-panels",
	"wifi_country": "CH",
	"wifi_ssid":    "",
	"timezone":     "Europe/Zurich",
	"locale":       "en_GB.UTF-8",
	"repo_url":     "https://github.com/neocleous/ha-panel.git",
}

func prefsPath() string {
	dir, err := os.UserConfigDir()
	if err != nil {
		dir = "."
	}
	return filepath.Join(dir, "ha-panel-setup", "prefs.json")
}

func loadPrefs() map[string]string {
	p := map[string]string{}
	for k, v := range factoryDefaults {
		p[k] = v
	}
	if b, err := os.ReadFile(prefsPath()); err == nil {
		var saved map[string]string
		if json.Unmarshal(b, &saved) == nil {
			for k := range factoryDefaults {
				if v, ok := saved[k]; ok {
					p[k] = v
				}
			}
		}
	}
	return p
}

func savePrefs(f map[string]string) {
	keep := map[string]string{}
	for k, def := range factoryDefaults {
		if v, ok := f[k]; ok {
			keep[k] = v
		} else {
			keep[k] = def
		}
	}
	path := prefsPath()
	_ = os.MkdirAll(filepath.Dir(path), 0o755)
	b, _ := json.MarshalIndent(keep, "", "  ")
	_ = os.WriteFile(path, b, 0o600)
}

// ── SD card (bootfs) detection ──────────────────────────────────────────────────

func isBootfs(p string) bool {
	c, err1 := os.Stat(filepath.Join(p, "config.txt"))
	m, err2 := os.Stat(filepath.Join(p, "cmdline.txt"))
	return err1 == nil && err2 == nil && !c.IsDir() && !m.IsDir()
}

func findBootfs() string {
	if p := os.Getenv("PANEL_SETUP_BOOTFS"); p != "" { // an unusual mount point, and the tests
		if isBootfs(p) {
			return p
		}
		return ""
	}
	var candidates []string
	switch runtime.GOOS {
	case "darwin":
		candidates = []string{"/Volumes/bootfs", "/Volumes/bootfs1", "/Volumes/boot"}
	case "windows":
		for d := 'C'; d <= 'Z'; d++ {
			candidates = append(candidates, string(d)+":\\")
		}
	default:
		user := os.Getenv("USER")
		candidates = []string{
			"/media/" + user + "/bootfs", "/run/media/" + user + "/bootfs",
			"/media/" + user + "/boot", "/media/bootfs",
		}
	}
	for _, p := range candidates {
		if isBootfs(p) {
			return p
		}
	}
	return ""
}

// ── Network helpers ──────────────────────────────────────────────────────────────

func hostResolves(host string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), 1200*time.Millisecond)
	defer cancel()
	_, err := net.DefaultResolver.LookupHost(ctx, host)
	return err == nil
}

func detectExistingPanels() []int {
	var mu sync.Mutex
	var found []int
	var wg sync.WaitGroup
	for n := 1; n <= 16; n++ {
		wg.Add(1)
		go func(n int) {
			defer wg.Done()
			h := fmt.Sprintf("panel-%02d", n)
			if hostResolves(h) || hostResolves(h+".local") {
				mu.Lock()
				found = append(found, n)
				mu.Unlock()
			}
		}(n)
	}
	wg.Wait()
	sort.Ints(found)
	return found
}

func nextFreePanel(existing []int) int {
	n := 1
	for {
		used := false
		for _, e := range existing {
			if e == n {
				used = true
				break
			}
		}
		if !used {
			return n
		}
		n++
	}
}

func resolveIPv4(host string) string {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	addrs, err := net.DefaultResolver.LookupIP(ctx, "ip4", host)
	if err != nil || len(addrs) == 0 {
		return ""
	}
	return addrs[0].String()
}

// mqttCheck performs a minimal MQTT 3.1.1 CONNECT and returns the CONNACK
// return code: 0 = ok, 4 = bad username/password, 5 = not authorised.
func mqttCheck(host, portStr, user, pass string) (int, error) {
	enc := func(s string) []byte {
		b := []byte(s)
		return append([]byte{byte(len(b) >> 8), byte(len(b))}, b...)
	}
	payload := append(append(enc("ha-panel-setup"), enc(user)...), enc(pass)...)
	varHdr := append(enc("MQTT"), 0x04, 0xC2, 0x00, 0x1E)
	remaining := len(varHdr) + len(payload)
	var rl []byte
	x := remaining
	for {
		d := byte(x % 128)
		x /= 128
		if x > 0 {
			d |= 0x80
		}
		rl = append(rl, d)
		if x == 0 {
			break
		}
	}
	pkt := append(append(append([]byte{0x10}, rl...), varHdr...), payload...)

	conn, err := net.DialTimeout("tcp", net.JoinHostPort(host, portStr), 4*time.Second)
	if err != nil {
		return -1, err
	}
	defer conn.Close()
	_ = conn.SetDeadline(time.Now().Add(4 * time.Second))
	if _, err := conn.Write(pkt); err != nil {
		return -1, err
	}
	resp := make([]byte, 4)
	nRead, err := conn.Read(resp)
	if err != nil || nRead < 4 || resp[0] != 0x20 {
		return -1, fmt.Errorf("unexpected broker response")
	}
	return int(resp[3]), nil
}

// ── SHA-512-crypt ($6$) — byte-identical to `openssl passwd -6` ──────────────

const itoa64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

func b6424(b2, b1, b0 byte, n int, out *strings.Builder) {
	w := uint32(b2)<<16 | uint32(b1)<<8 | uint32(b0)
	for i := 0; i < n; i++ {
		out.WriteByte(itoa64[w&0x3F])
		w >>= 6
	}
}

func randSalt() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	var s strings.Builder
	for _, c := range b {
		s.WriteByte(itoa64[int(c)%len(itoa64)])
	}
	return s.String()
}

func sha512Crypt(password, salt string) string {
	const rounds = 5000
	pw := []byte(password)
	if len(salt) > 16 {
		salt = salt[:16]
	}
	sl := []byte(salt)

	h := sha512.New()
	h.Write(pw)
	h.Write(sl)
	h.Write(pw)
	B := h.Sum(nil)

	a := sha512.New()
	a.Write(pw)
	a.Write(sl)
	i := len(pw)
	for i > 64 {
		a.Write(B)
		i -= 64
	}
	a.Write(B[:i])
	for i = len(pw); i > 0; i >>= 1 {
		if i&1 == 1 {
			a.Write(B)
		} else {
			a.Write(pw)
		}
	}
	A := a.Sum(nil)

	dp := sha512.New()
	for range pw {
		dp.Write(pw)
	}
	DP := dp.Sum(nil)
	P := make([]byte, 0, len(pw))
	for len(P) < len(pw) {
		P = append(P, DP...)
	}
	P = P[:len(pw)]

	ds := sha512.New()
	for j := 0; j < 16+int(A[0]); j++ {
		ds.Write(sl)
	}
	DS := ds.Sum(nil)
	S := make([]byte, 0, len(sl))
	for len(S) < len(sl) {
		S = append(S, DS...)
	}
	S = S[:len(sl)]

	C := A
	for r := 0; r < rounds; r++ {
		h := sha512.New()
		if r&1 == 1 {
			h.Write(P)
		} else {
			h.Write(C)
		}
		if r%3 != 0 {
			h.Write(S)
		}
		if r%7 != 0 {
			h.Write(P)
		}
		if r&1 == 1 {
			h.Write(C)
		} else {
			h.Write(P)
		}
		C = h.Sum(nil)
	}

	var out strings.Builder
	idx := [][3]int{
		{0, 21, 42}, {22, 43, 1}, {44, 2, 23}, {3, 24, 45}, {25, 46, 4},
		{47, 5, 26}, {6, 27, 48}, {28, 49, 7}, {50, 8, 29}, {9, 30, 51},
		{31, 52, 10}, {53, 11, 32}, {12, 33, 54}, {34, 55, 13}, {56, 14, 35},
		{15, 36, 57}, {37, 58, 16}, {59, 17, 38}, {18, 39, 60}, {40, 61, 19},
		{62, 20, 41},
	}
	for _, t := range idx {
		b6424(C[t[0]], C[t[1]], C[t[2]], 4, &out)
	}
	b6424(0, 0, C[63], 2, &out)
	return "$6$" + salt + "$" + out.String()
}

// wpaPSK is the 256-bit WPA2 pre-shared key, PBKDF2-HMAC-SHA1(passphrase,
// ssid, 4096, 32), as 64 hex digits — what wpa_passphrase prints and what a
// NetworkManager keyfile accepts as psk=. The passphrase itself never has to be
// escaped into a file on the card. (Standard library only: go.mod is 1.22,
// which has no crypto/pbkdf2.)
func wpaPSK(passphrase, ssid string) string {
	prf := hmac.New(sha1.New, []byte(passphrase))
	out := make([]byte, 0, 40)
	for block := uint32(1); len(out) < 32; block++ {
		prf.Reset()
		prf.Write([]byte(ssid))
		var ctr [4]byte
		binary.BigEndian.PutUint32(ctr[:], block)
		prf.Write(ctr[:])
		u := prf.Sum(nil)
		t := append([]byte(nil), u...)
		for i := 1; i < 4096; i++ {
			prf.Reset()
			prf.Write(u)
			u = prf.Sum(nil)
			for k := range t {
				t[k] ^= u[k]
			}
		}
		out = append(out, t...)
	}
	return hex.EncodeToString(out[:32])
}

// ── Validation ───────────────────────────────────────────────────────────────────
// Every value ends up in a shell script, a Python file or a kernel command line
// on the card. Anything that could break one of those is refused here, before a
// single byte is written.

var (
	reUsername = regexp.MustCompile(`^[a-z][a-z0-9-]{0,31}$`) // userconf-pi's own rule
	reHostname = regexp.MustCompile(`^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$`)
	reCountry  = regexp.MustCompile(`^[A-Z]{2}$`)
	reTimezone = regexp.MustCompile(`^[A-Za-z_]+(/[A-Za-z0-9_+\-]+){1,2}$`)
	reLocale   = regexp.MustCompile(`^[a-z]{2,3}_[A-Z]{2}\.UTF-8$`)
	reURL      = regexp.MustCompile(`^https?://[^\s'"\\` + "`" + `]+$`)
	reSSIDKey  = regexp.MustCompile(`^[A-Za-z0-9_.@+-]([A-Za-z0-9 _.@+-]*[A-Za-z0-9_.@+-])?$`)
)

type formData map[string]string

// printable: no control characters, so no value can end a line or a heredoc.
func printable(s string) bool {
	for _, r := range s {
		if r < 0x20 || r == 0x7f {
			return false
		}
	}
	return true
}

func validate(f formData) error {
	port, perr := strconv.Atoi(f["mqtt_port"])
	switch {
	case !reUsername.MatchString(f["username"]) || f["username"] == "root":
		return errors.New("Pi username: lower-case letters, digits and hyphens, starting with a letter, at most 32")
	case f["pi_pass"] == "" || !printable(f["pi_pass"]):
		return errors.New("Pi user password: required")
	case !reHostname.MatchString(f["hostname"]):
		return errors.New("hostname: lower-case letters, digits and hyphens")
	case !reURL.MatchString(f["ha_url"]):
		return errors.New("dashboard URL: http(s)://… with no spaces or quotes")
	case f["mqtt_host"] == "" || !printable(f["mqtt_host"]) || strings.ContainsAny(f["mqtt_host"], " /"):
		return errors.New("MQTT host: a hostname or IP address")
	case perr != nil || port < 1 || port > 65535:
		return errors.New("MQTT port: 1 to 65535")
	case !printable(f["mqtt_user"]) || !printable(f["mqtt_pass"]) || f["mqtt_pass"] == "":
		return errors.New("MQTT username/password: required, single line")
	case !reTimezone.MatchString(f["timezone"]):
		return errors.New("timezone: Area/City, e.g. Europe/Zurich")
	case !reLocale.MatchString(f["locale"]):
		return errors.New("locale: e.g. en_GB.UTF-8")
	case !reURL.MatchString(f["repo_url"]):
		return errors.New("repository URL: http(s)://… with no spaces or quotes")
	}
	if f["wifi_ssid"] != "" {
		switch {
		case len(f["wifi_ssid"]) > 32 || !printable(f["wifi_ssid"]):
			return errors.New("Wi-Fi SSID: at most 32 characters")
		case len(f["wifi_pass"]) < 8 || len(f["wifi_pass"]) > 63 || !printable(f["wifi_pass"]):
			return errors.New("Wi-Fi password: 8 to 63 characters (WPA2)")
		case !reCountry.MatchString(f["wifi_country"]):
			return errors.New("Wi-Fi country: pick one — the radio stays blocked without it")
		}
	}
	return nil
}

// ── File generation ────────────────────────────────────────────────────────────

func shq(v string) string { return "'" + strings.ReplaceAll(v, "'", `'\''`) + "'" }
func pyq(v string) string {
	return strings.ReplaceAll(strings.ReplaceAll(v, `\`, `\\`), `"`, `\"`)
}

// nmSSID is the SSID as a NetworkManager keyfile reads it: plain when that is
// unambiguous, otherwise as its bytes — ssid= takes either (nm-settings-keyfile(5)).
func nmSSID(s string) string {
	if reSSIDKey.MatchString(s) {
		return s
	}
	var b strings.Builder
	for _, c := range []byte(s) {
		b.WriteString(strconv.Itoa(int(c)) + ";")
	}
	return b.String()
}

// uuid4 is a random RFC 4122 UUID, for the NetworkManager connection.
func uuid4() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	b[6] = b[6]&0x0f | 0x40
	b[8] = b[8]&0x3f | 0x80
	return fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:16])
}

// hookArgs is what cmdline.txt carries for the one boot that runs firstrun.sh —
// Raspberry Pi Imager's own three words, with the path where Pi OS Bookworm and
// later mount the boot partition. (Imager writes /boot/firstrun.sh and relies
// on the initramfs's imager_fixup to rewrite it, at the cost of an extra
// reboot; the direct path skips that.) Part 1 removes exactly these words.
const hookArgs = "systemd.run=/boot/firmware/firstrun.sh systemd.run_success_action=reboot systemd.unit=kernel-command-line.target"

// withHook appends the hook to cmdline.txt's single line, once.
func withHook(cmdline string) string {
	line := strings.TrimRight(cmdline, "\r\n")
	if strings.Contains(line, "systemd.run=") {
		return line + "\n"
	}
	return line + " " + hookArgs + "\n"
}

func buildFiles(f formData, now time.Time) (map[string]string, error) {
	if err := validate(f); err != nil {
		return nil, err
	}
	hostname := f["hostname"]
	username := f["username"]
	pwHash := sha512Crypt(f["pi_pass"], randSalt())
	mqttHost := f["mqtt_host"]

	wifiBlock := "log \"Wi-Fi: none — Ethernet\"\n"
	if f["wifi_ssid"] != "" {
		wifiBlock = strings.NewReplacer(
			"@UUID@", uuid4(),
			"@SSID_NM@", nmSSID(f["wifi_ssid"]),
			"@PSK@", wpaPSK(f["wifi_pass"], f["wifi_ssid"]),
			"@COUNTRY@", f["wifi_country"],
		).Replace(wifiTemplate)
	}

	firstboot := strings.NewReplacer(
		"@USERNAME_SH@", shq(username),
		"@REPOURL_SH@", shq(f["repo_url"]),
	).Replace(firstbootScript)

	firstrun := strings.NewReplacer(
		"@GENERATED@", now.Format("2006-01-02 15:04"),
		"@HOSTNAME@", hostname,
		"@USERNAME_SH@", shq(username),
		"@HOSTNAME_SH@", shq(hostname),
		"@PWHASH_SH@", shq(pwHash),
		"@WIFIBLOCK@", wifiBlock,
		"@TIMEZONE@", f["timezone"],
		"@LOCALE@", f["locale"],
		"@HAURL_SH@", shq(f["ha_url"]),
		"@MQTTHOST_SH@", shq(mqttHost),
		"@MQTTPORT_SH@", shq(f["mqtt_port"]),
		"@MQTTUSER_SH@", shq(f["mqtt_user"]),
		"@MQTTPASS_SH@", shq(f["mqtt_pass"]),
		"@MQTTPORT@", f["mqtt_port"],
		"@MQTTHOST_PY@", pyq(mqttHost),
		"@MQTTUSER_PY@", pyq(f["mqtt_user"]),
		"@MQTTPASS_PY@", pyq(f["mqtt_pass"]),
		"@FIRSTBOOT@", firstboot,
		"@FIRSTBOOT_UNIT@", firstbootUnit,
	).Replace(firstrunTemplate)
	// (main_test.go checks that no @MARKER@ survives rendering — not done here,
	// because a password may legitimately look like one.)

	return map[string]string{
		"userconf.txt": username + ":" + pwHash + "\n",
		"firstrun.sh":  firstrun,
	}, nil
}

// writeCard writes userconf.txt, firstrun.sh and the hook in cmdline.txt —
// UTF-8 and LF always, because bash and the kernel read them. cmdline.txt is
// read before anything is written, so a card that has none is refused untouched.
func writeCard(sd string, f formData, now time.Time) error {
	files, err := buildFiles(f, now)
	if err != nil {
		return err
	}
	cmdPath := filepath.Join(sd, "cmdline.txt")
	cmd, err := os.ReadFile(cmdPath)
	if err != nil {
		return err
	}
	for name, content := range files {
		if err := os.WriteFile(filepath.Join(sd, name), []byte(content), 0o755); err != nil {
			return err
		}
	}
	return os.WriteFile(cmdPath, []byte(withHook(string(cmd))), 0o755)
}

// ── HTTP handlers ────────────────────────────────────────────────────────────────

func jsonResp(w http.ResponseWriter, code int, obj any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(obj)
}

func routes() *http.ServeMux {
	mux := http.NewServeMux()

	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/" {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "text/html; charset=utf-8")
		_, _ = w.Write([]byte(servedPage))
	})

	mux.HandleFunc("/api/defaults", func(w http.ResponseWriter, r *http.Request) {
		prefs := loadPrefs()
		existing := detectExistingPanels()
		if existing == nil {
			existing = []int{}
		}
		host := ""
		if u, err := url.Parse(prefs["ha_base"]); err == nil {
			host = u.Hostname()
		}
		guess := resolveIPv4(host)
		if guess == "" {
			guess = host
		}
		jsonResp(w, 200, map[string]any{
			"prefs":           prefs,
			"existing":        existing,
			"next_panel":      nextFreePanel(existing),
			"mqtt_host_guess": guess,
		})
	})

	mux.HandleFunc("/api/bootfs", func(w http.ResponseWriter, r *http.Request) {
		p := findBootfs()
		var v any
		if p != "" {
			v = p
		}
		jsonResp(w, 200, map[string]any{"path": v})
	})

	mux.HandleFunc("/api/mqtt", func(w http.ResponseWriter, r *http.Request) {
		var f formData
		if json.NewDecoder(r.Body).Decode(&f) != nil {
			jsonResp(w, 400, map[string]any{"ok": false, "error": "bad request"})
			return
		}
		rc, err := mqttCheck(f["mqtt_host"], f["mqtt_port"], f["mqtt_user"], f["mqtt_pass"])
		switch {
		case err != nil:
			jsonResp(w, 200, map[string]any{"ok": false,
				"error": "Cannot reach broker: " + err.Error()})
		case rc == 0:
			jsonResp(w, 200, map[string]any{"ok": true})
		case rc == 4 || rc == 5:
			jsonResp(w, 200, map[string]any{"ok": false,
				"error": "Broker reachable but rejected the username or password"})
		default:
			jsonResp(w, 200, map[string]any{"ok": false,
				"error": fmt.Sprintf("Broker refused (code %d)", rc)})
		}
	})

	mux.HandleFunc("/api/write", func(w http.ResponseWriter, r *http.Request) {
		var f formData
		if json.NewDecoder(r.Body).Decode(&f) != nil {
			jsonResp(w, 400, map[string]any{"ok": false, "error": "bad request"})
			return
		}
		sd := findBootfs()
		if sd == "" {
			jsonResp(w, 200, map[string]any{"ok": false, "error": "SD card no longer mounted"})
			return
		}
		if err := writeCard(sd, f, time.Now()); err != nil {
			jsonResp(w, 200, map[string]any{"ok": false, "error": err.Error()})
			return
		}
		savePrefs(f)
		jsonResp(w, 200, map[string]any{"ok": true})
	})

	mux.HandleFunc("/api/quit", func(w http.ResponseWriter, r *http.Request) {
		jsonResp(w, 200, map[string]any{"ok": true})
		go func() { time.Sleep(200 * time.Millisecond); os.Exit(0) }()
	})
	return mux
}

func main() {
	mux := routes()
	addr := "127.0.0.1:" + port
	urlStr := "http://" + addr + "/"
	fmt.Println("HA Panel Setup —", urlStr, " (Ctrl-C or the Quit button to exit)")
	go func() {
		time.Sleep(400 * time.Millisecond)
		openBrowser(urlStr)
	}()
	ln, err := net.Listen("tcp", addr)
	if err != nil {
		// Port taken — almost certainly another copy already running.
		// Just bring up its UI and exit quietly.
		openBrowser(urlStr)
		return
	}
	_ = http.Serve(ln, mux)
}

func openBrowser(u string) {
	switch runtime.GOOS {
	case "darwin":
		_ = exec.Command("open", u).Start()
	case "windows":
		_ = exec.Command("rundll32", "url.dll,FileProtocolHandler", u).Start()
	default:
		_ = exec.Command("xdg-open", u).Start()
	}
}
