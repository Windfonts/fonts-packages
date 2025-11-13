#!/usr/bin/env python3

import sys
import os
import json
import csv
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, Optional

# ============================================================================
# 环境变量配置管理（内置版本，不依赖外部文件）
# ============================================================================

class EnvConfig:
    """环境变量配置管理器 - 直接从 .env 文件读取，不使用系统环境变量缓存"""
    
    def __init__(self, env_file: Optional[Path] = None):
        if env_file is None:
            self.env_file = Path(__file__).parent.parent / '.env'
        else:
            self.env_file = env_file
        
        self._config: Dict[str, str] = {}
        self._load_env()
    
    def _load_env(self):
        """从 .env 文件加载配置"""
        if not self.env_file.exists():
            return
        
        with open(self.env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                    
                    self._config[key] = value
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set_env(self):
        """将配置设置到当前进程的环境变量中"""
        for key, value in self._config.items():
            os.environ[key] = value

# 加载配置并设置到环境变量
try:
    config = EnvConfig()
    config.set_env()
    print(f"✓ 已从 .env 文件加载配置")
except Exception as e:
    print(f"⚠ 警告: 加载 .env 文件失败: {e}")
    config = None

try:
    from fontTools.ttLib import TTFont
except ImportError:
    print("错误: 需要安装 fonttools")
    print("请运行: pip3 install fonttools")
    sys.exit(1)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def load_category_config():
    config_path = Path(__file__).parent.parent / 'config' / 'category.json'
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"警告: 无法加载 category.json: {e}")
    return None

CATEGORY_CONFIG = load_category_config()

