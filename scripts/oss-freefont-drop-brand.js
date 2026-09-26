const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const used = await c.execute({
    sql: 'select count(*) as n from fonts where brand_id=?',
    args: ['91b4e2d7-6c08-4a53-b1f9-5e7a3c8d64f0'],
  });
  const n = Number(used.rows[0].n);
  if (n) { console.log('kept, fonts', n); return; }
  const r = await c.execute({ sql: 'delete from brands where slug=?', args: ['chunyuyao'] });
  console.log('deleted', r.rowsAffected);
})().catch((e) => { console.error(e); process.exit(1); });
