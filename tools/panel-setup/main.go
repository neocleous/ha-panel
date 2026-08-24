// HA Panel Setup — self-contained SD-card preparation tool.
// Single static binary, no runtime dependencies. Serves a browser UI on
// http://127.0.0.1:8377 and writes userconf.txt + firstrun.sh straight to a
// mounted Pi OS boot partition.
package main

import (
	"context"
	"crypto/rand"
	"crypto/sha512"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"sort"
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

// ── File generation ────────────────────────────────────────────────────────────

func shq(v string) string { return "'" + strings.ReplaceAll(v, "'", `'\''`) + "'" }
func pyq(v string) string {
	return strings.ReplaceAll(strings.ReplaceAll(v, `\`, `\\`), `"`, `\"`)
}

type formData map[string]string

func buildFiles(f formData) (map[string]string, error) {
	hostname := f["hostname"]
	username := f["username"]
	pwHash := sha512Crypt(f["pi_pass"], randSalt())
	mqttHost := f["mqtt_host"]

	subnet := "192.168.0.0/16"
	parts := strings.Split(mqttHost, ".")
	if len(parts) == 4 {
		numeric := true
		for _, p := range parts {
			for _, c := range p {
				if c < '0' || c > '9' {
					numeric = false
				}
			}
			if p == "" {
				numeric = false
			}
		}
		if numeric {
			subnet = parts[0] + "." + parts[1] + "." + parts[2] + ".0/24"
		}
	}

	generated := time.Now().Format("2006-01-02 15:04")

	wifiBlock := "\n# Wi-Fi skipped — using ethernet.\n"
	if f["wifi_ssid"] != "" {
		wifiBlock = strings.NewReplacer(
			"@SSID@", f["wifi_ssid"],
			"@WPASS@", f["wifi_pass"],
			"@WCOUNTRY@", f["wifi_country"],
		).Replace(wifiTemplate)
	}

	firstrun := strings.NewReplacer(
		"@GENERATED@", generated,
		"@HOSTNAME@", hostname,
		"@USERNAME@", username,
		"@PWHASH@", pwHash,
		"@HAURL@", f["ha_url"],
		"@MQTTHOST@", mqttHost,
		"@MQTTPORT@", f["mqtt_port"],
		"@TIMEZONE@", f["timezone"],
		"@LOCALE@", f["locale"],
		"@REPOURL@", f["repo_url"],
		"@SUBNET@", subnet,
		"@WIFIBLOCK@", wifiBlock,
		"@HOSTNAME_SH@", shq(hostname),
		"@HAURL_SH@", shq(f["ha_url"]),
		"@MQTTHOST_SH@", shq(mqttHost),
		"@MQTTPORT_SH@", shq(f["mqtt_port"]),
		"@MQTTUSER_SH@", shq(f["mqtt_user"]),
		"@MQTTPASS_SH@", shq(f["mqtt_pass"]),
		"@MQTTHOST_PY@", pyq(mqttHost),
		"@MQTTUSER_PY@", pyq(f["mqtt_user"]),
		"@MQTTPASS_PY@", pyq(f["mqtt_pass"]),
	).Replace(firstrunTemplate)

	return map[string]string{
		"userconf.txt": username + ":" + pwHash + "\n",
		"firstrun.sh":  firstrun,
	}, nil
}

// ── HTTP handlers ────────────────────────────────────────────────────────────────

func jsonResp(w http.ResponseWriter, code int, obj any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(obj)
}

func main() {
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
		files, err := buildFiles(f)
		if err == nil {
			for name, content := range files {
				// UTF-8 + LF always — firstrun.sh is parsed by bash on the Pi.
				err = os.WriteFile(filepath.Join(sd, name), []byte(content), 0o755)
				if err != nil {
					break
				}
			}
		}
		if err != nil {
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