class AIFontNormalizer:
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.use_bot_api = False
        
        if not OPENAI_AVAILABLE:
            return
        
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('ARK_API_KEY')
        if not api_key:
            return
        
        base_url = (
            os.getenv('OPENAI_BASE_URL') or 
            os.getenv('ARK_BASE_URL') or
            'https://api.openai.com/v1'
        )
        
        if '/bots' in base_url or os.getenv('USE_BOT_API') == 'true':
            self.use_bot_api = True
        
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=60.0
            )
            self.enabled = True
        except Exception as e:
            print(f"警告: AI 客户端初始化失败: {e}")
    
    def _build_category_options(self):
        """构建分类选项文本"""
        if not CATEGORY_CONFIG:
            return ""
        
        category_list = CATEGORY_CONFIG.get('category', [])
        tags_list = CATEGORY_CONFIG.get('tags', [])
        languages_list = CATEGORY_CONFIG.get('languages', [])
        license_list = CATEGORY_CONFIG.get('licenseTypes', [])
        
        return f"""

预定义的分类选项（请从中选择最匹配的）：

**字体分类 (font_category)**：
{json.dumps(category_list, ensure_ascii=False)}

**字体标签 (font_tags)**：
{json.dumps(tags_list, ensure_ascii=False)}

**支持语言 (languages)**：
{json.dumps(languages_list, ensure_ascii=False)}

**授权类型 (license_type)**：
{json.dumps(license_list, ensure_ascii=False)}
"""
    
    def _build_common_rules(self):
        """构建通用规则文本"""
        search_instruction = ""
        if self.use_bot_api:
            search_instruction = """
## 🔍 互联网搜索（必须执行）

**搜索要求：**
- 必须主动搜索字体名称获取详细信息
- 搜索多个关键词组合：
  * "[字体名] 字体"
  * "[字体名] font"  
  * "[字体名] 设计师"
  * "[字体名] license 授权"
  * "[字体名] GitHub"

**搜索目标：**
- 设计师/作者姓名
- 字体厂商/工作室
- 发布年份
- 授权类型（开源/免费商用/付费等）
- 字体设计背景和特点
- 适用场景

**搜索来源优先级：**
1. 官方网站
2. GitHub 仓库
3. Google Fonts
4. 字体设计网站
5. 可靠的字体资源站

**重要：所有缺失字段必须尝试通过搜索补全！**
"""
        
        return f"""{search_instruction}

## 元信息优先原则
- 如果元信息中有 designer, copyright, version, trademark 等字段，必须直接使用原值
- 不要修改、翻译或替换元信息中已有的字段

## 版本号格式
- 使用标准的语义化版本格式：主版本号.次版本号.修订号
- 转换规则：
  * "Version 1.00" → "1.0.0"
  * "v2.5" → "2.5.0"
  * "3" → "3.0.0"
- 如果无法提取，使用 "1.0.0"

## 分类和标签
- font_category, font_tags, languages, license_type 必须从预定义列表中选择
- tags 可以是自由标签
- 如果信息缺失，设置为 null（不要编造）

## 推理和补全
- 优先使用字体元信息中已有的字段
- 如果元信息缺失，可以根据字体名称、设计风格等进行合理推理
- 可以推断字体的设计师、发布年份、适用场景等
- 提供详细的字体描述，包括设计背景、特点、适用场景
- 如果完全无法推断，再设置为 null
"""
    
    def _build_weight_rules(self):
        """构建字重识别规则文本"""
        return """
## 字重识别规则

从以下字段中识别字重（优先级从高到低）：
1. subfamily_name（最常用）
2. typographic_subfamily
3. full_name 中的字重部分
4. postscript_name 中的字重部分

**字重映射表**：
- Thin / Hairline / UltraLight → weight_name: "Thin", font_weight: 100
- ExtraLight / Extra Light / Ultra Light → weight_name: "ExtraLight", font_weight: 200
- Light → weight_name: "Light", font_weight: 300
- Regular / Normal / Book / Roman → weight_name: "Regular", font_weight: 400
- Medium → weight_name: "Medium", font_weight: 500
- SemiBold / Semi Bold / DemiBold / Demi Bold → weight_name: "SemiBold", font_weight: 600
- Bold → weight_name: "Bold", font_weight: 700
- ExtraBold / Extra Bold / UltraBold / Ultra Bold → weight_name: "ExtraBold", font_weight: 800
- Black / Heavy / Ultra / Fat → weight_name: "Black", font_weight: 900

**font_family 命名规则**：
- Regular: "WF-{normalized_name}" （不加字重后缀）
- 其他: "WF-{normalized_name}-{weight_name}"
"""
    
    def normalize_font_family(self, font_family_info: Dict) -> Dict:
        """
        规范化字体家族
        只使用第一个字体的元信息调用 AI，字重信息直接从文件名提取
        """
        if not self.enabled:
            return self._fallback_normalize_family(font_family_info)
        
        family_name = font_family_info.get('family_name', '')
        weights_info = font_family_info.get('weights', {})
        
        # 获取第一个字体的元信息
        first_weight_name = list(weights_info.keys())[0] if weights_info else None
        if not first_weight_name:
            return self._fallback_normalize_family(font_family_info)
        
        first_weight_data = weights_info.get(first_weight_name, {})
        first_metadata = first_weight_data.get('metadata', {})
        
        # 构建字体信息（和单个字体一样的格式）
        font_info = {
            'file_name': first_metadata.get('file_name', ''),
            'file_stem': family_name,  # 使用文件夹名作为 stem
            'family_name': first_metadata.get('family_name', family_name),
            'subfamily_name': first_metadata.get('subfamily_name', ''),
            'full_name': first_metadata.get('full_name', ''),
            'postscript_name': first_metadata.get('postscript_name', ''),
            'typographic_family': first_metadata.get('typographic_family', ''),
            'typographic_subfamily': first_metadata.get('typographic_subfamily', ''),
            'designer': first_metadata.get('designer', ''),
            'manufacturer': first_metadata.get('manufacturer', ''),
            'copyright': first_metadata.get('copyright', ''),
            'description': first_metadata.get('description', ''),
            'version': first_metadata.get('version', '')
        }
        
        try:
            # 使用和单个字体相同的方法获取 AI 分析结果
            result = self.normalize_font_name(font_info)
            
            # 强制使用文件夹名作为 normalized_name
            result['normalized_name'] = family_name
            result['font_family'] = f'WF-{family_name}'
            
            # 不需要 AI 返回的 weight_name 和 font_weight（我们用文件名）
            if 'weight_name' in result:
                del result['weight_name']
            if 'font_weight' in result:
                del result['font_weight']
            
            return result
            
        except Exception as e:
            import traceback
            print(f"  警告: AI 规范化失败，使用降级模式: {e}")
            print(f"  错误详情: {traceback.format_exc()}")
            return self._fallback_normalize_family(font_family_info)
    
    def normalize_font_name(self, font_info: Dict) -> Dict:
        if not self.enabled:
            return self._fallback_normalize(font_info)
        
        file_stem = font_info.get('file_stem', '')
        
        try:
            model = os.getenv('OPENAI_MODEL') or os.getenv('ARK_MODEL') or 'gpt-4o-mini'
            
            font_info_summary = {
                'file_name': font_info.get('file_name', ''),
                'family_name': font_info.get('family_name', ''),
                'subfamily_name': font_info.get('subfamily_name', ''),
                'full_name': font_info.get('full_name', ''),
                'postscript_name': font_info.get('postscript_name', ''),
                'typographic_family': font_info.get('typographic_family', ''),
                'typographic_subfamily': font_info.get('typographic_subfamily', ''),
                'designer': font_info.get('designer', ''),
                'manufacturer': font_info.get('manufacturer', ''),
                'copyright': font_info.get('copyright', ''),
                'description': font_info.get('description', ''),
                'version': font_info.get('version', '')
            }
            
            font_info_summary = {k: v for k, v in font_info_summary.items() if v}
            
            search_hint = ""
            if self.use_bot_api:
                font_name_for_search = font_info_summary.get('family_name', '') or font_info_summary.get('full_name', '')
                manufacturer = font_info_summary.get('manufacturer', '')
                copyright_info = font_info_summary.get('copyright', '')
                
                search_hint = f"""
# 🔍 第一步：互联网搜索（必须执行）

**搜索策略**：
1. 先搜索字体的官方名称和设计师/厂商信息
2. 搜索多个关键词组合以获取全面信息：
   - "{font_name_for_search} 字体 介绍"
   - "{font_name_for_search} font designer"
   - "{font_name_for_search} 授权 license"
   - "{font_name_for_search} GitHub repository"
   - "{manufacturer} {font_name_for_search}" (如果有厂商信息)

**搜索重点**：
- 🎨 设计师/作者的完整姓名
- 🏢 字体厂商/工作室/公司名称
- 📅 首次发布年份
- 📜 授权类型（开源协议/免费商用/个人免费/付费等）
- 📝 字体的设计背景、特点、风格描述
- 🎯 典型使用场景和应用领域
- 🌐 官方网站或 GitHub 链接

**搜索来源优先级**：
1. 官方网站和官方文档
2. GitHub 仓库（README、LICENSE 文件）
3. Google Fonts / Adobe Fonts 等字体平台
4. 字体设计网站（如 MyFonts、FontSquirrel）
5. 可靠的字体资源站和设计社区

**重要提示**：
- 如果元信息中已有 designer、manufacturer、copyright 等字段，优先使用这些信息作为搜索线索
- 搜索结果必须用于补全所有缺失字段（designer、foundry、release_year、description 等）
- 不要编造信息，如果搜索不到就设为 null
"""
            
            prompt = f"""你是一个专业的字体信息规范化和分析专家。请结合字体元信息和互联网搜索，提供完整准确的字体信息。

{search_hint}

# 字体元信息（已从字体文件中提取）
{json.dumps(font_info_summary, ensure_ascii=False, indent=2)}

{self._build_category_options()}

# 分析任务

## 第一步：信息收集
1. **分析元信息**：仔细阅读上面的字体元信息，提取已有的关键信息
2. **互联网搜索**：基于字体名称、设计师、厂商等信息进行搜索，获取缺失的详细信息
3. **交叉验证**：将元信息和搜索结果进行对比验证，确保信息准确性

## 第二步：信息推理与补全
根据以下优先级补全字段：
1. **直接使用**：元信息中已有的字段（designer、copyright、version、manufacturer 等）
2. **搜索补全**：通过互联网搜索获取的信息（release_year、license_type、详细 description 等）
3. **合理推理**：基于字体名称、风格特征进行推断（font_category、font_tags、languages 等）
4. **设为 null**：完全无法获取或推断的信息

## 第三步：字段说明

**必填字段**：
- normalized_name: PascalCase 格式的英文名称（如 AlibabaPuHuiTi）
- font_family: "WF-" + normalized_name + 字重后缀
- weight_name, font_weight: 从 subfamily_name 识别字重
- font_category: 从预定义列表选择（无衬线/衬线/手写体等）
- font_tags: 从预定义列表选择标签数组
- languages: 从预定义列表选择支持的语言数组
- license_type: 从预定义列表选择授权类型

**可选字段（尽量补全）**：
- english_name: 字体的英文名称
- chinese_name: 字体的中文名称
- designer: 设计师姓名（优先使用元信息，其次搜索）
- foundry: 字体厂商/工作室名称
- release_year: 首次发布年份（数字，如 2019）
- description: 详细描述（200-300字，包含设计背景、特点、风格）
- copyright: 版权信息（优先使用元信息）
- license: 具体授权协议名称（如 OFL、Apache 2.0）
- version: 版本号（标准格式如 1.0.0）
- tags: 自由标签数组
- use_cases: 使用场景数组

{self._build_weight_rules()}

{self._build_common_rules()}

## 输出要求
返回完整的 JSON 对象，包含所有字段。对于无法获取的信息，设置为 null（不要编造）。
"""
            
            system_message = """你是一个专业的字体信息分析和规范化专家，擅长：
1. 分析字体文件的元信息（metadata）
2. 使用互联网搜索获取字体的详细背景信息
3. 结合元信息和搜索结果，提供准确完整的字体信息
4. 对缺失信息进行合理推理和补全

工作原则：
- 优先使用字体元信息中的原始数据
- 主动搜索字体名称、设计师、厂商等关键词
- 将搜索结果与元信息交叉验证
- 提供详实的字体描述和使用建议
- 对无法确定的信息诚实地标记为 null"""
            
            if self.use_bot_api:
                system_message += "\n\n你拥有互联网搜索能力，请务必主动搜索以获取：设计师姓名、字体厂商、发布年份、授权类型、设计背景、使用场景等信息。不要猜测，要基于搜索结果。"
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get('normalized_name') == 'UnknownFont':
                if file_stem:
                    print(f"  ⚠ AI 返回 UnknownFont，使用原始文件名: {file_stem}")
                    result['normalized_name'] = file_stem
                    result['font_family'] = f"WF-{file_stem}"
                    result['description'] = f"AI 无法识别，使用原始文件名: {file_stem}"
                else:
                    print(f"  ⚠ AI 返回 UnknownFont，且无文件名可用")
            
            return result
            
        except Exception as e:
            print(f"  警告: AI 规范化失败，使用降级模式: {e}")
            return self._fallback_normalize(font_info)
    
    def _fallback_normalize_family(self, font_family_info: Dict) -> Dict:
        """降级模式：不使用 AI，直接从元信息提取"""
        family_name = font_family_info.get('family_name', 'Unknown')
        weights_info = font_family_info.get('weights', {})
        
        normalized_name = family_name if family_name != 'Unknown' else 'UnknownFont'
        
        # 从第一个字重提取元信息
        first_weight_data = next(iter(weights_info.values()), {}) if weights_info else {}
        first_metadata = first_weight_data.get('metadata', {})
        
        return {
            "normalized_name": normalized_name,
            "font_family": f"WF-{normalized_name}",
            "original_name": family_name,
            "description": family_name,
            "designer": first_metadata.get('designer'),
            "copyright": first_metadata.get('copyright'),
            "version": first_metadata.get('version'),
            "manufacturer": first_metadata.get('manufacturer'),
            "license": first_metadata.get('license'),
        }
    
    def _fallback_normalize(self, font_info: Dict) -> Dict:
        family_name = font_info.get('family_name', 'Unknown')
        file_stem = font_info.get('file_stem', family_name)
        
        clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', family_name)
        
        normalized_name = ''
        
        if clean_name and re.search(r'[\u4e00-\u9fff]', clean_name):
            normalized_name = file_stem
        elif clean_name:
            words = re.findall(r'[A-Z][a-z]*|[a-z]+', clean_name)
            if words:
                normalized_name = ''.join(word.capitalize() for word in words)
        
        if not normalized_name:
            normalized_name = file_stem if file_stem else 'UnknownFont'
        
        return {
            "normalized_name": normalized_name,
            "font_family": f"WF-{normalized_name}",
            "original_name": family_name,
            "copyright": font_info.get('copyright'),
            "designer": font_info.get('designer'),
            "version": font_info.get('version'),
            "description": family_name
        }


