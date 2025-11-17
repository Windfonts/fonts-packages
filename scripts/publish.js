#!/usr/bin/env node

/**
 * NPM Package Publish Script
 * 
 * This script generates and publishes an npm package containing:
 * - Font metadata with CDN URLs
 * - License information and usage rights
 * - TypeScript type definitions
 * - Query APIs for font information
 */

const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const semver = require('semver');
require('dotenv').config();

// Configuration
const METADATA_FILE = process.argv.find(arg => arg.startsWith('--metadata='))?.split('=')[1] || './metadata/font-analysis.json';
const URLS_FILE = process.argv.find(arg => arg.startsWith('--urls='))?.split('=')[1] || './dist/urls.json';
const OUTPUT_DIR = process.argv.find(arg => arg.startsWith('--output='))?.split('=')[1] || './npm-package';
const VERSION = process.argv.find(arg => arg.startsWith('--version='))?.split('=')[1];
const DRY_RUN = process.argv.includes('--dry-run');

const NPM_TOKEN = process.env.NPM_TOKEN;
const NPM_REGISTRY = process.env.NPM_REGISTRY || 'https://registry.npmjs.org/';

// Logging utilities
const log = {
  info: (msg) => console.log(`[INFO] ${msg}`),
  success: (msg) => console.log(`[SUCCESS] ${msg}`),
  warn: (msg) => console.warn(`[WARN] ${msg}`),
  error: (msg) => console.error(`[ERROR] ${msg}`)
};

/**
 * Read and parse metadata file
 */
function readMetadata() {
  log.info(`Reading metadata from ${METADATA_FILE}...`);
  
  if (!fs.existsSync(METADATA_FILE)) {
    throw new Error(`Metadata file not found: ${METADATA_FILE}`);
  }
  
  const metadata = fs.readJsonSync(METADATA_FILE);
  log.success(`Loaded metadata for ${metadata.summary?.total_fonts || 0} fonts`);
  
  return metadata;
}

/**
 * Read CDN URLs mapping
 */
function readCDNUrls() {
  log.info(`Reading CDN URLs from ${URLS_FILE}...`);
  
  if (!fs.existsSync(URLS_FILE)) {
    log.warn(`CDN URLs file not found: ${URLS_FILE}`);
    log.warn('Font files will not have CDN URLs. Run upload script first.');
    return {};
  }
  
  const urls = fs.readJsonSync(URLS_FILE);
  const fontCount = Object.keys(urls).length;
  log.success(`Loaded CDN URLs for ${fontCount} font families`);
  
  return urls;
}

/**
 * Transform metadata to npm package format with CDN URLs
 */
function transformMetadata(metadata, cdnUrls) {
  const fonts = {};
  
  // Process font families and standalone fonts
  if (metadata.fonts) {
    metadata.fonts.forEach(font => {
      if (font.children && font.children.length > 0) {
        // Font family with multiple weights
        font.children.forEach(child => {
          const fontKey = `${font.name}-${child.name}`;
          const weight = child.name;
          
          // Get CDN URLs for this font
          const fontCDN = cdnUrls[font.name]?.[weight] || {};
          
          fonts[fontKey] = {
            name: child.full_name || `${font.name} ${child.name}`,
            family: font.name,
            subfamily: child.subfamily_name || child.name,
            weight: weight,
            charCount: child.char_count,
            glyphCount: child.glyph_count,
            unicodeRanges: child.unicode_ranges,
            // CDN URLs from upload script
            files: {
              source: `fonts/${font.name}/${child.name}.ttf`,
              subsets: fontCDN // Contains CSS and chunks for each subset
            },
            // Placeholder for license info (to be filled manually or by license script)
            license: {
              type: 'Unknown',
              url: null,
              text: null,
              usageRights: {
                commercial: false,
                modification: false,
                distribution: false,
                privateUse: true
              }
            }
          };
        });
      } else {
        // Standalone font
        const fontKey = font.name;
        const fontCDN = cdnUrls[font.name] || {};
        
        fonts[fontKey] = {
          name: font.full_name || font.name,
          family: font.name,
          subfamily: font.subfamily_name || 'Regular',
          charCount: font.char_count,
          glyphCount: font.glyph_count,
          unicodeRanges: font.unicode_ranges,
          files: {
            source: `fonts/${font.name}.ttf`,
            subsets: fontCDN
          },
          license: {
            type: 'Unknown',
            url: null,
            text: null,
            usageRights: {
              commercial: false,
              modification: false,
              distribution: false,
              privateUse: true
            }
          }
        };
      }
    });
  }
  
  return fonts;
}

