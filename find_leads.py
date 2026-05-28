"""
Finds South Florida businesses with no website — leads for selling websites.

Setup:
  1) Create a Google Cloud project: https://console.cloud.google.com/
  2) Enable "Places API (New)" for the project.
  3) Create an API key (APIs & Services -> Credentials -> Create credentials -> API key).
  4) export GOOGLE_PLACES_API_KEY="your_key_here"
  5) pip install requests folium
  6) python find_leads.py

Filters: rating >= 3.5, review count >= 10, no website on Google.
Outputs:
  - Terminal: top 10 leads with pitch angle, best call time, review flags, links.
  - leads.csv: full call sheet you can open in Excel / Google Sheets.
  - leads_map.html: visual heatmap (auto-opens in browser).
"""

import csv
import os
import sys
import time
import webbrowser
from collections import Counter
from urllib.parse import quote_plus
import requests

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

MIN_RATING   = 3.5
MIN_REVIEWS  = 10
TARGET_LEADS = 10
CANDIDATE_POOL = 30
MAX_QUERIES    = 30

CITIES = [
    "Miami FL", "Hialeah FL", "Miami Beach FL", "Coral Gables FL", "Homestead FL",
    "Fort Lauderdale FL", "Hollywood FL", "Pembroke Pines FL", "Pompano Beach FL",
    "Coral Springs FL", "Miramar FL", "Boca Raton FL", "Delray Beach FL",
    "West Palm Beach FL", "Boynton Beach FL",
]

CATEGORIES = [
    "plumber", "electrician", "roofer", "landscaper", "auto repair shop",
    "hair salon", "barber shop", "nail salon", "tattoo shop",
    "restaurant", "bakery", "coffee shop",
    "dentist", "chiropractor", "veterinarian",
    "tow truck", "moving company", "junk removal", "pool cleaning",
    "hvac contractor", "pest control", "house cleaning",
]

SOCIAL_MEDIA_CATEGORIES = {"hair salon", "barber shop", "nail salon", "tattoo shop"}
TRADE_CATEGORIES = {
    "plumber", "electrician", "roofer", "hvac contractor",
    "pest control", "pool cleaning", "tow truck", "junk removal", "moving company",
}
FOOD_CATEGORIES = {"restaurant", "bakery", "coffee shop"}

