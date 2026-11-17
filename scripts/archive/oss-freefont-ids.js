const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute(
    "select id, font_family, normalized_name, name from fonts where normalized_name in ('Hmsx','Yqyk','Kywa','Mlyu','Cbds','Xcks','Xcdc','Xczz','Lzti','Yydq','Yyzs','Yyxl','Ubss')"
  );
  console.log(JSON.stringify(r.rows));
})().catch((e) => { console.error(e); process.exit(1); });
