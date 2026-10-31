
import re
from pathlib import Path
import json

import bibtexparser
from pylatexenc.latex2text import LatexNodes2Text

CATEGORIES = {
    "preprint": "Preprints and Under Review",
    "journal": "Journals",
    "conference": "Conferences",
    "patent": "Patents",
    "book": "Book Chapters",
}

latex = LatexNodes2Text()

def clean(value):
    if not value:
        return ""
    return re.sub(
        r"\s+", " ", latex.latex_to_text(value)
    ).strip()

def md(value):
    """Escape Markdown formatting characters."""
    return re.sub(
        r"([\\`*_{}\[\]<>])",
        r"\\\1",
        clean(value)
    )

def get_url(entry):
    """Find a publication link, if available."""
    for field in ("url", "pdf"):
        url = clean(entry.get(field, ""))
        if url.startswith(("https://", "http://")):
            return url

    doi = clean(entry.get("doi", ""))
    if doi:
        if doi.startswith(("https://", "http://")):
            return doi
        return "https://doi.org/" + doi

    eprint = clean(entry.get("eprint", ""))
    if eprint and re.fullmatch(
        r"\d{4}\.\d{4,5}(v\d+)?", eprint
    ):
        return "https://arxiv.org/abs/" + eprint

    return ""

def format_authors(entry):
    authors = entry.get("author", "")
    if not authors:
        return ""

    names = re.split(r"\s+and\s+", authors)
    formatted = []

    for name in names:
        name = clean(name)

        # Convert "Last, First" to "First Last"
        if "," in name:
            parts = name.split(",", 1)
            name = parts[1].strip() + " " + parts[0].strip()

        formatted.append(md(name))

    return ", ".join(formatted)

def format_entry(entry, category):
    title = md(entry.get("title", "Untitled"))
    authors = format_authors(entry)
    year = md(entry.get("year", ""))
    url = get_url(entry)

    # Title and authors on first line
    first_line = f"**{title}**"
    if authors:
        first_line += f", {authors}"

    # Venue
    if category == "preprint":
        eprint = md(entry.get("eprint", ""))
        venue = "arXiv Preprint"
        if eprint:
            venue += f" (arXiv:{eprint})"

    elif category == "journal":
        venue = md(entry.get("journal", ""))

    elif category == "conference":
        venue = md(entry.get("booktitle", ""))

    elif category == "book":
        venue = md(entry.get("publisher", ""))

    elif category == "patent":
        venue = md(
            entry.get("number", "")
            or entry.get("howpublished", "Patent")
        )

    else:
        venue = ""

    second_line = f"*{venue}*" if venue else ""

    if year:
        second_line += f" | {year}" if second_line else year

    if url:
        second_line += f" | [Link](<{url}>)"

    bib_id = entry["ID"]

    second_line += (
        f' | <a href="#" class="bibtex-copy" '
        f'data-bib-id="{bib_id}">BibTeX</a>'
    )

    return first_line + "  \n" + second_line

# Read BibTeX
with open("publications.bib", encoding="utf-8") as f:
    database = bibtexparser.load(f)

from bibtexparser.bibdatabase import BibDatabase

bibtex_entries = {}

for entry in database.entries:
    single = BibDatabase()
    single.entries = [entry]
    bibtex_entries[entry["ID"]] = bibtexparser.dumps(single)

with open("bibtex.json", "w", encoding="utf-8") as f:
    json.dump(bibtex_entries, f, ensure_ascii=False, indent=2)

groups = {key: [] for key in CATEGORIES}

for entry in database.entries:
    keywords = {
        word.strip().lower()
        for word in re.split(
            r"[,;]", entry.get("keywords", "")
        )
    }

    for category in CATEGORIES:
        if category in keywords:
            groups[category].append(entry)
            break

# Sort newest first
for entries in groups.values():
    entries.sort(
        key=lambda e: (
            int(e.get("year", "0"))
            if e.get("year", "").isdigit()
            else 0,
            clean(e.get("title", ""))
        ),
        reverse=True
    )

# Generate Quarto page
output = [
    "---",
    'title: "Publications"',
    "---",
    "",
    "## Preprints and Under Review",
    ""
]

for entry in groups["preprint"]:
    output.append(format_entry(entry, "preprint"))
    output.append("")

output.extend([
    "## Peer-Reviewed",
    "",
    "### Journals",
    ""
])

for entry in groups["journal"]:
    output.append(format_entry(entry, "journal"))
    output.append("")

output.extend([
    "### Conferences",
    ""
])

for entry in groups["conference"]:
    output.append(format_entry(entry, "conference"))
    output.append("")

for category in ("patent", "book"):
    output.append(f"## {CATEGORIES[category]}")
    output.append("")

    for entry in groups[category]:
        output.append(format_entry(entry, category))
        output.append("")

Path("publications.qmd").write_text(
    "\n".join(output),
    encoding="utf-8"
)

print("Generated publications.qmd successfully.")
