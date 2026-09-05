# Bedienanleitung

Anleitung für Anwender, die den Skill in Claract oder einer anderen Agent-Skills-fähigen Umgebung nutzen.

## Einmalige Einrichtung

Der Skill wird von einem Administrator einmalig aus dem GitHub-Repository importiert und ist danach für alle Anwender der Umgebung verfügbar. Nichts weiter zu tun.

## Vier Aufgabenarten

| Was Sie tun wollen | Sie senden | Sie brauchen zusätzlich |
|---|---|---|
| Dokument erstmals pseudonymisieren | `PSEUDONYMISIEREN` + Alias | Das Original-DOCX |
| Weiteres Dokument desselben Mandats codieren | `FORTSCHREIBEN` + Alias | Neues DOCX plus vorhandene JSON-Legende |
| Codes zurückführen | `RUECKUMWANDELN` + Alias | PSEUDO-DOCX plus JSON-Legende |
| PSEUDO-Datei zweitprüfen | `PRUEFEN` | Nur PSEUDO-DOCX (bewusst ohne Legende) |

## Ablauf einer Pseudonymisierung (typischer Fall)

**Schritt 1** — Dokument als DOCX hochladen. Andere Formate zuerst mit `rwt-skill-dokument-nach-docx` in DOCX überführen.

**Schritt 2** — Anweisung senden:

```
PSEUDONYMISIEREN
Alias: MANDAT-XY
```

Der Alias ist eine Kurzbezeichnung ohne Personenbezug, z. B. `PROJEKT-ALPHA`, `MANDAT-2026-042`. Kein Kundenname, keine Personennamen.

**Schritt 3** — Der Bot antwortet mit einer Vorschlagsliste und Zweifelsfällen. Er stellt Fragen zu Konfigurationsoptionen, die nicht Voreinstellung sind.

**Schritt 4** — Sie prüfen die Vorschlagsliste. Wenn etwas fehlt oder falsch klassifiziert ist, sagen Sie es präzise:

```
Korrektur:
- "Vogel Beteiligungs" ist FIRMA_01, nicht PERSON.
- "Aurora" gehört zu OBJEKT_01 wie "Projekt Aurora".
- KANZLEI_CODIEREN: nein (die Kanzlei ist selbst RWT und muss nicht codiert werden)
```

Der Bot passt die Liste an und legt sie erneut vor. Bei einfachen Läufen genügt oft eine Runde.

**Schritt 5** — Wenn Sie einverstanden sind:

```
FREIGABE
```

**Schritt 6** — Der Bot liefert drei Dateien: `<Name>_PSEUDO.docx`, `<ALIAS>_LEGENDE_v1.md`, `<ALIAS>_LEGENDE_v1.json`. Dazu einen kurzen Prüfbericht.

**Schritt 7** — Sie prüfen das PSEUDO-Dokument:

- Sind Klarnamen sichtbar? (Wenn ja: nicht ausliefern, Korrektur anweisen)
- Ist die Kennzeichnungszeile am Anfang? (Muss)
- Sind Struktur, Tabellen, Nummerierung erhalten? (Sollte)

**Schritt 8** — Die Legende speichern Sie in Ihrer geschlossenen Ablage. Das PSEUDO-Dokument dürfen Sie in offene KI-Umgebungen laden.

## Ablauf einer Rückumwandlung

**Schritt 1** — Beide Dateien hochladen: PSEUDO-DOCX und JSON-Legende.

**Schritt 2** — Anweisung senden:

```
RUECKUMWANDELN
Alias: MANDAT-XY
```

**Schritt 3** — Der Bot liefert `<Name>_KLAR.docx`. Er ersetzt jeden Code deterministisch. Der Text ist identisch mit dem Original, bis auf die Kennzeichnungszeile (entfernt) und ggf. Textstellen, die Sie in der offenen Umgebung bewusst geändert haben.

## Typische Fehlerbilder

**Der Bot liefert sofort ein PSEUDO-Dokument ohne Vorschlagsliste.**
Regel gebrochen. Sagen Sie `STOPP. Bitte zuerst Phase 1: Vorschlagsliste und Zweifelsfälle. Kein PSEUDO-Dokument ohne meine FREIGABE.` und starten Sie den Lauf neu.

**Die Legende steht im PSEUDO-Dokument.**
Regel gebrochen. Nicht ausliefern. Bot anweisen, die Legende zu entfernen und als eigene Datei bereitzustellen.

**Nach RUECKUMWANDELN steht `Alpenblick Praezisionsteile Präzisionsteile` doppelt.**
Die Grundform in der Änderungskarte hatte Umlaute anders geschrieben als das Dokument. Für den nächsten Lauf: Grundform aus dem Dokument kopieren, nicht paraphrasieren.

**Der Prüfbericht meldet Klarnamen in der Restsuche.**
Der Bot hat eine Stelle übersehen. Die Änderungskarte um die fehlende Entität erweitern (neuer Eintrag oder Variante) und Phase 2 wiederholen.

**Ein Code bleibt nach RUECKUMWANDELN im Text stehen.**
Der Code steht im PSEUDO-Dokument, aber die Legende enthält ihn nicht. Ursache: Legende beschädigt oder falsche Version. Legende gegen Backup prüfen.

**Der Bot fragt in Phase 1 nach Optionen, die Sie nicht kennen.**
Antworten Sie mit `Voreinstellungen`. Der Bot arbeitet mit den Standards weiter.

## Was nie in den Bot gehört

- Die Lösungsschlüssel A und B aus `assets/`. Sie würden den Test verfälschen.
- Die JSON-Legende, wenn Sie den PRUEFEN-Lauf machen.
- Echte Mandatsdokumente, solange die Freigabe für das Verfahren nicht erteilt ist. Für Testläufe ausschließlich die fiktiven Testdokumente verwenden.

## Grenzen

Der Skill kann DOCX. Andere Formate müssen vorher extrahiert werden. Gescannte PDFs ohne Textebene sind für ihn ebenfalls nicht bearbeitbar; nutzen Sie `rwt-skill-dokument-nach-docx` mit OCR-Vorlauf.

Der Skill ist ein Werkzeug. Er ersetzt weder die datenschutzrechtliche Bewertung noch die berufsrechtliche Prüfung, ob und wie Mandatsdaten in eine externe Umgebung gegeben werden dürfen. Vor produktivem Einsatz mit der RWT-KI-Richtlinie und dem Datenschutzbeauftragten abstimmen. Keine Rechts-, Steuer- oder Datenschutzberatung.
