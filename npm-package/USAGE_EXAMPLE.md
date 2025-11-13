# 使用示例 (Usage Examples)

## 安装 (Installation)

```bash
npm install windfonts-chinese-fonts
```

## 方法 1: 自动加载（推荐）⭐

### 1.1 使用 loadFont 函数

最简单的方式，自动注入 CSS 到页面：

```javascript
const { loadFont } = require('windfonts-chinese-fonts');

// 自动加载字体（使用默认子集 zh-common）
loadFont('Alibabapuhuiti-Bold').then(cssUrl => {
  console.log('✅ 字体已加载:', cssUrl);
  // 现在可以在页面中使用这个字体了
});

// 使用 async/await
async function init() {
  await loadFont('Alibabapuhuiti-Bold');
  // 字体已就绪
}
```

### 1.2 选择特定子集

```javascript
const { loadFont } = require('windfonts-chinese-fonts');

// 加载常用中文字符（推荐，体积小）
await loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });

// 加载完整中文字符集
await loadFont('Alibabapuhuiti-Bold', { subset: 'zh' });

// 仅加载英文字符（最小体积）
await loadFont('Alibabapuhuiti-Bold', { subset: 'en' });

// 加载完整字符集（体积最大）
await loadFont('Alibabapuhuiti-Bold', { subset: 'full' });
```

### 1.3 性能优化：预加载

```javascript
const { loadFont } = require('windfonts-chinese-fonts');

// 使用 preload 提升性能
await loadFont('Alibabapuhuiti-Bold', { 
  subset: 'zh-common',
  preload: true  // 添加 <link rel="preload">
});
```

## 方法 2: 单独导入字体（最简洁）⭐⭐

直接导入特定字体，无需记住字体名称：

```javascript
// 导入特定字体
const AlibabaBold = require('windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold');

// 直接调用即可加载
AlibabaBold().then(cssUrl => {
  console.log('✅ 字体已加载');
});

// 或使用 async/await
await AlibabaBold();

// 带选项
await AlibabaBold({ subset: 'en' });

// 访问字体信息
console.log(AlibabaBold.fontName);     // 'Alibabapuhuiti-Bold'
console.log(AlibabaBold.getSubsets()); // ['zh-common', 'en', 'zh', 'full']
console.log(AlibabaBold.info);         // 完整字体信息
```

## 方法 3: 手动获取 CSS URL

如果你想手动控制 CSS 加载：

```javascript
const { getFontCSS, getFontSubsets } = require('windfonts-chinese-fonts');

// 获取 CSS URL
const cssUrl = getFontCSS('Alibabapuhuiti-Bold', 'zh-common');
console.log(cssUrl);
// 输出: https://cn.windfonts.com/build/Alibabapuhuiti/Bold/zh-common/result.css

// 查看可用的子集
const subsets = getFontSubsets('Alibabapuhuiti-Bold');
console.log(subsets);
// 输出: ['zh-common', 'en', 'zh', 'full']

// 手动添加到 HTML
// <link rel="stylesheet" href="${cssUrl}">
```

## 框架集成 (Framework Integration)

### React 使用示例

#### 方法 A: 使用 loadFont（推荐）

```jsx
import { useEffect } from 'react';
import { loadFont } from 'windfonts-chinese-fonts';

function App() {
  useEffect(() => {
    // 自动加载字体
    loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' })
      .then(() => console.log('字体已加载'))
      .catch(err => console.error('加载失败:', err));
  }, []);

  return (
    <div style={{ fontFamily: 'Alibaba-PuHuiTi-B' }}>
      <h1>你好世界 Hello World</h1>
    </div>
  );
}
```

#### 方法 B: 直接导入字体

```jsx
import { useEffect } from 'react';
import AlibabaBold from 'windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold';

function App() {
  useEffect(() => {
    // 一行代码加载字体
    AlibabaBold();
  }, []);

  return (
    <div style={{ fontFamily: 'Alibaba-PuHuiTi-B' }}>
      <h1>你好世界 Hello World</h1>
    </div>
  );
}
```

#### 方法 C: 自定义 Hook

```jsx
import { useEffect, useState } from 'react';
import { loadFont } from 'windfonts-chinese-fonts';

function useFont(fontName, options) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadFont(fontName, options)
      .then(() => setLoaded(true))
      .catch(err => setError(err));
  }, [fontName, options?.subset]);

  return { loaded, error };
}

// 使用
function App() {
  const { loaded, error } = useFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });

  if (error) return <div>字体加载失败</div>;
  if (!loaded) return <div>加载中...</div>;

  return (
    <div style={{ fontFamily: 'Alibaba-PuHuiTi-B' }}>
      <h1>你好世界 Hello World</h1>
    </div>
  );
}
```

### Vue 使用示例

#### 方法 A: 在组件中加载

