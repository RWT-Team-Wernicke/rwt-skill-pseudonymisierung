# Legende TEST-A (Version 1)

Erstellt: 2026-09-05
Skill: rwt-skill-pseudonymisierung

Diese Datei enthält die Zuordnung zwischen Codes und Klarnamen.
Sie darf nicht mit dem pseudonymisierten Dokument in offene Umgebungen
gelangen. Zur Rückumwandlung wird ausschließlich der JSON-Block unten
oder die separate JSON-Datei benötigt.

## Codetabelle

| Code | Kategorie | Grundform | Varianten | Vorkommen im PSEUDO | Kommentar |
|---|---|---|---|---|---|
| PERSON_01 | PERSON | Dr. Klaus Vogel | Herr Dr. Vogel; K. Vogel; Vogels | 5 | Kommanditist, Anschrift Lindenallee |
| PERSON_02 | PERSON | Sabine Vogel | Frau Vogel | 3 | Kommanditistin, Ehefrau |
| PERSON_03 | PERSON | Jonas Vogel | — | 3 | Sohn |
| PERSON_04 | PERSON | Dr. Anja Reuter | Frau Dr. Reuter | 2 | Steuerberaterin |
| PERSON_05 | PERSON | Brandt | — | 2 | Sachbearbeiter Finanzamt |
| PERSON_06 | PERSON | Dr. Ilse Kaminski | — | 1 | Notarin |
| PERSON_07 | PERSON | Prof. Dr. Weber | — | 1 | Gutachter |
| FIRMA_01 | FIRMA | Vogel Beteiligungs | — | 2 | GmbH; enthaelt Namen von PERSON_01 |
| FIRMA_02 | FIRMA | Alpenblick Praezisionsteile | Alpenblick | 6 | GmbH & Co. KG |
| FIRMA_03 | FIRMA | Alpenblick Verwaltungs | — | 2 | GmbH, Komplementaerin |
| FIRMA_04 | FIRMA | Reuter & Kollegen | — | 2 | Steuerberatungsgesellschaft |
| FIRMA_05 | FIRMA | Oberland Volksbank | — | 1 | — |
| BEHOERDE_01 | BEHOERDE | Finanzamt Ravensburg | — | 2 | — |
| BEHOERDE_02 | BEHOERDE | Amtsgericht Ulm | — | 2 | — |
| ORT_01 | ORT | Ravensburg | — | 6 | einzeln stehend |
| ANSCHRIFT_01 | ANSCHRIFT | Lindenallee 12, 88212 Ravensburg | Lindenallee 12 | 1 | — |
| ANSCHRIFT_02 | ANSCHRIFT | Industriestrasse 7, 88214 Ravensburg | Industriestrasse 7 | 0 | — |
| KONTAKT_01 | KONTAKT | a.reuter@reuter-kollegen.de | — | 1 | — |
| KONTAKT_02 | KONTAKT | +49 751 123456-0 | — | 1 | — |
| STNR_01 | STNR | 77012/34567 | — | 1 | Steuernummer FIRMA_01 |
| STNR_02 | STNR | DE812345678 | — | 1 | USt-IdNr FIRMA_02 |
| STNR_03 | STNR | 12 345 678 901 | — | 1 | Steuer-ID PERSON_01 |
| REGISTER_01 | REGISTER | HRB 734512 | — | 1 | — |
| REGISTER_02 | REGISTER | HRA 720988 | — | 1 | — |
| REGISTER_03 | REGISTER | UR-Nr. 1234/2025 | — | 1 | — |
| REGISTER_04 | REGISTER | Flurstueck 1234/5, Grundbuch von Ravensburg Blatt 8901 | — | 0 | — |
| KONTO_01 | KONTO | DE89 3704 0044 0532 0130 00 | — | 1 | — |
| AZ_01 | AZ | 2026-0417-V | — | 1 | — |
| GEBDAT_01 | GEBDAT | 14.03.1961 | — | 1 | PERSON_01 |
| OBJEKT_01 | OBJEKT | Projekt Aurora | Aurora | 2 | — |

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
      "varianten": [
        "Herr Dr. Vogel",
        "K. Vogel",
        "Vogels"
      ],
      "kommentar": "Kommanditist, Anschrift Lindenallee"
    },
    {
      "code": "PERSON_02",
      "kategorie": "PERSON",
      "grundform": "Sabine Vogel",
      "varianten": [
        "Frau Vogel"
      ],
      "kommentar": "Kommanditistin, Ehefrau"
    },
    {
      "code": "PERSON_03",
      "kategorie": "PERSON",
      "grundform": "Jonas Vogel",
      "varianten": [],
      "kommentar": "Sohn"
    },
    {
      "code": "PERSON_04",
      "kategorie": "PERSON",
      "grundform": "Dr. Anja Reuter",
      "varianten": [
        "Frau Dr. Reuter"
      ],
      "kommentar": "Steuerberaterin"
    },
    {
      "code": "PERSON_05",
      "kategorie": "PERSON",
      "grundform": "Brandt",
      "varianten": [],
      "kommentar": "Sachbearbeiter Finanzamt"
    },
    {
      "code": "PERSON_06",
      "kategorie": "PERSON",
      "grundform": "Dr. Ilse Kaminski",
      "varianten": [],
      "kommentar": "Notarin"
    },
    {
      "code": "PERSON_07",
      "kategorie": "PERSON",
      "grundform": "Prof. Dr. Weber",
      "varianten": [],
      "kommentar": "Gutachter"
    },
    {
      "code": "FIRMA_01",
      "kategorie": "FIRMA",
      "grundform": "Vogel Beteiligungs",
      "varianten": [],
      "kommentar": "GmbH; enthaelt Namen von PERSON_01"
    },
    {
      "code": "FIRMA_02",
      "kategorie": "FIRMA",
      "grundform": "Alpenblick Praezisionsteile",
      "varianten": [
        "Alpenblick"
      ],
      "kommentar": "GmbH & Co. KG"
    },
    {
      "code": "FIRMA_03",
      "kategorie": "FIRMA",
      "grundform": "Alpenblick Verwaltungs",
      "varianten": [],
      "kommentar": "GmbH, Komplementaerin"
    },
    {
      "code": "FIRMA_04",
      "kategorie": "FIRMA",
      "grundform": "Reuter & Kollegen",
      "varianten": [],
      "kommentar": "Steuerberatungsgesellschaft"
    },
    {
      "code": "FIRMA_05",
      "kategorie": "FIRMA",
      "grundform": "Oberland Volksbank",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "BEHOERDE_01",
      "kategorie": "BEHOERDE",
      "grundform": "Finanzamt Ravensburg",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "BEHOERDE_02",
      "kategorie": "BEHOERDE",
      "grundform": "Amtsgericht Ulm",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "ORT_01",
      "kategorie": "ORT",
      "grundform": "Ravensburg",
      "varianten": [],
      "kommentar": "einzeln stehend"
    },
    {
      "code": "ANSCHRIFT_01",
      "kategorie": "ANSCHRIFT",
      "grundform": "Lindenallee 12, 88212 Ravensburg",
      "varianten": [
        "Lindenallee 12"
      ],
      "kommentar": ""
    },
    {
      "code": "ANSCHRIFT_02",
      "kategorie": "ANSCHRIFT",
      "grundform": "Industriestrasse 7, 88214 Ravensburg",
      "varianten": [
        "Industriestrasse 7"
      ],
      "kommentar": ""
    },
    {
      "code": "KONTAKT_01",
      "kategorie": "KONTAKT",
      "grundform": "a.reuter@reuter-kollegen.de",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "KONTAKT_02",
      "kategorie": "KONTAKT",
      "grundform": "+49 751 123456-0",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "STNR_01",
      "kategorie": "STNR",
      "grundform": "77012/34567",
      "varianten": [],
      "kommentar": "Steuernummer FIRMA_01"
    },
    {
      "code": "STNR_02",
      "kategorie": "STNR",
      "grundform": "DE812345678",
      "varianten": [],
      "kommentar": "USt-IdNr FIRMA_02"
    },
    {
      "code": "STNR_03",
      "kategorie": "STNR",
      "grundform": "12 345 678 901",
      "varianten": [],
      "kommentar": "Steuer-ID PERSON_01"
    },
    {
      "code": "REGISTER_01",
      "kategorie": "REGISTER",
      "grundform": "HRB 734512",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "REGISTER_02",
      "kategorie": "REGISTER",
      "grundform": "HRA 720988",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "REGISTER_03",
      "kategorie": "REGISTER",
      "grundform": "UR-Nr. 1234/2025",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "REGISTER_04",
      "kategorie": "REGISTER",
      "grundform": "Flurstueck 1234/5, Grundbuch von Ravensburg Blatt 8901",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "KONTO_01",
      "kategorie": "KONTO",
      "grundform": "DE89 3704 0044 0532 0130 00",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "AZ_01",
      "kategorie": "AZ",
      "grundform": "2026-0417-V",
      "varianten": [],
      "kommentar": ""
    },
    {
      "code": "GEBDAT_01",
      "kategorie": "GEBDAT",
      "grundform": "14.03.1961",
      "varianten": [],
      "kommentar": "PERSON_01"
    },
    {
      "code": "OBJEKT_01",
      "kategorie": "OBJEKT",
      "grundform": "Projekt Aurora",
      "varianten": [
        "Aurora"
      ],
      "kommentar": ""
    }
  ]
}
```
