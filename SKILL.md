---
name: pseudonymisierung-mandatsdokumente
description: |
  Reversible Pseudonymisierung von Kanzleidokumenten im DOCX-Format
  für die Weiterverarbeitung in offenen KI-Umgebungen. Erkennt Personen,
  Firmen, Behörden, Anschriften, Kontakte, Steuernummern, Register, Konten,
  Aktenzeichen, Geburtsdaten und Objekte in 13 Kategorien. Vier Betriebsarten:
  PSEUDONYMISIEREN, FORTSCHREIBEN, RUECKUMWANDELN, PRUEFEN. Zweiphasig mit
  ausdrücklicher Freigabe, deterministische Ersetzung per Skript,
  strikte Legendentrennung. Beträge, Fristen, Rechtsnormen und Fundstellen
  bleiben unverändert. Erkennt eingebettete Grafiken und Objekte im DOCX
  und weist darauf hin, dass Text darin nicht codiert wird. Trigger:
  pseudonymisieren, anonymisieren, unkenntlich machen, Mandantendaten
  schützen, Dokument für Perplexity vorbereiten, Legende erstellen,
  rückumwandeln, Klarnamen zurückführen. Eingang und Ausgang sind DOCX.
  Andere Formate zuerst mit dem Skill rwt-skill-dokument-nach-docx in
  DOCX überführen.
metadata:
  version: "1.2.1"
---

# Pseudonymisierungs-Skill für Mandatsdokumente

Dieser Skill wandelt ein DOCX-Kanzleidokument in eine pseudonymisierte Fassung um, in der alle direkten und die vom Kontext her identifizierenden Angaben durch Codes ersetzt sind, und führt die Codes bei Bedarf wieder in Klartext zurück. Der Skill trennt strikt zwischen dem Erkennen (Sprachmodell) und dem Ersetzen (deterministisches Skript). Der Anwender behält die Kontrolle über jede Ersetzung durch eine ausdrückliche Freigabephase.

## Wann diesen Skill verwenden

Nutzen Sie den Skill, wenn ein Kanzleidokument in einer offenen KI-Umgebung weiterverarbeitet werden soll und Mandats-, Personen- oder Firmengeheimnisse geschützt bleiben müssen. Nutzen Sie ihn nicht, wenn keine schutzbedürftigen Angaben enthalten sind (interne Notizen ohne Namen, veröffentlichte Muster) oder wenn eine echte Anonymisierung im Sinne des Datenschutzrechts nötig ist. Pseudonymisierung ist keine Anonymisierung: mit der Legende bleibt das Dokument personenbezogen (Art. 4 Nr. 5 DSGVO).

## Vier Betriebsarten

Der Anwender wählt eine Betriebsart durch das erste Wort der Anweisung:

- **PSEUDONYMISIEREN** — Erstverarbeitung eines Dokuments, zweiphasig mit Freigabe
- **FORTSCHREIBEN** — Folgedokument desselben Mandats mit derselben Legende
- **RUECKUMWANDELN** — pseudonymisiertes Dokument plus Legende in Klartext zurückführen
- **PRUEFEN** — Zweitkontrolle eines pseudonymisierten Dokuments ohne Legende, sucht Restklarnamen

## Ablauf PSEUDONYMISIEREN

Der Anwender startet mit:

```
PSEUDONYMISIEREN
Alias: MANDAT-XY
```

Optional Konfiguration in Folgezeilen (Voreinstellungen in Klammern):
`KANZLEI_CODIEREN: ja|nein (ja)`, `GEBDAT_CODIEREN: ja|nein (ja)`, `BETRAEGE_CODIEREN: ja|nein (nein)`, `DATEN_CODIEREN: ja|nein (nein)`.

Der Alias ist der Name der Legende. Er darf keinen Personenbezug tragen.

### Phase 1 — Vorschlagsliste und Freigabe

1. Lesen Sie das gesamte hochgeladene DOCX, einschließlich Kopf- und Fußzeilen, Tabellen und Fußnoten.
2. Erkennen Sie alle Entitäten nach dem Katalog in `references/kategorien-katalog.md`.
3. Rufen Sie `scripts/check_residuals.py` gegen das Original auf, um mit Regex nach harten Mustern zu suchen (Steuer-IDs, IBAN, HRB, USt-IdNr, E-Mail, Telefon). Übernehmen Sie die Treffer in die Vorschlagsliste, wenn sie noch nicht enthalten sind.
4. Geben Sie im Chat aus:
   - **Vorschlagsliste** als Markdown-Tabelle: Kategorie, Grundform, alle Varianten, vorgeschlagener Code, Textstellenzahl.
   - **Zweifelsfälle** als eigene Liste mit klaren Fragen (Namensgleichheiten, Kurzformen, Firmennamen mit Personenbezug, ambivalente Rechtsformzusätze).
   - **Konfiguration**: welche Voreinstellungen aktiv sind, welche der Anwender überschreiben kann.
