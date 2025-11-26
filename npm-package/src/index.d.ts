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

export type FontName = 'Albbpht-Bold' | 'Albbpht-Heavy' | 'Albbpht-Light' | 'Albbpht-Medium' | 'Albbpht-Regular' | 'Alhyznht-Regular' | 'Almmdfdk-Regular' | 'Almmdlt-Regular' | 'Almmsht-Bold' | 'Azbzzwzt-Regular' | 'Btot-Regular' | 'Btxbt-Regular' | 'Cexwz-Regular' | 'Cezkzdbs-Regular' | 'Cjkfqlt-Regular' | 'Cktjgt-Regular' | 'Cqscbbt-Regular' | 'Cylyt-Monospaced' | 'Cylyt-Regular' | 'Ddjbt-Normal' | 'Ddjbt-Regular' | 'Ddxstfx-Regular' | 'Ddxstlx-Regular' | 'Ddxstyx-Regular' | 'Dlkjt-Regular' | 'Dlzht-Normal' | 'Dyh-Oblique' | 'Dymht-Regular' | 'Dyzgt-Regular' | 'Gfmft-Regular' | 'Gljgbt-Regular' | 'Hcdht-Black' | 'Hcdht-Light' | 'Hckht-Normal' | 'Hclcks-Bold' | 'Hclcks-Extrabold' | 'Hclcks-Medium' | 'Hclcks-Regular' | 'Hcszt-Normal' | 'Hctyt-Normal' | 'Hctyt-Round' | 'Hkhlssxt-Regular' | 'Hsmbzt-Regular' | 'Hxbnst-Regular' | 'Hxbsb-Normal' | 'Hxbsbt-Regular' | 'Hxbzst-Regular' | 'Hyqzpt-Regular' | 'Hzpy-Regular' | 'Hzpyt-Regular' | 'Ibmps-Bold' | 'Ibmps-Extralight' | 'Ibmps-Light' | 'Ibmps-Regular' | 'Ibmps-Text' | 'Ibmps-Thin' | 'Jnbbh-Regular' | 'Jnymt-Regular' | 'Jnyyjyy-Regular' | 'Jsyjst-Regular' | 'Jxzk-Regular' | 'Jzkgeht-Heavy' | 'Jzkgemc-Heavy' | 'Kksjt-Regular' | 'Klsyt-Regular' | 'Kslgbht-Regular' | 'Kslmt-Regular' | 'Kslyt-Regular' | 'Lftsyh-Regular' | 'Lhktss-Regular' | 'Lhls-Regular' | 'Lhzt-Regular' | 'Light-Systcn' | 'Ljmc-Regular' | 'Lmqylszrht-Regular' | 'Misa-Bold' | 'Misa-Demibold' | 'Misa-Extralight' | 'Misa-Heavy' | 'Misa-Light' | 'Misa-Medium' | 'Misa-Normal' | 'Misa-Regular' | 'Misa-Semibold' | 'Misa-Thin' | 'Mksjh-Bold' | 'Mkwfys-Regular' | 'Mkwgzh-Regular' | 'Mkwgzs-Regular' | 'Mkwxy-Regular' | 'Mkzyt-Regular' | 'Mspyt-Regular' | 'Myrbsxt-Regular' | 'Mysxt-Regular' | 'Nsfx-Regular' | 'Nswt-Italic' | 'Nswt-Regular' | 'Opsa-Bold' | 'Opsa-Light' | 'Opsa-Medium' | 'Opsa-Regular' | 'Pfhtt-Regular' | 'Pmzdbtt-Regular' | 'Pmzdcsd-Regular' | 'Pmzdqst-Regular' | 'Pmzdzgkt-Regular' | 'Prsxt-Regular' | 'Pxzs-Regular' | 'Qssxt-Regular' | 'Qtbfsxt-Regular' | 'Qthht-Regular' | 'Qtmksxt-Regular' | 'Qtqmt-Regular' | 'Qtxht-Regular' | 'Qtxmt-Regular' | 'Qtxtt-Regular' | 'Qzkswjz-Regular' | 'Rzzyt-Regular' | 'Scjskkt-Regular' | 'Sft-Regular' | 'Stfytz-Regular' | 'Stfzxfxct-Regular' | 'Syhtcjk-Black' | 'Syhtcjk-Bold' | 'Syhtcjk-DemiLight' | 'Syhtcjk-Light' | 'Syhtcjk-Medium' | 'Syhtcjk-Regular' | 'Syhtcjk-Thin' | 'Symdxft-Regular' | 'Systcn-Bold' | 'Systcn-Extralight' | 'Systcn-Heavy' | 'Systcn-Light' | 'Systcn-Medium' | 'Systcn-Regular' | 'Systcn-Semibold' | 'Twjybbzjs-Regular' | 'Twjybbzst-Regular' | 'Twjybxxmt-Regular' | 'Unfdzh-Regular' | 'Wcsf-Normal' | 'Wqydkwmh-Regular' | 'Wqydkzh-Regular' | 'Wqywmh-Regular' | 'Wqyzh-Regular' | 'Xet-Regular' | 'Xlfht-Regular' | 'Xsslv-Regular' | 'Xwmh-Regular' | 'Xwxxh-Regular' | 'Xwxzs-Regular' | 'Ydwbnnsp-Regular' | 'Yffyt-Regular' | 'Yjmct-Regular' | 'Ysbth-Bold' | 'Ysbzt-Regular' | 'Yzklct-Regular' | 'Zhbtt-Oblique' | 'Zjgljt-Regular' | 'Zkgdht-Regular' | 'Zkkht-Regular' | 'Zkklt-Regular' | 'Zkwyt-Regular' | 'Zkxwt-Regular' | 'Zqkhyt-Regular' | 'Ztqxyjxs-Regular' | 'Zwxszt-Regular' | 'Zyss-Regular';
export const fonts: Record<FontName, FontInfo>;

