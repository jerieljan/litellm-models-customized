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

The compilation script automatically drops any model, upstream or custom, whose `deprecation_date` is today or earlier. This removed **347 deprecated models** on its introduction and continues to apply on every recompile.

### Fireworks AI Serverless Allowlist

Because the blocklist drops all upstream `fireworks_ai/.*` entries, serverless LLMs on Fireworks AI's model pages are re-injected via [`config/fireworks-serverless.json`](./config/fireworks-serverless.json).

These entries are crawled from the Fireworks AI gallery and use the short key format (`fireworks_ai/<model-id>`) instead of the long key format.

| Model Key | Source | Capabilities |
|-----------|--------|--------------|
| `fireworks_ai/deepseek-v4-flash` | [Pricing](https://fireworks.ai/models/fireworks/deepseek-v4-flash) | — |
| `fireworks_ai/deepseek-v4-pro` | [Pricing](https://fireworks.ai/models/fireworks/deepseek-v4-pro) | — |
| `fireworks_ai/glm-5p1` | [Pricing](https://fireworks.ai/models/fireworks/glm-5p1) | Reasoning |
| `fireworks_ai/gpt-oss-120b` | [Pricing](https://fireworks.ai/pricing) | Function calling, Reasoning, Response schema, Tool choice |
| `fireworks_ai/gpt-oss-20b` | [Pricing](https://fireworks.ai/pricing) | Function calling, Reasoning, Response schema, Tool choice |
| `fireworks_ai/kimi-k2p5` | [Pricing](https://fireworks.ai/pricing) | Function calling, Response schema, Tool choice |
| `fireworks_ai/kimi-k2p6` | [Pricing](https://fireworks.ai/models/fireworks/kimi-k2p6) | Vision |
| `fireworks_ai/kimi-k2p7-code` | [Pricing](https://fireworks.ai/models/fireworks/kimi-k2p7-code) | Vision |
| `fireworks_ai/minimax-m2p5` | [Pricing](https://fireworks.ai/models/fireworks/minimax-m2p5) | — |
| `fireworks_ai/minimax-m2p7` | [Pricing](https://fireworks.ai/models/fireworks/minimax-m2p7) | — |
| `fireworks_ai/minimax-m3` | [Pricing](https://fireworks.ai/models/fireworks/minimax-m3) | Vision |
| `fireworks_ai/nemotron-3-ultra-nvfp4` | [Pricing](https://fireworks.ai/models/fireworks/nemotron-3-ultra-nvfp4) | — |
| `fireworks_ai/qwen3-embedding-8b` | [Pricing](https://fireworks.ai/models/fireworks/qwen3-embedding-8b) | — |
| `fireworks_ai/qwen3-reranker-8b` | [Pricing](https://fireworks.ai/models/fireworks/qwen3-reranker-8b) | Rerank |
| `fireworks_ai/qwen3p6-plus` | [Pricing](https://fireworks.ai/models/fireworks/qwen3p6-plus) | Vision |
| `fireworks_ai/qwen3p7-plus` | [Pricing](https://fireworks.ai/models/fireworks/qwen3p7-plus) | Vision |

---

## History

### 2026-06-16

- **Added** `fireworks_ai/kimi-k2p7-code`, `fireworks_ai/minimax-m3`, `fireworks_ai/qwen3p7-plus`, and `fireworks_ai/nemotron-3-ultra-nvfp4` to the serverless allowlist.  
  Commit: [`27d71eb`](https://github.com/jerieljan/litellm-models-customized/commit/27d71eb)

### 2026-06-11

- **Synced upstream** and recompiled.  
  Added new providers: `snowflake` (Claude 3.7/4 Sonnet/Opus, GPT-5, Arctic embed, Llama 4 Maverick), `fal_ai` (nano-banana), `soniox` (stt-async-v4), `you_com` (search), `apiserpent` (deep_search, search), `inception` (mercury-2, mercury-edit-2), `bedrock_mantle` (gpt-5.4, gpt-5.5).  
  Added new models: `anthropic.claude-fable-5` (and `bedrock`, `vertex_ai`, regional, and `claude-fable-5` aliases), `azure_ai/kimi-k2.6`, `mistral/ministral-8b-latest`, `vertex_ai/google/gemma-4-26b-a4b-it-maas`, `minimax/MiniMax-M3`.  
  Dropped upstream: legacy `moonshot/*` Kimi preview/8k/32k/128k variants, `xai/grok-3`, `xai/grok-4-0709`, `xai/grok-4-fast*`, `xai/grok-4-1-fast*`, `xai/grok-code-fast-1*`, `eu.anthropic.claude-opus-4-8`.  
  Commit: [`09e17fd`](https://github.com/jerieljan/litellm-models-customized/commit/09e17fd)

### 2026-05-29

- **Synced upstream** and recompiled.  
  Added `anthropic.claude-opus-4-8` and all regional/`bedrock`/`vertex_ai`/`azure_ai` aliases, `gemini-3.1-flash-lite` (and `vertex_ai`/`openrouter` aliases), `mistral/ministral-8b-2512`, and OCI-hosted Cohere / Llama / OpenAI / xAI entries.  
  Added `openrouter/xiaomi/mimo-v2.5(-pro)`, `reducto/parse-v3`, `reducto/parse-legacy`.  
  Updated `fireworks_ai/glm-5p1` with cache read, output, max tokens, and capability flags.  
  Dropped upstream: `gemini-3.1-flash-lite-preview`, `gemini-3.1-flash-live-preview`, `oci/xai.grok-3`.  
  Commit: [`36a8360`](https://github.com/jerieljan/litellm-models-customized/commit/36a8360)

### 2026-05-20

- **Refactored** the serverless allowlist.  
  Simplified most entries to `mode`/`source`/`input_cost_per_token` only (and `supports_vision` where applicable); dropped redundant `output_cost_per_token`/`cache_read_input_token_cost`/`max_tokens`/non-vision capability fields to align with how the Fireworks serverless UI surfaces them.  
  **Removed** from the allowlist: `fireworks_ai/deepseek-v3p1`, `fireworks_ai/deepseek-v3p2`, `fireworks_ai/glm-4p7`, `fireworks_ai/glm-5`, `fireworks_ai/llama-v3p3-70b-instruct`, `fireworks_ai/qwen3-8b`, `fireworks_ai/qwen3-vl-30b-a3b-instruct`, `fireworks_ai/qwen3-vl-30b-a3b-thinking` (no longer serverless).  
  **Added** `fireworks_ai/deepseek-v4-flash`, `fireworks_ai/qwen3-reranker-8b` (rerank mode), and `fireworks_ai/qwen3-embedding-8b`.  
- **Synced upstream** and recompiled.  
  Added `azure_ai/gpt-5.4` family (5.4 / 5.4-mini / 5.4-nano / 5.4-pro and dated variants), `gemini-3.5-flash` (and `vertex_ai` alias), `gpt-realtime-2`, `jp.anthropic.claude-sonnet-4-6`.  
  Removed `claude-opus-4-20250514` and `claude-sonnet-4-20250514`.  
  Commit: [`10b4682`](https://github.com/jerieljan/litellm-models-customized/commit/10b4682)

### 2026-05-12

- **Synced upstream** and recompiled.  
  Added `xai/grok-4.3`, `xai/grok-4.3-latest`, `sambanova/MiniMax-M2.7`, `openrouter/qwen/qwen3.6-plus`.  
  Removed `vertex_ai/claude-3-7-sonnet@20250219`.  
  Commit: [`4d32d55`](https://github.com/jerieljan/litellm-models-customized/commit/4d32d55)

### 2026-05-06

- **Synced upstream** and recompiled.  
  Added `gpt-image-2` (and `azure` alias + dated variant), Crusoe provider entries (`Qwen3-235B-A22B-Instruct-2507`, `DeepSeek-R1-0528`, `DeepSeek-V3-0324`, `gemma-3-12b-it`, `Llama-3.3-70B-Instruct`, `Kimi-K2-Thinking`, `gpt-oss-120b`), and `vertex_ai/xai/grok-4.1-fast-{reasoning,non-reasoning}` and `grok-4.20-{reasoning,non-reasoning}`.  
  Removed `azure/text-embedding-3-small` and `claude-3-opus-20240229`.  
  Commit: [`dd2e09e`](https://github.com/jerieljan/litellm-models-customized/commit/dd2e09e)

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
