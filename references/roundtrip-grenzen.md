# Roundtrip-Grenzen und der Positionsindex

Diese Referenz erklaert, warum Skill v1.0 keinen wortgleichen Roundtrip
liefern konnte, wie Skill v1.1 das Problem loest und wo weiterhin Grenzen
bleiben. Sie ist die Herleitung fuer Kriterium K5a im Bewertungsbogen.

## Ausgangsproblem in v1.0

In v1.0 speicherte die Legende je Code nur:

- eine Grundform (z. B. "Dr. Klaus Vogel"), und
- eine Liste von Varianten (z. B. "Herr Dr. Vogel", "Vogels", "K. Vogel").

`pseudonymize.py` ersetzte alle diese Zeichenketten mit `[PERSON_01]`,
`depseudonymize.py` uebersetzte jedes `[PERSON_01]` wieder mit der
**Grundform**. Damit war der Roundtrip garantiert **nicht wortgleich**,
sobald der Originaltext irgendwo eine Variante statt der Grundform
verwendete. Im Freigabetest TEST-A Lauf 1 fuehrte das zu neun stilistisch
abweichenden Absaetzen (u. a. "Sehr geehrter Herr Dr. Vogel," gegen
"Sehr geehrter Dr. Klaus Vogel,").

Nach der strengen K5-Lesart (harte Grenze fuenf Abweichungen) war
Skill v1.0 damit nicht produktiv freigabefaehig.

## Loesungsansatz: Positionsindex je Code

Die Legende Schema v2 fuehrt je Code das Feld `vorkommen` mit einer
Liste stellenbezogener Eintraege:

```json
"vorkommen": [
  {"position": 1, "originalform": "Dr. Klaus Vogel"},
  {"position": 2, "originalform": "Herr Dr. Vogel"},
  {"position": 3, "originalform": "Vogels"}
]
```

- `position` beginnt je Code bei 1 und zaehlt in Textreihenfolge
  im PSEUDO-Dokument.
- `originalform` ist die exakte Zeichenkette an dieser Stelle im
  Ursprungsdokument.

`depseudonymize.py` fuehrt einen codebezogenen Cursor: das n-te
Vorkommen von `[PERSON_01]` wird mit `vorkommen[n].originalform`
ersetzt. Damit ist der Roundtrip wortgleich, solange:

1. das PSEUDO-Dokument zwischen Pseudonymisierung und Rueckumwandlung
   nicht manuell veraendert wurde,
2. die Iterationsreihenfolge (Absaetze -> Tabellen -> Kopf-/Fusszeilen)
   beim Rueckumwandeln dieselbe ist wie beim Pseudonymisieren (das
   sichert der Skill durch identischen Traversierungscode in beiden
   Skripten),
3. keine zusaetzlichen Codes eingefuegt oder entfernt wurden.

## Algorithmus in v1.1

Fuer jeden Absatz laeuft in `pseudonymize.py`:

1. **Kandidatensuche.** Fuer jeden Suchtext (Grundform oder Variante)
   werden alle Vorkommen im Absatz als Kandidat (start, end, code,
   suchtext) gesammelt.
2. **Ueberlappungsaufloesung.** Kandidaten werden sortiert nach:
   (Startposition aufsteigend, Trefferlaenge absteigend, Grundform vor
   Variante). Ein Greedy-Durchlauf akzeptiert den ersten Kandidaten
   und ueberspringt alle spaeteren, deren Start noch im belegten Bereich
   liegt. Damit gewinnt bei Ueberlappung immer der laengere Treffer
   (z. B. "Dr. Klaus Vogel" vor "Vogel").
3. **Positionsvergabe in Textreihenfolge.** Ueber die akzeptierten
   Treffer wird in Textreihenfolge iteriert und je Code eine
   Positionsnummer vergeben, die zusammen mit der Originalform in die
   Legende geschrieben wird.
4. **Ersetzung von hinten nach vorne.** Die tatsaechliche Textmutation
   erfolgt in umgekehrter Reihenfolge, damit die Indizes waehrend der
   Ersetzung stabil bleiben.

Das ist die entscheidende Verbesserung gegenueber einer naiven
Reihenfolge nach Zeichenkettenlaenge: die Positionsnummerierung folgt
strikt der Textreihenfolge im Original, nicht der Sortierordnung der
Suchliste. Ohne diese Trennung waere im Absatz mit "Vogels ... K. Vogel"
die Positionierung vertauscht worden und der Rueckumwandlungstext
lautete "K. Vogel ... Vogels".

## Grenzen des wortgleichen Roundtrips

Auch mit v1.1 ist ein wortgleicher Roundtrip in folgenden Faellen nicht
garantiert:

- **Manuelle Aenderung am PSEUDO-Dokument.** Wird ein `[CODE]` per Hand
  eingefuegt, geloescht oder verschoben, laeuft der Cursor auseinander.
  Der Skill erkennt das an einer Cursor-Konsistenzverletzung und meldet
  sie im Rueckumwandlungsbericht.
- **Alte Legende Schema v1.** Wortgleicher Roundtrip nicht moeglich;
  Bericht warnt.
- **Formatierungsbedingte Textrisse.** Fett gesetzte Einzelworte
  innerhalb einer Variante koennen dazu fuehren, dass ein Absatz beim
  Zusammenlesen der Runs nicht mit der Variante uebereinstimmt und die
  Variante nicht als Treffer erkannt wird. Der Skill fasst deshalb pro
  Absatz alle Runs zu einem einzigen Text zusammen. Nachteil: die
  Feinformatierung innerhalb des Absatzes geht beim ersten Run auf.
  Fuer Kanzleitexte (durchgehende Formatierung je Absatz) ist das
  akzeptabel; fuer stark ausgezeichnete Textteile ist es eine bekannte
  Grenze.
- **Kopf-, Fusszeilen und Tabellenzellen** werden mit derselben Logik
  behandelt, ihre Iterationsreihenfolge (Body -> Tables -> Sections)
  ist in Pseudonymisierung und Rueckumwandlung identisch. Aenderungen
  an der Section-Struktur zwischen den beiden Laeufen sind nicht
  vorgesehen.

## Beziehung zu Kriterium K5

- **K5a Inhaltstreue Roundtrip:** Ziel 0 abweichende Absaetze; harte
  Grenze 5. Ab v1.1 mit Schema v2 realistisch erreichbar.
- **K5b Formtreue:** unabhaengig davon, dass keine Umformulierung,
  Zusatz- oder Loeschtaetigkeit stattfindet. Wird bei Sichtpruefung
  geprueft.

## Migration alter PSEUDO-Dokumente

Ein PSEUDO-Dokument aus v1.0 laesst sich nicht rueckwirkend mit einer
Schema-v2-Legende ausstatten: der Positionsindex haengt vom
Textabgleich mit dem Original ab. Ist das Original noch verfuegbar,
kann das Dokument mit v1.1 neu pseudonymisiert werden. Ist das Original
nicht mehr verfuegbar, bleibt nur die Rueckumwandlung mit v1-Legende
(Grundform, K5a nur zufaellig erfuellt).
