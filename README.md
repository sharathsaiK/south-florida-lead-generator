# South Florida Business Lead Generator

> Built for **Co-web Consulting** — a web development consultancy that identifies local service businesses with no web presence and delivers custom websites to grow their customer acquisition.

A Python sales intelligence tool that uses the Google Places API to find high-rated local businesses across South Florida with no website, then generates a full outreach package for each lead — pitch, objection handling, best call time, review signals, social links, interactive heatmap, and a CSV call sheet.

---

## Features

### Lead Discovery
- Scans **15 cities × 23 business categories** across Miami-Dade, Broward, and Palm Beach counties
- Filters to businesses that are **operational**, **rated ≥ 3.5★**, have **≥ 10 reviews**, and **have no website listed on Google**
- Ranks results by review volume — highest social proof with no web presence = best lead

### Pitch Intelligence (per lead)
- **Objection prediction** — categorizes each business into one of 5 objection profiles based on review count and category:
  - *Word of mouth comfort* (150+ reviews)
  - *Using social media instead* (salons, tattoo shops)
  - *Too busy / no time* (restaurants, cafes)
  - *Doesn't see the ROI* (trades: plumbers, HVAC, roofers)
  - *Tech-averse / not sure how it works* (default)
- **Custom pitch** — tailored one-liner to counter each objection
- **Best call time** — category-aware timing (e.g. "Call 8–10 AM for tradespeople", "Avoid lunch rush for restaurants")

### Review Signal Detection
- Scans up to 5 Google reviews per business for keywords suggesting no online presence (`"no website"`, `"hard to find online"`, `"not online"`, `"google them"`, etc.)
- Flags businesses where customers have complained about their missing web presence — the warmest leads

### Outputs
| Output | Description |
|---|---|
| **Terminal** | Top 10 leads with full pitch package and social links |
| **leads.csv** | Complete call sheet — open in Excel or Google Sheets to track calls and follow-ups |
| **leads_map.html** | Interactive Folium heatmap — click any marker for the full lead card |

### Heatmap
Interactive map built with [Folium](https://python-visualization.github.io/folium/) showing lead density across South Florida. Each marker shows:
- Business name, rating, phone, address
- Business hours + best call time
- Objection type + pitch angle
- Review flag if a customer mentioned no online presence

---

## Sample Output

```
================================================================================
TOP 10 LEADS  (no website · >=3.5★ · >=10 reviews)
================================================================================

1. Yamashiro Miami  [restaurant]
   Rating   : 4.8  |  Reviews: 1575
   Phone    : (786) 412-2791
   Address  : 159 NE 6th St fl 9, Miami, FL 33132, USA
   About    : A top-rated restaurant with 1575+ customer reviews.
   Hours    : Tuesday: 5:00 – 11:00 PM
   Best time: Call 2–4 PM (avoid lunch rush 11:30 AM–1:30 PM)
   Objection: Word of mouth comfort
   Pitch    : "A site makes referrals faster — instead of describing your shop, people just send your link."
   Review   : None found
   Maps     : https://www.google.com/maps/place/?q=place_id:...
   Instagram: https://google.com/search?q="Yamashiro+Miami"+Miami+instagram
   Facebook : https://google.com/search?q="Yamashiro+Miami"+Miami+facebook

================================================================================
HOT ZONES  (out of 30 total leads)
================================================================================
  Miami                     ████████████ 12
  Hialeah                   ████████ 8
  Miami Beach               █████ 5
```

---

## Setup

```bash
git clone https://github.com/sharathsaiK/south-florida-lead-generator.git
cd south-florida-lead-generator
pip install requests folium
export GOOGLE_PLACES_API_KEY="your_key_here"
python find_leads.py
```

You'll need a [Google Places API key](https://console.cloud.google.com/) with **Places API (New)** enabled. The field mask in the request keeps billing minimal — only the fields actually used are charged.

---

## Stack

| Layer | Tech |
|---|---|
| Language | Python |
| Maps | Folium + Leaflet.js |
| Data | Google Places API (New) — `places:searchText` |
| Export | Python `csv` module → Excel/Sheets compatible |
| Social | Google search URL generation for Instagram/Facebook |

---

## Part of Co-web Consulting

This tool powers the client acquisition pipeline for Co-web Consulting. Once leads are identified and ranked, we call during the optimal window, lead with the category-matched pitch, and deliver custom mobile-responsive websites for local service businesses across South Florida.
