# fonts-packages

这个仓只做字体包：拆包、子集、上传。不改店面目录，不改 wenfeng.org 条目，不改 `/api/css` 的 `fontFamily`。

## 包放哪

- 桶：`oss://wenfeng-fonts`（广州）。公开地址：`https://cn.windfonts.com/fonts-packages/{目录}/{字重}/{子集}/result.css`。
- 目录名是店面 `normalized` 的**小写**。不是嵌入 `family` 短码。
- 例：霞鹜文楷 Bright 的目录仍是 `xwbright`。2026-10-07 店面 `family` 是 `wenfeng-xwwkb`。不要为了新短码去改名、搬目录或删旧目录。
- 2026-10-06 起混写目录（`Xwbright`）对公开 URL 是 404。新上传用小写。删混写要 wenpai 的删除权限，不要在本机猜钥匙。

## 不要做

- 不要把 `AGENTS.md`、`CLAUDE.md`、说明文档上传进桶。
- 不要用整树覆盖去「对齐」店面 `fonts.json`。包清单和店面目录是两份名单。
- 不要把 app 静态页传到这个桶。app 页面在杭州桶 `wenfeng-web-hz`，由 `fonts-front` 的 `scripts/deploy-web-hz.sh` 发。广州 `wenfeng-web` 不是访客在看的站。
- 不要改 `result.css` 里的 `font-family: "WF-{Normalized}"`。站点嵌入用的是另一层 `wenfeng-*`，在店面和 vault，不在这个文件里改。
