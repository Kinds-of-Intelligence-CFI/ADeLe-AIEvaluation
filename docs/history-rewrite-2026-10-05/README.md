# History rewrite of 2026-10-05

**Why.** A July 2026 pilot committed decrypted HAL agent traces in plain text: TAU-bench airline and SWE-bench
Verified Mini trajectories, tool calls, checkpoint frames, prompts built from them and worksheets. HAL encrypts its
traces to keep them out of training corpora. Removing the files from the branch tips was not enough, because the
repository is public and the files stayed in history.

**What changed.**
- The 58 paths in `purged-paths.txt` were removed from every commit with `git filter-repo --invert-paths`: everything
  under `labs/hal-traces/` except the scripts and README, plus `labs/rubric-qa/r30/nset.csv`.
- Commits that became empty were kept, so the mapping is one to one.
- Six branches were force-pushed: `agentic`, `agentic-v2`, `benchmark-results`, `rubrics/v2-improved`,
  `rubrics/v2-lab-record` and `sensory`.
- `main` and `legacy` were not touched. `legacy` never contained the files, and rewriting it would only have
  stripped GitHub's commit signatures.

**Checks before the push.**
- No purged path remained anywhere in history.
- Every branch tip had exactly the same file tree as before; the tips had already been cleaned the same day.
- Every branch had the same number of commits.

**Commit hashes.** Every commit from the pilot (6307dd8, 2026-07-06) onwards has a new hash. Hashes cited in
RESULTS.md, pre-registrations, run manifests (`repo_commit`) and other notes written before this date are old hashes.
`commit-map.txt` maps each of them (`old new`, full 40-character hashes) to its rewritten commit. Commit dates,
authors, messages and file contents are unchanged, so every "committed before labelling" claim still holds; only the
hash changed.

**Not purged here.** Copies in forks, GitHub's stored refs for closed pull requests, cached commit views, and the Git
LFS objects of the removed CSV files. Purging those needs GitHub Support and the fork owners.

**If you have a clone.** Re-sync each branch you use to its rewritten version, for example
`git fetch origin && git checkout agentic-v2 && git reset --keep origin/agentic-v2`. Rebase any unpushed work onto
the new history; do not merge the old history back in.
