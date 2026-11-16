const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute(
    "select id, font_family, normalized_name, name, foundry, license from fonts where normalized_name in ('Xstq','Yiny','Hyzi','Qsst','Qssb','Qkhm','Qkhc','Jpdz','Mjdz','Mjdm','Mshx','Yyxy','Qiji')"
  );
  console.log(JSON.stringify(r.rows));
  const now = Math.floor(Date.now() / 1000);
  for (const fam of ['wenfeng-jpdz', 'wenfeng-yyxy']) {
    const u = await c.execute({
      sql: 'update fonts set tags=?, updated_at=? where font_family=?',
      args: ['["开源"]', now, fam],
    });
    console.log('tags', fam, u.rowsAffected);
  }
  const f = await c.execute({
    sql: "update fonts set foundry=? where font_family=? and foundry=?",
    args: ['澳声通', 'wenfeng-xstq', 'ToneOZ'],
  });
  console.log('foundry', f.rowsAffected);
})().catch((e) => { console.error(e); process.exit(1); });
