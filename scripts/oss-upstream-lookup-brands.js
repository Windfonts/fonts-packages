const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute("select id, slug, name from brands where slug in ('mplus','wenquanyi','ume','yoz','aoyagi-kouzan','yuji')");
  console.log(JSON.stringify(r.rows));
})().catch((e) => { console.error(e); process.exit(1); });
