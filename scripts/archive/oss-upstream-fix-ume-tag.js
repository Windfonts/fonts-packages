const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const r = await c.execute({
    sql: 'update fonts set tags=? where font_family=?',
    args: [JSON.stringify(['开源', 'Ume', 'upstream']), 'wenfeng-umgh'],
  });
  console.log('rows', r.rowsAffected);
})().catch((e) => { console.error(e); process.exit(1); });
