# Chinese Fonts CDN

A collection of Chinese web fonts with CDN links and comprehensive license information.

## Installation

```bash
npm install windfonts-chinese-fonts
```

## Usage

### Method 1: Auto-load (Recommended)

Simply import and the font will be automatically loaded:

```javascript
// Import and auto-load with default subset (zh-common)
const { loadFont } = require('windfonts-chinese-fonts');

// Load a font (returns Promise)
loadFont('Alibabapuhuiti-Bold').then(cssUrl => {
  console.log('Font loaded:', cssUrl);
  // Font is now available to use
});

// Load with specific subset
loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });

// Load with preload for better performance
loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common', preload: true });
```

### Method 2: Individual Font Import

Import specific fonts directly:

```javascript
// Import a specific font
const font = require('windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold');

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
const { getFontCSS, getFontSubsets } = require('windfonts-chinese-fonts');

// Get CSS URL
const cssUrl = getFontCSS('Alibabapuhuiti-Bold', 'zh-common');
console.log(`CSS URL: ${cssUrl}`);

// Get available subsets
const subsets = getFontSubsets('Alibabapuhuiti-Bold');
console.log(`Available subsets: ${subsets.join(', ')}`);

// Manually add to HTML
// <link rel="stylesheet" href="${cssUrl}">
```

## License Information API

This package provides comprehensive license information for each font:

```javascript
const { getLicenseType, getLicenseUrl, getUsageRights } = require('windfonts-chinese-fonts');

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

This package includes 8 fonts:

### Alibaba-PuHuiTi-B

- **Family**: Alibabapuhuiti
- **Subfamily**: Bold
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/build/Alibabapuhuiti/Bold/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/build/Alibabapuhuiti/Bold/zh-common/result.css">
```

### Alibaba-PuHuiTi-H

- **Family**: Alibabapuhuiti
- **Subfamily**: Regular
- **Available Subsets**: zh-common, zh, full, en
- **CSS URL**: https://cn.windfonts.com/build/Alibabapuhuiti/Heavy/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/build/Alibabapuhuiti/Heavy/zh-common/result.css">
```

### Alibaba-PuHuiTi-R

- **Family**: Alibabapuhuiti
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/build/Alibabapuhuiti/Regular/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/build/Alibabapuhuiti/Regular/zh-common/result.css">
```

### Hanzipinyin

- **Family**: Hanzipinyin
- **Subfamily**: Regular
- **Available Subsets**: None
- **CSS URL**: Not available
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

### Huxiaobosaobao

- **Family**: Huxiaobosaobao
- **Subfamily**: Regular
- **Available Subsets**: None
- **CSS URL**: Not available
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

### Linhailishu

- **Family**: Linhailishu
- **Subfamily**: Regular
- **Available Subsets**: None
- **CSS URL**: Not available
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

### Liujiangmaocao

- **Family**: Liujiangmaocao
- **Subfamily**: Regular
- **Available Subsets**: None
- **CSS URL**: Not available
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

### Zhiyongshoushuti

- **Family**: Zhiyongshoushuti
- **Subfamily**: Regular
- **Available Subsets**: None
- **CSS URL**: Not available
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

## TypeScript Support

This package includes TypeScript type definitions:

```typescript
import { FontInfo, UsageRights, getAllFonts, getFontInfo } from 'windfonts-chinese-fonts';

const fonts: string[] = getAllFonts();
const fontInfo: FontInfo | undefined = getFontInfo('FontName');
```

## License

Each font has its own license. Please check the license information for each font before use.

## Contributing

To add new fonts or update existing ones, please submit a pull request to the repository.
