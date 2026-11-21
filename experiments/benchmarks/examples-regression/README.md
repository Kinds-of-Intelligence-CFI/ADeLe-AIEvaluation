# examples-regression — do the reviewed examples change other labels?

Owner: Pablo. Old against new rubric texts (`d4ec2ec~1` against `d4ec2ec`) on the lab battery and 60 real tasks, for
PLp, PLe, PLs, MSm and MSc. Judge: Opus 5.5 low. Design and rule: `PREREGISTRATION.md`. Runs `exreg-1`, `exreg-2`.

    python experiments/benchmarks/examples-regression/make_prompts.py
    python experiments/benchmarks/examples-regression/writers.py --run exreg-1 --transcripts <session>/subagents
    python experiments/benchmarks/examples-regression/collect.py --run exreg-1
    python experiments/benchmarks/examples-regression/analysis/analyse.py
