const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  const off = await c.execute({
    sql: "update fonts set status='offline', updated_at=? where font_family='wenfeng-twqz'",
    args: [now],
  });
  console.log('offline twqz', off.rowsAffected);
  const rows = await c.execute(
    "select font_family, name, designer, foundry, brand_id from fonts where name like '演示%'"
  );
  console.log(JSON.stringify(rows.rows));
  const key = await c.execute({ sql: "select id from brands where slug='keynote'", args: [] });
  const kid = key.rows[0] && key.rows[0].id;
  console.log('keynote', kid);
  if (!kid) return;
  const upd = await c.execute({
    sql: "update fonts set brand_id=?, designer=?, foundry=?, updated_at=? where name like '演示%' and (brand_id<>? or foundry like '%花乐%' or foundry like '%FWHP%')",
    args: [kid, '人生哥', 'Keynote研究所', now, kid],
  });
  console.log('relink', upd.rowsAffected);
})().catch((e) => { console.error(e); process.exit(1); });
