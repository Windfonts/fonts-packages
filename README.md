# 中文字体 Web 化工具

自动将中文字体转换为 Web 字体格式，支持智能分包、AI 命名规范化、多版本字符集。

## ✨ 特性

- 🚀 **一键转换** - 自动完成字体子集化、转换、分析全流程
- 🤖 **AI 智能命名** - 自动识别字体信息，生成规范化的英文名称
- 📦 **智能分包** - 按需加载，优化网页性能
- 🌐 **多版本支持** - 自动生成 full/en/zh/zh-common 四个版本
- 📊 **详细分析** - 生成字符统计、元信息、版权等详细报告
- 🔍 **联网搜索** - AI 自动搜索字体的设计师、分类、授权等信息

## 🎯 快速开始

### 1. 安装依赖

```bash
# Node.js 依赖
npm install

# Python 依赖
pip3 install fonttools openai
```

### 2. 配置 AI（可选，推荐）

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# 推荐使用火山引擎 ARK（国内访问快）
nano .env
```

### 3. 添加字体

⚠️ **重要**：字体文件必须使用 **PascalCase** 命名！

**单一字体**（直接放在 fonts/ 目录）：
```bash
fonts/
├── SourceHanSans.ttf
├── LxgwWenKai.ttf
└── ZcoolKuaiLe.ttf
```

**多变体字体**（放在文件夹中）：
```bash
fonts/
└── SourceHanSans/
    ├── Light.ttf
    ├── Regular.ttf
    ├── Medium.ttf
    └── Bold.ttf
```

**命名规则**：
- ✅ 使用 PascalCase：`SourceHanSans`、`NotoSansCJK`
- ✅ 每个单词首字母大写，无空格、连字符、下划线
- ✅ 缩写全大写：`CJK`、`SC`、`TC`
- ❌ 不要用：`source-han-sans`、`Source_Han_Sans`、`思源黑体`

**标准字重名称**：
- `Thin`、`ExtraLight`、`Light`、`Regular`、`Medium`
- `SemiBold`、`Bold`、`ExtraBold`、`Black`、`Heavy`

### 4. 一键转换

```bash
npm run build
```

完成！生成的文件在 `dist/` 目录。

## 📁 输出结构

```
dist/
├── ZhiYongHandwriting/          # AI 规范化的名称
│   ├── full/                    # 完整字符集
│   │   ├── result.css
│   │   └── *.woff2 (134个)
│   ├── en/                      # 纯英文
│   │   ├── result.css
│   │   └── *.woff2 (1个)
│   ├── zh/                      # 纯中文
│   │   ├── result.css
│   │   └── *.woff2 (130个)
│   └── zh-common/               # 常用中文（3500字）
│       ├── result.css
│       └── *.woff2 (10个)
└── HanziPinyinFont/
    └── ...

metadata/
├── font-mapping.json            # 字体名称映射和详细信息
├── font-analysis.json           # 字符统计报告
└── font-analysis.csv            # CSV 格式报告
```

## 🎨 使用字体

### 方法 1: 通过 npm 包使用（推荐）

```bash
npm install @windfonts/chinese-fonts
```

#### 自动加载字体

```javascript
const { loadFont } = require('@windfonts/chinese-fonts');

// 自动加载字体（默认使用 zh-common 子集）
await loadFont('Alibabapuhuiti-Bold');

// 指定子集
await loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });

// 预加载以提升性能
await loadFont('Alibabapuhuiti-Bold', { 
  subset: 'zh-common',
  preload: true 
});
```

#### 直接导入字体

```javascript
// 导入特定字体
const AlibabaBold = require('@windfonts/chinese-fonts/fonts/Alibabapuhuiti-Bold');

// 一行代码加载
await AlibabaBold();

// 或指定选项
await AlibabaBold({ subset: 'en' });
```

#### React 示例

```jsx
import { useEffect } from 'react';
import { loadFont } from '@windfonts/chinese-fonts';

