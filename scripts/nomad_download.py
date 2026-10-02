#!/usr/bin/env python3
"""Lädt alle Offline-Pakete für das NOMAD-iPhone auf einen Mac/PC – in einem Rutsch.

  * eigene Datenbank (nomad-erzgebirge.zim) + Kartenpunkte (GPX)
      – mit privat/-Ordner: wird lokal mit deinen privaten Angaben gebaut
      – sonst: aktuelles GitHub-Release
  * Kiwix-Pakete (Wikipedia DE ohne Bilder usw.) jeweils in der neuesten Version

Danach die Dateien per Finder (Mac) bzw. „Apple Geräte“/iTunes (Windows) aufs iPhone
übertragen – siehe LIESMICH.txt im Zielordner.

Nur Python-Standardbibliothek (Python ≥ 3.10). Abgebrochene Downloads werden fortgesetzt,
alte Versionen nach erfolgreichem Download gelöscht.

Beispiele:
  python3 scripts/nomad_download.py                      # Profil „basis“ nach ~/NOMAD-iPhone
  python3 scripts/nomad_download.py --profil erweitert
  python3 scripts/nomad_download.py --nur-anzeigen       # nur zeigen, was geladen würde
  python3 scripts/nomad_download.py --ziel D:\\NOMAD --pruefen
"""
import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "fmnznr/nomad-erz"
RELEASE = f"https://github.com/{REPO}/releases/latest/download"
KIWIX_CATALOG = "https://library.kiwix.org/catalog/v2/entries"
KIWIX_DOWNLOAD = "https://download.kiwix.org/zim"
UA = {"User-Agent": "nomad-erz-downloader/1.0"}


@dataclass
class Paket:
    titel: str
    ordner: str          # Unterordner auf download.kiwix.org/zim/
    praefixe: list[str]  # Dateinamen-Präfixe in Wunschreihenfolge (ohne _YYYY-MM.zim)
    profile: set[str]


PAKETE = [
    Paket("Wikipedia DE (nur Einleitungen)", "wikipedia", ["wikipedia_de_all_mini"], {"minimal"}),
    Paket("Wikipedia DE (ohne Bilder)", "wikipedia", ["wikipedia_de_all_nopic"], {"basis", "erweitert"}),
    Paket("Wikivoyage DE", "wikivoyage", ["wikivoyage_de_all_maxi", "wikivoyage_de_all_nopic"], {"basis", "erweitert"}),
    Paket("Wikibooks DE", "wikibooks", ["wikibooks_de_all_nopic", "wikibooks_de_all_maxi"], {"erweitert"}),
    Paket("Wiktionary DE", "wiktionary", ["wiktionary_de_all_nopic", "wiktionary_de_all_maxi"], {"erweitert"}),
    Paket("iFixit (EN, Reparatur)", "ifixit", ["ifixit_en_all"], {"erweitert"}),
    Paket("Post-Disaster (EN)", "other", ["zimgit-post-disaster_en"], {"erweitert"}),
    Paket("Water (EN)", "other", ["zimgit-water_en"], {"erweitert"}),
    Paket("Medicine (EN)", "other", ["zimgit-medicine_en"], {"erweitert"}),
    Paket("Food Preparation (EN)", "other", ["zimgit-food-preparation_en"], {"erweitert"}),
]

LIESMICH = """NOMAD Erzgebirge – Dateien aufs iPhone übertragen
==================================================

kiwix/   → in die App Kiwix
karten/  → in die App Organic Maps (GPX-Kartenpunkte)

MAC (Finder):
  1. iPhone per Kabel verbinden, im Finder links auswählen, Reiter „Dateien“.
  2. Alle .zim-Dateien aus kiwix/ auf den Eintrag „Kiwix“ ziehen.
  3. Kiwix auf dem iPhone öffnen – die Bücher erscheinen in der Bibliothek
     (falls nicht: Bibliothek → Öffnen → Datei auswählen).

WINDOWS („Apple Geräte“-App oder iTunes):
  1. iPhone per Kabel verbinden, Gerät auswählen → „Dateien“ / „Dateifreigabe“.
  2. „Kiwix“ wählen → „Datei hinzufügen“ → .zim-Dateien aus kiwix/ auswählen.

ALTERNATIVE ohne Kabel (gut für kleine Dateien):
  AirDrop (Mac) oder iCloud Drive → auf dem iPhone „In Dateien sichern“ →
  Datei antippen → Teilen → Kiwix bzw. Organic Maps.

GPX-Kartenpunkte: karten/alle.gpx aufs iPhone (AirDrop/iCloud/Mail) → antippen →
Teilen → Organic Maps. Vorher die alte Liste in Organic Maps löschen (sonst doppelt).

Alte Versionen in Kiwix danach löschen: Bibliothek → Buch → Löschen.
"""