/**
 * Generate index.js with font query APIs and auto-load functionality
 */
function generateIndexJs(fonts) {
  return `/**
 * Chinese Fonts CDN Package
 * 
 * This package provides access to Chinese web fonts with CDN links
 * and license information.
 */

const fonts = require('./fonts.json');

// Track loaded fonts to avoid duplicate loading
const loadedFonts = new Set();

/**
 * Load a font by automatically injecting its CSS into the document
 * @param {string} fontName - The name of the font
 * @param {Object} options - Loading options
 * @param {string} options.subset - The subset to load (default: 'zh-common' or first available)
 * @param {boolean} options.preload - Whether to preload the font (default: false)
 * @returns {Promise<string>} Promise that resolves with the CSS URL when loaded
 */
function loadFont(fontName, options = {}) {
  return new Promise((resolve, reject) => {
    const font = fonts[fontName];
    if (!font) {
      return reject(new Error(\`Font "\${fontName}" not found\`));
    }

    const subsets = font.files?.subsets;
    if (!subsets || Object.keys(subsets).length === 0) {
      return reject(new Error(\`No subsets available for font "\${fontName}"\`));
    }

    // Determine which subset to load
    let subset = options.subset;
    if (!subset) {
      // Default priority: zh-common > zh > en > first available
      if (subsets['zh-common']) subset = 'zh-common';
      else if (subsets['zh']) subset = 'zh';
      else if (subsets['en']) subset = 'en';
      else subset = Object.keys(subsets)[0];
    }

    const subsetData = subsets[subset];
    if (!subsetData || !subsetData.css) {
      return reject(new Error(\`Subset "\${subset}" not found for font "\${fontName}"\`));
    }

    const cssUrl = subsetData.css;
    const cacheKey = \`\${fontName}-\${subset}\`;

    // Check if already loaded
    if (loadedFonts.has(cacheKey)) {
      return resolve(cssUrl);
    }

    // Check if running in browser environment
    if (typeof document === 'undefined') {
      // Server-side: just return the URL
      loadedFonts.add(cacheKey);
      return resolve(cssUrl);
    }

    // Browser-side: inject CSS link
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = cssUrl;
    
    if (options.preload) {
      const preloadLink = document.createElement('link');
      preloadLink.rel = 'preload';
      preloadLink.as = 'style';
      preloadLink.href = cssUrl;
      document.head.appendChild(preloadLink);
    }

    link.onload = () => {
      loadedFonts.add(cacheKey);
      resolve(cssUrl);
    };

    link.onerror = () => {
      reject(new Error(\`Failed to load font CSS: \${cssUrl}\`));
    };

    document.head.appendChild(link);
  });
}

/**
 * Create a font loader function for a specific font
 * This allows: import font from 'windfonts-chinese-fonts/fonts/FontName'
 * @param {string} fontName - The name of the font
 * @returns {Function} Font loader function
 */
function createFontLoader(fontName) {
  const loader = (options) => loadFont(fontName, options);
  loader.fontName = fontName;
  loader.info = fonts[fontName];
  loader.load = (options) => loadFont(fontName, options);
  loader.getCSS = (subset) => getFontCSS(fontName, subset);
  loader.getSubsets = () => getFontSubsets(fontName);
  return loader;
}

/**
 * Get all available font names
 * @returns {string[]} Array of font names
 */
function getAllFonts() {
  return Object.keys(fonts);
}

/**
 * Get complete information for a specific font
 * @param {string} fontName - The name of the font
 * @returns {Object|undefined} Font information object
 */
function getFontInfo(fontName) {
  return fonts[fontName];
}

/**
 * Get the CSS URL for a specific font and subset
 * @param {string} fontName - The name of the font
 * @param {string} subset - The subset name (e.g., 'chinese', 'latin', default: first available)
 * @returns {string|undefined} CSS file URL
 */
function getFontCSS(fontName, subset) {
  const subsets = fonts[fontName]?.files?.subsets;
  if (!subsets) return undefined;
  
  // If subset specified, return that subset's CSS
  if (subset && subsets[subset]) {
    return subsets[subset].css;
  }
  
  // Otherwise return the first available subset's CSS
  const firstSubset = Object.keys(subsets)[0];
  return firstSubset ? subsets[firstSubset].css : undefined;
}

/**
 * Get all available subsets for a font
 * @param {string} fontName - The name of the font
 * @returns {string[]} Array of subset names
 */
function getFontSubsets(fontName) {
  const subsets = fonts[fontName]?.files?.subsets;
  return subsets ? Object.keys(subsets) : [];
}

/**
 * Get font chunks (woff2 files) for a specific subset
 * @param {string} fontName - The name of the font
 * @param {string} subset - The subset name
 * @returns {Array|undefined} Array of chunk objects with file and url
 */
function getFontChunks(fontName, subset) {
  return fonts[fontName]?.files?.subsets?.[subset]?.chunks;
}

/**
 * Get license information for a specific font
 * @param {string} fontName - The name of the font
 * @returns {Object|undefined} License information
 */
function getFontLicense(fontName) {
  return fonts[fontName]?.license;
}

/**
 * Get the license file CDN URL for a specific font
 * @param {string} fontName - The name of the font
 * @returns {string|undefined} License file URL
 */
function getLicenseUrl(fontName) {
  return fonts[fontName]?.license?.url;
}

/**
 * Get the license type for a specific font
 * @param {string} fontName - The name of the font
 * @returns {string|undefined} License type (e.g., 'OFL', 'MIT', 'Apache-2.0')
 */
function getLicenseType(fontName) {
  return fonts[fontName]?.license?.type;
}

/**
 * Get usage rights for a specific font
 * @param {string} fontName - The name of the font
 * @returns {Object|undefined} Usage rights object
 */
function getUsageRights(fontName) {
  return fonts[fontName]?.license?.usageRights;
}

/**
 * Check if a font allows commercial use
 * @param {string} fontName - The name of the font
 * @returns {boolean} True if commercial use is allowed
 */
function isCommercialUseAllowed(fontName) {
  return fonts[fontName]?.license?.usageRights?.commercial === true;
}

// Export main API
module.exports = {
  fonts,
  loadFont,
  createFontLoader,
  getAllFonts,
  getFontInfo,
  getFontCSS,
  getFontSubsets,
  getFontChunks,
  getFontLicense,
  getLicenseUrl,
  getLicenseType,
  getUsageRights,
  isCommercialUseAllowed
};
`;
}

