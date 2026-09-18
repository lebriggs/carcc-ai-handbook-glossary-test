"""Turns glossary terms into links to the glossary page.

The abbr extension wraps matching terms in <abbr title="...">.
After each page is rendered, this code replaces those elements with links to
the matching heading on glossary.md while preserving the tooltip text.

Terms found in headings, table headings, and glossary.md are excluded.
"""

# Imports

# logging sends the warnings to MkDocs so they show up coloured
# re is Python's regex module
# unescape turns things like &amp; back into normal characters
# markdown_slugify creates the same heading IDs that Markdown uses
# get_relative_url works out the path from the current page to the glossary

import logging
import re
from html import unescape

from mkdocs.utils import get_relative_url
from markdown.extensions.toc import slugify as markdown_slugify

# Set up the logger
# The name has to start with mkdocs. so MkDocs formats the warnings
# hooks says what this file actually is

log = logging.getLogger(f"mkdocs.hooks.{__name__}")

# SETTINGS

# Glossary file locations

# GLOSSARY_PAGE is the glossary page address used when building links.
# Example: "fairness" links to glossary/#fairness
GLOSSARY_PAGE = "glossary/"

# GLOSSARY_SOURCE is the glossary.md file inside docs/.
GLOSSARY_SOURCE = "glossary.md"

# How many times each glossary term is marked on a page

# Variants of the same term share one count, so Fairness and fairness count as one term
# 0 marks every Fairness and every fairness on the page
# 1 marks whichever of them comes first and leaves the rest plain (default)
# 2 marks the first two of them, and so on

# This is the variable you change:

MARKS_PER_PAGE = 1

# Terms already warned about during this build, so each problem is only reported once.
seen = set()

# Clear warning history at the start of each build.
def on_pre_build(config):
    seen.clear()

# Regex patterns for finding terms in the rendered HTML
# ABBR matches the <abbr> tags wrapped around each glossary term
# EXCLUDED matches headings, table header cells, and existing links,
# so glossary terms inside them are left alone

ABBR = re.compile(r'<abbr title="([^"]*)">(.*?)</abbr>', re.DOTALL)
EXCLUDED = re.compile(
    r'(<h[1-6][^>]*>.*?</h[1-6]>|<th[^>]*>.*?</th>|<a\b[^>]*>.*?</a>)',
    re.DOTALL,
)

# Turn a term into the same URL-friendly heading ID that Markdown uses
def slugify(term):
    return markdown_slugify(unescape(term), "-")

# Run after MkDocs renders each page

def on_page_content(html, page, config, files, **kwargs):

    # Do not add glossary links to the glossary page itself.

    if page.file.src_uri == GLOSSARY_SOURCE:
        return html
    
    # How many times each glossary entry has been marked on this page.

    marked = {}

    # Work out the relative path from the current page to glossary.md.

    target = get_relative_url(GLOSSARY_PAGE, page.url)

    # Read glossary headings and definitions.

    with open(f"{config['docs_dir']}/{GLOSSARY_SOURCE}", encoding="utf-8") as f:
        glossary = f.read()

    glossary_entries = re.findall(
        r"^###\s+(.+?)\s*$\n+\s*(.+)$", glossary, re.MULTILINE
    )

    # Replace each glossary tooltip with a link.
    # Flow: tooltip text → compare against full glossary definitions → find the matching glossary heading
    # → build the link to that heading

    def replace(match):

        # Get the tooltip definition and the term as it appears on the page.
        title, term = match.group(1), match.group(2)

        # Match the short tooltip definition to the full glossary definition.
        # The tooltip text must match the beginning of the glossary definition,
        # and the matching heading is used as the link destination.

        matches = [
            heading.strip()
            for heading, definition in glossary_entries
            if definition.strip().startswith(title)
        ]

        # Warn if the tooltip definition matches more than one glossary entry.
        # An ambiguous match cannot be linked reliably.
        if len(matches) > 1:
            if term not in seen:
                seen.add(term)
                log.warning(
                    f"HEY! There's a problem. More than one glossary entry matches: `{term}`"
                )
            return f'<abbr title="{title}">{term}</abbr>'

        heading = matches[0] if matches else None

        # Warn if the tooltip definition does not match an entry in glossary.md.
        # Warn once per term so a repeated term does not flood the output.
        # Leave the term as a tooltip without a link so the site can still build.

        if heading is None:
            if term not in seen:
                seen.add(term)
                log.warning(
                    f"HEY! There's a problem. No matching glossary entry found for: `{term}`"
                )
            return f'<abbr title="{title}">{term}</abbr>'

        # Count this occurrence against the entry's budget for this page.

        marked[heading] = marked.get(heading, 0) + 1

        # Leave later occurrences as plain text, with no underline and no link.

        if MARKS_PER_PAGE and marked[heading] > MARKS_PER_PAGE:
            return term

        # Keep the <abbr> element for tooltip styling, but wrap it in
        # a link to the matching heading on the full glossary page.

        return (
            f'<a class="glossary-link" href="{target}#{slugify(heading)}">'
            f'<abbr title="{title}">{term}</abbr></a>'
        )

    # Remove glossary markup from headings, table headers, and existing links.
    # These occurrences do not count toward the per-page marking limit.
    def strip_abbr(match):
        return match.group(2)

    parts = EXCLUDED.split(html)
    return "".join(
        ABBR.sub(strip_abbr, part) if i % 2 else ABBR.sub(replace, part)
        for i, part in enumerate(parts)
    )