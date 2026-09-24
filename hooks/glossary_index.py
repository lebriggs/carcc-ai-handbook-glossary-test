"""Builds the glossary index and alphabetical section headings.

The glossary terms are stored as ### headings in glossary.md.
This hook sorts those terms, generates the A to Z index, and inserts a
matching ## section heading before the first term for each letter.

Terms are sorted at build time, so they can be added to glossary.md in any order.
"""

# Imports

# logging reports problems through the MkDocs build output
# re is Python's regex module
# unicodedata lets us fold accented letters back to a plain letter
# Path lets us get the hook name from this Python file
# ascii_uppercase gives us the letters A through Z
# markdown_slugify creates the same heading IDs that Markdown uses

import logging
import re
import unicodedata
from pathlib import Path
from string import ascii_uppercase

from markdown.extensions.toc import slugify as markdown_slugify

# Get the hook name from this Python file for warning messages.
HOOK_NAME = Path(__file__).stem

# Logger for messages from this hook
log = logging.getLogger("mkdocs.hooks")

# SETTINGS

# Glossary file location
GLOSSARY_SOURCE = "glossary.md"

# Heading used for terms that do not start with a letter
NUMERIC_BUCKET = "0-9"

# Find glossary terms stored as ### headings
# Capture the heading text so each term can be sorted and added to the index
TERM_HEADING = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)

# Find the span used for the A to Z glossary index
INDEX_SPAN = re.compile(
    r'(<span class="glossary-index">).*?(</span>)',
    re.DOTALL,
)

# Work out which heading a term belongs under.
# Terms starting with a letter file under that letter.
# Accented letters fold to the plain letter, so Überanpassung files under U.
# Some letters, such as Ł, Ø, and Æ, do not decompose this way and will fall under 0-9.
# Everything else files under 0-9.


def bucket(term):
    first = unicodedata.normalize("NFKD", term.strip()[:1])[:1].upper()
    return first if first in ascii_uppercase else NUMERIC_BUCKET


# Run before MkDocs converts the page from Markdown to HTML
def on_page_markdown(markdown, page, config, files, **kwargs):

    # Only make these changes on glossary.md.
    if page.file.src_uri != GLOSSARY_SOURCE:
        return markdown

    # Find all glossary terms.
    terms = TERM_HEADING.findall(markdown)

    # Stop if there are no glossary terms.
    if not terms:
        return markdown

    # Error Handling:

    # Warn and stop if the index span is missing, rather than failing quietly.
    if not INDEX_SPAN.search(markdown):
        log.warning(
            f"HEY! From: [{HOOK_NAME}]. There's a problem. No glossary-index span found in {GLOSSARY_SOURCE}, so the A to Z index was not built."
        )
        return markdown

    # Warn if two glossary terms would generate the same link.
    # Markdown gives duplicate heading IDs different suffixes, but glossary links
    # only know the term text, so only the first heading can be linked reliably.
    # Solution: rename or delete one of the terms.

    links = {}

    for term in terms:
        link = markdown_slugify(term, "-")
        links.setdefault(link, []).append(term)

    for matching_terms in links.values():
        if len(matching_terms) > 1:
            log.warning(
                f"HEY! From: [{HOOK_NAME}]. These glossary terms would use the same link: "
                + ", ".join(f"`{term}`" for term in matching_terms)
            )

    # Sort the terms alphabetically

    # Cut the page at each ### heading
    # parts holds the page top, then a term and a body, alternating, for each entry
    # After splitting, odd-numbered parts are term headings and
    # even-numbered parts after the first are their matching entry bodies.
    parts = TERM_HEADING.split(markdown)

    # Pair each term with its body, then order by letter group first and term second
    entries = sorted(
        # Pair each term heading with the entry body that follows it.
        zip(parts[1::2], parts[2::2]),
        key=lambda entry: (
            bucket(entry[0]),
            unicodedata.normalize("NFKD", entry[0])
            .encode("ascii", "ignore")
            .decode("ascii")
            .lower(),
        ),
    )

    # Put the page back together, with the top unchanged and the entries in order
    markdown = parts[0] + "\n".join(
        f"### {term}\n\n{body.strip()}\n" for term, body in entries
    )

    # Tell the user if the terms had to be sorted.
    if [term for term, _ in entries] != terms:
        log.info(
            f"HEY! From: [{HOOK_NAME}]. The terms in {GLOSSARY_SOURCE} weren't in alphabetical order. "
            "I sorted them for you."
        )

    # Work out which headings have glossary entries.
    headings_used = {bucket(term) for term in terms}

    # Build the index, with 0-9 at the left end.
    # Headings with entries become links; the rest stay as plain text.
    # \u00a0 is a non-breaking space, so a dot never starts a wrapped line.
    index = "\u00a0· ".join(
        f"[{heading}](#{heading.lower()})" if heading in headings_used else heading
        for heading in [NUMERIC_BUCKET, *ascii_uppercase]
    )

    # Put the generated index inside the existing glossary-index span.
    # A function replacement keeps the index text out of regex escape handling.
    markdown = INDEX_SPAN.sub(
        lambda match: match.group(1) + index + match.group(2),
        markdown,
        count=1,
    )

    # Add a ## heading before the first term in each group.
    current_heading = None
    output = []

    for line in markdown.splitlines():
        match = TERM_HEADING.match(line)

        if match:
            heading = bucket(match.group(1))

            if heading != current_heading:
                output.append(f"## {heading}")
                output.append("")
                current_heading = heading

        output.append(line)

    return "\n".join(output)
