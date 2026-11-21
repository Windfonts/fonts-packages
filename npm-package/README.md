# Chinese Fonts CDN

A collection of Chinese web fonts with CDN links and comprehensive license information.

## Installation

```bash
npm i @windfonts/chinese-fonts

# 或直接装 CDN 上的 tarball（与 npm 发布同内容，1.0.23 起）：
npm i https://cn.windfonts.com/fonts-packages/npm/chinese-fonts-1.0.23.tgz

# 或从 GitHub 仓库安装（与上面同内容）：
npm i github:WenPai-org/chinese-fonts
```

## Usage

### Method 1: Auto-load (Recommended)

Simply import and the font will be automatically loaded:

```javascript
// Import and auto-load with default subset (zh-common)
const { loadFont } = require('@windfonts/chinese-fonts');

// Load a font (returns Promise)
loadFont('Albbpht-Bold').then(cssUrl => {
  console.log('Font loaded:', cssUrl);
  // Font is now available to use
});

// Load with specific subset
loadFont('Albbpht-Bold', { subset: 'zh-common' });

// Load with preload for better performance
loadFont('Albbpht-Bold', { subset: 'zh-common', preload: true });
```

### Method 2: Individual Font Import

Import specific fonts directly:

```javascript
// Import a specific font
const font = require('@windfonts/chinese-fonts/fonts/Albbpht-Bold');

// Load the font (auto-loads with default subset)
font().then(cssUrl => {
  console.log('Font loaded:', cssUrl);
});

// Or with options
font({ subset: 'en' }).then(cssUrl => {
  console.log('English subset loaded:', cssUrl);
});

// Access font information
console.log(font.fontName);  // Font name
console.log(font.info);      // Full font information
console.log(font.getSubsets()); // Available subsets
console.log(font.getCSS('zh-common')); // Get CSS URL without loading
```

### Method 3: Manual CSS URL

Get the CSS URL without auto-loading:

```javascript
const { getFontCSS, getFontSubsets } = require('@windfonts/chinese-fonts');

// Get CSS URL
const cssUrl = getFontCSS('Albbpht-Bold', 'zh-common');
console.log(`CSS URL: ${cssUrl}`);

// Get available subsets
const subsets = getFontSubsets('Albbpht-Bold');
console.log(`Available subsets: ${subsets.join(', ')}`);

// Manually add to HTML
// <link rel="stylesheet" href="${cssUrl}">
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

This package includes 168 fonts:

### Alibaba-PuHuiTi-B

- **Family**: Albbpht
- **Subfamily**: Bold
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/albbpht/Bold/zh-common/result.css
- **License**: 阿里巴巴普惠体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/albbpht/Bold/zh-common/result.css">
```

### Alibaba-PuHuiTi-H

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, zh, full, en
- **CSS URL**: https://cn.windfonts.com/fonts-packages/albbpht/Heavy/zh-common/result.css
- **License**: 阿里巴巴普惠体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/albbpht/Heavy/zh-common/result.css">
```

### Alibaba-PuHuiTi-L

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, full, zh
- **CSS URL**: https://cn.windfonts.com/fonts-packages/albbpht/Light/zh-common/result.css
- **License**: 阿里巴巴普惠体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/albbpht/Light/zh-common/result.css">
```

### Alibaba-PuHuiTi-M

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/albbpht/Medium/zh-common/result.css
- **License**: 阿里巴巴普惠体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/albbpht/Medium/zh-common/result.css">
```

### Alibaba-PuHuiTi-R

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, full, zh
- **CSS URL**: https://cn.windfonts.com/fonts-packages/albbpht/Regular/zh-common/result.css
- **License**: 阿里巴巴普惠体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/albbpht/Regular/zh-common/result.css">
```

### AliHYAiHei

- **Family**: Alhyznht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, full, zh
- **CSS URL**: https://cn.windfonts.com/fonts-packages/alhyznht/Regular/zh-common/result.css
- **License**: 阿里汉仪智能黑体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/alhyznht/Regular/zh-common/result.css">
```

### AlimamaDongFangDaKai

- **Family**: Almmdfdk
- **Subfamily**: Regular
- **Available Subsets**: zh-common, zh, en, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/almmdfdk/Regular/zh-common/result.css
- **License**: 阿里妈妈东方大楷授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/almmdfdk/Regular/zh-common/result.css">
```

### Alimama DaoLiTi

- **Family**: Almmdlt
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/almmdlt/Regular/zh-common/result.css
- **License**: 阿里妈妈刀隶体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/almmdlt/Regular/zh-common/result.css">
```

### Alimama ShuHeiTi

- **Family**: Almmsht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, zh, full, en
- **CSS URL**: https://cn.windfonts.com/fonts-packages/almmsht/Bold/zh-common/result.css
- **License**: 阿里妈妈数黑体授权协议
- **License URL**: Not available
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/almmsht/Bold/zh-common/result.css">
```

