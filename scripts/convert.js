#!/usr/bin/env node

const fs = require('fs-extra');
const path = require('path');
const { glob } = require('glob');
const { fontSplit } = require('cn-font-split');

// 日志工具
class Logger {
    static log(level, message) {
        const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
        console.log(`[${timestamp}] [${level}] [CONVERT] ${message}`);
    }

    static info(message) {
        this.log('INFO', message);
    }

    static warn(message) {
        this.log('WARN', message);
    }

    static error(message) {
        this.log('ERROR', message);
    }

    static fatal(message) {
        this.log('FATAL', message);
    }
}

// 映射文件路径
const MAPPING_FILE = path.resolve(__dirname, '../metadata/font-mapping.json');

// 默认配置（不再使用配置文件）
const DEFAULT_CONFIG = {
    input: './fonts',
    output: './dist',
    presets: [
        {
            name: 'standard',
            description: '标准分包',
            chunkSize: 70,
            enabled: true,
            report:false
        }
    ]
};

// 统计信息
const stats = {
    totalFonts: 0,
    totalPresets: 0,
    successCount: 0,
    failedCount: 0,
    startTime: Date.now()
};

// 字体映射缓存
let fontMapping = null;

/**
 * 加载字体映射文件
 * @returns {Promise<Object|null>} 映射对象
 */
async function loadFontMapping() {
    try {
        if (!await fs.pathExists(MAPPING_FILE)) {
            Logger.warn('字体映射文件不存在，将使用原始名称');
            return null;
        }

        const content = await fs.readFile(MAPPING_FILE, 'utf-8');
        const mapping = JSON.parse(content);

        Logger.info(`加载字体映射文件: ${MAPPING_FILE}`);
        Logger.info(`映射数量: ${Object.keys(mapping).length} 个字体`);

        return mapping;
    } catch (error) {
        Logger.warn(`加载字体映射文件失败: ${error.message}`);
        return null;
    }
}

/**
 * 根据原始字体名获取规范化名称
 * @param {string} originalName - 原始字体名（可能包含版本后缀如 -full）
 * @returns {string} 规范化名称
 */
function getNormalizedName(originalName) {
    if (!fontMapping) {
        Logger.warn(`映射文件未加载，使用原始名称: ${originalName}`);
        return originalName;
    }

    // 精确匹配
    if (fontMapping[originalName]) {
        Logger.info(`✓ 精确匹配: ${originalName} → ${fontMapping[originalName].normalized_name}`);
        return fontMapping[originalName].normalized_name;
    }

    // 模糊匹配（原始名称包含映射键，或映射键包含原始名称）
    for (const [key, value] of Object.entries(fontMapping)) {
        // 检查是否匹配（忽略版本后缀）
        if (originalName.includes(key) || key.includes(originalName)) {
            Logger.info(`✓ 模糊匹配: ${originalName} → ${value.normalized_name} (通过 ${key})`);
            return value.normalized_name;
        }
    }

    Logger.warn(`⚠ 未找到映射: ${originalName}，使用原始名称`);
    return originalName;
}

/**
 * 根据原始字体名获取 font-family
 * @param {string} originalName - 原始字体名（可能包含版本后缀如 -full）
 * @returns {string} font-family 名称
 */
function getFontFamily(originalName) {
    if (!fontMapping) {
        return originalName;
    }

    // 精确匹配
    if (fontMapping[originalName]) {
        return fontMapping[originalName].font_family;
    }

    // 模糊匹配
    for (const [key, value] of Object.entries(fontMapping)) {
        if (originalName.includes(key) || key.includes(originalName)) {
            return value.font_family;
        }
    }

    return originalName;
}

/**
 * 获取配置（使用默认配置）
 * @returns {Object} 配置对象
 */
function getConfig() {
    Logger.info('使用默认配置');
    return DEFAULT_CONFIG;
}

/**
 * 扫描源字体目录，查找所有字体文件
 * @param {string} inputDir - 源字体目录
 * @returns {Promise<Array>} 字体文件列表，包含结构信息
 */
