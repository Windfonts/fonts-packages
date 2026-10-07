#!/usr/bin/env python3
"""Audit shop / vault / OSS / aliases / pack-subsets after OSS unify.

  python3 verify-align.py --phase copy
  python3 verify-align.py --phase pointers
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOP = Path("/Users/feibisi-studio/Projects/fonts-front/data/fonts.json")
SUBSETS = Path("/Users/feibisi-studio/Projects/fonts-front/data/pack-subsets.json")
SHOP_ALIAS = Path("/Users/feibisi-studio/Projects/fonts-front/data/family-aliases.json")
LIST = Path("/Users/feibisi-studio/Projects/fonts-front/data/fonts-list.json")

PIN11 = {
    "xwwkb": "霞鹜文楷 Bright",
    "xwwkbc": None,
    "xwwkdk": None,
    "xwwkdktc": None,
    "xwxxhc": None,
    "xwxxhp": None,
    "xwxxhs": None,
    "xwxxhsf": None,
    "xwxzsp": None,
    "xwxzss": None,
    "xwxzssf": None,
}
NAMED = {
    "harmsa": "HarmonyOS Sans",
    "zyzyjp": None,
    "cpfjp": None,
    "hsmb": None,
    "cdmc": None,
    "jycjp": None,
    "hcdht": "寒蝉端黑体",
}


def short_of(family: str) -> str:
    fam = str(family or "").strip()
    if fam.lower().startswith("wenfeng-"):
        return fam[8:].lower()
    return fam.lower()


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("copy", "pointers"), required=True)
    args = ap.parse_args()
    phase = args.phase

    m = load_json(HERE / "map.json")
    oss = load_json(HERE / "oss-prefixes.json")
    vault = load_json(HERE / "vault-fonts.json")
    shop = load_json(SHOP)
    ow = load_json(HERE / "overwrite.json")
    copy_rows = []
    copy_path = HERE / "copy-wave1.jsonl"
    if copy_path.exists():
        with copy_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    copy_rows.append(json.loads(line))
    copy_by_id = {}
    for r in copy_rows:
        copy_by_id[r.get("id")] = r

    prefs = set(oss.get("prefixes") or [])
    wave1 = {x["id"]: x for x in m.get("wave1_copies") or []}
    wave2 = {x["id"]: x for x in m.get("wave2_copies") or []}
    keep_dest = set(ow.get("keep_dest_old") or [])
    overwrite_old = set(ow.get("overwrite_old") or [])
    empty_ids = {
        r["id"]
        for r in copy_rows
        if r.get("skip") == "empty-src" or (r.get("src") == 0 and not r.get("copied"))
    }

    v_by_id = {r["id"]: r for r in vault.get("rows") or []}
    v_pub = [r for r in vault.get("rows") or [] if r.get("status") == "published"]

    issues: dict[str, list] = defaultdict(list)

    # --- shop identity ---
    if len(shop) != 707:
        issues["shop_count"].append(len(shop))
    ids = [f["id"] for f in shop]
    if len(ids) != len(set(ids)):
        issues["shop_dup_id"].append(len(ids) - len(set(ids)))
    shorts = []
    for f in shop:
        fam = str(f.get("family") or "")
        if not fam.lower().startswith("wenfeng-"):
            issues["family_no_prefix"].append(
                {"id": f["id"], "name": f.get("name"), "family": fam}
            )
        shorts.append(short_of(fam))
    dup_short = defaultdict(list)
    for f in shop:
        dup_short[short_of(f.get("family") or "")].append(f.get("name"))
    for s, names in sorted(dup_short.items()):
        if len(names) > 1:
            issues["dup_short"].append({"short": s, "names": names})
    if "clduan" in dup_short or any(short_of(f.get("family") or "") == "clduan" for f in shop):
        issues["clduan_still_in_shop"].append(True)
    shop_by_short = {short_of(f.get("family") or ""): f for f in shop}

    for code, expect_name in {**PIN11, **NAMED}.items():
        f = shop_by_short.get(code)
        if not f:
            issues["named_short_missing"].append(code)
            continue
        if expect_name and f.get("name") != expect_name:
            issues["named_short_name"].append(
                {"short": code, "want": expect_name, "got": f.get("name")}
            )

    # --- per shop row vs OSS / vault ---
    for f in shop:
        sid = f["id"]
        name = f.get("name")
        short = short_of(f.get("family") or "")
        norm = str(f.get("normalized") or "").strip()
        nlow = norm.lower()
        w1 = wave1.get(sid)
        w2 = wave2.get(sid)
        cr = copy_by_id.get(sid)

        if phase == "pointers":
            if w2:
                if nlow == short:
                    issues["wave2_pointer_moved_early"].append(
                        {"name": name, "short": short, "normalized": norm}
                    )
                elif w2["old"] != nlow:
                    issues["wave2_normalized_unexpected"].append(
                        {"name": name, "want_old": w2["old"], "got": nlow}
                    )
            elif sid in empty_ids or (w1 and w1["old"] in {"shmgt"} and (not cr or cr.get("src") == 0)):
                issues["empty_src"].append({"name": name, "short": short, "old": nlow})
            else:
                if nlow != short:
                    issues["shop_norm_not_short"].append(
                        {"name": name, "normalized": norm, "short": short}
                    )
        else:
            # copy phase: dest short must exist for successful wave1
            if w1 and sid not in empty_ids:
                dest = w1["new"]
                if dest not in prefs:
                    issues["oss_missing_dest"].append(
                        {"name": name, "dest": dest, "old": w1["old"]}
                    )
                if w1["old"] not in prefs:
                    issues["oss_missing_old"].append(
                        {"name": name, "old": w1["old"], "dest": dest}
                    )

        # license urls should not still point at old dir after pointers
        if phase == "pointers" and w1 and nlow == short:
            for key in ("licenseFileUrl", "licenseUrl"):
                val = f.get(key)
                if not isinstance(val, str) or not val:
                    continue
                oldp = "/fonts-packages/" + w1["old"] + "/"
                if oldp in val and w1["old"] != short:
                    issues["license_url_old"].append(
                        {"name": name, "key": key, "url": val}
                    )

        vr = v_by_id.get(sid)
        if vr and vr.get("status") == "published" and phase == "pointers":
            vf = str(vr.get("font_family") or "")
            vn = str(vr.get("normalized_name") or "")
            ossp = str(vr.get("oss_path") or "")
            if short_of(vf) != short:
                issues["vault_family_ne_shop"].append(
                    {
                        "name": name,
                        "shop": f.get("family"),
                        "vault": vf,
                    }
                )
            if w2:
                pass
            elif sid in empty_ids:
                pass
            else:
                if vn.lower() != short:
                    issues["vault_norm_ne_short"].append(
                        {
                            "name": name,
                            "vault_norm": vn,
                            "short": short,
                            "status": vr.get("status"),
                        }
                    )
                want_oss = "/fonts-packages/" + short
                if ossp.lower() != want_oss:
                    issues["vault_oss_path"].append(
                        {"name": name, "oss_path": ossp, "want": want_oss}
                    )

    # --- vault published not in shop ---
    shop_ids = {f["id"] for f in shop}
    for r in v_pub:
        if r["id"] in shop_ids:
            continue
        short = short_of(r.get("font_family") or "")
        vn = str(r.get("normalized_name") or "").lower()
        if phase == "pointers" and r["id"] not in wave2 and r["id"] not in empty_ids:
            if vn != short and r["id"] in wave1:
                issues["vault_only_norm_ne_short"].append(
                    {
                        "name": r.get("name"),
                        "family": r.get("font_family"),
                        "norm": r.get("normalized_name"),
                    }
                )
        if phase == "copy" and r["id"] in wave1 and r["id"] not in empty_ids:
            dest = wave1[r["id"]]["new"]
            if dest not in prefs:
                issues["oss_missing_dest_vault_only"].append(
                    {"name": r.get("name"), "dest": dest}
                )

    # --- copy jsonl health ---
    mismatch = []
    real_fail = []
    empty = []
    ok_n = 0
    seen_ids = set()
    for r in copy_rows:
        seen_ids.add(r.get("id"))
        if r.get("skip") == "empty-src" or r.get("src") == 0:
            empty.append(r)
            continue
        errs = r.get("errors") or []
        mm = bool(errs) and all("dest-exists-size-mismatch" in str(e) for e in errs)
        if r.get("failed", 0) > 0 or r.get("ok") is False:
            if mm:
                mismatch.append(r)
            else:
                real_fail.append(r)
            continue
        ok_n += 1
    if real_fail:
        issues["copy_real_fail"].append(
            [{"name": r.get("name"), "old": r.get("old"), "new": r.get("new")} for r in real_fail]
        )
    expected_w1 = {x["id"] for x in m.get("wave1_copies") or []}
    missing_copy = expected_w1 - seen_ids
    if missing_copy and phase in ("copy", "pointers"):
        issues["copy_incomplete"].append(len(missing_copy))

    # mismatch leftovers: overwrite list must be resolved at pointers phase
    if phase == "pointers":
        ow_log = HERE / "copy-overwrite.jsonl"
        overwritten = set()
        if ow_log.exists():
            with ow_log.open(encoding="utf-8") as f:
                for line in f:
                    o = json.loads(line)
                    if o.get("ok") and o.get("failed", 0) == 0:
                        overwritten.add(o.get("old"))
        for r in mismatch:
            old = r.get("old")
            if old in keep_dest:
                continue
            if old in overwrite_old and old not in overwritten:
                issues["mismatch_not_overwritten"].append(
                    {"name": r.get("name"), "old": old, "new": r.get("new")}
                )

    # --- pack-subsets ---
    if SUBSETS.exists():
        packs = (load_json(SUBSETS).get("packs")) or {}
        if phase == "pointers":
            for x in m.get("wave1_copies") or []:
                if x["id"] in empty_ids:
                    continue
                if x["new"] not in packs and x["old"] in packs:
                    issues["pack_subsets_missing_new"].append(
                        {"name": x["name"], "new": x["new"]}
                    )

    # --- fonts-list vs fonts.json ---
    if LIST.exists() and phase == "pointers":
        lite = load_json(LIST)
        if len(lite) != len(shop):
            issues["list_count"].append({"list": len(lite), "shop": len(shop)})
        shop_fam = {f["id"]: f.get("family") for f in shop}
        shop_norm = {f["id"]: f.get("normalized") for f in shop}
        for row in lite:
            i = row.get("id")
            if shop_fam.get(i) != row.get("family"):
                issues["list_family_drift"].append(i)
            if shop_norm.get(i) != row.get("normalized"):
                issues["list_norm_drift"].append(i)

    # --- aliases: recycle live keys must not be alias keys ---
    if SHOP_ALIAS.exists():
        al = load_json(SHOP_ALIAS)
        live = {short_of(f.get("family") or "") for f in shop}
        live |= {"wenfeng-" + s for s in live}
        recycle = {"cjkfqlt", "hcth", "ddxstyx", "zmxs", "kaiso"}
        for k in al:
            raw = str(k)
            bare = raw[8:] if raw.startswith("wenfeng-") else raw
            if bare in recycle:
                issues["alias_recycle_key"].append(raw)

    report = {
        "phase": phase,
        "shop": len(shop),
        "vault_published": len(v_pub),
        "oss_prefixes": len(prefs),
        "copy_ok": ok_n,
        "copy_empty": len(empty),
        "copy_mismatch": len(mismatch),
        "copy_real_fail": len(real_fail),
        "copy_missing": len(missing_copy),
        "issue_counts": {k: len(v) for k, v in issues.items()},
        "issues": {k: v[:40] for k, v in issues.items()},
        "wave2": [
            {"name": x["name"], "old": x["old"], "new": x["new"]}
            for x in m.get("wave2_copies") or []
        ],
        "empty": [
            {"name": r.get("name"), "old": r.get("old"), "new": r.get("new")}
            for r in empty
        ],
        "mismatch": [
            {
                "name": r.get("name"),
                "old": r.get("old"),
                "new": r.get("new"),
                "failed": r.get("failed"),
                "copied": r.get("copied"),
                "skipped": r.get("skipped"),
            }
            for r in mismatch
        ],
    }
    out = HERE / f"verify-{phase}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "issues"}, ensure_ascii=False, indent=2))
    if issues:
        print("ISSUES", {k: len(v) for k, v in issues.items()}, file=sys.stderr)
        return 1
    print("ALIGN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
