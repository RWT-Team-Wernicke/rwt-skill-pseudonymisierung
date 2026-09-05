#!/usr/bin/env python3
"""
depseudonymize.py — deterministische Rueckumwandlung eines PSEUDO-DOCX in Klartext.

Aufruf:
    python depseudonymize.py \
        --input Dokument_PSEUDO.docx \
        --legend MANDAT-XY_LEGENDE_v1.json \
        --outdir ./output

Erzeugt:
    <name>_KLAR.docx   — DOCX mit rueckuebersetzten Codes

Regeln:
- Jeder Code der Form [KATEGORIE_NN] wird durch die Grundform aus der Legende ersetzt.
- Codes ohne Legendeneintrag bleiben stehen und werden im Bericht als Fehler gemeldet.
- Die Kennzeichnungszeile aus Phase 2 wird entfernt.
- Keine Umformulierungen, keine Zusaetze.
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


# Erkennungsmuster fuer Codes in eckigen Klammern
CODE_PATTERN = re.compile(
    r"\[(PERSON|FIRMA|BEHOERDE|ORT|ANSCHRIFT|KONTAKT|STNR|REGISTER|KONTO|AZ|GEBDAT|OBJEKT|SONSTIGES)_\d{2,3}\]"
)

# Erkennungsmuster fuer die Kennzeichnungszeile
MARKER_PATTERN = re.compile(
    r"^\[Pseudonymisiertes Dokument · Alias .+? · Legende v\d+ · Codes nicht aufl(ö|oe)sen\]$"
)


def load_legend(path: Path) -> dict[str, str]:
    """Lade die Legende, gib ein Mapping {code_ohne_klammern: grundform} zurueck."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    mapping: dict[str, str] = {}
    for eintrag in data.get("eintraege", []):
        mapping[eintrag["code"]] = eintrag["grundform"]
    return mapping


def apply_reverse_to_text(text: str, legend: dict[str, str],
                          counter: dict[str, int],
                          missing: set[str]) -> str:
    """Ersetzt alle Codes durch Grundformen. Registriert Treffer und Fehlstellen."""
    def repl(match: re.Match) -> str:
        code_full = match.group(0)  # z. B. "[PERSON_01]"
        code_key = code_full[1:-1]  # "PERSON_01"
        if code_key in legend:
            counter[code_full] = counter.get(code_full, 0) + 1
            return legend[code_key]
        missing.add(code_full)
        return code_full  # unveraendert lassen

    return CODE_PATTERN.sub(repl, text)


def process_paragraph(paragraph, legend: dict[str, str],
                      counter: dict[str, int], missing: set[str]) -> bool:
    """
    Bearbeitet einen Absatz. Gibt True zurueck, wenn der Absatz die Kennzeichnungszeile
    war und geloescht werden soll.
    """
    runs = paragraph.runs
    if not runs:
        return False

    text = "".join(run.text for run in runs)

    # Kennzeichnungszeile erkennen
    if MARKER_PATTERN.match(text.strip()):
        return True

    new_text = apply_reverse_to_text(text, legend, counter, missing)
    if new_text != text:
        runs[0].text = new_text
        for run in runs[1:]:
            run.text = ""
    return False


def process_document(doc, legend: dict[str, str]) -> tuple[dict[str, int], set[str]]:
    counter: dict[str, int] = {}
    missing: set[str] = set()

    # Marker-Absätze werden gesammelt und am Ende entfernt
    to_remove: list = []

    def walk_container(container):
        for paragraph in container.paragraphs:
            if process_paragraph(paragraph, legend, counter, missing):
                to_remove.append(paragraph)
        for table in container.tables:
            for row in table.rows:
                for cell in row.cells:
                    walk_container(cell)

    walk_container(doc)

    for section in doc.sections:
        for hf in (section.header, section.footer,
                   section.first_page_header, section.first_page_footer,
                   section.even_page_header, section.even_page_footer):
            if hf is not None:
                walk_container(hf)

    # Marker-Absätze aus dem XML entfernen
    for paragraph in to_remove:
        el = paragraph._element
        el.getparent().remove(el)

    return counter, missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministische Rueckumwandlung eines PSEUDO-DOCX."
    )
    parser.add_argument("--input", required=True, type=Path,
                        help="PSEUDO-DOCX (wird nicht veraendert)")
    parser.add_argument("--legend", required=True, type=Path,
                        help="JSON-Legende zum Alias")
    parser.add_argument("--outdir", required=True, type=Path,
                        help="Ausgabeverzeichnis")
    args = parser.parse_args()

    if not args.input.exists():
        sys.stderr.write(f"FEHLER: Eingabedatei nicht gefunden: {args.input}\n")
        return 2
    if not args.legend.exists():
        sys.stderr.write(f"FEHLER: Legende nicht gefunden: {args.legend}\n")
        return 2
    args.outdir.mkdir(parents=True, exist_ok=True)

    legend = load_legend(args.legend)
    doc = Document(str(args.input))
    counter, missing = process_document(doc, legend)

    # Ausgabename
    stem = args.input.stem
    if stem.endswith("_PSEUDO"):
        klar_name = stem[:-len("_PSEUDO")] + "_KLAR.docx"
    else:
        klar_name = stem + "_KLAR.docx"
    klar_path = args.outdir / klar_name
    doc.save(str(klar_path))

    # Legendeneintraege ohne Vorkommen im Dokument (informativ)
    unused = [f"[{code}]" for code in legend if f"[{code}]" not in counter]

    report = {
        "eingabe": str(args.input),
        "legende": str(args.legend),
        "ausgabe_klar": str(klar_path),
        "ersetzte_codes": counter,
        "codes_ohne_legende": sorted(missing),
        "legendeneintraege_ohne_vorkommen": unused,
        "status": "OK" if not missing else "WARNUNG: Codes ohne Legende gefunden",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
