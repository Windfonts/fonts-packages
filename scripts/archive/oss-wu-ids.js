const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute(
    "select id, font_family, normalized_name, name, status from fonts where normalized_name in ('Wjmp','Wjm2','Wysf','Wyhk','Wyyt')"
  );
  console.log(JSON.stringify(r.rows));
})().catch((e) => { console.error(e); process.exit(1); });
