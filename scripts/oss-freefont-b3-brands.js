const { createClient } = require('@libsql/client');
const brands = [
  { id: 'be607c4a-f7c1-459b-83d4-902c7f0e15fb', name: 'GlyphWiki', slug: 'hanamin', description: '花园明朝。可免费使用、修改、再分发。', website: 'http://glyphwiki.org/' },
  { id: 'cf718d5b-08d2-46ac-94e5-a13d801f26ac', name: '全字库', slug: 'cns11643', description: '台湾全字库正宋、正楷。开放政府数据授权 1.0。', website: 'https://data.gov.tw/license' },
  { id: 'd0829e6c-19e3-47bd-a5f6-b24e912037bd', name: 'LY Corporation', slug: 'lineseed', description: 'LINE Seed TW。字内写 OFL 1.1。', website: 'https://github.com/line/seed' },
];
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  for (const b of brands) {
    const ex = await c.execute({ sql: 'select id from brands where slug=?', args: [b.slug] });
    if (ex.rows.length) { console.log('skip', b.slug, ex.rows[0].id); continue; }
    await c.execute({
      sql: `insert into brands (id, name, slug, logo_url, banner_url, description, website, social_links, status, created_at, updated_at) values (?,?,?,?,?,?,?,?,?,?,?)`,
      args: [b.id, b.name, b.slug, '', '', b.description, b.website, null, 'published', now, now],
    });
    console.log('inserted', b.slug);
  }
})().catch((e) => { console.error(e); process.exit(1); });
