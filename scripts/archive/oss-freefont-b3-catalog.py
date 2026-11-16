import json
from pathlib import Path

root = Path("/Users/feibisi-studio/Projects/fonts-front/data")
chars = json.loads(Path("/Users/feibisi-studio/Projects/fonts-packages/logs/freefont-b3-chars.json").read_text())
ids = {
    "Fzss": "6edd444a-6ad8-4900-aa2a-fe39767a6ede",
    "Fzfs": "0e4a6f1a-d579-44f5-bd20-64d035050b1e",
    "Fzkt": "80a76c8e-d7e2-428f-a3a4-f6abad4c5168",
    "Fzht": "b4dd542d-d378-4357-bc81-9254a41d35fb",
    "Misn": "9274da30-db3a-4f75-8aa5-43d51fcf9daa",
    "Hyma": "cf168beb-bd70-4989-8e21-530a3178c544",
    "Hymb": "3277ffd3-ed09-45c1-8df2-e9c189f3f1ef",
    "Qzss": "090f94e8-b1cc-4c16-aa21-f6693de0c0fc",
    "Qzkt": "a6cd7642-0003-469f-83ce-666955f4b492",
    "Lnsw": "25430e57-734e-4d70-b8f5-dcb5de01e8ff",
    "Mdmz": "49feea55-1ff6-41fc-839c-3f9986df918c",
    "Xcdz": "39a52c13-4618-4864-89df-d3c6336bc038",
    "Xccx": "73d8769d-fd8a-420a-a1d3-e4572021fe58",
    "Xcld": "26abf312-2441-447a-a66d-e3d3c01188f4",
}

def brand(name, slug, site, desc):
    return {"name": name, "slug": slug, "logoUrl": "", "avatarUrl": "", "website": site, "description": desc}

founder = brand("方正字库", "founder", "https://www.foundertype.com", "方正书宋、仿宋、楷体、黑体。可免费商用，不可修改。")
xiaomi = brand("小米", "xiaomi", "https://www.mi.com", "小米 MiSans。可免费商用。")
hana = brand("GlyphWiki", "hanamin", "http://glyphwiki.org/", "花园明朝。可免费使用、修改、再分发。")
cns = brand("全字库", "cns11643", "https://data.gov.tw/license", "全字库正宋、正楷。开放政府数据授权 1.0。")
line = brand("LY Corporation", "lineseed", "https://github.com/line/seed", "LINE Seed TW。字内写 OFL 1.1。")
aqua = brand("Aqua", "aqua", "https://github.com/max32002", "Aqua / max32002")
xiang = brand("香萃", "xiangcui", "https://github.com/Miiiller", "香萃。")
nofix = "可免费商用。不可修改字体文件，不可再分发。"
ofl = "可免费商用、可修改。修改版须改名，不得单独售卖字体文件。"
freeuse = "可免费使用、修改、再分发。"
ogdl = "可免费商用、可修改、可再分发，须保留授权声明。"
unknown = "字内没有许可正文。同目录的香萃刻宋写的是 OFL 1.1。这一款只记免费商用，修改条款没有写在文件里。"
adobe = "字内版权仍是 Adobe 2017，保留名 Source，没有另写 OFL。是思源的改作。"

