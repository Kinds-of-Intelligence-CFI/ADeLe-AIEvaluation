# HAL trace pilot — data removed

The trace data of this pilot (decrypted HAL trajectories, tool calls, checkpoint frames, prompts built from them,
judge answers and worksheets) was removed on 2026-10-05. HAL encrypts its traces to limit contamination, and they
must not sit in plain text in a public repository. Only the scripts remain. To rebuild the data, download the traces
from the agent-evals/hal_traces dataset on Hugging Face and decrypt them locally (see
experiments/benchmarks/dtg-data/fetch_hal_tau.py on agentic-v2), keeping them in the gitignored data/ folder.
