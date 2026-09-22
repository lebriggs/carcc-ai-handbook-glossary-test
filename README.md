# Test Glossary for the CaRCC AI Facilitation Handbook

## Summary

Test site for adding a glossary to the CaRCC AI Facilitation Handbook. By default, the first occurrence of each glossary entry on a page is underlined. On desktop, it shows a short definition on hover and links to the full definition on the glossary page.

## Live Site

[https://lebriggs.github.io/carcc-ai-handbook-glossary-test/](https://lebriggs.github.io/carcc-ai-handbook-glossary-test/)

## How The Glossary Works

The `abbr` Markdown extension finds glossary terms in the page text and adds the tooltip definition. A small Python hook links the first occurrence of each glossary entry on a page to its full entry on the glossary page.

On devices that do not support hover, the tooltip is turned off so tapping a term goes straight to the glossary entry.

A second Python hook builds the A–Z index at the top of the glossary page and adds a letter heading before the first term under each letter. Letters with no entries stay as plain text in the index. Terms that do not begin with a letter file under a `0-9` heading, and accented letters file under their plain letter, so Überanpassung appears under U. The hook also sorts the terms in `glossary.md` in alphabetical order.

The page text comes from two real sections of the handbook. The glossary definitions are rough drafts used to test how the glossary works, not definitions for review.

## Exclusions

Glossary links are not added to:

- the glossary page itself
- headings
- table header cells
- terms that are already inside another link

## Error Handling

- If no glossary entry matches a tooltip definition, the build warns and leaves the term as a tooltip without a link.
- If more than one glossary entry shares a definition, the build warns and lists the matching entries. The term remains a tooltip without a link.
- If glossary terms would use the same link, the build warns and lists the conflicting terms.
- If the A–Z index span is missing, the build warns and leaves the glossary page as written without building the index.
- Each problem is reported once per build, and the site still builds.

## Files

- `docs/glossary.md` contains the full glossary entries. It also holds the empty span that the A–Z index is written into at build time.
- `includes/glossary_tooltips.md` contains the terms that `abbr` looks for and the shorter definitions used in the tooltips. Capitalized and plural forms each need their own line because `abbr` matches the text exactly. The tooltip definition must match the beginning of the full definition in `glossary.md`, because the hook uses that text to find the correct glossary entry.
- `hooks/glossary_links.py` adds the links from glossary terms to their full entries.
- `hooks/glossary_index.py` sorts the glossary terms and builds the A–Z index and letter headings.
- `docs/stylesheets/style.css` styles the glossary terms, the tooltips, the A–Z index, and the letter headings.

## What The Glossary Needs In mkdocs.yaml

Everything in `mkdocs.yaml` except `site_name` and `nav` is there for the glossary. Moving this into the handbook means bringing across:

- `hooks`, listing both `hooks/glossary_links.py` and `hooks/glossary_index.py`.
- `content.tooltips` under theme features, which is what draws the tooltip.
- `markdown_extensions`, all of it: `abbr` for the tooltip definitions, `attr_list` for the `{.glossary-page }` class on the glossary heading, and `pymdownx.snippets` with `auto_append` so the tooltip file is added to every page.
- `extra_css`, pointing at `stylesheets/style.css`.

## Running The Test Site Locally

    py -m pip install -r requirements.txt
    py -m mkdocs serve
    