NAME_IDS = {
    0: 'copyright',
    1: 'family_name',
    2: 'subfamily_name',
    3: 'unique_id',
    4: 'full_name',
    5: 'version',
    6: 'postscript_name',
    7: 'trademark',
    8: 'manufacturer',
    9: 'designer',
    10: 'description',
    11: 'vendor_url',
    12: 'designer_url',
    13: 'license',
    14: 'license_url',
    16: 'typographic_family',
    17: 'typographic_subfamily',
    18: 'compatible_full',
    21: 'wws_family',
    22: 'wws_subfamily'
}

NAME_DISPLAY = {
    0: 'Copyright',
    1: 'Family Name',
    2: 'Subfamily Name',
    3: 'Unique ID',
    4: 'Full Name',
    5: 'Version',
    6: 'PostScript Name',
    7: 'Trademark',
    8: 'Manufacturer',
    9: 'Designer',
    10: 'Description',
    11: 'Vendor URL',
    12: 'Designer URL',
    13: 'License',
    14: 'License URL',
    16: 'Typographic Family',
    17: 'Typographic Subfamily',
    18: 'Compatible Full',
    21: 'WWS Family',
    22: 'WWS Subfamily'
}

def extract_font_metadata(font_path: Path, verbose: bool = False) -> Dict:
    try:
        font = TTFont(font_path)
        name_table = font['name']
        metadata = {'all_names': {}}
        
        records_by_id = {}
        
        for record in name_table.names:
            try:
                value = record.toUnicode()
                name_id = record.nameID
                
                if not value or value == '?':
                    continue
                
                field_name = NAME_IDS.get(name_id, f'name_id_{name_id}')
                
                if field_name not in metadata['all_names']:
                    metadata['all_names'][field_name] = []
                metadata['all_names'][field_name].append({
                    'value': value,
                    'platform': f"{record.platformID}",
                    'encoding': f"{record.platEncID}",
                    'language': f"{record.langID}"
                })
                
                if field_name not in metadata:
                    metadata[field_name] = value
                
                if verbose:
                    if name_id not in records_by_id:
                        records_by_id[name_id] = []
                    
                    platform_name = {
                        0: 'Unicode',
                        1: 'Macintosh',
                        3: 'Windows'
                    }.get(record.platformID, f"Platform {record.platformID}")
                    
                    records_by_id[name_id].append({
                        'value': value,
                        'platform': platform_name,
                        'platform_id': record.platformID,
                        'encoding': record.platEncID,
                        'language': record.langID
                    })
                
            except Exception as e:
                continue
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"字体文件: {font_path}")
            print(f"{'='*80}\n")
            print("字体名称表 (Name Table):")
            print("-" * 80)
            
            for name_id in sorted(records_by_id.keys()):
                field_name = NAME_DISPLAY.get(name_id, f'Name ID {name_id}')
                records = records_by_id[name_id]
                
                print(f"\n{field_name} (ID: {name_id}):")
                for i, record in enumerate(records, 1):
                    print(f"  [{i}] {record['platform']}: {record['value']}")
            
            print(f"\n{'='*80}")
            print("\nJSON 格式（用于 AI 分析）:")
            print("-" * 80)
            
            simple_metadata = {}
            for field_name, value in metadata.items():
                if field_name != 'all_names' and value:
                    simple_metadata[field_name] = value
            
            print(json.dumps(simple_metadata, ensure_ascii=False, indent=2))
            print()
        
        if 'family_name' not in metadata:
            metadata['family_name'] = font_path.stem
        
        metadata['file_name'] = font_path.name
        metadata['file_stem'] = font_path.stem
        
        return metadata
        
    except Exception as e:
        if verbose:
            print(f"错误: 提取元信息失败: {e}")
        else:
            print(f"  警告: 提取元信息失败: {e}")
        return {
            'family_name': font_path.stem,
            'file_name': font_path.name,
            'file_stem': font_path.stem
        }




