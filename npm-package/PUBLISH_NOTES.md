# 发布说明 (Publish Notes)

## 版本信息
- **包名**: windfonts-chinese-fonts
- **版本**: 1.0.2
- **发布日期**: 准备中

## 包含的字体 (8个)

1. **Alibabapuhuiti-Bold** - 阿里巴巴普惠体 粗体
2. **Alibabapuhuiti-Heavy** - 阿里巴巴普惠体 特粗
3. **Alibabapuhuiti-Regular** - 阿里巴巴普惠体 常规
4. **Hanzipinyin** - 汉字拼音体
5. **Huxiaobosaobao** - 胡晓波骚包体
6. **Linhailishu** - 林海隶书
7. **Liujiangmaocao** - 刘江毛草
8. **Zhiyongshoushuti** - 智勇手书体

## 包大小
- 压缩后: 10.9 kB
- 解压后: 156.1 kB

## 主要功能

### 1. 自动加载字体
```javascript
const { loadFont } = require('windfonts-chinese-fonts');
await loadFont('Alibabapuhuiti-Bold');
```

### 2. 单独导入字体
```javascript
const AlibabaBold = require('windfonts-chinese-fonts/fonts/Alibabapuhuiti-Bold');
await AlibabaBold();
```

### 3. 获取CDN URL
```javascript
const { getFontCSS } = require('windfonts-chinese-fonts');
const cssUrl = getFontCSS('Alibabapuhuiti-Bold', 'zh-common');
```

### 4. 授权信息查询
```javascript
const { isCommercialUseAllowed, getLicenseType } = require('windfonts-chinese-fonts');
console.log(getLicenseType('Alibabapuhuiti-Bold'));
```

## 发布前检查清单

- [x] 包名已更新为 windfonts-chinese-fonts
- [x] 仓库地址已更新为 https://github.com/Windfonts/font-packages.git
- [x] 作者信息已更新为 WindFonts
- [x] 版本号已递增 (1.0.1 -> 1.0.2)
- [x] 所有8个字体都已包含
- [x] TypeScript类型定义已生成
- [x] README文档已生成
- [x] 个别字体加载器已生成
- [x] fonts.json元数据已生成
- [x] npm pack测试通过

## 发布命令

### 测试发布（推荐先执行）
```bash
node scripts/publish.js --dry-run
```

### 正式发布
```bash
# 确保已设置 NPM_TOKEN 环境变量
export NPM_TOKEN=your_npm_token

# 执行发布
node scripts/publish.js
```

或者手动发布：
```bash
cd npm-package
npm publish --access public
```

## 发布后验证

1. 检查npm包页面: https://www.npmjs.com/package/windfonts-chinese-fonts
2. 测试安装:
   ```bash
   npm install windfonts-chinese-fonts
   ```
3. 测试使用:
   ```javascript
   const { getAllFonts } = require('windfonts-chinese-fonts');
   console.log(getAllFonts());
   ```

## 注意事项

1. 确保NPM_TOKEN已正确配置
2. 首次发布需要使用 `--access public` 参数
3. 发布后版本号无法修改，请谨慎操作
4. 建议先使用 `--dry-run` 测试

## CDN信息

所有字体文件托管在: https://cn.windfonts.com/build/

## 相关文档

- [快速开始](./QUICK_START.md)
- [使用示例](./USAGE_EXAMPLE.md)
- [功能说明](./FEATURES.md)
- [README](./README.md)