### Droid Sans Fallback

- **Family**: Azbzzwzt
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/dshbt/Regular/zh-common/result.css
- **License**: Apache 2.0
- **License URL**: https://cn.windfonts.com/fonts-packages/dshbt/license/original.txt
- **Commercial Use**: ✅ Allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/dshbt/Regular/zh-common/result.css">
```

<details>
<summary>View all 168 fonts</summary>

| Font Key | Name | Family / Subfamily | Subsets | License | Commercial Use | Default CSS URL |
| --- | --- | --- | --- | --- | --- | --- |
| `Albbpht-Bold` | Alibaba-PuHuiTi-B | Albbpht / Bold | zh-common, en, zh, full | 阿里巴巴普惠体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/albbpht/Bold/zh-common/result.css |
| `Albbpht-Heavy` | Alibaba-PuHuiTi-H | Albbpht / Regular | zh-common, zh, full, en | 阿里巴巴普惠体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/albbpht/Heavy/zh-common/result.css |
| `Albbpht-Light` | Alibaba-PuHuiTi-L | Albbpht / Regular | zh-common, en, full, zh | 阿里巴巴普惠体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/albbpht/Light/zh-common/result.css |
| `Albbpht-Medium` | Alibaba-PuHuiTi-M | Albbpht / Regular | zh-common, en, zh, full | 阿里巴巴普惠体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/albbpht/Medium/zh-common/result.css |
| `Albbpht-Regular` | Alibaba-PuHuiTi-R | Albbpht / Regular | zh-common, en, full, zh | 阿里巴巴普惠体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/albbpht/Regular/zh-common/result.css |
| `Alhyznht-Regular` | AliHYAiHei | Alhyznht / Regular | zh-common, en, full, zh | 阿里汉仪智能黑体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/alhyznht/Regular/zh-common/result.css |
| `Almmdfdk-Regular` | AlimamaDongFangDaKai | Almmdfdk / Regular | zh-common, zh, en, full | 阿里妈妈东方大楷授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/almmdfdk/Regular/zh-common/result.css |
| `Almmdlt-Regular` | Alimama DaoLiTi | Almmdlt / Regular | zh-common, en, zh, full | 阿里妈妈刀隶体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/almmdlt/Regular/zh-common/result.css |
| `Almmsht-Bold` | Alimama ShuHeiTi | Almmsht / Regular | zh-common, zh, full, en | 阿里妈妈数黑体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/almmsht/Bold/zh-common/result.css |
| `Azbzzwzt-Regular` | Droid Sans Fallback | Azbzzwzt / Regular | zh-common, en, zh, full | [Apache 2.0](https://cn.windfonts.com/fonts-packages/dshbt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dshbt/Regular/zh-common/result.css |
| `Btot-Regular` | Potta One Regular | Btot / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/btot/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/btot/Regular/zh-common/result.css |
| `Btxbt-Regular` | baotuxiaobaiti | Btxbt / Regular | zh-common, zh, full, en | 包图小白体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/btxbt/Regular/zh-common/result.css |
| `Cexwz-Regular` | 仓耳小丸子 | Cexwz / Regular | zh-common, zh, en, full | 仓耳字库免费开源字体授权声明 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/cexwz/Regular/zh-common/result.css |
| `Cezkzdbs-Regular` | 仓耳周珂正大榜书 | Cezkzdbs / Regular | zh-common, en, zh, full | 仓耳字库免费开源字体授权声明 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/cezkzdbs/Regular/zh-common/result.css |
| `Cjkfqlt-Regular` | cjkFonts | Cjkfqlt / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/cjksxz/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/cjksxz/Regular/zh-common/result.css |
| `Cktjgt-Regular` | CKTKingKong | Cktjgt / Bold | zh-common, en, zh, full | 创客贴金刚体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/cktjgt/Regular/zh-common/result.css |
| `Cqscbbt-Regular` | YunFengchongqingbangbangti | Cqscbbt / Regular | zh-common, en, zh, full | 云峰字库重庆山城棒棒体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/yfzkzqscbbt/Regular/zh-common/result.css |
| `Cylyt-Monospaced` | _____ Thin Monospaced | Cylyt / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/cylytt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/cylytt/Monospaced/zh-common/result.css |
| `Cylyt-Regular` | _____ Thin | Cylyt / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/cylytt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/cylytt/Regular/zh-common/result.css |
| `Ddjbt-Normal` | DingTalk JinBuTi | Ddjbt / Regular | zh-common, en, zh, full | 钉钉进步体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ddjbt/Normal/zh-common/result.css |
| `Ddjbt-Regular` | DingTalk JinBuTi | Ddjbt / Regular | zh-common, zh, en, full | 钉钉进步体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ddjbt/Regular/zh-common/result.css |
| `Ddxstfx-Regular` | Dotted Songti Square Regular | Ddxstfx / Regular | zh-common, en, zh, full | [GPL-2.0](https://cn.windfonts.com/fonts-packages/dzxsstcgt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dzxsstcgt/Regular/zh-common/result.css |
| `Ddxstlx-Regular` | Dotted Songti Diamond Regular | Ddxstlx / Regular | zh-common, zh, en, full | [GPL-2.0](https://cn.windfonts.com/fonts-packages/ddxsstlx/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ddxsstlx/Regular/zh-common/result.css |
| `Ddxstyx-Regular` | Dotted Songti Circle Regular | Ddxstyx / Regular | zh-common, en, zh, full | [GPL-2.0](https://cn.windfonts.com/fonts-packages/ddxsyt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ddxsyt/Regular/zh-common/result.css |
| `Dlkjt-Regular` | 鼎猎客家体 | Dlkjt / Regular | zh-common, en, zh, full | 鼎猎客家体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dlkjt/Regular/zh-common/result.css |
| `Dlzht-Normal` | 鼎猎珠海体 | Dlzht / Regular | zh-common, en, zh, full | [鼎猎珠海体授权协议](https://cn.windfonts.com/fonts-packages/dlzht/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dlzht/Normal/zh-common/result.css |
| `Dyh-Oblique` | Smiley Sans Oblique | Dyh / Regular | zh-common, full, en, zh | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/dyh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dyh/Oblique/zh-common/result.css |
| `Dymht-Regular` | Douyin Sans Bold | Dymht / Bold | zh-common, en, zh, full | 抖音美好体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dymht/Regular/zh-common/result.css |
| `Dyzgt-Regular` | DOUYUFont | Dyzgt / Regular | zh-common, full, en, zh | 斗鱼追光体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/dyzgt/Regular/zh-common/result.css |
| `Gfmft-Regular` | 龚帆免费体3.0 | Gfmft / Regular | zh-common, en, zh, full | 龚帆免费体3.0授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/gfmft/Regular/zh-common/result.css |
| `Gljgbt-Regular` | 光良酒-干杯体 | Gljgbt / Regular | zh-common, zh, full, en | 光良酒-干杯体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/gljgbt/Regular/zh-common/result.css |
| `Hcdht-Black` | _____Black | Hcdht / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hcdht/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hcdht/Black/zh-common/result.css |
| `Hcdht-Light` | _____Light | Hcdht / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hcdht/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hcdht/Light/zh-common/result.css |
| `Hckht-Normal` | Chill K Sans | Hckht / Bold | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/hckht/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hckht/Normal/zh-common/result.css |
| `Hclcks-Bold` | _______Bold | Hclcks / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hclcks/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hclcks/Bold/zh-common/result.css |
| `Hclcks-Extrabold` | _______ExtraBold | Hclcks / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hclcks/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hclcks/Extrabold/zh-common/result.css |
| `Hclcks-Medium` | _______Medium | Hclcks / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hclcks/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hclcks/Medium/zh-common/result.css |
| `Hclcks-Regular` | _______Regular | Hclcks / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hclcks/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hclcks/Regular/zh-common/result.css |
| `Hcszt-Normal` | 寒蝉手拙体 | Hcszt / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/hcszt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hcszt/Normal/zh-common/result.css |
| `Hctyt-Normal` | 寒蝉团圆体_黑体 | Hctyt / Regular | zh-common, en, zh, full | [SIL Open Font License (OFL)](https://cn.windfonts.com/fonts-packages/hctyts/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hctyts/Normal/zh-common/result.css |
| `Hctyt-Round` | 寒蝉团圆体_圆体 | Hctyt / Regular | zh-common, en, zh, full | [SIL Open Font License (OFL)](https://cn.windfonts.com/fonts-packages/hctyts/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hctyts/Round/zh-common/result.css |
| `Hkhlssxt-Regular` | 黄凯桦律师手写体 | Hkhlssxt / Regular | zh-common, zh, en, full | 黄凯桦律师手写体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hkhlssxt/Regular/zh-common/result.css |
| `Hsmbzt-Regular` | KouzanBrushFontOTF | Hsmbzt / Regular | zh-common, en, zh, full | 衡山毛笔授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hsmb/Regular/zh-common/result.css |
| `Hxbnst-Regular` | HuXiaoBo-NanShen | Hxbnst / Regular | zh-common, zh, full, en | 胡晓波男神体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hxbnst/Regular/zh-common/result.css |
| `Hxbsb-Normal` | HuXiaoBao-SaoBao | Hxbsb / Regular | zh-common, en, full, zh | 胡晓波骚包体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hxbsbt/Normal/zh-common/result.css |
| `Hxbsbt-Regular` | HuXiaoBao-SaoBao | Hxbsbt / Regular | zh-common, en, zh, full | 胡晓波骚包体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hxbsbt/Regular/zh-common/result.css |
| `Hxbzst-Regular` | HuXiaoBo-ZhenShuai | Hxbzst / Regular | zh-common, zh, full, en | 胡晓波真帅体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hxbzst/Regular/zh-common/result.css |
| `Hyqzpt-Regular` | huangyinqi zhaopai | Hyqzpt / Regular | zh-common, en, zh, full | [黄引齐招牌体授权协议](https://cn.windfonts.com/fonts-packages/hyqzpt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hyqzpt/Regular/zh-common/result.css |
| `Hzpy-Regular` | Hanzi-Pinyin-Font | Hzpy / Regular | zh-common, zh, full | [CC-BY-SA-4.0](https://cn.windfonts.com/fonts-packages/hzpyt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hzpyt/Regular/zh-common/result.css |
| `Hzpyt-Regular` | Hanzi-Pinyin-Font | Hzpyt / Regular | zh-common, zh, full | [CC-BY-SA-4.0](https://cn.windfonts.com/fonts-packages/hzpyt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/hzpyt/Regular/zh-common/result.css |
| `Ibmps-Bold` | IBM Plex Sans SC Bold | Ibmps / Bold | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/ibmps/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ibmps/Bold/zh-common/result.css |
| `Ibmps-Extralight` | IBM Plex Sans SC ExtLt | Ibmps / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/ibmps/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ibmps/Extralight/zh-common/result.css |
| `Ibmps-Light` | IBM Plex Sans SC Light | Ibmps / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/ibmps/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ibmps/Light/zh-common/result.css |
| `Ibmps-Regular` | IBM Plex Sans SC | Ibmps / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/ibmps/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ibmps/Regular/zh-common/result.css |
| `Ibmps-Text` | IBM Plex Sans SC Text | Ibmps / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/ibmps/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ibmps/Text/zh-common/result.css |
| `Ibmps-Thin` | IBM Plex Sans SC Thin | Ibmps / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/ibmps/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ibmps/Thin/zh-common/result.css |
| `Jnbbh-Regular` | Kingnam Bobo Bold | Jnbbh / Bold | zh-common, en, zh, full | [荆南波波黑授权协议](https://cn.windfonts.com/fonts-packages/jnbbh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jnbbh/Regular/zh-common/result.css |
| `Jnymt-Regular` | 荆南缘默体 | Jnymt / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/jnymt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jnymt/Regular/zh-common/result.css |
| `Jnyyjyy-Regular` | SJjnyyjyy | Jnyyjyy / Regular | zh-common, en, full, zh | 今年也要加油鸭授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jnyyjyy/Regular/zh-common/result.css |
| `Jsyjst-Regular` | 金山云技术体 | Jsyjst / Bold | zh-common, en, zh, full | 金山云技术体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jsyjst/Regular/zh-common/result.css |
| `Jxzk-Regular` | jiangxizhuokai Regular | Jxzk / Regular | zh-common, en, zh, full | 江西拙楷体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jxzkt/Regular/zh-common/result.css |
| `Jzkgeht-Heavy` | Torono Kugel Sans Heavy | Jzkgeht / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/jzkgeht/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jzkgeht/Heavy/zh-common/result.css |
| `Jzkgemc-Heavy` | Torono Kugel Serif Heavy | Jzkgemc / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/jmct/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jmct/Heavy/zh-common/result.css |
| `Kksjt-Regular` | 快看世界體 標準 | Kksjt / Regular | zh-common, zh, en, full | 快看世界体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/kksjt/Regular/zh-common/result.css |
| `Klsyt-Regular` | I.Ngaan | Klsyt / Regular | zh-common, en, full, zh | GNU General Public License | ✅ Allowed | https://cn.windfonts.com/fonts-packages/inkslyt/Regular/zh-common/result.css |
| `Kslgbht-Regular` | I.PenCrane-B | Kslgbht / Regular | zh-common, en, zh, full | GNU General Public License v2.0 or later | ✅ Allowed | https://cn.windfonts.com/fonts-packages/gbhb/Regular/zh-common/result.css |
| `Kslmt-Regular` | I.Ming | Kslmt / Regular | zh-common, en, zh, full | [IPA Font License v1.0](https://cn.windfonts.com/fonts-packages/ydmt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ydmt/Regular/zh-common/result.css |
| `Kslyt-Regular` | I.Ming | Kslyt / Regular | zh-common, en, zh, full | [IPA Font License v1.0](https://cn.windfonts.com/fonts-packages/ydmt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ydmt/Regular/zh-common/result.css |
| `Lftsyh-Regular` | Cubic 11 | Lftsyh / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/lft11h/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/lft11h/Regular/zh-common/result.css |
| `Lhktss-Regular` | Liu Huan KaTong ShouShu | Lhktss / Regular | zh-common, en, zh, full | 刘欢卡通手书授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/lhktss/Regular/zh-common/result.css |
| `Lhls-Regular` | ??? Regular | Lhls / Regular | zh-common, zh, en, full | 临海体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/lhtt/Regular/zh-common/result.css |
| `Lhzt-Regular` | SetoFont | Lhzt / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/lhzt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/lhzt/Regular/zh-common/result.css |
| `Ljmc-Regular` | Liu Jian Mao Cao Regular | Ljmc / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/zqljmc/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zqljmc/Regular/zh-common/result.css |
| `Lmqylszrht-Regular` | lianmengqiyilushuaizhengruiheiti Regular | Lmqylszrht / Regular | zh-common, zh, en, full | 联盟起艺卢帅正锐黑体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/lmqylszrht/Regular/zh-common/result.css |
| `Misa-Bold` | MiSans Bold | Misa / Bold | zh-common, en, full, zh | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Bold/zh-common/result.css |
| `Misa-Demibold` | MiSans Demibold | Misa / Demibold | zh-common, en, full, zh | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Demibold/zh-common/result.css |
| `Misa-Extralight` | MiSans ExtraLight | Misa / ExtraLight | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Extralight/zh-common/result.css |
| `Misa-Heavy` | MiSans Heavy | Misa / Heavy | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Heavy/zh-common/result.css |
| `Misa-Light` | MiSans Light | Misa / Light | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Light/zh-common/result.css |
| `Misa-Medium` | MiSans Medium | Misa / Medium | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Medium/zh-common/result.css |
| `Misa-Normal` | MiSans Normal | Misa / Normal | zh-common, en, full, zh | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Normal/zh-common/result.css |
| `Misa-Regular` | MiSans | Misa / Regular | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Regular/zh-common/result.css |
| `Misa-Semibold` | MiSans Semibold | Misa / Semibold | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Semibold/zh-common/result.css |
| `Misa-Thin` | MiSans Thin | Misa / Thin | zh-common, en, zh, full | MiSans 字体知识产权许可协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/misa/Thin/zh-common/result.css |
| `Mksjh-Bold` | MaokenAssortedSans | Mksjh / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/mksjh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mksjh/Bold/zh-common/result.css |
| `Mkwfys-Regular` | MaokenFengYaSong | Mkwfys / Regular | zh-common, zh, en, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/mkwfys/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mkwfys/Regular/zh-common/result.css |
| `Mkwgzh-Regular` | Maoken Glitch Sans | Mkwgzh / Regular | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/mkwgzh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mkwgzh/Regular/zh-common/result.css |
| `Mkwgzs-Regular` | Maoken Glitch Serif | Mkwgzs / Regular | zh-common, en, zh, full | [SIL Open Font License (OFL)](https://cn.windfonts.com/fonts-packages/mkwgzs/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mkwgzs/Regular/zh-common/result.css |
| `Mkwxy-Regular` | MaoKenWangXingYuan | Mkwxy / Regular | zh-common, zh, full, en | [OFL](https://cn.windfonts.com/fonts-packages/mkwtyt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mkwtyt/Regular/zh-common/result.css |
| `Mkzyt-Regular` | MaokenZhuyuanTi Regular | Mkzyt / Regular | zh-common, zh, full, en | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/mkzyt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mkzyt/Regular/zh-common/result.css |
| `Mspyt-Regular` | Mengshen-HanSerif | Mspyt / Regular | zh-common, en, full, zh | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/myst/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/myst/Regular/zh-common/result.css |
| `Myrbsxt-Regular` | Muyao-Softbrush | Myrbsxt / Regular | zh-common, zh, en, full | 沐瑶软笔手写体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/myrbsxt/Regular/zh-common/result.css |
| `Mysxt-Regular` | Muyao-Softbrush | Mysxt / Regular | zh-common, zh, en, full | 沐瑶软笔手写体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/myrbsxt/Regular/zh-common/result.css |
| `Nsfx-Regular` | 女書鳳棲 | Nsfx / 鳳棲 | full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/nsfq/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/nsfq/Regular/full/result.css |
| `Nswt-Italic` | 女書梧桐斜意 | Nswt / Italic | full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/nswt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/nswt/Italic/full/result.css |
| `Nswt-Regular` | 女書梧桐 | Nswt / Regular | full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/nswt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/nswt/Regular/full/result.css |
| `Opsa-Bold` | OPPO Sans Bold | Opsa / Bold | zh-common, en, zh, full | [OPPO Sans Free Use License](https://cn.windfonts.com/fonts-packages/opsa/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/opsa/Bold/zh-common/result.css |
| `Opsa-Light` | OPPO Sans 4.0 | Opsa / Regular | zh-common, en, zh, full | [OPPO Sans Free Use License](https://cn.windfonts.com/fonts-packages/opsa/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/opsa/Light/zh-common/result.css |
| `Opsa-Medium` | OPPO Sans Medium | Opsa / Medium | zh-common, en, zh, full | [OPPO Sans Free Use License](https://cn.windfonts.com/fonts-packages/opsa/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/opsa/Medium/zh-common/result.css |
| `Opsa-Regular` | OPPO Sans | Opsa / Regular | zh-common, en, zh, full | [OPPO Sans Free Use License](https://cn.windfonts.com/fonts-packages/opsa/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/opsa/Regular/zh-common/result.css |
| `Pfhtt-Regular` | PFanHuTuTi | Pfhtt / Regular | zh-common, en, zh, full | PF频凡胡涂体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/pfhtt/Regular/zh-common/result.css |
| `Pmzdbtt-Regular` | PangMenZhengDao | Pmzdbtt / Regular | zh-common, zh, en, full | 庞门正道标题体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/pmzdbtt/Regular/zh-common/result.css |
| `Pmzdcsd-Regular` | PangMenZhengDao-Cu6.0 | Pmzdcsd / Regular | en, zh-common, zh, full | 庞门正道粗书体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/pmzdcst/Regular/zh-common/result.css |
| `Pmzdqst-Regular` | Pangmenzhengdaoqingsongti | Pmzdqst / Regular | zh-common, en, zh, full | 庞门正道轻松体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/pmzdqst/Regular/zh-common/result.css |
| `Pmzdzgkt-Regular` | PangZhenGui-PMZD | Pmzdzgkt / Regular | zh-common, zh, en, full | [庞门正道真贵楷体授权协议](https://cn.windfonts.com/fonts-packages/pmzdzgkt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/pmzdzgkt/Regular/zh-common/result.css |
| `Prsxt-Regular` | 品如手写体 | Prsxt / Regular | zh-common, en, zh, full | 品如手写体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/prsxt/Regular/zh-common/result.css |
| `Pxzs-Regular` | Clear Han Serif | Pxzs / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/pxzs/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/pxzs/Regular/zh-common/result.css |
| `Qssxt-Regular` | JasonWriting2 | Qssxt / JasonWriting2 | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/qssxt2/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qssxt2/Regular/zh-common/result.css |
| `Qtbfsxt-Regular` | qiantubifengshouxieti | Qtbfsxt / Regular | zh-common, zh, en, full | 千图笔锋手写体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qtbfsxt/Regular/zh-common/result.css |
| `Qthht-Regular` | qiantuhouheiti | Qthht / Regular | zh-common, zh, full, en | 千图厚黑体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qthht/Regular/zh-common/result.css |
| `Qtmksxt-Regular` | qiantumakeshouxieti | Qtmksxt / Regular | zh-common, en, full, zh | 千图马克手写体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qtmksxt/Regular/zh-common/result.css |
| `Qtqmt-Regular` | qiantuxianmoti | Qtqmt / Regular | zh, zh-common, en, full | 千图纤墨体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qtxmt/Regular/zh-common/result.css |
| `Qtxht-Regular` | qiantuxuehuati | Qtxht / Regular | zh-common, en, zh, full | 千图学画体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qtxht/Regular/zh-common/result.css |
| `Qtxmt-Regular` | qiantuxianmoti | Qtxmt / Regular | zh-common, en, zh, full | 千图纤墨体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qtxmt/Regular/zh-common/result.css |
| `Qtxtt-Regular` | QTxiaotu | Qtxtt / Regular | zh-common, en, full, zh | 千图小兔体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/qtxtt/Regular/zh-common/result.css |
| `Qzkswjz-Regular` | hWW | Qzkswjz / Medium | zh-common, en, zh, full | EBAS 无衬线体授权协议 | ❌ Not allowed | https://cn.windfonts.com/fonts-packages/ebaswcxt/Regular/zh-common/result.css |
| `Rzzyt-Regular` | ZhenyanGB Regular | Rzzyt / Regular | zh-common, zh, en, full | 臻妍GB 常规体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zygb/Regular/zh-common/result.css |
| `Scjskkt-Regular` | sucaijishikangkangti | Scjskkt / Regular | zh-common, zh, en, full | 素材集市康康体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/scjskkt/Regular/zh-common/result.css |
| `Sft-Regular` | The Peak Font 隨峰體 Beta | Sft / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/sftb/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/sftb/Regular/zh-common/result.css |
| `Stfytz-Regular` | w | Stfytz / Regular | zh-common, en, zh, full | 书体坊颜体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/stfyt/Regular/zh-common/result.css |
| `Stfzxfxct-Regular` | 书体坊禚效锋行草体 | Stfzxfxct / Regular | zh-common, en, full, zh | 书体坊禚效锋行草体授权协议 | ❌ Not allowed | https://cn.windfonts.com/fonts-packages/stfzxfxct/Regular/zh-common/result.css |
| `Syhtcjk-Black` | Noto Sans CJK Black Bold | Syhtcjk / Bold | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/Black/zh-common/result.css |
| `Syhtcjk-Bold` | Noto Sans CJK Bold Bold | Syhtcjk / Bold | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/Bold/zh-common/result.css |
| `Syhtcjk-DemiLight` | Noto Sans CJK DemiLight | Syhtcjk / Regular | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/DemiLight/zh-common/result.css |
| `Syhtcjk-Light` | Noto Sans CJK Light | Syhtcjk / Regular | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/Light/zh-common/result.css |
| `Syhtcjk-Medium` | Noto Sans CJK Medium | Syhtcjk / Regular | zh-common, zh, en, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/Medium/zh-common/result.css |
| `Syhtcjk-Regular` | Noto Sans CJK Regular | Syhtcjk / Regular | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/Regular/zh-common/result.css |
| `Syhtcjk-Thin` | Noto Sans CJK Thin | Syhtcjk / Regular | zh-common, en, zh, full | [SIL Open Font License](https://cn.windfonts.com/fonts-packages/syhtr/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/syhtr/Thin/zh-common/result.css |
| `Symdxft-Regular` | shetumodengxiaofangti | Symdxft / Regular | zh-common, zh, en, full | 摄图摩登小方体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/stmdxft/Regular/zh-common/result.css |
| `Systcn-Bold` | Source Han Serif CN Bold | Systcn / Bold | zh-common, en, full, zh | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Bold/zh-common/result.css |
| `Systcn-Extralight` | Source Han Serif CN ExtraLight | Systcn / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Extralight/zh-common/result.css |
| `Systcn-Heavy` | Source Han Serif CN Heavy | Systcn / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Heavy/zh-common/result.css |
| `Systcn-Light` | Source Han Serif CN Light | Systcn / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Light/zh-common/result.css |
| `Systcn-Medium` | Source Han Serif CN Medium | Systcn / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Medium/zh-common/result.css |
| `Systcn-Regular` | Source Han Serif CN | Systcn / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Regular/zh-common/result.css |
| `Systcn-Semibold` | Source Han Serif CN SemiBold | Systcn / Regular | zh-common, zh, full, en | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/systcn/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/systcn/Semibold/zh-common/result.css |
| `Twjybbzjs-Regular` | 教育部標準楷書 | Twjybbzjs / Regular | zh-common, en, full, zh | CC BY-ND 3.0 TW | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jybbzks/Regular/zh-common/result.css |
| `Twjybbzst-Regular` | MOESongUN | Twjybbzst / Regular | zh-common, en, zh, full | SIL Open Font License 1.1 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/jybbzstun/Regular/zh-common/result.css |
| `Twjybxxmt-Regular` | PMingLiU-TW | Twjybxxmt / Regular | zh-common, en, zh, full | PMingLiU 繁体中文版授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xxmttw/Regular/zh-common/result.css |
| `Unfdzh-Regular` | GNU Unifont Full | Unfdzh / Medium | zh-common, en, zh, full | [Dual license: GNU GPL version 2 or later with the GNU Font Embedding Exception, and SIL Open Font License version 1.1](https://cn.windfonts.com/fonts-packages/gnuuf/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/gnuuf/Regular/zh-common/result.css |
| `Wcsf-Normal` | 问藏书房 | Wcsf / Regular | zh-common, zh, en, full | 问藏书房授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/wcsf/Normal/zh-common/result.css |
| `Wqydkwmh-Regular` | WenQuanYi Micro Hei Mono | Wqydkwmh / Regular | zh-common, en, zh, full | [Apache 2.0 / GPLv3](https://cn.windfonts.com/fonts-packages/wqydkwmh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/wqydkwmh/Regular/zh-common/result.css |
| `Wqydkzh-Regular` | WenQuanYi Zen Hei Mono | Wqydkzh / Medium | zh-common, en, zh, full | [GPL-2.0-with-font-exception](https://cn.windfonts.com/fonts-packages/wqyzhdk/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/wqyzhdk/Regular/zh-common/result.css |
| `Wqywmh-Regular` | WenQuanYi Micro Hei | Wqywmh / Regular | zh-common, zh, en, full | [Apache 2.0 / GPLv3 (双许可证)](https://cn.windfonts.com/fonts-packages/wqywmh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/wqywmh/Regular/zh-common/result.css |
| `Wqyzh-Regular` | WenQuanYi Zen Hei | Wqyzh / Medium | zh-common, en, full, zh | [GPL-2.0-with-font-exception](https://cn.windfonts.com/fonts-packages/wqyzht/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/wqyzht/Regular/zh-common/result.css |
| `Xet-Regular` | XianErTi | Xet / Regular | zh-common, en, zh, full | 贤二体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xet/Regular/zh-common/result.css |
| `Xlfht-Regular` | xianglifang Regular | Xlfht / Regular | zh-common, zh, en, full | 乡立方黑体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xlfht/Regular/zh-common/result.css |
| `Xsslv-Regular` | Silver | Xsslv / Medium | zh-common, en, full, zh | CC BY 4.0 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xsszt/Regular/zh-common/result.css |
| `Xwmh-Regular` | LXGW Marker Gothic | Xwmh / Regular | zh-common, en, full, zh | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/xwmh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xwmh/Regular/zh-common/result.css |
| `Xwxxh-Regular` | LXGW Neo XiHei | Xwxxh / Regular | zh-common, zh, en, full | [IPA Font License](https://cn.windfonts.com/fonts-packages/xwxxh/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xwxxh/Regular/zh-common/result.css |
| `Xwxzs-Regular` | LXGW Neo ZhiSong | Xwxzs / Regular | zh-common, en, zh, full | [IPA Open Font License 1.0](https://cn.windfonts.com/fonts-packages/xwxzs/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/xwxzs/Regular/zh-common/result.css |
| `Ydwbnnsp-Regular` | YDW plus plus | Ydwbnnsp / Regular | zh-common, zh, en, full | 香蕉Plus字体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ydwxjhxt/Regular/zh-common/result.css |
| `Yffyt-Regular` | 云峰飞云体 | Yffyt / Regular | zh-common, en, zh, full | 云峰飞云体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/yffyt/Regular/zh-common/result.css |
| `Yjmct-Regular` | Genkaimincho | Yjmct / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/yjmc/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/yjmc/Regular/zh-common/result.css |
| `Ysbth-Bold` | YouSheBiaoTiHei | Ysbth / Regular | en, zh-common, zh, full | 优设标题黑授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ysbth/Bold/zh-common/result.css |
| `Ysbzt-Regular` | 峄山碑篆体 | Ysbzt / Regular | zh-common, en, full, zh | 峄山碑篆体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ysbzt/Regular/zh-common/result.css |
| `Yzklct-Regular` | Long Cang Regular | Yzklct / Regular | zh-common, en, full, zh | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/lct/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/lct/Regular/zh-common/result.css |
| `Zhbtt-Oblique` | zihunbiantaoti | Zhbtt / Regular | zh-common, en, full, zh | SIL Open Font License 1.1 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zhbtt/Oblique/zh-common/result.css |
| `Zjgljt-Regular` | ZhuoJianGanLanJianTi Regular | Zjgljt / Regular | zh-common, en, zh, full | 卓健橄榄简体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zjgljt/Regular/zh-common/result.css |
| `Zkgdht-Regular` | huxiaobo-gdh | Zkgdht / Regular | zh-common, en, zh, full | SIL Open Font License 1.1 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zkgdh/Regular/zh-common/result.css |
| `Zkkht-Regular` | HuXiaoBo_KuHei | Zkkht / Regular | zh-common, zh, en, full | 站酷酷黑授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zkkh/Regular/zh-common/result.css |
| `Zkklt-Regular` | HappyZcool-2016 | Zkklt / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/zkklt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zkklt/Regular/zh-common/result.css |
| `Zkwyt-Regular` | zcoolwenyiti | Zkwyt / Regular | zh-common, en, zh, full | 站酷文艺体授权协议 | ❌ Not allowed | https://cn.windfonts.com/fonts-packages/zkwyt/Regular/zh-common/result.css |
| `Zkxwt-Regular` | xiaowei | Zkxwt / Regular | zh-common, en, zh, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/zkxwt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zkxwt/Regular/zh-common/result.css |
| `Zqkhyt-Regular` | Regular | Zqkhyt / Regular | zh-common, en, full, zh | [郑庆科黄油体 Regular授权协议](https://cn.windfonts.com/fonts-packages/zqkhyt/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zqkhyt/Regular/zh-common/result.css |
| `Ztqxyjxs-Regular` | Fontquan-XinYiJiXiangSong Regular | Ztqxyjxs / Regular | zh-common, en, zh, full | 字体圈-信谊吉祥宋授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/ztqxyjxs/Regular/zh-common/result.css |
| `Zwxszt-Regular` | mplus_hzk_12 | Zwxszt / Regular | zh-common, zh, en, full | [SIL Open Font License 1.1](https://cn.windfonts.com/fonts-packages/mhzk12/license/original.txt) | ✅ Allowed | https://cn.windfonts.com/fonts-packages/mhzk12/Regular/zh-common/result.css |
| `Zyss-Regular` | ShouShuti | Zyss / Regular | zh-common, en, full, zh | 智勇手书体授权协议 | ✅ Allowed | https://cn.windfonts.com/fonts-packages/zysst/Regular/zh-common/result.css |

</details>

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
