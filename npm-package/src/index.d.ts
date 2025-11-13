/**
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
