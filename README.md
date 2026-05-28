# South Florida Business Lead Generator

> Built for **Co-web Consulting** — a web development consultancy that identifies local service businesses with no web presence and delivers custom websites to grow their customer acquisition.

A Python automation tool that uses the Google Places API to surface high-rated local businesses across South Florida that have no website — the ideal targets for web development outreach.

---

## What It Does

Scans **15 cities × 23 business categories = 345 targeted queries** across Miami-Dade, Broward, and Palm Beach counties. For each business it finds, it filters by:

- ✅ No website listed
- ✅ Rating ≥ 3.5 stars
- ✅ Review count ≥ 10
- ✅ Business status: Operational

Results are ranked by review volume — the businesses with the most reviews and no website are the highest-value leads (proven demand, missing online presence).

---

## Coverage

**Cities (15):** Miami, Hialeah, Miami Beach, Coral Gables, Homestead, Fort Lauderdale, Hollywood, Pembroke Pines, Pompano Beach, Coral Springs, Miramar, Boca Raton, Delray Beach, West Palm Beach, Boynton Beach

**Business Categories (23):** Plumber, Electrician, Roofer, Landscaper, Auto Repair, Hair Salon, Barber Shop, Nail Salon, Tattoo Shop, Restaurant, Bakery, Coffee Shop, Dentist, Chiropractor, Veterinarian, Tow Truck, Moving Company, Junk Removal, Pool Cleaning, HVAC, Pest Control, House Cleaning

---

## Sample Output

```
================================================================================
FOUND 60+ LEADS (no website, >=3.5★, >=10 reviews)
================================================================================

1. Miami Plumbing Experts  [plumber]
   4.8★  (312 reviews)
   (305) 555-0192
   1234 SW 8th St, Miami, FL 33135

2. South Beach Auto Repair  [auto repair shop]
   4.6★  (278 reviews)
   (305) 555-0147
   567 Alton Rd, Miami Beach, FL 33139
...
```

---

## Setup

```bash
git clone https://github.com/sharathsaiK/south-florida-lead-generator.git
cd south-florida-lead-generator
pip install requests

export GOOGLE_PLACES_API_KEY="your_key_here"
python find_leads.py
```

You'll need a [Google Places API key](https://console.cloud.google.com/) with the **Places API (New)** enabled.

---

## Stack

- **Language:** Python
- **API:** Google Places API (New) — `places:searchText` endpoint
- **Auth:** `X-Goog-Api-Key` header with field mask to minimize billing
- **Output:** Ranked console output sorted by review count

---

## Part of Co-web Consulting

This tool powers the client acquisition pipeline for [Co-web Consulting](https://github.com/sharathsaiK). Once leads are identified, we reach out and build custom, mobile-responsive websites for local service businesses across South Florida.