/**
 * Generate index.d.ts TypeScript definitions
 */
function generateTypeDefinitions() {
  return `/**
 * Chinese Fonts CDN Package - TypeScript Definitions
 */

export interface UsageRights {
  commercial: boolean;
  modification: boolean;
  distribution: boolean;
  privateUse: boolean;
}

export interface FontLicense {
  type: string;
  url: string | null;
  text: string | null;
  usageRights: UsageRights;
}

export interface FontChunk {
  file: string;
  url: string;
}

export interface FontSubset {
  css: string;
  chunks: FontChunk[];
}

export interface FontFiles {
  source: string;
  subsets: Record<string, FontSubset>;
}

export interface UnicodeRanges {
  [rangeName: string]: number;
}

export interface FontInfo {
  name: string;
  family: string;
  subfamily: string;
  weight?: string;
  charCount: number;
  glyphCount: number;
  unicodeRanges: UnicodeRanges;
  files: FontFiles;
  license: FontLicense;
}

export interface LoadFontOptions {
  subset?: string;
  preload?: boolean;
}

export interface FontLoader {
  (options?: LoadFontOptions): Promise<string>;
  fontName: string;
  info: FontInfo;
  load: (options?: LoadFontOptions) => Promise<string>;
  getCSS: (subset?: string) => string | undefined;
  getSubsets: () => string[];
}

export const fonts: Record<string, FontInfo>;

export function loadFont(fontName: string, options?: LoadFontOptions): Promise<string>;
export function createFontLoader(fontName: string): FontLoader;
export function getAllFonts(): string[];
export function getFontInfo(fontName: string): FontInfo | undefined;
export function getFontCSS(fontName: string, subset?: string): string | undefined;
export function getFontSubsets(fontName: string): string[];
export function getFontChunks(fontName: string, subset: string): FontChunk[] | undefined;
export function getFontLicense(fontName: string): FontLicense | undefined;
export function getLicenseUrl(fontName: string): string | undefined;
export function getLicenseType(fontName: string): string | undefined;
export function getUsageRights(fontName: string): UsageRights | undefined;
export function isCommercialUseAllowed(fontName: string): boolean;
`;
}

