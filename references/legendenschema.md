# Legendenschema

Die Legende ist das Herzstück des Verfahrens. Sie ist der einzige Weg, das pseudonymisierte Dokument wieder in Klartext zurückzuführen.

Ab Skill v1.1 gilt Legendenschema v2 mit Positionsindex. Schema v1 (aus Skill v1.0) bleibt lesbar, ein wortgleicher Roundtrip ist damit aber nicht garantiert. Neu erzeugte Legenden verwenden immer v2.

## Zwei Dateien pro Legende

Bei jedem PSEUDONYMISIEREN- oder FORTSCHREIBEN-Lauf werden zwei Dateien erzeugt:

- `<ALIAS>_LEGENDE_v<N>.md` — Markdown-Fassung für den Menschen (Übersicht, Kontext, Kommentare)
- `<ALIAS>_LEGENDE_v<N>.json` — Maschinenlesbare Fassung für `depseudonymize.py`

Die JSON-Fassung ist authoritativ für die Rückumwandlung. Die Markdown-Fassung enthält denselben JSON-Block, sodass beide Dateien austauschbar sind, aber nur die JSON-Datei ohne Rahmen wird vom Skript gelesen.

## Struktur der Markdown-Fassung

```
# Legende <ALIAS> (Iteration <N>, Schema v2)

Erstellt: <Datum>
Skill: rwt-skill-pseudonymisierung

Diese Datei enthält die Zuordnung zwischen Codes und Klarnamen.
Sie darf nicht mit dem pseudonymisierten Dokument in offene Umgebungen gelangen.

## Codetabelle

| Code | Kategorie | Grundform | Varianten (dedupliziert) | Vorkommen | Kommentar |
|---|---|---|---|---|---|
| PERSON_01 | PERSON | Dr. Klaus Vogel | Herr Dr. Vogel; Vogels; K. Vogel | 5 (Positionen 1, 2, 3, 4, 5) | Kommanditist |
| ... |

## JSON-Block (maschinenlesbar, Schema v2)

```json
{
  "alias": "TEST-A",
  "version": 2,
  "eintraege": [
    {
      "code": "PERSON_01",
      "kategorie": "PERSON",
      "grundform": "Dr. Klaus Vogel",
      "vorkommen": [
        {"position": 1, "originalform": "Dr. Klaus Vogel"},
        {"position": 2, "originalform": "Herr Dr. Vogel"},
        {"position": 3, "originalform": "Vogels"},
        {"position": 4, "originalform": "K. Vogel"},
        {"position": 5, "originalform": "Vogel"}
      ],
      "kommentar": "Kommanditist"
    },
    ...
  ]
}
```

### Feld `vorkommen`

- Jedes Vorkommen entspricht genau einer Ersetzung im PSEUDO-Dokument.
- `position` beginnt je Code bei 1 und zählt in Textreihenfolge im PSEUDO-Dokument, nicht dokumentweit über alle Codes.
- `originalform` ist die exakte Zeichenkette an dieser Stelle im Original. Sie kann die Grundform sein oder eine Variante (Genitiv, Kurzform, Anrede plus Nachname).
- Beim Rückumwandeln arbeitet `depseudonymize.py` mit einem codebezogenen Cursor: das n-te Vorkommen von `[PERSON_01]` im PSEUDO wird mit `vorkommen[n].originalform` ersetzt. Dadurch entsteht ein wortgleicher Roundtrip (K5a).
- Wenn ein Cursor über die vorhandenen Vorkommen hinausläuft (überzähliges `[CODE]` im PSEUDO), fällt das Skript auf die Grundform zurück und meldet den Fall im Bericht.

## Struktur bei Altlegende (Schema v1)

Legenden aus Skill v1.0 haben statt `vorkommen` das Feld `varianten` (nur die Liste der Schreibweisen, keine Positionsinformation). Die Rückumwandlung nutzt bei v1 durchgehend die Grundform und weist im Bericht darauf hin, dass K5a nur zufällig erfüllt werden kann.

Soll eine alte Fassung nachträglich wortgleich rueckgefuehrt werden, muss das Ursprungsdokument mit Skill v1.1 neu pseudonymisiert werden. Ein Upgrade der Legende ohne Zugriff auf das Original ist nicht möglich, weil die Positionsinformation dort nicht vorhanden ist.

## Struktur der Änderungskarte (Input für pseudonymize.py)

Die Änderungskarte bleibt in Schema v1 (mit `varianten`). Der Positionsindex wird beim Lauf automatisch aus dem Textabgleich erzeugt und steht dann in der Legende (v2). Der Bot erzeugt die Änderungskarte in Phase 2 aus der freigegebenen Vorschlagsliste.

Pflichtfelder je Eintrag:
- `code` — im Format `KATEGORIE_NN`, ohne eckige Klammern
- `kategorie` — eine der 13 zugelassenen Kategorien
- `grundform` — die häufigste oder klarste Form der Entität; wird bei RUECKUMWANDELN eingesetzt

Optionale Felder:
- `varianten` — Liste weiterer Schreibweisen (Genitiv, Initialen, Kurzformen)
- `kommentar` — freie Bemerkung für Menschen (nicht funktional)

## Reihenfolge der Ersetzung

Der Skript sammelt zunächst alle möglichen Treffer im Text und löst Überlappungen auf: bei zwei sich überlappenden Treffern gewinnt der längere („Dr. Klaus Vogel" vor „Vogel"), bei gleicher Länge die Grundform vor der Variante. Die verbleibenden nicht-überlappenden Treffer werden **in Textreihenfolge** ersetzt und in dieser Reihenfolge auch nummeriert. Damit stimmt die Position im PSEUDO-Dokument mit der Reihenfolge in `vorkommen` überein.

Empfehlung für Sonderfälle: Einen Familiennamen wie „Vogel" nicht als eigene Variante in die Änderungskarte aufnehmen, wenn er auch Teil einer Firmenbezeichnung ist („Vogel Beteiligungs GmbH"). Sonst wird der Firmenname zerlegt. Bei mehrdeutiger Zuordnung zwei getrennte Codes vergeben und den Zusammenhang im Kommentar erklären.

## Versionsführung

- Erstlauf: Iteration 1 (Dateiname `<ALIAS>_LEGENDE_v1.json`), Schema v2
- FORTSCHREIBEN: Iteration um 1 erhöhen, neue Codes ans Ende der Liste anhängen (nicht neu nummerieren), Positionsindex je Code neu berechnen
- Nummern werden nie wiederverwendet, auch wenn Einträge nachträglich als überflüssig erkannt werden
- Alte Iterationen der Legende aufbewahren, sonst sind alte PSEUDO-Dokumente nicht mehr rückführbar
- Nicht verwechseln: Iterationsnummer (Änderung des Mandats) und Schema-Version (Änderung des Skills)

## Sicherheit

Die Legende bleibt in der geschlossenen Umgebung. Sie darf nicht:

- gemeinsam mit dem PSEUDO-Dokument in eine offene KI-Umgebung geladen werden
- in ein öffentliches Repository, Ticketsystem oder Chat gestellt werden
- unverschlüsselt per E-Mail versendet werden

Der Skill kennzeichnet jede erzeugte Legende mit einem entsprechenden Hinweis im Kopf.

## Notfall-Rückweg ohne Skript

Falls `depseudonymize.py` nicht verfügbar ist (z. B. andere Umgebung ohne Python), kann die Rückumwandlung auch manuell in Word erfolgen: für jede Zeile der Codetabelle „Suchen und Ersetzen" nutzen (Code → Grundform). Die Reihenfolge ist hier egal, weil Codes eindeutig sind und keine Teiltreffer erzeugen. Dieser Weg ist mühsam, aber garantiert funktionsfähig, solange die Legende vorhanden ist.
