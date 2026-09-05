# Regex-Muster für die Restsuche

`scripts/check_residuals.py` sucht mit diesen Mustern nach harten Direktidentifikatoren. Die Muster sind bewusst konservativ (eher zu viele Treffer als zu wenige). Sie ersetzen nicht die inhaltliche Prüfung durch das Sprachmodell, sondern ergänzen sie.

## Muster und Zweck

| Name | Was es fängt | Beispiel | Bemerkung |
|---|---|---|---|
| IBAN | Ländercode + 2 Prüfziffern + Kontonummer | DE89 3704 0044 0532 0130 00 | Erkennt IBANs mit oder ohne Leerzeichen |
| BIC | 8 oder 11 Zeichen SWIFT-Code | DEUTDEDBFRA | Auch false positives möglich (jedes 8- oder 11-Zeichen-Wort in Großbuchstaben) |
| STEUER_ID_DE | 11 Ziffern zusammen oder mit Leerzeichen | 12 345 678 901 oder 12345678901 | Erkennt beide gängigen Darstellungen |
| STEUERNUMMER_DE | Länderspezifische Formate | 77012/34567 oder 077/012/34567 | Deckt die häufigsten Bundesland-Formate ab |
| USTID_DE | DE gefolgt von 9 Ziffern | DE812345678 | Standardformat |
| USTID_EU | Ländercode + 8-12 alphanumerische Zeichen | ATU12345678, FRXX999999999 | Grobes Muster, false positives möglich |
| HRB_HRA | HRB oder HRA plus Nummer | HRB 734512, HRA 720988 | Auch UR-Nr wird nicht durch dieses Muster erfasst |
| EMAIL | Standardformat | a.reuter@reuter-kollegen.de | Klassisch, sehr zuverlässig |
| TELEFON_DE | Deutsche Rufnummern | +49 751 123456-0, 0751 123456 | Heuristisch, kann false positives liefern |
| TELEFON_INTL | Internationale Rufnummern | +33 1 42 68 53 00 | Heuristisch |
| PLZ_ORT_DE | Fünfstellige PLZ gefolgt von Ortsname | 88212 Ravensburg | Nur mit Ortsname; PLZ allein wird nicht erkannt |

## Was das Muster NICHT erkennt

- Postleitzahlen alleinstehend (z. B. „88214" in einer Tabellenzelle)
- Ortsnamen ohne PLZ
- Personennamen (keine sinnvolle Regex möglich)
- Firmennamen ohne Rechtsform-Anhang
- Aktenzeichen in unstrukturierten Formaten
- Namen in URLs oder Dateinamen (`Vogel_Alpenblick_30-06-2025.pdf`)
- Grundbuchbezeichnungen wie `Flurstück 1234/5 Grundbuch von X Blatt Y`
- Interne Codewörter, Projektnamen
- Bankname ohne IBAN

Diese Klassen von Identifikatoren muss das Sprachmodell erkennen. Deshalb ist der PRUEFEN-Lauf mit Sprachmodell zusätzlich zur Regex-Restsuche kein Zusatz, sondern Pflicht.

## Erweiterung

Neue Muster werden in `scripts/check_residuals.py` in der Konstante `PATTERNS` ergänzt. Jedes Muster braucht:

- einen Kurznamen (Großbuchstaben, ohne Leerzeichen)
- ein kompiliertes Regex-Objekt
- eine kurze Beschreibung für den Bericht

Für neue Muster empfiehlt sich, sie zuerst gegen einen Testkorpus zu prüfen (mindestens 5 echte Treffer, mindestens 3 gezielt konstruierte Fälle, die kein Treffer sein sollten). Zu breite Muster erzeugen Alarmmüdigkeit und werden vom Anwender ignoriert.

## Rechtlicher Rahmen

Die Muster fangen technisch strukturierte Identifikatoren. Sie fangen weder rechtlich vollständige personenbezogene Daten im Sinne der DSGVO noch decken sie das Mandatsgeheimnis nach § 203 StGB, § 62a StBerG oder § 43 BRAO ab. Die Restsuche ist ein technischer Sicherheitsnetz, keine rechtliche Freigabe.
