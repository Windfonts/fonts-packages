
const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  const ex = await c.execute({ sql: 'select slug from brands where slug=?', args: ['sarasa'] });
  if (ex.rows.length) { console.log('skip sarasa'); return; }
  await c.execute({
    sql: `insert into brands (id, name, slug, logo_url, banner_url, description, website, social_links, status, created_at, updated_at) values (?,?,?,?,?,?,?,?,?,?,?)`,
    args: ['e049d0d7-b424-4713-9667-38ba3c0784f5', '更纱', 'sarasa', '', '', '更纱黑体，Belleve Invis。SIL OFL 1.1。', 'https://github.com/be5invis/Sarasa-Gothic', null, 'published', now, now],
  });
  console.log('inserted sarasa');
})().catch((e) => { console.error(e); process.exit(1); });
