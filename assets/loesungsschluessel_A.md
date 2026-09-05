# Lösungsschlüssel Testdokument A (Sachverhaltsschreiben)

Nicht in den Bot laden. Dient ausschließlich der Auswertung nach `06_Bewertungsbogen.md`.

Testdokument A ist ein fiktives Kanzleischreiben mit 2 Seiten. Es enthält 31 zu codierende Entitäten in 12 Kategorien, sieben absichtliche Fallen und neun Elemente, die nicht ersetzt werden dürfen.

## Soll-Liste (Nummerierung des Bots darf abweichen)

Bewertet wird die Gruppierung, nicht die konkrete Nummer. Ein Bot, der Dr. Klaus Vogel als [PERSON_03] führt, liegt richtig, solange alle Varianten denselben Code tragen.

| Nr. | Kategorie | Original (Grundform) | Varianten, die denselben Code tragen müssen | Erwartete Textstellen |
|---|---|---|---|---|
| 1 | PERSON | Dr. Klaus Vogel | Herr Dr. Vogel; Vogels (Genitiv); K. Vogel; Namensteil im Anlagen-Dateinamen | 6 (5 im Text, 1 im Dateinamen) |
| 2 | PERSON | Sabine Vogel | Frau Vogel | 3 |
| 3 | PERSON | Jonas Vogel | | 3 |
| 4 | PERSON | Dr. Anja Reuter | Frau Dr. Reuter | 2 |
| 5 | PERSON | Brandt | Herr Brandt | 2 (davon 1 im internen Vermerk) |
| 6 | PERSON | Dr. Ilse Kaminski | Dr. Kaminski | 2 |
| 7 | PERSON | Prof. Dr. Weber | | 1 |
| 8 | FIRMA | Vogel Beteiligungs | die Beteiligungs-GmbH | 4 |
| 9 | FIRMA | Alpenblick Präzisionsteile | die Alpenblick; Alpenblick; Namensteil im Anlagen-Dateinamen | 6 (5 im Text, 1 im Dateinamen) |
| 10 | FIRMA | Alpenblick Verwaltungs | | 2 |
| 11 | FIRMA | Reuter & Kollegen | die Kanzlei (nur wenn der Bot es so entscheidet, sonst zulässig unverändert) | 2 |
| 12 | FIRMA | Oberland Volksbank | | 1 |
| 13 | BEHOERDE | Finanzamt Ravensburg | | 2 |
| 14 | BEHOERDE | Amtsgericht Ulm | | 2 |
| 15 | ORT | Ravensburg | Ortszeile im Briefkopf; Ortsangabe der Notarin; Signatur | 3 eigenständige Nennungen |
| 16 | ANSCHRIFT | Lindenallee 12, 88212 Ravensburg | | 1 (Anschriftenblock, ggf. zeilenweise) |
| 17 | ANSCHRIFT | Industriestraße 7, 88214 Ravensburg | Industriestraße 7 (Tabelle) | 2 |
| 18 | KONTAKT | a.reuter@reuter-kollegen.de | | 1 |
| 19 | KONTAKT | +49 751 123456-0 | | 1 |
| 20 | STNR | 77012/34567 | | 1 |
| 21 | STNR | DE812345678 | | 1 |
| 22 | STNR | 12 345 678 901 | | 1 |
| 23 | REGISTER | HRB 734512 | | 1 |
| 24 | REGISTER | HRA 720988 | | 1 |
| 25 | REGISTER | UR-Nr. 1234/2025 | | 1 |
| 26 | REGISTER | Flurstück 1234/5, Grundbuch von Ravensburg Blatt 8901 | (auch als zwei Codes zulässig) | 1 |
| 27 | KONTO | DE89 3704 0044 0532 0130 00 | | 1 |
| 28 | AZ | 2026-0417-V | | 1 |
| 29 | GEBDAT | 14.03.1961 | | 1 |
| 30 | OBJEKT | Projekt Aurora | Aurora | 2 |
| 31 | FIRMA oder KONTAKT | reuter-kollegen (Domain in der E-Mail) | | in Nr. 18 enthalten; kein eigener Code nötig |

