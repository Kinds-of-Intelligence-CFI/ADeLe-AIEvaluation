"""Mass annotation runner: one command to annotate any (benchmarks x rubrics) grid with any judge.

    spec.toml --plan--> size and cost (no side effects)
              --pin---> run dir: manifest.json, cells.csv, ledger.csv; prompts in $ADELE_JUDGE_IO/<run>/
              submit / poll / fetch through a judge backend (subagent | anthropic-batch | openai-batch | litellm)
              collect --> labels.csv (one schema for every backend);  check --> coverage and protocol report

Modules: ``spec`` (load/validate), ``pin`` (freeze), ``ledger`` (progress), ``backends``, ``runner``
(submit/sync), ``collect`` (labels), ``check`` (audit), ``cli`` (``adele mass``). See
``experiments/benchmarks/mass-annotation/ARCHITECTURE.md``. ``adele.annotation.annotate`` is untouched.
"""