# ---------------------------------------------------------------- Netzwerk

def http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def remote_size(url: str) -> int | None:
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=60) as r:
            n = r.headers.get("Content-Length")
            return int(n) if n else None
    except Exception:  # noqa: BLE001
        return None


def neueste_url(paket: Paket) -> tuple[str, int | None] | None:
    """Sucht die neueste .zim-URL: erst Kiwix-Katalog (OPDS), dann Verzeichnisliste."""
    for praefix in paket.praefixe:
        muster = re.compile(re.escape(praefix) + r"_(\d{4}-\d{2})\.zim$")
        kandidaten: list[tuple[str, str, int | None]] = []

        # 1) OPDS-Katalog – Name mit und ohne Flavour probieren
        stamm = re.sub(r"_(maxi|nopic|mini)$", "", praefix)
        for name in dict.fromkeys([praefix, stamm]):
            try:
                xml = http_get(f"{KIWIX_CATALOG}?{urllib.parse.urlencode({'name': name, 'count': 50})}")
                for link in ET.fromstring(xml).iter("{http://www.w3.org/2005/Atom}link"):
                    href = (link.get("href") or "").removesuffix(".meta4")
                    m = muster.search(href)
                    if m:
                        laenge = link.get("length")
                        kandidaten.append((m.group(1), href, int(laenge) if laenge else None))
            except Exception as e:  # noqa: BLE001
                print(f"    Katalog ({name}) nicht erreichbar: {e}")
            if kandidaten:
                break

        # 2) Verzeichnisliste von download.kiwix.org
        if not kandidaten:
            try:
                index = http_get(f"{KIWIX_DOWNLOAD}/{paket.ordner}/").decode("utf-8", "replace")
                for datei in set(re.findall(r'href="([^"/]+\.zim)"', index)):
                    m = muster.search(datei)
                    if m:
                        kandidaten.append((m.group(1), f"{KIWIX_DOWNLOAD}/{paket.ordner}/{datei}", None))
            except Exception as e:  # noqa: BLE001
                print(f"    Verzeichnis {paket.ordner}/ nicht erreichbar: {e}")

        if kandidaten:
            _, url, groesse = max(kandidaten, key=lambda k: k[0])
            return url, groesse
    return None


def laden(url: str, ziel: Path, groesse: int | None = None) -> None:
    """Download mit Fortsetzen (.part-Datei) und Fortschrittsanzeige."""
    teil = ziel.with_name(ziel.name + ".part")
    for versuch in range(5):
        start = teil.stat().st_size if teil.exists() else 0
        if groesse and start >= groesse:
            break
        headers = dict(UA)
        if start:
            headers["Range"] = f"bytes={start}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=120) as r:
                if start and r.status != 206:      # Server kann nicht fortsetzen
                    start = 0
                if not groesse:
                    n = r.headers.get("Content-Length")
                    groesse = int(n) + start if n else None
                with open(teil, "ab" if start else "wb") as f:
                    geladen, t0, letzte = start, time.time(), 0.0
                    while chunk := r.read(1 << 20):
                        f.write(chunk)
                        geladen += len(chunk)
                        if time.time() - letzte > 2:
                            letzte = time.time()
                            rate = (geladen - start) / max(letzte - t0, 0.1) / 1e6
                            pct = f"{geladen / groesse * 100:5.1f} %" if groesse else ""
                            print(f"\r    {geladen / 1e9:6.2f} GB {pct}  {rate:5.1f} MB/s   ", end="", flush=True)
            print()
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            print(f"\n    Unterbrochen ({e}), neuer Versuch in {5 * (versuch + 1)} s …")
            time.sleep(5 * (versuch + 1))
    else:
        raise RuntimeError(f"Download fehlgeschlagen: {url}")
    teil.replace(ziel)


def pruefen(url: str, datei: Path) -> bool:
    try:
        soll = http_get(url + ".sha256").decode().split()[0].lower()
    except Exception:  # noqa: BLE001
        print("    (keine Prüfsumme verfügbar)")
        return True
    h = hashlib.sha256()
    with open(datei, "rb") as f:
        while chunk := f.read(1 << 22):
            h.update(chunk)
    ok = h.hexdigest() == soll
    print("    Prüfsumme OK" if ok else "    PRÜFSUMME FALSCH – Datei wird gelöscht")
    return ok


# ---------------------------------------------------------------- eigene Datenbank

