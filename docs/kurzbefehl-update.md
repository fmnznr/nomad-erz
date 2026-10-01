# Automatisch aktualisieren mit Kurzbefehlen (iPhone)

Mit der vorinstallierten App **Kurzbefehle** lädt das iPhone die NOMAD-Datenbank und die Kartenpunkte **einmal im Monat automatisch** herunter, nur im WLAN. Die großen Kiwix-Pakete (Wikipedia) und die Organic-Maps-Karten aktualisierst du weiterhin in den jeweiligen Apps. Die Apps machen das zuverlässiger als ein Kurzbefehl.

> Voraussetzung: Das Repository ist **öffentlich**, sonst liefert GitHub ohne Anmeldung keine Dateien.
> Die Bezeichnungen der Aktionen können je nach iOS-Version leicht abweichen.

## 1. Ordner anlegen

App **Dateien** → *Auf meinem iPhone* → lange drücken → **Neuer Ordner** → `NOMAD`.

## 2. Kurzbefehl „NOMAD aktualisieren“ erstellen

Kurzbefehle → **+** → oben den Namen auf **NOMAD aktualisieren** setzen. Dann diese Aktionen der Reihe nach hinzufügen (über die Suchleiste unten):

| # | Aktion | Einstellung |
|---|---|---|
| 1 | **Netzwerkdetails abrufen** | *WLAN* · Detail: *Netzwerkname* |
| 2 | **Wenn** | *Netzwerkdetails* · **hat keinen Wert** |
| 3 | ↳ **Kurzbefehl stoppen** | (kein WLAN → nichts tun) |
| 4 | **Ende wenn** | (wird automatisch eingefügt) |
| 5 | **URL** | `https://github.com/fmnznr/nomad-erz/releases/latest/download/nomad-erzgebirge.zim` |
| 6 | **Inhalte von URL abrufen** | Methode *GET* |
| 7 | **Name festlegen** | Name: `nomad-erzgebirge.zim` |
| 8 | **Datei sichern** | *Fragen, wo gesichert werden soll*: **aus** · Ziel: Ordner **NOMAD** · *Überschreiben, falls Datei vorhanden*: **an** |
| 9 | **URL** | `https://github.com/fmnznr/nomad-erz/releases/latest/download/alle.gpx` |
| 10 | **Inhalte von URL abrufen** | – |
| 11 | **Name festlegen** | `alle.gpx` |
| 12 | **Datei sichern** | wie Schritt 8 |
| 13 | **Mitteilung anzeigen** | `NOMAD Erzgebirge aktualisiert ✅` |

Einmal **manuell ausführen** (▶︎) und die Rückfragen zum Zugriff auf github.com und den Ordner erlauben.

## 3. Automation: monatlich ausführen

Kurzbefehle → Reiter **Automation** → **+** (bzw. *Neue Automation*):

1. Auslöser **Tageszeit** → z. B. **03:00 Uhr**, Wiederholen: **Monatlich** (Tag 2, der GitHub-Build läuft am 1.).
2. **Sofort ausführen** wählen (nicht „Vor dem Ausführen bestätigen“). *Bei Ausführung mitteilen* nach Wunsch.
3. Kurzbefehl **NOMAD aktualisieren** auswählen.

Tipp: Nachts hängt das iPhone meist am Ladekabel und ist im WLAN.

## 4. Kiwix mit der Datei im Ordner verbinden (einmalig)

Kiwix → *Bibliothek* → **Öffnen / +** → *Auf meinem iPhone → NOMAD →* `nomad-erzgebirge.zim`.

Wenn Kiwix die Datei **an Ort und Stelle** öffnet, ist nach jedem Update automatisch die neue Version da. Ob das bei deiner Kiwix-Version so ist, siehst du nach dem ersten automatischen Update: Datum auf der Startseite der Datenbank unten prüfen („Stand: …“).
Wenn noch das alte Datum dasteht: Kiwix hat eine Kopie angelegt. Dann nach einem Update in der Dateien-App die ZIM-Datei antippen → *Teilen* → **Kiwix** und das alte Buch in Kiwix löschen. Das ist ein Handgriff pro Monat.

## 5. Kartenpunkte in Organic Maps

Organic Maps kann importierte GPX-Listen nicht selbst aktualisieren. Krankenhäuser und Apotheken ändern sich aber selten, deshalb reicht es **alle paar Monate**:

1. Organic Maps → *Lesezeichen* → alte Liste „NOMAD Erzgebirge – alle Punkte“ **löschen**.
2. Dateien → *NOMAD* → `alle.gpx` antippen → *Teilen* → **Organic Maps**.

## Was sonst noch zu aktualisieren ist

| Was | Wie oft | Wo |
|---|---|---|
| Organic-Maps-Karte | bei Hinweis in der App (ca. monatlich) | Organic Maps → *Karten herunterladen* → **Alle aktualisieren** |
| Wikipedia & Co. | 1–2× pro Jahr | Kiwix → *Bibliothek* → neuere Version laden, alte löschen |
| KI-Modell | selten nötig | PocketPal |
| iOS | bei Sicherheitsupdates | Einstellungen |

Mit Mac/PC geht das Ganze in einem Rutsch: [`scripts/nomad_download.py`](../scripts/nomad_download.py) (siehe README).
