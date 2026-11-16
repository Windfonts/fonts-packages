
const fs=require("fs");
const {createClient}=require("@libsql/client");
const fams=fs.readFileSync("/app/license-note-comm.txt","utf8").split(/\s+/).filter(Boolean);
const name="免费商用，不可修改";
const note="可免费商用。不可修改字体文件，不可再分发。";
(async()=>{
  const c=createClient({url:"file:/app/data/prod.db"});
  for (const f of fams){
    const r=await c.execute({
      sql:"update fonts set license=?, license_type=?, license_description=? where font_family=?",
      args:[name, name, note, f]
    });
    console.log(f, r.rowsAffected||0);
  }
})().catch(e=>{console.error(e); process.exit(1);});
