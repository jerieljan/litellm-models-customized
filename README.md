# LiteLLM Models Customized

A curated, customizable version of [LiteLLM's `model_prices_and_context_window.json`](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json).

## What This Is

This repository fetches the upstream LiteLLM model pricing & context window database, applies your blocklist filters and custom additions, and produces a clean `model_prices_and_context_window.json` that LiteLLM itself can consume from a custom URL.

## Why Use This?

- **Remove unwanted models**: Filter out old, deprecated, or irrelevant providers via regex blocklist.
- **Add custom entries**: Inject your own private or fine-tuned models with full metadata.
- **Stay synced with upstream**: Re-run the compile script anytime to "rebase" on the latest upstream changes.
- **Git history as changelog**: The compiled output is committed, so diffs tell you exactly what changed.

## Repository Structure

```
.
├── scripts/
│   ├── compile.py              # Main compilation script
│   └── requirements.txt        # Python dependencies
├── config/
│   ├── blocklist.json          # Regex patterns to exclude models
│   ├── blocklist.schema.json   # JSON Schema for blocklist.json
│   ├── additions.json          # Custom model entries to inject/override
│   └── additions.schema.json   # JSON Schema for additions.json
├── model_prices_and_context_window.json   # COMPILED OUTPUT (committed)
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
uv pip install -r scripts/requirements.txt
```

Or with `pip`:

```bash
pip install -r scripts/requirements.txt
```

### 2. Configure

Edit `config/blocklist.json` to remove models:

```json
{
    "patterns": [
        "amazon\\..*",
        ".*dall-e.*",
        "ai21\\..*"
    ]
}
```

Edit `config/additions.json` to add or override models:

```json
{
    "my-org/custom-model": {
        "litellm_provider": "openai",
        "mode": "chat",
        "max_tokens": 128000,
        "input_cost_per_token": 1e-05,
        "output_cost_per_token": 3e-05,
        "supports_function_calling": true
    }
}
```

### 3. Compile

```bash
python scripts/compile.py
```

This will:
1. Fetch the latest upstream JSON from LiteLLM
2. Apply your blocklist
3. Merge your additions (additions override upstream for the same key)
4. Sort deterministically (`sample_spec` first, then alphabetical)
5. Write `model_prices_and_context_window.json`

### 4. Commit

```bash
git add model_prices_and_context_window.json config/
git commit -m "chore: compile with updated blocklist/additions"
```

## Integration with LiteLLM

Point LiteLLM to the raw URL of your compiled file:

```yaml
model_list:
  - model_name: "*"
    litellm_params:
      model: "*"
      custom_prompt_template: "https://raw.githubusercontent.com/YOUR_ORG/litellm-models-table-shortlist/main/model_prices_and_context_window.json"
```

Or set the environment variable:

```bash
export LITELLM_MODEL_COST_MAP_URL="https://raw.githubusercontent.com/YOUR_ORG/litellm-models-table-shortlist/main/model_prices_and_context_window.json"
```

## Syncing / Rebasing on Upstream

Since your customizations live in `config/`, updating is trivial:

```bash
python scripts/compile.py
git diff   # review what changed
git add model_prices_and_context_window.json
git commit -m "chore: sync upstream and recompile"
```

## JSON Schema Validation

Both `blocklist.json` and `additions.json` are validated against their respective JSON Schemas at compile time. The schemas are located in `config/*.schema.json` and will help your editor provide autocompletion and validation.

## Future: GitHub Actions

A `.github/workflows/sync-upstream.yml` can be added to auto-compile on a schedule (e.g., daily) and commit changes automatically.
