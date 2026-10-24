"""Turns glossary terms into links to the glossary page.

The abbr extension wraps matching terms in <abbr title="...">.
After each page is rendered, this code replaces those elements with links to
the matching heading on glossary.md while preserving the tooltip text.

Headings, table header cells, existing links, and reference footnotes are
excluded. Glossary definitions use separate counts and do not link to themselves.
"""

# Imports

# logging sends the warnings to MkDocs so they show up coloured
# re is Python's regex module
# unescape turns things like &amp; back into normal characters
# Path lets us get the hook name from this Python file
# here builds file paths from the project root
# markdown_slugify creates the same heading IDs that Markdown uses
# get_relative_url works out the path from the current page to the glossary

import logging
import re
from html import unescape
from pathlib import Path
from herepath import here
from markdown.extensions.toc import slugify as markdown_slugify
from mkdocs.utils import get_relative_url

# Get the hook name from this Python file for warning messages.
HOOK_NAME = Path(__file__).stem

# Set up the logger
# The name has to start with mkdocs. so MkDocs formats the warnings
# hooks says what this file actually is

log = logging.getLogger(f"mkdocs.hooks.{__name__}")

# SETTINGS

# Glossary file locations

# GLOSSARY_URL is the glossary page address used when building links.
# Example: "fairness" links to glossary/#fairness
GLOSSARY_URL = "glossary/"

# Glossary page used by MkDocs
GLOSSARY_PAGE = "glossary.md"

# Glossary source file
GLOSSARY_SOURCE = here("docs", "glossary.md")

# How many times each glossary term is marked on a page

# Variants of the same term share one count, so Fairness and fairness count as one term
# 0 marks every Fairness and every fairness on the page
# 1 marks whichever of them comes first and leaves the rest plain (default)
# 2 marks the first two of them, and so on

# This is the variable you change:

MARKS_PER_PAGE = 1

# On glossary.md, count each term separately within each definition.
# 1 links only its first occurrence in that definition; 0 links every occurrence.
MARKS_PER_DEFINITION = 1

# Terms already warned about during this build, so each problem is only reported once.
seen = set()


# Clear warning history at the start of each build.
def on_pre_build(config):
    seen.clear()


# Regex patterns for finding terms in the rendered HTML

# Find glossary terms that Markdown has wrapped in <abbr> tags.
# Capture the tooltip text separately from the visible term text.
ABBR = re.compile(r'<abbr title="([^"]*)">(.*?)</abbr>', re.DOTALL)

# Find HTML areas where glossary behavior should be removed:
# headings, table header cells, existing links, and reference footnotes.
EXCLUDED = re.compile(
    r'(<h[1-6][^>]*>.*?</h[1-6]>|<th[^>]*>.*?</th>|<a\b[^>]*>.*?</a>|<div class="footnote">.*?</div>)',
    re.DOTALL,
)


# Turn a term into the same URL-friendly heading ID that Markdown uses
def slugify(term):
    return markdown_slugify(unescape(term), "-")


# Identify each rendered glossary entry by its <h3> heading.
# The A–Z section headings are <h2> and are not definition boundaries.
GLOSSARY_HEADING = re.compile(r'(<h3\b[^>]*>.*?</h3>)', re.DOTALL)


# SHARED GLOSSARY LOOKUP

# Read glossary headings and definitions for both handbook pages and glossary links.
# Each glossary term must be a ### heading, followed by its full definition.
def read_glossary_entries():

    with open(GLOSSARY_SOURCE, encoding="utf-8") as f:
        glossary = f.read()

    return re.findall(
        r"^###\s+(.+?)\s*$\n+\s*(.+)$", glossary, re.MULTILINE
    )


# Match the short tooltip definition to the full glossary definition.
# Variants use the same definition, so they resolve to the same canonical heading.
# Report missing and ambiguous matches through the existing MkDocs warnings.
def find_glossary_heading(title, term, glossary_entries):

    # Remove the continuation marker only when matching to the glossary definition.
    match_title = title.removesuffix("\u00a0[...]")

    # The tooltip text must match the beginning of the glossary definition,
    # and the matching heading is used as the link destination.
    matches = [
        heading.strip()
        for heading, definition in glossary_entries
        if definition.strip().startswith(match_title)
    ]

    # Warn if the tooltip definition matches more than one glossary entry.
    # An ambiguous match cannot be linked reliably.
    # Report the conflicting glossary entries together and only once.

    if len(matches) > 1:
        warning_key = ("ambiguous", tuple(matches))

        if warning_key not in seen:
            seen.add(warning_key)
            log.warning(
                f"HEY! From: [{HOOK_NAME}]. There's a problem. "
                f"More than one glossary entry shares a definition: "
                + ", ".join(f"`{heading}`" for heading in matches)
            )

        return None

    heading = matches[0] if matches else None

    # Warn if the tooltip definition does not match an entry in glossary.md.
    # Warn once per term so a repeated term does not flood the output.
    # Leave the term as a tooltip without a link so the site can still build.

    if heading is None:
        if term not in seen:
            seen.add(term)
            log.warning(
                f"HEY! From: [{HOOK_NAME}]. There's a problem. "
                f"The tooltip definition for `{term}` does not match any glossary definition."
            )

    return heading