/**
 * Generate README.md documentation
 */
function generateReadme(fonts) {
  const fontList = Object.keys(fonts);
  const fontCount = fontList.length;
  
  let readme = `# Chinese Fonts CDN

A collection of Chinese web fonts with CDN links and comprehensive license information.

## Installation

\`\`\`bash
npm install windfonts-chinese-fonts
\`\`\`

## Usage

### Method 1: Auto-load (Recommended)

Simply import and the font will be automatically loaded:

\`\`\`javascript
// Import and auto-load with default subset (zh-common)
const { loadFont } = require('windfonts-chinese-fonts');

// Load a font (returns Promise)
loadFont('${fontList[0] || 'FontName'}').then(cssUrl => {
  console.log('Font loaded:', cssUrl);
  // Font is now available to use
});

// Load with specific subset
loadFont('${fontList[0] || 'FontName'}', { subset: 'zh-common' });

// Load with preload for better performance
loadFont('${fontList[0] || 'FontName'}', { subset: 'zh-common', preload: true });
\`\`\`

### Method 2: Individual Font Import

Import specific fonts directly:

\`\`\`javascript
// Import a specific font
const font = require('windfonts-chinese-fonts/fonts/${fontList[0] || 'FontName'}');

// Load the font (auto-loads with default subset)
font().then(cssUrl => {
  console.log('Font loaded:', cssUrl);
});

// Or with options
font({ subset: 'en' }).then(cssUrl => {
  console.log('English subset loaded:', cssUrl);
});

// Access font information
console.log(font.fontName);  // Font name
console.log(font.info);      // Full font information
console.log(font.getSubsets()); // Available subsets
console.log(font.getCSS('zh-common')); // Get CSS URL without loading
\`\`\`

### Method 3: Manual CSS URL

Get the CSS URL without auto-loading:

\`\`\`javascript
const { getFontCSS, getFontSubsets } = require('windfonts-chinese-fonts');

// Get CSS URL
const cssUrl = getFontCSS('${fontList[0] || 'FontName'}', 'zh-common');
console.log(\`CSS URL: \${cssUrl}\`);

// Get available subsets
const subsets = getFontSubsets('${fontList[0] || 'FontName'}');
console.log(\`Available subsets: \${subsets.join(', ')}\`);

// Manually add to HTML
// <link rel="stylesheet" href="\${cssUrl}">
\`\`\`

## License Information API

This package provides comprehensive license information for each font:

\`\`\`javascript
const { getLicenseType, getLicenseUrl, getUsageRights } = require('windfonts-chinese-fonts');

// Get license type
const licenseType = getLicenseType('FontName');
console.log(\`License: \${licenseType}\`); // e.g., 'OFL', 'MIT', 'Apache-2.0'

// Get license file URL
const licenseUrl = getLicenseUrl('FontName');
console.log(\`License URL: \${licenseUrl}\`);

// Get detailed usage rights
const rights = getUsageRights('FontName');
console.log(\`Commercial use: \${rights.commercial}\`);
console.log(\`Modification: \${rights.modification}\`);
console.log(\`Distribution: \${rights.distribution}\`);
console.log(\`Private use: \${rights.privateUse}\`);
\`\`\`

## Available Fonts

This package includes ${fontCount} fonts:

`;

  // Add font list with license information
  fontList.slice(0, 10).forEach(fontKey => {
    const font = fonts[fontKey];
    const subsets = font.files.subsets || {};
    const subsetNames = Object.keys(subsets);
    const firstSubset = subsetNames[0];
    const cssUrl = firstSubset ? subsets[firstSubset].css : 'Not available';
    
    readme += `### ${font.name}\n\n`;
    readme += `- **Family**: ${font.family}\n`;
    readme += `- **Subfamily**: ${font.subfamily}\n`;
    readme += `- **Available Subsets**: ${subsetNames.length > 0 ? subsetNames.join(', ') : 'None'}\n`;
    readme += `- **CSS URL**: ${cssUrl}\n`;
    readme += `- **License**: ${font.license.type}\n`;
    readme += `- **License URL**: ${font.license.url || 'Not available'}\n`;
    readme += `- **Commercial Use**: ${font.license.usageRights.commercial ? '✅ Allowed' : '❌ Not allowed'}\n\n`;
    
    // Add usage example
    if (cssUrl !== 'Not available') {
      readme += `**Usage:**\n\`\`\`html\n<link rel="stylesheet" href="${cssUrl}">\n\`\`\`\n\n`;
    }
  });

  if (fontCount > 10) {
    readme += `\n... and ${fontCount - 10} more fonts.\n\n`;
  }

  readme += `## TypeScript Support

This package includes TypeScript type definitions:

\`\`\`typescript
import { FontInfo, UsageRights, getAllFonts, getFontInfo } from 'windfonts-chinese-fonts';

const fonts: string[] = getAllFonts();
const fontInfo: FontInfo | undefined = getFontInfo('FontName');
\`\`\`

## License

Each font has its own license. Please check the license information for each font before use.

## Contributing

To add new fonts or update existing ones, please submit a pull request to the repository.
`;

  return readme;
}