def analyze_font(font_path, normalizer=None):
    try:
        font = TTFont(font_path)
        
        metadata = extract_font_metadata(font_path)
        
        cmap = font.getBestCmap()
        
        if not cmap:
            return {
                'success': False,
                'error': '无字符映射',
                'char_count': 0,
                'chars': []
            }
        
        chars = sorted(cmap.keys())
        char_strings = [chr(c) for c in chars]
        
        try:
            font_name = font['name'].getDebugName(1) or font['name'].getDebugName(4)
        except:
            font_name = Path(font_path).stem
        
        num_glyphs = font['maxp'].numGlyphs
        
        normalized_info = None
        if normalizer:
            font_info = {
                'file_name': metadata.get('file_name'),
                'file_stem': metadata.get('file_stem'),
                'family_name': metadata.get('family_name', font_name),
                'subfamily_name': metadata.get('subfamily_name'),
                'full_name': metadata.get('full_name'),
                'postscript_name': metadata.get('postscript_name'),
                'typographic_family': metadata.get('typographic_family'),
                'copyright': metadata.get('copyright'),
                'designer': metadata.get('designer'),
                'version': metadata.get('version'),
                'trademark': metadata.get('trademark'),
                'description': metadata.get('description')
            }
            normalized_info = normalizer.normalize_font_name(font_info)
        
        result = {
            'success': True,
            'font_name': font_name,
            'char_count': len(chars),
            'glyph_count': num_glyphs,
            'chars': char_strings,
            'unicode_ranges': get_unicode_ranges(chars),
            'metadata': metadata
        }
        
        if normalized_info:
            result['normalized'] = normalized_info
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'char_count': 0,
            'chars': []
        }

