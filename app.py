from flask import Flask, request, jsonify, render_template_string
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    host = os.environ.get("DB_HOST", "postgress-0.postgress.database.svc.cluster.local")
    dbname = os.environ.get("DB_NAME") or os.environ.get("POSTGRES_DB", "mydb")
    user = os.environ.get("DB_USER") or os.environ.get("POSTGRES_USER", "admin")
    password = os.environ.get("DB_PASSWORD") or os.environ.get("POSTGRES_PASSWORD", "")
    return psycopg2.connect(host=host, database=dbname, user=user, password=password)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>UserVault — AKS</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#020817;--surface:rgba(15,23,42,0.9);--border:rgba(99,179,237,0.15);--border-bright:rgba(99,179,237,0.4);--accent:#38bdf8;--accent2:#818cf8;--accent3:#34d399;--danger:#f87171;--text:#e2e8f0;--muted:#64748b}
body{font-family:'Syne',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden}
.bg-grid{position:fixed;inset:0;z-index:0;background-image:linear-gradient(rgba(56,189,248,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(56,189,248,.03) 1px,transparent 1px);background-size:60px 60px}
.orb{position:fixed;border-radius:50%;filter:blur(80px);opacity:.1;z-index:0}
.o1{width:500px;height:500px;background:#38bdf8;top:-100px;left:-100px}
.o2{width:400px;height:400px;background:#818cf8;bottom:-100px;right:-50px}
.o3{width:300px;height:300px;background:#34d399;top:40%;left:45%}
.wrap{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 24px 80px}
header{padding:40px 0 36px}
.badge{display:inline-flex;align-items:center;gap:7px;background:rgba(56,189,248,.08);border:1px solid var(--border-bright);border-radius:100px;padding:5px 14px;font-family:'Space Mono',monospace;font-size:10px;color:var(--accent);letter-spacing:.08em;margin-bottom:18px}
.dot{width:6px;height:6px;border-radius:50%;background:var(--accent3);box-shadow:0 0 8px var(--accent3);animation:pulse 2s ease infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
h1{font-size:clamp(2rem,5vw,3.8rem);font-weight:800;letter-spacing:-.03em;background:linear-gradient(135deg,#e2e8f0,#38bdf8 50%,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.05;margin-bottom:10px}
.sub{font-size:.9rem;color:var(--muted);line-height:1.6;max-width:500px}
.sub b{color:var(--accent)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:28px}
.sc{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:16px 18px;backdrop-filter:blur(20px);transition:border-color .3s,transform .3s}
.sc:hover{border-color:var(--border-bright);transform:translateY(-2px)}
.sl{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;margin-bottom:5px}
.sv{font-size:1.7rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sv.g{background:linear-gradient(135deg,var(--accent3),#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sv.p{background:linear-gradient(135deg,var(--accent2),#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sv.r{background:linear-gradient(135deg,#f87171,#fb923c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.grid{display:grid;grid-template-columns:1fr 340px;gap:18px;align-items:start}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:18px;backdrop-filter:blur(20px);overflow:hidden}
.ph{padding:14px 22px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;background:rgba(15,23,42,.5)}
.pt{font-size:.78rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;display:flex;align-items:center;gap:8px}
.ic{width:24px;height:24px;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:12px}
.ib{background:rgba(56,189,248,.12)}.ip{background:rgba(129,140,248,.12)}.ir{background:rgba(248,113,113,.12)}
.pb{padding:16px 22px}
.toolbar{display:flex;gap:8px;margin-bottom:12px}
.srch{flex:1;display:flex;align-items:center;gap:7px;background:rgba(15,23,42,.8);border:1px solid var(--border);border-radius:9px;padding:8px 12px;transition:border-color .2s}
.srch:focus-within{border-color:var(--accent)}
.srch input{background:none;border:none;outline:none;color:var(--text);font-family:'Syne',sans-serif;font-size:.83rem;flex:1}
.srch input::placeholder{color:var(--muted)}
.srt{background:rgba(15,23,42,.8);border:1px solid var(--border);border-radius:9px;padding:8px 10px;color:var(--text);font-family:'Space Mono',monospace;font-size:9px;outline:none;cursor:pointer}
.srt option{background:#0f172a}
table{width:100%;border-collapse:collapse}
th{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:8px 10px;text-align:left;border-bottom:1px solid var(--border);cursor:pointer}
th:hover{color:var(--accent)}
tbody tr{border-bottom:1px solid rgba(99,179,237,.04);transition:background .15s}
tbody tr:hover{background:rgba(56,189,248,.04)}
td{padding:11px 10px;font-size:.83rem}
.idb{font-family:'Space Mono',monospace;font-size:10px;background:rgba(56,189,248,.1);border:1px solid rgba(56,189,248,.2);color:var(--accent);padding:2px 6px;border-radius:5px}
.av{width:28px;height:28px;border-radius:8px;display:inline-flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;color:#fff;margin-right:8px;flex-shrink:0}
.nc{display:flex;align-items:center}
.em{font-family:'Space Mono',monospace;font-size:10px;color:var(--muted)}
.db{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.2);color:var(--danger);border-radius:6px;padding:3px 9px;font-family:'Space Mono',monospace;font-size:9px;cursor:pointer;transition:all .2s}
.db:hover{background:rgba(248,113,113,.18)}
.pg{display:flex;align-items:center;justify-content:space-between;margin-top:12px;padding-top:12px;border-top:1px solid var(--border)}
.pi{font-family:'Space Mono',monospace;font-size:9px;color:var(--muted)}
.pbs{display:flex;gap:5px}
.pb2{background:rgba(56,189,248,.08);border:1px solid var(--border);color:var(--accent);border-radius:6px;padding:4px 10px;font-family:'Space Mono',monospace;font-size:9px;cursor:pointer;transition:all .2s}
.pb2:hover{background:rgba(56,189,248,.15)}
.pb2:disabled{opacity:.3;cursor:not-allowed}
.pb2.ac{background:rgba(56,189,248,.2);border-color:var(--border-bright)}
.fl{font-family:'Space Mono',monospace;font-size:9px;letter-spacing:.1em;color:var(--muted);text-transform:uppercase;display:block;margin-bottom:6px}
.fi{width:100%;background:rgba(15,23,42,.8);border:1px solid var(--border);border-radius:9px;padding:10px 13px;color:var(--text);font-family:'Syne',sans-serif;font-size:.85rem;outline:none;transition:border-color .2s,box-shadow .2s;margin-bottom:12px}
.fi::placeholder{color:var(--muted)}
.fi:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(56,189,248,.07)}
.btn{width:100%;padding:11px;border:none;border-radius:9px;font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;cursor:pointer;transition:all .2s}
.btn-p{background:linear-gradient(135deg,#0ea5e9,#6366f1);color:#fff;box-shadow:0 4px 14px rgba(14,165,233,.2)}
.btn-p:hover{transform:translateY(-1px);box-shadow:0 7px 20px rgba(14,165,233,.35)}
.btn-p:disabled{opacity:.5;cursor:not-allowed;transform:none}
.btn-d{background:linear-gradient(135deg,#ef4444,#dc2626);color:#fff;margin-top:8px;box-shadow:0 4px 14px rgba(239,68,68,.15)}
.btn-d:hover{transform:translateY(-1px)}
.sp{display:inline-block;width:12px;height:12px;border:2px solid rgba(56,189,248,.2);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.toast{position:fixed;bottom:22px;right:22px;z-index:999;padding:11px 16px;border-radius:11px;font-size:.8rem;font-weight:600;display:flex;align-items:center;gap:7px;transform:translateY(70px);opacity:0;transition:all .4s cubic-bezier(.34,1.56,.64,1);backdrop-filter:blur(20px);border:1px solid;max-width:280px}
.toast.show{transform:translateY(0);opacity:1}
.toast.ok{background:rgba(52,211,153,.1);border-color:rgba(52,211,153,.3);color:var(--accent3)}
.toast.err{background:rgba(248,113,113,.1);border-color:rgba(248,113,113,.3);color:var(--danger)}
.ov{position:fixed;inset:0;background:rgba(2,8,23,.85);z-index:100;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(8px);opacity:0;pointer-events:none;transition:opacity .3s}
.ov.show{opacity:1;pointer-events:all}
.md{background:#0f172a;border:1px solid var(--border-bright);border-radius:18px;padding:26px;width:100%;max-width:380px;transform:scale(.95);transition:transform .3s}
.ov.show .md{transform:scale(1)}
.mt{font-size:.95rem;font-weight:700;margin-bottom:14px;display:flex;align-items:center;gap:8px}
.ma{display:flex;gap:8px;margin-top:14px}
.ma .btn{width:auto;flex:1;padding:9px}
.es{text-align:center;padding:36px 0;color:var(--muted)}
.rb{background:rgba(56,189,248,.08);border:1px solid var(--border);color:var(--accent);border-radius:7px;padding:5px 11px;font-family:'Space Mono',monospace;font-size:9px;cursor:pointer;transition:all .2s;letter-spacing:.04em}
.rb:hover{background:rgba(56,189,248,.15)}
.chip{padding:3px 9px;border-radius:100px;font-family:'Space Mono',monospace;font-size:9px;border:1px solid}
.cb{background:rgba(56,189,248,.07);border-color:rgba(56,189,248,.2);color:var(--accent)}
.cp{background:rgba(129,140,248,.07);border-color:rgba(129,140,248,.2);color:var(--accent2)}
.cg{background:rgba(52,211,153,.07);border-color:rgba(52,211,153,.2);color:var(--accent3)}
.dberr{background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.2);border-radius:10px;padding:20px;text-align:center;font-family:'Space Mono',monospace;font-size:.78rem;color:var(--danger);line-height:1.8}
</style>
</head>
<body>
<div class="bg-grid"></div>
<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>
<div class="wrap">
  <header>
    <div class="badge"><span class="dot"></span>LIVE · AKS · CENTRAL INDIA</div>
    <h1>UserVault</h1>
    <p class="sub">Cloud-native user management on <b>Azure Kubernetes Service</b> — Key Vault secrets, PostgreSQL StatefulSet, zero hardcoded credentials.</p>
  </header>

  <div class="stats">
    <div class="sc"><div class="sl">Total Users</div><div class="sv" id="sTot">—</div></div>
    <div class="sc"><div class="sl">Filtered</div><div class="sv p" id="sFil">—</div></div>
    <div class="sc"><div class="sl">API Status</div><div class="sv g" id="sApi">ONLINE</div></div>
    <div class="sc"><div class="sl">DB Pods</div><div class="sv r">3 / 3</div></div>
  </div>

  <div class="grid">
    <!-- TABLE -->
    <div class="panel">
      <div class="ph">
        <div class="pt"><span class="ic ib">👥</span>User Registry</div>
        <button class="rb" onclick="load()" id="rbtn">↻ REFRESH</button>
      </div>
      <div class="pb">
        <div class="toolbar">
          <div class="srch">
            <span style="color:var(--muted);font-size:13px">⌕</span>
            <input type="text" id="q" placeholder="Search name or email…" oninput="search()"/>
          </div>
          <select class="srt" id="srt" onchange="render()">
            <option value="id-asc">ID ↑</option>
            <option value="id-desc">ID ↓</option>
            <option value="name-asc">Name A–Z</option>
            <option value="name-desc">Name Z–A</option>
          </select>
        </div>
        <table>
          <thead><tr>
            <th onclick="sort('id')">ID</th>
            <th onclick="sort('name')">Name</th>
            <th onclick="sort('email')">Email</th>
            <th>Del</th>
          </tr></thead>
          <tbody id="tb"><tr><td colspan="4"><div class="es"><span class="sp"></span></div></td></tr></tbody>
        </table>
        <div class="pg">
          <span class="pi" id="pi">—</span>
          <div class="pbs" id="pbs"></div>
        </div>
      </div>
    </div>

    <!-- SIDEBAR -->
    <div style="display:flex;flex-direction:column;gap:14px">
      <!-- ADD USER -->
      <div class="panel">
        <div class="ph"><div class="pt"><span class="ic ip">✦</span>Add User</div></div>
        <div class="pb">
          <label class="fl">Full Name</label>
          <input class="fi" type="text" id="nm" placeholder="e.g. Afiza Bee"/>
          <label class="fl">Email</label>
          <input class="fi" type="email" id="em" placeholder="e.g. afiza@afizabee.online"/>
          <button class="btn btn-p" onclick="create()" id="cbtn">Create User</button>
        </div>
      </div>

      <!-- BULK -->
      <div class="panel">
        <div class="ph"><div class="pt"><span class="ic ir">⚡</span>Bulk Actions</div></div>
        <div class="pb">
          <p style="font-size:.78rem;color:var(--muted);margin-bottom:10px;line-height:1.5">Generate random test users or clear all data.</p>
          <button class="btn btn-p" onclick="bulk()" id="bbtn">Generate 20 Random Users</button>
          <button class="btn btn-d" onclick="clearAll()">Clear All Users</button>
        </div>
      </div>

      <!-- STACK -->
      <div class="panel">
        <div class="ph"><div class="pt"><span class="ic ib">⬡</span>Tech Stack</div></div>
        <div class="pb" style="display:flex;gap:6px;flex-wrap:wrap">
          <span class="chip cb">AKS</span>
          <span class="chip cb">App Gateway</span>
          <span class="chip cp">PostgreSQL</span>
          <span class="chip cp">Workload Identity</span>
          <span class="chip cg">Key Vault CSI</span>
          <span class="chip cg">Flask</span>
          <span class="chip cb">AGIC</span>
          <span class="chip cp">managed-csi</span>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- MODALS -->
<div class="ov" id="dMod">
  <div class="md">
    <div class="mt"><span class="ic ir">🗑</span>Delete User</div>
    <p style="font-size:.85rem;color:var(--muted);line-height:1.6">Delete <b id="dName" style="color:var(--text)"></b>? Cannot be undone.</p>
    <div class="ma">
      <button class="btn" style="background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--muted)" onclick="hideDel()">Cancel</button>
      <button class="btn btn-d" onclick="doDel()" id="dBtn">Delete</button>
    </div>
  </div>
</div>
<div class="ov" id="cMod">
  <div class="md">
    <div class="mt"><span class="ic ir">⚠</span>Clear All</div>
    <p style="font-size:.85rem;color:var(--muted);line-height:1.6">Permanently delete <b id="cCnt" style="color:var(--danger)"></b> users?</p>
    <div class="ma">
      <button class="btn" style="background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--muted)" onclick="hideClear()">Cancel</button>
      <button class="btn btn-d" onclick="doClear()">Delete All</button>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
const CLR=['linear-gradient(135deg,#38bdf8,#6366f1)','linear-gradient(135deg,#34d399,#0ea5e9)','linear-gradient(135deg,#818cf8,#c084fc)','linear-gradient(135deg,#f472b6,#818cf8)','linear-gradient(135deg,#fb923c,#f43f5e)','linear-gradient(135deg,#a3e635,#06b6d4)','linear-gradient(135deg,#f59e0b,#ef4444)'];
const FN=['James Wilson','Emma Thompson','Noah Garcia','Olivia Martinez','Liam Anderson','Sophia Taylor','Mason Lee','Isabella White','Ethan Harris','Ava Clark','Lucas Lewis','Mia Robinson','Charlotte Hall','Benjamin Young','Amelia King','Logan Wright','Harper Scott','Evelyn Baker','Sofia Campbell','Victoria Evans','Afiza Bee','Zara Khan','Ali Mohammed','Sara Rizvi','Omar Sheikh','Nadia Hassan','Fatima Zahra','Hassan Ali','Bilal Ahmed','Mariam Yusuf'];
const DOM=['gmail.com','outlook.com','yahoo.com','hotmail.com','icloud.com','proton.me'];
let all=[],fil=[],pg=1,pp=10,did=null;
const gi=n=>n.split(' ').map(x=>x[0]).join('').toUpperCase().slice(0,2);
const rnd=a=>a[Math.floor(Math.random()*a.length)];
function toast(m,t='ok'){const el=document.getElementById('toast');el.textContent=(t==='ok'?'✓ ':'✕ ')+m;el.className='toast '+t+' show';setTimeout(()=>el.classList.remove('show'),3200)}
function sort(c){const s=document.getElementById('srt');s.value=s.value===c+'-asc'?c+'-desc':c+'-asc';render()}
function search(){pg=1;render()}
function sorted(a){
  const[c,d]=document.getElementById('srt').value.split('-');
  return[...a].sort((x,y)=>{let a=c==='id'?x.id:x[c].toLowerCase(),b=c==='id'?y.id:y[c].toLowerCase();return d==='asc'?(a>b?1:-1):(a<b?1:-1)});
}
function render(){
  const q=document.getElementById('q').value.toLowerCase();
  fil=q?all.filter(u=>u.name.toLowerCase().includes(q)||u.email.toLowerCase().includes(q)):all;
  const s=sorted(fil),tp=Math.max(1,Math.ceil(s.length/pp));
  if(pg>tp)pg=tp;
  const st=(pg-1)*pp,sl=s.slice(st,st+pp);
  document.getElementById('sTot').textContent=all.length;
  document.getElementById('sFil').textContent=fil.length;
  document.getElementById('pi').textContent='Page '+pg+' of '+tp+' · '+fil.length+' results';
  const tb=document.getElementById('tb');
  if(!sl.length){tb.innerHTML='<tr><td colspan="4"><div class="es">🌌<br/><small>No users found</small></div></td></tr>';
  }else{
    tb.innerHTML=sl.map((u,i)=>'<tr style="animation:none"><td><span class="idb">#'+String(u.id).padStart(3,'0')+'</span></td><td><div class="nc"><div class="av" style="background:'+CLR[u.id%CLR.length]+'">'+gi(u.name)+'</div>'+u.name+'</div></td><td><span class="em">'+u.email+'</span></td><td><button class="db" onclick="showDel('+u.id+',\''+u.name.replace(/'/g,"\\'")+'\')">\u2715</button></td></tr>').join('');
  }
  const pb=document.getElementById('pbs');
  let h='<button class="pb2" onclick="gp('+(pg-1)+')" '+(pg<=1?'disabled':'')+'>‹</button>';
  const s2=Math.max(1,pg-2),e=Math.min(tp,s2+4);
  for(let p=s2;p<=e;p++)h+='<button class="pb2 '+(p===pg?'ac':'')+'" onclick="gp('+p+')">'+p+'</button>';
  h+='<button class="pb2" onclick="gp('+(pg+1)+')" '+(pg>=tp?'disabled':'')+'>›</button>';
  pb.innerHTML=h;
}
function gp(p){pg=p;render()}
async function load(){
  const btn=document.getElementById('rbtn');
  btn.innerHTML='<span class="sp"></span>';btn.disabled=true;
  try{
    const r=await fetch('/users');
    const d=await r.json();
    if(!r.ok)throw new Error(d.error||'HTTP '+r.status);
    all=d;pg=1;render();
    document.getElementById('sApi').textContent='ONLINE';
  }catch(e){
    document.getElementById('sApi').textContent='ERROR';
    document.getElementById('tb').innerHTML='<tr><td colspan="4"><div class="dberr">DB Error: '+e.message+'</div></td></tr>';
    toast(e.message,'err');
  }finally{btn.innerHTML='↻ REFRESH';btn.disabled=false}
}
async function create(){
  const n=document.getElementById('nm').value.trim(),e=document.getElementById('em').value.trim();
  if(!n||!e){toast('Name and email required','err');return}
  if(!e.includes('@')){toast('Invalid email','err');return}
  const btn=document.getElementById('cbtn');
  btn.disabled=true;btn.innerHTML='<span class="sp"></span> Creating…';
  try{
    const r=await fetch('/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,email:e})});
    const d=await r.json();
    if(!r.ok)throw new Error(d.error||'Failed');
    document.getElementById('nm').value='';document.getElementById('em').value='';
    toast(n+' added!');await load();
  }catch(e){toast(e.message,'err')}
  finally{btn.disabled=false;btn.innerHTML='Create User'}
}
async function bulk(){
  const btn=document.getElementById('bbtn');
  btn.disabled=true;btn.innerHTML='<span class="sp"></span> Generating…';
  let ok=0;
  for(let i=0;i<20;i++){
    const n=rnd(FN),e=n.toLowerCase().replace(/ /g,'.')+'.'+Math.floor(Math.random()*9999)+'@'+rnd(DOM);
    try{const r=await fetch('/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,email:e})});if(r.ok)ok++}catch(e){}
  }
  toast(ok+' users generated!');await load();
  btn.disabled=false;btn.innerHTML='Generate 20 Random Users';
}
function showDel(id,name){did=id;document.getElementById('dName').textContent=name;document.getElementById('dMod').classList.add('show')}
function hideDel(){document.getElementById('dMod').classList.remove('show');did=null}
async function doDel(){
  const btn=document.getElementById('dBtn');btn.disabled=true;btn.innerHTML='<span class="sp"></span>';
  try{const r=await fetch('/users/'+did,{method:'DELETE'});if(!r.ok)throw new Error();toast('Deleted');hideDel();await load()}
  catch(e){toast('Delete failed','err')}
  finally{btn.disabled=false;btn.innerHTML='Delete'}
}
function clearAll(){document.getElementById('cCnt').textContent=all.length;document.getElementById('cMod').classList.add('show')}
function hideClear(){document.getElementById('cMod').classList.remove('show')}
async function doClear(){
  try{const r=await fetch('/users/all',{method:'DELETE'});if(!r.ok)throw new Error();toast('Cleared');hideClear();await load()}
  catch(e){toast('Failed','err')}
}
document.addEventListener('keydown',e=>{if(e.key==='Enter'&&['nm','em'].includes(document.activeElement.id))create();if(e.key==='Escape'){hideDel();hideClear()}});
document.getElementById('dMod').addEventListener('click',e=>{if(e.target===e.currentTarget)hideDel()});
document.getElementById('cMod').addEventListener('click',e=>{if(e.target===e.currentTarget)hideClear()});
load();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return jsonify({"status": "healthy", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "db": str(e)}), 500


@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users ORDER BY id;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([{"id": r[0], "name": r[1], "email": r[2]} for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("email"):
        return jsonify({"error": "Name and email required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;",
            (data["name"], data["email"])
        )
        new_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"id": new_id, "message": "User created"}), 201
    except psycopg2.errors.UniqueViolation:
        return jsonify({"error": "Email already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if not deleted:
            return jsonify({"error": "Not found"}), 404
        return jsonify({"message": "Deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/users/all", methods=["DELETE"])
def delete_all():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users;")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "All deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)