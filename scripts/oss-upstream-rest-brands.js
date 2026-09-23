const { createClient } = require('@libsql/client');
const brands = [
  { id: '271649e6-fdcb-43e4-84bc-e02430f3cafb', name: 'Y.OzVox', slug: 'yoz', description: 'Y.OzFont。SIL OFL 1.1。', website: 'http://yozvox.web.fc2.com/' },
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
  const r = await c.execute({
    sql: `update fonts set name=?, chinese_name=?, english_name=?, license=?, description=? where font_family=?`,
    args: [
      '衡山毛笔',
      '衡山毛笔',
      'Kouzan Brush Font',
      '免费商用，没有限制',
      '衡山毛笔（KouzanBrushFont）。书法家青柳衡山写的免费毛笔字。站点写明可免费商用，商用没有限制，无保证。',
      'wenfeng-hsmbzt',
    ],
  });
  console.log('hsmb rows', r.rowsAffected);
})().catch((e) => { console.error(e); process.exit(1); });
