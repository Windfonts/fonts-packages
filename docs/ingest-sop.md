# 字体入库 SOP（fonts-packages → OSS）

本仓只做一件事：把源字体变成 OSS 上的 webfont 包。**不改店面目录、不改 wenfeng.org 条目、不改 `/api/css` 的 `fontFamily`**（见 `AGENTS.md` / `CLAUDE.md`，红线优先级高于 `README.md`——README 已过时）。

产物落点：`oss://wenfeng-fonts`（广州），公开地址 `https://cn.windfonts.com/fonts-packages/{目录}/{字重}/{子集}/result.css`。

## 0. 前置准备

```bash
npm install
pip3 install fonttools openai brotli
cp .env.example .env   # 填 OSS_* 和 AI key
```

`.env` 关键项：

| 变量 | 说明 |
|---|---|
| `OSS_ACCESS_KEY_ID` / `OSS_ACCESS_KEY_SECRET` / `OSS_BUCKET=wenfeng-fonts` / `OSS_REGION=oss-cn-guangzhou` / `OSS_ENDPOINT` | 上传凭据 |
| `OSS_BASE_PATH=fonts-packages/` | OSS 前缀，**必须保持此值**，与生产一致 |
| `OSS_UPLOAD_DIRS=./dist,./metadata` | upload.js 默认值 |
| `OSS_CDN_DOMAIN=https://cn.windfonts.com` | urls.json 里写 CDN 地址 |
| `OPENAI_API_KEY` 或 `ARK_API_KEY`，`OPENAI_BASE_URL`/`ARK_BASE_URL`，`OPENAI_MODEL`/`ARK_MODEL` | analyze-fonts.py 的 AI 命名/元数据补全；不配则跑降级模式 |
| `SUBSET_ONLY=full` 等 | 可选，只产指定子集版本，省时间/磁盘 |

## 1. 源字体入位

放入 `fonts/`，两种结构都支持：

```
fonts/{Norm}/{Weight}.ttf        # 家族目录结构（推荐）
fonts/{FontName}.ttf             # 独立字体（兼容旧模式）
```

- `{Norm}` = 未来的 OSS 目录名（`normalized`），**保持现有大小写**，小写化由 upload.js 统一做。
- `{Weight}` = **文件名 stem 原样**作为字重名（`Regular.ttf` → `Regular`）。字重名不做自动映射转换，想改名就改文件名。
- 只收 `.ttf`/`.otf` 进子集和转换；analyze 阶段也认 woff/woff2 但后续不处理。
- **语种准入**：**禁收韩语（KR）字体，保留日文（JP）字体**。入库前剔除 KR 字库，保留 JP 及简繁 CJK/西文字库。
- `fonts/`、`dist/`、`fonts-subset/`、`metadata/`、`staging/` 全部 gitignore，不入库。

## 2. 元信息分析 → `metadata/font-mapping.json`

```bash
python3 python-scripts/analyze-fonts.py          # 全量
python3 python-scripts/analyze-fonts.py test 3   # 只跑前 3 个，试 AI/流程
python3 python-scripts/analyze-fonts.py inspect fonts/Xxx/Regular.ttf  # 单文件看 name 表
```

产物：

- `metadata/font-mapping.json` — convert.js 的命名依据
- `metadata/font-analysis.json` / `.csv` — 字符统计报告

要点：

- `normalized_name` **被强制等于 `fonts/` 目录名**（代码里写死），AI 改不了它。
- `font_family` 规则：Regular/Normal 字重 → `WF-{Norm}`；其他字重 → `WF-{Norm}-{Weight}`。
- AI 只补 designer/copyright/category/license 等元数据字段；没配 key 时降级模式仍能出 mapping，只是字段空。
- **小批量或限流确定性兜底**：**小批量（≤20 款）或 AI 限流尾项，直接用 `TTFont` `name` 表 + 权威档案确定性补齐**，**禁止死等 AI 额度**。
- 字体名映射查不到时 convert.js 会 warn 并回退用目录名——**上线前检查日志里没有成片 "未找到映射"**。

### `font-mapping.json` 格式

顶层 key = `fonts/` 目录名；每个家族一个对象：

