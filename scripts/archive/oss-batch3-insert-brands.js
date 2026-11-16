const { createClient } = require('@libsql/client');
const brands = [
  { id: '7f850511-3793-4f49-9a38-e3e478ea020e', name: '汇文', slug: 'huiwen', description: '汇文明朝修正版，CC0 1.0。', website: 'https://github.com/bosswnx/huiwenmincho-improved' },
  { id: '6d4facbf-0fb7-4140-b51a-c896ff537e6c', name: '中文网字计划', slug: 'guiwonder', description: 'GuiWonder 的开源字体。', website: 'https://github.com/GuiWonder' },
  { id: '92ea2979-bdf3-4189-b895-bb9a968c418b', name: '澳声通', slug: 'toneoz', description: '澳声通拼音文楷。SIL OFL 1.1。', website: 'https://github.com/jeffreyxuan/toneoz-font-pinyin-wenkai' },
];
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  for (const b of brands) {
    const ex = await c.execute({ sql: 'select slug from brands where slug=?', args: [b.slug] });
    if (ex.rows.length) { console.log('skip', b.slug); continue; }
    await c.execute({
      sql: `insert into brands (id, name, slug, logo_url, banner_url, description, website, social_links, status, created_at, updated_at)
            values (?,?,?,?,?,?,?,?,?,?,?)`,
      args: [b.id, b.name, b.slug, '', '', b.description, b.website, null, 'published', now, now],
    });
    console.log('inserted', b.slug);
  }
})().catch((e) => { console.error(e); process.exit(1); });
