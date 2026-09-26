const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute(
    "select id, name, slug from brands where slug in ('founder','fangzheng','xiaomi','hanyi','aqua','xiangcui','lineseed','hanamin','cns11643')"
  );
  console.log(JSON.stringify(r.rows));
})().catch((e) => { console.error(e); process.exit(1); });
