const { createClient } = require('@libsql/client');
const brands = [
  { id: '1a6c8e40-5d27-4b91-8f3a-9c2e7b04d651', name: 'ToneOZ', slug: 'toneoz', description: '晓声通秋茄。OFL 1.1。', website: 'https://github.com/jeffreyxuan/toneoz-font-tsuipita' },
  { id: '2b7d9f51-6e38-4c02-9a4b-0d3f8c15e762', name: 'MoneMizuno', slug: 'genne', description: '源音黑体 Genne Gothic。基于思源黑体。OFL 1.1。', website: 'https://github.com/MoneMizuno/Genne-Gothic' },
  { id: '3c8e0a62-7f49-4d13-8b5c-1e4a9d26f873', name: 'WD-XL', slug: 'wdxl', description: '滑油字。OFL 1.1。', website: 'https://github.com/NightFurySL2001/WD-XL-font' },
  { id: '4d9f1b73-805a-4e24-9c6d-2f5b0e37a984', name: 'NoHeartPen', slug: 'qiushui', description: '秋水书体。OFL 1.1。', website: 'https://github.com/NoHeartPen/QiushuiShotai' },
  { id: '5e0a2c84-916b-4f35-8d7e-3a6c1f48b095', name: 'ChiuMing-Neko', slug: 'chiukong', description: '秋空黑体。基于思源黑体。OFL 1.1。', website: 'https://github.com/ChiuMing-Neko/ChiuKongGothic' },
  { id: '6f1b3d95-a27c-4046-9e8f-4b7d2a59c0a6', name: '字言字语', slug: 'boutique', description: '精品点阵体。可免费使用、复制、修改和分发。不是 SIL OFL。', website: 'https://github.com/scott0107000/BoutiqueBitmap9x9' },
  { id: '7a2c4e06-b38d-4157-8f90-5c8e3b6ad1b7', name: '萌神', slug: 'mengshen', description: '萌神手写体。OFL 1.1。', website: 'https://github.com/MaruTama/Mengshen-pinyin-font' },
  { id: '8b3d5f17-c49e-4268-90a1-6d9f4c7be2c8', name: 'Lingdong Huang', slug: 'lingdong', description: '齐伋体。OFL 1.1。', website: 'https://github.com/LingDong-/qiji-font' },
];
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  for (const b of brands) {
    const ex = await c.execute({ sql: 'select slug from brands where slug=?', args: [b.slug] });
    if (ex.rows.length) { console.log('skip', b.slug); continue; }
    await c.execute({
      sql: `insert into brands (id, name, slug, logo_url, banner_url, description, website, social_links, status, created_at, updated_at) values (?,?,?,?,?,?,?,?,?,?,?)`,
      args: [b.id, b.name, b.slug, '', '', b.description, b.website, null, 'published', now, now],
    });
    console.log('inserted', b.slug);
  }
})().catch((e) => { console.error(e); process.exit(1); });
