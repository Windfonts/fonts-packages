const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute(
    "select id, font_family, normalized_name, name from fonts where normalized_name in ('Fzss','Fzfs','Fzkt','Fzht','Misn','Hyma','Hymb','Qzss','Qzkt','Lnsw','Mdmz','Xcdz','Xccx','Xcld')"
  );
  console.log(JSON.stringify(r.rows));
  const now = Math.floor(Date.now() / 1000);
  const oflOk = new Set(['wenfeng-lnsw', 'wenfeng-mdmz']);
  for (const row of r.rows) {
    if (oflOk.has(row.font_family)) continue;
    const u = await c.execute({
      sql: 'update fonts set tags=?, updated_at=? where font_family=?',
      args: ['["开源"]', now, row.font_family],
    });
    console.log('tags', row.font_family, u.rowsAffected);
  }
})().catch((e) => { console.error(e); process.exit(1); });
