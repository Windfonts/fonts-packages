const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute({ sql: "select id, name, slug from brands where slug='fontworks'", args: [] });
  console.log(JSON.stringify(r.rows));
})().catch((e) => { console.error(e); process.exit(1); });
