#!/usr/bin/env node

/**
 * OSS Upload Script
 * 
 * Uploads converted font files to Aliyun OSS (Object Storage Service)
 * Supports concurrent uploads with retry mechanism and generates URL mapping
 * 
 * Usage:
 *   node scripts/upload.js
 * 
 * Environment Variables:
 *   OSS_UPLOAD_DIRS     Directories to upload, comma-separated (default: ./dist,./metadata)
 *   OSS_CDN_DOMAIN      CDN domain for accessing uploaded files (optional)
 *   OSS_DRY_RUN         Simulate upload without actually uploading (true/false, default: false)
 */

const fs = require('fs-extra');
const path = require('path');
const OSS = require('ali-oss');
const { glob } = require('glob');
const pLimit = require('p-limit');
require('dotenv').config();

// Logger utility
class Logger {
  constructor() {
    this.startTime = Date.now();
  }

  log(level, message) {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${level}] [UPLOAD] ${message}`);
  }

  info(message) {
    this.log('INFO', message);
  }

  warn(message) {
    this.log('WARN', message);
  }

  error(message) {
    this.log('ERROR', message);
  }

  fatal(message) {
    this.log('FATAL', message);
  }
}

const logger = new Logger();

// Get Content-Type based on file extension
function getContentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const contentTypes = {
    '.woff2': 'font/woff2',
    '.woff': 'font/woff',
    '.ttf': 'font/ttf',
    '.otf': 'font/otf',
    '.css': 'text/css; charset=utf-8',
    '.json': 'application/json; charset=utf-8'
  };
  return contentTypes[ext] || 'application/octet-stream';
}

// Initialize OSS client
function initOSSClient() {
  const requiredEnvVars = [
    'OSS_ACCESS_KEY_ID',
    'OSS_ACCESS_KEY_SECRET',
    'OSS_BUCKET',
    'OSS_REGION'
  ];

  // Check required environment variables
  const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
  if (missingVars.length > 0) {
    logger.fatal(`Missing required environment variables: ${missingVars.join(', ')}`);
    logger.info('Please configure these variables in .env file or environment');
    process.exit(1);
  }

  try {
    const client = new OSS({
      accessKeyId: process.env.OSS_ACCESS_KEY_ID,
      accessKeySecret: process.env.OSS_ACCESS_KEY_SECRET,
      bucket: process.env.OSS_BUCKET,
      region: process.env.OSS_REGION,
      endpoint: process.env.OSS_ENDPOINT
    });

    logger.info(`OSS client initialized: bucket=${process.env.OSS_BUCKET}, region=${process.env.OSS_REGION}`);
    return client;
  } catch (error) {
    logger.fatal(`Failed to initialize OSS client: ${error.message}`);
    process.exit(1);
  }
}

// Upload a single file with retry mechanism
async function uploadFileWithRetry(client, localPath, remotePath, maxRetries = 3) {
  const contentType = getContentType(localPath);
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      // metadata JSON 会原地覆盖；一年缓存会导致边缘长期吃旧分析/映射。
      const isMetadata = remotePath.includes('/metadata/') || remotePath.startsWith('metadata/');
      const cacheControl = isMetadata
        ? 'public, max-age=300, must-revalidate'
        : 'public, max-age=31536000';
      const result = await client.put(remotePath, localPath, {
        headers: {
          'Cache-Control': cacheControl,
          'Content-Type': contentType
        }
      });

      return {
        success: true,
        url: result.url,
        name: result.name
      };
    } catch (error) {
      if (attempt === maxRetries) {
        logger.error(`Failed to upload ${localPath} after ${maxRetries} attempts: ${error.message}`);
        return {
          success: false,
          error: error.message,
          localPath
        };
      }
      
      // Exponential backoff
      const delay = Math.pow(2, attempt) * 1000;
      logger.warn(`Upload attempt ${attempt} failed for ${localPath}, retrying in ${delay}ms...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

// Scan directory for files to upload
async function scanFiles(inputDir) {
  logger.info(`Scanning directory: ${inputDir}`);
  
  if (!await fs.pathExists(inputDir)) {
    logger.warn(`Directory does not exist: ${inputDir}, skipping...`);
    return [];
  }

  // Build glob pattern - scan all files
  const pattern = path.join(inputDir, '**', '*');

  // Find all files (exclude directories)
  const allPaths = await glob(pattern, { nodir: true });
  
  // Filter for relevant file types
  const files = allPaths.filter(file => {
    const ext = path.extname(file).toLowerCase();
    return ['.woff2', '.woff', '.css', '.json'].includes(ext);
  });

  logger.info(`Found ${files.length} files in ${inputDir}`);
  return files;
}

// Generate remote path for OSS
function generateRemotePath(localPath, baseDir) {
  const basePath = process.env.OSS_BASE_PATH || 'fonts/';
  
  // Determine which directory this file belongs to
  let dirName = '';
  if (localPath.includes('metadata')) {
    dirName = 'metadata';
  } else if (localPath.includes('dist')) {
    dirName = 'fonts';
  }
  
  const relativePath = path.relative(baseDir, localPath);
  
  // Normalize path separators for OSS (always use forward slash)
  const normalizedPath = relativePath.split(path.sep).join('/');
  
  // For metadata, use metadata path; for dist, use fonts path
  if (dirName === 'metadata') {
    return path.posix.join(basePath.replace('fonts/', ''), 'metadata', normalizedPath);
  } else {
    return path.posix.join(basePath, normalizedPath);
  }
}

// Upload files with concurrency control
async function uploadFiles(client, files, inputDir, dryRun = false) {
  const limit = pLimit(10); // Limit concurrent uploads to 10
  const results = {
    success: [],
    failed: [],
    total: files.length
  };

  logger.info(`Starting upload of ${files.length} files (concurrency: 10)`);
  
  if (dryRun) {
    logger.info('DRY RUN MODE - No files will be actually uploaded');
  }

  const uploadPromises = files.map(localPath => 
    limit(async () => {
      const remotePath = generateRemotePath(localPath, inputDir);
      const fileSize = (await fs.stat(localPath)).size;
      const fileSizeKB = (fileSize / 1024).toFixed(2);

      if (dryRun) {
        logger.info(`[DRY RUN] Would upload: ${localPath} -> ${remotePath} (${fileSizeKB} KB)`);
        results.success.push({
          localPath,
          remotePath,
          url: `https://${process.env.OSS_BUCKET}.${process.env.OSS_ENDPOINT}/${remotePath}`,
          size: fileSize
        });
        return;
      }

      const result = await uploadFileWithRetry(client, localPath, remotePath);
      
      if (result.success) {
        logger.info(`✓ Uploaded: ${remotePath} (${fileSizeKB} KB)`);
        results.success.push({
          localPath,
          remotePath,
          url: result.url,
          size: fileSize
        });
      } else {
        results.failed.push({
          localPath,
          remotePath,
          error: result.error
        });
      }
    })
  );

  await Promise.all(uploadPromises);

  return results;
}

// Convert OSS URL to CDN URL if CDN domain is configured
function convertToCDNUrl(ossUrl) {
  const cdnDomain = process.env.OSS_CDN_DOMAIN;
  if (!cdnDomain) {
    return ossUrl;
  }

  // Extract the path from OSS URL
  // OSS URL format: https://bucket.endpoint/path
  const urlObj = new URL(ossUrl);
  const urlPath = urlObj.pathname;

  // Build CDN URL
  const cdnUrl = `https://${cdnDomain}${urlPath}`;
  return cdnUrl;
}

// Generate URL mapping file
function generateURLMapping(results, inputDir) {
  const mapping = {};

  results.success.forEach(item => {
    const relativePath = path.relative(inputDir, item.localPath);
    const parts = relativePath.split(path.sep);
    
    // Structure: fontFamily/weight/subset/file
    if (parts.length >= 4) {
      const fontFamily = parts[0];
      const weight = parts[1];
      const subset = parts[2];
      const fileName = parts[3];

      if (!mapping[fontFamily]) {
        mapping[fontFamily] = {};
      }
      
      if (!mapping[fontFamily][weight]) {
        mapping[fontFamily][weight] = {};
      }

      if (!mapping[fontFamily][weight][subset]) {
        mapping[fontFamily][weight][subset] = {
          css: null,
          chunks: []
        };
      }

      // Convert to CDN URL if configured
      const finalUrl = convertToCDNUrl(item.url);

      if (fileName === 'result.css') {
        mapping[fontFamily][weight][subset].css = finalUrl;
      } else if (fileName.endsWith('.woff2')) {
        mapping[fontFamily][weight][subset].chunks.push({
          file: fileName,
          url: finalUrl
        });
      }
    }
  });

  // Sort chunks by filename
  Object.keys(mapping).forEach(fontFamily => {
    Object.keys(mapping[fontFamily]).forEach(weight => {
      Object.keys(mapping[fontFamily][weight]).forEach(subset => {
        mapping[fontFamily][weight][subset].chunks.sort((a, b) => {
          const numA = parseInt(a.file.match(/\d+/)?.[0] || '0');
          const numB = parseInt(b.file.match(/\d+/)?.[0] || '0');
          return numA - numB;
        });
      });
    });
  });

  return mapping;
}

// Print upload statistics
function printStatistics(results, startTime) {
  const duration = ((Date.now() - startTime) / 1000).toFixed(2);
  const totalSize = results.success.reduce((sum, item) => sum + item.size, 0);
  const totalSizeMB = (totalSize / 1024 / 1024).toFixed(2);

  console.log('\n' + '='.repeat(60));
  console.log('Upload Statistics');
  console.log('='.repeat(60));
  console.log(`Total files:     ${results.total}`);
  console.log(`Successful:      ${results.success.length}`);
  console.log(`Failed:          ${results.failed.length}`);
  console.log(`Total size:      ${totalSizeMB} MB`);
  console.log(`Duration:        ${duration} seconds`);
  console.log(`Average speed:   ${(totalSize / 1024 / parseFloat(duration)).toFixed(2)} KB/s`);
  console.log('='.repeat(60));

  if (results.failed.length > 0) {
    console.log('\nFailed uploads:');
    results.failed.forEach(item => {
      console.log(`  ✗ ${item.localPath}`);
      console.log(`    Error: ${item.error}`);
    });
  }
}

// Main function
async function main() {
  const startTime = Date.now();
  
  // Get configuration from environment variables
  const uploadDirsStr = process.env.OSS_UPLOAD_DIRS || './dist,./metadata';
  const uploadDirs = uploadDirsStr.split(',').map(dir => dir.trim());
  const dryRun = process.env.OSS_DRY_RUN === 'true';
  
  logger.info('OSS Upload Script started');
  logger.info(`Upload directories: ${uploadDirs.join(', ')}`);
  
  const cdnDomain = process.env.OSS_CDN_DOMAIN;
  if (cdnDomain) {
    logger.info(`CDN domain: ${cdnDomain}`);
  }
  
  if (dryRun) {
    logger.info('Running in DRY RUN mode');
  }

  // Initialize OSS client (skip in dry-run mode)
  let client = null;
  if (!dryRun) {
    client = initOSSClient();
  } else {
    logger.info('Skipping OSS client initialization (dry-run mode)');
  }

  // Scan files from all directories
  let allFiles = [];
  const dirFileMap = {};
  
  for (const uploadDir of uploadDirs) {
    const files = await scanFiles(uploadDir);
    allFiles = allFiles.concat(files);
    dirFileMap[uploadDir] = files;
  }
  
  if (allFiles.length === 0) {
    logger.warn('No files found to upload');
    return;
  }

  logger.info(`Total files to upload: ${allFiles.length}`);

  // Upload files from each directory
  const allResults = {
    success: [],
    failed: [],
    total: 0
  };

  for (const uploadDir of uploadDirs) {
    const files = dirFileMap[uploadDir];
    if (files.length === 0) continue;

    logger.info(`\nProcessing directory: ${uploadDir}`);
    const results = await uploadFiles(client, files, uploadDir, dryRun);
    
    allResults.success.push(...results.success);
    allResults.failed.push(...results.failed);
    allResults.total += results.total;
  }

  // Generate URL mapping for dist directory
  const distDir = uploadDirs.find(dir => dir.includes('dist'));
  if (distDir) {
    const distResults = {
      success: allResults.success.filter(item => item.localPath.includes('dist')),
      failed: allResults.failed.filter(item => item.localPath.includes('dist'))
    };
    
    const urlMapping = generateURLMapping(distResults, distDir);
    const mappingPath = path.join(distDir, 'urls.json');
    
    await fs.writeJson(mappingPath, urlMapping, { spaces: 2 });
    logger.info(`URL mapping saved to: ${mappingPath}`);
  }

  // Print statistics
  printStatistics(allResults, startTime);

  // Exit with error code if there were failures
  if (allResults.failed.length > 0) {
    logger.error(`Upload completed with ${allResults.failed.length} failures`);
    process.exit(1);
  }

  logger.info('Upload completed successfully');
}

// Run main function
if (require.main === module) {
  main().catch(error => {
    logger.fatal(`Unexpected error: ${error.message}`);
    console.error(error.stack);
    process.exit(1);
  });
}

module.exports = {
  uploadFileWithRetry,
  scanFiles,
  generateRemotePath,
  getContentType,
  generateURLMapping
};
