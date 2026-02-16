# ADeLe-AIEvaluation

## 🚀 Unified AI Evaluation with Explanatory & Predictive Power

**ADeLe** (Artificial Demands and Levels) is a comprehensive toolkit for evaluating AI systems not just on *performance* (correctness), but on *capability matching*. It breaks down benchmarks into 18 cognitive demand dimensions (e.g., Reasoning, Knowledge, Memory) and assesses how well a model's capabilities align with these demands.

This package provides a unified, end-to-end pipeline:
1.  **Load** any benchmark (HuggingFace or local).
2.  **Annotate** its demand profile using LLM judges (via OpenAI Batch API).
3.  **Evaluate** models on the benchmark (via Inspect AI).
4.  **Profile** the results (Demand-Ability matching, Predictive Power).

---

## 📦 Installation

```bash
git clone https://github.com/your-org/ADeLe-AIEvaluation.git
cd ADeLe-AIEvaluation
pip install -e .
```

---

## 🔑 API Keys

Set the API key(s) for whichever provider(s) you plan to use:

```bash
export OPENAI_API_KEY="sk-..."          # OpenAI (GPT, o-series)
export GOOGLE_API_KEY="AI..."           # Google (Gemini)
export ANTHROPIC_API_KEY="sk-ant-..."   # Anthropic (Claude)
export OPENROUTER_API_KEY="sk-or-..."     # OpenRouter (DeepSeek, Llama 3, etc.)
```

