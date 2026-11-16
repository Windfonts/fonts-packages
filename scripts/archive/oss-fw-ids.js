const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute(
    "select id, font_family, normalized_name, name from fonts where normalized_name in ('Dg16','Trn1','Rgg1','Rmp1')"
  );
  console.log(JSON.stringify(r.rows));
})().catch((e) => { console.error(e); process.exit(1); });
