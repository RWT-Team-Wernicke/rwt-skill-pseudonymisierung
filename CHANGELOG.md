# Changelog

Alle nennenswerten Aenderungen an `rwt-skill-pseudonymisierung`.

Versionsangabe ist der Wert `version` im Frontmatter von `SKILL.md`.
Datumsangaben beziehen sich auf den Merge nach `main`.

---

## v1.2 (2026-09-07)

Commit `451582cc`, Pull Request #2.

### Neu

- **Erkennung eingebetteter Grafiken und Objekte.** `pseudonymize.py`
  liest den DOCX-Zip-Container direkt und prueft die Ordner
  `word/media/` (Bilder) und `word/embeddings/` (eingebettete Objekte,
  z. B. OLE-Objekte).
- **Neues Feld im Pruefbericht:** `eingebettete_grafiken` mit `gefunden`,
  `anzahl_bilder`, `anzahl_objekte` und Dateiliste. Bei Fund zusaetzlich
  `hinweis_grafiken`.
- **Warnung auf stderr** bei Fund, mit Anzahl der Funde und Verweis auf
  die Dokumentation.

### Anlass

Anwendungsfinding aus der Praxis: Text innerhalb einer eingebetteten
Grafik wird von der Codierung nicht erfasst, weil das Skript nur
Fliesstext in `paragraph.runs` durchsucht und keine Texterkennung auf
Bildinhalten durchfuehrt. Ein Klarname, der nur als Bildbestandteil im
Dokument steht (eingescannter Briefkopf, Screenshot einer E-Mail,
Signatur als Bild), blieb dadurch im PSEUDO-Dokument sichtbar, auch wenn
derselbe Name im Fliesstext korrekt codiert wurde.

### Ausdrueckliche Grenze

Die Erkennung stellt fest, **dass** Grafiken vorhanden sind, nicht
**was** darauf zu sehen ist. Eine automatische Schwaerzung oder
OCR-gestuetzte Codierung von Grafikinhalten ist nicht Teil des Skills.
Die Sichtpruefung bleibt Aufgabe des Anwenders.

### Dokumentation

- `references/roundtrip-grenzen.md`: neuer Abschnitt "Eingebettete
  Grafiken"
- `SKILL.md`: neuer Ablaufschritt mit Pflicht zum sichtbaren
  Warnhinweis in der Zielumgebung, neue Regel 10, ergaenzter Abschnitt
  "Grenzen"
- `README.md`: Versionsstand und Kurzhinweis

### Tests

- Regressionslauf gegen `assets/Testdokument_A_Sachverhaltsschreiben.docx`
  (grafikfrei): `gefunden: false`, 30 Ersetzungen unveraendert
- Positivtest mit eingebettetem Bild: `gefunden: true`,
  `anzahl_bilder: 1`, Warnung erscheint
- Vollstaendiger Rundlauf Pseudonymisieren, Restsuche, Rueckumwandeln:
  0 Restfunde, Status OK, keine Positionsindex-Fallbacks
- Textvergleich Original gegen Rueckumwandlung (K5a): 0 abweichende
  Absaetze

Keine Aenderung an Legendenschema v2, `depseudonymize.py` oder
`check_residuals.py`.

---

## v1.1 (2026-09-06)

Commit `94c867af`, Pull Request #1.

### Neu

- **Legendenschema v2 mit Positionsindex.** Je Code wird nicht nur die
  Grundform gespeichert, sondern zusaetzlich eine Liste `vorkommen` mit
  Position und `originalform` jeder einzelnen Ersetzung.
- **Wortgleicher Roundtrip.** `depseudonymize.py` setzt an jeder Stelle
  die dort tatsaechlich vorgefundene Originalform zurueck, nicht die
  Grundform.

### Anlass

Der Freigabetest TEST-A, Lauf 1, verfehlte Kriterium K5 (Inhaltstreue
Roundtrip) nach strenger Lesart mit 9 Abweichungen gegenueber einer
harten Grenze von 5. Alle 9 waren Grundform-statt-Variante-Ersetzungen:
aus "Sehr geehrter Herr Dr. Vogel," wurde bei der Rueckumwandlung "Sehr
geehrter Dr. Klaus Vogel,". Ursache war strukturell, nicht modellbedingt:
die Legende in Fassung v1.0 kannte je Code nur eine Grundform und eine
Menge von Varianten, aber keine stellenbezogene Zuordnung. Damit war
v1.0 nicht produktiv freigabefaehig.

### Tests

- Erneuter TEST-A-Lauf: Absatzzahl in Original und KLAR identisch,
  0 inhaltlich abweichende Absaetze
- K5a (Zielwert 0): erfuellt

### Hinweis zur Rueckwaertskompatibilitaet

Ein PSEUDO-Dokument aus v1.0 laesst sich nicht rueckwirkend mit einer
Schema-v2-Legende ausstatten, weil der Positionsindex zum Zeitpunkt der
Ersetzung entsteht. Einzelheiten in `references/roundtrip-grenzen.md`.

---

## v1.0 (2026-09-05)

Commit `49edddfb`, Erstimport.

### Umfang der ersten Fassung

- Vier Betriebsarten: `PSEUDONYMISIEREN`, `FORTSCHREIBEN`,
  `RUECKUMWANDELN`, `PRUEFEN`
- 13 Kategorien, Codeformat `[KATEGORIE_NN]`
- Zweiphasiges Verfahren: Vorschlagsliste mit ausdruecklicher Freigabe,
  danach deterministische Ersetzung per Skript
- Strikte Legendentrennung, Ausgabe tabellarisch und als JSON
- Betraege, Fristen, Rechtsnormen und Fundstellen bleiben unveraendert
- Drei Skripte: `pseudonymize.py`, `depseudonymize.py`,
  `check_residuals.py`
- Testmaterial: fiktives Sachverhaltsschreiben mit 31 Entitaeten und
  7 absichtlichen Namensfallen, Loesungsschluessel, Bewertungsbogen

Ergebnis des Freigabetests: nach strenger Lesart nicht bestanden, siehe
v1.1.

---

## Verfahren

Aenderungen gelangen ausschliesslich ueber Feature-Branch und Pull
Request nach `main`. Die Repository-Rule auf `main` erzwingt den
Statuscheck "Syntax, Import und Rundlauf" und damit den PR-Weg auch fuer
Eigentuemer.

---

Interner Skill der RWT-Gruppe / Die TaxMaxen.
Keine Rechts-, Steuer- oder Datenschutzberatung. Vor produktivem Einsatz
mit der RWT-KI-Richtlinie und dem Datenschutzbeauftragten abstimmen.
