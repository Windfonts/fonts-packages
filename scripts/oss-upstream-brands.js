const { createClient } = require('@libsql/client');
const brands = [
  { id: '4d1f7549-3a73-4119-b9f3-5957d3b68a87', name: '佑字', slug: 'yuji', description: '佑字肃（Yuji Syuku）。SIL OFL 1.1。', website: 'https://github.com/Kinutafontfactory/Yuji' },
  { id: '62a25df6-6a89-4376-84c3-89c4139588e8', name: '梅字体', slug: 'ume', description: '梅ゴシック。可免费使用、修改、再分发，无保证。不是 OFL。', website: 'https://osdn.jp/projects/ume-font/' },
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
