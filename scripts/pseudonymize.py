#!/usr/bin/env python3
"""
pseudonymize.py — deterministische Ersetzung von Klarnamen durch Codes in einem DOCX.

Skill-Version 1.1, Legendenschema v2 (Positionsindex).

Aufruf:
    python pseudonymize.py \
        --input Originaldokument.docx \
        --changemap changemap.json \
        --alias MANDAT-XY \
        --outdir ./output

Erzeugt:
    <name>_PSEUDO.docx   — DOCX mit ersetzten Zeichenketten, Struktur erhalten
    <ALIAS>_LEGENDE_v1.md   — Legende als Markdown (Kopf, Tabelle, JSON-Block)
    <ALIAS>_LEGENDE_v1.json — Legende als reine JSON-Datei (fuer Rueckumwandlung)

Neu in v1.1
-----------
Die Legende schreibt zusaetzlich zur Grundform eine Liste `vorkommen`
mit stellenbezogener `originalform` und codebezogener Position im
PSEUDO-Dokument. Damit kann `depseudonymize.py` einen wortgleichen
Roundtrip liefern, statt jede Fundstelle mit der Grundform zu ersetzen.

Die Aenderungskarte auf Eingabeseite bleibt v1-kompatibel:
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

Die erzeugte Legende ist Schema v2:
    {
      "alias": "MANDAT-XY",
      "version": 2,
      "eintraege": [
        {
          "code": "PERSON_01",
          "kategorie": "PERSON",
          "grundform": "Dr. Klaus Vogel",
          "vorkommen": [
            {"position": 1, "originalform": "Dr. Klaus Vogel"},
            {"position": 2, "originalform": "Herr Dr. Vogel"},
            ...
          ],
          "kommentar": "Optionaler Hinweis"
        }
      ]
    }

Wichtige Konventionen
---------------------
- Reihenfolge der Ersetzung: laengste Zeichenkette zuerst, damit
  "Dr. Klaus Vogel" vor "Vogel" ersetzt wird. Kollidiert eine Variante
  eines Codes mit der Grundform eines anderen Codes, gewinnt die
  laengere Zeichenkette. Bei gleicher Laenge wird die Grundform vor
  einer Variante bevorzugt.
- Gross-/Kleinschreibung wird beachtet (case-sensitive).
- Ersetzt wird in: Absaetzen (auch verschachtelt), Tabellenzellen,
  Kopf- und Fusszeilen.
- Positionsnummerierung ist codebezogen (nicht dokumentweit) und
  laeuft in Reihenfolge des Auftretens im PSEUDO-Dokument.
- Auf Absatzebene: wir sammeln den Absatztext, wenden die Ersetzungen
  an und schreiben das Ergebnis in den ersten Run zurueck (weitere
  Runs werden geleert). Feinformatierungen (z. B. fette Einzelworte)
  koennen verloren gehen — dokumentiert in references/.
"""

from __future__ import annotations
import argparse
import json
import sys
from datetime import date
from pathlib import Path

try:
    from docx import Document
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

LEGEND_SCHEMA_VERSION = 2


def load_changemap(path: Path) -> dict:
    """Lade und validiere die Aenderungskarte (Eingabe-Schema v1)."""
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    if "alias" not in data or "eintraege" not in data:
        raise ValueError("Aenderungskarte: 'alias' und 'eintraege' sind Pflichtfelder.")

    codes_seen: set[str] = set()
    for eintrag in data["eintraege"]:
        for feld in ("code", "kategorie", "grundform"):
            if feld not in eintrag:
                raise ValueError(f"Aenderungskarte: Eintrag ohne '{feld}': {eintrag}")

        code = eintrag["code"]
        if code in codes_seen:
            raise ValueError(f"Aenderungskarte: Code '{code}' mehrfach vergeben.")
        codes_seen.add(code)

        kategorie = eintrag["kategorie"]
        if kategorie not in CATEGORIES_ALLOWED:
            raise ValueError(
                f"Aenderungskarte: unbekannte Kategorie '{kategorie}' fuer Code '{code}'."
            )
        if not code.startswith(kategorie + "_"):
            raise ValueError(
                f"Aenderungskarte: Code '{code}' passt nicht zu Kategorie '{kategorie}'."
            )

        eintrag.setdefault("varianten", [])
        eintrag.setdefault("kommentar", "")

    return data