5. Fordern Sie ausdrücklich `FREIGABE` an. Erzeugen Sie in Phase 1 kein pseudonymisiertes Dokument.

### Phase 2 — Ausführung

Nach `FREIGABE` (mit oder ohne Korrekturhinweisen des Anwenders):

1. Erzeugen Sie eine Änderungskarte als JSON: `{"MANDAT-XY": [{"code": "PERSON_01", "kategorie": "PERSON", "grundform": "Dr. Klaus Vogel", "varianten": ["Herr Dr. Vogel", "Vogels", "K. Vogel"], "kommentar": "..."}, ...]}`. Nutzen Sie die exakte Grundform und alle Varianten aus der Vorschlagsliste, ergänzt um vom Anwender bestätigte Korrekturen.
2. Rufen Sie `scripts/pseudonymize.py` mit dem hochgeladenen DOCX und der Änderungskarte auf. Das Skript erzeugt drei Dateien: `<Name>_PSEUDO.docx`, `<Alias>_LEGENDE_v1.md` und `<Alias>_LEGENDE_v1.json`.
3. Rufen Sie `scripts/check_residuals.py` gegen die PSEUDO-Datei auf. Fassen Sie das Ergebnis im Prüfbericht als „Restsuche" zusammen. Klarnamen dort sind Fehler, die vor Auslieferung korrigiert werden müssen.
4. Prüfen Sie im Pruefbericht von `pseudonymize.py` das Feld `eingebettete_grafiken`. Steht dort `"gefunden": true`, weist das Original eingebettete Bilder oder Objekte auf (z. B. Screenshot, gescannte Unterschrift, eingebettetes Objekt). Text innerhalb dieser Grafiken wird nicht codiert. Geben Sie diesen Hinweis **ausdrücklich und in der Zielumgebung sichtbar** aus, nicht nur im Bericht, damit Anwender in Claract/Askdata die Grafik vor Weitergabe manuell prüfen.
5. Geben Sie im Chat aus:
   - die drei Dateien zum Download
   - einen kurzen **Prüfbericht** in Markdown mit: Anzahl ersetzter Vorkommen je Code, Ergebnis der Restsuche, gekennzeichnete Konfiguration, ausdrücklicher Hinweis „Legende getrennt aufbewahren, nicht in offene Umgebungen laden", und bei Fund von eingebetteten Grafiken einen eigenen Warnabsatz „Eingebettete Grafik erkannt: Text darin ist nicht pseudonymisiert, manuell prüfen".
6. Ergänzen Sie am Anfang der PSEUDO-Datei die Zeile: `[Pseudonymisiertes Dokument · Alias <ALIAS> · Legende v<N> · Codes nicht auflösen]`.

## Ablauf FORTSCHREIBEN

Der Anwender lädt ein neues DOCX und die vorhandene JSON-Legende hoch:

```
FORTSCHREIBEN
Alias: MANDAT-XY
```

1. Lesen Sie das neue Dokument.
2. Lesen Sie die JSON-Legende und übernehmen Sie alle bestehenden Codes unverändert.
3. Identifizieren Sie neue Entitäten, die noch nicht in der Legende stehen. Führen Sie dafür wie in PSEUDONYMISIEREN eine kurze Vorschlagsphase mit `FREIGABE` durch, aber nur für die neuen Entitäten.
4. Nach Freigabe: Änderungskarte erweitern (neue Codes hinter den bestehenden fortlaufend nummerieren), `pseudonymize.py` aufrufen, `check_residuals.py` aufrufen. Ausgabe: neues PSEUDO-Dokument, aktualisierte Legende mit erhöhter Versionsnummer.

## Ablauf RUECKUMWANDELN

Der Anwender lädt ein PSEUDO-DOCX und die zugehörige JSON-Legende hoch:

```
RUECKUMWANDELN
Alias: MANDAT-XY
```

