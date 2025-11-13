# 快速开始 (Quick Start)

## 🚀 30 秒上手

### 1. 安装

```bash
npm install windfonts-chinese-fonts
```

### 2. 使用（三种方式任选其一）

#### 方式 A: 最简单 - 直接导入字体 ⭐⭐⭐

```javascript
// 导入字体
const AlibabaBold = require('windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold');

// 加载字体（一行代码）
await AlibabaBold();

// 现在可以使用了！
// CSS: font-family: 'Alibaba-PuHuiTi-B';
```

#### 方式 B: 使用 loadFont 函数

```javascript
const { loadFont } = require('@your-org/chinese-fonts');

// 加载字体
await loadFont('Alibabapuhuiti-Bold');

// 完成！
```

#### 方式 C: 手动获取 URL

```javascript
const { getFontCSS } = require('windfonts-chinese-fonts');

// 获取 CSS URL
const cssUrl = getFontCSS('Alibabapuhuiti-Bold');
console.log(cssUrl);
// https://cn.windfonts.com/build/Alibabapuhuiti/Bold/zh-common/result.css

// 手动添加到 HTML
// <link rel="stylesheet" href="${cssUrl}">
```

## 📦 在项目中使用

### React 项目

```jsx
import { useEffect } from 'react';
import AlibabaBold from 'windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold';

function App() {
  useEffect(() => {
    AlibabaBold(); // 自动加载
  }, []);

  return (
    <h1 style={{ fontFamily: 'Alibaba-PuHuiTi-B' }}>
      你好世界
    </h1>
  );
}
```

### Vue 项目

```vue
<template>
  <h1 :style="{ fontFamily: 'Alibaba-PuHuiTi-B' }">
    你好世界
  </h1>
</template>

<script>
import AlibabaBold from 'windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold';

export default {
  mounted() {
    AlibabaBold(); // 自动加载
  }
}
</script>
```

### 原生 JavaScript

```html
<!DOCTYPE html>
<html>
<head>
  <title>字体示例</title>
</head>
<body>
  <h1 style="font-family: 'Alibaba-PuHuiTi-B'">你好世界</h1>

  <script>
    // 如果使用打包工具（webpack/vite）
    const { loadFont } = require('windfonts-chinese-fonts');
    loadFont('Alibabapuhuiti-Bold');
  </script>
</body>
</html>
```

## 🎯 常见场景

### 场景 1: 加载多个字体

```javascript
const { loadFont } = require('windfonts-chinese-fonts');

// 并行加载多个字体
await Promise.all([
  loadFont('Alibabapuhuiti-Bold'),
  loadFont('Alibabapuhuiti-Regular'),
  loadFont('Hanzipinyin')
]);

console.log('所有字体已加载！');
```

### 场景 2: 选择不同子集

```javascript
const AlibabaBold = require('windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold');

// 常用中文（推荐，体积小）
await AlibabaBold({ subset: 'zh-common' });

// 完整中文
await AlibabaBold({ subset: 'zh' });

// 仅英文（最小）
await AlibabaBold({ subset: 'en' });

// 完整字符集（最大）
await AlibabaBold({ subset: 'full' });
```

### 场景 3: 性能优化

```javascript
const { loadFont } = require('windfonts-chinese-fonts');

// 使用 preload 提升性能
await loadFont('Alibabapuhuiti-Bold', {
  subset: 'zh-common',
  preload: true  // 添加预加载
});
```

### 场景 4: 检查授权

```javascript
const { isCommercialUseAllowed, getLicenseType } = require('windfonts-chinese-fonts');

const fontName = 'Alibabapuhuiti-Bold';

if (isCommercialUseAllowed(fontName)) {
  console.log('✅ 可以商业使用');
} else {
  console.log('❌ 不可商业使用');
  console.log('授权类型:', getLicenseType(fontName));
}
```

## 📋 可用字体列表

```javascript
const { getAllFonts } = require('windfonts-chinese-fonts');

// 获取所有字体
const fonts = getAllFonts();
console.log(fonts);
// ['Alibabapuhuiti-Bold', 'Alibabapuhuiti-Regular', ...]
```

## 🔍 查看字体信息

```javascript
const AlibabaBold = require('windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold');

// 字体名称
console.log(AlibabaBold.fontName);
// 'Alibabapuhuiti-Bold'

// 可用子集
console.log(AlibabaBold.getSubsets());
// ['zh-common', 'en', 'zh', 'full']

// 获取 CSS URL（不加载）
console.log(AlibabaBold.getCSS('zh-common'));
// 'https://cn.windfonts.com/...'

// 完整信息
console.log(AlibabaBold.info);
// { name, family, subfamily, charCount, ... }
```

## ⚡ 性能建议

1. **选择合适的子集**
   - `zh-common`: 常用 3500 字（推荐）
   - `en`: 仅英文（最小）
   - `zh`: 完整中文
   - `full`: 所有字符（最大）

2. **使用 preload**
   ```javascript
   loadFont('FontName', { preload: true });
   ```

3. **按需加载**
   只在需要时加载字体，不要一次性加载所有字体

4. **缓存**
   字体会自动缓存，重复调用不会重复加载

## 🆘 常见问题

### Q: 字体没有显示？
A: 确保 CSS 中的 font-family 名称正确，可以通过 `font.info.name` 查看

### Q: 如何在服务端渲染中使用？
A: loadFont 在服务端会直接返回 URL，不会尝试操作 DOM

### Q: 可以离线使用吗？
A: 不可以，字体托管在 CDN 上，需要网络连接

### Q: 如何查看字体的授权信息？
A: 使用 `getLicenseType()` 和 `getUsageRights()` 函数

## 📚 更多文档

- [完整 API 文档](./FEATURES.md)
- [详细使用示例](./USAGE_EXAMPLE.md)
- [README](./README.md)
