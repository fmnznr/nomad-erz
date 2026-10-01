# iPhone 12 mini einrichten – Schritt für Schritt

Ziel: ein komplett offline nutzbares Wissens-iPhone nach dem Vorbild von [Project NOMAD](https://github.com/Crosstalk-Solutions/project-nomad), zugeschnitten auf Zwönitz und den Erzgebirgskreis.

| NOMAD (PC/Server) | Hier (iPhone) |
|---|---|
| Kiwix-Server | **Kiwix**-App |
| ProtoMaps / Karten | **Organic Maps** |
| Ollama (lokale KI) | **PocketPal AI** |
| Eigene Inhalte | **`nomad-erzgebirge.zim`** aus diesem Projekt |

> **Schneller mit Mac/PC:** `python3 scripts/nomad_download.py` lädt alle Pakete auf einmal (inkl. Wikipedia, mit Fortsetzen bei Abbruch) in den Ordner `~/NOMAD-iPhone`. Danach per Kabel aufs iPhone übertragen, siehe `LIESMICH.txt` im Zielordner. Dann entfallen die Downloads in Schritt 1 und 2. Apps installieren und Karten laden musst du trotzdem.

---

## 0. Speicherplan für 64 GB

iOS und die Grund-Apps belegen ca. 12–18 GB. Prüfe den freien Platz unter *Einstellungen → Allgemein → iPhone-Speicher*. Die Größen (Stand Herbst 2026) ändern sich mit jeder Version. Aktuelle Werte zeigt `python3 scripts/nomad_download.py --nur-anzeigen` oder die Kiwix-Bibliothek.

| Paket | ca. Größe | Priorität |
|---|---|---|
| `nomad-erzgebirge.zim` (dieses Projekt) | < 1 MB | ★★★ |
| Organic Maps: Sachsen + tschechisches Grenzgebiet | 0,3–0,6 GB | ★★★ |
| **Wikipedia Deutsch ohne Bilder** (`wikipedia_de_all_nopic`) | ca. 14,6 GB | ★★★ |
| KI-Modell (1–2 Mrd. Parameter, Q4) | 0,8–1,5 GB | ★★ |
| Wikivoyage Deutsch (`wikivoyage_de_all_maxi`) | ca. 1,3 GB | ★★ |
| Wikibooks Deutsch (Kochbuch, Anleitungen) (`wikibooks_de_all_nopic`) | ca. 2,9 GB | ★ |
| Wiktionary Deutsch (`wiktionary_de_all_nopic`) | ca. 1,3 GB | ★ |
| iFixit (Englisch, Reparaturanleitungen) (`ifixit_en_all`) | ca. 3,6 GB | ★ |
| „zimgit“-Pakete (Englisch): `zimgit-post-disaster`, `zimgit-water`, `zimgit-medicine`, `zimgit-food-preparation` | zusammen ca. 0,8 GB | ★ |
| MedlinePlus / WikEM (Englisch, Medizin) | je ca. 0,5–2 GB | ★ |

**Basis-Paket (★★★ + ★★): ca. 18 GB.** Alles zusammen (inkl. ★) ca. 27 GB. Auf 64 GB passt beides, es bleibt Puffer für Fotos und Updates.
Wird es zu knapp: `wikipedia_de_all_mini` (nur Artikel-Einleitungen) statt `nopic`.

---

## 1. Kiwix (Nachschlagewerk)

1. **Kiwix** aus dem App Store installieren (kostenlos, Kiwix e.V.).
2. Im WLAN: *Bibliothek → Kategorien* durchsuchen, Sprache **Deutsch** filtern und die Pakete aus der Tabelle oben laden.
3. **Eigene Datenbank hinzufügen:**
    - In Safari öffnen: `https://github.com/fmnznr/nomad-erz/releases/latest/download/nomad-erzgebirge.zim`
      (funktioniert ohne Anmeldung, wenn das Repository öffentlich ist)
    - Download landet in der **Dateien-App** (Ordner *Downloads*).
    - Kiwix → *Bibliothek* → **„+“ / Öffnen** → Datei auswählen. Alternativ in der Dateien-App die Datei antippen → *Teilen* → **Kiwix**.
4. Die Volltextsuche funktioniert offline (z. B. „Kreuzotter“, „Steinpilz“, „Stromausfall“).

> Tipp: In Kiwix die Startseite der NOMAD-Datenbank als **Lesezeichen** speichern.

## 2. Organic Maps (Karten)

1. **Organic Maps** installieren (kostenlos, Open Source).
2. Im WLAN: *Menü → Karten herunterladen → Deutschland → Sachsen* (bzw. die Teilkarte mit dem Erzgebirge). Zusätzlich **Tschechien → Karlsbader und Aussiger Region**.
3. *Einstellungen → Ebenen*: **Höhenlinien** aktivieren.
4. **Kartenpunkte importieren:** `alle.gpx` (oder einzelne Kategorien) aus dem GitHub-Release laden → in der Dateien-App antippen → *Teilen* → **Organic Maps**.
   Download-Link: `https://github.com/fmnznr/nomad-erz/releases/latest/download/alle.gpx`
5. Optional: Lesezeichen für Zuhause, Treffpunkte, Arbeitsplatz und Schule setzen.

## 3. PocketPal AI (lokale KI, optional)

Das iPhone 12 mini hat **4 GB RAM**. Es eignen sich deshalb nur **kleine Modelle (1–2 Mrd. Parameter)** in 4-Bit-Quantisierung (Q4_K_M, Dateigröße ca. 0,8–1,5 GB). Größere Modelle (3B+) laufen sehr langsam oder stürzen ab.

1. **PocketPal AI** installieren (kostenlos, Open Source, nutzt llama.cpp).
2. *Models → Add from Hugging Face*: ein aktuelles kleines Modell mit guter Deutschunterstützung wählen, z. B.
    - **Qwen3 1.7B** (Instruct, Q4_K_M): gutes Deutsch für die Größe
    - **Gemma 3 1B** (it, Q4_K_M): schnell und sparsam
    - **Llama 3.2 1B** (Instruct, Q4_K_M)
    Neuere Modelle derselben Größenklasse sind meist besser. Entscheidend: **≤ 2B Parameter, Q4**.
3. Unter *Pals* einen Assistenten mit diesem Systemprompt anlegen:

```
Du bist ein hilfsbereiter Offline-Assistent für eine Person in Zwönitz im Erzgebirge (Sachsen, ca. 520 m ü. NHN).
Antworte kurz, auf Deutsch, praktisch.
Wichtig: Bei Pilzen, Wildpflanzen, Medizin und Notfällen gibst du nur allgemeine Hinweise,
erfindest keine Fakten und verweist auf 112, den Giftnotruf Erfurt (0361 730 730) und die Kiwix-Datenbank „NOMAD Erzgebirge“.
Wenn du etwas nicht sicher weißt, sag das.
```

> ⚠️ Kleine Sprachmodelle **erfinden Fakten** („halluzinieren“). Nutze sie zum Formulieren, Rechnen, Erklären und Ideensammeln, **niemals** zur Pilz- oder Pflanzenbestimmung oder für medizinische Entscheidungen. Fakten in Kiwix nachschlagen.

## 4. Weitere nützliche Offline-Apps

| App | Zweck |
|---|---|
| **Kompass** (vorinstalliert) | Koordinaten, Höhe, Richtung, auch offline |
| **Health → Notfallpass** | Medizinische Daten im Sperrbildschirm |
| **NINA** | Warnungen (braucht Netz, Cell Broadcast kommt zusätzlich) |
| **nora** | Offizielle Notruf-App (Text-Notruf) |
| **Hilfe im Wald** | Rettungspunkte im Wald |
| Eine **Barometer-App** | Luftdruckverlauf als Wetterprognose (das 12 mini hat einen Sensor) |
| **Flora Incognita** | Pflanzenbestimmung (TU Ilmenau), braucht meist Internet. Nur als Hinweis, nicht für Essbarkeit. |

## 5. Pflege

**Automatisch:** Ein Kurzbefehl lädt Datenbank und Kartenpunkte monatlich im WLAN: [kurzbefehl-update.md](kurzbefehl-update.md).

**Private Angaben** (Hausarzt, Notfallkontakte, Familien-Notfallplan) kommen nur in die Datenbank, wenn du sie am Mac/PC selbst baust (README → „Private Angaben“). Ohne Computer: im *Notfallpass* (Health) und in einer Notiz speichern.

- **Alle 3–6 Monate** im WLAN: Kiwix-Pakete, Organic-Maps-Karten und die NOMAD-ZIM aktualisieren.
- **Akku:** Das iPhone im Notfallrucksack bei 50–80 % lagern und alle paar Monate nachladen. Powerbank dazulegen.
- Ein altes iPhone **ohne SIM** kann trotzdem **112** anrufen.
- Ein Flugmodus-iPhone ist ein gutes **„Offline-Lexikon“**. Zusätzlich gehören Papierkarte und Kompass in den Rucksack.
