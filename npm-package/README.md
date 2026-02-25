# Chinese Fonts CDN

A collection of Chinese web fonts with CDN links and comprehensive license information.

## Installation

```bash
npm i @windfonts/chinese-fonts
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
- **Available Subsets**: zh-common, zh, full, en
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Heavy/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Heavy/zh-common/result.css">
```

### Alibaba-PuHuiTi-L

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, full, zh
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
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Albbpht/Medium/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Albbpht/Medium/zh-common/result.css">
```

### Alibaba-PuHuiTi-R

- **Family**: Albbpht
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, full, zh
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
- **Available Subsets**: zh-common, en, full, zh
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Alhyznht/Regular/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Alhyznht/Regular/zh-common/result.css">
```

### AlimamaDongFangDaKai

- **Family**: Almmdfdk
- **Subfamily**: Regular
- **Available Subsets**: zh-common, zh, en, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Almmdfdk/Regular/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Almmdfdk/Regular/zh-common/result.css">
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
- **Available Subsets**: zh-common, zh, full, en
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Almmsht/Bold/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Almmsht/Bold/zh-common/result.css">
```

### Droid Sans Fallback

- **Family**: Azbzzwzt
- **Subfamily**: Regular
- **Available Subsets**: zh-common, en, zh, full
- **CSS URL**: https://cn.windfonts.com/fonts-packages/Azbzzwzt/Regular/zh-common/result.css
- **License**: Unknown
- **License URL**: Not available
- **Commercial Use**: ❌ Not allowed

**Usage:**
```html
<link rel="stylesheet" href="https://cn.windfonts.com/fonts-packages/Azbzzwzt/Regular/zh-common/result.css">
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
