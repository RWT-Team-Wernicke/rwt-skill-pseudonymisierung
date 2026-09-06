# Bewertungsbogen: Kann der Claract-Bot pseudonymisieren? (Version 1.0, Stand 2026-09-04)

Zweck: Reproduzierbare Antwort auf die Frage, ob der Bot die Aufgabe zuverlässig genug für den Einsatz mit echten Mandatsdokumenten erfüllt. Je Testlauf einen Bogen ausfüllen. Mindestens drei Läufe je Testdokument, weil Sprachmodelle nicht deterministisch arbeiten; ein einzelner bestandener Lauf sagt wenig.

## Kriterien

| Nr. | Kriterium | Messung | Ziel | K.o.? |
|---|---|---|---|---|
| K1 | Vollständigkeit (Recall) | Anzahl codierter Soll-Entitäten geteilt durch Soll-Anzahl aus dem Lösungsschlüssel; getrennt für Direktidentifikatoren (PERSON, FIRMA, KONTAKT, STNR, REGISTER, KONTO, AZ, GEBDAT, ANSCHRIFT) und Kontextidentifikatoren (BEHOERDE, ORT, OBJEKT) | Direkt 100 %, Kontext mindestens 90 % | Ja: ein übersehener Direktidentifikator im freigegebenen Ergebnis = Lauf nicht bestanden |
| K2 | Textstellen-Vollständigkeit | Für jede erkannte Entität: Anzahl ersetzter Vorkommen geteilt durch tatsächliche Vorkommen (Strg+F im Ergebnis nach Original-Schreibweisen) | 100 % | Ja: ein Klarname an irgendeiner Textstelle = Lauf nicht bestanden |
| K3 | Überpseudonymisierung (Precision) | Anzahl fälschlich codierter Elemente aus der Liste „Muss unverändert bleiben" | 0, höchstens 2 mit nachvollziehbarer Begründung des Bots | Nein |
| K4 | Konsistenz | Eine Entität, ein Code; verschiedene Entitäten, verschiedene Codes; alle Fallen des Lösungsschlüssels bestanden | Alle Fallen bestanden | Ja bei zusammengelegten Personen (F3 in A, F1 in B) |
| K5 | Inhaltstreue (Roundtrip) | Original und KLAR-Fassung nach RUECKUMWANDELN in Word vergleichen; Anzahl abweichender Wörter ohne die zulässigen Ausnahmen des Lösungsschlüssels | 0 | Nein, aber ab 5 Abweichungen Verfahren nicht produktiv nutzbar |
| K6 | Rückwandelbarkeit | Rückumwandlungsbericht Abschnitt b) „Codes ohne Legendeneintrag" und Abgleich Tabelle gegen JSON-Block der Legende | Leer; Tabelle und JSON stimmen überein | Ja bei Codes ohne Eintrag |
| K7 | Formatreue | Überschriften, Absätze, Tabelle, Aufzählungen im PSEUDO-Dokument erhalten; Dateiausgabe im Eingabeformat | Erhalten | Nein |
| K8 | Prozessdisziplin | Phase 1 vor Phase 2 eingehalten; Legende getrennt ausgegeben; Prüfbericht mit Restsuche geliefert; Zweifelsfälle sinnvoll | Alle vier Punkte | Ja, wenn die Legende im PSEUDO-Dokument steht |
| K9 | Robustheit gegen den Rückweg | Perplexity-Ergebnis mit Übergabeprompt: Anzahl veränderter oder erfundener Codes | 0 | Nein, aber Hinweis auf Übergabeprompt-Qualität |
| K10 | Bedienaufwand | Minuten je Dokument (Upload bis freigegebene Ausgabe), Anzahl Korrekturrunden in Phase 1 | Richtwert unter 15 Minuten, höchstens 2 Runden für ein 2-seitiges Dokument | Nein |

Gesamturteil je Lauf: „bestanden", wenn kein K.o.-Kriterium ausgelöst wurde und K3, K5, K7 im Zielbereich liegen. „bestanden mit Auflagen", wenn kein K.o., aber K3, K5 oder K7 außerhalb des Ziels. Sonst „nicht bestanden".

Freigabeempfehlung für echte Dokumente erst, wenn mindestens drei von drei Läufen je Testdokument „bestanden" oder „bestanden mit Auflagen" sind und kein Lauf einen Klarnamen durchgelassen hat. Die Freigabe selbst trifft die Kanzlei (Berufsrecht, Datenschutz), nicht dieser Bogen.

## Protokollblatt (je Lauf kopieren)

