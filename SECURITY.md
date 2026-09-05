# Sicherheitsmeldungen

Dieser Skill verarbeitet in seiner Zielumgebung (Claract) potenziell mandatsbezogene Dokumente. Sicherheitsprobleme werden deshalb nicht als oeffentliches GitHub-Issue gemeldet, sondern intern.

## Meldeweg

**Interner Ansprechpartner (Uebergangsstand):**
Daniel Wernicke, RWT-Gruppe / Die TaxMaxen
E-Mail: daniel.wernicke@rwt-gruppe.de

Der Ansprechpartner leitet die Meldung an RWT-IT und, wenn Mandatsbezug moeglich ist, an RWT-Datenschutz weiter.

## Was gemeldet werden sollte

- Fehlverhalten der Skripte, das zu ungewollter Preisgabe von Klarnamen fuehrt (z. B. eine Kombination aus Eingabe und changemap, bei der der Pseudonymisierer nicht greift, aber `codes_ohne_treffer` leer bleibt)
- Fehlverhalten der Restsuche (harte Identifikatoren im Dokument, die weder von Regex noch von der Selbstpruefung erkannt wurden)
- Rueckumwandlung, die aus dem PSEUDO-Dokument mehr rekonstruiert als die Legende erlaubt (z. B. weil die Klarnamen doch noch als Metadaten enthalten sind)
- Auffaelligkeiten in Abhaengigkeiten (`python-docx` etc.), die fuer den Anwendungsfall relevant sind
- Jede Situation, in der der Skill in einer offenen KI-Umgebung eingesetzt wurde, obwohl er dafuer nicht vorgesehen ist

## Was NICHT hier gemeldet wird

- Bugs ohne Sicherheitsbezug: normales GitHub-Issue im jeweiligen Repository
- Fragen zur Bedienung: siehe `references/bedienanleitung.md` und die zentrale IT-Uebergabe-Notiz

## Vertrauliche Kommunikation

Wenn eine Meldung mandatsbezogene Beispiele enthaelt, ausschliesslich verschluesselt uebermitteln. Der Ansprechpartner nennt auf Nachfrage den passenden Weg (z. B. verschluesselte Anlage oder persoenliche Uebergabe).

## Reaktionszeiten (Richtwerte)

- Eingangsbestaetigung: 3 Arbeitstage
- Erste inhaltliche Rueckmeldung: 10 Arbeitstage
- Verbindliche Regelung nach Vollintegration in die RWT-GitHub-Organisation