/**
 * Get current version from existing package.json or default to 1.0.0
 */
function getCurrentVersion() {
  const packageJsonPath = path.join(OUTPUT_DIR, 'package.json');
  
  if (fs.existsSync(packageJsonPath)) {
    const pkg = fs.readJsonSync(packageJsonPath);
    return pkg.version || '1.0.0';
  }
  
  return '1.0.0';
}

/**
 * Get next version (increment patch)
 */
function getNextVersion(currentVersion) {
  return semver.inc(currentVersion, 'patch');
}

/**
 * Generate package.json
 */
function generatePackageJson(version) {
  return {
    name: '@windfonts/chinese-fonts',
    version: version,
    description: 'Chinese web fonts with CDN links and comprehensive license information',
    main: 'src/index.js',
    types: 'src/index.d.ts',
    files: [
      'src',
      'fonts'
    ],
    keywords: [
      'fonts',
      'chinese',
      'cjk',
      'webfonts',
      'cdn',
      'typography',
      'license',
      'windfonts',
      '中文字体',
      'web-fonts',
      'font-loader',
      'alibaba-puhuiti',
      'chinese-typography'
    ],
    author: 'WindFonts',
    license: 'SEE LICENSE IN README.md',
    repository: {
      type: 'git',
      url: 'https://github.com/Windfonts/font-packages.git'
    },
    bugs: {
      url: 'https://github.com/Windfonts/font-packages/issues'
    },
    homepage: 'https://github.com/Windfonts/font-packages#readme'
  };
}

/**
 * Configure npm authentication
 */
function configureNpmAuth() {
  if (!NPM_TOKEN) {
    log.warn('NPM_TOKEN not found in environment variables');
    return false;
  }
  
  const npmrcPath = path.join(process.env.HOME || process.env.USERPROFILE, '.npmrc');
  const npmrcContent = `//registry.npmjs.org/:_authToken=${NPM_TOKEN}\n`;
  
  try {
    fs.writeFileSync(npmrcPath, npmrcContent);
    log.success('NPM authentication configured');
    return true;
  } catch (error) {
    log.error(`Failed to configure npm auth: ${error.message}`);
    return false;
  }
}

