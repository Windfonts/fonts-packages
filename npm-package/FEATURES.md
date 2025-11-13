# NPM 包功能说明 (Package Features)

## 概述 (Overview)

这个 npm 包提供了一个简单的 API 来访问托管在 CDN 上的中文字体。用户安装包后，可以通过 API 获取字体的 CDN URL，而不需要下载实际的字体文件。

## 核心特性 (Core Features)

### 1. 🌐 CDN 托管 (CDN Hosted)

- 所有字体文件托管在 CDN 上
- 用户只需引入 CSS URL，无需下载字体文件
- 支持按需加载，减少初始加载时间

### 2. 📦 多子集支持 (Multiple Subsets)

每个字体提供多个子集选项：

- **zh-common**: 常用中文字符（约 3500 个常用汉字）
- **en**: 英文字符（最小体积）
- **zh**: 完整中文字符集
- **full**: 包含所有字符（最大字符集）

### 3. 🔍 查询 API (Query API)

提供完整的字体信息查询功能：

```javascript
// 获取所有字体
getAllFonts()

// 获取字体详细信息
getFontInfo(fontName)

// 获取 CSS URL
getFontCSS(fontName, subset)

// 获取可用子集
getFontSubsets(fontName)

// 获取字体块（woff2 文件）
getFontChunks(fontName, subset)
```

### 4. 📜 授权信息 (License Information)

每个字体包含完整的授权信息：

```javascript
// 获取授权类型
getLicenseType(fontName)

// 获取授权文件 URL
getLicenseUrl(fontName)

// 获取使用权限
getUsageRights(fontName)

// 检查是否允许商业使用
isCommercialUseAllowed(fontName)
```

### 5. 💪 TypeScript 支持 (TypeScript Support)

完整的 TypeScript 类型定义：

```typescript
interface FontInfo {
  name: string;
  family: string;
  subfamily: string;
  weight?: string;
  charCount: number;
  glyphCount: number;
  unicodeRanges: UnicodeRanges;
  files: FontFiles;
  license: FontLicense;
}

interface UsageRights {
  commercial: boolean;
  modification: boolean;
  distribution: boolean;
  privateUse: boolean;
}
```

## 数据结构 (Data Structure)

### 字体信息 (Font Information)

```json
{
  "Alibabapuhuiti-Bold": {
    "name": "Alibaba-PuHuiTi-B",
    "family": "Alibabapuhuiti",
    "subfamily": "Bold",
    "weight": "Bold",
    "charCount": 28937,
    "glyphCount": 28987,
    "unicodeRanges": {
      "Basic Latin": 100,
      "CJK Unified Ideographs": 20902
    },
    "files": {
      "source": "fonts/Alibabapuhuiti/Bold.ttf",
      "subsets": {
        "zh-common": {
          "css": "https://cdn.example.com/.../result.css",
          "chunks": [
            {
              "file": "0.woff2",
              "url": "https://cdn.example.com/.../0.woff2"
            }
          ]
        }
      }
    },
    "license": {
      "type": "Unknown",
      "url": null,
      "usageRights": {
        "commercial": false,
        "modification": false,
        "distribution": false,
        "privateUse": true
      }
    }
  }
}
```

## 使用场景 (Use Cases)

### 1. Web 应用 (Web Applications)

```javascript
// 动态加载字体
const cssUrl = getFontCSS('Alibabapuhuiti-Bold', 'zh-common');
const link = document.createElement('link');
link.rel = 'stylesheet';
link.href = cssUrl;
document.head.appendChild(link);
```

### 2. React/Vue/Next.js 应用

在组件中动态加载字体，支持服务端渲染。

### 3. 字体选择器 (Font Picker)

```javascript
// 构建字体选择器
const allFonts = getAllFonts();
allFonts.forEach(fontName => {
  const info = getFontInfo(fontName);
  // 显示字体信息和预览
});
```

### 4. 授权检查工具 (License Checker)

```javascript
// 检查项目中使用的字体授权
const usedFonts = ['Alibabapuhuiti-Bold', 'Alibabapuhuiti-Heavy'];
usedFonts.forEach(font => {
  if (!isCommercialUseAllowed(font)) {
    console.warn(`⚠️ ${font} 不允许商业使用`);
  }
});
```

## 性能优化 (Performance Optimization)

### 1. 按需加载 (Lazy Loading)

只加载需要的字体子集，减少初始加载时间。

### 2. CDN 缓存 (CDN Caching)

所有字体文件通过 CDN 分发，利用浏览器缓存和 CDN 边缘节点。

### 3. 字体分块 (Font Chunking)

大字体文件被分割成多个小块，支持按需加载。

### 4. font-display: swap

CSS 中包含 `font-display: swap`，确保文本在字体加载时立即可见。

## 包大小 (Package Size)

- **npm 包大小**: < 1MB（仅包含元数据和 API）
- **实际字体文件**: 托管在 CDN 上，不占用项目空间
- **运行时依赖**: 无外部依赖

## 浏览器支持 (Browser Support)

- Chrome/Edge: ✅
- Firefox: ✅
- Safari: ✅
- Opera: ✅
- IE 11: ⚠️ 需要 polyfill

## API 完整列表 (Complete API Reference)

| 函数 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `getAllFonts()` | - | `string[]` | 获取所有字体名称 |
| `getFontInfo(fontName)` | `fontName: string` | `FontInfo \| undefined` | 获取字体详细信息 |
| `getFontCSS(fontName, subset?)` | `fontName: string, subset?: string` | `string \| undefined` | 获取 CSS URL |
| `getFontSubsets(fontName)` | `fontName: string` | `string[]` | 获取可用子集列表 |
| `getFontChunks(fontName, subset)` | `fontName: string, subset: string` | `FontChunk[] \| undefined` | 获取字体块列表 |
| `getFontLicense(fontName)` | `fontName: string` | `FontLicense \| undefined` | 获取授权信息 |
| `getLicenseUrl(fontName)` | `fontName: string` | `string \| undefined` | 获取授权文件 URL |
| `getLicenseType(fontName)` | `fontName: string` | `string \| undefined` | 获取授权类型 |
| `getUsageRights(fontName)` | `fontName: string` | `UsageRights \| undefined` | 获取使用权限 |
| `isCommercialUseAllowed(fontName)` | `fontName: string` | `boolean` | 检查是否允许商业使用 |

## 更新日志 (Changelog)

### v1.0.0
- ✨ 初始版本发布
- 🌐 支持 CDN URL 访问
- 📦 支持多子集选择
- 📜 包含授权信息
- 💪 完整 TypeScript 支持
