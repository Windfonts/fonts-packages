const { createClient } = require('@libsql/client');
const rows = [
  ["wenfeng-wjmp", "Copyright (c) 2024-2026, Takushun Wu, with Reserved Font Name 'WenJin Mincho' / '文津宋体'."],
  ["wenfeng-wjm2", "Copyright (c) 2024-2026, Takushun Wu, with Reserved Font Name 'WenJin Mincho' / '文津宋体'."],
  ["wenfeng-wysf", "Copyright (c) 2024-2026, Takushun Wu, with Reserved Font Name 'WenYuan Serif' / '文渊宋体'."],
  ["wenfeng-wyhk", "Copyright (c) 2024-2026, Takushun Wu, with Reserved Font Name 'WenYuan Sans' / '文渊黑体'."],
  ["wenfeng-wyyt", "Copyright (c) 2024-2026, Takushun Wu, with Reserved Font Name 'WenYuan Rounded' / '文源圆体'."],
];
(async () => {
  const c = createClient({ url: 'file:/app/data/prod.db' });
  const now = Math.floor(Date.now() / 1000);
  for (const [family, copyright] of rows) {
    const r = await c.execute({
      sql: 'update fonts set copyright=?, updated_at=? where font_family=?',
      args: [copyright, now, family],
    });
    console.log(family, r.rowsAffected);
  }
})().catch((e) => { console.error(e); process.exit(1); });