meta = {
    "Fzss": dict(name="方正书宋简体", en="FZ ShuSong", cat="宋体", weights=["Regular"], designer="方正", foundry="方正字库", brand=founder, lic="免费商用，不可修改", notes=nofix, verified=True, url="https://www.foundertype.com", copy="Copyright 2015 Beijing Founder Electronics", langs=["简体中文"], uses=["正文"], desc="方正书宋简体。方正公布这四款基础字可免费商用，不可修改字体文件，不可单独再分发。不是 OFL。"),
    "Fzfs": dict(name="方正仿宋简体", en="FZ FangSong", cat="宋体", weights=["Regular"], designer="方正", foundry="方正字库", brand=founder, lic="免费商用，不可修改", notes=nofix, verified=True, url="https://www.foundertype.com", copy="Copyright 2015 Beijing Founder Electronics", langs=["简体中文"], uses=["正文"], desc="方正仿宋简体。可免费商用，不可修改字体文件，不可单独再分发。不是 OFL。"),
    "Fzkt": dict(name="方正楷体简体", en="FZ Kai", cat="手写体", weights=["Regular"], designer="方正", foundry="方正字库", brand=founder, lic="免费商用，不可修改", notes=nofix, verified=True, url="https://www.foundertype.com", copy="Copyright 2015 Beijing Founder Electronics", langs=["简体中文"], uses=["正文"], desc="方正楷体简体。可免费商用，不可修改字体文件，不可单独再分发。不是 OFL。"),
    "Fzht": dict(name="方正黑体简体", en="FZ Hei", cat="无衬线字体", weights=["Regular"], designer="方正", foundry="方正字库", brand=founder, lic="免费商用，不可修改", notes=nofix, verified=True, url="https://www.foundertype.com", copy="Copyright 2017 Beijing Founder Electronics", langs=["简体中文"], uses=["正文"], desc="方正黑体简体。可免费商用，不可修改字体文件，不可单独再分发。不是 OFL。"),
    "Misn": dict(name="小米 MiSans", en="MiSans", cat="无衬线字体", weights=["Light", "Regular", "Medium", "Bold"], designer="小米", foundry="小米", brand=xiaomi, lic="免费商用", notes="小米公布可免费商用。字内没有写明能否修改、能否再分发。", verified=False, url="https://www.mi.com", copy="Copyright 2020-2023 Beijing Xiaomi Mobile Software", langs=["简体中文", "繁体中文"], uses=["正文"], desc="小米 MiSans。小米公布可免费商用。字内没有 OFL 正文，也没有写明能否修改。放了细、常规、中、粗。"),
    "Hyma": dict(name="花园明朝 A", en="HanaMin A", cat="宋体", weights=["Regular"], designer="GlyphWiki", foundry="GlyphWiki", brand=hana, lic="可免费使用、修改、再分发", notes=freeuse, verified=False, url="http://glyphwiki.org/", copy="Created by GlyphWiki", langs=["简体中文", "繁体中文", "日文"], uses=["正文"], desc="花园明朝 A。GlyphWiki 制作。公开说明可自由使用、修改、再分发。不是 OFL。这一档覆盖基本区汉字。"),
    "Hymb": dict(name="花园明朝 B", en="HanaMin B", cat="宋体", weights=["Regular"], designer="GlyphWiki", foundry="GlyphWiki", brand=hana, lic="可免费使用、修改、再分发", notes=freeuse, verified=False, url="http://glyphwiki.org/", copy="Created by GlyphWiki", langs=["简体中文", "繁体中文", "日文"], uses=["正文"], desc="花园明朝 B。扩展区为主，基本区汉字很少。和 A 是同一套的另一平面。"),
    "Qzss": dict(name="全字库正宋体", en="TW-Sung", cat="宋体", weights=["Regular"], designer="国家发展委员会", foundry="全字库", brand=cns, lic="台湾开放政府数据授权条款 1.0", notes=ogdl, verified=True, url="https://data.gov.tw/license", copy="Copyright 2018 National Development Council. Open Government Data License, version 1.0", langs=["繁体中文"], uses=["正文"], desc="全字库正宋体。字内版权是台湾国家发展委员会，授权条款是开放政府数据授权 1.0。可免费商用、可修改、可再分发，须保留授权声明。"),
    "Qzkt": dict(name="全字库正楷体", en="TW-Kai", cat="手写体", weights=["Regular"], designer="国家发展委员会", foundry="全字库", brand=cns, lic="台湾开放政府数据授权条款 1.0", notes=ogdl, verified=True, url="https://data.gov.tw/license", copy="Copyright 2018 National Development Council. Open Government Data License, version 1.0", langs=["繁体中文"], uses=["正文"], desc="全字库正楷体。授权条款与正宋体相同，开放政府数据授权 1.0。"),
    "Lnsw": dict(name="LINE Seed TW", en="LINE Seed TW", cat="无衬线字体", weights=["Thin", "Regular", "Bold", "ExtraBold"], designer="LY Corporation", foundry="LY Corporation", brand=line, lic="SIL Open Font License 1.1", notes=ofl, verified=True, url="https://scripts.sil.org/OFL", copy="Copyright LY Corporation", langs=["繁体中文"], uses=["正文"], desc="LINE Seed TW。字内写着 OFL 1.1，版权行是 LY Corporation。LY 公开的 LINE Seed 条款是另一份免费商用许可。放了特细、常规、粗、特粗。"),
    "Mdmz": dict(name="莫大毛笔", en="Bakudai", cat="手写体", weights=["Light", "Regular", "Medium", "Bold"], designer="Max Yao", foundry="Aqua", brand=aqua, lic="SIL Open Font License 1.1", notes=ofl, verified=True, url="https://github.com/max32002", copy="Copyright Chun yu Yao. Based on Aoyagi Kouzan.", langs=["繁体中文", "简体中文"], uses=["标题"], desc="莫大毛笔。字内家族名 Bakudai，基于衡山毛笔。和库里的爆呆字符数相同，中文名不同，另列一款。OFL 1.1。放了细、常规、中、粗。"),
    "Xcdz": dict(name="香萃打字机", en="Xiangcui Typewriter W15", cat="Mono", weights=["Regular"], designer="香萃", foundry="香萃", brand=xiang, lic="免费商用", notes=unknown, verified=False, url="https://github.com/Miiiller", copy="", langs=["简体中文"], uses=["正文"], desc="香萃打字机 W15。字内没有许可正文。同目录的香萃刻宋写的是 OFL 1.1。"),
    "Xccx": dict(name="香萃潮汐宋", en="Xiangcui Tide Song W15", cat="宋体", weights=["Regular"], designer="香萃", foundry="香萃", brand=xiang, lic="免费商用", notes=unknown, verified=False, url="https://github.com/Miiiller", copy="", langs=["简体中文"], uses=["正文"], desc="香萃潮汐宋 W15。字内没有许可正文。同目录的香萃刻宋写的是 OFL 1.1。"),
    "Xcld": dict(name="香萃零度黑", en="Xiangcui Zero Hei", cat="无衬线字体", weights=["Regular"], designer="香萃", foundry="香萃", brand=xiang, lic="免费商用", notes=adobe, verified=False, url="https://github.com/Miiiller/Xiangcui-ZeroHei", copy="Copyright 2017 Adobe Systems Incorporated. Reserved Font Name Source.", langs=["简体中文"], uses=["正文"], desc="香萃零度黑 2.0。字内版权仍是 Adobe 2017，保留名 Source，没有另写 OFL。是思源的改作。"),
}

