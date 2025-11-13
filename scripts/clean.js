#!/usr/bin/env node

/**
 * 清理脚本 - 删除生成的文件和临时文件
 */

const fs = require('fs-extra');
const path = require('path');

// 需要清理的目录
const DIRS_TO_CLEAN = [
    'dist',
    'fonts-subset',
    'npm-package'
];

// 需要清理的文件模式
const FILES_TO_CLEAN = [
    'metadata/*.json',
    'metadata/*.csv',
    'metadata/*-chars.txt'
];

async function clean(deep = false) {
    console.log('========== 清理项目 ==========\n');
    
    let cleaned = 0;
    let failed = 0;
    
    // 清理目录
    for (const dir of DIRS_TO_CLEAN) {
        if (await fs.pathExists(dir)) {
            try {
                // 尝试修改权限
                await fs.chmod(dir, 0o755).catch(() => {});
                
                // 删除目录
                await fs.remove(dir);
                console.log(`✓ ${dir}/ 已清理`);
                cleaned++;
            } catch (error) {
                console.log(`✗ ${dir}/ 清理失败: ${error.message}`);
                failed++;
            }
        } else {
            console.log(`- ${dir}/ 不存在`);
        }
    }
    
    // 清理文件
    const { glob } = require('glob');
    for (const pattern of FILES_TO_CLEAN) {
        const files = await glob(pattern);
        for (const file of files) {
            try {
                await fs.remove(file);
                cleaned++;
            } catch (error) {
                failed++;
            }
        }
        if (files.length > 0) {
            console.log(`✓ 清理 ${files.length} 个 ${pattern} 文件`);
        }
    }
    
    // 深度清理
    if (deep) {
        console.log('\n执行深度清理...');
        
        // 清理 node_modules 缓存
        const cacheDir = 'node_modules/.cache';
        if (await fs.pathExists(cacheDir)) {
            try {
                await fs.remove(cacheDir);
                console.log('✓ node_modules 缓存已清理');
                cleaned++;
            } catch (error) {
                console.log(`✗ 缓存清理失败: ${error.message}`);
                failed++;
            }
        }
    }
    
    console.log('\n========== 清理完成 ==========');
    console.log(`清理: ${cleaned} 项`);
    if (failed > 0) {
        console.log(`失败: ${failed} 项`);
    }
    console.log('\n提示:');
    console.log('  node scripts/clean.js        # 清理生成文件');
    console.log('  node scripts/clean.js --deep # 深度清理（包括缓存）');
}

// 解析参数
const deep = process.argv.includes('--deep');

// 执行清理
clean(deep).catch(error => {
    console.error('清理失败:', error);
    process.exit(1);
});
