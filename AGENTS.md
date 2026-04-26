# Agent Guide: LiteLLM Models Customized

This document describes the build workflow and how to maintain this repository.

## Objective

Fetch LiteLLM's upstream `model_prices_and_context_window.json`, apply a regex-based blocklist to remove unwanted models, inject custom additions/overrides, and produce a compiled `model_prices_and_context_window.json` that LiteLLM can consume from a raw GitHub URL.

## Files You Will Edit

| File | Purpose |
|------|---------|
| `config/blocklist.json` | Regex patterns that exclude upstream models from the compiled output. |
| `config/additions.json` | Custom model entries to inject or override. Additions take precedence over upstream for the same model key. |
| `config/blocklist.schema.json` | JSON Schema for `blocklist.json`. Update if you change the blocklist config format. |
| `config/additions.schema.json` | JSON Schema for `additions.json`. Update if you add new fields to model entries. |
| `scripts/compile.py` | The compilation script. Modify if the workflow logic needs to change. |

**DO NOT manually edit** `model_prices_and_context_window.json` — it is a generated artifact.

## Workflow

### 1. Configure

Decide what to block and/or add.

#### Blocklist (`config/blocklist.json`)

Each entry in `patterns` is a Python regex evaluated against the model name (the JSON object key).

```json
{
    "patterns": [
        "amazon\\..*",
        ".*dall-e.*",
        "ai21\\..*",
        "anthropic\\.claude-instant.*"
    ]
}
```

- Patterns are matched with `re.search()` (partial match anywhere in the key).
- Invalid regex will cause the script to exit with an error.

#### Additions (`config/additions.json`)

Model entries follow the LiteLLM `sample_spec` format. Keys are model names; values are metadata objects.

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

- If a key already exists in upstream, the addition **overrides** it.
- If a key was blocked by the blocklist, the addition **re-injects** it.

### 2. Validate (Optional but Recommended)

Both configuration files are JSON Schema-validated at compile time, but you can pre-validate with any JSON Schema validator:

```bash
# If you have check-jsonschema installed:
check-jsonschema --schemafile config/blocklist.schema.json config/blocklist.json
check-jsonschema --schemafile config/additions.schema.json config/additions.json
```

### 3. Compile

Run the compilation script:

```bash
python scripts/compile.py
```

What happens:
1. Fetches the latest upstream JSON from GitHub (raw URL).
2. Validates `blocklist.json` against `blocklist.schema.json`.
3. Validates `additions.json` against `additions.schema.json`.
4. Applies the blocklist (drops matching upstream keys).
5. Merges additions (injects/overrides).
6. **Filters deprecated models** — by default, any model whose `deprecation_date` is today or earlier is removed. This applies to both upstream and custom additions.
7. Sorts output: `sample_spec` first, then alphabetical.
8. Writes `model_prices_and_context_window.json`.

To include deprecated models, pass `--ignore-deprecations`:

```bash
python scripts/compile.py --ignore-deprecations
```

### 4. Review

Always review the diff before committing:

```bash
git diff model_prices_and_context_window.json
```

Check for:
- Unexpected removals (overly broad blocklist regex)
- Missing expected additions
- Large upstream changes that may warrant adjusting the blocklist

### 5. Commit

Commit both the configuration changes and the compiled output together:

```bash
git add config/ model_prices_and_context_window.json
git commit -m "feat: block old Titan models, add my-org/custom-model"
```

The compiled JSON is part of the repo so LiteLLM can fetch it via raw GitHub URL, and git history serves as a changelog.

## Syncing / Rebasing on Upstream

Since customizations live in `config/`, updating upstream is trivial:

```bash
python scripts/compile.py
git diff   # review what upstream changed
git add model_prices_and_context_window.json
git commit -m "chore: sync upstream and recompile"
```

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Too many models removed | Overly broad regex (e.g., `claude.*` removes all Claude variants) | Narrow pattern to specific prefixes or suffixes |
| Addition not appearing | Key was not blocked and upstream doesn't have it either | Check key spelling; verify upstream key format |
| Addition appears but fields are wrong | Not matching LiteLLM spec | Reference `sample_spec` in compiled output or upstream source |
| Compile script fails schema validation | Malformed JSON or missing required fields | Run JSON lint; compare against schema |
| Deprecated model missing from output | Model's `deprecation_date` is today or earlier | Pass `--ignore-deprecations` to keep it |

## Dependencies

```bash
pip install -r scripts/requirements.txt
```

The only required dependency is `jsonschema` for validation. `requests` is not used; the script uses `urllib` from the standard library.

## Future: GitHub Actions

A `.github/workflows/sync-upstream.yml` can be added to:
- Run `compile.py` on a cron schedule (e.g., daily at 06:00 UTC)
- Auto-commit if the compiled output changed
- Optionally open a PR instead of direct commit

The repository structure is already designed to support this — no workflow changes needed.