> **Two annotation backends:**
> ADeLe automatically picks the best backend based on your model:
> - **Batch** (OpenAI models only) — uses the [OpenAI Batch API](https://platform.openai.com/docs/guides/batch) for 50% cost reduction and higher rate limits. Auto-selected when using `gpt-*` or `o1`/`o3` models.
> - **Direct** (any model) — calls the model via [litellm](https://github.com/BerriAI/litellm), which supports OpenAI, Gemini, Claude, and 100+ other providers. Auto-selected for non-OpenAI models. You can force either backend with `--backend batch` or `--backend direct`.

---

## 🛠️ Usage

### 1. Annotate a Benchmark (Demand Profile)

The `annotate` command scores demand levels for each instance using an LLM judge.

```bash
# Using OpenAI (auto-selects Batch API for cost savings)
adele annotate mmlu-pro --model gpt-4o --output-dir ./results/mmlu

# Using Gemini (auto-selects direct mode via litellm)
adele annotate mmlu-pro --model gemini/gemini-2.0-flash --output-dir ./results/mmlu

# Using Claude
adele annotate mmlu-pro --model claude-sonnet-4-20250514 --output-dir ./results/mmlu

# Force direct mode even for OpenAI (useful for testing)
adele annotate mmlu-pro --model gpt-4o --backend direct --max-samples 5
```

**Output:** `annotations_wide.csv` — one row per instance, one column per demand (AS, CEc, CL, ..., VO), values 0–5.

### 2. Evaluate a Model

The `evaluate` command wraps [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) to run your model on the benchmark and record per-instance correctness.

```bash
adele evaluate openai/gpt-4o mmlu-pro --output-dir ./results/mmlu
```

**Output:** `evaluation_results.csv` with `custom_id`, `model_answer`, and `correct` (0/1).

### 3. Generate Profiles (Visualization)

```bash
adele profile ./results/mmlu/annotations_wide.csv --title "MMLU-Pro Demands"
```

---

## 🤖 Evaluating Model Families

ADeLe supports **any model** that Inspect AI supports. Here are the three major families:

### OpenAI (GPT, o-series)

```bash
export OPENAI_API_KEY="sk-..."

adele evaluate openai/gpt-4o mmlu-pro
adele evaluate openai/gpt-4o-mini mmlu-pro
adele evaluate openai/o1 mmlu-pro
adele evaluate openai/o3-mini mmlu-pro
```

### Google Gemini

```bash
export GOOGLE_API_KEY="AI..."

adele evaluate google/gemini-2.0-flash mmlu-pro
adele evaluate google/gemini-2.5-pro-preview-05-06 mmlu-pro
```

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

adele evaluate anthropic/claude-sonnet-4-20250514 mmlu-pro
adele evaluate anthropic/claude-3-5-haiku-20241022 mmlu-pro
```

### OpenRouter (DeepSeek, Llama 3, etc.)

```bash
export OPENROUTER_API_KEY="sk-or-..."

# Use the 'openrouter/' prefix
adele evaluate openrouter/deepseek/deepseek-r1 mmlu-pro
adele evaluate openrouter/meta-llama/llama-3.1-405b-instruct mmlu-pro
```

### Python API (all providers)

```python
from adele.data import load_benchmark
from adele.evaluation import evaluate_model

data = load_benchmark("mmlu-pro", max_samples=100)

# Evaluate any model — just change the model string:
gpt_results   = evaluate_model("openai/gpt-4o", data, task_type="multiple-choice")
gem_results   = evaluate_model("google/gemini-2.0-flash", data, task_type="multiple-choice")
claude_results = evaluate_model("anthropic/claude-sonnet-4-20250514", data, task_type="multiple-choice")
```

---

## 📊 Custom HuggingFace Benchmarks

HuggingFace datasets do **not** follow a standard structure — column names, splits, and prompt formats vary widely. ADeLe handles this with **column mapping**.

### Pre-registered benchmarks (21 built-in)

Run `adele benchmarks list` to see all 21 pre-configured benchmarks. These "just work" because we've already defined the correct column mappings:

```bash
adele annotate mmlu-pro       # knows to use column "question", split "test"
adele annotate gsm8k          # knows to use column "question", split "test"
```

### Arbitrary HuggingFace datasets

For datasets **not** in the registry, you must tell ADeLe which columns to use, because datasets differ:

| Dataset | Question column | Answer column | Split |
|---------|----------------|---------------|-------|
| `openai/gsm8k` | `question` | `answer` | `test` |
| `TIGER-Lab/MMLU-Pro` | `question` | `answer` | `test` |
| `lighteval/MATH` | `problem` | `solution` | `test` |
| `cais/mmlu` | `question` | `answer` | `test` |

```python
from adele.data import load_benchmark

# If the dataset has standard "question"/"answer" columns, this may work as-is:
data = load_benchmark("some-org/some-dataset")

# If the columns have non-standard names, specify mappings:
data = load_benchmark(
    "some-org/custom-benchmark",
    split="validation",              # which split to load
    prompt_column="input_text",      # which column contains the task text
    target_column="gold_label",      # which column contains the correct answer
    id_column="uid",                 # which column to use as instance ID (optional)
    prompt_template="Question: {input_text}\nAnswer:",  # wrap into a prompt format
    max_samples=500,                 # limit for testing
)
```

The `prompt_template` argument is useful when the raw column text needs formatting. Use `{column_name}` placeholders — they will be filled from the dataset row.

Once loaded, annotate directly:

```python
from adele.annotation import annotate

# Annotate all 18 demand dimensions using Gemini as the judge
results = annotate(data=data, model="gemini/gemini-2.0-flash", output_dir="./results")

# Or annotate only specific dimensions
results = annotate(data=data, demands=["AS", "MCr", "KNa"], model="gpt-4o")
```

Or from the CLI, pass the HuggingFace ID directly with column mappings:

```bash
adele annotate "lighteval/MATH" --split test --model gpt-4o -o ./results/math
```

### Local files (CSV, JSONL, Parquet)

```python
from adele.data.loader import load_from_file

data = load_from_file("./my_data.csv", prompt_column="question", target_column="answer")
```

---

## ➕ Adding Custom Demand Dimensions

To add a new rubric (demand dimension), **no code changes are needed**. Just create a `.txt` file:

```
# Emotional Intelligence
This criterion assesses the level of emotional intelligence required...

Level 0: No emotional understanding is needed.
Examples: "What is 2+2?"...

Level 1: Basic emotional recognition is needed.
Examples: "Is this person happy?"...

...

Level 5: Complex multi-agent emotional dynamics with hidden motivations.
Examples: ...
```

Then either:
- **Bundle it**: place in `src/adele/rubrics/data/EQ.txt` and reinstall.
- **Use a custom folder**: `adele annotate mmlu-pro --rubrics ./my_rubrics/`

The file name (without `.txt`) becomes the dimension acronym. The `# Header` line becomes the full name. Levels 0–5 and Example sections are required for validation.

---

## 🧠 Core Concepts

### 1. Demand Profile (The "Problem Space")
A **Demand Profile** visualizes what a benchmark *asks* of a model. It scores 18 dimensions (0-5 scale):
- **Reasoning**: `AS` (Attention), `CEc` (Causal Comprehension), `QLq` (Quant. Reasoning)...
- **Knowledge**: `KNa` (Academic), `KNf` (Factual), `KNs` (Specialized)...
- **Metacognition**: `MCr` (Reflection), `MCu` (Uncertainty)...

### 2. Ability Profile (The "Solution Space")
An **Ability Profile** visualizes what a model *is capable of*. It is computed by fitting an **`AbilityModel`** on (demand_profile, correctness) data.

The default implementation (`LogisticAbilityModel`) fits an independent logistic regression per demand dimension. Each instance's success probability depends only on the demand level in the dimension being scored (the "max-demand" assumption).

You can implement custom ability models by subclassing `AbilityModel`:

```python
from adele.analysis import AbilityModel, compute_ability_scores

class CustomAbilityModel(AbilityModel):
    def fit(self, demand_profiles, correctness, demands, **kw):
        # demand_profiles: DataFrame (N instances × D demands, values 0–5)
        # correctness: 1-D array of 0/1
        # Implement your model here
        ...
    @property
    def ability_scores(self) -> dict:
        # Return {demand: ability_score} from your model
        ...

scores = compute_ability_scores(model_data, annotations, model_class=CustomAbilityModel)
```


### 3. Predictive Power
We train a **Random Forest** classifier to predict *model correctness* solely from the *demand levels* of the task.
- High accuracy → The demand profile explains the model's failure modes.
- Feature Importance → Identifies which specific demands cause the model to fail.

---

## 📂 Project Structure

- **`adele.data`** — Loads benchmarks from HuggingFace (`load_benchmark`) and standardizes their varying column names into a uniform schema: `prompt` (question text), `target` (correct answer), and `custom_id` (unique instance identifier). Ships with 21 pre-configured benchmarks (e.g. MMLU-Pro, GSM8K, ARC) so their column mappings don't need to be specified manually.
- **`adele.annotation`** — Multi-provider annotation with dual backends.
    - `prompts.py`: Builds Chain-of-Thought prompts using 18 bundled rubrics.
    - `annotator.py`: Orchestrates annotation via two backends:
        - **Batch** (OpenAI only): Uses the OpenAI Batch API for 50% cost savings.
        - **Direct** (any provider): Parallel calls via litellm (OpenAI, Gemini, Claude, etc.).
    - `parsing.py`: Extracts demand scores (0-5) from LLM judge responses.
- **`adele.evaluation`** — Wraps Inspect AI to run models and extract per-instance correctness.
- **`adele.analysis`** — Profiling and visualization.
    - `demand.py`: Generates demand profile polar heatmaps (matplotlib).
    - `ability.py`: Computes ability scores (AUC) and Spearman correlations.
    - `prediction.py`: Random Forest analysis of predictive power.