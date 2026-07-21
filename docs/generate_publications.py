#!/usr/bin/env python3
"""Generate the English and Spanish publication pages from src/publications.bib.

The parser is intentionally dependency-free so the script also works in a clean
CI environment. Add an optional ``category`` field to a BibTeX entry when its
badge cannot be inferred from the entry type, for example::

    category = {report}

Supported category names are: research article, preprint, report, conference
paper, and book chapter. Unknown values are displayed as written.
"""

from __future__ import annotations

import html
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BIB_PATH = ROOT / "src" / "publications.bib"
OUTPUTS = {
    "en": ROOT / "docs" / "publications.md",
    "es": ROOT / "docs" / "es" / "publications.md",
}

PAGE_COPY = {
    "en": {
        "description": "Selected scientific publications by David Montero Loaiza.",
        "banner_alt": "Earth observation image",
        "title": "Publications",
        "lead": (
            "  Selected research across Earth observation, Earth system data cubes, vegetation dynamics,\n"
            "  artificial intelligence, and open scientific software. The complete record is available on\n"
            '  <a href="https://scholar.google.com/citations?user=-wTpOdsAAAAJ&hl=en">Google Scholar</a>.'
        ),
    },
    "es": {
        "description": "Publicaciones científicas seleccionadas de David Montero Loaiza.",
        "banner_alt": "Imagen de observación de la Tierra",
        "title": "Publicaciones",
        "lead": (
            "  Una selección de investigaciones sobre observación de la Tierra, cubos de datos del sistema Tierra,\n"
            "  dinámica de la vegetación, inteligencia artificial y software científico abierto. El registro completo\n"
            '  está disponible en <a href="https://scholar.google.com/citations?user=-wTpOdsAAAAJ&hl=es">Google Scholar</a>.'
        ),
    },
}

CATEGORY_LABELS = {
    "en": {
        "research article": "Research article",
        "preprint": "Preprint",
        "report": "Report",
        "conference paper": "Conference paper",
        "book chapter": "Book chapter",
        "thesis": "Thesis",
    },
    "es": {
        "research article": "Artículo científico",
        "preprint": "Preprint",
        "report": "Informe",
        "conference paper": "Artículo de conferencia",
        "book chapter": "Capítulo de libro",
        "thesis": "Tesis",
    },
}

ENTRY_DEFAULT_CATEGORIES = {
    "article": "research article",
    "misc": "preprint",
    "inproceedings": "conference paper",
    "conference": "conference paper",
    "inbook": "book chapter",
    "incollection": "book chapter",
    "techreport": "report",
    "report": "report",
    "phdthesis": "thesis",
    "mastersthesis": "thesis",
}

COMBINING_MARKS = {
    '"': "\u0308",
    "'": "\u0301",
    "`": "\u0300",
    "^": "\u0302",
    "~": "\u0303",
    "=": "\u0304",
    ".": "\u0307",
    "u": "\u0306",
    "v": "\u030C",
    "H": "\u030B",
}


def parse_bibtex(source: str) -> list[dict[str, str]]:
    """Parse the subset of BibTeX used by the publication database."""
    entries: list[dict[str, str]] = []
    start_pattern = re.compile(r"@(\w+)\s*([({])", re.IGNORECASE)
    position = 0

    while match := start_pattern.search(source, position):
        entry_type = match.group(1).lower()
        opening = match.group(2)
        closing = "}" if opening == "{" else ")"
        body_start = match.end()
        depth = 1
        index = body_start
        quoted = False
        escaped = False

        while index < len(source) and depth:
            character = source[index]
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = not quoted
            elif not quoted:
                if character == opening:
                    depth += 1
                elif character == closing:
                    depth -= 1
            index += 1

        if depth:
            raise ValueError(f"Unclosed @{entry_type} entry near character {match.start()}")

        position = index
        if entry_type in {"comment", "preamble", "string"}:
            continue

        body = source[body_start : index - 1]
        key_end = _find_top_level_comma(body)
        if key_end < 0:
            raise ValueError(f"BibTeX entry @{entry_type} has no citation key separator")

        entry: dict[str, str] = {
            "entrytype": entry_type,
            "key": body[:key_end].strip(),
        }
        entry.update(_parse_fields(body[key_end + 1 :]))
        entries.append(entry)

    return entries