# Keywords in reviews that suggest the business needs a website.
# Kept specific to online presence — avoid ambiguous phrases like
# "hard to find" which often means the physical location.
WEBSITE_KEYWORDS = [
    "no website",
    "website",
    "web page",
    "webpage",
    "find them online",
    "find you online",
    "find it online",
    "hard to find online",
    "can't find online",
    "couldn't find online",
    "look them up online",
    "not online",
    "no online",
    "online presence",
    "google them",
    "google you",
    "internet",
    "social media page",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def lead_rating_label(rating):
    if rating >= 4.7: return "top-rated"
    if rating >= 4.3: return "highly rated"
    if rating >= 3.8: return "well-reviewed"
    return "established"


def find_review_signals(reviews):
    """
    Scan up to 5 Google reviews for mentions of no online presence.
    Returns (flag: bool, snippet: str | None).
    """
    if not reviews:
        return False, None
    for review in reviews:
        text = (review.get("text") or {}).get("text") or ""
        text_lower = text.lower()
        for kw in WEBSITE_KEYWORDS:
            if kw in text_lower:
                snippet = text[:150].replace("\n", " ").strip()
                if len(text) > 150:
                    snippet += "..."
                return True, snippet
    return False, None


def extract_best_call_time(hours_data, category):
    """Returns (hours_summary, best_call_tip)."""
    if category in FOOD_CATEGORIES:
        tip = "Call 2–4 PM (avoid lunch rush 11:30 AM–1:30 PM)"
    elif category in SOCIAL_MEDIA_CATEGORIES:
        tip = "Call Tue–Thu 10–11:30 AM (many closed Mondays)"
    elif category in TRADE_CATEGORIES:
        tip = "Call 8–10 AM (tradespeople start early, slow before first job)"
    else:
        tip = "Call 10–11:30 AM or 2–4 PM weekdays"

    if not hours_data:
        return "Hours unavailable", tip

    descriptions = hours_data.get("weekdayDescriptions", [])
    # Tuesday (index 1) is a reliable typical-weekday proxy.
    tuesday = descriptions[1] if len(descriptions) > 1 else (descriptions[0] if descriptions else None)
    return tuesday or "Hours unavailable", tip


def predict_objection(lead):
    reviews  = lead["reviews"]
    category = lead["category"]

    if reviews >= 150:
        return (
            "Word of mouth comfort",
            "\"A site makes referrals faster — instead of describing your shop, "
            "people just send your link.\""
        )
    if category in SOCIAL_MEDIA_CATEGORIES:
        return (
            "Using social media instead",
            "\"Social media gets likes — a website gets customers. "
            "You own your website forever; Instagram can change anytime.\""
        )
    if category in FOOD_CATEGORIES:
        return (
            "Too busy / no time",
            "\"You don't touch anything — we build it, you just approve how it looks. "
            "Takes 20 minutes of your time total.\""
        )
    if category in TRADE_CATEGORIES:
        return (
            "Doesn't see the ROI",
            "\"Most of our clients get their first new customer from the site within a month. "
            "People Google trades constantly — if you're not there, your competitor gets that call.\""
        )
    return (
        "Tech-averse / not sure how it works",
        "\"We handle everything — design, setup, all of it. "
        "You just tell us what you want and we make it happen.\""
    )


def extract_city(address):
    parts = [p.strip() for p in address.split(",")]
    return parts[1] if len(parts) >= 3 else "Unknown"


def save_csv(leads, path):
    """Save full lead list to a CSV call sheet."""
    fieldnames = [
        "rank", "name", "category", "rating", "reviews",
        "phone", "address", "summary", "hours", "best_call_time",
        "objection", "pitch_angle", "review_flag", "review_snippet",
        "maps_link", "instagram_search", "facebook_search",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, lead in enumerate(leads, 1):
            objection, angle = predict_objection(lead)
            city  = extract_city(lead["address"])
            query = quote_plus(f'"{lead["name"]}" {city}')
            writer.writerow({
                "rank":             i,
                "name":             lead["name"],
                "category":         lead["category"],
                "rating":           lead["rating"],
                "reviews":          lead["reviews"],
                "phone":            lead["phone"],
                "address":          lead["address"],
                "summary":          lead["summary"],
                "hours":            lead["hours"],
                "best_call_time":   lead["best_call_tip"],
                "objection":        objection,
                "pitch_angle":      angle,
                "review_flag":      "YES — review mentions online presence" if lead["review_flag"] else "",
                "review_snippet":   lead["review_snippet"] or "",
                "maps_link":        lead["maps_link"],
                "instagram_search": f"https://google.com/search?q={query}+instagram",
                "facebook_search":  f"https://google.com/search?q={query}+facebook",
            })


# ── API ───────────────────────────────────────────────────────────────────────

def search(query):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": ",".join([
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.rating",
            "places.userRatingCount",
            "places.websiteUri",
            "places.nationalPhoneNumber",
            "places.businessStatus",
            "places.location",
            "places.editorialSummary",
            "places.regularOpeningHours",
            "places.reviews",
        ]),
    }
    body = {"textQuery": query, "pageSize": 20}
    results = []
    for _ in range(3):
        r = requests.post(ENDPOINT, headers=headers, json=body, timeout=30)
        if r.status_code != 200:
            print(f"  ! API error {r.status_code}: {r.text[:200]}", file=sys.stderr)
            return results
        data = r.json()
        results.extend(data.get("places", []))
        token = data.get("nextPageToken")
        if not token:
            break
        body = {"textQuery": query, "pageSize": 20, "pageToken": token}
        time.sleep(2)
    return results


# ── Heatmap ───────────────────────────────────────────────────────────────────