async function scanFontFiles(inputDir) {
    Logger.info(`扫描字体目录: ${inputDir}`);

    if (!await fs.pathExists(inputDir)) {
        Logger.error(`字体目录不存在: ${inputDir}`);
        return [];
    }

    // 查找所有字体文件（ttf和otf格式）
    const pattern = `${inputDir}/**/*.{ttf,otf}`;
    const fontFiles = await glob(pattern, { nocase: true });

    // 分析目录结构，识别字体家族和字重
    const fontInfoList = fontFiles.map(fontPath => {
        const relativePath = path.relative(inputDir, fontPath);
        const parts = relativePath.split(path.sep);
        
        let family = null;
        let weight = null;
        
        // 检查是否是 字体名/字重/字重-版本.ttf 结构
        if (parts.length === 3) {
            family = parts[0];  // 字体家族名
            weight = parts[1];  // 字重目录名
        }
        // 检查是否是 字体名/字重-版本.ttf 结构（旧的 fonts-subset 格式）
        else if (parts.length === 2) {
            family = parts[0];  // 字体家族名
            // 从文件名提取字重（如果有）
            const fileName = path.basename(fontPath, path.extname(fontPath));
            const versionMatch = fileName.match(/^(.+?)-(full|en|zh-common|zh)$/);
            if (versionMatch) {
                // 这是一个版本文件，字重可能在基础名中
                weight = null;  // 暂时不处理，保持兼容
            }
        }
        
        return {
            path: fontPath,
            family,
            weight
        };
    });

    Logger.info(`找到 ${fontInfoList.length} 个字体文件`);
    
    // 统计字体家族
    const families = new Set(fontInfoList.filter(f => f.family).map(f => f.family));
    if (families.size > 0) {
        Logger.info(`包含 ${families.size} 个字体家族`);
    }

    return fontInfoList;
}

/**
 * 检查并使用 fonts-subset 目录
 * @returns {Promise<Object>} 返回 { useSubset: boolean, subsetDir: string }
 */
async function checkSubsetDirectory() {
    const subsetDir = path.resolve(process.cwd(), 'fonts-subset');

    if (await fs.pathExists(subsetDir)) {
        // 支持多层目录结构：fonts-subset/**/*.{ttf,otf}
        const fontFiles = await glob(`${subsetDir}/**/*.{ttf,otf}`, { nocase: true });

        if (fontFiles.length > 0) {
            Logger.info(`检测到 fonts-subset 目录，包含 ${fontFiles.length} 个字体文件`);
            Logger.info(`将处理所有子集版本（full, en, zh, zh-common）`);
            return { useSubset: true, subsetDir };
        }
    }

    return { useSubset: false, subsetDir: null };
}

/**
 * 获取字体信息
 * @param {string} fontPath - 字体文件路径
 * @returns {Object} 字体信息
 */
function getFontInfo(fontPath) {
    const relativePath = path.relative(process.cwd(), fontPath);
    const fontDir = path.dirname(fontPath);
    const fontFileName = path.basename(fontPath);
    const fontName = path.basename(fontPath, path.extname(fontPath));

    return {
        path: fontPath,
        relativePath,
        dir: fontDir,
        fileName: fontFileName,
        name: fontName,
        ext: path.extname(fontPath)
    };
}

/**
 * 从字体文件名中提取版本信息
 * @param {string} fontFileName - 字体文件名
 * @returns {Object} { baseName: string, version: string|null }
 */
function extractVersionFromFileName(fontFileName) {
    const nameWithoutExt = path.basename(fontFileName, path.extname(fontFileName));

    // 检查是否有版本后缀 (-full, -en, -zh, -zh-common)
    const versionSuffixes = ['-full', '-en', '-zh-common', '-zh'];

    for (const suffix of versionSuffixes) {
        if (nameWithoutExt.endsWith(suffix)) {
            const baseName = nameWithoutExt.slice(0, -suffix.length);
            const version = suffix.slice(1); // 去掉开头的 '-'
            return { baseName, version };
        }
    }

    // 没有版本后缀，使用原始名称
    return { baseName: nameWithoutExt, version: null };
}