def eigene_dateien(ziel: Path, nur_anzeigen: bool) -> None:
    kiwix, karten = ziel / "kiwix", ziel / "karten"
    privat = (ROOT / "privat").is_dir()
    print("\n== Eigene Datenbank (NOMAD Erzgebirge)")
    if privat:
        print("  privat/ gefunden → lokal bauen (mit deinen privaten Angaben)")
        if nur_anzeigen:
            return
        try:
            subprocess.run([sys.executable, str(ROOT / "scripts" / "fetch_osm.py")], check=False)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "fetch_images.py")], check=False)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "build_zim.py")], check=True)
            for z in (ROOT / "dist").glob("nomad-erzgebirge*.zim"):
                shutil.copy2(z, kiwix / z.name)
                print(f"  → kiwix/{z.name}")
            if (ROOT / "dist" / "gpx").is_dir():
                for g in (ROOT / "dist" / "gpx").glob("*.gpx"):
                    shutil.copy2(g, karten / g.name)
                print("  → karten/*.gpx")
            return
        except Exception as e:  # noqa: BLE001
            print(f"  Lokaler Build fehlgeschlagen ({e}) – lade stattdessen das öffentliche Release.")
            print("  Tipp: pip install -r requirements.txt")
    for name, ordner in [("nomad-erzgebirge.zim", kiwix), ("alle.gpx", karten)]:
        print(f"  {RELEASE}/{name}")
        if nur_anzeigen:
            continue
        try:
            tmp = ordner / (name + ".neu")
            laden(f"{RELEASE}/{name}", tmp)
            tmp.replace(ordner / name)
        except Exception as e:  # noqa: BLE001
            print(f"  Fehler: {e}  (Ist das Repo öffentlich? Private Repos brauchen eine Anmeldung.)")


# ---------------------------------------------------------------- main

def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description="NOMAD-Pakete für das iPhone herunterladen")
    ap.add_argument("--profil", choices=["minimal", "basis", "erweitert"], default="basis")
    ap.add_argument("--ziel", type=Path, default=Path.home() / "NOMAD-iPhone")
    ap.add_argument("--nur-anzeigen", action="store_true", help="nichts herunterladen, nur auflisten")
    ap.add_argument("--pruefen", action="store_true", help="SHA-256-Prüfsummen der Kiwix-Dateien prüfen")
    ap.add_argument("--alte-behalten", action="store_true", help="ältere Versionen nicht löschen")
    ap.add_argument("--ohne-eigene", action="store_true", help="eigene Datenbank/GPX überspringen")
    args = ap.parse_args()

    ziel: Path = args.ziel.expanduser()
    for sub in ("kiwix", "karten"):
        (ziel / sub).mkdir(parents=True, exist_ok=True)
    (ziel / "LIESMICH.txt").write_text(LIESMICH, encoding="utf-8")
    print(f"Zielordner: {ziel}   Profil: {args.profil}")

    if not args.ohne_eigene:
        eigene_dateien(ziel, args.nur_anzeigen)

    print("\n== Kiwix-Pakete")
    plan = []
    for p in PAKETE:
        if args.profil not in p.profile:
            continue
        print(f"  {p.titel}: suche neueste Version …")
        res = neueste_url(p)
        if not res:
            print("    nicht gefunden – übersprungen")
            continue
        url, groesse = res
        groesse = groesse or remote_size(url)
        name = url.rsplit("/", 1)[-1]
        print(f"    {name}  ({groesse / 1e9:.2f} GB)" if groesse else f"    {name}")
        plan.append((p, url, name, groesse))

    fehlend = [(p, u, n, g) for p, u, n, g in plan if not (ziel / "kiwix" / n).exists()]
    summe = sum(g or 0 for *_, g in fehlend)
    frei = shutil.disk_usage(ziel).free
    print(f"\n  Neu zu laden: {len(fehlend)} Datei(en), ca. {summe / 1e9:.1f} GB · frei: {frei / 1e9:.1f} GB")
    if args.nur_anzeigen:
        return
    if summe > frei:
        raise SystemExit("Nicht genug Speicherplatz im Zielordner.")

    for p, url, name, groesse in plan:
        datei = ziel / "kiwix" / name
        if datei.exists():
            print(f"\n  {name}: schon aktuell")
        else:
            print(f"\n  {name}: lade …")
            laden(url, datei, groesse)
            if args.pruefen and not pruefen(url, datei):
                datei.unlink()
                continue
        if not args.alte_behalten:
            praefix = re.sub(r"_\d{4}-\d{2}\.zim$", "", name)
            for alt in (ziel / "kiwix").glob(f"{praefix}_*.zim"):
                if alt.name != name and re.fullmatch(re.escape(praefix) + r"_\d{4}-\d{2}\.zim", alt.name):
                    print(f"    alte Version gelöscht: {alt.name}")
                    alt.unlink()

    print(f"\nFertig. Weiter mit {ziel / 'LIESMICH.txt'}")


if __name__ == "__main__":
    main()