def build_heatmap(leads, out_path):
    try:
        import folium
        from folium.plugins import HeatMap
    except ImportError:
        print("\n(folium not installed — run: pip install folium)", file=sys.stderr)
        return False
    if not leads:
        return False

    avg_lat = sum(l["lat"] for l in leads) / len(leads)
    avg_lng = sum(l["lng"] for l in leads) / len(leads)

    m = folium.Map(location=[avg_lat, avg_lng], zoom_start=10, tiles="cartodbpositron")
    HeatMap([[l["lat"], l["lng"]] for l in leads], radius=25, blur=20).add_to(m)

    for lead in leads:
        objection, angle = predict_objection(lead)
        review_line = (
            f"<br>⚠️ <b>Review flag:</b> \"{lead['review_snippet']}\""
            if lead["review_flag"] and lead["review_snippet"] else ""
        )
        popup_html = (
            f"<b>{lead['name']}</b><br>"
            f"{lead['rating']}★ ({lead['reviews']} reviews)<br>"
            f"{lead['phone']}<br>"
            f"{lead['address']}<br>"
            f"<i>{lead['summary']}</i><br><br>"
            f"🕐 {lead['hours']}<br>"
            f"📞 {lead['best_call_tip']}<br><br>"
            f"<i>Objection: {objection}</i><br>"
            f"<b>Pitch:</b> {angle}"
            f"{review_line}"
        )
        tooltip_text = (
            f"{lead['name']}\n"
            f"{lead['rating']}★ ({lead['reviews']} reviews)\n"
            f"{lead['phone']}\n"
            f"{lead['summary']}"
        )
        folium.CircleMarker(
            location=[lead["lat"], lead["lng"]],
            radius=4, color="#cc0000", fill=True, fill_opacity=0.7,
            tooltip=folium.Tooltip(tooltip_text, sticky=True),
            popup=folium.Popup(popup_html, max_width=320),
        ).add_to(m)

    m.save(out_path)
    return True


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: set GOOGLE_PLACES_API_KEY in your environment.", file=sys.stderr)
        sys.exit(1)

    leads = {}
    done  = 0
    stop  = False

    for city in CITIES:
        if stop:
            break
        for category in CATEGORIES:
            done += 1
            query = f"{category} in {city}"
            print(f"[{done}/{MAX_QUERIES}] {query} (have {len(leads)} leads so far)", file=sys.stderr)
            for p in search(query):
                if p.get("websiteUri"):
                    continue
                if p.get("businessStatus") and p["businessStatus"] != "OPERATIONAL":
                    continue
                rating  = p.get("rating", 0) or 0
                reviews = p.get("userRatingCount", 0) or 0
                if rating < MIN_RATING or reviews < MIN_REVIEWS:
                    continue
                loc = p.get("location") or {}
                if not loc.get("latitude") or not loc.get("longitude"):
                    continue

                hours_data = p.get("regularOpeningHours") or {}
                hours, best_call_tip = extract_best_call_time(hours_data, category)

                review_flag, review_snippet = find_review_signals(p.get("reviews") or [])

                summary = (
                    (p.get("editorialSummary") or {}).get("text")
                    or f"A {lead_rating_label(rating)} {category} with {reviews}+ customer reviews."
                )

                place_id  = p.get("id", "")
                maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

                leads[place_id] = {
                    "name":           p.get("displayName", {}).get("text", "?"),
                    "address":        p.get("formattedAddress", "?"),
                    "phone":          p.get("nationalPhoneNumber", "—"),
                    "rating":         rating,
                    "reviews":        reviews,
                    "category":       category,
                    "summary":        summary,
                    "hours":          hours,
                    "best_call_tip":  best_call_tip,
                    "review_flag":    review_flag,
                    "review_snippet": review_snippet,
                    "maps_link":      maps_link,
                    "lat":            loc["latitude"],
                    "lng":            loc["longitude"],
                }

            if done >= MAX_QUERIES or len(leads) >= CANDIDATE_POOL:
                stop = True
                break

    all_leads = sorted(leads.values(), key=lambda x: (x["reviews"], x["rating"]), reverse=True)
    top = all_leads[:TARGET_LEADS]

    # ── Terminal output ───────────────────────────────────────────────────────
    print(f"\n{'=' * 80}")
    print(f"TOP {len(top)} LEADS  (no website · >={MIN_RATING}★ · >={MIN_REVIEWS} reviews)")
    print(f"{'=' * 80}\n")

    for i, lead in enumerate(top, 1):
        objection, angle = predict_objection(lead)
        city  = extract_city(lead["address"])
        query = quote_plus(f'"{lead["name"]}" {city}')

        print(f"{i}. {lead['name']}  [{lead['category']}]")
        print(f"   Rating   : {lead['rating']}  |  Reviews: {lead['reviews']}")
        print(f"   Phone    : {lead['phone']}")
        print(f"   Address  : {lead['address']}")
        print(f"   About    : {lead['summary']}")
        print(f"   Hours    : {lead['hours']}")
        print(f"   Best time: {lead['best_call_tip']}")
        print(f"   Objection: {objection}")
        print(f"   Pitch    : {angle}")
        if lead["review_flag"]:
            print(f"   Review   : ⚠️  \"{lead['review_snippet']}\"")
        else:
            print(f"   Review   : None found")
        print(f"   Maps     : {lead['maps_link']}")
        print(f"   Instagram: https://google.com/search?q={query}+instagram")
        print(f"   Facebook : https://google.com/search?q={query}+facebook")
        print()

    # ── Hot zones ─────────────────────────────────────────────────────────────
    city_counts = Counter(extract_city(l["address"]) for l in all_leads)
    print(f"{'=' * 80}")
    print(f"HOT ZONES  (out of {len(all_leads)} total leads)")
    print(f"{'=' * 80}\n")
    for c, count in city_counts.most_common():
        print(f"  {c:<25} {'█' * count} {count}")
    print()

    # ── CSV export ────────────────────────────────────────────────────────────
    csv_path = os.path.abspath("leads.csv")
    save_csv(all_leads, csv_path)
    print(f"Call sheet saved: {csv_path}")
    print("(Open in Excel or Google Sheets to track calls, notes, and follow-ups)\n")

    # ── Heatmap ───────────────────────────────────────────────────────────────
    map_path = os.path.abspath("leads_map.html")
    if build_heatmap(all_leads, map_path):
        print(f"Visual heatmap: {map_path}")
        webbrowser.open(f"file://{map_path}")


if __name__ == "__main__":
    main()
