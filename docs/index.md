---
hide:
  - toc
---

# Cross-Cutting Section

## AI Ethics

### Fairness, Non-Discrimination, and Bias

Fairness concerns whether AI systems perform equitably across relevant groups, populations, contexts, or use cases. Bias can enter at multiple stages, including data collection, labeling, preprocessing, model selection, evaluation, deployment, and interpretation. RCD decisions around data, software, platforms, and infrastructure can introduce, amplify, or help mitigate bias at the data, model, and evaluation stages. RCD facilitators can help researchers select and run tooling to detect disparate performance across subgroups and ensure evaluation environments are representative, documented, and reproducible. See the Benchmarking and Results & Reporting sections for fairness, interpretability, and reporting tooling.

### Accountability and Responsibility

Fairness and the other goals in this section remain aspirational unless a project team can show how a result was produced, who made key decisions, and who is responsible for addressing errors, harms, or unexpected outcomes. From an RCD perspective, accountability is supported through auditability, provenance, and documentation: audit logs of experiment configurations, datasets, and results; version control for data, code, and model artifacts; documented approval pathways; and structured reporting such as model cards 3. These practices allow a team to trace biased, anomalous, or non-reproducible outcomes back to their source and assign clear ownership for remediation. See the Results & Reporting section for reporting and documentation practices.

### Transparency and Explainability

Transparency concerns whether the assumptions, data sources, methods, limitations, and decision pathways of an AI system are documented and accessible to appropriate stakeholders. Explainability concerns whether model behavior and outputs can be interpreted in ways that are meaningful for the research context. RCD facilitators can support transparency and explainability by encouraging version-controlled workflows, documented software environments, data and model provenance, experiment tracking, reproducible pipelines, and structured reporting artifacts such as model cards 3 and datasheets 4. These practices help researchers explain not only what a model produced, but how the result was generated.

### Test Cases

1. Add a test for Fairness versus fairness.

2. Add a test for audit log verus audit logs.

3. Add a test for QC & optimization and QC & Optimization. Ampersands are tricky for links.

4. Add a failure test where the tooltip defintion does not match the glossary definition:  
RCD (correct) versus RCDs (incorrect).

5. Add RCDs and RCDs to test the handling of unmatched term logging. You will only see one error warning, even though there are three failures. The build will still be successful.
