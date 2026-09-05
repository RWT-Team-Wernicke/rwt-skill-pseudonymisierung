#!/usr/bin/env python3
"""
pseudonymize.py — deterministische Ersetzung von Klarnamen durch Codes in einem DOCX.

Aufruf:
    python pseudonymize.py \
        --input Originaldokument.docx \
        --changemap changemap.json \
        --alias MANDAT-XY \
        --outdir ./output

Erzeugt:
    <name>_PSEUDO.docx   — DOCX mit ersetzten Zeichenketten, Struktur erhalten
    <ALIAS>_LEGENDE_v1.md   — Legende als Markdown (Kopf, Tabelle, JSON-Block)
    <ALIAS>_LEGENDE_v1.json — Legende als reine JSON-Datei (für Rückumwandlung)

Die Änderungskarte (changemap.json) hat das Format:
    {
      "alias": "MANDAT-XY",
      "version": 1,
      "eintraege": [
        {
          "code": "PERSON_01",
          "kategorie": "PERSON",
          "grundform": "Dr. Klaus Vogel",
          "varianten": ["Herr Dr. Vogel", "Vogels", "K. Vogel"],
          "kommentar": "Optionaler Hinweis"
        },
        ...
      ]
    }

Wichtige Konventionen:
- Reihenfolge der Ersetzung: längste Zeichenkette zuerst, damit "Dr. Klaus Vogel"
  vor "Vogel" ersetzt wird und keine Teilersetzung entsteht.
- Groß-/Kleinschreibung wird beachtet (case-sensitive).
- Ersetzt wird in: Absätzen (auch verschachtelt), Tabellenzellen, Kopf-/Fußzeilen.
- Rechtsformzusätze werden NICHT vom Skript entfernt; sie stehen in der Grundform
  nicht, sondern verbleiben im Text hinter dem Code (z. B. "[FIRMA_02] GmbH & Co. KG").
- Um Runs mit gemischten Formaten korrekt zu behandeln, wird auf Absatzebene ersetzt
  (der gesamte Absatztext wird gesammelt, ersetzt, dann in einen einzigen Run
  zurückgeschrieben). Das kann feine Formatunterschiede (z. B. Fettung eines
  Wortes innerhalb eines Absatzes) verlieren — dokumentiert in references/.
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
except ImportError:
    sys.stderr.write(
        "FEHLER: python-docx nicht installiert. "
        "Bitte 'pip install -r requirements.txt' ausfuehren.\n"
    )
    sys.exit(2)


CATEGORIES_ALLOWED = {
    "PERSON", "FIRMA", "BEHOERDE", "ORT", "ANSCHRIFT", "KONTAKT",
    "STNR", "REGISTER", "KONTO", "AZ", "GEBDAT", "OBJEKT", "SONSTIGES",
}


def load_changemap(path: Path) -> dict:
    """Lade und validiere die Änderungskarte."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if "alias" not in data or "eintraege" not in data:
        raise ValueError("Änderungskarte: 'alias' und 'eintraege' sind Pflichtfelder.")

    codes_seen: set[str] = set()
    for eintrag in data["eintraege"]:
        for feld in ("code", "kategorie", "grundform"):
            if feld not in eintrag:
                raise ValueError(f"Änderungskarte: Eintrag ohne '{feld}': {eintrag}")

        code = eintrag["code"]
        if code in codes_seen:
            raise ValueError(f"Änderungskarte: Code '{code}' mehrfach vergeben.")
        codes_seen.add(code)

        kategorie = eintrag["kategorie"]
        if kategorie not in CATEGORIES_ALLOWED:
            raise ValueError(
                f"Änderungskarte: unbekannte Kategorie '{kategorie}' fuer Code '{code}'."
            )

        # Präfix des Codes muss zur Kategorie passen
        if not code.startswith(kategorie + "_"):
            raise ValueError(
                f"Änderungskarte: Code '{code}' passt nicht zu Kategorie '{kategorie}'."
            )

        eintrag.setdefault("varianten", [])
        eintrag.setdefault("kommentar", "")

    return data


