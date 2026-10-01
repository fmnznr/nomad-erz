#!/usr/bin/env python3
"""Baut die Offline-Wissensdatenbank aus content/*.md.

Ausgabe in dist/:
  html/                    – statische HTML-Seiten (im Browser nutzbar)
  gpx/                     – Kartenpunkte für Organic Maps / OsmAnd (falls data/osm/pois.json existiert)
  nomad-erzgebirge.zim     – Datei für die Kiwix-App (iPhone, Android, PC)

Aufruf:  python3 scripts/build_zim.py [--no-zim]
"""
import argparse
import html
import json
import math
import re
import shutil
import struct
import zlib
from datetime import date
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
POIS = ROOT / "data" / "osm" / "pois.json"
ZIM_NAME = "nomad-erzgebirge.zim"

TITLE = "NOMAD Erzgebirge"
DESCRIPTION = "Offline-Wissen für Zwönitz & Erzgebirgskreis: Natur, Notfall, Karten"

CATEGORIES = {
    "krankenhaus": ("🏥", "Krankenhäuser", "Umkreis 35 km um Zwönitz. Ob es eine 24-h-Notaufnahme gibt, vorab prüfen!"),
    "apotheke": ("💊", "Apotheken", "Notdienst: 0800 00 22 8 33 (Festnetz) bzw. 22 8 33 (Handy)."),
    "defibrillator": ("❤️", "Defibrillatoren (AED)", "Zugänglichkeit (Öffnungszeiten, innen/außen) vor Ort prüfen. Gerät einschalten – es sagt jeden Schritt an."),
    "feuerwehr": ("🚒", "Feuerwehren", "Gerätehäuser sind oft Anlaufstellen bei Großschadenslagen und Stromausfall."),
    "polizei": ("🚓", "Polizei", "Notruf immer 110."),
    "schutzhuette": ("🛖", "Schutzhütten", "Unterstand bei Regen und Gewitter. Bei Gewitter jedoch nicht auf Kuppen."),
    "quelle": ("💧", "Quellen", "Nicht amtlich überwacht – Wasser im Zweifel aufbereiten. Keine Stollen- oder Haldenwässer trinken!"),
    "trinkwasser": ("🚰", "Trinkwasserstellen", "Brunnen und Zapfstellen laut OpenStreetMap. Saisonal oder abgestellt möglich."),
    "gipfel": ("⛰️", "Gipfel & Berge", "Mit Höhenangabe, falls in OSM vorhanden."),
}

SINGULAR = {
    "krankenhaus": "Krankenhaus", "apotheke": "Apotheke", "defibrillator": "Defibrillator",
    "feuerwehr": "Feuerwehr", "polizei": "Polizei", "schutzhuette": "Schutzhütte",
    "quelle": "Quelle", "trinkwasser": "Trinkwasserstelle", "gipfel": "Gipfel",
}

MD_EXTENSIONS = ["tables", "toc", "admonition", "attr_list", "sane_lists", "fenced_code"]


# ---------------------------------------------------------------- Hilfsfunktionen

def rel_prefix(path: str) -> str:
    """'natur/pilze.html' -> '../'"""
    return "../" * path.count("/")