def get_unicode_ranges(chars):
    ranges = {
        'Basic Latin': (0x0000, 0x007F),
        'Latin-1 Supplement': (0x0080, 0x00FF),
        'CJK Unified Ideographs': (0x4E00, 0x9FFF),
        'CJK Extension A': (0x3400, 0x4DBF),
        'CJK Compatibility': (0xF900, 0xFAFF),
        'Hiragana': (0x3040, 0x309F),
        'Katakana': (0x30A0, 0x30FF),
        'Hangul': (0xAC00, 0xD7AF),
    }
    
    range_counts = {}
    for range_name, (start, end) in ranges.items():
        count = sum(1 for c in chars if start <= c <= end)
        if count > 0:
            range_counts[range_name] = count
    
    return range_counts

WEIGHT_MAPPING = {
    'thin': ('Thin', 100),
    'hairline': ('Thin', 100),
    'ultralight': ('Thin', 100),
    'extralight': ('ExtraLight', 200),
    'extra light': ('ExtraLight', 200),
    'ultra light': ('ExtraLight', 200),
    'light': ('Light', 300),
    'regular': ('Regular', 400),
    'normal': ('Regular', 400),
    'book': ('Regular', 400),
    'roman': ('Regular', 400),
    'medium': ('Medium', 500),
    'semibold': ('SemiBold', 600),
    'semi bold': ('SemiBold', 600),
    'demi bold': ('SemiBold', 600),
    'demibold': ('SemiBold', 600),
    'bold': ('Bold', 700),
    'extrabold': ('ExtraBold', 800),
    'extra bold': ('ExtraBold', 800),
    'ultra bold': ('ExtraBold', 800),
    'ultrabold': ('ExtraBold', 800),
    'black': ('Black', 900),
    'heavy': ('Black', 900),
    'ultra': ('Black', 900),
    'fat': ('Black', 900),
}

WEIGHT_PRIORITY_KEYWORDS = [
    'extralight', 'extra light', 'ultra light',
    'extrabold', 'extra bold', 'ultra bold', 'ultrabold',
    'semibold', 'semi bold', 'demi bold', 'demibold',
    'thin', 'hairline', 'ultralight',
    'light',
    'bold',
    'black', 'heavy', 'ultra', 'fat',
    'medium',
    'regular', 'normal', 'book', 'roman'
]

def extract_font_weight(subfamily_name):
    if not subfamily_name:
        return 'Regular', 400
    
    name_lower = subfamily_name.lower()
    
    if name_lower in WEIGHT_MAPPING:
        return WEIGHT_MAPPING[name_lower]
    
    for keyword in WEIGHT_PRIORITY_KEYWORDS:
        if keyword in name_lower:
            return WEIGHT_MAPPING[keyword]
    
    return 'Regular', 400

def generate_report(results, output_dir):
    """
    生成字体分析报告，支持字族嵌套结构
    """
    # 按照文件路径分组：区分字族和独立字体
    font_families = defaultdict(dict)  # 字族：family_name -> {weight_name: result}
    standalone_fonts = {}  # 独立字体：file_name -> result
    
    for file_path, result in results.items():
        if not result['success']:
            continue
        
        path = Path(file_path)
        parent_dir = path.parent.name
        file_name = path.stem
        
        # 判断是否在字族文件夹中
        if parent_dir != 'fonts':
            # 在字族文件夹中
            family_name = parent_dir
            weight_name = file_name
            font_families[family_name][weight_name] = result
        else:
            # 独立字体文件
            standalone_fonts[file_name] = result
    
    fonts_array = []
    
    # 处理字族
    for family_name, weights in sorted(font_families.items()):
        # 获取第一个字重的数据用于提取家族级别的元信息
        first_weight_data = next(iter(weights.values()))
        
        font_obj = {
            'name': family_name,
            'children': []  # 使用 children 表示这是一个字族
        }
        
        # 从第一个字重提取家族级别的元信息
        if 'normalized' in first_weight_data:
            normalized = first_weight_data['normalized']
            font_obj.update({
                'normalized_name': normalized.get('normalized_name'),
                'font_family': normalized.get('font_family'),
                'english_name': normalized.get('english_name'),
                'chinese_name': normalized.get('chinese_name'),
                'designer': normalized.get('designer'),
                'foundry': normalized.get('foundry'),
                'release_year': normalized.get('release_year'),
                'category': normalized.get('category'),
                'font_category': normalized.get('font_category'),
                'style': normalized.get('style'),
                'copyright': normalized.get('copyright'),
                'license': normalized.get('license'),
                'license_type': normalized.get('license_type'),
                'version': normalized.get('version'),
                'description': normalized.get('description'),
                'tags': normalized.get('tags', []),
                'font_tags': normalized.get('font_tags', []),
                'languages': normalized.get('languages', []),
                'use_cases': normalized.get('use_cases', [])
            })
        
        # 添加每个字重作为子项
        for weight_name, data in sorted(weights.items()):
            weight_obj = {
                'name': weight_name,
                'char_count': data['char_count'],
                'glyph_count': data['glyph_count'],
                'unicode_ranges': data['unicode_ranges'],
                'characters': ''.join(data['chars'])
            }
            
            # 如果有字重级别的元信息，也添加进去
            metadata = data.get('metadata', {})
            if metadata:
                weight_obj['subfamily_name'] = metadata.get('subfamily_name', '')
                weight_obj['full_name'] = metadata.get('full_name', '')
            
            font_obj['children'].append(weight_obj)
        
        fonts_array.append(font_obj)
    
    # 处理独立字体
    for font_name, result in sorted(standalone_fonts.items()):
        font_obj = {
            'name': font_name,
            'char_count': result['char_count'],
            'glyph_count': result['glyph_count'],
            'unicode_ranges': result['unicode_ranges'],
            'characters': ''.join(result['chars'])
        }
        
        if 'normalized' in result:
            normalized = result['normalized']
            font_obj.update({
                'normalized_name': normalized.get('normalized_name'),
                'font_family': normalized.get('font_family'),
                'english_name': normalized.get('english_name'),
                'chinese_name': normalized.get('chinese_name'),
                'designer': normalized.get('designer'),
                'foundry': normalized.get('foundry'),
                'release_year': normalized.get('release_year'),
                'category': normalized.get('category'),
                'font_category': normalized.get('font_category'),
                'style': normalized.get('style'),
                'copyright': normalized.get('copyright'),
                'license': normalized.get('license'),
                'license_type': normalized.get('license_type'),
                'version': normalized.get('version'),
                'description': normalized.get('description'),
                'tags': normalized.get('tags', []),
                'font_tags': normalized.get('font_tags', []),
                'languages': normalized.get('languages', []),
                'use_cases': normalized.get('use_cases', [])
            })
        
        fonts_array.append(font_obj)
    
    # 计算统计信息
    total_fonts = len(font_families) + len(standalone_fonts)
    total_weights = sum(len(weights) for weights in font_families.values()) + len(standalone_fonts)
    
    json_report = {
        'summary': {
            'total_fonts': total_fonts,
            'total_font_families': len(font_families),
            'total_standalone_fonts': len(standalone_fonts),
            'total_weights': total_weights
        },
        'fonts': fonts_array
    }
    
    json_path = output_dir / 'font-analysis.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON 报告已保存: {json_path}")
    
    # 生成 CSV 报告
    csv_path = output_dir / 'font-analysis.csv'
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['字体类型', '字体名称', '字重/版本', '字符数量', '字形数量', 'Unicode范围'])
        
        # 写入字族
        for family_name, weights in sorted(font_families.items()):
            for weight_name, data in sorted(weights.items()):
                ranges_str = ', '.join(f"{k}: {v}" for k, v in data['unicode_ranges'].items())
                writer.writerow([
                    '字族',
                    family_name,
                    weight_name,
                    data['char_count'],
                    data['glyph_count'],
                    ranges_str
                ])
        
        # 写入独立字体
        for font_name, data in sorted(standalone_fonts.items()):
            ranges_str = ', '.join(f"{k}: {v}" for k, v in data['unicode_ranges'].items())
            writer.writerow([
                '独立字体',
                font_name,
                '-',
                data['char_count'],
                data['glyph_count'],
                ranges_str
            ])
    
    print(f"✓ CSV 报告已保存: {csv_path}")
    
    return json_report

