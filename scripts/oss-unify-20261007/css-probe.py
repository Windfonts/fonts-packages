#!/usr/bin/env python3
"""Probe vault /api/css for every published family. Run on feicode-prod.

Reads JSON list from stdin (css-probe-list.json). Writes JSON report to stdout.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "http://127.0.0.1:4000/api/css"
DIR_RE = re.compile(r"fonts-packages/([^/\"'?]+)/")
FF_RE = re.compile(r"font-family:\s*['\"]([^'\"]+)['\"]")


def probe(item: dict) -> dict:
    fam = item.get("family") or ""
    weight = item.get("weight") or "Regular"
    q = urllib.parse.urlencode({"family": fam, "display": "full", "weight": weight})
    url = f"{BASE}?{q}"
    out = {
        "id": item.get("id"),
        "name": item.get("name"),
        "family": fam,
        "expect_dir": item.get("expect_dir"),
        "weight": weight,
        "http": None,
        "dir": None,
        "css_family": None,
        "err": None,
        "bytes": 0,
    }
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=12) as resp:
            body = resp.read(65536)
            out["http"] = resp.status
            out["bytes"] = len(body)
            text = body.decode("utf-8", "replace")
            m = DIR_RE.search(text)
            if m:
                out["dir"] = m.group(1)
            m2 = FF_RE.search(text)
            if m2:
                out["css_family"] = m2.group(1)
    except urllib.error.HTTPError as e:
        out["http"] = e.code
        try:
            body = e.read(2048)
            out["bytes"] = len(body)
        except Exception:
            pass
        out["err"] = f"HTTP {e.code}"
    except Exception as e:
        out["err"] = f"{type(e).__name__}: {e}"
    return out


def main() -> int:
    items = json.load(sys.stdin)
    results = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = [ex.submit(probe, it) for it in items]
        for fu in as_completed(futs):
            results.append(fu.result())
    results.sort(key=lambda r: (r.get("name") or "", r.get("family") or ""))
    ok = []
    http_fail = []
    dir_mismatch = []
    no_dir = []
    for r in results:
        if r.get("http") != 200:
            http_fail.append(r)
            continue
        d = (r.get("dir") or "").lower()
        exp = (r.get("expect_dir") or "").lower()
        if not d:
            no_dir.append(r)
        elif d != exp:
            dir_mismatch.append(r)
        else:
            ok.append(r)
    report = {
        "n": len(results),
        "ok": len(ok),
        "http_fail": len(http_fail),
        "dir_mismatch": len(dir_mismatch),
        "no_dir": len(no_dir),
        "http_fail_rows": [
            {k: r[k] for k in ("name", "family", "http", "err", "expect_dir")} for r in http_fail
        ],
        "dir_mismatch_rows": [
            {k: r[k] for k in ("name", "family", "dir", "expect_dir", "css_family")} for r in dir_mismatch
        ],
        "no_dir_rows": [
            {k: r[k] for k in ("name", "family", "http", "bytes", "expect_dir")} for r in no_dir
        ],
    }
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if not http_fail and not dir_mismatch and not no_dir else 1


if __name__ == "__main__":
    raise SystemExit(main())
