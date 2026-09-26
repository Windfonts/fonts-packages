
const fs=require("fs");
const {createClient}=require("@libsql/client");
const fams=fs.readFileSync("/app/republish-families.txt","utf8").split(/\s+/).filter(Boolean);
(async()=>{
  const c=createClient({url:"file:/app/data/prod.db"});
  let n=0, miss=[];
  for (const f of fams){
    const r=await c.execute({sql:"update fonts set status=? where font_family=? and status='offline'", args:["published", f]});
    const ch=r.rowsAffected||0;
    if(!ch){
      const ex=await c.execute({sql:"select status from fonts where font_family=?", args:[f]});
      if(!ex.rows.length) miss.push(f);
    } else n+=ch;
  }
  console.log("republished", n, "missing", miss.length);
  if(miss.length) console.log(miss.join(" "));
})().catch(e=>{console.error(e); process.exit(1);});
