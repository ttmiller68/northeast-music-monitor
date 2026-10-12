import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_KEY = os.environ["JAMBASE_API_KEY"]
API_URL = "https://api.data.jambase.com/v3/events"

# Capital Region: approximately 60 miles around Schenectady
LATITUDE = 42.6526
LONGITUDE = -73.7562
RADIUS_MILES = 60

today = datetime.now(timezone.utc).date()
end_date = today + timedelta(days=90)

all_events = []

for page in range(1, 5):
    params = {
        "geoLatitude": LATITUDE,
        "geoLongitude": LONGITUDE,
        "geoRadiusAmount": RADIUS_MILES,
        "geoRadiusUnits": "mi",
        "eventDateFrom": today.isoformat(),
        "eventDateTo": end_date.isoformat(),
        "page": page,
        "perPage": 40
    }

    url = API_URL + "?" + urllib.parse.urlencode(params)

    request = urllib.request.Request(
        url,
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Accept": "application/json",
            "User-Agent": "NortheastMusicMonitor/1.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)

    if not data.get("success"):
        raise RuntimeError("JamBase did not return a successful response")

    events = data.get("events", [])
    all_events.extend(events)

    if len(events) < 40:
        break

def simplify(event):
    venue = event.get("location") or {}
    performers = event.get("performer") or []

    artist_names = [
        artist.get("name", "")
        for artist in performers
        if isinstance(artist, dict)
    ]

    return {
        "title": event.get("name", "Concert"),
        "artists": artist_names,
        "venue": venue.get("name", "Venue TBA"),
        "date": event.get("startDate", ""),
        "announced": event.get("datePublished", ""),
        "url": event.get("url", ""),
        "id": event.get("identifier", "")
    }

concerts = [
    simplify(event)
    for event in all_events
    if event.get("startDate")
    and event.get("eventStatus", "").lower() != "cancelled"
]

# Remove duplicate event listings
unique = {}
for concert in concerts:
    key = concert["id"] or (
        concert["title"] + concert["date"]
    )
    unique[key] = concert

concerts = list(unique.values())

# Shows happening soonest
upcoming = sorted(
    concerts,
    key=lambda event: event["date"]
)[:40]

# Most recently published listings
recent = sorted(
    concerts,
    key=lambda event: event["announced"],
    reverse=True
)[:40]

output = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "upcoming": upcoming,
    "recent": recent
}

with open("concerts.json", "w", encoding="utf-8") as file:
    json.dump(output, file, indent=2, ensure_ascii=False)

print(f"Retrieved {len(concerts)} unique concerts")
print(f"Upcoming: {len(upcoming)}")
print(f"Recently published: {len(recent)}")
