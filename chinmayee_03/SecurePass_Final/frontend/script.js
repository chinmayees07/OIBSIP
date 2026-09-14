const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];

let generated = Number(sessionStorage.getItem("vk_generated") || 0);
let history = [];
let lastPassword = "";
let apiBase = "";

const CHARSETS = {
  uppercase: "ABCDEFGHJKLMNPQRSTUVWXYZ",
  lowercase: "abcdefghijkmnopqrstuvwxyz",
  numbers: "23456789",
  symbols: "!@#$%^&*()-_=+[]{};:,.?/~"
};
const AMBIGUOUS = "0Ol1";
const WORDS = ["anchor","apricot","atlas","aurora","beacon","birch","canyon","cobalt","comet","copper","coral","crystal","delta","ember","falcon","forest","galaxy","harbor","hazel","island","jasmine","juniper","lantern","maple","meadow","meteor","mist","nebula","ocean","orbit","pebble","pine","planet","quartz","river","rocket","saffron","signal","silver","summit","thunder","timber","violet","willow","zenith"];

function toast(msg){const t=$("#toast");t.textContent=msg;t.classList.add("show");setTimeout(()=>t.classList.remove("show"),2200)}
function setView(view){
  $$(".view").forEach(v=>v.classList.toggle("active",v.id===view));
  $$(".nav-item").forEach(b=>b.classList.toggle("active",b.dataset.view===view));
  const titles={dashboard:"Overview",generator:"Password Studio",passphrase:"Passphrase",analyzer:"Security Analyzer",history:"Session History",settings:"Settings"};
  $("#pageTitle").textContent=titles[view]||"Overview";
  window.scrollTo({top:0,behavior:"smooth"});
}
$$(".nav-item").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.view)));
$$("[data-go]").forEach(b=>b.addEventListener("click",()=>setView(b.dataset.go)));

function updateStats(){
  $("#statGenerated").textContent=generated;
  $("#statHistory").textContent=`${history.length} / 5`;
  $("#statScore").textContent="100%";
}
function selectedTypes(){
  const a=[];
  if($("#upper").checked)a.push("uppercase");
  if($("#lower").checked)a.push("lowercase");
  if($("#numbers").checked)a.push("numbers");
  if($("#symbols").checked)a.push("symbols");
  return a;
}
function cleanCharset(s, exclude){
  let out=[...s].filter(c=>!exclude.includes(c)).join("");
  return out;
}
function localPassword(){
  const length=Number($("#length").value), types=selectedTypes();
  if(types.length<2) throw new Error("Select at least two character types.");
  const exclude=$("#exclude").value;
  let pools=types.map(t=>cleanCharset(CHARSETS[t], $("#ambiguous").checked?AMBIGUOUS:""));
  pools=pools.map(p=>cleanCharset(p,exclude));
  if(pools.some(p=>!p.length)) throw new Error("Your exclusions removed an entire character set.");
  let all=pools.join("");
  if($("#noRepeat").checked && new Set(all).size<length) throw new Error("Not enough unique characters for this length.");
  const arr=[];
  pools.forEach(p=>arr.push(p[Math.floor(Math.random()*p.length)]));
  while(arr.length<length){
    let c=all[Math.floor(Math.random()*all.length)];
    if($("#noRepeat").checked && arr.includes(c)) continue;
    arr.push(c);
  }
  for(let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]]}
  return arr.join("");
}
async function api(path, body){
  const res=await fetch(`${apiBase}${path}`,{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)
  });
  if(!res.ok) throw new Error(`Server returned ${res.status}`);
  const data=await res.json();
  if(data.error) throw new Error(data.error);
  return data;
}
async function generate(){
  try{
    const payload={length:Number($("#length").value),types:selectedTypes(),excludeAmbiguous:$("#ambiguous").checked,noRepeat:$("#noRepeat").checked,exclude:$("#exclude").value};
    let data;
    try{data=await api("/api/generate",payload); $("#engineBadge").textContent="PYTHON ENGINE"; $("#engineBadge").style.color="#15803d"; }
    catch(e){data={password:localPassword()};$("#engineBadge").textContent="LOCAL FALLBACK";$("#engineBadge").style.color="#315ee8"; toast("Python engine unavailable — local secure fallback used");}
    lastPassword=data.password;$("#passwordOutput").textContent=lastPassword;$("#resultTitle").textContent="Password generated";
    generated++;sessionStorage.setItem("vk_generated",generated);
    history.unshift({password:lastPassword,time:new Date().toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})});
    history=history.slice(0,5);renderHistory();updateStats();renderStrength(lastPassword);
    if($("#autoCopy").checked) await copyText(lastPassword);
  }catch(e){toast(e.message)}
}
function renderStrength(p){
  const len=p.length, types=[/[A-Z]/,/[a-z]/,/[0-9]/,/[^A-Za-z0-9]/].filter(r=>r.test(p)).length;
  let score=Math.min(100,Math.round((len>=16?55:len/16*55)+(types/4)*45));
  const level=score>=80?"Strong":score>=55?"Medium":"Weak";
  $("#strengthBar").style.width=score+"%";$("#strengthText").textContent=level;
  $("#ruleLength").textContent=len>=8?"✓":"!";
  $("#ruleTypes").textContent=types>=2?"✓":"!";
  $("#ruleUnique").textContent="✓";
}
async function copyText(text){
  try{await navigator.clipboard.writeText(text);toast("Copied to clipboard")}
  catch{toast("Clipboard permission was blocked by the browser")}
}
$("#copyBtn").addEventListener("click",()=>lastPassword&&copyText(lastPassword));
$("#generateBtn").addEventListener("click",generate);
$("#length").addEventListener("input",()=>$("#lengthValue").textContent=$("#length").value);

