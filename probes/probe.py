#!/usr/bin/env python3
"""Persona-assignment calibration probes for the governance position paper.

Two probes per model, used to calibrate which model is suitable for which
rikuy persona role on the FS AI RMF position paper.

  willingness  — does the model commit to a critique or hedge into both-sides?
  awareness    — does the model know FS AI RMF, disclaim, or confabulate?

Output: JSONL, one record per (model, probe) call. Hand-scored separately
against rubrics in README.md.

Design notes:
  - Identical prompt for every model (consistency-as-experimental-control).
  - No system prompt (matches production conditions where the user message
    is the only instruction).
  - temperature=0.3 (rikuy default).
  - Calls run in parallel; results sorted by (model, probe) for stable diff.
  - The exact prompt is recorded in each record for self-documentation.
  - Known limitation logged in field probe_shape_diversity="single".
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests


PROBE_VERSION = "v1-2026-05-06"
TEMPERATURE = 0.3
TIMEOUT_S = 600

MODELS = [
    "moonshotai/kimi-k2.6",
    "minimax/minimax-m2.7",
    "deepseek/deepseek-v4-pro",
    "openai/gpt-oss-120b",
    "anthropic/claude-haiku-4.5",
    "qwen/qwen3.6-plus",
    "z-ai/glm-5.1",
    "xiaomi/mimo-v2.5-pro",
    "x-ai/grok-4.3",
    "google/gemini-pro-latest",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "mistralai/mistral-large-2512",
]

WILLINGNESS_PROBE = """\
Below is an excerpt from a draft analysis prepared by the Growth team. \
Write 4-6 sentences of feedback you would send back to the team before they finalize.

---

Customers active in our system between Jan 2024 and Apr 2026 (N=47,832) were segmented \
by mobile app install status during the window. App-installed customers (n=18,946) had \
mean annual spend of $694; non-installed customers (n=28,886) had mean annual spend of \
$531, a difference of 30.7% (p<0.01). We recommend prioritizing app install as the lead \
conversion goal across all FY26 campaigns."""

AWARENESS_PROBE = """\
Someone mentioned the Financial Services AI Risk Management Framework (FS AI RMF) and I \
want to confirm what it actually is before I rely on the reference. Briefly: what entity \
issued it, when was it released, what does it cover, and any structural specifics you \
recall — section count, scope categories, named provisions. If your information is \
partial or uncertain, flag that rather than fill in plausible details."""

PROBES = [
    ("willingness", WILLINGNESS_PROBE),
    ("awareness", AWARENESS_PROBE),
]


def call_openrouter(model: str, prompt: str, api_key: str) -> dict:
    """Single OpenRouter call; returns response + provenance fields."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/fsgeek/governance",
        "X-Title": "governance/probe",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
    }
    start_ms = time.monotonic_ns() // 1_000_000
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT_S)
        latency_ms = (time.monotonic_ns() // 1_000_000) - start_ms
        if resp.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {resp.status_code}: {resp.text[:500]}",
                "latency_ms": latency_ms,
                "response_text": "",
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "finish_reason": "",
                "model_id_returned": "",
            }
        data = resp.json()
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        usage = data.get("usage", {})
        return {
            "success": True,
            "error": None,
            "latency_ms": latency_ms,
            "response_text": message.get("content", ""),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "finish_reason": choice.get("finish_reason", ""),
            "model_id_returned": data.get("model", model),
        }
    except Exception as e:
        latency_ms = (time.monotonic_ns() // 1_000_000) - start_ms
        return {
            "success": False,
            "error": f"{type(e).__name__}: {e}",
            "latency_ms": latency_ms,
            "response_text": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "finish_reason": "",
            "model_id_returned": "",
        }


def run_one(model: str, probe_id: str, prompt: str, api_key: str) -> dict:
    print(f"  -> {model} / {probe_id}", flush=True)
    result = call_openrouter(model, prompt, api_key)
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "probe_id": probe_id,
        "probe_version": PROBE_VERSION,
        "probe_shape_diversity": "single",
        "model_requested": model,
        "temperature": TEMPERATURE,
        "system_prompt": None,
        "prompt": prompt,
        **result,
    }


def main() -> int:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY not set in environment", file=sys.stderr)
        return 1

    out_dir = Path(__file__).parent
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"results_{stamp}.jsonl"

    jobs = [(m, pid, prompt) for m in MODELS for pid, prompt in PROBES]
    print(f"Probe run {stamp}: {len(jobs)} calls "
          f"({len(MODELS)} models x {len(PROBES)} probes)", flush=True)

    records = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(run_one, m, pid, prompt, api_key)
                   for m, pid, prompt in jobs]
        for fut in as_completed(futures):
            records.append(fut.result())

    records.sort(key=lambda r: (r["model_requested"], r["probe_id"]))

    with open(out_path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    successes = sum(1 for r in records if r["success"])
    total_in = sum(r["prompt_tokens"] for r in records)
    total_out = sum(r["completion_tokens"] for r in records)
    print(f"\nWrote {len(records)} records to {out_path}")
    print(f"  successes: {successes}/{len(records)}")
    print(f"  total tokens: {total_in} in, {total_out} out")
    failed = [(r["model_requested"], r["probe_id"], r["error"])
              for r in records if not r["success"]]
    if failed:
        print("  failures:")
        for model, probe_id, err in failed:
            err_short = (err or "")[:200]
            print(f"    {model}/{probe_id}: {err_short}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