/**
 * 转换单个字体（单个版本，单个预设）
 * @param {Object} fontFileInfo - 字体文件信息对象 { path, family, weight }
 * @param {string} outputDir - 输出目录
 * @param {Object} preset - 预设配置
 * @param {boolean} useSubset - 是否使用子集模式
 * @returns {Promise<Object>} 转换结果
 */
async function convertFont(fontFileInfo, outputDir, preset, useSubset) {
    const fontPath = fontFileInfo.path;
    const familyName = fontFileInfo.family;
    const weightName = fontFileInfo.weight;
    
    const fontInfo = getFontInfo(fontPath);
    const { baseName, version } = extractVersionFromFileName(fontInfo.fileName);

    Logger.info(`开始转换字体: ${fontInfo.relativePath}`);
    Logger.info('-----------------------------------');

    try {
        // 调试信息
        Logger.info(`文件名: ${fontInfo.fileName}`);
        Logger.info(`基础名: ${baseName}`);
        Logger.info(`版本: ${version || '无'}`);
        if (familyName) Logger.info(`字体家族: ${familyName}`);
        if (weightName) Logger.info(`字重: ${weightName}`);
        
        // 获取规范化名称（使用家族名或基础名）
        const nameForMapping = familyName || baseName;
        const normalizedName = getNormalizedName(nameForMapping);
        const fontFamily = getFontFamily(nameForMapping);

        Logger.info(`规范化名称: ${normalizedName}`);
        Logger.info(`Font Family: ${fontFamily}`);
        
        if (normalizedName !== nameForMapping) {
            Logger.info(`✓ 使用规范化名称: ${nameForMapping} → ${normalizedName}`);
        } else {
            Logger.warn(`⚠ 未找到映射，使用原始名称: ${nameForMapping}`);
        }

        // 创建输出目录
        let destFold;
        // 如果没有字重，默认使用 Regular
        const effectiveWeightName = weightName || 'Regular';
        
        if (version) {
            // 新结构：dist/规范化名称/字重/版本/
            destFold = path.join(outputDir, normalizedName, effectiveWeightName, version);
        } else {
            // 普通模式：dist/规范化名称/字重/预设名/
            destFold = path.join(outputDir, normalizedName, effectiveWeightName, preset.name);
        }
        await fs.ensureDir(destFold);

        // 配置cn-font-split参数
        const resolvedFontPath = path.resolve(fontPath);
        const resolvedOutDir = path.resolve(destFold);

        // 检查字体文件是否存在
        if (!await fs.pathExists(resolvedFontPath)) {
            throw new Error(`字体文件不存在: ${resolvedFontPath}`);
        }

        // 读取字体文件为 Buffer
        const fontBuffer = await fs.readFile(resolvedFontPath);

        // 检查文件大小
        const fileStats = await fs.stat(resolvedFontPath);
        if (fileStats.size < 1024) {
            throw new Error(`字体文件太小 (${fileStats.size} bytes)，可能为空或损坏`);
        }

        const options = {
            input: fontBuffer,
            outDir: resolvedOutDir,
            chunkSize: preset.chunkSize * 1024,
            testHtml: false,
            reporter: false,
            languageAreas: true,
            renameOutputFont: '[index].[ext]',
            silent: true,
            css: {
                fontFamily: fontFamily,
                localFamily: fontFamily
            }
        };

        Logger.info(`使用完整字符集，分包大小: ${preset.chunkSize}KB`);
        Logger.info(`Font Family: ${fontFamily}`);
        Logger.info(`输出目录: ${destFold}`);

        // 执行字体转换
        await fontSplit(options);

        // 检查生成的文件
        const files = await fs.readdir(resolvedOutDir);
        const woff2Files = files.filter(f => f.endsWith('.woff2'));
        Logger.info(`生成 ${woff2Files.length} 个字体文件`);

        Logger.info(`✓ 转换成功`);

        return {
            success: true,
            version: version || preset.name,
            fontInfo,
            family: familyName,
            weight: weightName,
            destFold,
            fileCount: woff2Files.length
        };

    } catch (error) {
        Logger.error(`✗ 转换失败: ${error.message}`);

        return {
            success: false,
            version: version || preset.name,
            fontInfo,
            family: familyName,
            weight: weightName,
            error: error.message
        };
    }
}

