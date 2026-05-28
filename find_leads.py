import os
import sys
import time
import requests

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")
ENDPOINT = "https://places.googleapis.com/v1/places:searchText"

MIN_RATING = 3.5
MIN_REVIEWS = 10

# South Florida coverage — Miami-Dade, Broward, Palm Beach.
CITIES = [
    "Miami FL", "Hialeah FL", "Miami Beach FL", "Coral Gables FL", "Homestead FL",
    "Fort Lauderdale FL", "Hollywood FL", "Pembroke Pines FL", "Pompano Beach FL",
    "Coral Springs FL", "Miramar FL", "Boca Raton FL", "Delray Beach FL",
    "West Palm Beach FL", "Boynton Beach FL",
]

# Business types — local service businesses are the best targets (high ticket,
# website matters for trust, owner-operated so decisions are fast).
CATEGORIES = [
    "plumber", "electrician", "roofer", "landscaper", "auto repair shop",
    "hair salon", "barber shop", "nail salon", "tattoo shop",
    "restaurant", "bakery", "coffee shop",
    "dentist", "chiropractor", "veterinarian",
    "tow truck", "moving company", "junk removal", "pool cleaning",
    "hvac contractor", "pest control", "house cleaning",
]


def search(query):
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        # Field mask = pay only for the fields we ask for.
        "X-Goog-FieldMask": ",".join([
            "places.id",
            "places.displayName",
            "places.formattedAddress",
            "places.rating",
            "places.userRatingCount",
            "places.websiteUri",
            "places.nationalPhoneNumber",
            "places.businessStatus",
        ]),
    }
    body = {"textQuery": query, "pageSize": 20}
    results = []
    for _ in range(3):  # up to 60 results (3 pages of 20)
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
        time.sleep(2)  # next-page tokens need a moment to activate
    return results


def main():
    if not API_KEY:
        print("ERROR: set GOOGLE_PLACES_API_KEY in your environment.", file=sys.stderr)
        sys.exit(1)

    leads = {}
    total_queries = len(CITIES) * len(CATEGORIES)
    done = 0
    for city in CITIES:
        for category in CATEGORIES:
            done += 1
            query = f"{category} in {city}"
            print(f"[{done}/{total_queries}] {query}", file=sys.stderr)
            for p in search(query):
                if p.get("websiteUri"):
                    continue
                if p.get("businessStatus") and p["businessStatus"] != "OPERATIONAL":
                    continue
                rating = p.get("rating", 0) or 0
                reviews = p.get("userRatingCount", 0) or 0
                if rating < MIN_RATING or reviews < MIN_REVIEWS:
                    continue
                leads[p["id"]] = {
                    "name": p.get("displayName", {}).get("text", "?"),
                    "address": p.get("formattedAddress", "?"),
                    "phone": p.get("nationalPhoneNumber", "—"),
                    "rating": rating,
                    "reviews": reviews,
                    "category": category,
                }

    ranked = sorted(leads.values(), key=lambda x: (x["reviews"], x["rating"]), reverse=True)

    print(f"\n{'=' * 80}")
    print(f"FOUND {len(ranked)} LEADS (no website, >={MIN_RATING}★, >={MIN_REVIEWS} reviews)")
    print(f"{'=' * 80}\n")
    for i, lead in enumerate(ranked, 1):
        print(f"{i}. {lead['name']}  [{lead['category']}]")
        print(f"   {lead['rating']}★  ({lead['reviews']} reviews)")
        print(f"   {lead['phone']}")
        print(f"   {lead['address']}")
        print()


if __name__ == "__main__":
    main()