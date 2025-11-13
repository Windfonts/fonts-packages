#!/usr/bin/env node

/**
 * 字体处理一体化脚本
 * 整合了字体子集化、转换、分析的完整流程
 */

const fs = require('fs-extra');
const path = require('path');
const { glob } = require('glob');
const { execSync } = require('child_process');

// 日志工具
class Logger {
    static log(level, message) {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        console.log(`[${timestamp}] [${level}] ${message}`);
    }

    static info(message) { this.log('INFO', message); }
    static warn(message) { this.log('WARN', message); }
    static error(message) { this.log('ERROR', message); }
    static success(message) { this.log('SUCCESS', message); }
}

// 配置
const CONFIG_FILE = path.resolve(__dirname, '../config/font-split.config.json');
const FONTS_DIR = 'fonts';
const SUBSET_DIR = 'fonts-subset';
const OUTPUT_DIR = 'dist';
const METADATA_DIR = 'metadata';

// 统计信息
const stats = {
    startTime: Date.now(),
    subsetsCreated: 0,
    fontsConverted: 0,
    filesGenerated: 0
};

/**
 * 显示帮助信息
 */
function showHelp() {
    console.log(`
字体处理一体化工具

用法: node scripts/build.js [选项]

选项:
  --skip-subset     跳过字体子集化步骤
  --skip-convert    跳过字体转换步骤
  --skip-analyze    跳过字符分析和规范化步骤
  --clean           处理前清理输出目录
  --help            显示帮助信息

示例:
  node scripts/build.js                    # 完整流程
  node scripts/build.js --skip-subset      # 跳过子集化
  node scripts/build.js --skip-analyze     # 跳过分析和规范化
  node scripts/build.js --clean            # 清理后重新处理
    `);
}

/**
 * 解析命令行参数
 */
function parseArgs() {
    const args = process.argv.slice(2);
    return {
        skipSubset: args.includes('--skip-subset'),
        skipConvert: args.includes('--skip-convert'),
        skipAnalyze: args.includes('--skip-analyze'),
        clean: args.includes('--clean'),
        help: args.includes('--help')
    };
}

/**
 * 清理输出目录
 */
async function cleanOutputs() {
    Logger.info('清理输出目录...');
    
    const dirs = [OUTPUT_DIR, SUBSET_DIR, METADATA_DIR];
    
    for (const dir of dirs) {
        if (await fs.pathExists(dir)) {
            try {
                await fs.chmod(dir, 0o755);
                await fs.remove(dir);
                Logger.info(`✓ 已删除 ${dir}/`);
            } catch (error) {
                Logger.warn(`清理 ${dir}/ 失败: ${error.message}`);
            }
        }
    }
}

/**
 * 步骤1: 字体元信息分析和规范化
 */
async function analyzeFontsMetadata() {
    Logger.info('========== 步骤 1/4: 字体元信息分析 ==========');
    Logger.info('提取字体元信息，使用 AI 生成规范化名称');
    
    try {
        execSync('python3 scripts/analyze-fonts.py', {
            stdio: 'inherit',
            cwd: process.cwd()
        });
        
        // 检查是否生成了映射文件
        const mappingFile = path.join(METADATA_DIR, 'font-mapping.json');
        if (await fs.pathExists(mappingFile)) {
            const mapping = JSON.parse(await fs.readFile(mappingFile, 'utf-8'));
            Logger.success(`✓ 字体元信息分析完成，生成 ${Object.keys(mapping).length} 个字体映射`);
            return true;
        } else {
            Logger.warn('未生成映射文件，将使用原始字体名称');
            return false;
        }
    } catch (error) {
        Logger.warn(`字体元信息分析失败（将使用原始名称）: ${error.message}`);
        return false;
    }
}

/**
 * 步骤2: 字体子集化
 */
async function createSubsets() {
    Logger.info('========== 步骤 2/4: 字体子集化 ==========');
    Logger.info('生成 4 个版本: full, en, zh, zh-common');
    
    try {
        execSync('python3 scripts/create-font-subsets.py', {
            stdio: 'inherit',
            cwd: process.cwd()
        });
        
        // 统计生成的文件
        const subsetFiles = await glob(`${SUBSET_DIR}/*.{ttf,otf}`);
        stats.subsetsCreated = subsetFiles.length;
        
        Logger.success(`✓ 字体子集化完成，生成 ${stats.subsetsCreated} 个文件`);
        return true;
    } catch (error) {
        Logger.error(`✗ 字体子集化失败: ${error.message}`);
        return false;
    }
}

