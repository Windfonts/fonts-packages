import { createRequire } from 'module'
const require = createRequire(import.meta.url)
const fontList = require('./font-list.json')
function getFontData(name) { try { return require(`./font-data/${name}.json`) } catch (_) { return undefined } }
const fonts = new Proxy({}, { get: (_, k) => getFontData(k) })
const loadedFonts = new Set()
function loadFont(fontName, options = {}) {
  return new Promise((resolve, reject) => {
    const font = getFontData(fontName)
    if (!font) return reject(new Error(`Font "${fontName}" not found`))
    const subsets = font.files?.subsets
    if (!subsets || Object.keys(subsets).length === 0) return reject(new Error(`No subsets available for font "${fontName}"`))
    let subset = options.subset
    if (!subset) { if (subsets['zh-common']) subset = 'zh-common'; else if (subsets['zh']) subset = 'zh'; else if (subsets['en']) subset = 'en'; else subset = Object.keys(subsets)[0] }
    const subsetData = subsets[subset]
    if (!subsetData || !subsetData.css) return reject(new Error(`Subset "${subset}" not found for font "${fontName}"`))
    const cssUrl = subsetData.css
    const cacheKey = `${fontName}-${subset}`
    if (loadedFonts.has(cacheKey)) return resolve(cssUrl)
    if (typeof document === 'undefined') { loadedFonts.add(cacheKey); return resolve(cssUrl) }
    const link = document.createElement('link')
    link.rel = 'stylesheet'
    link.href = cssUrl
    if (options.preload) { const preloadLink = document.createElement('link'); preloadLink.rel = 'preload'; preloadLink.as = 'style'; preloadLink.href = cssUrl; document.head.appendChild(preloadLink) }
    link.onload = () => { loadedFonts.add(cacheKey); resolve(cssUrl) }
    link.onerror = () => { reject(new Error(`Failed to load font CSS: ${cssUrl}`)) }
    document.head.appendChild(link)
  })
}
function createFontLoader(fontName) { const loader = (options) => loadFont(fontName, options); loader.fontName = fontName; loader.info = getFontData(fontName); loader.load = (options) => loadFont(fontName, options); loader.getCSS = (subset) => getFontCSS(fontName, subset); loader.getSubsets = () => getFontSubsets(fontName); return loader }
function getAllFonts() { return Array.isArray(fontList) ? fontList : [] }
function getFontInfo(fontName) { return getFontData(fontName) }
function getFontCSS(fontName, subset) { const subsets = getFontData(fontName)?.files?.subsets; if (!subsets) return undefined; if (subset && subsets[subset]) return subsets[subset].css; const firstSubset = Object.keys(subsets)[0]; return firstSubset ? subsets[firstSubset].css : undefined }
function getFontSubsets(fontName) { const subsets = getFontData(fontName)?.files?.subsets; return subsets ? Object.keys(subsets) : [] }
function getFontChunks(fontName, subset) { return getFontData(fontName)?.files?.subsets?.[subset]?.chunks }
function getFontLicense(fontName) { return getFontData(fontName)?.license }
function getLicenseUrl(fontName) { return getFontData(fontName)?.license?.url }
function getLicenseType(fontName) { return getFontData(fontName)?.license?.type }
function getUsageRights(fontName) { return getFontData(fontName)?.license?.usageRights }
function isCommercialUseAllowed(fontName) { return getFontData(fontName)?.license?.usageRights?.commercial === true }
export { fonts, loadFont, createFontLoader, getAllFonts, getFontInfo, getFontCSS, getFontSubsets, getFontChunks, getFontLicense, getLicenseUrl, getLicenseType, getUsageRights, isCommercialUseAllowed }
