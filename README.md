# NOMAD Erzgebirge 📱⛰️

Offline-Wissensdatenbank für **Zwönitz und den Erzgebirgskreis**, gedacht für ein altes **iPhone 12 mini (64 GB)**. Vorbild ist [Project NOMAD](https://github.com/Crosstalk-Solutions/project-nomad), aber ohne Server: Alles läuft in Offline-Apps.

| Baustein | App | Inhalt |
|---|---|---|
| Regionale Datenbank | Kiwix | **Diese Repo**: Natur, Notfall & Überleben, Geografie, OSM-Kartenpunkte |
| Nachschlagewerk | Kiwix | Wikipedia DE (ohne Bilder), Wikivoyage, Wikibooks … |
| Karten | Organic Maps | OSM Sachsen + Grenzgebiet CZ, Höhenlinien, GPX-Kartenpunkte |
| KI (optional) | PocketPal AI | Kleines lokales Sprachmodell (≤ 2B) |

👉 **Einrichtung auf dem iPhone:** [docs/iphone-einrichtung.md](docs/iphone-einrichtung.md)

👉 **Automatisch aktualisieren (Kurzbefehl):** [docs/kurzbefehl-update.md](docs/kurzbefehl-update.md)

## Alles auf einmal herunterladen (Mac/PC)

```bash
python3 scripts/nomad_download.py                    # Profil „basis“ (~15 GB) nach ~/NOMAD-iPhone
python3 scripts/nomad_download.py --nur-anzeigen     # vorher ansehen, was geladen würde
python3 scripts/nomad_download.py --profil erweitert # + Wiktionary, iFixit, zimgit-Pakete
python3 scripts/nomad_download.py --profil minimal   # Wikipedia nur Einleitungen
```

Das Skript sucht jeweils die **neueste Version** im Kiwix-Katalog, setzt abgebrochene Downloads fort, löscht alte Versionen und prüft auf Wunsch die Prüfsummen (`--pruefen`). Es braucht nur Python ≥ 3.10, keine Zusatzpakete. Erneut ausführen = aktualisieren. Unter Windows `py` statt `python3` verwenden. Die Übertragung aufs iPhone ist in `LIESMICH.txt` im Zielordner beschrieben.

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

## Private Angaben

Persönliches (Hausarzt, Notfallkontakte, Störungsnummern, Treffpunkt, eigene Seiten wie ein Familien-Notfallplan) gehört **nicht** ins Repository:

```bash
cp -r privat-vorlage privat        # bzw. Ordner kopieren und umbenennen; privat/ wird von git ignoriert
# privat/eintraege.txt ausfüllen, eigene Seiten in privat/seiten/*.md
python3 scripts/build_zim.py       # → dist/nomad-erzgebirge-privat.zim
```

In den Texten stehen dafür Platzhalter wie `{{privat:hausarzt}}`. Die öffentliche Version zeigt dort „nicht eingetragen“. `nomad_download.py` baut automatisch die private Version, wenn `privat/` existiert. Die private ZIM-Datei **nicht** hochladen oder teilen.

## Inhalte ergänzen

Alle Texte liegen als Markdown in `content/`. Eine neue `.md`-Datei wird automatisch zur Seite. Verlinke sie dann im passenden `index.md`. Der Build meldet kaputte interne Links.

## Lizenz & Haftung

Texte: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.de) · Code: MIT · Kartendaten: © OpenStreetMap-Mitwirkende (ODbL). Details in [LICENSE](LICENSE).

Orientierungshilfe ohne Gewähr. Kein Ersatz für Erste-Hilfe-Kurs, Pilzberatung oder ärztlichen Rat.