def build_search_list(changemap: dict) -> list[tuple[str, str, bool]]:
    """
    Baut eine Liste (suchtext, code, ist_grundform), sortiert nach absteigender
    Laenge des Suchtexts. Bei gleicher Laenge wird die Grundform vor einer
    Variante einsortiert (stabiler Vergleich mit Rang).
    """
    suchliste: list[tuple[str, str, bool]] = []
    for eintrag in changemap["eintraege"]:
        code = eintrag["code"]
        suchliste.append((eintrag["grundform"], code, True))
        for variante in eintrag.get("varianten", []):
            if variante:
                suchliste.append((variante, code, False))
    # laenger zuerst; bei gleicher Laenge: Grundform (True) vor Variante (False)
    suchliste.sort(key=lambda t: (-len(t[0]), 0 if t[1] else 1, 0 if t[2] else 1))
    return suchliste


def find_all_matches(text: str, suchliste) -> list[tuple[int, int, str, str]]:
    """
    Findet alle nicht-ueberlappenden Treffer im Text.

    Vorgehen:
    - Alle Kandidatentreffer sammeln (fuer jeden Suchtext alle Positionen).
    - Nach Textposition sortieren, bei Ueberlappung gewinnt der laengere
      Treffer, bei gleicher Laenge die Grundform vor der Variante.
    - Reihenfolge der Ausgabe: Textposition aufsteigend.

    Rueckgabe: Liste von (start, end, code, suchtext).
    """
    # Kandidaten sammeln
    kandidaten: list[tuple[int, int, str, str, bool]] = []
    for suchtext, code, ist_grundform in suchliste:
        if not suchtext:
            continue
        start = 0
        while True:
            idx = text.find(suchtext, start)
            if idx < 0:
                break
            kandidaten.append((idx, idx + len(suchtext), code, suchtext, ist_grundform))
            start = idx + 1  # ueberlappende Kandidaten zulassen, wird unten aufgeloest

    # Nach Prioritaet sortieren: fruehere Position zuerst, laengerer Treffer bevorzugt,
    # Grundform vor Variante als Tie-Breaker.
    kandidaten.sort(key=lambda t: (t[0], -(t[1] - t[0]), 0 if t[4] else 1))

    # Ueberlappungen aufloesen: greedy in Positionsreihenfolge, laengster Treffer gewinnt
    result: list[tuple[int, int, str, str]] = []
    belegt_bis = -1
    for start, end, code, suchtext, _ist_grundform in kandidaten:
        if start < belegt_bis:
            continue  # Ueberlappung mit bereits akzeptiertem Treffer
        # Pruefen, ob ein spaeterer Kandidat, der an derselben Startposition beginnt,
        # laenger ist. Da wir bereits nach (position, -laenge) sortiert haben,
        # ist der aktuelle Kandidat an dieser Position schon der laengste.
        result.append((start, end, code, suchtext))
        belegt_bis = end
    return result


def replace_in_text(text: str, suchliste, cursor: dict[str, int],
                    vorkommen_by_code: dict[str, list[dict]]) -> str:
    """
    Ersetzt Klartext-Vorkommen durch [CODE] und protokolliert je Ersetzung
    ein Vorkommen {position, originalform} in vorkommen_by_code[code].

    Wichtig: Positionsnummerierung folgt der Textreihenfolge, nicht der
    Laengensortierung der Suchliste. Damit ist die Rueckumwandlung
    positions-getreu wiederherstellbar.

    cursor[code] ist die naechste zu vergebende Positionsnummer je Code.
    """
    treffer = find_all_matches(text, suchliste)
    if not treffer:
        return text

    # Von hinten nach vorne ersetzen, damit die Indizes stabil bleiben.
    # Positionsvergabe aber in Textreihenfolge (also erst am Ende).
    # Loesung: erst Positionen in Textreihenfolge vergeben, dann von hinten
    # ersetzen.
    for start, end, code, suchtext in treffer:  # Textreihenfolge
        pos = cursor.get(code, 1)
        vorkommen_by_code.setdefault(code, []).append(
            {"position": pos, "originalform": suchtext}
        )
        cursor[code] = pos + 1

    for start, end, code, suchtext in reversed(treffer):
        code_bracketed = f"[{code}]"
        text = text[:start] + code_bracketed + text[end:]
    return text


