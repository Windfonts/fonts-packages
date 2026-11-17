
const { createClient } = require('@libsql/client');
const brands = [
  { id: '52815176-d72d-48ec-b489-7f243323de65', name: '斜月', slug: 'smiley-moon', description: '斜月体，得意黑加宽屏显版。SIL OFL 1.1。', website: 'https://github.com/onichan0923/smiley-moon' },
  { id: '81aa7111-c094-4934-8558-a5a0527a3ae1', name: 'Dela Gothic', slug: 'dela', description: 'Dela Gothic One，粗黑体。SIL OFL 1.1。', website: 'https://github.com/syakuzen/DelaGothic' },
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
