# General Scales Unlock AI Evaluation with Explanatory and Predictive Power

This repository is part of a [collaborative platform](https://kinds-of-intelligence-cfi.github.io/ADELE/) initiated by researchers at the [Leverhulme Centre for the Future of Intelligence](https://www.lcfi.ac.uk) (University of Cambridge) and the [Center for Information Technology Policy](https://citp.princeton.edu) (Princeton University), aimed at continuously supporting and extending ADeLe (Annotated-Demand-Levels) v1.0, a novel methodology for AI Evaluation that unlocks both explanatory and predictive power introduced in the paper [“General Scales Unlock AI Evaluation with Explanatory and Predictive Power”](https://arxiv.org/abs/2503.06378).

In a nutshell, ADeLe annotate the levels of cognitive capabilities and knowledge that a problem requires and evaluates a model’s capabilities comprehensively and robustly by considering these levels. More concretely, by comparing what a task requires with what a model can do, ADeLe generates ability profiles that not only can reliably predict model performance (at instance-level) but also explains why a model is likely to succeed or fail—linking outcomes to specific strengths or limitations of the model with respect to what levels of demands a problem requires. The paper's [takeaways are on X](https://x.com/lexin_zhou/status/1899271596264825308) and a more accessible [Microsoft Research Blog](https://www.microsoft.com/en-us/research/blog/predicting-and-explaining-ai-model-performance-a-new-approach-to-evaluation/) summarizes it for the general audience.

This repository offers the following elements:

- ./rubrics contains the list of rubrics (in txt format) used in ADeLe v1.0, described in section 10 of the [original paper](https://arxiv.org/abs/2503.06378).

- ./generating_scc has the script to reproduce the computation of both subjective characteristics curves (SCCs) and ability scores.

- ADeLe.txt links the ADELE v1.0 battery.

- DeLeAn.txt links an official toolkit for reproducing and extending the DeLeAn pipeline (i.e. annotate demand levels for task instances). It includes a high-level Python API and a comprehensive CLI interface for managing large-scale annotation jobs using the OpenAI Batch API, along with utilities for customizing, reusing and potentially expanding demand-level rubrics. Whether you're contributing to ADeLe or building your own evaluation workflows, this package offers the core infrastructure to make demand-level annotations accessible and reproducible.
