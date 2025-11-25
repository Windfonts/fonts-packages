#!/usr/bin/env python3
"""
字体多版本子集化工具
支持创建多个字符集版本：全量、纯中文、纯英文、常用中文
"""

import sys
import os
import json
from pathlib import Path

try:
    from fontTools.subset import Subsetter
    from fontTools.ttLib import TTFont
except ImportError:
    print("错误: 需要安装 fonttools")
    print("请运行: pip3 install fonttools")
    sys.exit(1)

# 字符集定义
CHARSET_DEFINITIONS = {
    'full': {
        'name': '全量版本',
        'description': '完整字符集，包含字体中的所有字符',
        'unicodes': None,  # None 表示不进行子集化
        'suffix': 'full'
    },
    
    'english': {
        'name': '纯英文版本',
        'description': '仅包含拉丁字母、数字和基本标点符号',
        'unicodes': (
            # 基本拉丁字母 (A-Z, a-z)
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            'abcdefghijklmnopqrstuvwxyz'
            # 数字 (0-9)
            '0123456789'
            # 基本标点符号
            ',.!?;:\'"()-[]{}/<>@#$%^&*+=_~`|'
            # 空格
            ' '
        ),
        'suffix': 'en'
    },
    
    'chinese': {
        'name': '纯中文版本',
        'description': '仅包含中文字符（CJK统一汉字）',
        'unicodes': None,  # 将通过Unicode范围定义
        'unicode_ranges': [
            (0x4E00, 0x9FFF),  # CJK统一汉字
            (0x3400, 0x4DBF),  # CJK扩展A
            (0xF900, 0xFAFF),  # CJK兼容汉字
        ],
        'suffix': 'zh'
    },
    
    'chinese_common': {
        'name': '常用中文版本',
        'description': '包含最常用的3500个中文字符 + 基本标点',
        'unicodes': (
            # 最常用的3500个中文字符（国标一级字库）
            '的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙飞'
            # 常用标点符号
            '，。！？；：、·…—（）【】《》""''「」『』〈〉〔〕〖〗〘〙〚〛'
            # 基本拉丁字母和数字（用于中英文混合内容）
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
            # 空格
            ' '
        ),
        'suffix': 'zh-common'
    }
}

def string_to_unicodes(text):
    """将字符串转换为 Unicode 码点列表"""
    return [ord(char) for char in text]

def get_unicode_ranges(ranges):
    """根据Unicode范围生成码点列表"""
    unicodes = []
    for start, end in ranges:
        unicodes.extend(range(start, end + 1))
    return unicodes

def create_subset_font(input_font, output_font, unicodes, charset_name):
    """创建字符集限制的字体"""
    print(f"  处理: {charset_name}")
    print(f"    输入: {input_font}")
    print(f"    输出: {output_font}")
    
    if unicodes is None:
        print(f"    跳过子集化（保持完整字符集）")
        # 直接复制文件
        import shutil
        shutil.copy2(input_font, output_font)
        # 设置文件权限为可读写
        os.chmod(output_font, 0o644)
        return True
    
    print(f"    字符数量: {len(unicodes)}")
    
    try:
        # 加载字体
        font = TTFont(input_font)
        
        # 创建子集化器
        subsetter = Subsetter()
        
        # 设置选项
        subsetter.options.retain_gids = False
        subsetter.options.notdef_outline = True
        subsetter.options.recommended_glyphs = True
        subsetter.options.name_IDs = ['*']
        subsetter.options.name_legacy = True
        subsetter.options.name_languages = ['*']
        subsetter.options.layout_features = ['*']  # 保留字体特性
        subsetter.options.glyph_names = True
        
        # 执行子集化
        subsetter.populate(unicodes=unicodes)
        subsetter.subset(font)
        
        # 保存字体
        font.save(output_font)
        
        # 检查字体是否为空
        cmap = font.getBestCmap()
        if not cmap or len(cmap) == 0:
            print(f"    ⚠ 警告: 字体为空，跳过")
            os.remove(output_font)
            return False
        
        # 设置文件权限为可读写
        os.chmod(output_font, 0o644)
        
        print(f"    ✓ 子集化完成 ({len(cmap)} 个字符)")
        return True
        
    except Exception as e:
        print(f"    ✗ 子集化失败: {e}")
        return False

def process_font_file(font_path, output_dir, font_family_name=None, weight_name=None):
    """处理单个字体文件，生成所有版本
    
    Args:
        font_path: 字体文件路径
        output_dir: 输出根目录
        font_family_name: 字体家族名称（如果在文件夹中）
        weight_name: 字重名称（文件名，如 Bold, Light）
    """
    font_name = Path(font_path).stem
    font_ext = Path(font_path).suffix
    
    print(f"\n处理字体: {font_path}")
    if font_family_name and weight_name:
        print(f"字体家族: {font_family_name}")
        print(f"字重: {weight_name}")
    else:
        print(f"字体名称: {font_name}")
    
    results = {}
    
    for charset_id, charset_config in CHARSET_DEFINITIONS.items():
        # 根据是否有字体家族名称决定输出路径结构
        if font_family_name and weight_name:
            # 输出到: fonts-subset/字体名/字重/字重-版本.ttf
            weight_dir = output_dir / font_family_name / weight_name
            weight_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"{weight_name}-{charset_config['suffix']}{font_ext}"
            output_path = weight_dir / output_filename
        else:
            # 输出到: fonts-subset/字体名-版本.ttf（兼容旧模式）
            output_filename = f"{font_name}-{charset_config['suffix']}{font_ext}"
            output_path = output_dir / output_filename
        
        # 准备Unicode码点列表
        unicodes = None
        if charset_config['unicodes'] is not None:
            unicodes = string_to_unicodes(charset_config['unicodes'])
        elif 'unicode_ranges' in charset_config:
            unicodes = get_unicode_ranges(charset_config['unicode_ranges'])
        
        # 创建子集化字体
        success = create_subset_font(
            font_path, 
            str(output_path), 
            unicodes, 
            charset_config['name']
        )
        
        results[charset_id] = {
            'success': success,
            'output_path': str(output_path),
            'config': charset_config
        }
    
    return results