export function loadFont(fontName: FontName, options?: LoadFontOptions): Promise<string>;
export function createFontLoader(fontName: FontName): FontLoader;
export function getAllFonts(): FontName[];
export function getFontInfo(fontName: FontName): FontInfo | undefined;
export function getFontCSS(fontName: FontName, subset?: string): string | undefined;
export function getFontSubsets(fontName: FontName): string[];
export function getFontChunks(fontName: FontName, subset: string): FontChunk[] | undefined;
export function getFontLicense(fontName: FontName): FontLicense | undefined;
export function getLicenseUrl(fontName: FontName): string | undefined;
export function getLicenseType(fontName: FontName): string | undefined;
export function getUsageRights(fontName: FontName): UsageRights | undefined;
export function isCommercialUseAllowed(fontName: FontName): boolean;

declare module '@windfonts/chinese-fonts/fonts/*' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Albbpht-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Albbpht-Heavy' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Albbpht-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Albbpht-Medium' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Albbpht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Alhyznht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Almmdfdk-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Almmdlt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Almmsht-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Azbzzwzt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Btot-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Btxbt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cexwz-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cezkzdbs-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cjkfqlt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cktjgt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cqscbbt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cylyt-Monospaced' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Cylyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ddjbt-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ddjbt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ddxstfx-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ddxstlx-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ddxstyx-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Dlkjt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Dlzht-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Dyh-Oblique' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Dymht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Dyzgt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Gfmft-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Gljgbt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hcdht-Black' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hcdht-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hckht-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hclcks-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hclcks-Extrabold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hclcks-Medium' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hclcks-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hcszt-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hctyt-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hctyt-Round' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hkhlssxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hsmbzt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hxbnst-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hxbsb-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hxbsbt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hxbzst-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hyqzpt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hzpy-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Hzpyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ibmps-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ibmps-Extralight' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ibmps-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ibmps-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ibmps-Text' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ibmps-Thin' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jnbbh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jnymt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jnyyjyy-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jsyjst-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jxzk-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jzkgeht-Heavy' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Jzkgemc-Heavy' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Kksjt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Klsyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Kslgbht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Kslmt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Kslyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Lftsyh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Lhktss-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Lhls-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Lhzt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Light-Systcn' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ljmc-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Lmqylszrht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Demibold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Extralight' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Heavy' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Medium' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Semibold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Misa-Thin' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mksjh-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mkwfys-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mkwgzh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mkwgzs-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mkwxy-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mkzyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mspyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Myrbsxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Mysxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Nsfx-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Nswt-Italic' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Nswt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Opsa-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Opsa-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Opsa-Medium' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Opsa-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Pfhtt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Pmzdbtt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Pmzdcsd-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Pmzdqst-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Pmzdzgkt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Prsxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Pxzs-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qssxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qtbfsxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qthht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qtmksxt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qtqmt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qtxht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qtxmt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qtxtt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Qzkswjz-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Rzzyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Scjskkt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Sft-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Stfytz-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Stfzxfxct-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-Black' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-DemiLight' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-Medium' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Syhtcjk-Thin' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Symdxft-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Extralight' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Heavy' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Light' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Medium' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Systcn-Semibold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Twjybbzjs-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Twjybbzst-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Twjybxxmt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Unfdzh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Wcsf-Normal' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Wqydkwmh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Wqydkzh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Wqywmh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Wqyzh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Xet-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Xlfht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Xsslv-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Xwmh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Xwxxh-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Xwxzs-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ydwbnnsp-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Yffyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Yjmct-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ysbth-Bold' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ysbzt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Yzklct-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zhbtt-Oblique' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zjgljt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zkgdht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zkkht-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zkklt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zkwyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zkxwt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zqkhyt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Ztqxyjxs-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zwxszt-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
declare module '@windfonts/chinese-fonts/fonts/Zyss-Regular' {
  const loader: import('./index').FontLoader;
  export default loader;
}
