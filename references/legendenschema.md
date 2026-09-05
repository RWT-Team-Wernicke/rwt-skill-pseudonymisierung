# Legendenschema

Die Legende ist das Herzstück des Verfahrens. Sie ist der einzige Weg, das pseudonymisierte Dokument wieder in Klartext zurückzuführen.

## Zwei Dateien pro Legende

Bei jedem PSEUDONYMISIEREN- oder FORTSCHREIBEN-Lauf werden zwei Dateien erzeugt:

- `<ALIAS>_LEGENDE_v<N>.md` — Markdown-Fassung für den Menschen (Übersicht, Kontext, Kommentare)
- `<ALIAS>_LEGENDE_v<N>.json` — Maschinenlesbare Fassung für `depseudonymize.py`

Die JSON-Fassung ist authoritativ für die Rückumwandlung. Die Markdown-Fassung enthält denselben JSON-Block, sodass beide Dateien austauschbar sind, aber nur die JSON-Datei ohne Rahmen wird vom Skript gelesen.

## Struktur der Markdown-Fassung

```
# Legende <ALIAS> (Version <N>)

Erstellt: <Datum>
Skill: rwt-skill-pseudonymisierung

Diese Datei enthält die Zuordnung zwischen Codes und Klarnamen.
Sie darf nicht mit dem pseudonymisierten Dokument in offene Umgebungen gelangen.

## Codetabelle

| Code | Kategorie | Grundform | Varianten | Vorkommen im PSEUDO | Kommentar |
|---|---|---|---|---|---|
| PERSON_01 | PERSON | Dr. Klaus Vogel | Herr Dr. Vogel; Vogels; K. Vogel | 5 | Kommanditist |
| ... |

## JSON-Block (maschinenlesbar)

```json
{
  "alias": "TEST-A",
  "version": 1,
  "eintraege": [
    {
      "code": "PERSON_01",
      "kategorie": "PERSON",
      "grundform": "Dr. Klaus Vogel",
      "varianten": ["Herr Dr. Vogel", "Vogels", "K. Vogel"],
      "kommentar": "Kommanditist"
    },
    ...
  ]
}
```

## Struktur der Änderungskarte (Input für pseudonymize.py)

Die Änderungskarte hat dieselbe Struktur wie der JSON-Block der Legende. Der Bot erzeugt sie in Phase 2 aus der freigegebenen Vorschlagsliste.

Pflichtfelder je Eintrag:
- `code` — im Format `KATEGORIE_NN`, ohne eckige Klammern
- `kategorie` — eine der 13 zugelassenen Kategorien
- `grundform` — die häufigste oder klarste Form der Entität; wird bei RUECKUMWANDELN eingesetzt

Optionale Felder:
- `varianten` — Liste weiterer Schreibweisen (Genitiv, Initialen, Kurzformen)
- `kommentar` — freie Bemerkung für Menschen (nicht funktional)

## Reihenfolge der Ersetzung

Der Skript ersetzt in der Reihenfolge **absteigende Zeichenkettenlänge**. Damit wird eine lange Zeichenkette (z. B. „Dr. Klaus Vogel") vor einer kurzen („Vogel") ersetzt, sodass keine Teiltreffer entstehen. Das ist der Grund, warum Sie einen Familiennamen wie „Vogel" nicht als eigene Variante in die changemap aufnehmen sollten, wenn er auch Teil einer Firmenbezeichnung ist („Vogel Beteiligungs GmbH"): sonst wird der Firmenname zerlegt. Die Reihenfolge löst die häufigsten Fälle korrekt, aber nicht alle. In Zweifelsfällen: zwei getrennte Codes vergeben, den Zusammenhang im Kommentar erklären.

## Versionsführung

- Erstlauf: Version 1
- FORTSCHREIBEN: Version um 1 erhöhen, neue Codes ans Ende der Liste anhängen (nicht neu nummerieren)
- Nummern werden nie wiederverwendet, auch wenn Einträge nachträglich als überflüssig erkannt werden
- Alte Versionen der Legende aufbewahren, sonst sind alte PSEUDO-Dokumente nicht mehr rückführbar

## Sicherheit

Die Legende bleibt in der geschlossenen Umgebung. Sie darf nicht:

- gemeinsam mit dem PSEUDO-Dokument in eine offene KI-Umgebung geladen werden
- in ein öffentliches Repository, Ticketsystem oder Chat gestellt werden
- unverschlüsselt per E-Mail versendet werden

Der Skill kennzeichnet jede erzeugte Legende mit einem entsprechenden Hinweis im Kopf.

## Notfall-Rückweg ohne Skript

Falls `depseudonymize.py` nicht verfügbar ist (z. B. andere Umgebung ohne Python), kann die Rückumwandlung auch manuell in Word erfolgen: für jede Zeile der Codetabelle „Suchen und Ersetzen" nutzen (Code → Grundform). Die Reihenfolge ist hier egal, weil Codes eindeutig sind und keine Teiltreffer erzeugen. Dieser Weg ist mühsam, aber garantiert funktionsfähig, solange die Legende vorhanden ist.