```jsonc
{
  "{Norm}": {
    "normalized_name": "{Norm}",          // = 目录名
    "font_family": "WF-{Norm}",           // 家族级 family
    "original_name": "...",
    "english_name": "...", "chinese_name": "...",
    "designer": "...", "foundry": "...", "release_year": null,
    "category": "...", "font_category": "...", "style": "...",
    "copyright": "...", "license": "...", "license_type": "...",
    "version": "...", "description": "...",
    "tags": [], "font_tags": [], "languages": [], "use_cases": [],
    "weights": {
      "{Weight}": {                        // key = 文件名 stem
        "font_family": "WF-{Norm}[-{Weight}]",
        "weight_name": "{Weight}",
        "font_weight": 400,                // 由字重名推断的 CSS font-weight
        "versions": {
          "original": {
            "file": "Regular.ttf",
            "char_count": 0,               // 0 或缺文件 = 空包，assertPublishable 会拒
            "glyph_count": 0,
            "subfamily_name": "...",
            "typographic_subfamily": "..."
          }
        }
      }
    }
  }
}
```

## 3. 子集化 → `fonts-subset/`

```bash
python3 python-scripts/create-font-subsets.py
SUBSET_ONLY=full python3 python-scripts/create-font-subsets.py   # 只出 full（full=直接 copy，不子集）
```

产物：`fonts-subset/{Norm}/{Weight}/{Weight}-{suffix}.ttf`，suffix ∈ `full` / `en` / `zh` / `zh-common`（约 3500 常用字）。

- `full` 档不做 subset，是 copy——文件大，全量入库才需要。
- 子集为空（cmap 为空）的版本会被跳过并告警。

## 4. 转换分包 → `dist/`

```bash
node scripts/convert.js
```

- 优先读 `fonts-subset/`（存在即用，处理完自动删除该目录）；不存在才退回 `fonts/` 原始字体。
- 输出 `dist/{Norm}/{Weight}/{version}/{N.woff2, result.css}`：
  - **`version` 维度来自文件名后缀**（`-full/-en/-zh-common/-zh`），不是 preset。`presets[]` 只剩一个 `standard`（70KB 分片），只在非子集模式下作为兜底目录名。
  - `result.css` 内 `font-family` 规则：Regular/Normal → `WF-{Norm}`，其他 → `WF-{Norm}-{Weight}`。**不要改这个文件里的 `WF-*` 名**。
- 结束自动清理 `index.proto` / `reporter.bin`。

也可以一条龙：`npm run build`（= analyze + subset + convert），`npm run clean` 清产物。

## 5. 只入库部分字体（park 机制）

`fonts/` 里已有上百个家族时，analyze/subset/convert 会扫全部。历史批次的做法（`scripts/archive/oss-batch1-build.sh`）：

1. 把不在本批的 `fonts/{Norm}/` 临时 `mv` 到旁边的 park 目录（如 `_oss_batch_park/` 或 `~/Projects/_fonts_park/`）；
2. 跑 analyze → subset → convert → upload；
3. 上传后 `dist/{Norm}/` 可删；源字体去留自定——`fonts/` 本身 gitignore，历史批次习惯把已入库的源移到 `_fonts_park` 类 staging 归档。

`SUBSET_ONLY=full` 可进一步只出 full 档。手工单字体入库时同理：只留目标家族目录再跑流水线，跑完恢复其余目录。

## 6. 上传 OSS

```bash
OSS_DRY_RUN=true node scripts/upload.js   # 先干跑，看 remote path 对不对
node scripts/upload.js
```

- `OSS_UPLOAD_DIRS` 默认 `./dist,./metadata`：dist 树 → `fonts-packages/{norm小写}/{Weight}/{version}/`；metadata → `fonts-packages/metadata/`。
- 首段目录名**强制小写**（防 `Xwbright/` 和 `xwbright/` 双树）；字重、version 段保持原样。
- Cache-Control：woff2/css/json 包一年 immutable；`metadata/` 路径 5 分钟。
- 并发 10，失败重试 3 次指数退避；有失败 exit 1。
- 跑完写 `dist/urls.json`（family → weight → subset → css/chunks 的 CDN URL 映射）。