def _find_top_level_comma(value: str) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index, character in enumerate(value):
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == '"':
            quoted = not quoted
        elif not quoted:
            if character in "{(":
                depth += 1
            elif character in "})":
                depth -= 1
            elif character == "," and depth == 0:
                return index
    return -1


def _parse_fields(source: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    index = 0

    while index < len(source):
        while index < len(source) and (source[index].isspace() or source[index] == ","):
            index += 1
        if index >= len(source):
            break

        name_match = re.match(r"[\w-]+", source[index:])
        if not name_match:
            raise ValueError(f"Could not parse BibTeX field near: {source[index:index + 40]!r}")
        name = name_match.group(0).lower()
        index += len(name_match.group(0))

        while index < len(source) and source[index].isspace():
            index += 1
        if index >= len(source) or source[index] != "=":
            raise ValueError(f"Expected '=' after BibTeX field {name!r}")
        index += 1
        while index < len(source) and source[index].isspace():
            index += 1

        if index >= len(source):
            fields[name] = ""
            break

        if source[index] in "{\"":
            opening = source[index]
            closing = "}" if opening == "{" else '"'
            index += 1
            value_start = index
            depth = 1
            escaped = False
            while index < len(source) and depth:
                character = source[index]
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif opening == "{" and character == "{":
                    depth += 1
                elif character == closing:
                    depth -= 1
                index += 1
            if depth:
                raise ValueError(f"Unclosed value for BibTeX field {name!r}")
            value = source[value_start : index - 1]
        else:
            value_start = index
            while index < len(source) and source[index] != ",":
                index += 1
            value = source[value_start:index]

        fields[name] = value.strip()

    return fields


def clean_tex(value: str) -> str:
    """Convert common BibTeX/LaTeX text escapes to readable Unicode."""
    value = html.unescape(value)
    value = value.replace("---", "—").replace("--", "–")
    value = value.replace(r"\&", "&").replace("~", " ")
    value = value.replace(r"\i", "i").replace(r"\j", "j")

    accent_pattern = re.compile(r'''\\(["'`^~=\.uvH])\s*\{?([A-Za-z])\}?''')

    def add_accent(match: re.Match[str]) -> str:
        mark = COMBINING_MARKS[match.group(1)]
        return unicodedata.normalize("NFC", match.group(2) + mark)

    value = accent_pattern.sub(add_accent, value)
    value = re.sub(
        r"\\c\s*\{?([A-Za-z])\}?",
        lambda match: unicodedata.normalize("NFC", match.group(1) + "\u0327"),
        value,
    )
    value = re.sub(r"\\[a-zA-Z]+\s*", "", value)
    value = value.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", value).strip()


def initials(given_names: str) -> str:
    parts = re.findall(r"[^\W\d_]+(?:-[^\W\d_]+)?", given_names, flags=re.UNICODE)
    rendered: list[str] = []
    for part in parts:
        rendered.append("-".join(f"{piece[0].upper()}." for piece in part.split("-") if piece))
    return " ".join(rendered)


def format_person(raw_name: str) -> str:
    name = clean_tex(raw_name)
    parts = [part.strip() for part in name.split(",")]
    if len(parts) >= 2:
        family, given = parts[0], parts[1]
    else:
        tokens = name.split()
        family, given = tokens[-1], " ".join(tokens[:-1])

    rendered = html.escape(family)
    given_initials = initials(given)
    if given_initials:
        rendered += f", {html.escape(given_initials)}"

    normalized_family = unicodedata.normalize("NFKD", family).encode("ascii", "ignore").decode().casefold()
    if normalized_family in {"montero", "montero loaiza"}:
        return f"<strong>{rendered}</strong>"
    return rendered


def format_authors(raw_authors: str) -> str:
    authors = [format_person(author) for author in re.split(r"\s+and\s+", raw_authors.strip())]
    if len(authors) > 20:
        return ", ".join(authors[:19]) + ", … " + authors[-1]
    if len(authors) == 1:
        return authors[0]
    if len(authors) == 2:
        return f"{authors[0]}, &amp; {authors[1]}"
    return ", ".join(authors[:-1]) + f", &amp; {authors[-1]}"


def publication_category(entry: dict[str, str]) -> str:
    custom = clean_tex(entry.get("category", "")).strip().casefold()
    if custom:
        return custom

    entry_type = entry["entrytype"]
    journal = clean_tex(entry.get("journal", "")).casefold()
    if entry_type == "article" and not journal:
        return "preprint"
    if "international archives of the photogrammetry" in journal:
        return "conference paper"
    return ENTRY_DEFAULT_CATEGORIES.get(entry_type, entry_type.replace("_", " "))


def citation_source(entry: dict[str, str], category: str) -> str:
    entry_type = entry["entrytype"]
    journal = clean_tex(entry.get("journal", ""))
    booktitle = clean_tex(entry.get("booktitle", ""))
    publisher = clean_tex(entry.get("publisher", ""))
    volume = clean_tex(entry.get("volume", ""))
    number = clean_tex(entry.get("number", ""))
    pages = clean_tex(entry.get("pages", ""))

    if journal:
        source = f"<em>{html.escape(journal)}</em>"
        if volume:
            source += f", {html.escape(volume)}"
            if number:
                source += f"({html.escape(number)})"
        elif number:
            source += f", ({html.escape(number)})"
        if pages:
            source += f", {html.escape(pages)}"
        return source

    if booktitle:
        prefix = "In " if entry_type in {"inproceedings", "conference", "inbook", "incollection"} else ""
        source = f"<em>{prefix}{html.escape(booktitle)}</em>"
        if pages:
            source += f" (pp. {html.escape(pages)})"
        if publisher:
            source += f". {html.escape(publisher)}"
        return source

    if publisher:
        escaped_publisher = html.escape(publisher)
        return f"<em>{escaped_publisher}</em>" if category == "preprint" else escaped_publisher
    return ""


def format_citation(entry: dict[str, str]) -> str:
    category = publication_category(entry)
    authors = format_authors(entry.get("author", ""))
    year = html.escape(clean_tex(entry.get("year", "n.d.")))
    title = html.escape(clean_tex(entry.get("title", "Untitled")))
    source = citation_source(entry, category)

    citation = f"{authors} ({year}). <strong>{title}</strong>."
    if source:
        citation += f" {source}."

    doi = clean_tex(entry.get("doi", ""))
    url = clean_tex(entry.get("url", ""))
    link = f"https://doi.org/{doi}" if doi else url
    if link:
        escaped_link = html.escape(link, quote=True)
        citation += f' <a href="{escaped_link}">{html.escape(link)}</a>'
    return citation


def render_page(entries: list[dict[str, str]], language: str) -> str:
    copy = PAGE_COPY[language]
    grouped: dict[int, list[dict[str, str]]] = defaultdict(list)
    for entry in entries:
        raw_year = clean_tex(entry.get("year", ""))
        if not raw_year.isdigit():
            raise ValueError(f"Entry {entry['key']!r} has an invalid or missing year: {raw_year!r}")
        grouped[int(raw_year)].append(entry)

    lines = [
        "---",
        "outline: deep",
        f"description: {copy['description']}",
        "---",
        "",
        "<!-- Generated by docs/generate_publications.py from src/publications.bib. Do not edit manually. -->",
        "",
        f'<PageBanner src="/publications-hero-12-5.webp" alt="{copy["banner_alt"]}" />',
        "",
        f"# {copy['title']}",
        "",
        '<p class="page-lead">',
        copy["lead"],
        "</p>",
        "",
        f'<PublicationSearch lang="{language}" />',
        "",
    ]

    for year in sorted(grouped, reverse=True):
        lines.extend([f"## {year}", "", '<div class="publication-list">'])
        for entry in grouped[year]:
            category = publication_category(entry)
            label = CATEGORY_LABELS[language].get(category, category.title())
            key = html.escape(entry["key"], quote=True)
            lines.extend(
                [
                    f'  <article class="publication-item" data-publication-key="{key}">',
                    f'    <span class="publication-tag">{html.escape(label)}</span>',
                    f"    <p>{format_citation(entry)}</p>",
                    "  </article>",
                ]
            )
        lines.extend(["</div>", ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    entries = parse_bibtex(BIB_PATH.read_text(encoding="utf-8"))
    if not entries:
        raise ValueError(f"No BibTeX entries found in {BIB_PATH}")

    for language, output_path in OUTPUTS.items():
        rendered = render_page(entries, language)
        if output_path.exists() and output_path.read_text(encoding="utf-8") == rendered:
            status = "unchanged"
        else:
            output_path.write_text(rendered, encoding="utf-8")
            status = "updated"
        print(f"{output_path.relative_to(ROOT)}: {status} ({len(entries)} publications)")


if __name__ == "__main__":
    main()
