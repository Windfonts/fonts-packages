const fs = require('fs');
const path = require('path');
const src = path.join(__dirname, '..', 'src', 'fonts.json');
const raw = fs.readFileSync(src, 'utf8');
const data = JSON.parse(raw);

const pruneSubsets = (subsets) => {
  if (!subsets || typeof subsets !== 'object') return {};
  const out = {};
  for (const [name, info] of Object.entries(subsets)) {
    out[name] = {
      css: info && info.css,
      chunks: Array.isArray(info && info.chunks)
        ? info.chunks.map((c) => ({ file: c.file, url: c.url }))
        : undefined,
    };
  }
  return out;
};

const lean = {};
for (const [fontName, f] of Object.entries(data)) {
  lean[fontName] = {
    family: f.family,
    files: {
      subsets: pruneSubsets(f.files && f.files.subsets),
    },
    license: f.license,
  };
}

fs.writeFileSync(src, JSON.stringify(lean));
console.log('fonts.json pruned and minified');

const outDir = path.join(__dirname, '..', 'src', 'font-data');
try { fs.mkdirSync(outDir, { recursive: true }); } catch {}
const names = Object.keys(lean);
for (const name of names) {
  const fp = path.join(outDir, `${name}.json`);
  fs.writeFileSync(fp, JSON.stringify(lean[name]));
}
const listPath = path.join(__dirname, '..', 'src', 'font-list.json');
fs.writeFileSync(listPath, JSON.stringify(names));
console.log(`split ${names.length} fonts into font-data and wrote font-list.json`);
