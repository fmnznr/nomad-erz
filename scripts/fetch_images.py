#!/usr/bin/env python3
"""Lädt Artbilder (Pflanzen, Pilze, Tiere) von Wikipedia/Wikimedia Commons.

In den Texten steht ein Platzhalter {{bild:Artikeltitel}} (Titel des deutschen
Wikipedia-Artikels). Dieses Skript holt für jeden Titel das Hauptbild des Artikels
als Vorschaubild samt Urheber- und Lizenzangabe.

Ergebnis: data/bilder/<name>.jpg|png und data/bilder/bilder.json
Bereits vorhandene Bilder werden nicht erneut geladen.
Nur Standardbibliothek. Aufruf:  python3 scripts/fetch_images.py
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "data" / "bilder"
META = OUT / "bilder.json"
API = "https://de.wikipedia.org/w/api.php"
WIDTH = 480
# Wikimedia verlangt einen aussagekräftigen User-Agent
UA = {"User-Agent": "nomad-erz/1.0 (https://github.com/fmnznr/nomad-erz; offline knowledge base)"}

MARKER = re.compile(r"\{\{bild:([^}|]+)\}\}")


def slug(title: str) -> str:
    s = title.lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def api(params: dict) -> dict:
    params = {**params, "format": "json", "formatversion": "2"}
    url = f"{API}?{urllib.parse.urlencode(params)}"
    for versuch in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print(f"  API-Fehler ({e}), neuer Versuch …", file=sys.stderr)
            time.sleep(5 * (versuch + 1))
    raise SystemExit("Wikipedia-API nicht erreichbar")


def strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def titles_in_content() -> list[str]:
    found = set()
    for f in CONTENT.rglob("*.md"):
        found.update(t.strip() for t in MARKER.findall(f.read_text(encoding="utf-8")))
    return sorted(found)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    meta: dict = json.loads(META.read_text(encoding="utf-8")) if META.exists() else {}
    wanted = titles_in_content()
    todo = [t for t in wanted if not (t in meta and (OUT / meta[t]["datei"]).exists())]
    print(f"{len(wanted)} Bild-Platzhalter, davon {len(todo)} neu zu laden")

    # 1) Artikeltitel -> Hauptbild (Dateiname)
    files: dict[str, str] = {}
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        res = api({"action": "query", "prop": "pageimages", "piprop": "name",
                   "redirects": "1", "titles": "|".join(batch)})
        q = res.get("query", {})
        mapping = {t: t for t in batch}
        for n in q.get("normalized", []):
            for k, v in mapping.items():
                if v == n["from"]:
                    mapping[k] = n["to"]
        for r in q.get("redirects", []):
            for k, v in mapping.items():
                if v == r["from"]:
                    mapping[k] = r["to"]
        by_title = {p["title"]: p for p in q.get("pages", [])}
        for t in batch:
            p = by_title.get(mapping[t], {})
            if p.get("missing"):
                print(f"  ⚠️  Artikel nicht gefunden: {t}")
            elif not p.get("pageimage"):
                print(f"  ⚠️  Kein Hauptbild im Artikel: {t}")
            else:
                files[t] = p["pageimage"]

    # 2) Dateiname -> Vorschau-URL, Urheber, Lizenz
    infos: dict[str, dict] = {}
    names = sorted(set(files.values()))
    for i in range(0, len(names), 50):
        batch = names[i:i + 50]
        res = api({"action": "query", "prop": "imageinfo", "iiprop": "url|extmetadata",
                   "iiurlwidth": str(WIDTH), "titles": "|".join(f"Datei:{n}" for n in batch)})
        for p in res.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata", {})
            name = p["title"].split(":", 1)[1].replace(" ", "_")
            infos[name] = {
                "thumb": ii.get("thumburl") or ii.get("url"),
                "quelle": ii.get("descriptionurl", ""),
                "urheber": strip_html(em.get("Artist", {}).get("value", "")) or "unbekannt",
                "lizenz": strip_html(em.get("LicenseShortName", {}).get("value", "")) or "siehe Quelle",
                "lizenz_url": em.get("LicenseUrl", {}).get("value", ""),
            }

    # 3) Herunterladen
    ok = 0
    for t, fname in files.items():
        info = infos.get(fname.replace(" ", "_"))
        if not info or not info["thumb"]:
            print(f"  ⚠️  Keine Bildinfo: {t} ({fname})")
            continue
        ext = ".png" if info["thumb"].lower().endswith(".png") else ".jpg"
        datei = slug(t) + ext
        try:
            with urllib.request.urlopen(urllib.request.Request(info["thumb"], headers=UA), timeout=60) as r:
                (OUT / datei).write_bytes(r.read())
        except Exception as e:  # noqa: BLE001
            print(f"  ⚠️  Download fehlgeschlagen: {t}: {e}")
            continue
        meta[t] = {"datei": datei, "commons_datei": fname, **{k: v for k, v in info.items() if k != "thumb"}}
        ok += 1
        time.sleep(0.2)  # schonend für die Server

    # nicht mehr verwendete Einträge entfernen
    for t in list(meta):
        if t not in wanted:
            (OUT / meta[t]["datei"]).unlink(missing_ok=True)
            del meta[t]

    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    print(f"{ok} Bilder neu geladen, {len(meta)} insgesamt in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