/**
 * 批量处理所有字体
 * @param {Array} fontFileInfoList - 字体文件信息列表 [{ path, family, weight }]
 * @param {string} outputDir - 输出目录
 * @param {Object} preset - 预设配置（只使用第一个）
 * @param {boolean} useSubset - 是否使用子集模式
 * @returns {Promise<Array>} 处理结果列表
 */
async function processAllFonts(fontFileInfoList, outputDir, preset, useSubset) {
    const allResults = [];

    stats.totalFonts = fontFileInfoList.length;
    stats.totalPresets = 1;

    if (fontFileInfoList.length === 0) {
        Logger.warn('没有找到需要处理的字体文件');
        return allResults;
    }

    if (useSubset) {
        Logger.info(`开始批量处理 ${fontFileInfoList.length} 个字体版本`);
    } else {
        Logger.info(`开始批量处理 ${fontFileInfoList.length} 个字体`);
    }
    Logger.info('===================================');
    Logger.info('');

    for (let i = 0; i < fontFileInfoList.length; i++) {
        const fontFileInfo = fontFileInfoList[i];
        Logger.info(`[${i + 1}/${fontFileInfoList.length}] 处理字体文件...`);

        const result = await convertFont(fontFileInfo, outputDir, preset, useSubset);
        allResults.push(result);

        if (result.success) {
            stats.successCount++;
        } else {
            stats.failedCount++;
        }

        Logger.info('-----------------------------------');
        Logger.info('');
    }

    return allResults;
}

/**
 * 生成处理统计信息
 * @param {Array} results - 处理结果列表
 */
function generateStatistics(results) {
    const endTime = Date.now();
    const duration = ((endTime - stats.startTime) / 1000).toFixed(2);

    Logger.info('');
    Logger.info('========== 处理统计 ==========');
    Logger.info(`处理数量: ${stats.totalFonts} 个`);
    Logger.info(`成功: ${stats.successCount} 个`);
    Logger.info(`失败: ${stats.failedCount} 个`);
    Logger.info(`耗时: ${duration} 秒`);
    Logger.info('==============================');

    // 按字体分组显示结果（支持字重）
    const fontGroups = {};
    results.forEach(r => {
        const { baseName, version } = extractVersionFromFileName(r.fontInfo.fileName);
        const groupKey = r.family || baseName || r.fontInfo.name;

        if (!fontGroups[groupKey]) {
            fontGroups[groupKey] = {
                name: groupKey,
                weights: {}
            };
        }
        
        const weightKey = r.weight || 'default';
        if (!fontGroups[groupKey].weights[weightKey]) {
            fontGroups[groupKey].weights[weightKey] = {
                name: weightKey,
                versions: []
            };
        }
        
        fontGroups[groupKey].weights[weightKey].versions.push({
            version: version || 'default',
            success: r.success,
            destFold: r.destFold,
            fileCount: r.fileCount,
            error: r.error
        });
    });

    if (stats.failedCount > 0) {
        Logger.info('');
        Logger.info('失败的转换:');
        Object.keys(fontGroups).sort().forEach(fontName => {
            const font = fontGroups[fontName];
            let hasFailed = false;
            
            Object.keys(font.weights).sort().forEach(weightName => {
                const weight = font.weights[weightName];
                const failed = weight.versions.filter(v => !v.success);
                
                if (failed.length > 0) {
                    if (!hasFailed) {
                        Logger.error(`  ${fontName}:`);
                        hasFailed = true;
                    }
                    if (weightName !== 'default') {
                        Logger.error(`    [${weightName}]:`);
                    }
                    failed.forEach(v => {
                        Logger.error(`      - [${v.version}] ${v.error}`);
                    });
                }
            });
        });
    }

    if (stats.successCount > 0) {
        Logger.info('');
        Logger.info('成功转换的字体:');
        Object.keys(fontGroups).sort().forEach(fontName => {
            const font = fontGroups[fontName];
            let hasSuccess = false;
            
            Object.keys(font.weights).sort().forEach(weightName => {
                const weight = font.weights[weightName];
                const success = weight.versions.filter(v => v.success);
                
                if (success.length > 0) {
                    if (!hasSuccess) {
                        Logger.info(`  ✓ ${fontName}:`);
                        hasSuccess = true;
                    }
                    if (weightName !== 'default') {
                        Logger.info(`    [${weightName}]:`);
                    }
                    success.forEach(v => {
                        Logger.info(`      - [${v.version}] ${v.destFold} (${v.fileCount} 个文件)`);
                    });
                }
            });
        });
    }
}

