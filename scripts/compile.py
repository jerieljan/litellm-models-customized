#!/usr/bin/env python3
"""
Compile script for litellm-models-table-shortlist.

Fetches upstream model_prices_and_context_window.json from LiteLLM,
applies blocklist filters and custom additions, and writes the compiled output.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

UPSTREAM_URL = (
    "https://raw.githubusercontent.com/BerriAI/litellm/main/"
    "model_prices_and_context_window.json"
)

REPO_ROOT = Path(__file__).parent.parent.resolve()
CONFIG_DIR = REPO_ROOT / "config"
OUTPUT_PATH = REPO_ROOT / "model_prices_and_context_window.json"

BLOCKLIST_PATH = CONFIG_DIR / "blocklist.json"
ADDITIONS_PATH = CONFIG_DIR / "additions.json"
BLOCKLIST_SCHEMA_PATH = CONFIG_DIR / "blocklist.schema.json"
ADDITIONS_SCHEMA_PATH = CONFIG_DIR / "additions.schema.json"


def fetch_upstream():
    print(f"Fetching upstream from {UPSTREAM_URL} ...")
    with urllib.request.urlopen(UPSTREAM_URL, timeout=30) as response:
        return json.load(response)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_with_schema(data, schema_path, label):
    try:
        import jsonschema
    except ImportError:
        print(f"Warning: jsonschema not installed, skipping {label} validation.")
        return

    schema = load_json(schema_path)
    try:
        jsonschema.validate(instance=data, schema=schema)
        print(f"  OK {label} validated against schema.")
    except jsonschema.ValidationError as e:
        print(f"  ERROR {label} validation failed: {e.message}")
        print(f"    Path: {list(e.path)}")
        sys.exit(1)


def apply_blocklist(upstream, blocklist_config):
    patterns = blocklist_config.get("patterns", [])
    compiled = []
    for p in patterns:
        try:
            compiled.append(re.compile(p))
        except re.error as e:
            print(f"Error: Invalid regex in blocklist: '{p}' — {e}")
            sys.exit(1)

    if not compiled:
        print("No blocklist patterns configured.")
        return upstream

    filtered = {}
    removed = 0
    for key, value in upstream.items():
        if any(rx.search(key) for rx in compiled):
            removed += 1
            continue
        filtered[key] = value

    print(f"Blocklist removed {removed} model(s), kept {len(filtered)}.")
    return filtered


def merge_additions(filtered, additions):
    overridden = 0
    for key, value in additions.items():
        if key in filtered:
            overridden += 1
        filtered[key] = value

    if overridden:
        print(f"Additions overridden {overridden} existing upstream entry(ies).")
    print(f"Additions injected {len(additions)} entry(ies).")
    return filtered


def sort_output(data):
    if "sample_spec" in data:
        sample = {"sample_spec": data.pop("sample_spec")}
    else:
        sample = {}

    sorted_data = dict(sorted(data.items()))
    return {**sample, **sorted_data}


def main():
    # 1. Fetch upstream
    upstream = fetch_upstream()

    # 2. Load and validate blocklist
    blocklist = load_json(BLOCKLIST_PATH)
    validate_with_schema(blocklist, BLOCKLIST_SCHEMA_PATH, "blocklist")

    # 3. Load and validate additions
    additions = load_json(ADDITIONS_PATH)
    validate_with_schema(additions, ADDITIONS_SCHEMA_PATH, "additions")

    # 4. Apply blocklist
    filtered = apply_blocklist(upstream, blocklist)

    # 5. Merge additions
    merged = merge_additions(filtered, additions)

    # 6. Sort
    final = sort_output(merged)

    # 7. Write output
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, indent=4, ensure_ascii=False)
        f.write("\n")

    total = len(final) - (1 if "sample_spec" in final else 0)
    print(f"Wrote {OUTPUT_PATH} with {total} model entries (+ sample_spec).")


if __name__ == "__main__":
    main()
