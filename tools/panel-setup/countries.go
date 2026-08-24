package main

import "strings"

var countries = [][2]string{
	{"AL", "Albania"}, {"AR", "Argentina"}, {"AU", "Australia"},
	{"AT", "Austria"}, {"BE", "Belgium"}, {"BA", "Bosnia and Herzegovina"},
	{"BR", "Brazil"}, {"BG", "Bulgaria"}, {"CA", "Canada"}, {"CL", "Chile"},
	{"CN", "China"}, {"CO", "Colombia"}, {"HR", "Croatia"}, {"CY", "Cyprus"},
	{"CZ", "Czechia"}, {"DK", "Denmark"}, {"EG", "Egypt"}, {"EE", "Estonia"},
	{"FI", "Finland"}, {"FR", "France"}, {"GE", "Georgia"}, {"DE", "Germany"},
	{"GR", "Greece"}, {"HK", "Hong Kong"}, {"HU", "Hungary"},
	{"IS", "Iceland"}, {"IN", "India"}, {"ID", "Indonesia"},
	{"IE", "Ireland"}, {"IL", "Israel"}, {"IT", "Italy"}, {"JP", "Japan"},
	{"KR", "Korea, Republic of"}, {"LV", "Latvia"},
	{"LI", "Liechtenstein"}, {"LT", "Lithuania"}, {"LU", "Luxembourg"},
	{"MY", "Malaysia"}, {"MT", "Malta"}, {"MX", "Mexico"},
	{"MD", "Moldova"}, {"ME", "Montenegro"}, {"NL", "Netherlands"},
	{"NZ", "New Zealand"}, {"MK", "North Macedonia"}, {"NO", "Norway"},
	{"PH", "Philippines"}, {"PL", "Poland"}, {"PT", "Portugal"},
	{"RO", "Romania"}, {"RS", "Serbia"}, {"SG", "Singapore"},
	{"SK", "Slovakia"}, {"SI", "Slovenia"}, {"ZA", "South Africa"},
	{"ES", "Spain"}, {"SE", "Sweden"}, {"CH", "Switzerland"},
	{"TW", "Taiwan"}, {"TH", "Thailand"}, {"TR", "Türkiye"},
	{"UA", "Ukraine"}, {"AE", "United Arab Emirates"},
	{"GB", "United Kingdom"}, {"US", "United States"}, {"VN", "Vietnam"},
}

func init() {
	var b strings.Builder
	for _, c := range countries {
		b.WriteString(`<option value="` + c[0] + `">` + c[0] + " — " + c[1] + "</option>")
	}
	// page is a package-level const; build the served variant here.
	servedPage = strings.Replace(page, "__COUNTRY_OPTIONS__", b.String(), 1)
}

var servedPage string
