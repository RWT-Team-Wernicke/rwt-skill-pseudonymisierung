# Lösungsschlüssel Testdokument B (Nordmark-Mailverlauf)

Nicht in den Bot laden. Dient ausschließlich der Auswertung nach `06_Bewertungsbogen.md`.

Testdokument B ist kein neues Dokument, sondern der bereits im Projekt vorhandene fiktive Mandanten-Mailverlauf aus dem Selbstschulungs-Materialsatz:

`Selbstschulung-Materialsatz/260828_Schulung_Mailverlauf_Nordmark.pdf` (6 Seiten, zehn Nachrichten; Textfassung `.txt` daneben)

Er eignet sich als zweiter Testfall, weil er die typischen Schwächen von E-Mail-Exporten enthält: Kopfzeilen mit Adressen, verschachtelte Zitatblöcke, wechselnde Betreffzeilen, Signaturen, Anhangsnamen, ein Deckblatt mit Beteiligtenliste und eine bewusst eingebaute Namensfalle. Das Dokument ist vollständig erfunden und enthält keine Mandatsdaten.

## Soll-Liste

| Nr. | Kategorie | Original (Grundform) | Varianten, die denselben Code tragen müssen | Anmerkung |
|---|---|---|---|---|
| 1 | PERSON | Torben Kessler | Herr Kessler (in Anreden des Beraters); Kessler (Signatur „Gruß, Torben Kessler") | Kaufmännischer Leiter, Absender der meisten Mails |
| 2 | PERSON | Kessler (Betriebsprüfer) | „ein Herr Kessler vom Finanzamt" (Mail vom 22.01.2026, 14:20); „Regierungsamtsrat Kessler" (Deckblatt) | Andere Person als Nr. 1. Namensfalle |
| 3 | PERSON | Hellwege | Herr Hellwege; Hellwege, Steuerberater; Steuerberater Hellwege | Berater; Name auch Bestandteil von Nr. 6 |
| 4 | PERSON | Sondermann | Rechtsanwältin Sondermann; Sondermann, Rechtsanwältin | Beraterin |
| 5 | PERSON | Alfons Ostermeier | | Nur im Deckblatt genannt |
| 6 | FIRMA | Hellwege & Partner | Kanzlei Hellwege & Partner PartG mbB; Kanzlei Hellwege; „bei uns in der Kanzlei" (Gattungsbegriff, kein Code nötig) | Kanzlei; enthält Namen von Nr. 3 |
| 7 | FIRMA | Nordmark Präzisionstechnik Holding | Nordmark; Namensteil im Anhang „Bp-Bericht_Nordmark_120_Seiten.pdf"; Kopfzeile jeder Seite | Mandantin |
| 8 | FIRMA | Vektor | die Vektor; Namensteil im Anhang „Darlehensuebersicht_Vektor_2020-2024.xlsx"; Betreffzeilen | Tochtergesellschaft; im Mailverlauf nur als Kurzform „Vektor" |
| 9 | FIRMA | Kavaris | „die Kavaris-Sache" | Ehemaliger Kunde, einmalige Nennung in Alltagssprache |
| 10 | FIRMA | Marlow Corporate Finance | | Berater im Verkaufsprozess 2022 |
| 11 | BEHOERDE | Finanzamt für Großbetriebsprüfung Lüneburg | | Nur im Deckblatt; „vom Finanzamt", „beim Finanzamt" im Text sind Gattungsbegriffe und bleiben |
| 12 | KONTAKT | t.kessler@nordmark-holding.de | | Mehrfach in Kopfzeilen |
| 13 | KONTAKT | hellwege@hellwege-partner.de | | Mehrfach in Kopfzeilen |
| 14 | KONTAKT | sondermann@hellwege-partner.de | | Cc-Zeile |

Ergänzend zulässig: ORT „Lüneburg" als eigener Code, wenn der Bot die Behörde nicht als Block codiert. Im Ergebnis darf „Lüneburg" nicht mehr stehen.

## Die fünf Fallen

| Falle | Erwartetes Verhalten |
|---|---|
| F1 Zwei Personen Kessler | Zwei PERSON-Codes. Der Satz „witzigerweise derselbe Nachname wie ich" bleibt inhaltlich erhalten und ergibt nach Codierung „ein Herr [PERSON_02] vom Finanzamt, witzigerweise derselbe Nachname wie ich" |
| F2 Hellwege als Person und als Kanzleiname | PERSON-Code für die Person, FIRMA-Code für „Kanzlei Hellwege" und „Hellwege & Partner PartG mbB"; Legendenhinweis auf den Zusammenhang |
| F3 Zitatverschachtelung | Alle Nennungen in Zitatblöcken („Am 17.02.2026 um 09:15 schrieb Hellwege, Steuerberater:") codiert, nicht nur die Kopfzeilen |
| F4 Seitenkopfzeile „Mandanten-Mailverlauf · Nordmark Präzisionstechnik Holding GmbH" | Auf jeder Seite codiert, nicht nur auf der ersten |
| F5 Deckblatt mit Beteiligtenliste und Hinweisen | Wird mitverarbeitet; Ostermeier, Regierungsamtsrat Kessler und Finanzamt Lüneburg dürfen nicht übersehen werden |

## Muss unverändert bleiben

| Element | Grund |
|---|---|
| Alle Datums- und Zeitangaben (22.01.2026 bis 18.02.2026; 14.11.2022; 03.12.2024; Uhrzeiten) | Vorgangsdaten |
| „so um die 5,5 Millionen", „um die 2,4 Prozent", „2020", „2022", „Mitte 2023" | Beträge, Quoten, Jahreszahlen |
| „Tz. 41", „Tz. 44", „§ 12" des Anteilskaufvertrags | Fundstellen innerhalb der Akte |
| „Bp-Bericht", „Gesellschafterdarlehen", „Rangrücktritt", „Sicherungsübereignung", „Teilwertabschreibung" | Fachbegriffe |
| „vom Finanzamt", „beim Finanzamt" (ohne Ort) | Gattungsbegriffe |
| „Steuerberater", „Rechtsanwältin", „kaufmännischer Leiter", „Betriebsprüfer", „unser Anwalt", „unsere Buchhaltung", „die Bank" | Funktionsbezeichnungen ohne Namen |
| Der interne Kanzleivermerk in eckigen Klammern (Mail Sondermann vom 16.02.2026) | Inhalt bleibt; nur Namen darin codiert |
| Fußzeile „Fiktive Übungsunterlage. Keine Mandatsdaten." | Kein Identifikator |

## Besondere Prüfpunkte für Testdokument B

- Der Bot muss Nummer 1 und Nummer 2 in Phase 1 als Zweifelsfall Z1 ausweisen oder von sich aus trennen. Fasst er beide zusammen, ist die Konsistenzprüfung nicht bestanden, auch wenn alles andere stimmt.
- „die Bank" bleibt unverändert, weil im Mailverlauf kein Bankname genannt wird. Ein Bot, der hier einen FIRMA-Code vergibt, erfindet eine Entität (Regel 2).
- Dieses Dokument ist als PDF vorhanden. Es testet damit zugleich, ob Claract PDF-Eingaben verarbeitet und in welchem Format der Bot das Ergebnis ausgibt.