def print_summary(json_report):
    print("\n" + "=" * 60)
    print("字体字符分析报告")
    print("=" * 60)
    
    summary = json_report['summary']
    print(f"\n总计:")
    print(f"  字体总数: {summary['total_fonts']} 个")
    print(f"  - 字族: {summary['total_font_families']} 个")
    print(f"  - 独立字体: {summary['total_standalone_fonts']} 个")
    print(f"  字重总数: {summary['total_weights']} 个")
    
    print(f"\n详细信息:")
    for font in json_report['fonts']:
        font_name = font['name']
        
        # 判断是字族还是独立字体
        if 'children' in font:
            # 字族
            print(f"\n  📁 {font_name} (字族, {len(font['children'])} 个字重):")
            for child in font['children']:
                print(f"    ├─ {child['name']}: {child['char_count']} 个字符, {child['glyph_count']} 个字形")
                if child['unicode_ranges']:
                    ranges_str = ', '.join(f"{k}: {v}" for k, v in list(child['unicode_ranges'].items())[:3])
                    print(f"       └─ {ranges_str}")
        else:
            # 独立字体
            print(f"\n  📄 {font_name}:")
            print(f"    {font['char_count']} 个字符, {font['glyph_count']} 个字形")
            if font['unicode_ranges']:
                ranges_str = ', '.join(f"{k}: {v}" for k, v in list(font['unicode_ranges'].items())[:3])
                print(f"    {ranges_str}")

def inspect_single_font(font_path: Path):
    if not font_path.exists():
        print(f"错误: 文件不存在: {font_path}")
        sys.exit(1)
    
    if not font_path.suffix.lower() in ['.ttf', '.otf']:
        print(f"错误: 不是字体文件: {font_path}")
        sys.exit(1)
    
    metadata = extract_font_metadata(font_path, verbose=True)
    
    normalizer = AIFontNormalizer()
    if normalizer.enabled:
        print("\n使用 AI 分析字体名称...")
        print("-" * 80)
        
        font_info = {
            'file_name': metadata.get('file_name', ''),
            'family_name': metadata.get('family_name', ''),
            'subfamily_name': metadata.get('subfamily_name', ''),
            'full_name': metadata.get('full_name', ''),
            'postscript_name': metadata.get('postscript_name', ''),
            'typographic_family': metadata.get('typographic_family', ''),
            'typographic_subfamily': metadata.get('typographic_subfamily', ''),
            'designer': metadata.get('designer', ''),
            'manufacturer': metadata.get('manufacturer', ''),
            'copyright': metadata.get('copyright', ''),
            'description': metadata.get('description', ''),
            'version': metadata.get('version', '')
        }
        
        normalized = normalizer.normalize_font_name(font_info)
        
        print("\nAI 规范化结果:")
        print(json.dumps(normalized, ensure_ascii=False, indent=2))
        print()
    else:
        print("\n⚠ AI 分析未启用")
        print("提示: 设置环境变量以启用 AI 功能")
        print("  export ARK_API_KEY=your_key")
        print()