def build_replacement_list(changemap: dict) -> list[tuple[str, str]]:
    """
    Baut eine Liste (suchtext, ersatzcode), sortiert nach absteigender Länge.
    Damit werden längere Zeichenketten zuerst ersetzt (verhindert Teiltreffer).
    """
    replacements: list[tuple[str, str]] = []
    for eintrag in changemap["eintraege"]:
        code_bracketed = f"[{eintrag['code']}]"
        # Grundform als erste Suchzeichenkette
        replacements.append((eintrag["grundform"], code_bracketed))
        for variante in eintrag["varianten"]:
            replacements.append((variante, code_bracketed))

    # Nach Länge absteigend sortieren
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)
    return replacements


def apply_replacements_to_text(text: str, replacements: list[tuple[str, str]],
                               counter: dict[str, int]) -> str:
    """
    Wendet alle Ersetzungen auf einen Text an.
    Zählt Vorkommen je Ersatzcode in `counter`.
    """
    for suchtext, ersatzcode in replacements:
        if not suchtext:
            continue
        if suchtext in text:
            # Anzahl vor Ersetzung zählen
            n = text.count(suchtext)
            text = text.replace(suchtext, ersatzcode)
            counter[ersatzcode] = counter.get(ersatzcode, 0) + n
    return text


def replace_in_paragraph(paragraph, replacements: list[tuple[str, str]],
                         counter: dict[str, int]) -> None:
    """
    Ersetzt Text in einem Absatz.

    Strategie: Wir sammeln den Text aller Runs, wenden die Ersetzungen an,
    und wenn sich etwas geändert hat, schreiben wir das Ergebnis in den ersten
    Run zurück und leeren alle weiteren Runs. Die Absatzformatvorlage bleibt
    erhalten, aber Feinformatierungen innerhalb des Absatzes (z. B. einzelne
    fette Wörter) gehen verloren, wenn eine Ersetzung sie betrifft.
    """
    runs = paragraph.runs
    if not runs:
        return

    original_text = "".join(run.text for run in runs)
    new_text = apply_replacements_to_text(original_text, replacements, counter)

    if new_text == original_text:
        return

    # Formatierung des ersten Runs übernehmen, den Rest leeren
    runs[0].text = new_text
    for run in runs[1:]:
        run.text = ""


def replace_in_document(doc, replacements: list[tuple[str, str]]) -> dict[str, int]:
    """Wendet die Ersetzungen auf das gesamte Dokument an."""
    counter: dict[str, int] = {}

    # Hauptteil: Absätze und Tabellen
    def walk_container(container):
        for paragraph in container.paragraphs:
            replace_in_paragraph(paragraph, replacements, counter)
        for table in container.tables:
            for row in table.rows:
                for cell in row.cells:
                    walk_container(cell)

    walk_container(doc)

    # Kopf- und Fußzeilen aller Sections
    for section in doc.sections:
        for header_footer in (section.header, section.footer,
                              section.first_page_header, section.first_page_footer,
                              section.even_page_header, section.even_page_footer):
            if header_footer is not None:
                walk_container(header_footer)

    return counter


def insert_marker(doc, alias: str, version: int) -> None:
    """Fügt die Kennzeichnungszeile als ersten Absatz ein."""
    marker_text = (
        f"[Pseudonymisiertes Dokument · Alias {alias} · "
        f"Legende v{version} · Codes nicht auflösen]"
    )
    new_paragraph = doc.paragraphs[0].insert_paragraph_before(marker_text)
    # Kennzeichnungsstil: kursiv, damit optisch abgesetzt
    for run in new_paragraph.runs:
        run.italic = True


