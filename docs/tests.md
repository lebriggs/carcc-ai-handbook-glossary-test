# Behavior Tests & Edge Cases

This page lists behavior tests and edge cases for the glossary.

1. Add a test for term variants. Checks that all variants of the same glossary term share one count per page, controlled by the `MARKS_PER_PAGE` setting in `glossary_links.py`. At the **default of 1**:  
The first accelerators is underlined, but the later Accelerator is not.

2. Add a test for Objective & key results. Checks that an ampersand is handled correctly in the glossary link.

3. Add a test for AI/ML workflow. The slash should be removed from the heading ID rather than turned into a hyphen.

4. Add a test for auditable infrastructure. Checks that a glossary definition can contain bullets.

5. Add a test for overlapping glossary terms. Checks that a longer glossary term and the shorter term contained within it are matched as separate entries.  
Real-time inference and Inference, or Deployment plan and Deployment

6. Add a test comparing a one-line definition with a multi-line definition. Checks that the tooltip for the multi-line definition includes `[...]`.  
Use Explainability for the one-line definition and Benchmarking for the multi-line definition.

7. Add an **exclusion** test. Confirm that a glossary term inside an existing hyperlink stays a normal link instead of being turned into a glossary link.  
Link to my favourite: [ARX For Fun And Profit](https://youtu.be/QDia3e12czc)

8. Add an **exclusion** test for a glossary term in a table column header. No glossary links in column headers.

    | Challenge | Feature encoding should not be a glossary term here. | Neither should Container. |
    | --- | --- | --- |
    | Exciting content. | More exciting content. | spaCy can have a link. |

9. Add an **exclusion** test for reference footnotes. Checks that glossary terms in reference footnotes receive neither tooltips nor glossary links.  
Let's add two references here.[@gebruDatasheetsDatasets2021; @mitchellModelCardsModel2019]  
