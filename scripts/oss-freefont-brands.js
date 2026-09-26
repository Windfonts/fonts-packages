const { createClient } = require('@libsql/client');
const brands = [
  { id: '7c1e9a20-4b6d-4e8a-9f31-2a8c5d0e11b4', name: 'Nanigashitei', slug: 'nanigashi', description: '何某手写体 NaniFont。OFL 1.1。', website: '' },
  { id: '3f8a2c61-9d14-4b70-a6e5-8c1d4f7b20aa', name: 'ItMarki', slug: 'itmarki', description: '芫茜雅楷。基于 Klee。OFL 1.1。', website: 'https://github.com/ItMarki/jyunsaikaai' },
  { id: '91b4e2d7-6c08-4a53-b1f9-5e7a3c8d64f0', name: 'Chun yu Yao', slug: 'chunyuyao', description: '马路口圆体。OFL 1.1。', website: '' },
  { id: 'b2d6f4a8-1e39-4c57-8a0b-6f3e9d1c75aa', name: 'yzdnn', slug: 'yzdnn', description: '长坂点宋。OFL 1.1。', website: 'https://github.com/yzdnn' },
  { id: '4e7c1b93-8a25-4d6f-b0c2-9a5f3e8d17c6', name: '香萃', slug: 'xiangcui', description: '香萃刻宋、等粗宋、自在。OFL 1.1。', website: '' },
  { id: '6a9d3f12-c4b8-4e70-9d15-2b7c8a0e43f1', name: 'LogoSC', slug: 'logosc', description: '龙珠体。OFL 1.1。标小智是注册商标。', website: '' },
  { id: '8c2e5b47-1d90-4f6a-a3c8-7e1b9d4f06aa', name: '余繁', slug: 'yufan', description: '余繁丹青宋、真素、细柳。OFL。', website: '' },
  { id: '5d1a8e36-7b42-4c09-8f6d-3a9c2e7b15d4', name: 'Unbounded Sans', slug: 'unbounded', description: '无界黑 Unbounded Sans。不是 Dela Gothic One。OFL 1.1。', website: '' },
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
