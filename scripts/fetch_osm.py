#!/usr/bin/env python3
"""Lädt wichtige Kartenpunkte für den Erzgebirgskreis aus OpenStreetMap (Overpass API).

Ergebnis: data/osm/pois.json – wird von build_zim.py zu Seiten und GPX-Dateien verarbeitet.
Nur Standardbibliothek, damit es überall (auch in GitHub Actions) läuft.

Aufruf:  python3 scripts/fetch_osm.py
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "osm" / "pois.json"

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

# Zwönitz Zentrum (ca.) – Bezugspunkt für Entfernungen
HOME = (50.6300, 12.8100)
# Krankenhäuser auch außerhalb des Kreises (Chemnitz, Zwickau …)
HOSPITAL_RADIUS_M = 35000

# Kategorie -> (Overpass-Filter, Bereich) ; Bereich "area" = Erzgebirgskreis, "around" = Radius um Zwönitz
CATEGORIES = {
    "krankenhaus": (['["amenity"="hospital"]'], "around"),
    "apotheke": (['["amenity"="pharmacy"]'], "area"),
    "defibrillator": (['["emergency"="defibrillator"]'], "area"),
    "feuerwehr": (['["amenity"="fire_station"]'], "area"),
    "polizei": (['["amenity"="police"]'], "area"),
    "schutzhuette": (['["amenity"="shelter"]', '["tourism"="wilderness_hut"]', '["tourism"="alpine_hut"]'], "area"),
    "quelle": (['["natural"="spring"]'], "area"),
    "trinkwasser": (['["amenity"="drinking_water"]', '["drinking_water"="yes"]["man_made"="water_well"]'], "area"),
    "gipfel": (['["natural"="peak"]["name"]'], "area"),
}

KEEP_TAGS = [
    "name", "operator", "addr:street", "addr:housenumber", "addr:postcode", "addr:city",
    "phone", "contact:phone", "opening_hours", "emergency", "healthcare", "shelter_type",
    "drinking_water", "ele", "defibrillator:location", "access", "indoor", "description",
    "website", "seasonal", "amenity", "tourism", "natural",
]


def build_query() -> str:
    parts = []
    for filters, scope in CATEGORIES.values():
        for f in filters:
            if scope == "area":
                parts.append(f"nwr{f}(area.kreis);")
            else:
                parts.append(f"nwr{f}(around:{HOSPITAL_RADIUS_M},{HOME[0]},{HOME[1]});")
    body = "\n  ".join(parts)
    return (
        "[out:json][timeout:300];\n"
        'area["boundary"="administrative"]["admin_level"="6"]["name"="Erzgebirgskreis"]->.kreis;\n'
        f"(\n  {body}\n);\n"
        "out center tags;\n"
    )


def classify(tags: dict) -> str | None:
    if tags.get("amenity") == "hospital":
        return "krankenhaus"
    if tags.get("amenity") == "pharmacy":
        return "apotheke"
    if tags.get("emergency") == "defibrillator":
        return "defibrillator"
    if tags.get("amenity") == "fire_station":
        return "feuerwehr"
    if tags.get("amenity") == "police":
        return "polizei"
    if tags.get("amenity") == "shelter" or tags.get("tourism") in ("wilderness_hut", "alpine_hut"):
        return "schutzhuette"
    if tags.get("natural") == "spring":
        return "quelle"
    if tags.get("amenity") == "drinking_water" or (
        tags.get("man_made") == "water_well" and tags.get("drinking_water") == "yes"
    ):
        return "trinkwasser"
    if tags.get("natural") == "peak" and tags.get("name"):
        return "gipfel"
    return None


def fetch(query: str) -> dict:
    data = urllib.parse.urlencode({"data": query}).encode()
    last_err = None
    for attempt in range(3):
        for url in ENDPOINTS:
            try:
                req = urllib.request.Request(
                    url, data=data,
                    headers={"User-Agent": "nomad-erz/1.0 (offline knowledge base)"},
                )
                with urllib.request.urlopen(req, timeout=360) as resp:
                    return json.load(resp)
            except Exception as e:  # noqa: BLE001 – nächsten Server probieren
                last_err = e
                print(f"  {url}: {e}", file=sys.stderr)
        time.sleep(10 * (attempt + 1))
    raise SystemExit(f"Overpass nicht erreichbar: {last_err}")


def convert(raw: dict) -> list[dict]:
    pois, seen = [], set()
    for el in raw.get("elements", []):
        tags = el.get("tags", {})
        cat = classify(tags)
        if not cat:
            continue
        if "lat" in el:
            lat, lon = el["lat"], el["lon"]
        elif "center" in el:
            lat, lon = el["center"]["lat"], el["center"]["lon"]
        else:
            continue
        key = (el["type"], el["id"])
        if key in seen:
            continue
        seen.add(key)
        pois.append({
            "cat": cat,
            "osm": f"{el['type']}/{el['id']}",
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "tags": {k: v for k, v in tags.items() if k in KEEP_TAGS},
        })
    pois.sort(key=lambda p: (p["cat"], p["osm"]))
    return pois


def main() -> None:
    query = build_query()
    print("Frage Overpass API ab …")
    raw = fetch(query)
    pois = convert(raw)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": "© OpenStreetMap-Mitwirkende, ODbL",
        "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "home": HOME,
        "pois": pois,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    counts = {}
    for p in pois:
        counts[p["cat"]] = counts.get(p["cat"], 0) + 1
    print(f"{len(pois)} Punkte gespeichert in {OUT.relative_to(ROOT)}: {counts}")


if __name__ == "__main__":
    main()