```vue
<template>
  <div :style="{ fontFamily: 'Alibaba-PuHuiTi-B' }">
    <h1>你好世界 Hello World</h1>
  </div>
</template>

<script>
import { loadFont } from 'windfonts-chinese-fonts';

export default {
  async mounted() {
    // 自动加载字体
    await loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });
    console.log('字体已加载');
  }
}
</script>
```

#### 方法 B: 直接导入

```vue
<template>
  <div :style="{ fontFamily: 'Alibaba-PuHuiTi-B' }">
    <h1>你好世界 Hello World</h1>
  </div>
</template>

<script>
import AlibabaBold from 'windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold';

export default {
  async mounted() {
    await AlibabaBold();
  }
}
</script>
```

### Next.js 使用示例

#### 在 _app.js 中全局加载

```jsx
// pages/_app.js
import { useEffect } from 'react';
import { loadFont } from 'windfonts-chinese-fonts';

function MyApp({ Component, pageProps }) {
  useEffect(() => {
    // 加载多个字体
    Promise.all([
      loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common', preload: true }),
      loadFont('Alibabapuhuiti-Regular', { subset: 'zh-common', preload: true })
    ]).then(() => {
      console.log('所有字体已加载');
    });
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;
```

#### 在特定页面加载

```jsx
// pages/index.js
import { useEffect } from 'react';
import AlibabaBold from 'windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold';

export default function Home() {
  useEffect(() => {
    AlibabaBold({ subset: 'zh-common' });
  }, []);

  return (
    <div style={{ fontFamily: 'Alibaba-PuHuiTi-B' }}>
      <h1>你好世界</h1>
    </div>
  );
}
```

### Nuxt.js 使用示例

```javascript
// plugins/fonts.client.js
import { loadFont } from 'windfonts-chinese-fonts';

export default defineNuxtPlugin(() => {
  // 在客户端加载字体
  loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });
});
```

### 7. 检查授权信息 (Check License Information)

```javascript
const { 
  getLicenseType, 
  getLicenseUrl, 
  getUsageRights, 
  isCommercialUseAllowed 
} = require('windfonts-chinese-fonts');

const fontName = 'Alibabapuhuiti-Bold';

// 获取授权类型
const licenseType = getLicenseType(fontName);
console.log(`License: ${licenseType}`);

// 获取授权文件 URL
const licenseUrl = getLicenseUrl(fontName);
console.log(`License URL: ${licenseUrl}`);

// 获取详细使用权限
const rights = getUsageRights(fontName);
console.log('Usage Rights:', rights);
// {
//   commercial: false,
//   modification: false,
//   distribution: false,
//   privateUse: true
// }

// 检查是否允许商业使用
if (isCommercialUseAllowed(fontName)) {
  console.log('✅ 可以商业使用');
} else {
  console.log('❌ 不可商业使用，请查看授权信息');
}
```

### 8. 获取所有字体列表 (Get All Fonts)

```javascript
const { getAllFonts, getFontInfo } = require('windfonts-chinese-fonts');

// 获取所有可用字体
const allFonts = getAllFonts();
console.log(`Total fonts: ${allFonts.length}`);

// 遍历所有字体
allFonts.forEach(fontName => {
  const info = getFontInfo(fontName);
  console.log(`${fontName}:`);
  console.log(`  - Family: ${info.family}`);
  console.log(`  - Subsets: ${Object.keys(info.files.subsets).join(', ')}`);
});
```

### 9. 获取字体块信息 (Get Font Chunks)

```javascript
const { getFontChunks } = require('windfonts-chinese-fonts');

// 获取特定子集的所有字体块
const chunks = getFontChunks('Alibabapuhuiti-Bold', 'zh-common');

chunks.forEach(chunk => {
  console.log(`File: ${chunk.file}`);
  console.log(`URL: ${chunk.url}`);
});
```

## 性能优化建议 (Performance Tips)

### 1. 选择合适的子集

- **zh-common**: 常用中文字符（推荐用于大多数中文网站）
- **en**: 仅英文字符（最小体积）
- **zh**: 完整中文字符集
- **full**: 包含所有字符（体积最大）

### 2. 预加载字体

```html
<!-- 在 HTML head 中预加载 -->
<link rel="preload" href="FONT_CSS_URL" as="style">
<link rel="stylesheet" href="FONT_CSS_URL">
```

### 3. 使用 font-display

字体 CSS 已经包含了 `font-display: swap` 属性，确保文本在字体加载时可见。

## TypeScript 支持 (TypeScript Support)

```typescript
import { 
  FontInfo, 
  UsageRights, 
  getAllFonts, 
  getFontInfo,
  getFontCSS,
  getFontSubsets
} from 'windfonts-chinese-fonts';

const fonts: string[] = getAllFonts();
const fontInfo: FontInfo | undefined = getFontInfo('Alibabapuhuiti-Bold');
const cssUrl: string | undefined = getFontCSS('Alibabapuhuiti-Bold', 'zh-common');
const subsets: string[] = getFontSubsets('Alibabapuhuiti-Bold');
```