function App() {
  useEffect(() => {
    loadFont('Alibabapuhuiti-Bold', { subset: 'zh-common' });
  }, []);

  return (
    <div style={{ fontFamily: 'Alibaba-PuHuiTi-B' }}>
      <h1>你好世界 Hello World</h1>
    </div>
  );
}
```

### 方法 2: 直接使用 CDN

```html
<!-- 引入常用中文版本（推荐） -->
<link rel="stylesheet" href="https://cn.windfonts.com/build/Alibabapuhuiti/Bold/zh-common/result.css">

<style>
  body {
    font-family: 'Alibaba-PuHuiTi-B', sans-serif;
  }
</style>
```

### 授权信息查询

```javascript
const { 
  getLicenseType, 
  getLicenseUrl, 
  isCommercialUseAllowed 
} = require('@windfonts/chinese-fonts');

// 检查授权类型
const license = getLicenseType('Alibabapuhuiti-Bold');
console.log(`License: ${license}`);

// 检查是否允许商业使用
if (isCommercialUseAllowed('Alibabapuhuiti-Bold')) {
  console.log('✅ 可以商业使用');
} else {
  console.log('❌ 不可商业使用');
}

// 获取授权文件 URL
const licenseUrl = getLicenseUrl('Alibabapuhuiti-Bold');
```

## 📊 版本对比

| 版本 | 文件大小 | 文件数量 | 适用场景 |
|------|----------|----------|----------|
| **en** | ~30KB | 1个 | 纯英文网站 |
| **zh-common** | ~230KB | 10个 | 中英文混合 ⭐ 推荐 |
| **zh** | ~3.2MB | 130个 | 纯中文内容 |
| **full** | ~3.3MB | 134个 | 需要完整字符集 |

## 🤖 AI 功能

### 自动识别字体信息

AI 会通过联网搜索获取字体的详细信息：

- ✅ **规范化名称** - 生成 PascalCase 英文名称
- ✅ **设计师信息** - 作者、工作室、发布年份
- ✅ **分类标签** - 衬线/无衬线/手写/装饰等
- ✅ **版权授权** - 商业/开源/免费等
- ✅ **详细描述** - 设计背景、特点、适用场景
- ✅ **使用建议** - 推荐的应用场景

### 示例输出

```json
{
  "normalized_name": "ZhiYongHandwriting",
  "font_family": "WF-ZhiYongHandwriting",
  "english_name": "Zhi Yong Handwriting Font",
  "chinese_name": "智勇手书体",
  "designer": "贾智勇",
  "release_year": 2017,
  "category": "handwriting",
  "license": "免费个人使用",
  "description": "智勇手书体是由设计师贾智勇于2017年创作的一款中文手写字体...",
  "tags": ["手写体", "中文书法", "个性化"],
  "use_cases": ["社交媒体设计", "文艺作品排版", "个性化印刷品"]
}
```

### 配置 AI

**火山引擎 ARK（推荐国内用户）：**

```bash
export ARK_API_KEY=your_key
export ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
export ARK_MODEL=deepseek-v3-250324
```

**OpenAI：**

```bash
export OPENAI_API_KEY=your_key
export OPENAI_MODEL=gpt-4o-mini
```

详见：[ARK API 配置指南](docs/ARK_API_SETUP.md)

## 🛠️ 常用命令

### 完整流程

```bash
npm run build              # 标准流程
npm run build:clean        # 清理后重新处理
```

### 跳过某些步骤

```bash
npm run build:skip-subset    # 跳过子集化（直接转换原始字体）
npm run build:skip-analyze   # 跳过分析（使用原始名称）
```

### 单独执行

```bash
# 查看字体详细信息
python3 scripts/analyze-fonts.py inspect fonts/字体.ttf

# 只分析字体
python3 scripts/analyze-fonts.py

# 只子集化
python3 scripts/create-font-subsets.py

# 只转换
node scripts/convert.js

# 清理
npm run clean
```

## 📖 工作流程

```
1. 字体元信息分析 (fonts/ → metadata/font-mapping.json)
   ├─ 提取字体元信息（名称、版权、设计师等）
   ├─ 使用 AI 联网搜索详细信息
   └─ 生成规范化的 PascalCase 名称

2. 字体子集化 (fonts/ → fonts-subset/)
   ├─ full: 完整字符集
   ├─ en: 纯英文
   ├─ zh: 纯中文
   └─ zh-common: 常用中文（3500字）

