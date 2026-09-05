# Kategorienkatalog

Dreizehn Kategorien, in denen Entitäten codiert werden. Der Bot ordnet in Phase 1 jede erkannte Entität einer Kategorie zu; das Skript ersetzt in Phase 2 mechanisch.

## Codeformat

`[KATEGORIE_NN]` mit zweistelliger, je Kategorie fortlaufender Nummer. Rechtsformzusätze verbleiben unmittelbar hinter dem Code im Text, z. B. `[FIRMA_02] GmbH & Co. KG`, `[FIRMA_04] Steuerberatungsgesellschaft mbH`.

## Die Kategorien

| Kategorie | Umfasst | Beispiele | Codiert |
|---|---|---|---|
| PERSON | Natürliche Personen mit Namen, Titel, Anreden | Dr. Klaus Vogel, Frau Reuter, Herr Brandt | Ja |
| FIRMA | Juristische Personen, Personengesellschaften, Marken, Kanzleien | Vogel Beteiligungs GmbH, Alpenblick Präzisionsteile GmbH & Co. KG | Ja |
| BEHOERDE | Finanzämter mit Ort, Gerichte, Ministerien, Kammern mit Ort | Finanzamt Ravensburg, Amtsgericht Ulm | Ja |
| ORT | Städte, Regionen, Bundesländer, Länder wenn identifizierend | Ravensburg (einzeln stehend) | Ja |
| ANSCHRIFT | Vollständige oder teilweise Postanschriften | Lindenallee 12, 88212 Ravensburg | Ja |
| KONTAKT | E-Mail-Adressen, Telefon-, Fax-, Mobilnummern | a.reuter@reuter-kollegen.de, +49 751 123456-0 | Ja |
| STNR | Steuerliche Identifikationsnummer, Steuernummer, USt-IdNr | 12 345 678 901, 77012/34567, DE812345678 | Ja |
| REGISTER | Handels-, Vereins-, Genossenschaftsregister, UR-Nr, Grundbuchdaten | HRB 734512, HRA 720988, UR-Nr. 1234/2025, Flurstück 1234/5 Blatt 8901 | Ja |
| KONTO | IBAN, BIC, Kontonummer, Bankleitzahl | DE89 3704 0044 0532 0130 00 | Ja |
| AZ | Aktenzeichen, Vorgangsnummern, Mandantennummern | 2026-0417-V | Ja |
| GEBDAT | Geburtsdaten natürlicher Personen | 14.03.1961 | Ja (per Voreinstellung) |
| OBJEKT | Projektnamen, Codenamen, Kaufobjekte mit Bezug zum Mandat | Projekt Aurora | Ja |
| SONSTIGES | Auffangkategorie für sonstige identifizierende Angaben | Interne Codewörter, ungewöhnliche Bezeichner | Ja |

## Bleibt stehen (Muss unverändert bleiben)

Diese Elemente dürfen nicht codiert werden. Sie sind Fundstellen, Fachbegriffe oder Zahlen mit rechtlichem Gehalt, deren Ersetzung den Inhalt entwerten würde.

| Klasse | Beispiele | Grund |
|---|---|---|
| Rechtsnormen | § 20 UmwStG, § 8b Abs. 3 Satz 3 KStG, Art. 4 Nr. 5 DSGVO | Fundstellen, kein Personenbezug |
| Verwaltungsanweisungen | BMF-Schreiben vom 11.11.2011, IV C 2 - S 1978-b/08/10001, BStBl I 2011, 1314, Rn. 20.06 | Fundstellen |
| Gerichtsentscheidungen | BFH-Urteil vom 21.09.2011, I R 89/10 | Fundstellen |
| Beträge und Quoten | 2.350.000 Euro, 60 %, 25 %, 8,5 Prozent | Wirtschaftlicher Gehalt |
| Vorgangs- und Fristdaten | 30.06.2025, 20. August 2026 (Geburtsdaten sind gesondert behandelt, siehe GEBDAT) | Prozessuale und materielle Fristen |
| Rechtsformen | GmbH, GmbH & Co. KG, KGaA, eG, PartG mbB, Stiftung & Co. KG | Steht hinter dem FIRMA-Code, nicht als Code |
| Funktionsbezeichnungen ohne Namen | Notarin, Steuerberater, Betriebsprüfer, Kommanditist, Geschäftsführerin | Rolle, kein Identifikator |
| Gattungsbegriffe ohne Bezug | „das Finanzamt", „die Bank", „unsere Kanzlei", „unser Mandant" | Kein spezifischer Identifikator |
| Fachbegriffe | Teilwertabschreibung, Sperrfrist, Sacheinlage, Rückspaltung | Fachterminologie |
| Fundstellen in Akten | Tz. 41, Rn. 20.06, § 12 des Vertrags | Interne Verweise |

## Zweifelsfälle (immer in Phase 1 nachfragen)

- Personennamen, die auch Firmenbestandteil sind (Vogel als Person und Vogel Beteiligungs GmbH als Firma → beide codieren, unterschiedliche Codes)
- Namensgleichheit verschiedener Personen (zwei Personen Kessler, dritter Vogel) → getrennte PERSON-Codes
- Kurzformen und Vollformen derselben Firma (Alpenblick, Alpenblick Präzisionsteile GmbH & Co. KG) → selber FIRMA-Code
- Ort als Behörden-Bestandteil vs. eigenständig (Finanzamt Ravensburg = BEHOERDE, Ravensburg allein = ORT) → einzeln entscheiden
- Dateinamen im Text (Einbringungsvertrag_Vogel_Alpenblick_30-06-2025.pdf) → Namensteile mitcodieren
- Interne Vermerke in eckigen Klammern → Inhalt erhalten, Namen darin codieren

## Optionale Konfiguration (Voreinstellungen)

Der Anwender kann per Anweisungszeile umstellen:

- `KANZLEI_CODIEREN: ja|nein` (voreingestellt: ja) — auch die eigene Kanzlei wird codiert
- `GEBDAT_CODIEREN: ja|nein` (voreingestellt: ja) — Geburtsdaten werden codiert
- `BETRAEGE_CODIEREN: ja|nein` (voreingestellt: nein) — Geldbeträge bleiben stehen
- `DATEN_CODIEREN: ja|nein` (voreingestellt: nein) — andere Datumsangaben bleiben stehen

Die getroffene Wahl wird im Prüfbericht ausdrücklich dokumentiert.