/**
 * Publish package to npm
 */
function publishPackage() {
  if (DRY_RUN) {
    log.info('DRY RUN: Skipping npm publish');
    return;
  }
  
  if (!NPM_TOKEN) {
    log.error('Cannot publish: NPM_TOKEN not configured');
    throw new Error('NPM_TOKEN required for publishing');
  }
  
  log.info('Publishing package to npm...');
  
  try {
    execSync('npm publish --access public', {
      cwd: OUTPUT_DIR,
      stdio: 'inherit'
    });
    log.success('Package published successfully!');
  } catch (error) {
    log.error(`Failed to publish package: ${error.message}`);
    throw error;
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    log.info('Starting npm package generation...');
    
    // Read metadata
    const metadata = readMetadata();
    
    // Read CDN URLs
    const cdnUrls = readCDNUrls();
    
    // Transform metadata with CDN URLs
    log.info('Transforming metadata with CDN URLs...');
    const fonts = transformMetadata(metadata, cdnUrls);
    log.success(`Transformed ${Object.keys(fonts).length} fonts`);
    
    // Determine version
    const currentVersion = getCurrentVersion();
    const nextVersion = VERSION || getNextVersion(currentVersion);
    log.info(`Package version: ${nextVersion} (previous: ${currentVersion})`);
    
    // Create output directory structure
    log.info(`Creating package structure in ${OUTPUT_DIR}...`);
    fs.ensureDirSync(path.join(OUTPUT_DIR, 'src'));
    
    // Generate files
    log.info('Generating package files...');
    
    // index.js
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'src', 'index.js'),
      generateIndexJs(fonts)
    );
    log.success('Generated src/index.js');
    
    // Generate individual font files
    log.info('Generating individual font loaders...');
    const fontsDir = path.join(OUTPUT_DIR, 'fonts');
    fs.ensureDirSync(fontsDir);
    
    Object.keys(fonts).forEach(fontKey => {
      const fontFile = `const { createFontLoader } = require('../src/index.js');
module.exports = createFontLoader('${fontKey}');
`;
      fs.writeFileSync(
        path.join(fontsDir, `${fontKey}.js`),
        fontFile
      );
    });
    log.success(`Generated ${Object.keys(fonts).length} individual font loaders`);
    
    // index.d.ts
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'src', 'index.d.ts'),
      generateTypeDefinitions()
    );
    log.success('Generated src/index.d.ts');
    
    // fonts.json
    fs.writeJsonSync(
      path.join(OUTPUT_DIR, 'src', 'fonts.json'),
      fonts,
      { spaces: 2 }
    );
    log.success('Generated src/fonts.json');
    
    // package.json
    fs.writeJsonSync(
      path.join(OUTPUT_DIR, 'package.json'),
      generatePackageJson(nextVersion),
      { spaces: 2 }
    );
    log.success('Generated package.json');
    
    // README.md
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'README.md'),
      generateReadme(fonts)
    );
    log.success('Generated README.md');
    
    // Configure npm authentication
    if (!DRY_RUN) {
      configureNpmAuth();
    }
    
    // Publish package
    if (DRY_RUN) {
      log.info('DRY RUN: Package generated but not published');
      log.info(`Package location: ${OUTPUT_DIR}`);
    } else {
      publishPackage();
    }
    
    // Summary
    log.success('='.repeat(50));
    log.success('NPM Package Generation Complete!');
    log.success('='.repeat(50));
    log.info(`Package: windfonts-chinese-fonts@${nextVersion}`);
    log.info(`Fonts: ${Object.keys(fonts).length}`);
    log.info(`Location: ${OUTPUT_DIR}`);
    if (DRY_RUN) {
      log.info('Mode: DRY RUN (not published)');
    } else {
      log.info('Status: Published to npm');
    }
    
  } catch (error) {
    log.error(`Failed to generate npm package: ${error.message}`);
    console.error(error);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = {
  readMetadata,
  transformMetadata,
  generateIndexJs,
  generateTypeDefinitions,
  generateReadme,
  generatePackageJson
};
