#!/usr/bin/env python3
"""
Crawl Fireworks AI serverless LLMs and produce config/fireworks-serverless.json.

Requirements:
- Chrome with remote debugging enabled on port 9222
- agent-browser CLI available in PATH

This script:
1. Opens the Fireworks AI model library filtered to LLM + Serverless.
2. Extracts the list of serverless model cards.
3. Visits each model detail page to collect exact metadata.
4. Fetches the upstream LiteLLM model_prices_and_context_window.json.
5. For each crawled model:
   - If it exists upstream (short or long format), copies that metadata.
   - Otherwise, builds metadata from the crawl data.
6. Writes config/fireworks-serverless.json with short-format keys
   (fireworks_ai/<model-id>).

Usage:
    python3 scripts/crawl-fireworks.py

When Fireworks updates their page layout, update the JavaScript selectors
in this script accordingly.
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = REPO_ROOT / "config"
OUTPUT_PATH = CONFIG_DIR / "fireworks-serverless.json"

UPSTREAM_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)

CDP_PORT = 9222
LISTING_URL = "https://app.fireworks.ai/models?filter=LLM&serverless=true"


def verify_chrome_debugging() -> None:
    """Check that a Chrome CDP session is available on CDP_PORT."""
    try:
        with urllib.request.urlopen(
            f"http://localhost:{CDP_PORT}/json/version", timeout=2
        ) as response:
            if response.status == 200:
                return
    except urllib.error.URLError:
        pass
    except Exception:
        pass
    print(
        f"Error: Chrome remote debugging not detected on port {CDP_PORT}.\n"
        "Please start Chrome with --remote-debugging-port=9222 before running this script.",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Agent-browser helpers
# ---------------------------------------------------------------------------


def _agent_browser(*args: str, timeout: int = 60) -> str:
    """Run an agent-browser command and return stdout."""
    cmd = ["agent-browser", "--cdp", str(CDP_PORT), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"agent-browser error: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"agent-browser failed: {result.stderr}")
    return result.stdout


def open_page(url: str) -> None:
    _agent_browser("open", url)
    _agent_browser("wait", "--load", "networkidle")


def eval_js(js_code: str, timeout: int = 60):
    """Evaluate JS via agent-browser -b (base64) and return parsed data."""
    b64 = base64.b64encode(js_code.encode()).decode()
    cmd = ["agent-browser", "--cdp", str(CDP_PORT), "eval", "-b", b64]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        print(f"eval error: {result.stderr}", file=sys.stderr)
        raise RuntimeError(f"JS eval failed: {result.stderr}")
    raw = result.stdout.strip()
    # agent-browser eval returns JSON-encoded strings.
    # For JSON.stringify(x) the output is a JSON string like '[...]',
    # so we may need two json.loads calls.
    try:
        first = json.loads(raw)
        if isinstance(first, str):
            return json.loads(first)
        return first
    except json.JSONDecodeError:
        return raw


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def parse_price(text: str) -> float | None:
    """Convert a price string like '$0.95/M' to cost-per-token."""
    m = re.search(r"\$([0-9.]+)/M", text)
    if not m:
        return None
    return float(m.group(1)) / 1_000_000


def parse_context(text: str) -> int | None:
    """Extract context length from text like '262k Context' or '40k Context'."""
    m = re.search(r"([0-9.]+)k\s+Context", text, re.IGNORECASE)
    if not m:
        return None
    val = float(m.group(1))
    # Most upstream values are powers of two (e.g. 262144 = 256*1024).
    # For round numbers like 262k we use the nearest common power-of-two
    # when it makes sense, otherwise just multiply by 1024.
    if val == 262:
        return 262144
    if val == 131:
        return 131072
    if val == 196:
        return 200704  # 196 * 1024
    if val == 202:
        return 202800  # matches upstream glm-4p7
    if val == 163:
        return 163840  # matches upstream deepseek-v3p2
    if val == 40:
        return 40960
    return int(val * 1024)


def parse_capabilities(text: str) -> dict[str, bool]:
    """Parse Supported Functionality section into boolean flags.

    Fireworks detail pages concatenate labels without newlines, e.g.:
    "...Function CallingSupportedEmbeddingsNot supported..."
    We use regex to find "LabelSupported" vs "LabelNot supported".
    """
    caps = {}
    lower = text.lower().replace(" ", "").replace("\n", "")

    def _supported(label: str) -> bool:
        # Look for "labelsupported" or "labelnotsupported"
        if f"{label}notsupported" in lower:
            return False
        if f"{label}supported" in lower:
            return True
        return False

    caps["supports_function_calling"] = _supported("functioncalling")
    caps["supports_vision"] = _supported("imageinput")
    caps["supports_tool_choice"] = _supported("toolchoice")
    caps["supports_reasoning"] = _supported("reasoning")
    return {k: v for k, v in caps.items() if v}


# ---------------------------------------------------------------------------
# Crawl workflow
# ---------------------------------------------------------------------------


def crawl_listing() -> list[dict]:
    """Return list of {id, name, href, raw_text} from the serverless listing."""
    print("Opening serverless LLM listing...")
    open_page(LISTING_URL)

    js = (
        "JSON.stringify("
        "Array.from(document.querySelectorAll('a[href*=\"/models/fireworks/\"]'))"
        ".filter(a => a.innerText.includes('/M') && a.innerText.includes('Serverless'))"
        ".map(a => {"
        "  const href = a.href;"
        "  const id = href.split('/models/fireworks/')[1].split('?')[0];"
        "  const text = a.innerText.trim();"
        "  const name = text.split(String.fromCharCode(10))[0] || text;"
        "  return {id, name, href, text};"
        "})"
        ".filter((m, i, arr) => arr.findIndex(x => x.id === m.id) === i)"
        ")"
    )
    models = eval_js(js)
    print(f"Found {len(models)} unique serverless models.")
    return models


def crawl_model_detail(model_id: str, href: str) -> dict:
    """Open a model detail page and extract structured metadata."""
    print(f"  Crawling detail page for {model_id} ...")
    open_page(href)

    js = (
        "JSON.stringify({"
        "  modelId: window.location.pathname.split('/').pop(),"
        "  title: document.title,"
        "  metadata: (() => {"
        "    const h = Array.from(document.querySelectorAll('h3')).find(el => el.innerText.includes('Metadata'));"
        "    return h ? h.parentElement.innerText : '';"
        "  })(),"
        "  specification: (() => {"
        "    const h = Array.from(document.querySelectorAll('h3')).find(el => el.innerText.includes('Specification'));"
        "    return h ? h.parentElement.innerText : '';"
        "  })(),"
        "  functionality: (() => {"
        "    const h = Array.from(document.querySelectorAll('h3')).find(el => el.innerText.includes('Supported Functionality'));"
        "    return h ? h.parentElement.innerText : '';"
        "  })()"
        "})"
    )
    return eval_js(js)


# ---------------------------------------------------------------------------
# Upstream mapping
# ---------------------------------------------------------------------------


def fetch_upstream() -> dict:
    print(f"Fetching upstream from {UPSTREAM_URL} ...")
    with urllib.request.urlopen(UPSTREAM_URL, timeout=30) as response:
        return json.load(response)


def find_upstream_entry(upstream: dict, model_id: str) -> dict | None:
    """
    Look for the model in upstream under short or long format.
    Returns the metadata dict if found, else None.
    """
    short_key = f"fireworks_ai/{model_id}"
    long_key = f"fireworks_ai/accounts/fireworks/models/{model_id}"
    return upstream.get(short_key) or upstream.get(long_key)


# ---------------------------------------------------------------------------
# Build output
# ---------------------------------------------------------------------------


def build_entry(model_id: str, listing_text: str, detail: dict, upstream_entry: dict | None) -> dict:
    """Build a single LiteLLM-compatible model entry."""
    if upstream_entry:
        # Start from upstream metadata (has correct costs, flags, etc.)
        entry = dict(upstream_entry)
        # Ensure provider is set
        entry["litellm_provider"] = "fireworks_ai"
        # If upstream has a source pointing to pricing, keep it; otherwise set one.
        if not entry.get("source"):
            entry["source"] = f"https://fireworks.ai/models/fireworks/{model_id}"
        return entry

    # No upstream entry — build from crawl data
    entry: dict[str, object] = {
        "litellm_provider": "fireworks_ai",
        "mode": "chat",
        "source": f"https://fireworks.ai/models/fireworks/{model_id}",
    }

    # Parse pricing from listing card text
    input_cost = parse_price(listing_text)
    cached_cost = None
    output_cost = None

    # Look for cached input price
    cached_match = re.search(r"\$([0-9.]+)/M\s+Cached\s+Input", listing_text, re.IGNORECASE)
    if cached_match:
        cached_cost = float(cached_match.group(1)) / 1_000_000

    # Look for output price
    output_match = re.search(r"\$([0-9.]+)/M\s+Output", listing_text, re.IGNORECASE)
    if output_match:
        output_cost = float(output_match.group(1)) / 1_000_000

    if input_cost is not None:
        entry["input_cost_per_token"] = input_cost
    if cached_cost is not None:
        entry["cache_read_input_token_cost"] = cached_cost
    if output_cost is not None:
        entry["output_cost_per_token"] = output_cost

    # Parse context length
    ctx = parse_context(listing_text)
    if ctx is not None:
        entry["max_tokens"] = ctx
        entry["max_input_tokens"] = ctx
        entry["max_output_tokens"] = ctx

    # Parse capabilities from detail page
    caps = parse_capabilities(detail.get("functionality", ""))
    entry.update(caps)

    # If listing says "Vision", force vision flag
    if "vision" in listing_text.lower():
        entry["supports_vision"] = True

    return entry


def main() -> int:
    verify_chrome_debugging()

    # ------------------------------------------------------------------
    # 1. Crawl listing
    # ------------------------------------------------------------------
    models = crawl_listing()
    if not models:
        print("No models found on listing page. Layout may have changed.", file=sys.stderr)
        return 1

    # ------------------------------------------------------------------
    # 2. Crawl detail pages
    # ------------------------------------------------------------------
    details: dict[str, dict] = {}
    for m in models:
        try:
            details[m["id"]] = crawl_model_detail(m["id"], m["href"])
        except Exception as exc:
            print(f"    Warning: failed to crawl {m['id']}: {exc}", file=sys.stderr)
            details[m["id"]] = {}

    # ------------------------------------------------------------------
    # 3. Fetch upstream
    # ------------------------------------------------------------------
    upstream = fetch_upstream()

    # ------------------------------------------------------------------
    # 4. Build entries
    # ------------------------------------------------------------------
    output: dict[str, dict] = {}
    for m in models:
        model_id = m["id"]
        upstream_entry = find_upstream_entry(upstream, model_id)
        entry = build_entry(model_id, m["text"], details.get(model_id, {}), upstream_entry)
        short_key = f"fireworks_ai/{model_id}"
        output[short_key] = entry
        status = "(from upstream)" if upstream_entry else "(from crawl)"
        print(f"  -> {short_key} {status}")

    # ------------------------------------------------------------------
    # 5. Write output
    # ------------------------------------------------------------------
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
        f.write("\n")

    print(f"\nWrote {len(output)} entries to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
