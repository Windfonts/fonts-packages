
const { createClient } = require('@libsql/client');
const brands = [
  { id: '837baf65-61ec-483a-8c58-9670c14c0840', name: '汉典', slug: 'zdic', description: '汉典秦系文字体。CC0 1.0。', website: 'https://github.com/AlainAlan/zdic-qx-font' },
  { id: '4d22d1b8-8442-42c8-bb4f-a9288ab8c727', name: '激笔', slug: 'gekifude', description: '激笔 SFX。CC0 1.0。', website: 'https://github.com/ukr8b3g-cmyk/GEKIFUDE-SFX' },
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