def replace_in_paragraph(paragraph, suchliste, cursor, vorkommen_by_code) -> None:
    runs = paragraph.runs
    if not runs:
        return
    original_text = "".join(run.text for run in runs)
    new_text = replace_in_text(original_text, suchliste, cursor, vorkommen_by_code)
    if new_text == original_text:
        return
    runs[0].text = new_text
    for run in runs[1:]:
        run.text = ""


def replace_in_document(doc, suchliste) -> tuple[dict[str, int], dict[str, list[dict]]]:
    """Wendet die Ersetzungen an, gibt Cursorstand und Vorkommens-Dict zurueck."""
    cursor: dict[str, int] = {}
    vorkommen_by_code: dict[str, list[dict]] = {}

    def walk_container(container):
        for paragraph in container.paragraphs:
            replace_in_paragraph(paragraph, suchliste, cursor, vorkommen_by_code)
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

    return cursor, vorkommen_by_code


def insert_marker(doc, alias: str, version: int) -> None:
    """Fuegt die Kennzeichnungszeile als ersten Absatz ein."""
    marker_text = (
        f"[Pseudonymisiertes Dokument · Alias {alias} · "
        f"Legende v{version} · Codes nicht aufloesen]"
    )
    new_paragraph = doc.paragraphs[0].insert_paragraph_before(marker_text)
    for run in new_paragraph.runs:
        run.italic = True


def build_legend_v2(changemap: dict, vorkommen_by_code: dict[str, list[dict]]) -> dict:
    """Baut die neue Legende (Schema v2) aus Aenderungskarte und Vorkommens-Dict."""
    legende = {
        "alias": changemap["alias"],
        "version": LEGEND_SCHEMA_VERSION,
        "eintraege": [],
    }
    for eintrag in changemap["eintraege"]:
        code = eintrag["code"]
        legende["eintraege"].append({
            "code": code,
            "kategorie": eintrag["kategorie"],
            "grundform": eintrag["grundform"],
            "vorkommen": vorkommen_by_code.get(code, []),
            "kommentar": eintrag.get("kommentar", ""),
        })
    return legende