3. 字符统计分析 (fonts-subset/ → metadata/)
   ├─ 统计每个版本的字符数量
   ├─ 分析 Unicode 范围
   └─ 生成分析报告

4. 字体转换和分包 (fonts-subset/ → dist/)
   ├─ 使用规范化名称创建输出目录
   ├─ 转换为 woff2 格式
   ├─ 按 70KB 分包
   └─ 生成 CSS 文件
```

## ⚙️ 配置

### 修改分包大小

编辑 `scripts/convert.js` 中的 `DEFAULT_CONFIG`：

```javascript
const DEFAULT_CONFIG = {
    presets: [
        {
            chunkSize: 70,  // 修改这里（单位：KB）
            enabled: true
        }
    ]
};
```

### 修改常用字集

编辑 `scripts/create-font-subsets.py` 中的 `COMMON_CHARS_FILE`：

```python
COMMON_CHARS_FILE = 'common-chars-3500.txt'  # 3500 常用字
```

## 📚 元数据文件

### font-mapping.json

包含字体的完整信息：

```json
{
  "智勇手书体": {
    "normalized_name": "ZhiYongHandwriting",
    "font_family": "WF-ZhiYongHandwriting",
    "english_name": "Zhi Yong Handwriting Font",
    "chinese_name": "智勇手书体",
    "designer": "贾智勇",
    "foundry": "个人发布",
    "release_year": 2017,
    "category": "handwriting",
    "style": "中文手写体、书法风格、自然流畅",
    "copyright": "(C) Copyright JiaZhiyong 2017",
    "license": "免费个人使用",
    "description": "详细的字体描述...",
    "tags": ["手写体", "中文书法", "个性化"],
    "use_cases": ["社交媒体设计", "文艺作品排版"],
    "versions": {
      "default": {
        "file": "智勇手书体.ttf",
        "char_count": 7584
      }
    }
  }
}
```

### font-analysis.json

包含字符统计信息：

```json
{
  "summary": {
    "total_fonts": 5,
    "total_versions": 20
  },
  "fonts": {
    "智勇手书体": {
      "full": {
        "char_count": 7584,
        "glyph_count": 7586,
        "unicode_ranges": {
          "Basic Latin": 95,
          "CJK Unified Ideographs": 6763
        },
        "characters": "完整的字符串..."
      }
    }
  }
}
```

## 🔍 调试

### 查看字体元信息

```bash
python3 scripts/analyze-fonts.py inspect fonts/字体.ttf
```

输出：
- 完整的 Name Table 信息
- JSON 格式的元数据
- AI 规范化结果

### 查看映射文件

```bash
cat metadata/font-mapping.json | python3 -m json.tool
```

### 查看日志

所有脚本都有详细的日志输出，包括时间戳、日志级别、操作详情。

## 📈 性能优化

### 文件大小优化

- ✅ **智能分包** - 按 70KB 分包，按需加载
- ✅ **woff2 格式** - 比 ttf 小 30-50%
- ✅ **字符子集** - 只包含需要的字符

### 加载速度优化

- ✅ **CSS 预加载** - 使用 `<link rel="preload">`
- ✅ **CDN 加速** - 部署到 CDN
- ✅ **版本选择** - 根据场景选择合适的版本

### 推荐配置

```html
<!-- 预加载 CSS -->
<link rel="preload" href="dist/ZhiYongHandwriting/zh-common/result.css" as="style">
<link rel="stylesheet" href="dist/ZhiYongHandwriting/zh-common/result.css">