fonts = json.loads((root / "fonts.json").read_text())
have = {x["family"] for x in fonts}
for norm, m in meta.items():
    family = "wenfeng-" + norm.lower()
    if family in have:
        raise SystemExit("dup " + family)
    reg = chars[norm]["Regular"]
    fonts.append({
        "id": ids[norm],
        "name": m["name"],
        "en": m["en"],
        "family": family,
        "normalized": norm,
        "designer": m["designer"],
        "designerShort": m["designer"],
        "category": m["cat"],
        "tags": [],
        "weights": m["weights"],
        "description": m["desc"],
        "license": "免费商用",
        "licenseName": m["lic"],
        "licenseUrl": m["url"],
        "licenseFileUrl": "",
        "licenseNotes": m["notes"],
        "licenseVerified": m["verified"],
        "purchaseUrl": None,
        "copyright": m["copy"],
        "foundry": m["foundry"],
        "brand": m["brand"],
        "releaseYear": None,
        "version": "1",
        "languages": m["langs"],
        "useCases": m["uses"],
        "charCount": reg["chars"],
        "glyphCount": reg["glyphs"],
        "viewCount": 0,
    })
(root / "fonts.json").write_text(json.dumps(fonts, ensure_ascii=False, indent=2) + "\n")

foundries = json.loads((root / "foundries.json").read_text())
byid = {x["id"]: x for x in foundries["foundries"]}
for fid, names in {
    "founder": ["方正书宋简体", "方正仿宋简体", "方正楷体简体", "方正黑体简体"],
    "xiaomi": ["小米 MiSans"],
    "xiangcui": ["香萃打字机", "香萃潮汐宋", "香萃零度黑"],
}.items():
    byid[fid].setdefault("fontNames", [])
    for n in names:
        if n not in byid[fid]["fontNames"]:
            byid[fid]["fontNames"].append(n)
add = [
    {"id": "hanamin", "name": "GlyphWiki", "en": "HanaMin", "short": "花园", "website": "http://glyphwiki.org/", "aliases": ["花园明朝", "HanaMin"], "fontNames": ["花园明朝 A", "花园明朝 B"], "kind": "author", "openSource": True, "claimed": False, "description": "花园明朝。可免费使用、修改、再分发。不是 OFL。"},
    {"id": "cns11643", "name": "全字库", "en": "CNS 11643", "short": "全字库", "website": "https://data.gov.tw/license", "aliases": ["国家发展委员会", "TW-Sung", "TW-Kai"], "fontNames": ["全字库正宋体", "全字库正楷体"], "kind": "foundry", "openSource": True, "claimed": False, "description": "全字库正宋、正楷。开放政府数据授权 1.0。"},
    {"id": "lineseed", "name": "LY Corporation", "en": "LINE Seed", "short": "LINE", "website": "https://github.com/line/seed", "aliases": ["LINE Seed"], "fontNames": ["LINE Seed TW"], "kind": "brand", "openSource": False, "claimed": False, "description": "LINE Seed TW。字内写 OFL 1.1。LY 公开条款是另一份免费商用许可。"},
]
for fnd in add:
    if fnd["id"] in byid:
        raise SystemExit("foundry " + fnd["id"])
    foundries["foundries"].append(fnd)
(root / "foundries.json").write_text(json.dumps(foundries, ensure_ascii=False, indent=2) + "\n")

lin = json.loads((root / "font-lineage.json").read_text())
by = lin["byName"]
extra = {
    "莫大毛笔": {"ownerId": "aqua", "makerId": "aqua", "relation": "fork", "licenseFollows": "inherit", "upstreamOwnerId": "aoyagi-kouzan", "upstreamName": "衡山毛笔"},
    "香萃零度黑": {"ownerId": "xiangcui", "makerId": "xiangcui", "group": "source-han-sans", "relation": "fork", "licenseFollows": "inherit", "upstreamOwnerId": "adobe", "upstreamName": "思源黑体"},
    "花园明朝 B": {"ownerId": "hanamin", "makerId": "hanamin", "relation": "locale", "licenseFollows": "inherit", "upstreamOwnerId": "hanamin", "upstreamName": "花园明朝 A"},
}
for k, v in extra.items():
    if k in by:
        raise SystemExit("lin " + k)
    by[k] = v
(root / "font-lineage.json").write_text(json.dumps(lin, ensure_ascii=False, indent=2) + "\n")
print("fonts", len(fonts))
