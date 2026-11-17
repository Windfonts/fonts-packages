const { createClient } = require('@libsql/client');
const tags = {
  'wenfeng-ummc': ['开源', 'Ume', 'upstream'],
  'wenfeng-mp12': ['开源', 'Mplus', 'upstream'],
  'wenfeng-wqys': ['开源', 'GPL-2.0', 'upstream'],
  'wenfeng-yozf': ['开源', 'OFL-1.1', 'upstream'],
};
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  for (const [fam, tag] of Object.entries(tags)) {
    const r = await c.execute({ sql: 'update fonts set tags=? where font_family=?', args: [JSON.stringify(tag), fam] });
    console.log(fam, r.rowsAffected);
  }
  const q = await c.execute("select id, font_family, name, status, license, license_type from fonts where font_family in ('wenfeng-ummc','wenfeng-yozf','wenfeng-mp12','wenfeng-wqys','wenfeng-hsmbzt')");
  console.log(JSON.stringify(q.rows));
})().catch((e) => { console.error(e); process.exit(1); });
