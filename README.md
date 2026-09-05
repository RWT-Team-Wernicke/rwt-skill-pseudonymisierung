# rwt-skill-pseudonymisierung

Agent-Skill für die reversible Pseudonymisierung von Mandatsdokumenten (DOCX) in einer geschlossenen KI-Umgebung. Erzeugt ein PSEUDO-Dokument, das gefahrlos in offene KI-Umgebungen geladen werden darf, sowie eine getrennte Legende zur Rückumwandlung.

Interner Skill der RWT-Gruppe / Die TaxMaxen. Zielumgebung: Claract (OMM Solutions, Stuttgart) oder eine andere Umgebung mit Unterstützung für [Open Agent Skills](https://github.com/agentskills/agentskills).

---

## Übersicht

- Vier Aufgabenarten: `PSEUDONYMISIEREN`, `FORTSCHREIBEN`, `RUECKUMWANDELN`, `PRUEFEN`
- Zwei-Phasen-Verfahren: Vorschlagsliste zur Freigabe, dann deterministische Skript-Ausführung
- 13 Kategorien, Codeformat `[KATEGORIE_NN]`, buchstabengetreue Ersetzung
- Legende in Markdown und JSON, JSON ist maschinenlesbar authoritativ
- Rundlauf-getestet gegen ein fiktives Sachverhaltsschreiben (siehe `assets/`)

## Repositoriumsaufbau

```
rwt-skill-pseudonymisierung/
├── SKILL.md                              Systemprompt und Regeln (vom Agenten gelesen)
├── README.md                             diese Datei (für Menschen)
├── scripts/
│   ├── requirements.txt
│   ├── pseudonymize.py                   Ersetzt Klarnamen durch Codes (DOCX → DOCX)
│   ├── depseudonymize.py                 Setzt Codes zurück in Klarnamen (DOCX → DOCX)
│   └── check_residuals.py                Restsuche nach harten Identifikatoren
├── references/
│   ├── kategorien-katalog.md             Die 13 Kategorien und Regeln
│   ├── legendenschema.md                 Struktur von Legende und Änderungskarte
│   ├── regex-muster.md                   Muster der Restsuche
│   └── bedienanleitung.md                Anwenderhandbuch
└── assets/
    ├── Testdokument_A_Sachverhaltsschreiben.docx
    ├── 260828_Schulung_Mailverlauf_Nordmark.pdf
    ├── loesungsschluessel_A.md          (nicht mit Bot teilen)
    ├── loesungsschluessel_B.md          (nicht mit Bot teilen)
    ├── bewertungsbogen.md               Prüfliste für die Testauswertung
    ├── beispiel_changemap_TEST-A.json   Beispiel-Änderungskarte
    └── beispiel_legende_TEST-A.md       Beispiel-Legende
```

## Einrichtung im GitHub-Repo (einmalig)

1. Repository in der RWT-GitHub-Organisation anlegen (private): `rwt-skill-pseudonymisierung`
2. Diese Inhalte in den Hauptzweig commiten (`main`)
3. In Claract unter „Skills → Import" die Kennung `<org>/rwt-skill-pseudonymisierung` eingeben (z. B. `rwt-gruppe/rwt-skill-pseudonymisierung`)
4. Skill wird für alle Anwender der Umgebung verfügbar

Ohne GitHub-Organisation kann übergangsweise das persönliche Konto eines Kollegen genutzt werden. Aus Kontinuitätsgründen ist eine funktionale Organisation vorzuziehen.

## Voraussetzungen der Umgebung

- Python 3.11 oder höher
- Zugriff auf pip zum Installieren von `python-docx` (siehe `scripts/requirements.txt`)
- Kein Netzzugriff aus dem Skript-Kontext heraus erforderlich; alle Läufe sind lokal

## Test in einer beliebigen Python-Umgebung

Für einen Test außerhalb Claracts genügt eine lokale Python-Installation:

```bash
cd rwt-skill-pseudonymisierung
python -m pip install -r scripts/requirements.txt

python scripts/pseudonymize.py \
  --input assets/Testdokument_A_Sachverhaltsschreiben.docx \
  --changemap assets/beispiel_changemap_TEST-A.json \
  --alias TEST-A \
  --outdir out/

python scripts/check_residuals.py --input out/Testdokument_A_Sachverhaltsschreiben_PSEUDO.docx

python scripts/depseudonymize.py \
  --input out/Testdokument_A_Sachverhaltsschreiben_PSEUDO.docx \
  --legend out/TEST-A_LEGENDE_v1.json \
  --outdir out/
```

Erwartetes Ergebnis:

- `out/Testdokument_A_Sachverhaltsschreiben_PSEUDO.docx` enthält Codes anstelle der Klarnamen und eine Kennzeichnungszeile
- `out/TEST-A_LEGENDE_v1.md` und `.json` enthalten die Codetabelle
- `check_residuals.py` meldet 0 Treffer (Regex-Restsuche allein; das Sprachmodell muss ergänzend prüfen)
- `out/Testdokument_A_Sachverhaltsschreiben_KLAR.docx` entspricht (bis auf Kennzeichnungszeile) dem Original

Bekannte Schwäche der Beispieldatei `beispiel_changemap_TEST-A.json`: zwei Einträge enthalten `Praezisionsteile` statt `Präzisionsteile` und `Industriestrasse` statt `Industriestraße`. Der Effekt ist im PSEUDO-Dokument sichtbar und dokumentiert bewusst den häufigsten Bedienfehler.

## Testauswertung

Die Datei `assets/bewertungsbogen.md` enthält eine zehnteilige Prüfliste mit K.o.-Kriterien. Sie ist die verbindliche Auswertungsgrundlage für Freigabetests.

Die Lösungsschlüssel A und B (`assets/loesungsschluessel_*.md`) enthalten die vollständigen Codelisten der beiden Testdokumente. Sie werden dem Bot nicht gezeigt. Sie dienen dem Prüfer zum Abgleich der Bot-Vorschläge mit der Sollmenge.

## Kein Ersatz für Rechts-, Steuer- oder Datenschutzberatung

Der Skill ist ein technisches Werkzeug. Er ersetzt weder die datenschutzrechtliche Bewertung nach DSGVO noch die berufsrechtliche Prüfung der zulässigen Verarbeitung von Mandatsdaten (§ 203 StGB, § 62a StBerG, § 43 BRAO). Vor produktivem Einsatz ist eine Freigabe durch RWT-Datenschutz und -Berufsrecht einzuholen.

## Version

Version 1.0 vom 05.09.2026 (getestet in isolierter Sandbox, nicht in Claract-Produktion).