/**
 * 主函数
 */
async function main() {
    try {
        Logger.info('========== 字体转换脚本（多版本生成）==========');
        Logger.info('');

        // 加载字体映射文件
        fontMapping = await loadFontMapping();
        Logger.info('');

        // 获取配置
        const config = getConfig();

        // 检查是否使用 fonts-subset 目录
        const { useSubset, subsetDir } = await checkSubsetDirectory();

        let inputDir = config.input;
        if (useSubset) {
            inputDir = subsetDir;
            Logger.info('使用 fonts-subset 目录中的子集字体');
            Logger.info('将为每个版本（full, en, zh, zh-common）生成分包');
        }

        Logger.info(`输入目录: ${inputDir}`);
        Logger.info(`输出目录: ${config.output}`);
        Logger.info('===============================================');
        Logger.info('');

        // 过滤启用的预设，只使用第一个
        const enabledPresets = config.presets.filter(p => p.enabled);

        if (enabledPresets.length === 0) {
            Logger.error('没有启用的预设版本');
            Logger.info('请在配置文件中将预设的 enabled 设置为 true');
            process.exit(1);
        }

        // 只使用第一个启用的预设
        const preset = enabledPresets[0];

        if (useSubset) {
            Logger.info(`分包配置: ${preset.name} (${preset.chunkSize}KB)`);
        } else {
            Logger.info(`将生成版本: ${preset.name} - ${preset.description}`);
        }
        Logger.info('');
        Logger.info('注意：使用完整字符集，通过分包大小控制输出');
        Logger.info('');

        // 确保输出目录存在
        await fs.ensureDir(config.output);

        // 扫描字体文件
        const fontFiles = await scanFontFiles(inputDir);

        if (fontFiles.length === 0) {
            Logger.warn('未找到任何字体文件，请检查输入目录');
            process.exit(0);
        }

        // 批量处理字体
        const results = await processAllFonts(fontFiles, config.output, preset, useSubset);

        // 生成统计信息
        generateStatistics(results);

        // 清理不需要的元数据文件
        Logger.info('');
        Logger.info('清理元数据文件...');
        try {
            const protoFiles = await glob(`${config.output}/**/index.proto`);
            const binFiles = await glob(`${config.output}/**/reporter.bin`);
            const filesToDelete = [...protoFiles, ...binFiles];

            for (const file of filesToDelete) {
                await fs.remove(file);
            }

            if (filesToDelete.length > 0) {
                Logger.info(`✓ 已删除 ${filesToDelete.length} 个元数据文件`);
            }
        } catch (error) {
            Logger.warn(`清理元数据文件失败: ${error.message}`);
        }

        // 如果使用了 fonts-subset 目录，处理完成后删除它
        if (useSubset) {
            Logger.info('清理临时目录...');
            try {
                await fs.remove(subsetDir);
                Logger.info(`✓ 已删除临时目录: ${subsetDir}`);
            } catch (error) {
                Logger.warn(`删除临时目录失败: ${error.message}`);
            }
        }

        // 根据结果设置退出码
        if (stats.failedCount > 0) {
            Logger.warn('部分字体转换失败');
            process.exit(1);
        } else if (stats.successCount === 0) {
            Logger.error('没有成功转换任何字体');
            process.exit(1);
        } else {
            Logger.info('所有字体转换完成！');
            process.exit(0);
        }

    } catch (error) {
        Logger.fatal(`脚本执行失败: ${error.message}`);
        Logger.fatal(error.stack);
        process.exit(1);
    }
}

// 执行主函数
main();