def generate_report(all_results):
    """生成处理报告"""
    print("\n" + "="*60)
    print("字体子集化处理报告")
    print("="*60)
    
    total_fonts = len(all_results)
    total_versions = sum(len(results) for results in all_results.values())
    successful_versions = sum(
        sum(1 for r in results.values() if r['success']) 
        for results in all_results.values()
    )
    
    print(f"处理字体数量: {total_fonts}")
    print(f"生成版本总数: {total_versions}")
    print(f"成功版本数量: {successful_versions}")
    print(f"失败版本数量: {total_versions - successful_versions}")
    
    print(f"\n版本说明:")
    for charset_id, config in CHARSET_DEFINITIONS.items():
        print(f"  {config['suffix']}: {config['name']} - {config['description']}")
    
    print(f"\n详细结果:")
    for font_name, results in all_results.items():
        print(f"\n  {font_name}:")
        for charset_id, result in results.items():
            status = "✓" if result['success'] else "✗"
            config = result['config']
            print(f"    {status} {config['suffix']}: {config['name']}")
            if result['success']:
                file_size = Path(result['output_path']).stat().st_size
                print(f"      文件: {result['output_path']} ({file_size:,} bytes)")

def main():
    print("========== 字体多版本子集化工具 ==========")
    print("支持版本: 全量、纯中文、纯英文、常用中文")
    print("支持结构: fonts/字体名/字重.ttf 或 fonts/字体.ttf")
    print()
    
    # 检查输入目录
    input_dir = Path('fonts')
    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        sys.exit(1)
    
    # 查找字体文件（支持两种结构）
    font_files = []
    font_families = {}  # 存储字体家族结构
    
    # 1. 查找根目录下的字体文件（旧模式）
    for pattern in ['*.ttf', '*.otf']:
        root_fonts = list(input_dir.glob(pattern))
        for font_file in root_fonts:
            font_files.append({
                'path': font_file,
                'family': None,
                'weight': None
            })
    
    # 2. 查找子目录中的字体文件（新模式：fonts/字体名/字重.ttf）
    for subdir in input_dir.iterdir():
        if subdir.is_dir():
            family_name = subdir.name
            family_fonts = []
            
            for pattern in ['*.ttf', '*.otf']:
                for font_file in subdir.glob(pattern):
                    weight_name = font_file.stem  # 文件名作为字重名
                    font_files.append({
                        'path': font_file,
                        'family': family_name,
                        'weight': weight_name
                    })
                    family_fonts.append(weight_name)
            
            if family_fonts:
                font_families[family_name] = family_fonts
    
    if not font_files:
        print(f"错误: 在 {input_dir} 中未找到字体文件")
        sys.exit(1)
    
    print(f"找到 {len(font_files)} 个字体文件:")
    
    # 显示字体家族结构
    if font_families:
        print("\n字体家族结构:")
        for family_name, weights in font_families.items():
            print(f"  {family_name}:")
            for weight in weights:
                print(f"    - {weight}")
    
    # 显示独立字体
    standalone_fonts = [f for f in font_files if f['family'] is None]
    if standalone_fonts:
        print("\n独立字体:")
        for font_info in standalone_fonts:
            print(f"  - {font_info['path'].name}")
    
    # 创建输出目录
    output_dir = Path('fonts-subset')
    output_dir.mkdir(exist_ok=True)
    # 设置目录权限为可读写执行
    os.chmod(output_dir, 0o755)
    print(f"\n输出目录: {output_dir}")
    
    # 处理所有字体文件
    all_results = {}
    for font_info in font_files:
        font_path = font_info['path']
        family_name = font_info['family']
        weight_name = font_info['weight']
        
        results = process_font_file(font_path, output_dir, family_name, weight_name)
        
        # 构建结果键
        if family_name and weight_name:
            result_key = f"{family_name}/{weight_name}"
        else:
            result_key = font_path.stem
        
        all_results[result_key] = results
    
    # 生成报告
    generate_report(all_results)
    
    print(f"\n处理完成！")
    print(f"子集化字体保存在: {output_dir}")
    print(f"\n下一步:")
    print(f"1. 检查生成的字体文件")
    print(f"2. 选择需要的版本复制到 fonts/ 目录")
    print(f"3. 运行 node scripts/convert.js 进行分包转换")

if __name__ == '__main__':
    main()