1. Rufen Sie `scripts/depseudonymize.py` mit beiden Dateien auf. Das Skript ersetzt jeden Code deterministisch und ohne Umformulierung. Ab Legendenschema v2 (Skill v1.1) wird jedes Vorkommen positions- und wortgetreu mit der im Original an dieser Stelle verwendeten `originalform` ersetzt. Bei einer alten Legende Schema v1 (Skill v1.0) wird auf die `grundform` zurückgegriffen; der Bericht weist dann darauf hin, dass ein wortgleicher Roundtrip nicht garantiert ist.
2. Geben Sie aus: `<Name>_KLAR.docx` und einen kurzen Rückumwandlungsbericht mit: Anzahl je Code ersetzter Vorkommen, Codes ohne Legendeneintrag (sollte leer sein), Codes in der Legende ohne Vorkommen im Dokument (informativ), Legendenschema (v1 oder v2), Zahl der Grundform-Fallbacks (bei v2 muss 0 sein), Konsistenz des Positionscursors.
3. Ergänzen Sie keine erklärenden Zusätze im Text. Die Kennzeichnungszeile aus Phase 2 wird beim Rückumwandeln entfernt.
4. Ab Skill v1.1 ist Kriterium K5a (Inhaltstreue Roundtrip, harte Grenze: 5 abweichende Absätze; Ziel 0) das Freigabekriterium. Weichen Absätze nach der Rückumwandlung ab, ist entweder die Legende v1 (kein Positionsindex), die Ersetzungsreihenfolge im Ursprungsdokument mehrdeutig, oder das PSEUDO-Dokument wurde manuell nachbearbeitet.

## Ablauf PRUEFEN

Der Anwender lädt nur ein PSEUDO-DOCX hoch (ohne Legende):

```
PRUEFEN
```

1. Rufen Sie `scripts/check_residuals.py` gegen die Datei auf.
2. Lesen Sie das Dokument zusätzlich mit dem Sprachmodell und suchen Sie nach Klarnamen und Inkonsistenzen (verschiedene Codes für dieselbe Person, gleiche Codes für verschiedene Personen).
3. Geben Sie einen Prüfbericht aus: harte Restfunde (aus dem Skript), weiche Verdachtsfälle (aus dem Modell), Gesamtwertung „unauffällig / prüfen / Fehler".
4. Kein Ausgabedokument, nur Bericht.

## Verbindliche Regeln für alle Betriebsarten

1. **Inhaltstreue.** Text nicht umformulieren, nicht zusammenfassen, keine erläuternden Zusätze einfügen. Nur ersetzen.
2. **Nie erfinden.** Wenn eine Entität nicht sicher zuzuordnen ist, in Zweifelsfälle aufnehmen, nicht raten.
3. **Legende getrennt.** Die Legende wird nie in das PSEUDO-Dokument geschrieben, immer als eigene Datei.
4. **Freigabe pflichtig.** Kein PSEUDO-Dokument ohne vorherige `FREIGABE` des Anwenders.
5. **Rechtsnormen, Fundstellen, Beträge, Fristen bleiben stehen.** Vgl. `references/kategorien-katalog.md`, Spalte „Bleibt stehen".
6. **Geburtsdaten werden codiert.** Andere Datumsangaben bleiben stehen, sofern nicht durch Konfiguration umgestellt.
7. **Rechtsformzusätze stehen hinter dem Code.** `[FIRMA_02] GmbH & Co. KG`, nicht `[FIRMA_02]`.
8. **Anhangsdateinamen werden mitcodiert.** Namensbestandteile in Dateinamen sind Identifikatoren.
9. **Dokumente können nur als DOCX verarbeitet werden.** PDF, PPTX, XLSX und andere Formate bitte zuerst mit `rwt-skill-dokument-nach-docx` in DOCX überführen.
10. **Eingebettete Grafiken werden nicht codiert.** Meldet der Pruefbericht `eingebettete_grafiken.gefunden = true`, geben Sie in jedem Fall einen sichtbaren Warnhinweis an den Anwender aus. Siehe `references/roundtrip-grenzen.md`, Abschnitt „Eingebettete Grafiken".

## Codeformat

`[KATEGORIE_NN]` mit zweistelliger Nummer je Kategorie, beginnend bei `01`. Kategorien: `PERSON`, `FIRMA`, `BEHOERDE`, `ORT`, `ANSCHRIFT`, `KONTAKT`, `STNR`, `REGISTER`, `KONTO`, `AZ`, `GEBDAT`, `OBJEKT`, `SONSTIGES`. Ausführliche Beschreibung in `references/kategorien-katalog.md`.

## Kritischer Hinweis zur Änderungskarte

Die Ersetzung ist ein exakter Zeichenkettenabgleich. Grundformen und Varianten müssen **buchstabengetreu** so in der Änderungskarte stehen, wie sie im Dokument vorkommen, einschließlich Umlaute (ä, ö, ü, ß), Bindestriche, Leerzeichen und Zeichensetzung. Beispiele für typische Fehler:

- `Praezisionsteile` in der Karte, aber `Präzisionsteile` im Dokument → das Wort wird nicht ersetzt
- `Industriestrasse 7` in der Karte, aber `Industriestraße 7` im Dokument → die Anschrift wird nicht ersetzt
- `Flurstueck` in der Karte, aber `Flurstück` im Dokument → das Register-Kennzeichen bleibt sichtbar
- Anschriften mit Komma in der Grundform (`Lindenallee 12, 88212 Ravensburg`) und zusätzlich eine Variante nur mit Straße (`Lindenallee 12`) verursachen bei mehrzeiliger Adresse doppelte Nennungen der PLZ nach Rückumwandlung

Regel für die Erstellung der Änderungskarte in Phase 1:

- Grundformen aus dem Dokumenttext kopieren, nicht paraphrasieren
- Mehrteilige Anschriften nur als Kombination aufführen, wenn sie im Original zusammenhängend stehen
- Nach Phase 2 immer den Prüfbericht mit der Restsuche prüfen und zusätzlich den PSEUDO-Text sichten (Sprachmodell), weil die Regex-Restsuche nicht alle Muster kennt

## Selbstkontrollen am Ende jedes Laufs

Vor Auslieferung eines PSEUDO-Dokuments prüfen:

- Enthält die Ausgabe die Kennzeichnungszeile am Anfang? (verbindlich)
- Steht die Legende in einer eigenen Datei? (verbindlich)
- Meldet `check_residuals.py` Klarnamen? (dann: nicht ausliefern, sondern erneut korrigieren)
- Ist die Nummerierung in der Legende lückenlos und je Kategorie eindeutig?

## Referenzen und Beispiele

- `references/kategorien-katalog.md` — die 13 Kategorien mit Beispielen und der „Bleibt stehen"-Liste
- `references/legendenschema.md` — Aufbau der Legende (Kopf, Markdown-Tabelle, JSON-Block)
- `references/regex-muster.md` — die harten Muster, die `check_residuals.py` nutzt
- `references/bedienanleitung.md` — Schrittfolge für Anwender, Fehlerbilder, Ausschluss
- `references/roundtrip-grenzen.md` — Herleitung des Positionsindex und Grenzen des wortgleichen Roundtrips (v1.1), Grenzen bei eingebetteten Grafiken (v1.2)
- `assets/Testdokument_A_Sachverhaltsschreiben.docx` — fiktives Kanzleischreiben mit 31 Entitäten, 7 Fallen; für Testläufe
- `assets/loesungsschluessel_A.md` — Soll-Liste zum Vergleich; **nie in den Bot laden**, nur beim Tester
- `assets/bewertungsbogen.md` — Kriterien K1 bis K10 mit K.o.-Regeln

## Grenzen

Der Skill trennt Erkennen und Ersetzen. Das Ersetzen ist deterministisch und in der Ausgabe garantiert vollständig, wenn die Änderungskarte vollständig ist. Die Vollständigkeit der Änderungskarte hängt von der Erkennung durch das Sprachmodell und vom Regex-Vorfilter ab. Beides ist gut, aber nicht perfekt. Die Freigabephase, die Restsuche und der zweite PRUEFEN-Lauf sind Bestandteil des Verfahrens, kein Zusatz. Für gescannte PDFs oder Bilder ohne Textebene ist der Skill nicht zuständig; nutzen Sie `rwt-skill-dokument-nach-docx` mit OCR-Vorlauf.

**Eingebettete Grafiken im DOCX.** Enthält das Original eine eingebettete Grafik oder ein eingebettetes Objekt (Foto, Screenshot, gescannte Unterschrift, OLE-Objekt), erkennt `pseudonymize.py` dies ab Version 1.2 über den DOCX-Zip-Container und meldet es im Prüfbericht (`eingebettete_grafiken`). Text **innerhalb** der Grafik wird dabei nicht codiert, weil der Skill nur Fließtext durchsucht, keine Texterkennung (OCR) auf Bildinhalten durchführt. Bei Fund ist ein sichtbarer Warnhinweis an den Anwender in der Zielumgebung (Claract/Askdata) verbindlich. Siehe `references/roundtrip-grenzen.md`, Abschnitt „Eingebettete Grafiken".

Keine Rechts-, Steuer- oder Datenschutzberatung. Vor produktivem Einsatz mit der RWT-KI-Richtlinie und dem Datenschutzbeauftragten abstimmen.
