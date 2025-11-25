# Python Scripts

字体分析和子集化脚本

## 脚本说明

- `analyze-fonts.py` - 分析字体并使用 AI 生成规范化名称
- `create-font-subsets.py` - 创建字体子集（full/en/zh/zh-common）

## 使用方式

```bash
# 分析字体
python3 python-scripts/analyze-fonts.py

# 创建子集
python3 python-scripts/create-font-subsets.py
```

## 输出

- `metadata/font-mapping.json` - 字体映射和元数据
- `fonts-subset/` - 子集化后的字体文件