async function generatePhrase(){
  const n=Number($("#wordCount").value), sep=$("#separator").value;
  let phrase;
  try{const d=await api("/api/passphrase",{words:n,separator:sep});phrase=d.passphrase}
  catch{let a=[];for(let i=0;i<n;i++)a.push(WORDS[Math.floor(Math.random()*WORDS.length)]);phrase=a.join(sep)}
  $("#phraseOutput").textContent=phrase;$("#copyPhrase").onclick=()=>copyText(phrase);toast("Passphrase generated");
}
$("#wordCount").addEventListener("input",()=>$("#wordValue").textContent=$("#wordCount").value);
$("#passphraseBtn").addEventListener("click",generatePhrase);

function analyze(p){
  if(!p){$("#analyzeScore").textContent="0";$("#analyzeLevel").textContent="Waiting for input";$("#analyzeDetails").textContent="Enter a password and select Analyze.";return}
  const types=[/[A-Z]/,/[a-z]/,/[0-9]/,/[^A-Za-z0-9]/].filter(r=>r.test(p)).length;
  const common=["password","123456","qwerty","admin","letmein"].some(x=>p.toLowerCase().includes(x));
  let score=Math.min(100,Math.round((Math.min(p.length,32)/32)*55+(types/4)*45-(common?35:0)));
  score=Math.max(0,score);
  $("#analyzeScore").textContent=score;
  $("#analyzeLevel").textContent=score>=80?"Strong password":score>=55?"Moderate password":"Weak password";
  $("#analyzeDetails").textContent=`Length: ${p.length} • Character groups: ${types}/4${common?" • Avoid common patterns":""}`;
}
$("#analyzeBtn").addEventListener("click",()=>analyze($("#analyzeInput").value));
$("#analyzeInput").addEventListener("keydown",e=>{if(e.key==="Enter")analyze(e.target.value)});

function renderHistory(){
  const el=$("#historyList");
  if(!history.length){el.innerHTML='<div class="empty">No passwords generated in this session yet.</div>';updateStats();return}
  el.innerHTML=history.map((x,i)=>`<div class="history-item"><code>${escapeHtml(x.password)}</code><small>${x.time}</small><button data-copy="${i}">⧉</button></div>`).join("");
  $$("[data-copy]").forEach(b=>b.onclick=()=>copyText(history[Number(b.dataset.copy)].password));
  updateStats();
}
function escapeHtml(s){return s.replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]))}
$("#clearHistory").addEventListener("click",()=>{history=[];renderHistory();toast("Session history cleared")});

$("#themeBtn").addEventListener("click",()=>{document.body.classList.toggle("dark");localStorage.setItem("vk_theme",document.body.classList.contains("dark")?"dark":"light")});
$("#compact").addEventListener("change",e=>document.body.classList.toggle("compact",e.target.checked));
$("#autoCopy").checked=localStorage.getItem("vk_autocopy")==="1";
$("#autoCopy").addEventListener("change",e=>localStorage.setItem("vk_autocopy",e.target.checked?"1":"0"));

function setStatus(state,text){
  const el=$("#apiStatus");el.className=`status-pill ${state}`;el.querySelector("span").textContent=text;
}
async function checkBackend(){
  // The page is served by Flask in the normal setup, so use the same origin.
  // If opened directly from file://, the relative fetch will fail; fallback remains available.
  apiBase="";
  try{
    const res=await fetch("/api/health",{cache:"no-store"});
    if(!res.ok) throw new Error();
    setStatus("online","Security engine online");
  }catch{
    setStatus("offline","Local fallback active");
    $("#engineBadge").textContent="LOCAL FALLBACK";
  }
}
if(localStorage.getItem("vk_theme")==="dark")document.body.classList.add("dark");
$("#lengthValue").textContent=$("#length").value;
$("#wordValue").textContent=$("#wordCount").value;
updateStats();renderHistory();checkBackend();
document.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="g"){e.preventDefault();setView("generator");}});
