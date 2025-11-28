# Chinese Fonts CDN / 中文字体 CDN

A collection of Chinese web fonts with CDN links and comprehensive license information.

中文 Web 字体集合，提供可直接使用的 CDN CSS 链接与许可信息。

## Installation / 安装

```bash
npm i @windfonts/chinese-fonts
```

## Usage / 使用

### Method 1: Auto-load (Recommended) / 方法一：自动加载（推荐）

Simply import and the font will be automatically loaded / 直接导入即自动加载：

```javascript
// Import and auto-load with default subset (zh-common)
const { loadFont } = require('@windfonts/chinese-fonts');

// Load a font (returns Promise)
loadFont('Albbpht-Bold').then(cssUrl => {
  console.log('Font loaded:', cssUrl);
  // Font is now available to use
});

// Load with specific subset / 指定子集加载
loadFont('Albbpht-Bold', { subset: 'zh-common' });

// Load with preload for better performance / 预加载提升性能
loadFont('Albbpht-Bold', { subset: 'zh-common', preload: true });
```

### Method 2: Individual Font Import / 方法二：按字体模块导入

Import specific fonts directly:

```javascript
// Import a specific font
const font = require('@windfonts/chinese-fonts/fonts/Albbpht-Bold');

// Load the font (auto-loads with default subset)
font().then(cssUrl => {
  console.log('Font loaded:', cssUrl);
});

// Or with options / 传入选项
font({ subset: 'en' }).then(cssUrl => {
  console.log('English subset loaded:', cssUrl);
});

// Access font information / 获取字体信息
console.log(font.fontName);  // Font name
console.log(font.info);      // Full font information
console.log(font.getSubsets()); // Available subsets
console.log(font.getCSS('zh-common')); // Get CSS URL without loading
```

### Method 3: Manual CSS URL / 方法三：仅获取 CSS 链接

Get the CSS URL without auto-loading / 仅返回链接不自动加载：

```javascript
const { getFontCSS, getFontSubsets } = require('@windfonts/chinese-fonts');

// Get CSS URL / 获取 CSS 链接
const cssUrl = getFontCSS('Albbpht-Bold', 'zh-common');
console.log(`CSS URL: ${cssUrl}`);

// Get available subsets / 获取可用子集
const subsets = getFontSubsets('Albbpht-Bold');
console.log(`Available subsets: ${subsets.join(', ')}`);

// Manually add to HTML / 手动插入到 HTML
// <link rel="stylesheet" href="${cssUrl}">
```

### ESM Quick Start / ESM 快速使用

```js
import { loadFont, getAllFonts, getFontInfo } from '@windfonts/chinese-fonts'

await loadFont('Albbpht-Bold', { subset: 'zh-common', preload: true })
const names = getAllFonts()
const info = getFontInfo('Albbpht-Bold')
```

```js
import AlbbphtBold from '@windfonts/chinese-fonts/fonts/Albbpht-Bold'

await AlbbphtBold({ subset: 'zh-common' })
```

### TypeScript Lazy Load / TypeScript 懒加载示例

```ts
import type { FontLoader, LoadFontOptions } from '@windfonts/chinese-fonts';
import AlbbphtBold from '@windfonts/chinese-fonts/fonts/Albbpht-Bold';

const run = async (opts?: LoadFontOptions) => {
  const css = await AlbbphtBold({ subset: 'zh-common', preload: true });
};

import { getAllFonts, getFontInfo } from '@windfonts/chinese-fonts';
const names = getAllFonts();
const info = getFontInfo('Albbpht-Bold');
```

## License Information API

This package provides comprehensive license information for each font:

```javascript
const { getLicenseType, getLicenseUrl, getUsageRights } = require('@windfonts/chinese-fonts');

// Get license type
const licenseType = getLicenseType('FontName');
console.log(`License: ${licenseType}`); // e.g., 'OFL', 'MIT', 'Apache-2.0'

// Get license file URL
const licenseUrl = getLicenseUrl('FontName');
console.log(`License URL: ${licenseUrl}`);

// Get detailed usage rights
const rights = getUsageRights('FontName');
console.log(`Commercial use: ${rights.commercial}`);
console.log(`Modification: ${rights.modification}`);
console.log(`Distribution: ${rights.distribution}`);
console.log(`Private use: ${rights.privateUse}`);
```

## Available Fonts

This package includes 169 fonts:

### Alibaba-PuHuiTi-B

- **Family**: Albbpht
- **Subfamily**: Bold
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Bold/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Bold/zh-common/result.css">
```

### Alibaba-PuHuiTi-H

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh, zh-common, full, en
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Heavy/zh/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Heavy/zh/result.css">
```

### Alibaba-PuHuiTi-L

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Light/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Light/zh-common/result.css">
```

### Alibaba-PuHuiTi-M

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: en, zh-common, full, zh
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Medium/en/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Medium/en/result.css">
```

### Alibaba-PuHuiTi-R

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Regular/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Regular/zh-common/result.css">
```

### AliHYAiHei

- **Family**: Alhyznht
- **Subfamily**: Regular
- **Available Subsets**: zh, en, zh-common, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Alhyznht/Regular/zh/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Alhyznht/Regular/zh/result.css">
```

### AlimamaDongFangDaKai

- **Family**: Almmdfdk
- **Subfamily**: Regular
- **Available Subsets**: zh, en, zh-common, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Almmdfdk/Regular/zh/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Almmdfdk/Regular/zh/result.css">
```

### Alimama DaoLiTi

- **Family**: Almmdlt
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Almmdlt/Regular/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Almmdlt/Regular/zh-common/result.css">
```

### Alimama ShuHeiTi

- **Family**: Almmsht
- **Subfamily**: Regular
- **Available Subsets**: zh, en, zh-common, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Almmsht/Bold/zh/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Almmsht/Bold/zh/result.css">
```

### Droid Sans Fallback

- **Family**: Azbzzwzt
- **Subfamily**: Regular
- **Available Subsets**: zh, en, zh-common, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Azbzzwzt/Regular/zh/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Azbzzwzt/Regular/zh/result.css">
```


... and 159 more fonts.

## TypeScript Support

This package includes TypeScript type definitions:

```typescript
import { FontInfo, UsageRights, getAllFonts, getFontInfo } from '@windfonts/chinese-fonts';

const fonts: string[] = getAllFonts();
const fontInfo: FontInfo | undefined = getFontInfo('FontName');
```

## License

Each font has its own license. Please check the license information for each font before use.

## Contributing

To add new fonts or update existing ones, please submit a pull request to the repository.