Zulässige Abweichungen: „Ravensburg" innerhalb von Nr. 13, 16, 17 und 26 muss nicht zusätzlich als ORT codiert sein, wenn der umgebende Block als Ganzes codiert ist. Wichtig ist nur: Im Ergebnis darf das Wort „Ravensburg" an keiner Stelle mehr stehen.

## Die sieben Fallen

| Falle | Erwartetes Verhalten | Typischer Fehler |
|---|---|---|
| F1 Genitiv „Vogels Anteil" | gleicher Code wie Dr. Klaus Vogel, ggf. „der Anteil von [PERSON_xx]" | eigener Code oder Übersehen |
| F2 Initiale „K. Vogel" | gleicher Code wie Dr. Klaus Vogel | eigener Code |
| F3 Drei Personen Vogel | drei verschiedene PERSON-Codes; Frau Vogel = Sabine, nicht Klaus | Zusammenfassung zu einem Code |
| F4 Name im Firmennamen „Vogel Beteiligungs GmbH" | FIRMA-Code, Legendenhinweis „enthält Namen von [PERSON_xx]"; nicht PERSON-Code | Person-Code im Firmennamen oder Firmenname übersehen |
| F5 Kurzform „die Alpenblick" und Komplementärin „Alpenblick Verwaltungs GmbH" | Kurzform = KG-Code; Verwaltungs-GmbH eigener Code | Kurzform zur Verwaltungs-GmbH gezählt oder umgekehrt |
| F6 Anlagen-Dateiname „Einbringungsvertrag_Vogel_Alpenblick_30-06-2025.pdf" | Namensteile ersetzt: „Einbringungsvertrag_[PERSON_xx]_[FIRMA_yy]_30-06-2025.pdf" | Dateiname unverändert |
| F7 Interner Vermerk in eckigen Klammern mit „Brandt" | Vermerk bleibt inhaltlich stehen, Name codiert | Vermerk gelöscht (Inhaltsänderung) oder Name übersehen |

## Muss unverändert bleiben (Überpseudonymisierung)

| Element | Grund |
|---|---|
| § 20 Abs. 1 UmwStG, § 20 Abs. 2 Satz 2 UmwStG, § 22 Abs. 1 UmwStG, § 8b Abs. 3 Satz 3 KStG | Rechtsnormen |
| BMF-Schreiben vom 11.11.2011, IV C 2 - S 1978-b/08/10001, BStBl I 2011, 1314, Rn. 20.06 | Verwaltungsanweisung mit Aktenzeichen (Kategorie AZ schließt Fundstellen aus) |
| BFH-Urteil vom 21.09.2011, I R 89/10 | Gerichtsentscheidung als Fundstelle |
| 2.350.000 Euro, 480.000 Euro, 312.400 Euro, 9.800.000 Euro, 60 %, 25 %, 15 %, 0 % | Beträge und Quoten |
| 30.06.2025, 31.12.2024, 18.06.2025, 12.08.2026, 15.05.2025, 15.10.2026, 30.09.2026, 07.10.2026, 30.06.2032, 20. August 2026 | Vorgangs- und Fristdaten (nur das Geburtsdatum wird codiert) |
| „das Finanzamt" (ohne Ort, Abschnitt 4) | Gattungsbegriff |
| „Notarin", „Steuerberaterin", „Komplementärin", „Kommanditanteile" | Funktions- und Fachbegriffe |
| „GmbH", „GmbH & Co. KG", „eG", „Steuerberatungsgesellschaft mbH" | Rechtsformen bleiben hinter dem Code |
| Hinweiszeile „Fiktive Übungsunterlage ..." am Dokumentanfang | Kein Identifikator |

## Roundtrip-Erwartung

Nach RUECKUMWANDELN des unveränderten PSEUDO-Dokuments muss der Text mit dem Original bis auf zwei zulässige Abweichungen identisch sein: (1) „Vogels Anteil" darf als „der Anteil von Dr. Klaus Vogel" zurückkommen, wenn der Bot in Phase 2 umgestellt hat; (2) die Kennzeichnungszeile aus Phase 2 ist entfernt. Jede weitere Abweichung ist ein Inhaltstreue-Fehler.

Kontrollweg ohne KI: Original-DOCX und KLAR-DOCX in Word über „Überprüfen > Vergleichen" gegenüberstellen.