/**
 * 步骤4: 字体转换和分包（调用 convert.js）
 */
async function convertFonts() {
    Logger.info('========== 步骤 4/4: 字体转换和分包 ==========');
    Logger.info('调用 convert.js 进行转换（使用规范化名称）');
    
    try {
        execSync('node scripts/convert.js', {
            stdio: 'inherit',
            cwd: process.cwd()
        });
        
        // 统计生成的文件
        const woff2Files = await glob(`${OUTPUT_DIR}/**/*.woff2`);
        stats.filesGenerated = woff2Files.length;
        stats.fontsConverted = woff2Files.length > 0 ? 1 : 0;
        
        Logger.success(`✓ 字体转换完成，生成 ${stats.filesGenerated} 个文件`);
        return true;
    } catch (error) {
        Logger.error(`✗ 字体转换失败: ${error.message}`);
        return false;
    }
}

/**
 * 步骤3: 字符统计分析
 */
async function analyzeCharacters() {
    Logger.info('========== 步骤 3/4: 字符统计分析 ==========');
    Logger.info('统计子集化后的字符数量和 Unicode 范围');
    
    try {
        execSync('python3 scripts/analyze-fonts.py', {
            stdio: 'inherit',
            cwd: process.cwd()
        });
        
        Logger.success('✓ 字符统计分析完成');
        return true;
    } catch (error) {
        Logger.warn(`字符统计分析失败（不影响字体转换）: ${error.message}`);
        return false;
    }
}



/**
 * 显示最终统计
 */
function showStatistics() {
    const duration = ((Date.now() - stats.startTime) / 1000).toFixed(2);
    
    Logger.info('');
    Logger.info('========== 处理完成 ==========');
    Logger.info(`子集化: ${stats.subsetsCreated} 个文件`);
    Logger.info(`转换: ${stats.fontsConverted} 个字体`);
    Logger.info(`生成: ${stats.filesGenerated} 个 woff2 文件`);
    Logger.info(`耗时: ${duration} 秒`);
    Logger.info('==============================');
}



/**
 * 主函数
 */
async function main() {
    const options = parseArgs();
    
    if (options.help) {
        showHelp();
        process.exit(0);
    }
    
    Logger.info('========== 字体处理一体化工具 ==========');
    Logger.info('流程: 元信息分析 → 子集化 → 字符统计 → 转换分包');
    Logger.info('');
    
    try {
        // 清理
        if (options.clean) {
            await cleanOutputs();
        }
        
        // 步骤1: 字体元信息分析（分析原始字体，生成 font-mapping.json）
        if (!options.skipAnalyze) {
            const analyzeSuccess = await analyzeFontsMetadata();
            if (!analyzeSuccess) {
                Logger.warn('⚠ 元信息分析失败，将使用原始字体名称');
            }
        } else {
            Logger.warn('⚠ 跳过元信息分析，将使用原始字体名称');
        }
        
        // 步骤2: 字体子集化（使用规范化名称）
        if (!options.skipSubset) {
            const success = await createSubsets();
            if (!success && !options.skipConvert) {
                Logger.error('字体子集化失败，终止流程');
                process.exit(1);
            }
        }
        
        // 步骤3: 字符统计分析（分析子集化后的字体）
        if (!options.skipAnalyze && !options.skipSubset) {
            await analyzeCharacters();
        }
        
        // 步骤4: 字体转换（使用 font-mapping.json 中的规范化名称）
        if (!options.skipConvert) {
            const success = await convertFonts();
            if (!success) {
                Logger.error('字体转换失败');
                process.exit(1);
            }
        }
        
        // 清理临时目录（在所有处理完成后）
        if (await fs.pathExists(SUBSET_DIR)) {
            await fs.remove(SUBSET_DIR);
            Logger.info('✓ 已清理临时目录');
        }
        
        // 显示统计
        showStatistics();
        
        Logger.success('所有处理完成！');
        
    } catch (error) {
        Logger.error(`处理失败: ${error.message}`);
        console.error(error.stack);
        process.exit(1);
    }
}

// 执行
main();
