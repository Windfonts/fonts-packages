const { createClient } = require('@libsql/client');
const fams = [
  'wenfeng-xwbrightcodegb', 'wenfeng-xwbrightcodetc',
  'wenfeng-xwbrightgb', 'wenfeng-xwbrighttc',
  'wenfeng-xwwkkr', 'wenfeng-xwwklite', 'wenfeng-xwwkgblite',
  'wenfeng-xwwkscreen', 'wenfeng-xwwkgbscreen', 'wenfeng-xwwkgbfusion',
  'wenfeng-xwwkmonolite', 'wenfeng-xwwkgbmonolite', 'wenfeng-xwwkmonoscreen',
  'wenfeng-xwwkmonogbscreen', 'wenfeng-xwwkgbmonofusion', 'wenfeng-xwwkmonokr',
];
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  let n = 0;
  const miss = [];
  for (const f of fams) {
    const r = await c.execute({
      sql: "update fonts set status=? where font_family=? and status!='offline'",
      args: ['offline', f],
    });
    const ch = r.rowsAffected || 0;
    if (!ch) {
      const ex = await c.execute({ sql: 'select status from fonts where font_family=?', args: [f] });
      if (!ex.rows.length) miss.push(f);
      else console.log('already', f, ex.rows[0].status);
    } else n += ch;
  }
  console.log(JSON.stringify({ updated: n, missing: miss }));
})().catch((e) => { console.error(e); process.exit(1); });
