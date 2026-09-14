## Purpose

Test site for adding a glossary to the CaRCC AI Facilitation Handbook. Glossary terms are underlined wherever they appear in the handbook. On desktop, they show a short definition on hover and link to the full definition on the glossary page.

Live site: https://lebriggs.github.io/carcc-ai-handbook-glossary-test/

The page text is one real section from the handbook. The glossary definitions are rough drafts used to test how the glossary works, not definitions for review.

## How The Glossary Works

The `abbr` Markdown extension finds glossary terms in the page text and adds the tooltip definition. A small Python hook turns each term into a link to its full entry on the glossary page.

On devices that do not support hover, the tooltip is turned off so tapping a term goes straight to the glossary entry.

## Error Handling

If a term has no matching entry, the build prints a warning naming the term, once per page. The term keeps its tooltip but gets no link. The site
still builds.

## Files

`docs/glossary.md` contains the full glossary entries.

`includes/glossary_tooltips.md` contains the terms that `abbr` looks for and the shorter definitions used in the tooltips. Capitalized and plural forms each need their own line because `abbr` matches the text exactly.

The tooltip definition must match the beginning of the full definition in `glossary.md`. The Python hook uses that text to find the correct glossary entry.

`hooks/glossary_links.py` adds the links from glossary terms to their full entries and warns when it cannot find a matching glossary entry.

## Running The Test Site Locally

py -m pip install -r requirements.txt
py -m mkdocs serve
