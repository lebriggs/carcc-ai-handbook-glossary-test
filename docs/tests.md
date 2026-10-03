# Behavior Tests & Edge Cases

This page lists behavior tests and edge cases for the glossary.

1. Add a test for stemming. ariants of a term share one count, so the number of underlined occurrences depends on the `MARKS_PER_PAGE` setting in `glossary_links.py`. At the **default of 1**:
This first Audit log is underlined but this later audit logs is not.

2. Add a test for QC & optimization. Checks that an ampersand is handled correctly in the glossary link.

3. Add a test for a term that begins with a number: 3-2-1 backup rule. Checks that a term beginning with a number links correctly to its glossary entry.

4. Add a test for a term that includes an accent: Überanpassung and Naïve Bayes. Checks that accented characters produce the correct glossary links.

5. Add a test that Überanpassung comes before Übung on the glossary page. Checks that accented terms are sorted correctly.

6. Add a test for AI/ML. The slash should be removed from the heading ID rather than turned into a hyphen.

7. Add a test for auditable infrastructure. Checks that a glossary definition can contain bullets.

8. RCD professionals help researchers understand the concept of fairness.  
Checks that fairness and fairness assessment are matched as separate glossary terms.

9. Add a test comparing a one-line definition with a multi-line definition. Checks that the tooltip for the multi-line definition includes `[...]`.  
Use Explainability for the one-line definition and Benchmarking for the multi-line definition.

10. Add an **exclusion** test. Confirm that a glossary term, AI/ML, inside an existing hyperlink stays a normal link instead of being turned into a glossary link.  
Link to my favorite: [AI/ML Workflow Fun](https://youtu.be/dQw4w9WgXcQ)

11. Add an **exclusion** test for a glossary term in a table column header. No glossary links in column headers.

    | Challenge | Provenance should not be a glossary term here. | Neither should Container. |
    | --- | --- | --- |
    | Exciting content. | More exciting content. | Even more exciting content. |

12. Add an **exclusion** test for reference footnotes. Checks that glossary terms in reference footnotes receive neither tooltips nor glossary links.
Let's add a reference here.[@gebruDatasheetsDatasets2021; @mitchellModelCardsModel2019]  
