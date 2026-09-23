#!/usr/bin/env python3
"""Turn a BDF into a static TTF of square pixels. JIS X 0208 encodings are mapped to Unicode."""
import sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


def jis_to_unicode(enc):
    if enc < 256:
        return enc
    hi, lo = (enc >> 8) & 0xff, enc & 0xff
    if hi < 0x21 or lo < 0x21 or hi > 0x7e or lo > 0x7e:
        return enc if enc <= 0x10FFFF else None
    raw = bytes([0x1B, 0x24, 0x42, hi, lo, 0x1B, 0x28, 0x42])
    try:
        s = raw.decode("iso2022_jp")
    except Exception:
        return None
    if len(s) != 1:
        return None
    return ord(s)


def parse_bdf(path, jis=False):
    glyphs = {}
    meta = {"ascent": 12, "descent": 2, "family": "Bitmap"}
    cur = None
    in_bitmap = False
    rows = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("FAMILY_NAME "):
                meta["family"] = line.split(" ", 1)[1].strip().strip('"')
            elif line.startswith("FONT_ASCENT "):
                meta["ascent"] = int(line.split()[1])
            elif line.startswith("FONT_DESCENT "):
                meta["descent"] = int(line.split()[1])
            elif line.startswith("CHARSET_REGISTRY "):
                meta["charset"] = line.split(" ", 1)[1].strip().strip('"').lower()
            elif line == "BITMAP":
                in_bitmap = True
                rows = []
            elif line == "ENDCHAR":
                in_bitmap = False
                if cur and cur.get("enc") is not None:
                    uni = jis_to_unicode(cur["enc"]) if jis or "jis" in meta.get("charset", "") else cur["enc"]
                    if uni is not None and 0 < uni <= 0x10FFFF and uni not in glyphs:
                        glyphs[uni] = (cur["bbx"], cur["dwidth"], rows)
                cur = None
            elif in_bitmap:
                rows.append(line.strip())
            elif line.startswith("STARTCHAR"):
                cur = {"enc": None, "bbx": (0, 0, 0, 0), "dwidth": 12}
            elif cur is not None and line.startswith("ENCODING "):
                cur["enc"] = int(line.split()[1])
            elif cur is not None and line.startswith("DWIDTH "):
                cur["dwidth"] = int(line.split()[1])
            elif cur is not None and line.startswith("BBX "):
                parts = line.split()
                cur["bbx"] = tuple(int(x) for x in parts[1:5])
    return meta, glyphs


def build(path, out, family, full, jis=False):
    meta, glyphs = parse_bdf(path, jis=jis)
    ppem = max(1, meta["ascent"] + meta["descent"])
    scale = 1000 / ppem
    ascent = int(round(meta["ascent"] * scale))
    descent = int(round(meta["descent"] * scale))
    order = [".notdef"]
    glyf = {}
    cmap = {}
    metrics = {".notdef": (600, 0)}
    pen = TTGlyphPen(None)
    glyf[".notdef"] = pen.glyph()
    for uni in sorted(glyphs):
        (bw, bh, xoff, yoff), dwidth, rows = glyphs[uni]
        name = "uni%04X" % uni if uni <= 0xFFFF else "u%X" % uni
        pen = TTGlyphPen(None)
        for r, hexrow in enumerate(rows):
            if not hexrow:
                continue
            bits = int(hexrow, 16)
            width_bits = max(bw, len(hexrow) * 4)
            y = (yoff + (bh - 1 - r)) * scale
            c = 0
            while c < bw:
                bit = 1 << (width_bits - 1 - c)
                if bits & bit:
                    start = c
                    c += 1
                    while c < bw and (bits & (1 << (width_bits - 1 - c))):
                        c += 1
                    x0 = (xoff + start) * scale
                    x1 = (xoff + c) * scale
                    y0 = y
                    y1 = y + scale
                    pen.moveTo((x0, y0))
                    pen.lineTo((x1, y0))
                    pen.lineTo((x1, y1))
                    pen.lineTo((x0, y1))
                    pen.closePath()
                else:
                    c += 1
        order.append(name)
        glyf[name] = pen.glyph()
        cmap[uni] = name
        adv = max(1, int(round(dwidth * scale)))
        metrics[name] = (adv, 0)
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyf)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascent, descent=-descent)
    fb.setupOS2(
        sTypoAscender=ascent,
        sTypoDescender=-descent,
        usWinAscent=ascent,
        usWinDescent=descent,
        sxHeight=int(ascent * 0.5),
        sCapHeight=int(ascent * 0.7),
    )
    fb.setupPost()
    fb.setupNameTable({
        "familyName": family,
        "styleName": "Regular",
        "uniqueFontIdentifier": family.replace(" ", "") + "-Regular",
        "fullName": full,
        "psName": family.replace(" ", "") + "-Regular",
        "version": "Version 1.000",
    })
    fb.save(out)
    cjk = sum(1 for u in cmap if 0x4E00 <= u <= 0x9FFF)
    print(out, "glyphs", len(cmap), "cjk", cjk, "family", family)


if __name__ == "__main__":
    src, dest, family, full = sys.argv[1:5]
    jis = "--jis" in sys.argv[5:]
    build(src, dest, family, full, jis=jis)
