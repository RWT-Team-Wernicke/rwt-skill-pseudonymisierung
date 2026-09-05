#!/usr/bin/env python3
"""
check_residuals.py — Restsuche nach harten Identifikatoren in einem DOCX.

Zweck 1 (vor Pseudonymisierung): Muster finden, die auf jeden Fall codiert werden
sollten (IBAN, deutsche Steuer-ID, HRB-Nummer, USt-IdNr, E-Mail, Telefon).
Zweck 2 (nach Pseudonymisierung): pruefen, ob solche Muster in der PSEUDO-Datei
noch vorkommen. Treffer sind dann Fehler.

Aufruf:
    python check_residuals.py --input Dokument.docx [--json]

Ausgabe: Bericht als Text oder JSON (mit --json).
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

try:
    from docx import Document
except ImportError:
    sys.stderr.write(
        "FEHLER: python-docx nicht installiert. "
        "Bitte 'pip install -r requirements.txt' ausfuehren.\n"
    )
    sys.exit(2)


# Muster mit Bezeichnungen und Erlaeuterungen.
# Sie sind bewusst konservativ (eher zu viele Treffer als zu wenige) —
# false positives sind harmlos, false negatives waeren gefaehrlich.
PATTERNS = [
    (
        "IBAN",
        re.compile(r"\b[A-Z]{2}\d{2}[ ]?(?:\d{4}[ ]?){2,7}\d{1,4}\b"),
        "Internationale Bankkontonummer",
    ),
    (
        "BIC",
        re.compile(r"\b[A-Z]{6}[A-Z0-9]{2}(?:[A-Z0-9]{3})?\b"),
        "Bank Identifier Code (SWIFT)",
    ),
    (
        "STEUER_ID_DE",
        re.compile(r"\b\d{2}\s\d{3}\s\d{3}\s\d{3}\b|\b\d{11}\b"),
        "Deutsche steuerliche Identifikationsnummer (11 Ziffern)",
    ),
    (
        "STEUERNUMMER_DE",
        re.compile(r"\b\d{2,3}/\d{3,4}/\d{4,5}\b|\b\d{5}/\d{5}\b"),
        "Deutsche Steuernummer (Format je Bundesland)",
    ),
    (
        "USTID_DE",
        re.compile(r"\bDE[ ]?\d{9}\b"),
        "Umsatzsteuer-Identifikationsnummer Deutschland",
    ),
    (
        "USTID_EU",
        re.compile(r"\b(?:AT|BE|BG|CY|CZ|DK|EE|EL|ES|FI|FR|HR|HU|IE|IT|LT|LU|LV|MT|NL|PL|PT|RO|SE|SI|SK)[ ]?[A-Z0-9]{8,12}\b"),
        "USt-IdNr anderes EU-Land (grobes Muster)",
    ),
    (
        "HRB_HRA",
        re.compile(r"\bHR[BA][ ]\d{2,6}\b"),
        "Handelsregisternummer",
    ),
    (
        "EMAIL",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "E-Mail-Adresse",
    ),
    (
        "TELEFON_DE",
        re.compile(r"(?:\+49[ /-]?|0)[1-9]\d{1,4}[ /-]?\d{3,}[ /-]?\d{0,}"),
        "Deutsche Telefonnummer (heuristisch)",
    ),
    (
        "TELEFON_INTL",
        re.compile(r"\+\d{1,3}[ /-]?\d{2,4}[ /-]?\d{3,}[ /-]?\d{0,}"),
        "Internationale Telefonnummer (heuristisch)",
    ),
    (
        "PLZ_ORT_DE",
        re.compile(r"\b\d{5}\s+[A-ZÄÖÜ][a-zäöüß\-]+(?:\s+[A-ZÄÖÜ][a-zäöüß\-]+)?\b"),
        "Deutsche Postleitzahl mit Ortsname",
    ),
]

# Falsch-positive Muster, die ausgefiltert werden (bekannte Standard-Nennungen)
KNOWN_FALSE_POSITIVES = {
    "IBAN",  # Kontext prüfen
}


MARKER_PATTERN = re.compile(r"^\[Pseudonymisiertes Dokument")


def extract_all_text(doc) -> list[tuple[str, str]]:
    """
    Sammelt (kontext, text) fuer jeden Absatz und jede Zelle.
    Kontext beschreibt grob, wo der Text stand.
    Die Kennzeichnungszeile am Dokumentanfang wird uebersprungen, damit der
    Alias-Name darin keine false positives ausloest (BIC-Muster etc.).
    """
    result: list[tuple[str, str]] = []

    def walk(container, ctx: str):
        for i, paragraph in enumerate(container.paragraphs):
            text = "".join(run.text for run in paragraph.runs)
            if text.strip() and not MARKER_PATTERN.match(text.strip()):
                result.append((f"{ctx}/absatz[{i}]", text))
        for ti, table in enumerate(container.tables):
            for ri, row in enumerate(table.rows):
                for ci, cell in enumerate(row.cells):
                    walk(cell, f"{ctx}/tabelle[{ti}]/zeile[{ri}]/spalte[{ci}]")

    walk(doc, "body")
    for si, section in enumerate(doc.sections):
        for name, hf in (
            ("header", section.header),
            ("footer", section.footer),
            ("first_page_header", section.first_page_header),
            ("first_page_footer", section.first_page_footer),
            ("even_page_header", section.even_page_header),
            ("even_page_footer", section.even_page_footer),
        ):
            if hf is not None:
                walk(hf, f"section[{si}]/{name}")

    return result


def scan(doc) -> list[dict]:
    """Scanne das Dokument nach allen Mustern."""
    findings: list[dict] = []
    for ctx, text in extract_all_text(doc):
        for name, pattern, beschreibung in PATTERNS:
            for match in pattern.finditer(text):
                # Kontextfenster fuer manuelle Beurteilung
                start = max(0, match.start() - 30)
                end = min(len(text), match.end() + 30)
                findings.append({
                    "muster": name,
                    "beschreibung": beschreibung,
                    "treffer": match.group(0),
                    "kontext": text[start:end],
                    "position": ctx,
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regex-Restsuche nach harten Identifikatoren."
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json", action="store_true",
                        help="Ausgabe als JSON statt Text")
    args = parser.parse_args()

    if not args.input.exists():
        sys.stderr.write(f"FEHLER: Eingabedatei nicht gefunden: {args.input}\n")
        return 2

    doc = Document(str(args.input))
    findings = scan(doc)

    if args.json:
        print(json.dumps({
            "eingabe": str(args.input),
            "trefferzahl": len(findings),
            "treffer": findings,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Restsuche in: {args.input}")
        print(f"Treffer gesamt: {len(findings)}")
        print()
        if not findings:
            print("Keine harten Muster gefunden.")
        else:
            for f in findings:
                print(f"- {f['muster']}: {f['treffer']!r}")
                print(f"  Kontext: ...{f['kontext']}...")
                print(f"  Position: {f['position']}")
                print()

    # Exit-Code 0 = keine Treffer, 1 = Treffer vorhanden (fuer skriptgetriebene Nutzung)
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
