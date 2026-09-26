const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  const fams = ['wenfeng-dg16', 'wenfeng-trn1', 'wenfeng-rgg1', 'wenfeng-rmp1'];
  for (const f of fams) {
    const u = await c.execute({
      sql: "update fonts set status='offline', updated_at=? where font_family=?",
      args: [now, f],
    });
    console.log(f, u.rowsAffected);
  }
})().catch((e) => { console.error(e); process.exit(1); });
