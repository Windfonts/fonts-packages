# @windfonts/chinese-fonts

中文 Web 字体集合，提供可直接使用的 CDN CSS 链接与完整许可元数据。通过简单 API 或按字体模块导入，即可在浏览器或 SSR 环境中加载中文字体。

## 安装

```bash
npm i @windfonts/chinese-fonts
# 或
yarn add @windfonts/chinese-fonts
# 或
pnpm add @windfonts/chinese-fonts
```

## 快速开始

### 通过 API 动态加载

```js
const { loadFont } = require('@windfonts/chinese-fonts');

(async () => {
  await loadFont('Albbpht-Bold', { subset: 'zh-common', preload: true });
})();
```

### 按字体模块导入（tree-shaking）

```js
const AlbbphtBold = require('@windfonts/chinese-fonts/fonts/Albbpht-Bold');

(async () => {
  await AlbbphtBold({ subset: 'zh-common' });
})();
```

```ts
import AlbbphtBold from '@windfonts/chinese-fonts/fonts/Albbpht-Bold';
await AlbbphtBold({ subset: 'zh-common' });
```

加载成功后，页面会注入对应的字体 CSS。根据字体的 `family` 使用：

```ts
import { getFontInfo } from '@windfonts/chinese-fonts';
const family = getFontInfo('Albbpht-Bold')?.family;
```

```css
body { font-family: 'Albbpht', system-ui, sans-serif; }
```

## 运行环境与默认行为

- 浏览器环境自动向 `document.head` 注入 `<link rel="stylesheet" href="...">`。
- Node/SSR 环境返回 CSS 链接字符串，不注入 DOM，可自行写入到 HTML。
- 子集默认选择优先级：`zh-common` > `zh` > `en` > 第一个可用子集。
- 传入 `preload: true` 会额外注入 `<link rel="preload" as="style">`。

## 常用 API

```ts
import {
  fonts,
  loadFont,
  createFontLoader,
  getAllFonts,
  getFontInfo,
  getFontCSS,
  getFontSubsets,
  getFontChunks,
  getLicenseUrl,
  getLicenseType,
  getUsageRights,
  isCommercialUseAllowed,
} from '@windfonts/chinese-fonts';
```

- `loadFont(fontName, options)` 加载并返回 CSS 链接。
- `createFontLoader(fontName)` 返回 `FontLoader`，支持 `loader(options) / loader.load()`、`loader.getCSS()`、`loader.getSubsets()`、`loader.info`。
- `getAllFonts()` 返回可用字体名列表。
- `getFontInfo(fontName)` 返回字体信息（家族、字形数、许可等）。
- `getFontCSS(fontName, subset?)` 返回指定子集的 CSS 链接。
- `getFontSubsets(fontName)` 返回可用子集名称数组。
- `getFontChunks(fontName, subset)` 返回该子集的 woff2 分片信息。
- `getLicenseType / getLicenseUrl / getUsageRights / isCommercialUseAllowed` 查询许可类型、许可文件链接、使用权与是否允许商业使用。

## TypeScript

包内置完整类型定义，支持模块声明：

```ts
import type { FontLoader, FontName, LoadFontOptions } from '@windfonts/chinese-fonts';
import Loader from '@windfonts/chinese-fonts/fonts/Albbpht-Bold';

const run = async (opts?: LoadFontOptions) => {
  const url = await Loader(opts);
};
```

## 在框架中使用

### React

```tsx
import { useEffect } from 'react';
import { loadFont } from '@windfonts/chinese-fonts';

export default function App() {
  useEffect(() => {
    loadFont('Albbpht-Bold', { subset: 'zh-common' });
  }, []);
  return <div style={{ fontFamily: 'Albbpht, system-ui, sans-serif' }}>中文文本</div>;
}
```

### Vue 3

```ts
import { onMounted } from 'vue';
import { loadFont } from '@windfonts/chinese-fonts';

export default {
  setup() {
    onMounted(() => {
      loadFont('Albbpht-Bold', { subset: 'zh-common' });
    });
  },
};
```

## CDN 与子集

- CSS 与 woff2 文件由 WindFonts CDN 提供，例如：`https://cn.windfonts.com/fonts-packages/Albbpht/Bold/zh-common/result.css`。
- 常见子集：`zh-common`、`zh`、`en`。可通过 `getFontSubsets(fontName)` 获取当前字体的可用子集。

## 列出所有支持字体

```ts
import { getAllFonts } from '@windfonts/chinese-fonts';
console.log(getAllFonts());
```

## 许可说明

本包仅提供字体的 CDN 链接与许可元数据，字体版权归各字体作者或机构所有。使用前请通过 API 查询并遵循相应许可条款：

```ts
import { getFontLicense, getLicenseUrl, isCommercialUseAllowed } from '@windfonts/chinese-fonts';
const lic = getFontLicense('Albbpht-Bold');
const url = getLicenseUrl('Albbpht-Bold');
const ok = isCommercialUseAllowed('Albbpht-Bold');
```

如需商业使用或分发，请阅读许可文件并在合规范围内使用。

## 问题反馈

- 仓库：`https://github.com/Windfonts/font-packages`
- Issue：`https://github.com/Windfonts/font-packages/issues`

