1) System requirements

All dependencies & OS: Python 3.11; packages required are all described each individual ipynb. It shall work for any operating system that admits a python interpreter.

Versions tested: macOS 14, Ubuntu 22.04, and Windows 11; Python 3.11.

2) Installation guide

Instructions: Clone repo; use the corresponding ipynb files either for generating demand profiles, ability profiles, or calculating predictive power.

Typical install time: Not applicable (scripts, no installer). Dependency install typically <5 minutes on a standard laptop as of 2025.

3) One quick demo

Example: Go to the folder "generating_scc" and run "scc_and_ability_profiles.ipynb"  to obtain ability profiles (Figure 7 and 8 in https://arxiv.org/pdf/2503.06378).

Expected outputs: PDF figures in outputs or tables of numbers

Expected runtime: ~1-5 minutes on a typical laptop CPU as of 2025, depending which ipynb file is run. The only exception is the DeLeAn toolkit for getting demand annotations, which depends on the speed of the source of the LLM-judge used (e.g. using Batch API could take a few hours).

4) Instructions for use

How to run on your data & Reproduction instructions: See the main README file in the repo.