def main():
    if len(sys.argv) >= 2 and (sys.argv[1] == 'inspect' or sys.argv[1] == '--inspect'):
        if len(sys.argv) < 3:
            print("用法: python3 scripts/analyze-fonts.py inspect <字体文件路径>")
            print()
            print("示例:")
            print("  python3 scripts/analyze-fonts.py inspect fonts/字体.ttf")
            print("  python3 scripts/analyze-fonts.py inspect fonts-subset/字体-full.ttf")
            sys.exit(1)
        
        font_path = Path(sys.argv[2])
        inspect_single_font(font_path)
        return
    
    print("========== 字体字符分析和规范化工具 ==========")
    print()
    
    normalizer = AIFontNormalizer()
    if normalizer.enabled:
        print("✓ AI 规范化已启用")
        if normalizer.use_bot_api:
            print("✓ 使用 Bot API（支持互联网搜索）")
            print("  提示：AI 将自动搜索字体信息以补全缺失字段")
        else:
            print("  提示：未启用互联网搜索，仅使用 AI 推理")
            print("  如需启用搜索，请使用豆包 Bot API")
        model = os.getenv('OPENAI_MODEL') or os.getenv('ARK_MODEL') or 'gpt-4o-mini'
        print(f"  模型: {model}")
    else:
        print("⚠ AI 规范化未启用，将使用降级模式")
        if not OPENAI_AVAILABLE:
            print("  提示: 安装 openai 库以启用 AI 功能")
            print("  pip3 install openai")
        else:
            print("  提示: 设置环境变量以启用 AI 功能")
            print("  export ARK_API_KEY=your_key")
    print()
    
    input_dir = Path('fonts')
    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        print("请确保 fonts/ 目录存在并包含字体文件")
        sys.exit(1)
    print(f"使用原始字体目录: {input_dir}")
    
    font_files_info = []
    font_families = {}
    
    for pattern in ['*.ttf', '*.otf']:
        root_fonts = list(input_dir.glob(pattern))
        for font_file in root_fonts:
            font_files_info.append((font_file, None, None))
    
    for subdir in input_dir.iterdir():
        if subdir.is_dir():
            family_name = subdir.name
            family_fonts = []
            
            for pattern in ['*.ttf', '*.otf']:
                for font_file in subdir.glob(pattern):
                    weight_name = font_file.stem
                    font_files_info.append((font_file, family_name, weight_name))
                    family_fonts.append(weight_name)
            
            if family_fonts:
                font_families[family_name] = family_fonts
    
    if not font_files_info:
        print(f"错误: 在 {input_dir} 中未找到字体文件")
        sys.exit(1)
    
    print(f"找到 {len(font_files_info)} 个字体文件")
    
    if font_families:
        print("\n字体家族结构:")
        for family_name, weights in font_families.items():
            print(f"  {family_name}:")
            for weight in weights:
                print(f"    - {weight}")
    
    standalone_fonts = [f for f in font_files_info if f[1] is None]
    if standalone_fonts:
        print("\n独立字体:")
        for font_path, _, _ in standalone_fonts:
            print(f"  - {font_path.name}")
    
    print()
    
    print("按字体家族分组...")
    families_to_analyze = {}
    standalone_fonts = []
    
    results = {}
    for i, (font_file, family_name, weight_name) in enumerate(font_files_info, 1):
        print(f"[{i}/{len(font_files_info)}] 提取元信息: {font_file.name}")
        if family_name and weight_name:
            print(f"  家族: {family_name}, 字重: {weight_name}")
        
        result = analyze_font(font_file, None)
        results[str(font_file)] = result
        
        if result['success']:
            print(f"  ✓ {result['char_count']} 个字符")
            
            if family_name:
                if family_name not in families_to_analyze:
                    families_to_analyze[family_name] = []
                families_to_analyze[family_name].append((font_file, weight_name, result))
            else:
                standalone_fonts.append((font_file, result))
        else:
            print(f"  ✗ 失败: {result['error']}")
    
    print()
    print("="*60)
    print("开始AI规范化...")
    print("="*60)
    print()
    
    font_mapping = {}
    
    for family_idx, (family_name, family_fonts) in enumerate(families_to_analyze.items(), 1):
        print(f"[家族 {family_idx}/{len(families_to_analyze)}] 分析字体家族: {family_name} ({len(family_fonts)} 个字重)")
        
        family_info = {
            'family_name': family_name,
            'weights': {
                weight_name: {
                    'metadata': result.get('metadata', {}),
                    'char_count': result.get('char_count', 0),
                    'glyph_count': result.get('glyph_count', 0)
                }
                for font_file, weight_name, result in family_fonts
            }
        }
        
        normalized = normalizer.normalize_font_family(family_info)
        
        print(f"  ✓ AI返回结果:")
        print(f"    normalized_name: {normalized.get('normalized_name', 'N/A')}")
        print(f"    font_family: {normalized.get('font_family', 'N/A')}")
        
        meta_fields = ['designer', 'copyright', 'version', 'description', 'category', 'license']
        filled_fields = sum(1 for f in meta_fields if normalized.get(f))
        print(f"    元信息字段: {filled_fields}/{len(meta_fields)} 个已填充")
        
        mapping_key = family_name
        
        font_mapping[mapping_key] = {
            'normalized_name': normalized.get('normalized_name', family_name),
            'font_family': normalized.get('font_family', f'WF-{family_name}'),
            'original_name': normalized.get('original_name', family_name),
            'weights': {},
            'english_name': normalized.get('english_name'),
            'chinese_name': normalized.get('chinese_name'),
            'designer': normalized.get('designer'),
            'foundry': normalized.get('foundry'),
            'release_year': normalized.get('release_year'),
            'category': normalized.get('category'),
            'font_category': normalized.get('font_category'),
            'style': normalized.get('style'),
            'copyright': normalized.get('copyright'),
            'license': normalized.get('license'),
            'license_type': normalized.get('license_type'),
            'version': normalized.get('version'),
            'description': normalized.get('description'),
            'tags': normalized.get('tags', []),
            'font_tags': normalized.get('font_tags', []),
            'languages': normalized.get('languages', []),
            'use_cases': normalized.get('use_cases', [])
        }
        
        # 处理每个字重：直接使用文件名提取字重信息
        for font_file, weight_file_name, result in family_fonts:
            # 从文件名提取字重
            weight_name, font_weight = extract_font_weight(weight_file_name)
            
            # 构建 font_family
            if weight_name != 'Regular':
                font_family_full = f"WF-{family_name}-{weight_name}"
            else:
                font_family_full = f"WF-{family_name}"
            
            print(f"    [{weight_file_name}] → {weight_name} (CSS: {font_weight})")
            
            font_mapping[mapping_key]['weights'][weight_name] = {
                'font_family': font_family_full,
                'weight_name': weight_name,
                'font_weight': font_weight,
                'versions': {
                    'original': {
                        'file': font_file.name,
                        'char_count': result.get('char_count', 0),
                        'glyph_count': result.get('glyph_count', 0),
                        'subfamily_name': result.get('metadata', {}).get('subfamily_name', ''),
                        'typographic_subfamily': result.get('metadata', {}).get('typographic_subfamily', '')
                    }
                }
            }
        
        print()
    
    for font_idx, (font_file, result) in enumerate(standalone_fonts, 1):
        print(f"[独立 {font_idx}/{len(standalone_fonts)}] 分析独立字体: {font_file.name}")
        
        metadata = result.get('metadata', {})
        font_info = {
            'file_name': metadata.get('file_name', ''),
            'file_stem': metadata.get('file_stem', ''),
            'family_name': metadata.get('family_name', font_file.stem),
            'subfamily_name': metadata.get('subfamily_name', ''),
            'full_name': metadata.get('full_name', ''),
            'postscript_name': metadata.get('postscript_name', ''),
            'typographic_family': metadata.get('typographic_family', ''),
            'copyright': metadata.get('copyright', ''),
            'designer': metadata.get('designer', ''),
            'version': metadata.get('version', ''),
            'trademark': metadata.get('trademark', ''),
            'description': metadata.get('description', '')
        }
        
        normalized = normalizer.normalize_font_name(font_info)
        
        ai_weight_name = normalized.get('weight_name', '')
        ai_font_weight = normalized.get('font_weight', '')
        
        if ai_weight_name and ai_font_weight:
            subfamily, font_weight_value = ai_weight_name, ai_font_weight
        else:
            subfamily, font_weight_value = extract_font_weight(metadata.get('subfamily_name', 'Regular'))
        
        font_family_with_variant = (
            f"{normalized['font_family']}-{subfamily}" 
            if subfamily and subfamily.lower() not in ['regular', 'normal']
            else normalized['font_family']
        )
        
        file_name = font_file.stem
        parts = file_name.rsplit('-', 1)
        mapping_key = parts[0] if len(parts) == 2 and parts[1] in ['full', 'en', 'zh', 'zh-common'] else file_name
        
        print(f"  → {normalized.get('font_family', font_file.stem)}")
        
        font_mapping[mapping_key] = {
            'normalized_name': normalized.get('normalized_name', file_name),
            'font_family': normalized.get('font_family', f'WF-{file_name}'),
            'original_name': normalized.get('original_name', file_name),
            'weights': {
                subfamily: {
                    'font_family': font_family_with_variant,
                    'weight_name': subfamily,
                    'font_weight': font_weight_value,
                    'versions': {
                        'original': {
                            'file': font_file.name,
                            'char_count': result.get('char_count', 0),
                            'glyph_count': result.get('glyph_count', 0),
                            'subfamily_name': metadata.get('subfamily_name', ''),
                            'typographic_subfamily': metadata.get('typographic_subfamily', '')
                        }
                    }
                }
            },
            'english_name': normalized.get('english_name'),
            'chinese_name': normalized.get('chinese_name'),
            'designer': normalized.get('designer'),
            'foundry': normalized.get('foundry'),
            'release_year': normalized.get('release_year'),
            'category': normalized.get('category'),
            'font_category': normalized.get('font_category'),
            'style': normalized.get('style'),
            'copyright': normalized.get('copyright'),
            'license': normalized.get('license'),
            'license_type': normalized.get('license_type'),
            'version': normalized.get('version'),
            'description': normalized.get('description'),
            'tags': normalized.get('tags', []),
            'font_tags': normalized.get('font_tags', []),
            'languages': normalized.get('languages', []),
            'use_cases': normalized.get('use_cases', [])
        }
        
        print()
    
    # 创建输出目录
    output_dir = Path('metadata')
    output_dir.mkdir(exist_ok=True)
    os.chmod(output_dir, 0o755)
    
    # 生成字体映射文件
    if font_mapping:
        print()
        print("生成字体映射文件...")
        mapping_file = output_dir / 'font-mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(font_mapping, f, ensure_ascii=False, indent=2)
        print(f"✓ 字体映射已保存: {mapping_file}")
        
        # 显示映射摘要
        print()
        print("字体名称映射:")
        for base_name, info in sorted(font_mapping.items()):
            print(f"  {base_name}")
            print(f"    → {info['font_family']}")
            if info['weights']:
                print(f"    字重: {', '.join(info['weights'].keys())}")
    
    # 生成报告
    print()
    print("生成字符分析报告...")
    json_report = generate_report(results, output_dir)
    
    # 打印摘要
    print_summary(json_report)
    
    print()
    print("分析完成！")
    print()
    print("生成的文件:")
    print(f"  - metadata/font-mapping.json   (字体名称映射)")
    print(f"  - metadata/font-analysis.json  (JSON 格式报告)")
    print(f"  - metadata/font-analysis.csv   (CSV 格式报告)")

if __name__ == '__main__':
    main()