def fix_links(body: str) -> str:
    """Interne .md-Links auf .html umbiegen."""
    return re.sub(r'href="([^":#]+)\.md(#[^"]*)?"', lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', body)


def page(path: str, title: str, body: str, crumbs: list[tuple[str, str]]) -> str:
    pre = rel_prefix(path)
    nav = " › ".join(
        [f'<a href="{pre}index.html">Start</a>'] + [f'<a href="{pre}{href}">{html.escape(t)}</a>' for href, t in crumbs]
    )
    if path == "index.html":
        nav = ""
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{pre}style.css">
</head>
<body>
<header><a class="brand" href="{pre}index.html">⛰️ {TITLE}</a><a class="sos" href="{pre}notfall/notrufe.html">SOS 112</a></header>
<nav class="crumbs">{nav}</nav>
<main>
{body}
</main>
<footer>Stand: {date.today().isoformat()} · Angaben ohne Gewähr · <a href="{pre}hinweise.html">Hinweise &amp; Quellen</a></footer>
</body>
</html>
"""


SECTION_TITLES = {"natur": "Natur", "notfall": "Notfall", "geografie": "Geografie"}


def crumbs_for(path: str) -> list[tuple[str, str]]:
    parts = path.split("/")
    if len(parts) > 1 and parts[-1] != "index.html":
        return [(f"{parts[0]}/index.html", SECTION_TITLES.get(parts[0], parts[0]))]
    return []


def render_md(text: str) -> tuple[str, str]:
    md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs={"toc": {"permalink": False}})
    body = fix_links(md.convert(text))
    m = re.search(r"^#\s+(.+)$", text, re.M)
    title = m.group(1).strip() if m else "Ohne Titel"
    return title, body


def haversine_km(a, b) -> float:
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def bearing(a, b) -> str:
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    x = math.sin(lo2 - lo1) * math.cos(la2)
    y = math.cos(la1) * math.sin(la2) - math.sin(la1) * math.cos(la2) * math.cos(lo2 - lo1)
    deg = (math.degrees(math.atan2(x, y)) + 360) % 360
    return ["N", "NO", "O", "SO", "S", "SW", "W", "NW"][int((deg + 22.5) // 45) % 8]


def poi_name(p: dict) -> str:
    t = p["tags"]
    if t.get("name"):
        return t["name"]
    return f"{SINGULAR[p['cat']]} (ohne Name)"


def poi_details(p: dict) -> str:
    t = p["tags"]
    bits = []
    addr = " ".join(x for x in [t.get("addr:street"), t.get("addr:housenumber")] if x)
    city = " ".join(x for x in [t.get("addr:postcode"), t.get("addr:city")] if x)
    if addr or city:
        bits.append(", ".join(x for x in [addr, city] if x))
    if t.get("ele"):
        bits.append(f"{t['ele']} m")
    if t.get("defibrillator:location"):
        bits.append(t["defibrillator:location"])
    if t.get("indoor") == "yes":
        bits.append("innen")
    if t.get("opening_hours"):
        bits.append(f"Öffnungszeiten: {t['opening_hours']}")
    phone = t.get("phone") or t.get("contact:phone")
    if phone:
        bits.append(f"☎ {phone}")
    if t.get("drinking_water") == "no":
        bits.append("⚠️ laut OSM kein Trinkwasser")
    if t.get("shelter_type"):
        bits.append(t["shelter_type"].replace("_", " "))
    return " · ".join(html.escape(b) for b in bits)


def gpx(points: list[dict], name: str) -> str:
    wpts = []
    for p in points:
        n = html.escape(poi_name(p))
        desc = poi_details(p)
        wpts.append(
            f'  <wpt lat="{p["lat"]}" lon="{p["lon"]}"><name>{n}</name>'
            f"<desc>{desc}</desc><type>{html.escape(CATEGORIES[p['cat']][1])}</type></wpt>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<gpx version="1.1" creator="nomad-erz" xmlns="http://www.topografix.com/GPX/1/1">\n'
        f"  <metadata><name>{html.escape(name)}</name><copyright author=\"OpenStreetMap-Mitwirkende\">"
        "<license>https://opendatacommons.org/licenses/odbl/</license></copyright></metadata>\n"
        + "\n".join(wpts)
        + "\n</gpx>\n"
    )


# ---------------------------------------------------------------- Kartenpunkte

def build_poi_pages(pages: dict, files: dict) -> None:
    """Erzeugt geografie/kartenpunkte.html (+ Unterseiten) und GPX-Dateien."""
    crumbs = [("geografie/index.html", "Geografie")]
    if not POIS.exists():
        body = render_md(
            "# Kartenpunkte\n\n!!! info \"Noch keine Daten\"\n"
            "    Die Kartenpunkte werden mit `python3 scripts/fetch_osm.py` aus OpenStreetMap geladen "
            "(passiert automatisch im GitHub-Build). Danach die Datenbank neu bauen.\n"
        )[1]
        pages["geografie/kartenpunkte.html"] = ("Kartenpunkte", body, crumbs)
        return

    data = json.loads(POIS.read_text(encoding="utf-8"))
    home = tuple(data.get("home", (50.63, 12.81)))
    by_cat: dict[str, list] = {c: [] for c in CATEGORIES}
    for p in data["pois"]:
        if p["cat"] in by_cat:
            p["dist"] = haversine_km(home, (p["lat"], p["lon"]))
            by_cat[p["cat"]].append(p)

    rows = []
    all_points = []
    for cat, (icon, label, hint) in CATEGORIES.items():
        pts = sorted(by_cat[cat], key=lambda p: p["dist"])
        all_points += pts
        if not pts:
            continue
        rows.append(f'<li><a href="kartenpunkte/{cat}.html">{icon} {label}</a> <span class="muted">({len(pts)})</span>'
                    f' · <a href="../gpx/{cat}.gpx">GPX</a></li>')
        trs = []
        for p in pts:
            trs.append(
                "<tr>"
                f"<td>{p['dist']:.1f} km {bearing(home, (p['lat'], p['lon']))}</td>"
                f"<td><strong>{html.escape(poi_name(p))}</strong><br><span class=\"muted\">{poi_details(p)}</span></td>"
                f"<td class=\"coord\">{p['lat']:.5f}, {p['lon']:.5f}</td>"
                "</tr>"
            )
        body = (
            f"<h1>{icon} {label}</h1>\n<p>{html.escape(hint)}</p>\n"
            f"<p class=\"muted\">Sortiert nach Entfernung (Luftlinie) von Zwönitz-Zentrum. "
            f"Koordinaten in Organic Maps ins Suchfeld eingeben. "
            f"Datenstand OSM: {html.escape(data.get('fetched', '?'))}.</p>\n"
            f"<p><a href=\"../../gpx/{cat}.gpx\">GPX-Datei für Organic Maps</a></p>\n"
            "<div class=\"table\"><table><thead><tr><th>Entfernung</th><th>Name</th><th>Koordinaten</th></tr></thead>"
            f"<tbody>{''.join(trs)}</tbody></table></div>"
        )
        pages[f"geografie/kartenpunkte/{cat}.html"] = (label, body, crumbs + [("geografie/kartenpunkte.html", "Kartenpunkte")])
        files[f"gpx/{cat}.gpx"] = gpx(pts, f"NOMAD Erzgebirge – {label}").encode()

    files["gpx/alle.gpx"] = gpx(all_points, "NOMAD Erzgebirge – alle Punkte").encode()
    body = (
        "<h1>Kartenpunkte aus OpenStreetMap</h1>\n"
        "<p>Wichtige Orte im Erzgebirgskreis (Krankenhäuser im Umkreis von 35 km). "
        f"Datenstand: {html.escape(data.get('fetched', '?'))} · © OpenStreetMap-Mitwirkende (ODbL).</p>\n"
        f"<ul class=\"cards\">{''.join(rows)}</ul>\n"
        "<p><a href=\"../gpx/alle.gpx\">Alle Punkte als eine GPX-Datei</a> – Import in Organic Maps: "
        "<a href=\"karten.html\">Anleitung</a>.</p>\n"
        "<p class=\"muted\">OSM-Daten sind von Freiwilligen erfasst und können unvollständig oder veraltet sein.</p>"
    )
    pages["geografie/kartenpunkte.html"] = ("Kartenpunkte", body, crumbs)


# ---------------------------------------------------------------- Illustration (48x48 PNG, ohne Pillow)

def illustration_png(size: int = 48) -> bytes:
    bg, fg, snow = (34, 94, 60), (235, 240, 235), (255, 255, 255)
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            c = bg
            # zwei Berge
            if y > size * 0.30 + abs(x - size * 0.38) * 1.1 and y < size * 0.85:
                c = fg
            if y > size * 0.45 + abs(x - size * 0.70) * 1.0 and y < size * 0.85:
                c = fg
            if y > size * 0.30 + abs(x - size * 0.38) * 1.1 and y < size * 0.42:
                c = snow
            row += bytes(c)
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


# ---------------------------------------------------------------- ZIM

def write_zim(pages: dict, files: dict, out: Path) -> None:
    from libzim.writer import Creator, Hint, Item, StringProvider

    class Entry(Item):
        def __init__(self, path, title, mimetype, content: bytes, front=False):
            super().__init__()
            self._p, self._t, self._m, self._c, self._f = path, title, mimetype, content, front

        def get_path(self): return self._p
        def get_title(self): return self._t
        def get_mimetype(self): return self._m
        def get_contentprovider(self): return StringProvider(self._c)
        def get_hints(self): return {Hint.FRONT_ARTICLE: self._f, Hint.COMPRESS: True}

    if out.exists():
        out.unlink()
    with Creator(str(out)).config_indexing(True, "deu") as c:
        c.set_mainpath("index.html")
        c.add_illustration(48, illustration_png())
        meta = {
            "Name": "nomad-erzgebirge_de",
            "Title": TITLE,
            "Description": DESCRIPTION[:80],
            "LongDescription": "Regionale Offline-Wissensdatenbank nach dem Vorbild von Project NOMAD: Flora, Fauna, "
                               "Pilze, Erste Hilfe, Krisenvorsorge, Wettergefahren, Geografie und Kartenpunkte für "
                               "Zwönitz und den Erzgebirgskreis.",
            "Language": "deu",
            "Creator": "nomad-erz",
            "Publisher": "nomad-erz",
            "Date": date.today().isoformat(),
            "Tags": "_category:other;_pictures:no;_videos:no;_details:yes;erzgebirge;sachsen;survival",
        }
        for k, v in meta.items():
            c.add_metadata(k, v)
        for path, (title, html_doc) in pages.items():
            c.add_item(Entry(path, title, "text/html", html_doc.encode("utf-8"), front=True))
        for path, content in files.items():
            mime = {"css": "text/css", "gpx": "application/gpx+xml"}.get(path.rsplit(".", 1)[-1], "application/octet-stream")
            c.add_item(Entry(path, path, mime, content))


# ---------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-zim", action="store_true", help="nur HTML/GPX erzeugen")
    args = ap.parse_args()

    raw_pages: dict[str, tuple[str, str, list]] = {}
    for md_file in sorted(CONTENT.rglob("*.md")):
        rel = md_file.relative_to(CONTENT).with_suffix(".html").as_posix()
        title, body = render_md(md_file.read_text(encoding="utf-8"))
        raw_pages[rel] = (title, body, crumbs_for(rel))

    files: dict[str, bytes] = {"style.css": (ROOT / "scripts" / "style.css").read_bytes()}
    build_poi_pages(raw_pages, files)

    pages = {p: (t, page(p, t, b, cr)) for p, (t, b, cr) in raw_pages.items()}

    # Linkprüfung
    broken = []
    for p, (_, doc) in pages.items():
        base = Path(p).parent
        for href in re.findall(r'href="([^"#:]+)(?:#[^"]*)?"', doc):
            target = (base / href).as_posix()
            norm = Path(*[x for x in Path(target).parts]).as_posix()
            # ../ auflösen
            stack = []
            for part in norm.split("/"):
                if part == "..":
                    stack and stack.pop()
                elif part not in ("", "."):
                    stack.append(part)
            target = "/".join(stack)
            if target not in pages and target not in files:
                broken.append(f"{p} -> {href}")
    if broken:
        print("⚠️  Kaputte Links:\n  " + "\n  ".join(broken))

    html_dir = DIST / "html"
    if html_dir.exists():
        shutil.rmtree(html_dir)
    for path, (_, doc) in pages.items():
        f = html_dir / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(doc, encoding="utf-8")
    for path, content in files.items():
        f = html_dir / path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(content)
    if any(k.startswith("gpx/") for k in files):
        gdir = DIST / "gpx"
        if gdir.exists():
            shutil.rmtree(gdir)
        shutil.copytree(html_dir / "gpx", gdir)
    print(f"{len(pages)} Seiten → {html_dir.relative_to(ROOT)}")

    if not args.no_zim:
        out = DIST / ZIM_NAME
        write_zim(pages, files, out)
        print(f"ZIM → {out.relative_to(ROOT)} ({out.stat().st_size / 1024:.0f} KB)")

    if broken:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
