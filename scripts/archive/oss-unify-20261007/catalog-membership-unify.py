#!/usr/bin/env python3
"""Make shop + org catalogs share the same shorts and membership.

- Shop: lowercase remaining CamelCase normalized; 上海摩登 Shmgt→shmdt; insert 6 BDF.
- Org: insert shop-only rows; insert 6 BDF; merge 寒蝉端黑 Clduan into hcdht;
  lowercase leftover CamelCase norms. Do not run export-wenfeng.py (it unlinks overlays).
- 26 org-only faces with no vault row and no Guangzhou pack stay org-only.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = Path.home()
SHOP_ROOT = HOME / "Projects" / "fonts-front"
ORG = HOME / "Projects" / "wenfeng-org"
LIC_ROOT = HOME / "Projects" / "font-licenses"
FOUNDRY_ROOT = HOME / "Projects" / "font-foundries"
TODAY = date.today().isoformat()
SHOP_HREF = "https://app.windfonts.com/fonts/"
ARCHIVE_HREF_PREFIX = "https://cn.windfonts.com/wenfeng-original/"
DEFAULT_AVATAR = (
    "https://cravatar.com/avatar/"
    "bda050585a00f0f6cb502350559d75532ae3b244c9498b996e7c5df2d98dfc8d"
    "?s=144&d=identicon"
)
LICENSE_URL_RE = re.compile(
    r"/(OFL|OFLLICENSE|LICENSE|COPYING)[^/]*$|/licenses?/|\.txt$|\.pdf$", re.I
)
OFL_TEXT_STATES = ("full", "pointer", "missing")
SLIM_KEYS = (
    "norm",
    "name",
    "en",
    "licenseName",
    "foundry",
    "foundrySlug",
    "offer",
    "slice",
    "distribution",
    "shop",
    "weights",
    "family",
    "license",
)
BDF_IDS = {
    "c0754a33-c53b-46cd-96d6-501ba0adb1ff",
    "7fc63136-1286-4a40-9df4-090d135db09b",
    "30ecc980-dbf8-452e-9799-4b3ad65896b6",
    "da9743c0-853d-41eb-896d-e9dcc7f98a08",
    "2aa12e56-6e03-4350-abc9-31ca73904e74",
    "9bcab8ba-4793-4309-b677-276a9ad87148",
}


def load(path: Path):
    return json.loads(path.read_text("utf-8"))


def dump(path: Path, obj, indent=None, compact=False):
    if compact:
        text = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    else:
        text = json.dumps(obj, ensure_ascii=False, indent=indent)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, "utf-8")


def family_short(family: str) -> str:
    fam = str(family or "").strip()
    if fam.startswith("wenfeng-"):
        return fam[8:]
    return fam


def weight_names(weights) -> list:
    out = []
    if not weights:
        return ["Regular"]
    if isinstance(weights, dict):
        keys = list(weights.keys())
        if "Regular" in keys:
            keys = ["Regular"] + [k for k in keys if k != "Regular"]
        return keys
    for x in weights:
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            n = x.get("name") or x.get("weight_name") or x.get("weight")
            if n:
                out.append(str(n))
    return out or ["Regular"]


def add_alias(aliases, value):
    if not value:
        return
    s = str(value).strip()
    if not s:
        return
    have = {str(x).lower() for x in aliases}
    if s.lower() in have:
        return
    aliases.append(s)


def slim_license(lic):
    lic = lic or {}
    out = {"textState": lic.get("textState")}
    if lic.get("spdx"):
        out["spdx"] = lic["spdx"]
    return out


def slim_of(full):
    row = {k: full.get(k) for k in SLIM_KEYS}
    row["license"] = slim_license(full.get("license"))
    aliases = full.get("aliases") or []
    if aliases:
        row["aliases"] = aliases
    return {k: v for k, v in row.items() if v not in (None, [], "")}


def repo_like(u):
    return bool(u) and not LICENSE_URL_RE.search(str(u))


def parse_rfn(text):
    m = re.search(r"with Reserved Font Names?\s+(.+?)\.(?:\s|$)", text or "")
    if not m:
        return None
    names = re.findall(r"'([^']+)'", m.group(1))
    return "、".join(names) if names else None


def spdx_of(info, base):
    if info and info.get("spdx"):
        return info["spdx"]
    name = (base.get("licenseName") or "").lower()
    for token, spdx in (
        ("open font license", "OFL-1.1"),
        ("apache", "Apache-2.0"),
        ("mit license", "MIT"),
        ("gnu lesser", "LGPL-2.1"),
        ("gnu general", "GPL-3.0"),
        ("cc-by-sa", "CC-BY-SA-4.0"),
        ("cc by 4.0", "CC-BY-4.0"),
    ):
        if token in name:
            return spdx
    return None


def text_state(lic_path, info):
    if lic_path and lic_path.exists():
        return "full"
    if info:
        return "pointer"
    return "missing"


def offer_of(mirror_state, info, upstream, has_text=False):
    if mirror_state == "mirrored":
        return "source"
    if (info or has_text) and upstream:
        return "jump"
    if info or has_text:
        return "pending"
    return "missing"


def owner_names(foundries_root: Path):
    names = {}
    if not foundries_root.is_dir():
        return names
    for d in foundries_root.iterdir():
        prof = d / "profile.json"
        if not prof.exists():
            continue
        try:
            p = load(prof)
        except Exception:
            continue
        names[d.name] = p.get("name") or p.get("nameEn") or d.name
    return names


def build_origin(lin, owners):
    if not lin or lin.get("relation") != "fork":
        return None
    work = lin.get("upstreamName") or ""
    owner_id = lin.get("upstreamOwnerId") or ""
    author = owners.get(owner_id, owner_id)
    if not work or not author:
        return None
    return {
        "rootAuthor": author,
        "rootWork": work,
        "note": "衍生字体，授权随上游沿袭。"
        if lin.get("licenseFollows") == "inherit"
        else "衍生字体，授权见各自主页。",
    }


def json_list(val):
    if isinstance(val, list):
        return val
    if isinstance(val, str) and val.startswith("["):
        try:
            return json.loads(val)
        except Exception:
            return []
    return []


def shop_row_from_vault(v, foundries_by_id):
    fam = v["font_family"]
    short = family_short(fam)
    weights = v.get("weights")
    if isinstance(weights, str):
        try:
            weights = json.loads(weights)
        except Exception:
            weights = {}
    wnames = weight_names(weights)
    char_count = 0
    glyph_count = 0
    if isinstance(weights, dict):
        first = weights.get("Regular") or (next(iter(weights.values())) if weights else {})
        orig = ((first or {}).get("versions") or {}).get("original") or {}
        char_count = orig.get("char_count") or 0
        glyph_count = orig.get("glyph_count") or 0
    lic = v.get("license") or ""
    lic_l = str(lic).lower()
    if "ofl" in lic_l:
        license_name = "SIL Open Font License 1.1"
        shop_lic = "免费商用"
    elif "cc-by-sa" in lic_l:
        license_name = "CC-BY-SA-4.0"
        shop_lic = "免费商用"
    else:
        license_name = f"{v['name']}授权协议"
        shop_lic = "免费商用"
    foundry_name = v.get("foundry") or ""
    brand = None
    fid = (v.get("brand_id") or "").strip()
    # foundries.json uses slug ids like flopdesign, not vault UUIDs
    for entry in foundries_by_id:
        if foundry_name and (
            foundry_name in (entry.get("aliases") or [])
            or foundry_name == entry.get("name")
            or foundry_name == entry.get("en")
        ):
            brand = {
                "name": entry.get("name") or foundry_name,
                "slug": entry.get("id") or (foundry_name.lower().replace(" ", "")),
                "logoUrl": "",
                "avatarUrl": "",
                "website": entry.get("website") or "",
            }
            break
    designer = v.get("designer") or ""
    return {
        "id": v["id"],
        "name": v["name"],
        "en": v.get("english_name") or v.get("name"),
        "family": fam,
        "normalized": short,
        "designer": designer,
        "designerShort": designer.split("(")[0].strip() if designer else "—",
        "category": v.get("category") or "",
        "tags": json_list(v.get("tags")),
        "weights": wnames,
        "description": v.get("description") or "",
        "license": shop_lic,
        "licenseName": license_name,
        "licenseUrl": "",
        "licenseFileUrl": "",
        "licenseNotes": "",
        "licenseVerified": None,
        "purchaseUrl": None,
        "copyright": v.get("copyright") or "",
        "foundry": foundry_name,
        "brand": brand,
        "releaseYear": v.get("release_year"),
        "version": v.get("version") or "",
        "languages": json_list(v.get("languages")),
        "useCases": json_list(v.get("use_cases")),
        "charCount": char_count,
        "glyphCount": glyph_count,
        "viewCount": v.get("view_count") or 0,
        "foundryAvatar": DEFAULT_AVATAR,
    }


def lic_dir_map(lic_dir: Path):
    out = {}
    if not lic_dir.is_dir():
        return out
    for d in lic_dir.iterdir():
        if d.is_dir():
            out[d.name.lower()] = d
    return out


def pick_lic_dir(dmap, *names):
    for n in names:
        if not n:
            continue
        hit = dmap.get(str(n).lower())
        if hit:
            return hit
    return None


def org_entry_from_shop(s, ctx):
    short = family_short(s.get("family") or "")
    old_norm = s.get("normalized") or short
    aliases = []
    add_alias(aliases, old_norm)
    add_alias(aliases, str(old_norm).lower())
    d = pick_lic_dir(ctx["lic_dirs"], short, old_norm, str(old_norm).lower())
    info = None
    lic_path = None
    if d:
        info_path = d / "license-info.json"
        lic_path = d / "LICENSE"
        if info_path.exists():
            info = load(info_path)
        if not lic_path.exists():
            lic_path = None
    mir = (
        ctx["mirrors"].get(short)
        or ctx["mirrors"].get(str(old_norm).lower())
        or ctx["mirrors"].get(old_norm)
        or {}
    )
    raw_upstream = (
        mir.get("upstream")
        or (info or {}).get("licenseUrl")
        or s.get("licenseUrl")
        or None
    )
    upstream = raw_upstream if repo_like(raw_upstream) else None
    mirror_state = mir.get("mirror_state") or "absent"
    state = text_state(lic_path, info)
    sha = None
    body = None
    fetched = ctx["fetched"].get(d.name) if d else None
    if lic_path and lic_path.exists():
        raw = lic_path.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        body = raw.decode("utf-8", "replace")
        if fetched is None:
            fetched = ctx["fetched"].get(lic_path.parent.name)
    spdx = spdx_of(info, s)
    rfn = parse_rfn(body) if (spdx == "OFL-1.1" and body) else None
    lin = ctx["by_name"].get(s.get("name") or "")
    origin = build_origin(lin, ctx["owners"])
    offer = offer_of(mirror_state, info, upstream, has_text=bool(sha))
    files = []
    if offer == "source":
        files.append(
            {
                "kind": "archive",
                "label": "源文件归档",
                "format": "tar.gz",
                "href": ARCHIVE_HREF_PREFIX + short + ".tar.gz",
                "sha256": None,
                "staged": True,
            }
        )
    if upstream and str(upstream).startswith("http"):
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", str(upstream))).split("/")[0]
        files.append(
            {
                "kind": "upstream",
                "label": "上游 " + host,
                "format": "git",
                "href": upstream,
                "sha256": None,
            }
        )
    files.append(
        {
            "kind": "slice",
            "label": "网页切片包（自托管）",
            "format": "zip",
            "href": None,
            "status": "planned",
            "sha256": None,
        }
    )
    brand_slug = ((s.get("brand") or {}) or {}).get("slug")
    foundry_name = s.get("foundry") or ""
    if brand_slug:
        base_brand, base_foundry = brand_slug, foundry_name
    elif foundry_name:
        base_brand, base_foundry = foundry_name.lower(), foundry_name
    elif (s.get("name") or "") in ctx["dict_by_fontname"]:
        base_brand, base_foundry = ctx["dict_by_fontname"][s["name"]]
    else:
        base_brand, base_foundry = "unknown", ""
    lic_block = {
        "spdx": spdx,
        "textState": state,
        "sourceUrl": raw_upstream,
        "fetchedAt": fetched,
        "textSha256": sha,
        "verifiedAt": (info or {}).get("verifiedAt"),
        "rfn": rfn,
    }
    if origin:
        lic_block["origin"] = origin
    entry = {
        "norm": short,
        "name": s.get("name") or short,
        "en": s.get("en") or "",
        "aliases": aliases,
        "licenseName": s.get("licenseName") or (info or {}).get("type") or "授权待核",
        "license": lic_block,
        "foundry": base_foundry,
        "foundrySlug": base_brand,
        "offer": offer,
        "slice": "planned",
        "distribution": bool(
            (info or {}).get("distribution", s.get("license") == "免费商用")
        ),
        "shop": SHOP_HREF + short,
        "weights": weight_names(s.get("weights")),
        "mirror": {
            "state": mirror_state
            if mirror_state == "mirrored"
            else ("absent" if mirror_state == "skipped" else mirror_state),
            "feicode": mir.get("feicode_mirror"),
            "upstream": mir.get("upstream") or upstream,
            "syncedAt": None,
            "headSha": None,
        },
        "lineage": None,
        "files": files,
        "visitorNote": "",
        "family": s.get("family") or ("wenfeng-" + short),
    }
    lic_index = {
        "textKind": state if state in OFL_TEXT_STATES else "missing",
        "title": entry["licenseName"] or "许可原文",
        "evidence": {
            "source": (info or {}).get("verifiedBy")
            or ("上游仓原文" if state == "full" else "结构化记录"),
            "url": lic_block["sourceUrl"],
            "commit": None,
            "fetchedAt": fetched,
            "rule": None,
        },
    }
    text_payload = None
    if body:
        text_payload = {
            "norm": short,
            "title": lic_index["title"],
            "body": body,
            "textKind": lic_index["textKind"],
            "evidence": lic_index["evidence"],
        }
    return entry, lic_index, text_payload


def git_add_dates(repo: Path):
    dates = {}
    if not repo.is_dir():
        return dates
    import subprocess

    try:
        out = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "log",
                "--format=%as",
                "--name-only",
                "--diff-filter=A",
                "--",
                "licenses/",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except Exception:
        return dates
    cur = None
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", line):
            cur = line
        elif line.startswith("licenses/") and line.endswith("/LICENSE"):
            norm = line.split("/")[1]
            if norm not in dates and cur:
                dates[norm] = cur
    return dates


def apply_shop(report):
    fonts_path = SHOP_ROOT / "data" / "fonts.json"
    bak = SHOP_ROOT / "data" / "fonts.json.bak-catalog-membership-20261007"
    if not bak.exists():
        shutil.copy2(fonts_path, bak)
    fonts = load(fonts_path)
    vault_rows = load(HERE / "vault-catalog-gap-clean.json")
    foundries_doc = load(SHOP_ROOT / "data" / "foundries.json")
    foundry_list = foundries_doc.get("foundries") or []

    case_n = 0
    shmdt_n = 0
    have_ids = {f.get("id") for f in fonts}
    have_names = {f.get("name") for f in fonts}
    for f in fonts:
        fam = f.get("family") or ""
        short = family_short(fam)
        n = f.get("normalized") or ""
        if f.get("name") == "上海摩登体":
            if n != "shmdt":
                f["normalized"] = "shmdt"
                shmdt_n += 1
            continue
        if short and n != short and n.lower() == short.lower():
            f["normalized"] = short
            case_n += 1
        elif short and n.lower() != short.lower() and n:
            # leave real mismatches except 上海摩登 (handled)
            pass

    inserted = []
    for v in vault_rows:
        if v["id"] not in BDF_IDS:
            continue
        if v["id"] in have_ids or v["name"] in have_names:
            continue
        row = shop_row_from_vault(v, foundry_list)
        fonts.append(row)
        inserted.append(row["name"])
        have_ids.add(row["id"])
        have_names.add(row["name"])

    dump(fonts_path, fonts, indent=2)
    report["shop"] = {
        "count": len(fonts),
        "case_lower": case_n,
        "shmdt": shmdt_n,
        "bdf_inserted": inserted,
        "bak": str(bak.name),
    }
    return fonts


def load_org_ctx():
    mirrors_raw = load(LIC_ROOT / "data" / "source-mirrors.json")["fonts"]
    if isinstance(mirrors_raw, list):
        mirrors_list = mirrors_raw
    else:
        mirrors_list = list(mirrors_raw.values()) if isinstance(mirrors_raw, dict) else []
    mirrors = {}
    for m in mirrors_list:
        n = str(m.get("norm") or "")
        if n:
            mirrors[n] = m
            mirrors[n.lower()] = m
    lineage = load(SHOP_ROOT / "data" / "font-lineage.json")
    owners = owner_names(FOUNDRY_ROOT)
    dict_by_fontname = {}
    try:
        for entry in load(SHOP_ROOT / "data" / "foundries.json").get("foundries") or []:
            for fn in entry.get("fontNames") or []:
                dict_by_fontname[fn] = (
                    entry.get("id") or entry.get("slug") or "unknown",
                    entry.get("name") or entry.get("en") or fn,
                )
    except Exception:
        pass
    return {
        "mirrors": mirrors,
        "by_name": lineage.get("byName") or {},
        "owners": owners,
        "dict_by_fontname": dict_by_fontname,
        "fetched": git_add_dates(LIC_ROOT),
        "lic_dirs": lic_dir_map(LIC_ROOT / "licenses"),
    }


def apply_org(shop_fonts, report):
    bak_dir = ORG / "data" / "_bak-catalog-membership-20261007"
    bak_dir.mkdir(parents=True, exist_ok=True)
    for rel in (
        "data/samples-full.json",
        "samples.json",
        "data/licenses.json",
        "data/webfonts.json",
        "data/oss-packs.json",
        "data/norm-history.json",
    ):
        src = ORG / rel
        if src.exists() and not (bak_dir / src.name).exists():
            shutil.copy2(src, bak_dir / src.name)

    full_doc = load(ORG / "data" / "samples-full.json")
    fonts = full_doc["fonts"]
    licenses = load(ORG / "data" / "licenses.json")
    webfonts_doc = load(ORG / "data" / "webfonts.json")
    webfonts = webfonts_doc.get("fonts") or webfonts_doc
    oss_packs_doc = load(ORG / "data" / "oss-packs.json")
    oss_packs = oss_packs_doc.get("fonts") or oss_packs_doc
    prefixes = set(
        x.lower()
        for x in load(HERE / "oss-prefixes.json").get("prefixes") or []
    )
    overlay_dir = ORG / "data" / "font"
    text_dir = ORG / "data" / "license-text"
    text_dir.mkdir(parents=True, exist_ok=True)
    ctx = load_org_ctx()
    org_names = {o["name"] for o in fonts}
    taken_short = {str(o.get("norm") or "").lower(): o.get("name") for o in fonts}

    inserted = []
    for s in shop_fonts:
        if s["name"] in org_names:
            continue
        short = family_short(s.get("family") or "")
        occ = taken_short.get(short.lower())
        if occ:
            report.setdefault("org_insert_skip", []).append(
                {"name": s["name"], "short": short, "occ": occ}
            )
            continue
        entry, lic_index, text_payload = org_entry_from_shop(s, ctx)
        fonts.append(entry)
        org_names.add(s["name"])
        taken_short[short.lower()] = s["name"]
        inserted.append(s["name"])
        dump(overlay_dir / (entry["norm"] + ".json"), entry, indent=1)
        if entry["norm"] not in licenses:
            licenses[entry["norm"]] = lic_index
        if text_payload and not (text_dir / (entry["norm"] + ".json")).exists():
            dump(text_dir / (entry["norm"] + ".json"), text_payload, indent=None)
        short = entry["norm"]
        if short in prefixes and short not in webfonts:
            webfonts[short] = "full"

    # merge 寒蝉端黑 into 寒蝉端黑体
    hcdht = next((f for f in fonts if f.get("name") == "寒蝉端黑体"), None)
    clduan = next((f for f in fonts if f.get("name") == "寒蝉端黑"), None)
    merged = False
    if hcdht and clduan:
        aliases = list(hcdht.get("aliases") or [])
        add_alias(aliases, "Clduan")
        add_alias(aliases, "Hcdht")
        add_alias(aliases, "clduan")
        add_alias(aliases, "寒蝉端黑")
        hcdht["aliases"] = aliases
        hcdht["norm"] = "hcdht"
        hcdht["family"] = "wenfeng-hcdht"
        hcdht["shop"] = SHOP_HREF + "hcdht"
        if clduan.get("offer") == "source":
            hcdht["offer"] = "source"
            hcdht["mirror"] = clduan.get("mirror") or hcdht.get("mirror")
        seen_href = {
            (x.get("kind"), x.get("href")) for x in (hcdht.get("files") or [])
        }
        files = list(hcdht.get("files") or [])
        for x in clduan.get("files") or []:
            key = (x.get("kind"), x.get("href"))
            if key in seen_href:
                continue
            files.append(x)
            seen_href.add(key)
        hcdht["files"] = files
        w = weight_names(hcdht.get("weights"))
        for extra in weight_names(clduan.get("weights")):
            if extra not in w:
                w.append(extra)
        hcdht["weights"] = w
        fonts = [f for f in fonts if f.get("name") != "寒蝉端黑"]
        dump(overlay_dir / "hcdht.json", hcdht, indent=1)
        if "hcdht" not in licenses:
            licenses["hcdht"] = licenses.get("Hcdht") or licenses.get("Clduan") or {
                "textKind": "full",
                "title": hcdht.get("licenseName") or "许可原文",
            }
        merged = True

    # 上海摩登 + remaining CamelCase org norms → family short
    moves = []
    taken = {}
    for f in fonts:
        taken[str(f.get("norm") or "").lower()] = f.get("name")
    for f in fonts:
        short = family_short(f.get("family") or "")
        old = f.get("norm") or ""
        if f.get("name") == "上海摩登体":
            short = "shmdt"
            f["family"] = "wenfeng-shmdt"
        if not short:
            continue
        if old == short:
            f["shop"] = SHOP_HREF + short
            continue
        occ = taken.get(short.lower())
        if occ and occ != f.get("name"):
            report.setdefault("org_dest_skip", []).append(
                {"name": f.get("name"), "old": old, "new": short, "occ": occ}
            )
            continue
        aliases = list(f.get("aliases") or [])
        add_alias(aliases, old)
        f["aliases"] = aliases
        f["norm"] = short
        f["shop"] = SHOP_HREF + short
        if not str(f.get("family") or "").startswith("wenfeng-"):
            f["family"] = "wenfeng-" + short
        elif family_short(f["family"]).lower() == short.lower():
            f["family"] = "wenfeng-" + short
        taken.pop(old.lower(), None)
        taken[short.lower()] = f.get("name")
        dump(overlay_dir / (short + ".json"), f, indent=1)
        if old in licenses and short not in licenses:
            licenses[short] = licenses[old]
        old_text = None
        for cand in (text_dir / (old + ".json"), text_dir / (old.lower() + ".json")):
            if cand.exists():
                old_text = cand
                break
        if old_text and not (text_dir / (short + ".json")).exists():
            payload = load(old_text)
            payload["norm"] = short
            dump(text_dir / (short + ".json"), payload, indent=None)
        if old.lower() in webfonts and short not in webfonts:
            webfonts[short] = webfonts[old.lower()]
        if old.lower() in oss_packs and short not in oss_packs:
            oss_packs[short] = oss_packs[old.lower()]
        moves.append({"name": f.get("name"), "old": old, "new": short})

    full_doc["fonts"] = fonts
    full_doc["generated"] = TODAY
    full_doc["comment"] = (
        "2026-10-07 目录与店面一致：店面有的都进本站；6 款 BDF 入库；"
        "寒蝉端黑并进寒蝉端黑体。无包无库的 26 条仍只在本站。"
    )
    full_doc["coverage"] = dict(full_doc.get("coverage") or {})
    full_doc["coverage"]["shop_fonts"] = len(shop_fonts)
    full_doc["coverage"]["sample_fonts"] = len(fonts)

    dump(ORG / "data" / "samples-full.json", full_doc, indent=1)
    slim = {
        "generated": TODAY,
        "purpose": full_doc.get("purpose"),
        "comment": "瘦目录（首页/列表/卡片）；详情页按需取 data/font/<norm>.json",
        "coverage": full_doc["coverage"],
        "fonts": [slim_of(f) for f in fonts],
    }
    dump(ORG / "samples.json", slim, compact=True)

    # licenses two-pass: canonical new keys first
    new_lic = {}
    for f in fonts:
        n = f.get("norm")
        if n and n not in new_lic:
            new_lic[n] = licenses.get(n) or licenses.get(str(n).lower()) or {
                "textKind": (f.get("license") or {}).get("textState") or "missing",
                "title": f.get("licenseName") or "许可原文",
            }
    for k, v in licenses.items():
        if k.lower() not in {x.lower() for x in new_lic}:
            new_lic[k] = v
    dump(ORG / "data" / "licenses.json", new_lic, indent=1)

    webfonts_doc["fonts"] = webfonts
    dump(ORG / "data" / "webfonts.json", webfonts_doc, indent=1)
    oss_packs_doc["fonts"] = oss_packs
    dump(ORG / "data" / "oss-packs.json", oss_packs_doc, indent=1)

    hist_path = ORG / "data" / "norm-history.json"
    hist = load(hist_path) if hist_path.exists() else {"maps": []}
    hist["generated"] = TODAY
    hist.setdefault("maps", []).extend(moves)
    dump(hist_path, hist, indent=1)

    report["org"] = {
        "count": len(fonts),
        "inserted": len(inserted),
        "inserted_names_head": inserted[:20],
        "clduan_merged": merged,
        "moves": len(moves),
        "bak": str(bak_dir),
    }
    shop_names = {s["name"] for s in shop_fonts}
    org_names = {o["name"] for o in fonts}
    report["gap_after"] = {
        "shop_only": sorted(shop_names - org_names),
        "org_only": sorted(org_names - shop_names),
        "shop": len(shop_fonts),
        "org": len(fonts),
    }
    return fonts


def main():
    report = {"generated": TODAY}
    shop_fonts = apply_shop(report)
    apply_org(shop_fonts, report)
    out = HERE / "catalog-membership-unify.json"
    dump(out, report, indent=1)
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