# Remove glossary markup from excluded elements, leaving the text as written.
def strip_abbr(match):
    return match.group(2)


# Run after MkDocs renders each page


def on_page_content(html, page, config, files, **kwargs):

    # The glossary page has its own linking rules, handled below.

    if page.file.src_uri == GLOSSARY_PAGE:
        return link_glossary_definitions(html)

    # How many times each glossary entry has been marked on this page.

    marked = {}

    # Work out the relative path from the current page to glossary.md.

    target = get_relative_url(GLOSSARY_URL, page.url)

    # Read glossary headings and definitions.
    glossary_entries = read_glossary_entries()

    # Replace each glossary tooltip with a link.
    # Flow: tooltip text → compare against full glossary definitions → find the matching glossary heading
    # → build the link to that heading

    def replace(match):

        # Get the tooltip definition and the term as it appears on the page.
        title, term = match.group(1), match.group(2)

        # Resolve the term to its canonical glossary heading.
        heading = find_glossary_heading(title, term, glossary_entries)
        if heading is None:
            return f'<abbr title="{title}">{term}</abbr>'

        # Count this occurrence against the entry's budget for this page.

        marked[heading] = marked.get(heading, 0) + 1

        # Leave later occurrences as plain text, with no underline and no link.

        if MARKS_PER_PAGE and marked[heading] > MARKS_PER_PAGE:
            return term

        # Keep the <abbr> element for tooltip styling, but wrap it in
        # a link to the matching heading on the full glossary page.

        # A keyboard accessibility issue: 
        # While navigating handbook pages via Tab, glossary links receive focus, but tooltips do not appear.
        # In Microsoft Edge, moving the title attribute onto the link caused overlapping
        # native Edge and Material tooltips. This issue is not easily resolved.
        # Keyboard users can still follow links to the full glossary definitions.
        # A similar issue was documented in Bootstrap (2015):
        # https://github.com/twbs/bootstrap/issues/18692

        return (
            f'<a class="glossary-link" href="{target}#{slugify(heading)}">'
            f'<abbr title="{title}">{term}</abbr></a>'
        )

    # Remove glossary markup from headings, table headers, reference footnotes, and existing links.
    # These occurrences do not count toward the per-page marking limit.
    # EXCLUDED.split() keeps the excluded HTML blocks in the list.
    # Even-numbered parts are normal content; odd-numbered parts are excluded areas.
    # Normal content gets glossary links; excluded areas only have the <abbr> markup removed.

    parts = EXCLUDED.split(html)
    output = []

    for i, part in enumerate(parts):
        if i % 2:
            # Remove glossary markup from excluded areas, leaving the text as written.
            output.append(ABBR.sub(strip_abbr, part))
        else:
            # Add glossary links to normal content, using the per-page marking limit.
            output.append(ABBR.sub(replace, part))

    return "".join(output)


# GLOSSARY PAGE LINKS

# Link terms inside each glossary definition, without changing handbook-page behavior.
# Counts start over at each <h3> entry, rather than once for the entire page.
def link_glossary_definitions(html):

    # Use the same canonical headings and tooltip definitions as the handbook links.
    # The rendered <h3> IDs tell us which definition we are currently reading.
    glossary_entries = read_glossary_entries()
    terms_by_id = {slugify(heading): heading for heading, _ in glossary_entries}

    # Keep the page title and A–Z index, then process one definition at a time.
    # Splitting on <h3> leaves the <h2> letter headings in place.
    sections = GLOSSARY_HEADING.split(html)
    output = [ABBR.sub(strip_abbr, sections[0])]

    for heading_html, definition_html in zip(sections[1::2], sections[2::2]):
        heading_id = re.search(r'\bid="([^"]+)"', heading_html).group(1)
        current_term = terms_by_id[heading_id]
        marked = {}

        # Leave all glossary entry headings as ordinary text, with no tooltip.
        output.append(ABBR.sub(strip_abbr, heading_html))

        def replace_in_definition(match):
            title, term = match.group(1), match.group(2)
            # Resolve variants by their tooltip definitions, just as on handbook pages.
            heading = find_glossary_heading(title, term, glossary_entries)
            if heading is None:
                return f'<abbr title="{title}">{term}</abbr>'

            # The current term (including its variants) should never link to itself.
            if heading == current_term:
                return term

            # Each different term gets its own count within this definition.
            marked[heading] = marked.get(heading, 0) + 1
            if MARKS_PER_DEFINITION and marked[heading] > MARKS_PER_DEFINITION:
                return term

            # Use a same-page anchor; preserve the existing tooltip and link styling.
            return (
                f'<a class="glossary-link" href="#{slugify(heading)}">'
                f'<abbr title="{title}">{term}</abbr></a>'
            )

        # Keep the handbook exclusions: no links in headings, table headers,
        # existing links, or reference footnotes.
        parts = EXCLUDED.split(definition_html)
        output.append("".join(
            ABBR.sub(strip_abbr, part) if i % 2 else ABBR.sub(replace_in_definition, part)
            for i, part in enumerate(parts)
        ))

    return "".join(output)
