"""Turns glossary terms into links to the glossary page.

The abbr extension wraps matching terms in <abbr title="...">.
After each page is rendered, this code replaces those elements with links to
the matching heading on glossary.md while preserving the tooltip text.

Terms found in headings and glossary.md are excluded.
"""

# Imports

# logging sends the warnings to MkDocs so they show up coloured
# re is Python's regex module
# unescape turns things like &amp; back into normal characters
# get_relative_url works out the path from the current page to the glossary.

import logging
import re
from html import unescape

from mkdocs.utils import get_relative_url

# Set up the logger
# The name has to start with mkdocs. so MkDocs formats the warnings
# hooks says what this file actually is

log = logging.getLogger(f"mkdocs.hooks.{__name__}")

# Glossary file locations

# GLOSSARY_PAGE is the glossary page address used when building links.
# Example: "fairness" links to glossary/#fairness
GLOSSARY_PAGE = "glossary/"

# GLOSSARY_SOURCE is the glossary.md file inside docs/.
GLOSSARY_SOURCE = "glossary.md"

# Regex patterns for finding terms in the rendered HTML
# ABBR matches the <abbr> tags wrapped around each glossary term
# HEADING matches a whole heading, so terms inside one can be left alone

ABBR = re.compile(r'<abbr title="([^"]*)">(.*?)</abbr>', re.DOTALL)
HEADING = re.compile(r'(<h[1-6][^>]*>.*?</h[1-6]>)', re.DOTALL)

# Turn a term into a URL-friendly heading ID

def slugify(term):
    return re.sub(r"[^a-z0-9]+", "-", unescape(term).lower().strip()).strip("-")

# Run after MkDocs renders each page

def on_page_content(html, page, config, files, **kwargs):

    # Do not add glossary links to the glossary page itself.

    if page.file.src_uri == GLOSSARY_SOURCE:
        return html

    # Terms already warned about on this page, so each one is only reported once.

    seen = set()

    # Work out the relative path from the current page to glossary.md.

    target = get_relative_url(GLOSSARY_PAGE, page.url)

    # Read glossary headings and definitions.

    with open(f"{config['docs_dir']}/{GLOSSARY_SOURCE}", encoding="utf-8") as f:
        glossary = f.read()

    glossary_entries = re.findall(
        r"^##\s+(.+?)\s*$\n+\s*(.+)$", glossary, re.MULTILINE
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

        heading = next(
            (
                heading.strip()
                for heading, definition in glossary_entries
                if definition.strip().startswith(title)
            ),
            None,
        )

        # Error Handling:
        
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
        
        # Keep the <abbr> element for tooltip styling, but wrap it in
        # a link to the matching heading on the full glossary page.

        return (
            f'<a class="glossary-link" href="{target}#{slugify(heading)}">'
            f'<abbr title="{title}">{term}</abbr></a>'
        )

    # Leave headings unchanged and add glossary links everywhere else.

    parts = HEADING.split(html)
    return "".join(
        part if i % 2 else ABBR.sub(replace, part)
        for i, part in enumerate(parts)
    )