```
TESTLAUF Nr. ___   Datum: ________   Tester: ________
Testdokument:  [ ] A Sachverhaltsschreiben (DOCX)   [ ] B Nordmark-Mailverlauf (PDF)   [ ] anderes: ________
Umgebung: Claract, Bot-Version 1.0, Modell (falls wählbar/ersichtlich): ________
Systemprompt vollständig eingefügt: [ ] ja  [ ] gekürzt (Abschnitte: ________)

K1  Recall direkt: ___ / ___ = ___ %     Recall Kontext: ___ / ___ = ___ %
    Übersehene Entitäten: ______________________________________________
K2  Klarnamen im Ergebnis gefunden (Strg+F): [ ] keine  [ ] ja: _________________
K3  Fälschlich codiert: ___ Elemente: __________________________________
K4  Fallen bestanden: A: F1[ ] F2[ ] F3[ ] F4[ ] F5[ ] F6[ ] F7[ ]   B: F1[ ] F2[ ] F3[ ] F4[ ] F5[ ]
K5  Roundtrip-Abweichungen (Word-Vergleich): ___   Beispiele: _______________
K6  Codes ohne Legendeneintrag: ___   Tabelle = JSON: [ ] ja [ ] nein
K7  Format erhalten: [ ] ja [ ] teilweise: ____________ [ ] nein   Ausgabeformat: ______
K8  Phase 1 vor Phase 2 [ ]  Legende getrennt [ ]  Prüfbericht mit Restsuche [ ]  Zweifelsfälle sinnvoll [ ]
K9  Perplexity-Rückweg getestet: [ ] nein  [ ] ja, veränderte/erfundene Codes: ___
K10 Dauer: ___ min   Korrekturrunden Phase 1: ___

K.o. ausgelöst: [ ] nein  [ ] ja, Kriterium: ___
Gesamturteil: [ ] bestanden  [ ] bestanden mit Auflagen  [ ] nicht bestanden
Beobachtungen / Prompt-Änderungsbedarf:
_____________________________________________________________________
```

## Auswertung über alle Läufe

| Lauf | Dokument | Modell | K1 direkt | K2 | K3 | K4 | K5 | K6 | K8 | Urteil |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | | | | | | | | | |
| 2 | A | | | | | | | | | |
| 3 | A | | | | | | | | | |
| 4 | B | | | | | | | | | |
| 5 | B | | | | | | | | | |
| 6 | B | | | | | | | | | |

## Was die Ergebnisse für die Weiterentwicklung bedeuten

- K1 oder K2 wiederholt verfehlt: Der Bot liest nicht das ganze Dokument oder verliert Aufmerksamkeit in Zitatblöcken und Kopfzeilen. Abhilfe: Dokument teilen, stärkeres Modell, oder im Systemprompt die Regel 6 um ein konkretes Beispiel aus dem Fehlerfall ergänzen. Bleibt es dabei, ist ein LLM-Bot für diese Aufgabe allein nicht ausreichend; dann wäre ein deterministischer Vorfilter (Regex für Nummernmuster, Adressen, E-Mails) auf Anbieterseite nötig.
- K3 wiederholt verfehlt: Bot ist übervorsichtig bei Fundstellen. Abhilfe: Beispiele im Abschnitt KATEGORIEN, Spalte „Bleibt stehen", erweitern.
- K4 verfehlt: Namensfallen. Abhilfe: Phase 1 ernst nehmen, Zweifelsfälle als Pflichtausgabe betonen.
- K5a verfehlt bei Skill v1.1 (Legende Schema v2): Positionsindex oder Cursor stimmen nicht. Mögliche Ursachen: das PSEUDO-Dokument wurde nachträglich manuell geändert, die Legende gehört zu einer anderen Fassung, oder die Iterationsreihenfolge des Dokuments hat sich zwischen Pseudonymisierung und Rückumwandlung verändert. Bei Skill v1.0 (Schema v1) ist K5a strukturell nur zufällig erreichbar; dann Legende neu erzeugen.
- K5b verfehlt: Der Bot „verbessert" Text. Abhilfe: Regel 1 im Prompt an den Anfang der Ausführungsanweisung wiederholen; bei anhaltendem Problem mechanischer Rückweg (Word Suchen-Ersetzen) als Standard.
- K8 verfehlt: Der Bot ignoriert die Phasen. Prüfen, ob Claract den Systemprompt kürzt oder ein Zeichenlimit hat.

Alle Beobachtungen mit Datum und Modell festhalten. Sie sind die Grundlage für Version 1.1 des Systemprompts und für die Entscheidung, ob das Verfahren in die RWT-KI-Richtlinie aufgenommen wird.
