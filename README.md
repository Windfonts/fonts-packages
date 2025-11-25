# 中文字体 Web 化工具

自动将中文字体转换为 Web 字体格式，支持智能分包、AI 命名规范化、多版本字符集。

## ✨ 特性

- 🤖 **AI 智能命名** - 自动识别字体信息，生成规范化的英文名称
- 📦 **智能分包** - 按需加载，优化网页性能
- 🌐 **多版本支持** - 自动生成 full/en/zh/zh-common 四个版本
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
nano .env
```

### 3. 添加字体

将字体文件（TTF/OTF 格式）放入 `fonts/` 目录

### 4. 构建字体

```bash
# 完整流程
npm run build

# 或分步执行
npm run analyze  # 分析字体并生成规范化名称
npm run subset   # 创建字体子集
npm run convert  # 转换为 Web 字体格式
```

## 🛠️ 命令

```bash
npm run analyze  # 分析字体并生成规范化名称（Python）
npm run subset   # 创建字体子集（Python）
npm run convert  # 转换为 Web 字体格式（Node.js）
npm run build    # 完整流程（analyze + subset + convert）
npm run upload   # 上传到 OSS
npm run publish  # 发布到 npm
npm run clean    # 清理生成文件
```

### 测试模式

```bash
# 只处理前 2 个字体（快速测试）
python3 python-scripts/analyze-fonts.py test 2

# 只处理前 5 个字体
python3 python-scripts/analyze-fonts.py test 5

# 查看单个字体详细信息
python3 python-scripts/analyze-fonts.py inspect fonts/字体.ttf
```

## 📁 项目结构

```
python-scripts/              # Python 脚本
├── analyze-fonts.py         # 字体分析和 AI 规范化
└── create-font-subsets.py   # 字体子集化

scripts/                     # Node.js 脚本
├── convert.js               # 字体转换和分包
├── upload.js                # 上传到 OSS
├── publish.js               # 发布到 npm
└── clean.js                 # 清理脚本

fonts/                       # 原始字体文件
fonts-subset/                # 子集化字体（临时）
dist/                        # 转换后的 Web 字体
metadata/                    # 元数据和分析报告
```

## 📖 工作流程

```
1. analyze (Python)
   ├─ 扫描 fonts/ 目录
   ├─ 使用 AI 生成规范化名称
   └─ 生成 metadata/font-mapping.json

2. subset (Python)
   ├─ 读取 metadata/font-mapping.json
   ├─ 创建 4 个版本（full/en/zh/zh-common）
   └─ 输出到 fonts-subset/

3. convert (Node.js)
   ├─ 读取 fonts-subset/
   ├─ 转换为 woff2 格式
   ├─ 按 70KB 分包
   └─ 输出到 dist/
```

## 🏷️ 字体字重命名规则

**重要原则：字重名称以文件名为准（人工定义的），不进行自动映射转换。**

这确保了 `metadata/font-mapping.json` 中的字重名称与 `dist/` 目录中的字重文件夹名称完全一致。

### 示例

```
fonts/Hxbsb/Normal.ttf  →  字重名称: "Normal"  →  dist/Hxbsb/Normal/
```

不会被转换为 `Regular`，保持原始文件名。

### 常见字重对应

| 文件名 | 字重名称 | CSS font-weight |
|--------|----------|-----------------|
| Normal.ttf | Normal | 400 |
| Regular.ttf | Regular | 400 |
| Heavy.ttf | Heavy | 900 |
| Extralight.ttf | Extralight | 200 |
| Semibold.ttf | Semibold | 600 |

### font_family 命名规则

- **Regular/Normal 字重**：`WF-{family_name}`
- **其他字重**：`WF-{family_name}-{weight_name}`

## 📄 License

GPL-3.0
