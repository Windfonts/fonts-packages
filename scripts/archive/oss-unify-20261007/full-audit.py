#!/usr/bin/env python3
"""Full shop / vault / OSS / alias / subset / list alignment after OSS unify.

Writes full-audit.json and css-probe-list.json.
Does not hit the network.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHOP = Path("/Users/feibisi-studio/Projects/fonts-front/data/fonts.json")
SUBSETS = Path("/Users/feibisi-studio/Projects/fonts-front/data/pack-subsets.json")
SHOP_ALIAS = Path("/Users/feibisi-studio/Projects/fonts-front/data/family-aliases.json")
LIST = Path("/Users/feibisi-studio/Projects/fonts-front/data/fonts-list.json")

PIN11 = [
    "xwwkb",
    "xwwkbc",
    "xwwkdk",
    "xwwkdktc",
    "xwxxhc",
    "xwxxhp",
    "xwxxhs",
    "xwxxhsf",
    "xwxzsp",
    "xwxzss",
    "xwxzssf",
]
NAMED = {
    "harmsa": "HarmonyOS Sans",
    "zyzyjp": None,
    "cpfjp": None,
    "hsmb": None,
    "cdmc": None,
    "jycjp": None,
    "hcdht": "寒蝉端黑体",
    "cjksxz": "CJK手写字",
    "cjkfqlt": "cjkFonts 全濑体",
}
RECYCLE_LIVE = {"cjkfqlt", "hcth", "ddxstyx", "zmxs", "kaiso", "cjksxz", "hcyjt", "ddxsyt", "kisjp"}
MERGE_STEAL_OK = {
    "clduan": "hcdht",
    "wenfeng-clduan": "wenfeng-hcdht",
}


def short_of(family: str) -> str:
    fam = str(family or "").strip()
    if fam.lower().startswith("wenfeng-"):
        return fam[8:].lower()
    return fam.lower()


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def parse_weights(raw):
    if raw is None or raw == "":
        return "empty", []
    if isinstance(raw, (dict, list)):
        obj = raw
    else:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            return "unparseable", []
    if isinstance(obj, list):
        names = [str(x) for x in obj]
        return "array", names
    if isinstance(obj, dict):
        return "object", list(obj.keys())
    return "other", []


def pick_weight(kind: str, names: list[str]) -> str:
    if "Regular" in names:
        return "Regular"
    if names:
        return names[0]
    return "Regular"


def main() -> int:
    m = load(HERE / "map.json")
    oss = load(HERE / "oss-prefixes.json")
    vault = load(HERE / "vault-fonts.json")
    shop = load(SHOP)
    ow = load(HERE / "overwrite.json")
    shop_al_raw = load(SHOP_ALIAS) if SHOP_ALIAS.exists() else {}
    shop_al = shop_al_raw.get("aliases") if isinstance(shop_al_raw, dict) and "aliases" in shop_al_raw else shop_al_raw
    vault_al_wrap = load(HERE / "vault-family-aliases.json")
    vault_al = vault_al_wrap.get("aliases") if isinstance(vault_al_wrap, dict) and "aliases" in vault_al_wrap else vault_al_wrap
    packs = (load(SUBSETS).get("packs") or {}) if SUBSETS.exists() else {}
    lite = load(LIST) if LIST.exists() else []
    prefs = set(oss.get("prefixes") or [])

    wave1 = {x["id"]: x for x in m.get("wave1_copies") or []}
    wave2 = {x["id"]: x for x in m.get("wave2_copies") or []}
    dropped = {x["id"]: x for x in m.get("wave1_dropped_dup_dest") or []}
    keep_dest = set(ow.get("keep_dest_old") or [])
    overwrite_old = set(ow.get("overwrite_old") or [])

    copy_by_id = {}
    copy_path = HERE / "copy-wave1.jsonl"
    if copy_path.exists():
        with copy_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    o = json.loads(line)
                    copy_by_id[o.get("id")] = o
    empty_ids = {
        r["id"]
        for r in copy_by_id.values()
        if r.get("skip") == "empty-src" or (r.get("src") == 0 and not r.get("copied"))
    }
    overwritten = set()
    ow_log = HERE / "copy-overwrite.jsonl"
    if ow_log.exists():
        with ow_log.open(encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                if o.get("ok") and o.get("failed", 0) == 0:
                    overwritten.add(o.get("old"))

    v_rows = vault.get("rows") or []
    v_by_id = {r["id"]: r for r in v_rows}
    v_pub = [r for r in v_rows if r.get("status") == "published"]
    shop_by_id = {f["id"]: f for f in shop}
    shop_ids = set(shop_by_id)

    issues: dict[str, list] = defaultdict(list)
    expected_open: dict[str, list] = defaultdict(list)

    # --- shop identity ---
    if len(shop) != 707:
        issues["shop_count"].append(len(shop))
    ids = [f["id"] for f in shop]
    if len(ids) != len(set(ids)):
        issues["shop_dup_id"].append(len(ids) - len(set(ids)))
    dup_short = defaultdict(list)
    for f in shop:
        fam = str(f.get("family") or "")
        if not fam.lower().startswith("wenfeng-"):
            issues["family_no_prefix"].append({"id": f["id"], "name": f.get("name"), "family": fam})
        dup_short[short_of(fam)].append(f.get("name"))
    for s, names in sorted(dup_short.items()):
        if len(names) > 1:
            issues["dup_short"].append({"short": s, "names": names})
    if any(short_of(f.get("family") or "") == "clduan" for f in shop):
        issues["clduan_still_in_shop"].append(True)

    shop_by_short = {short_of(f.get("family") or ""): f for f in shop}
    for code in PIN11:
        if code not in shop_by_short:
            issues["named_short_missing"].append(code)
    for code, expect_name in NAMED.items():
        f = shop_by_short.get(code)
        if not f:
            issues["named_short_missing"].append(code)
            continue
        if expect_name and f.get("name") != expect_name:
            issues["named_short_name"].append({"short": code, "want": expect_name, "got": f.get("name")})

    # --- per shop row ---
    for f in shop:
        sid = f["id"]
        name = f.get("name")
        short = short_of(f.get("family") or "")
        nlow = str(f.get("normalized") or "").strip().lower()
        w1 = wave1.get(sid)
        w2 = wave2.get(sid)
        vr = v_by_id.get(sid)

        if w2:
            if nlow == short:
                expected_open["wave2_shop_already_short"].append({"name": name, "short": short})
            elif nlow != w2["old"]:
                issues["wave2_normalized_unexpected"].append({"name": name, "want_old": w2["old"], "got": nlow})
            else:
                expected_open["wave2_shop_old_dir"].append({"name": name, "old": nlow, "new": short})
        elif sid in empty_ids:
            expected_open["empty_src"].append({"name": name, "short": short, "normalized": nlow})
        elif sid in dropped:
            # dest occupied: shop may already point at short while dest belongs to the other registration
            if nlow != short:
                expected_open["dropped_shop_kept_old"].append({"name": name, "normalized": nlow, "short": short})
            else:
                expected_open["dropped_shop_points_occupied_dest"].append({"name": name, "short": short, "old": dropped[sid]["old"]})
        else:
            if nlow != short:
                issues["shop_norm_not_short"].append({"name": name, "normalized": f.get("normalized"), "short": short})

        if short and short not in prefs and nlow not in prefs:
            if sid in empty_ids:
                pass
            else:
                issues["oss_missing_shop_dir"].append({"name": name, "short": short, "normalized": nlow})
        elif short and short not in prefs and nlow in prefs:
            if w2 or sid in empty_ids or sid in dropped:
                expected_open["oss_only_old_dir"].append({"name": name, "old": nlow, "short": short})
            else:
                issues["oss_missing_new_dir"].append({"name": name, "short": short, "old": nlow})

        if w1 and nlow == short:
            for key in ("licenseFileUrl", "licenseUrl"):
                val = f.get(key)
                if not isinstance(val, str) or not val:
                    continue
                oldp = "/fonts-packages/" + w1["old"] + "/"
                if oldp in val and w1["old"] != short:
                    issues["license_url_old"].append({"name": name, "key": key, "url": val})

        if vr and vr.get("status") == "published":
            vf = str(vr.get("font_family") or "")
            vn = str(vr.get("normalized_name") or "")
            ossp = str(vr.get("oss_path") or "")
            if short_of(vf) != short:
                issues["vault_family_ne_shop"].append({"name": name, "shop": f.get("family"), "vault": vf})
            skip_norm = bool(w2) or sid in empty_ids or sid in dropped
            if skip_norm:
                if vn.lower() != short:
                    expected_open["vault_kept_old_norm"].append(
                        {"name": name, "vault_norm": vn, "short": short, "why": "wave2" if w2 else ("empty" if sid in empty_ids else "dropped")}
                    )
            else:
                if vn.lower() != short:
                    issues["vault_norm_ne_short"].append({"name": name, "vault_norm": vn, "short": short})
                want_oss = "/fonts-packages/" + short
                if ossp.lower() != want_oss:
                    issues["vault_oss_path"].append({"name": name, "oss_path": ossp, "want": want_oss})

        if sid in packs or short in packs or nlow in packs:
            pass
        elif w1 and short not in packs and w1["old"] in packs:
            issues["pack_subsets_missing_new"].append({"name": name, "new": short})

    # --- vault published ---
    css_probe = []
    weights_array = []
    for r in v_pub:
        kind, names = parse_weights(r.get("weights"))
        short = short_of(r.get("font_family") or "")
        vn = str(r.get("normalized_name") or "").lower()
        ossp = str(r.get("oss_path") or "")
        expect_dir = vn
        if kind == "array":
            weights_array.append({"name": r.get("name"), "id": r["id"], "weights": names, "family": r.get("font_family")})
            issues["vault_weights_array"].append({"name": r.get("name"), "weights": names, "family": r.get("font_family")})
        elif kind == "empty":
            issues["vault_weights_empty"].append({"name": r.get("name"), "family": r.get("font_family")})
        css_probe.append(
            {
                "id": r["id"],
                "name": r.get("name"),
                "family": r.get("font_family"),
                "normalized": r.get("normalized_name"),
                "expect_dir": expect_dir,
                "weight": pick_weight(kind, names),
                "in_shop": r["id"] in shop_ids,
                "wave2": r["id"] in wave2,
                "empty": r["id"] in empty_ids,
                "dropped": r["id"] in dropped,
            }
        )
        if r["id"] not in shop_ids:
            expected_open["vault_only_published"].append(
                {"id": r["id"], "name": r.get("name"), "family": r.get("font_family"), "norm": r.get("normalized_name")}
            )
        if r["id"] in dropped and vn != dropped[r["id"]]["old"] and vn != short:
            issues["dropped_vault_norm_unexpected"].append({"name": r.get("name"), "norm": vn, "old": dropped[r["id"]]["old"], "short": short})
        # oss_path vs normalized for ALL published
        want = "/fonts-packages/" + vn
        if ossp.lower() != want:
            issues["vault_oss_ne_norm"].append({"name": r.get("name"), "oss_path": ossp, "want": want})
        if vn and vn not in prefs:
            item = {"name": r.get("name"), "norm": vn, "family": r.get("font_family")}
            if r["id"] in empty_ids:
                expected_open["oss_missing_empty_src"].append(item)
            else:
                issues["oss_missing_vault_norm"].append(item)

    shop_only = []
    for f in shop:
        if f["id"] not in v_by_id:
            shop_only.append({"id": f["id"], "name": f.get("name"), "family": f.get("family")})
        elif v_by_id[f["id"]].get("status") != "published":
            expected_open["shop_vault_unpublished"].append(
                {"name": f.get("name"), "status": v_by_id[f["id"]].get("status"), "family": f.get("family")}
            )
    if shop_only:
        expected_open["shop_only_no_vault_row"].extend(shop_only)

    # --- fonts-list ---
    if lite:
        if len(lite) != len(shop):
            issues["list_count"].append({"list": len(lite), "shop": len(shop)})
        shop_fam = {f["id"]: f.get("family") for f in shop}
        shop_norm = {f["id"]: f.get("normalized") for f in shop}
        for row in lite:
            i = row.get("id")
            if shop_fam.get(i) != row.get("family"):
                issues["list_family_drift"].append({"id": i, "list": row.get("family"), "shop": shop_fam.get(i)})
            if shop_norm.get(i) != row.get("normalized"):
                issues["list_norm_drift"].append({"id": i, "list": row.get("normalized"), "shop": shop_norm.get(i)})

    # --- aliases ---
    live_shop = {short_of(f.get("family") or "") for f in shop}
    live_vault = {short_of(r.get("font_family") or "") for r in v_pub}
    live_all = live_shop | live_vault

    def alias_problems(al: dict, tag: str):
        if not isinstance(al, dict):
            issues[f"{tag}_not_dict"].append(type(al).__name__)
            return
        for k, v in al.items():
            bare_k = short_of(k)
            bare_v = short_of(str(v or ""))
            if bare_k in RECYCLE_LIVE:
                issues[f"{tag}_recycle_key"].append({"key": k, "to": v})
            ok_merge = MERGE_STEAL_OK.get(k) == v or MERGE_STEAL_OK.get(bare_k) == bare_v
            if bare_k in live_all and bare_v and bare_v != bare_k and not ok_merge:
                # live family used as alias key → steal
                owner_shop = shop_by_short.get(bare_k)
                owner_name = owner_shop.get("name") if owner_shop else None
                issues[f"{tag}_steal_live_key"].append({"key": k, "to": v, "owner": owner_name})

    alias_problems(shop_al, "shop_alias")
    alias_problems(vault_al, "vault_alias")

    # 寒蝉 merge must exist
    for k in ("clduan", "wenfeng-clduan"):
        if shop_al.get(k) not in ("hcdht", "wenfeng-hcdht") and shop_al.get("wenfeng-clduan") != "wenfeng-hcdht":
            if k in shop_al or "wenfeng-clduan" in shop_al:
                pass
        got = shop_al.get(k) or shop_al.get("wenfeng-" + k if not k.startswith("wenfeng-") else k)
    if shop_al.get("wenfeng-clduan") != "wenfeng-hcdht" and shop_al.get("clduan") not in ("hcdht", "wenfeng-hcdht"):
        issues["clduan_alias_missing"].append({"shop": {k: shop_al.get(k) for k in ("clduan", "wenfeng-clduan")}})
    if vault_al.get("wenfeng-clduan") != "wenfeng-hcdht" and vault_al.get("clduan") not in ("hcdht", "wenfeng-hcdht"):
        issues["clduan_alias_missing"].append({"vault": {k: vault_al.get(k) for k in ("clduan", "wenfeng-clduan")}})

    # overwrite leftovers
    for old in overwrite_old:
        if old not in overwritten:
            issues["mismatch_not_overwritten"].append(old)

    # mixed OSS
    mixed = [p for p in prefs if p != p.lower()]
    if mixed:
        issues["oss_mixed_case"].append(len(mixed))

    report = {
        "shop": len(shop),
        "vault_n": vault.get("n"),
        "vault_published": len(v_pub),
        "oss_prefixes": len(prefs),
        "oss_mixed": len(mixed),
        "shop_aliases": len(shop_al) if isinstance(shop_al, dict) else None,
        "vault_aliases": len(vault_al) if isinstance(vault_al, dict) else None,
        "pack_subsets": len(packs),
        "fonts_list": len(lite),
        "css_probe_n": len(css_probe),
        "issue_counts": {k: len(v) for k, v in issues.items()},
        "expected_open_counts": {k: len(v) for k, v in expected_open.items()},
        "issues": {k: v[:50] for k, v in issues.items()},
        "expected_open": {k: v[:50] for k, v in expected_open.items()},
        "wave2": [
            {"name": x["name"], "old": x["old"], "new": x["new"], "source": x.get("source")}
            for x in m.get("wave2_copies") or []
        ],
        "dropped_dup_dest": m.get("wave1_dropped_dup_dest") or [],
        "keep_dest_old": sorted(keep_dest),
        "overwrite_old": sorted(overwrite_old),
        "overwritten": sorted(overwritten),
        "pin11_ok": all(c in shop_by_short for c in PIN11),
        "named_ok": all(c in shop_by_short for c in NAMED),
    }
    (HERE / "full-audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "css-probe-list.json").write_text(json.dumps(css_probe, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k not in ("issues", "expected_open")}, ensure_ascii=False, indent=2))
    if issues:
        print("ISSUES", {k: len(v) for k, v in issues.items()})
        return 1
    print("DATA_ALIGN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
