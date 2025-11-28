/**
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
      return reject(new Error(`Font "${fontName}" not found`));
    }

    const subsets = font.files?.subsets;
    if (!subsets || Object.keys(subsets).length === 0) {
      return reject(new Error(`No subsets available for font "${fontName}"`));
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
      return reject(new Error(`Subset "${subset}" not found for font "${fontName}"`));
    }

    const cssUrl = subsetData.css;
    const cacheKey = `${fontName}-${subset}`;

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
      reject(new Error(`Failed to load font CSS: ${cssUrl}`));
    };

    document.head.appendChild(link);
  });
}

/**
 * Create a font loader function for a specific font
 * This allows: import font from '@windfonts/chinese-fonts/fonts/FontName'
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