<!-- 或使用 CDN -->
<link rel="stylesheet" href="https://cdn.example.com/fonts/ZhiYongHandwriting/zh-common/result.css">
```

## 🚨 常见问题

### Q: 为什么输出目录名称是英文？

A: 使用 AI 自动生成规范化的英文名称，便于：
- 跨平台兼容（避免中文路径问题）
- URL 友好（可以直接用于 CDN）
- 代码规范（符合命名规范）

### Q: 如何关闭 AI 功能？

A: 不设置 API Key 即可，会自动使用降级模式（简单的名称规范化）。

### Q: 生成的文件太多怎么办？

A: 
1. 只使用需要的版本（如 zh-common）
2. 增加分包大小（修改 `chunkSize`）
3. 使用 CDN 部署，按需加载

### Q: 如何添加自定义字符集？

A: 编辑 `scripts/create-font-subsets.py`，添加自定义字符列表。

### Q: 字体版权问题？

A: 
- AI 会自动识别字体的授权信息
- 请查看 `metadata/font-mapping.json` 中的 `license` 字段
- 使用前请确认字体的授权范围

## 📦 项目结构

```
font-packages/
├── fonts/                       # 原始字体文件
├── fonts-subset/                # 子集化字体（临时）
├── dist/                        # 转换后的 Web 字体
├── metadata/                    # 元数据和分析报告
├── scripts/                     # 处理脚本
│   ├── analyze-fonts.py         # 字体分析和 AI 规范化
│   ├── create-font-subsets.py   # 字体子集化
│   ├── convert.js               # 字体转换和分包
│   ├── build.js                 # 一体化构建脚本
│   └── clean.js                 # 清理脚本
├── docs/                        # 文档
├── .env                         # 环境变量（需自行创建）
├── .env.example                 # 环境变量模板
├── package.json                 # Node.js 配置
└── README.md                    # 本文件
```

## 📦 发布流程

### 自动发布（推荐）

配置 GitHub Actions / Forgejo Actions 后，推送字体文件即可自动发布：

```bash
# 1. 添加字体（使用 PascalCase 命名）
cp font.ttf fonts/SourceHanSans.ttf

# 2. 提交并推送
git add fonts/
git commit -m "feat: add SourceHanSans font"
git push origin main

# 3. 自动执行：构建 → 上传 OSS → 发布 npm → 提交元数据
```

**工作流程**：
1. **构建字体**：`node scripts/build.js`
2. **上传 OSS**：`node scripts/upload.js`
3. **发布 npm**：`node scripts/publish.js`
4. **提交元数据**：自动提交到 Git

### 手动发布

```bash
# 1. 构建字体
node scripts/build.js

# 2. 上传到 OSS
node scripts/upload.js

# 3. 发布 npm 包
node scripts/publish.js

# 4. 提交元数据
git add metadata/ npm-package/
git commit -m "chore: update font metadata"
git push
```

### 配置 CI/CD

详细配置请查看：[.forgejo/SECRETS_GUIDE_CN.md](.forgejo/SECRETS_GUIDE_CN.md)

**必需的 Secrets**：
- OSS 配置：`OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`、`OSS_BUCKET`、`OSS_REGION`、`OSS_ENDPOINT`、`OSS_BASE_PATH`
- NPM 配置：`NPM_TOKEN`
- AI 配置（可选）：`AI_API_KEY`、`AI_API_ENDPOINT`、`AI_MODEL`

## 🔗 相关文档

### ⚙️ CI/CD 配置
- [Secrets 配置指南](.forgejo/SECRETS_GUIDE_CN.md) - 🌟 详细的 Secrets 配置（推荐）
- [快速配置清单](.forgejo/QUICK_SETUP.md) - 快速配置 Forgejo Actions
- [测试指南](.forgejo/TESTING.md) - 测试工作流
- [兼容性说明](.forgejo/COMPATIBILITY.md) - GitHub/Forgejo 兼容性

## 📝 更新日志

- [AI 联网搜索功能](CHANGELOG-ai-web-search.md) - AI 自动搜索字体详细信息
- [工作流程优化](CHANGELOG-workflow-reorder.md) - 元信息分析前置
- [元信息识别整合](CHANGELOG-inspect-integration.md) - 整合字体检查功能
- [降级逻辑优化](CHANGELOG-fallback-to-filename.md) - 使用原始文件名
- [配置文件移除](CHANGELOG-remove-config-file.md) - 简化配置
- [JSON 优化](CHANGELOG-optimize-analysis-json.md) - 减小文件体积

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

GPL-3.0 - 详见 [LICENSE](LICENSE) 文件

---

**提示**: 首次使用建议查看 [快速开始指南](QUICK_START.md)
