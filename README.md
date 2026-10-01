# NOMAD Erzgebirge 📱⛰️

Offline-Wissensdatenbank für **Zwönitz und den Erzgebirgskreis**, gedacht für ein altes **iPhone 12 mini (64 GB)**. Vorbild ist [Project NOMAD](https://github.com/Crosstalk-Solutions/project-nomad), aber ohne Server: Alles läuft in Offline-Apps.

| Baustein | App | Inhalt |
|---|---|---|
| Regionale Datenbank | Kiwix | **Diese Repo**: Natur, Notfall & Überleben, Geografie, OSM-Kartenpunkte |
| Nachschlagewerk | Kiwix | Wikipedia DE (ohne Bilder), Wikivoyage, Wikibooks … |
| Karten | Organic Maps | OSM Sachsen + Grenzgebiet CZ, Höhenlinien, GPX-Kartenpunkte |
| KI (optional) | PocketPal AI | Kleines lokales Sprachmodell (≤ 2B) |

👉 **Einrichtung auf dem iPhone:** [docs/iphone-einrichtung.md](docs/iphone-einrichtung.md)

## Inhalt der Datenbank

- **Natur:** Lebensräume, Bäume & Sträucher, essbare Wildpflanzen, Giftpflanzen, **Pilze** (inkl. regional relevanter Giftpilze wie Raukopf und Kegelhütiger Knollenblätterpilz), Säugetiere, Vögel, Reptilien/Amphibien/Fische, Zecken & Insekten, Sammelkalender
- **Notfall & Überleben:** Notrufe, Erste Hilfe, Vergiftungen, Trinkwasser, Krisenvorsorge & Stromausfall, Wettergefahren (Gewitter, Hochwasser, Raueis, Böhmischer Wind), **Altbergbau & Radon**, Orientierung, Feuer & Unterschlupf
- **Geografie & Karten:** Zwönitz, Erzgebirgskreis, Berge, Gewässer, Geologie, Klima & Gartenjahr, Schutzgebiete, Offline-Karten, **Kartenpunkte aus OpenStreetMap** (Krankenhäuser, Apotheken, Defis, Feuerwehr, Polizei, Schutzhütten, Quellen, Trinkwasser, Gipfel), auch als GPX

## Bauen

**Automatisch:** Jeder Push auf `main` (und monatlich) baut über GitHub Actions die ZIM-Datei mit frischen OSM-Daten und veröffentlicht sie als Release:

- `https://github.com/fmnznr/nomad-erz/releases/latest/download/nomad-erzgebirge.zim`
- `https://github.com/fmnznr/nomad-erz/releases/latest/download/alle.gpx`

**Lokal** (Linux/macOS, Python ≥ 3.10):

```bash
pip install -r requirements.txt
python3 scripts/fetch_osm.py      # Kartenpunkte aus OpenStreetMap laden (Internet nötig)
python3 scripts/build_zim.py      # → dist/nomad-erzgebirge.zim, dist/html/, dist/gpx/
```

`dist/html/index.html` lässt sich auch direkt im Browser öffnen.

## Inhalte ergänzen

Alle Texte liegen als Markdown in `content/`. Eine neue `.md`-Datei wird automatisch zur Seite. Verlinke sie dann im passenden `index.md`. Der Build meldet kaputte interne Links.

Platzhalter `_eintragen_` (z. B. Hausarzt, Störungsnummern, Notfall-Anlaufstelle) solltest du mit deinen eigenen Daten füllen. Repository dann privat halten!

## Haftung

Orientierungshilfe ohne Gewähr. Kein Ersatz für Erste-Hilfe-Kurs, Pilzberatung oder ärztlichen Rat. Kartendaten © OpenStreetMap-Mitwirkende (ODbL).
