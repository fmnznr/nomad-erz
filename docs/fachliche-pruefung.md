# Fachliche Prüfung – Checkliste

Die Inhalte von NOMAD Erzgebirge sind aus allgemeinem Fachwissen geschrieben und **noch nicht fachlich gegengelesen**. Diese Liste zeigt, welche Seite von wem geprüft werden sollte.

## So läuft eine Prüfung ab

1. Seite lesen, am besten in der fertigen Datenbank (Kiwix) oder direkt hier im Ordner `content/`.
2. Fehler, Lücken oder gefährliche Vereinfachungen melden:
   - auf GitHub über **Issues → New issue → „Korrektur / fachliche Prüfung“**, oder
   - direkt als Änderung (Pull Request) an der Markdown-Datei.
3. Nach der Prüfung in der Tabelle unten Datum und Prüfer:in (Name oder Funktion) eintragen.
4. Bei den Sicherheitsseiten den Block `!!! warning "Fachlich noch nicht geprüft"` am Seitenanfang entfernen.
5. Erledigte Prüfpunkte `{{prüfen:…}}` im Text löschen bzw. die Angabe korrigieren.

Alle offenen Prüfpunkte erscheinen in der Datenbank auf der Seite **„Offene Prüfpunkte“**.

## Wo findet man Fachleute?

| Fachgebiet | Ansprechpartner (Beispiele) |
|---|---|
| Pilze | Pilzsachverständige der Deutschen Gesellschaft für Mykologie (DGfM), örtliche Pilzberatungsstellen, Pilzvereine in Sachsen |
| Pflanzen | Botanische Arbeitskreise, NABU-Gruppen, Kräuterpädagog:innen, Naturpark Erzgebirge/Vogtland |
| Erste Hilfe, Vergiftungen | Erste-Hilfe-Ausbilder:innen (DRK, ASB, Johanniter, Malteser), Rettungsdienst, Giftinformationszentrum Erfurt |
| Tiere | NABU, Landesjagdverband, Fachstelle Wolf (LfULG), Angelverein |
| Krisenvorsorge, Wetter | Freiwillige Feuerwehr Zwönitz, Katastrophenschutz des Landkreises |
| Bergbau, Radon | Bergbauverein, Sächsisches Oberbergamt, Radonberatungsstelle Sachsen |
| Geografie, Ortsangaben | Stadtverwaltung Zwönitz, Heimatverein, Ortschronisten |

## Prüfstand

| Seite | Prüfen durch | Priorität | Geprüft am / von |
|---|---|---|---|
| `natur/pilze.md` | Pilzsachverständige:r (DGfM) | **hoch** | ☐ |
| `natur/giftpflanzen.md` | Botanik, Giftinformationszentrum | **hoch** | ☐ |
| `natur/essbare-wildpflanzen.md` | Botanik, Wildpflanzen-Kunde | **hoch** | ☐ |
| `notfall/erste-hilfe.md` | Erste-Hilfe-Ausbildung, Rettungsdienst | **hoch** | ☐ |
| `notfall/vergiftungen.md` | Giftinformationszentrum, Notfallmedizin | **hoch** | ☐ |
| `notfall/notrufe.md` | Rettungsleitstelle, Feuerwehr | **hoch** | ☐ |
| `notfall/trinkwasser.md` | Gesundheitsamt, Wasserversorger | mittel | ☐ |
| `notfall/krisenvorsorge.md` | Feuerwehr, Katastrophenschutz | mittel | ☐ |
| `notfall/wetter-gefahren.md` | Feuerwehr, Sachsenforst | mittel | ☐ |
| `notfall/bergbau-gefahren.md` | Oberbergamt, Bergbauverein | mittel | ☐ |
| `natur/zecken-insekten.md` | Hausarzt/-ärztin, Gesundheitsamt | mittel | ☐ |
| `natur/sammelkalender.md` | Pilzberatung, Botanik | mittel | ☐ |
| `notfall/draussen.md`, `notfall/orientierung.md` | Bergwacht, Sachsenforst | niedrig | ☐ |
| `natur/baeume-straeucher.md`, `natur/lebensraeume.md` | Sachsenforst, Naturpark | niedrig | ☐ |
| `natur/saeugetiere.md`, `natur/voegel.md`, `natur/reptilien-amphibien-fische.md` | NABU, Jagdverband, LfULG | niedrig | ☐ |
| `geografie/*.md` | Stadt Zwönitz, Heimatverein | niedrig | ☐ |

## Fotos prüfen

Die Fotos werden automatisch aus dem jeweiligen deutschen Wikipedia-Artikel übernommen (Hauptbild). Bitte stichprobenartig prüfen, besonders bei **Pilzen und Giftpflanzen**:

- Zeigt das Foto wirklich die genannte Art, mit typischen Merkmalen?
- Ist ein anderes Foto aus Wikimedia Commons besser geeignet? Dann im Text den Platzhalter `{{bild:…}}` auf einen passenderen Artikel ändern oder ein Issue anlegen.

Übersicht aller Fotos: Seite **„Bildnachweise“** in der Datenbank.
