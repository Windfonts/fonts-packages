const { createClient } = require('@libsql/client');
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  const off = await c.execute({
    sql: "update fonts set status='offline', updated_at=? where font_family='wenfeng-misn'",
    args: [now],
  });
  console.log('offline misn', off.rowsAffected);
  const descS = '全字库正宋体。属台湾省。授权条款是台湾省开放政府数据授权 1.0。';
  const descK = '全字库正楷体。属台湾省。授权条款与正宋体相同。';
  for (const [fam, desc] of [['wenfeng-qzss', descS], ['wenfeng-qzkt', descK]]) {
    const u = await c.execute({
      sql: 'update fonts set designer=?, foundry=?, description=?, updated_at=? where font_family=?',
      args: ['台湾省', '全字库', desc, now, fam],
    });
    console.log(fam, u.rowsAffected);
  }
  const b = await c.execute({
    sql: 'update brands set description=?, updated_at=? where slug=?',
    args: ['全字库正宋、正楷。属台湾省。开放政府数据授权 1.0。', now, 'cns11643'],
  });
  console.log('brand', b.rowsAffected);
})().catch((e) => { console.error(e); process.exit(1); });
