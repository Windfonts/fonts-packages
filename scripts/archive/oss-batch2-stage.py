#!/usr/bin/env python3
"""Stage oss-batch2-map.json families into fonts/{Norm}/.

Uses the batch1 downloader's stage_family. Does not upload.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "scripts" / "oss-batch2-map.json"


def load_downloader():
    spec = importlib.util.spec_from_file_location(
        "oss_batch1_download", ROOT / "scripts" / "oss-batch1-download.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("norms", nargs="*")
    args = ap.parse_args()
    want = set(args.norms)
    dl = load_downloader()
    data = json.loads(MAP.read_text())
    results = []
    for fam in data["families"]:
        if want and fam["norm"] not in want:
            continue
        if fam["norm"] in {"Hcpixels", "Hcline", "Sykd"}:
            print(f"== skip already registered {fam['norm']}", flush=True)
            continue
        print(f"== {fam['norm']} {fam.get('name')} ==", flush=True)
        try:
            result = dl.stage_family(fam)
        except Exception as e:
            result = {"status": "fail", "norm": fam["norm"], "reason": str(e)}
        print("  ->", result, flush=True)
        results.append(result)
    out = ROOT / "logs" / "oss-batch2-download.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n")
    print("wrote", out, flush=True)
    failed = [r for r in results if r.get("status") == "fail"]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