def write_legend(legende: dict, outdir: Path,
                 pseudo_version_for_dateiname: int) -> tuple[Path, Path]:
    """
    Schreibt die Legende als Markdown und JSON.
    Der Dateiname bleibt konventionell 'LEGENDE_v1' fuer das Erstdokument
    (nicht das Schema-v1, sondern die Legende-Iteration Nr. 1 wie in v1.0).
    Neue Legenden-Iterationen (Fortschreibung) verwenden hoehere Zahlen.
    """
    alias = legende["alias"]
    md_path = outdir / f"{alias}_LEGENDE_v{pseudo_version_for_dateiname}.md"
    json_path = outdir / f"{alias}_LEGENDE_v{pseudo_version_for_dateiname}.json"

    today = date.today().isoformat()
    lines = [
        f"# Legende {alias} (Iteration {pseudo_version_for_dateiname}, Schema v{legende['version']})",
        "",
        f"Erstellt: {today}",
        f"Skill: rwt-skill-pseudonymisierung",
        "",
        "Diese Datei enthaelt die Zuordnung zwischen Codes und Klarnamen.",
        "Sie darf nicht mit dem pseudonymisierten Dokument in offene Umgebungen",
        "gelangen. Zur Rueckumwandlung wird ausschliesslich der JSON-Block unten",
        "oder die separate JSON-Datei benoetigt.",
        "",
        "Legendenschema v2: je Code eine Liste 'vorkommen' mit codebezogener",
        "Position und der an dieser Stelle im Original verwendeten 'originalform'.",
        "Damit ist ein wortgleicher Roundtrip moeglich (Kriterium K5a Inhaltstreue).",
        "",
        "## Codetabelle",
        "",
        "| Code | Kategorie | Grundform | Varianten (dedupliziert) | Vorkommen | Kommentar |",
        "|---|---|---|---|---|---|",
    ]
    for eintrag in legende["eintraege"]:
        grundform = eintrag["grundform"]
        vorkommen = eintrag.get("vorkommen", [])
        n = len(vorkommen)
        # Varianten aus vorkommen dedupliziert, Grundform ausgenommen
        varianten_dedup = []
        gesehen = {grundform}
        for v in vorkommen:
            of = v["originalform"]
            if of not in gesehen:
                varianten_dedup.append(of)
                gesehen.add(of)
        varianten_str = "; ".join(varianten_dedup) or "—"
        pos_liste = ", ".join(str(v["position"]) for v in vorkommen) if vorkommen else "—"
        vorkommen_str = f"{n} (Positionen {pos_liste})" if vorkommen else "0"
        kommentar = eintrag.get("kommentar", "") or "—"
        # Pipes escapen
        g = grundform.replace("|", "\\|")
        vst = varianten_str.replace("|", "\\|")
        vk = vorkommen_str.replace("|", "\\|")
        k = kommentar.replace("|", "\\|")
        lines.append(
            f"| {eintrag['code']} | {eintrag['kategorie']} | {g} | {vst} | {vk} | {k} |"
        )

    lines.extend([
        "",
        "## JSON-Block (maschinenlesbar, Schema v2)",
        "",
        "```json",
        json.dumps(legende, ensure_ascii=False, indent=2),
        "```",
        "",
    ])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    json_path.write_text(
        json.dumps(legende, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return md_path, json_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministische Pseudonymisierung eines DOCX (Skill v1.1, Legende Schema v2)."
    )
    parser.add_argument("--input", required=True, type=Path,
                        help="Original-DOCX (wird nicht veraendert)")
    parser.add_argument("--changemap", required=True, type=Path,
                        help="JSON mit den zu ersetzenden Entitaeten (Eingabe-Schema v1)")
    parser.add_argument("--alias", required=True,
                        help="Alias des Mandats (Kurzbezeichnung, kein Personenbezug)")
    parser.add_argument("--outdir", required=True, type=Path,
                        help="Ausgabeverzeichnis")
    parser.add_argument("--legende-iteration", type=int, default=1,
                        help="Iterationsnummer der Legende (1 fuer Erstlauf, "
                             "2..n fuer Fortschreibung; default 1)")
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

    suchliste = build_search_list(changemap)

    doc = Document(str(args.input))
    _cursor, vorkommen_by_code = replace_in_document(doc, suchliste)
    insert_marker(doc, args.alias, args.legende_iteration)

    pseudo_name = args.input.stem + "_PSEUDO.docx"
    pseudo_path = args.outdir / pseudo_name
    doc.save(str(pseudo_path))

    legende = build_legend_v2(changemap, vorkommen_by_code)
    md_path, json_path = write_legend(legende, args.outdir, args.legende_iteration)

    # Pruefbericht
    codes_ohne_treffer = [
        e["code"] for e in legende["eintraege"] if not e["vorkommen"]
    ]
    ersetzungen = {
        e["code"]: len(e["vorkommen"]) for e in legende["eintraege"]
    }
    report = {
        "skill_version": "1.1",
        "legendenschema": LEGEND_SCHEMA_VERSION,
        "eingabe": str(args.input),
        "ausgabe_pseudo": str(pseudo_path),
        "legende_md": str(md_path),
        "legende_json": str(json_path),
        "alias": args.alias,
        "legende_iteration": args.legende_iteration,
        "ersetzungen": ersetzungen,
        "codes_ohne_treffer": codes_ohne_treffer,
        "hinweis": "Die Legende NICHT in offene KI-Umgebungen laden.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