def write_legend(changemap: dict, counter: dict[str, int], outdir: Path) -> tuple[Path, Path]:
    """Schreibt die Legende als Markdown und JSON."""
    alias = changemap["alias"]
    version = changemap.get("version", 1)

    md_path = outdir / f"{alias}_LEGENDE_v{version}.md"
    json_path = outdir / f"{alias}_LEGENDE_v{version}.json"

    # Markdown-Fassung
    today = date.today().isoformat()
    lines = [
        f"# Legende {alias} (Version {version})",
        "",
        f"Erstellt: {today}",
        f"Skill: rwt-skill-pseudonymisierung",
        "",
        "Diese Datei enthält die Zuordnung zwischen Codes und Klarnamen.",
        "Sie darf nicht mit dem pseudonymisierten Dokument in offene Umgebungen",
        "gelangen. Zur Rückumwandlung wird ausschließlich der JSON-Block unten",
        "oder die separate JSON-Datei benötigt.",
        "",
        "## Codetabelle",
        "",
        "| Code | Kategorie | Grundform | Varianten | Vorkommen im PSEUDO | Kommentar |",
        "|---|---|---|---|---|---|",
    ]
    for eintrag in changemap["eintraege"]:
        code_key = f"[{eintrag['code']}]"
        vorkommen = counter.get(code_key, 0)
        varianten_str = "; ".join(eintrag.get("varianten", [])) or "—"
        kommentar = eintrag.get("kommentar", "") or "—"
        # Pipe-Zeichen in Feldern escapen
        grundform = eintrag["grundform"].replace("|", "\\|")
        varianten_str = varianten_str.replace("|", "\\|")
        kommentar = kommentar.replace("|", "\\|")
        lines.append(
            f"| {eintrag['code']} | {eintrag['kategorie']} | {grundform} | "
            f"{varianten_str} | {vorkommen} | {kommentar} |"
        )

    lines.extend([
        "",
        "## JSON-Block (maschinenlesbar)",
        "",
        "```json",
        json.dumps(changemap, ensure_ascii=False, indent=2),
        "```",
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # JSON-Fassung (identisch, ohne Rahmen)
    json_path.write_text(
        json.dumps(changemap, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministische Pseudonymisierung eines DOCX."
    )
    parser.add_argument("--input", required=True, type=Path,
                        help="Original-DOCX (wird nicht veraendert)")
    parser.add_argument("--changemap", required=True, type=Path,
                        help="JSON mit den zu ersetzenden Entitaeten")
    parser.add_argument("--alias", required=True,
                        help="Alias des Mandats (Kurzbezeichnung, kein Personenbezug)")
    parser.add_argument("--outdir", required=True, type=Path,
                        help="Ausgabeverzeichnis")
    args = parser.parse_args()

    if not args.input.exists():
        sys.stderr.write(f"FEHLER: Eingabedatei nicht gefunden: {args.input}\n")
        return 2
    if not args.changemap.exists():
        sys.stderr.write(f"FEHLER: Aenderungskarte nicht gefunden: {args.changemap}\n")
        return 2
    args.outdir.mkdir(parents=True, exist_ok=True)

    changemap = load_changemap(args.changemap)
    if changemap["alias"] != args.alias:
        sys.stderr.write(
            f"FEHLER: Alias in Aenderungskarte ('{changemap['alias']}') "
            f"stimmt nicht mit --alias ('{args.alias}') ueberein.\n"
        )
        return 2

    replacements = build_replacement_list(changemap)

    doc = Document(str(args.input))
    counter = replace_in_document(doc, replacements)
    insert_marker(doc, args.alias, changemap.get("version", 1))

    pseudo_name = args.input.stem + "_PSEUDO.docx"
    pseudo_path = args.outdir / pseudo_name
    doc.save(str(pseudo_path))

    md_path, json_path = write_legend(changemap, counter, args.outdir)

    # Prüfbericht ausgeben (nach stdout)
    report = {
        "eingabe": str(args.input),
        "ausgabe_pseudo": str(pseudo_path),
        "legende_md": str(md_path),
        "legende_json": str(json_path),
        "alias": args.alias,
        "version": changemap.get("version", 1),
        "ersetzungen": counter,
        "codes_ohne_treffer": [
            f"[{e['code']}]" for e in changemap["eintraege"]
            if counter.get(f"[{e['code']}]", 0) == 0
        ],
        "hinweis": "Die Legende NICHT in offene KI-Umgebungen laden.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
