const { createClient } = require('@libsql/client');
const brands = [
  {
    id: 'ea5649c7-1a95-4ab4-8151-04be4ddcc48e',
    name: 'Takushun Wu',
    slug: 'takushun',
    description: 'Takushun Wu。文津宋体、文渊宋黑圆。OFL 1.1。',
    website: 'https://github.com/takushun-wu',
  },
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