### 上传后自检

```bash
curl -sI "https://cn.windfonts.com/fonts-packages/{norm小写}/{Weight}/{version}/result.css" | head -3
```

确认 200 且 `font-family` 是 `WF-*`。目录必须全小写——混写目录对公开 URL 是 404（2026-10-06 起）。

## 7. preview-shop 预览包（可选）

店面卡片/详情页的小字预览包，不走全量分包：

```bash
python3 scripts/build-preview-pack.py --pack shop --norm {Norm} --weight {Weight}
node scripts/upload-preview-shop.js          # dry-run
node scripts/upload-preview-shop.js --apply  # 上传 staging/preview-shop-oss → {norm}/{Weight}/preview-shop/
```

`config/preview-packs.json` 定义 pack 枚举（shop/card/yong）。

### 7.1 OG 分享图资产（og/）

店面/社媒分享图（og-a/b/d、banner、cover、yong 等 webp + yong svg）产物在
`fonts-packages/{norm}/og/`。批量生成器与渲染管线在 modiqi 仓
`tools/wpfonts-preview/og-layouts/gen-batch.mjs`（Satori/ImageResponse，
消费 `og-coverage.json` 预检结果）；上传用本仓 `scripts/upload-og-assets.js`
（webp+svg → `{norm}/og/`，默认 dry-run，`--apply` 上传，`--only` 单字体，
`--src` 指定产物目录）。

**硬约束：渲染源不能是 CFF2 表的字体**（Satori/resvg 报
`Font doesn't contain TrueType or CFF outlines`）。CFF2 可变字体要先静态化，
且实例化后表仍是 CFF2——需要换 CFF(1) 静态实例（先例：syhtxs 思源黑体像素
用 `fonts/syhtcn/SourceHanSansCN-Regular.otf` 替代渲染，2026-11-21）。
入库前用 `fontTools` 查 `'CFF2' in TTFont(path)` 预检；BDF/位图字体同样不可渲染。

## 8. 入库记录（必做）

每个新字体在 `scripts/` 留一份 `{norm}-map.json`，格式见 `scripts/yzdr-map.json`：来源 URL、tag、sha256、license、family/短码、glyphCount、nameNote。**入库后提交这个文件**，它是这批 OSS 包的台账。

历史批次脚本已归档到 `scripts/archive/`（`oss-*`、`lxgw-*`、`oss-unify-20261007/` 批处理，以及 `fix-*`/`offline-*`/`republish-*` vault prod.db 一次性修复）——**不是常驻流程，不要照抄重跑**；`*-map.json` 台账留在 `scripts/` 根。

唯一例外是 `scripts/normalize-pack-case.js`：OSS 上混写目录小写化工具，默认 dry-run，`--go` 执行、`--only={norm}` 单个、`--merge-only` 只合并不删（桶 ACL 可能拒删）。

## 9. 下游（不在本仓做）

OSS 包上线 ≠ 店面可用。后续在各自仓库：

- **fonts-vault**：`prod.db` 登记字体行（先例 `scripts/register-yzdr.js`、`register-oss-batch1.js`）、必要时 `family-aliases.json`。
- **fonts-front**：店面 `fonts.json` 条目。
- 三个名字系统（`normalized` 小写 / `family=wenfeng-{短码}` / `norm` 短码）可互不相同，靠别名衔接；**不要为新短码改 OSS 目录名**。

## 红线（摘自 AGENTS.md）

- 不上传 `AGENTS.md`/`CLAUDE.md`/说明文档进桶。
- 不用整树覆盖对齐店面 `fonts.json`。
- 不把 app 静态页传进 `wenfeng-fonts`（app 页在杭州桶 `wenfeng-web-hz`，由 fonts-front 发）。
- 不改 `result.css` 里的 `font-family: "WF-{Normalized}"`。
- 不为新 `family` 短码去改名/搬目录/删旧目录；删混写目录需要 wenpai 的删除权限。
- 上传 OSS / 改 prod.db 前先确认人批；本 SOP 的干跑（`OSS_DRY_RUN`、`upload-preview-shop.js`、`normalize-pack-case.js`）除外。
