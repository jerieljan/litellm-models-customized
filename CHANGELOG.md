# Changelog

This document tracks how the compiled `model_prices_and_context_window.json` in this repository diverges from the [upstream LiteLLM source](https://github.com/BerriAI/litellm/blob/main/model_prices_and_context_window.json).

For the complete git history, see the [commit log](https://github.com/jerieljan/litellm-models-customized/commits/main).

---

## Current Customizations

### Blocked Model Patterns

These regex patterns in [`config/blocklist.json`](./config/blocklist.json) are applied to upstream model keys. Any match is removed from the compiled output.

| Pattern | Effect |
|---------|--------|
| `babbage-002` | Removes OpenAI `babbage-002` models |
| `davinci-002` | Removes OpenAI `davinci-002` models |
| `gpt-3([^0-9]\|$)` | Removes GPT-3.5 family models (e.g., `gpt-3.5-turbo`) |
| `gpt-4([^0-9]\|$)` | Removes GPT-4 family models (e.g., `gpt-4`, `gpt-4-turbo`) |
| `gemini-2` | Removes Google Gemini 2.x models |
| `fireworks_ai/.*` | Removes **all** Fireworks AI models from upstream |

### Automatic Deprecation Filter

The compilation script automatically drops any model, upstream or custom whose `deprecation_date` is today or earlier. This removed **347 deprecated models** on its introduction and counting and continues to apply on every recompile. 

### Fireworks AI Serverless Allowlist

Because the blocklist drops all upstream `fireworks_ai/.*` entries, serverless LLMs on Fireworks AI's model pages are re-injected via [`config/fireworks-serverless.json`](./config/fireworks-serverless.json).

These entries are crawled from the Fireworks AI gallery and use the short key format (`fireworks_ai/<model-id>`) instead of the long key format.

| Model Key | Source | Capabilities |
|-----------|--------|--------------|
| `fireworks_ai/deepseek-v4-pro` | [Pricing](https://fireworks.ai/models/fireworks/deepseek-v4-pro) | Function calling |
| `fireworks_ai/kimi-k2p6` | [Pricing](https://fireworks.ai/models/fireworks/kimi-k2p6) | Function calling, Vision |
| `fireworks_ai/minimax-m2p7` | [Pricing](https://fireworks.ai/models/fireworks/minimax-m2p7) | Function calling |
| `fireworks_ai/qwen3p6-plus` | [Pricing](https://fireworks.ai/models/fireworks/qwen3p6-plus) | Function calling, Vision |
| `fireworks_ai/glm-5p1` | [Pricing](https://fireworks.ai/models/fireworks/glm-5p1) | Function calling |
| `fireworks_ai/kimi-k2p5` | [Pricing](https://fireworks.ai/pricing) | Function calling, Response schema, Tool choice |
| `fireworks_ai/deepseek-v3p2` | [Pricing](https://fireworks.ai/models/fireworks/deepseek-v3p2) | Function calling, Reasoning, Response schema, Tool choice |
| `fireworks_ai/glm-5` | [Pricing](https://fireworks.ai/models/fireworks/glm-5) | Function calling |
| `fireworks_ai/deepseek-v3p1` | [Pricing](https://fireworks.ai/pricing) | Reasoning, Response schema, Tool choice |
| `fireworks_ai/gpt-oss-120b` | [Pricing](https://fireworks.ai/pricing) | Function calling, Reasoning, Response schema, Tool choice |
| `fireworks_ai/gpt-oss-20b` | [Pricing](https://fireworks.ai/pricing) | Function calling, Reasoning, Response schema, Tool choice |
| `fireworks_ai/llama-v3p3-70b-instruct` | [Pricing](https://fireworks.ai/models/fireworks/llama-v3p3-70b-instruct) | — |
| `fireworks_ai/minimax-m2p5` | [Pricing](https://fireworks.ai/models/fireworks/minimax-m2p5) | Function calling |
| `fireworks_ai/glm-4p7` | [Pricing](https://fireworks.ai/models/fireworks/glm-4p7) | Function calling, Reasoning, Response schema, Tool choice |
| `fireworks_ai/qwen3-vl-30b-a3b-thinking` | [Pricing](https://fireworks.ai/models/fireworks/qwen3-vl-30b-a3b-thinking) | — |
| `fireworks_ai/qwen3-vl-30b-a3b-instruct` | [Pricing](https://fireworks.ai/models/fireworks/qwen3-vl-30b-a3b-instruct) | — |
| `fireworks_ai/qwen3-8b` | [Pricing](https://fireworks.ai/models/fireworks/qwen3-8b) | Reasoning |

---

## History

### 2026-04-28

- **Added** `fireworks_ai/deepseek-v4-pro` to the serverless allowlist.  
  Commit: [`f67056a`](https://github.com/jerieljan/litellm-models-customized/commit/f67056a)

### 2026-04-27

- **Added** Fireworks AI serverless allowlist (`config/fireworks-serverless.json`).  
  Added 16 serverless models (see table above).  
  Commit: [`3964f0b`](https://github.com/jerieljan/litellm-models-customized/commit/3964f0b)
- **Blocked** all upstream `fireworks_ai/.*` models via `config/blocklist.json`.  
  This prevents the hundreds of non-serverless / on-demand Fireworks entries from appearing in the compiled output.  
  Commit: [`3964f0b`](https://github.com/jerieljan/litellm-models-customized/commit/3964f0b)

- **Removed** 347 deprecated models automatically.  
  The `compile.py` script now filters out any model whose `deprecation_date` has passed.  
  Commit: [`d16c4ab`](https://github.com/jerieljan/litellm-models-customized/commit/d16c4ab)

- **Blocked** Google Gemini 2.x and OpenAI GPT-3.5 models.  
  Patterns added: `gpt-3([^0-9]|$)`, `gemini-2`.  
  Commit: [`05ba014`](https://github.com/jerieljan/litellm-models-customized/commit/05ba014)

- **Blocked** OpenAI GPT-4, Babbage, and Davinci models.  
  Patterns added: `babbage-002`, `davinci-002`, `gpt-4([^0-9]|$)`.  
  Commit: [`b46573f`](https://github.com/jerieljan/litellm-models-customized/commit/b46573f)

- **Initial release** of the repository.  
  Added compilation script, JSON schemas, empty blocklist/additions configs, and the first upstream sync.  
  Commit: [`09165d1`](https://github.com/jerieljan/litellm-models-customized/commit/09165d1)
