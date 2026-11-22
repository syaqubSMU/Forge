// Signal Explorer: illustrative SAMPLE data only. Deadlines are generated relative to today so the demo always has future dates.
(function(){
var DAY=864e5, today=new Date(); today.setHours(0,0,0,0);
function d(n){return n===null?null:new Date(today.getTime()+n*DAY);}
var DATA=[
{id:"S-001",t:"Machine Learning for Rural Health Access",sp:"National Science Foundation",st:"open",dl:45,cat:"Computer & Information Sciences",syn:"Sample record: supports data-driven methods that improve access to care in rural communities."},
{id:"S-002",t:"Coastal Resilience Engineering Research",sp:"Department of Energy",st:"open",dl:20,cat:"Environmental & Earth Sciences",syn:"Sample record: research on infrastructure that withstands sea-level rise and storm surge."},
{id:"S-003",t:"Translational Neuroscience Pilot Awards",sp:"National Institutes of Health",st:"open",dl:90,cat:"Biological & Biomedical Sciences",syn:"Sample record: pilot funding for early-stage translational neuroscience projects."},
{id:"S-004",t:"STEM Teaching Innovation in Undergraduate Education",sp:"National Science Foundation",st:"forecasted",dl:null,cat:"Education",syn:"Sample record: forecasted opportunity; not yet open for applications."},
{id:"S-005",t:"Humanities Collections and Digital Access",sp:"National Endowment for the Humanities",st:"open",dl:60,cat:"Humanities & Arts",syn:"Sample record: digitization and public access for cultural collections."},
{id:"S-006",t:"Advanced Battery Materials Discovery",sp:"Department of Energy",st:"forecasted",dl:null,cat:"Physical Sciences & Engineering",syn:"Sample record: forecasted program in energy storage materials."},
{id:"S-007",t:"Community Health Data Science Initiative",sp:"National Institutes of Health",st:"open",dl:12,cat:"Health & Public Health",syn:"Sample record: public health analytics. Short window to test the lead-time filter."},
{id:"S-008",t:"Cross-Disciplinary Sensing and Society",sp:"National Science Foundation",st:"open",dl:120,cat:"Interdisciplinary / Cross-cutting",syn:"Sample record: sensing technologies studied alongside social and policy effects."}
].map(function(o){o.date=d(o.dl);return o;});
var KEY="forgeSignalSaved", saved=[];
try{saved=JSON.parse(localStorage.getItem(KEY)||"[]");}catch(e){}
function persist(){try{localStorage.setItem(KEY,JSON.stringify(saved));}catch(e){}}
var $=function(i){return document.getElementById(i);};
var q=$("q"),sp=$("sp"),stt=$("st"),lt=$("lt"),out=$("results"),chips=$("chips"),count=$("count"),view="discover";
var sponsors=[...new Set(DATA.map(function(o){return o.sp;}))].sort();
sponsors.forEach(function(s){var o=document.createElement("option");o.value=s;o.textContent=s;sp.appendChild(o);});
function fmt(dt){return dt?dt.toLocaleDateString(undefined,{year:"numeric",month:"short",day:"numeric"}):"Deadline not specified";}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});}
function filtered(){
 var term=q.value.trim().toLowerCase(),lead=parseInt(lt.value,10)||0;
 var list=DATA.filter(function(o){
  if(view==="saved")return saved.indexOf(o.id)>-1;
  if(sp.value&&o.sp!==sp.value)return false;
  if(stt.value&&o.st!==stt.value)return false;
  if(term&&(o.t+" "+o.sp+" "+o.id+" "+o.syn+" "+o.cat).toLowerCase().indexOf(term)<0)return false;
  if(lead>0&&o.date&&(o.date-today)/DAY<lead)return false;
  return true;});
 return list.sort(function(a,b){if(!a.date&&!b.date)return a.id<b.id?-1:1;if(!a.date)return 1;if(!b.date)return -1;return a.date-b.date;});
}
function chip(label,fn){var s=document.createElement("span");s.className="chip";s.textContent=label+" ";var b=document.createElement("button");b.type="button";b.setAttribute("aria-label","Remove filter "+label);b.textContent="×";b.onclick=fn;s.appendChild(b);chips.appendChild(s);}
function render(){
 chips.innerHTML="";
 if(view==="discover"){
  if(q.value.trim())chip("Search: "+q.value.trim(),function(){q.value="";render();});
  if(sp.value)chip(sp.value,function(){sp.value="";render();});
  if(stt.value)chip("Status: "+stt.options[stt.selectedIndex].text,function(){stt.value="";render();});
  if(parseInt(lt.value,10)>0)chip("Min. lead time: "+lt.value+" days",function(){lt.value="0";render();});
  if(chips.children.length>1){var c=document.createElement("button");c.type="button";c.className="tab";c.textContent="Clear all";c.onclick=function(){q.value="";sp.value="";stt.value="";lt.value="0";render();};chips.appendChild(c);}
 }
 var l=filtered();
 count.textContent=l.length+" "+(view==="saved"?"saved ":"")+"result"+(l.length===1?"":"s")+" · sorted by nearest deadline";
 if(!l.length){out.innerHTML='<p>'+(view==="saved"?"Nothing saved yet. Choose Save on any opportunity in Discover.":"No results. Try broadening your search or clearing a filter.")+"</p>";return;}
 out.innerHTML=l.map(function(o){var on=saved.indexOf(o.id)>-1;
  return '<article class="opp"><div><h3>'+esc(o.t)+'<span class="sample">SAMPLE</span></h3><p class="meta">'+esc(o.sp)+" · "+esc(o.id)+' · <span class="badge '+(o.st==="open"?"b-open":"b-fore")+'">'+(o.st==="open"?"Open / verify":"Forecasted")+"</span></p><p class=\"meta\"><strong>"+esc(fmt(o.date))+"</strong> · "+esc(o.cat)+"</p><p>"+esc(o.syn)+'</p></div><button class="save" type="button" aria-pressed="'+on+'" data-id="'+o.id+'">'+(on?"Saved ✓":"Save")+"</button></article>";}).join("");
}
out.addEventListener("click",function(e){var b=e.target.closest(".save");if(!b)return;var id=b.dataset.id,i=saved.indexOf(id);if(i>-1)saved.splice(i,1);else saved.push(id);persist();render();var nb=out.querySelector('[data-id="'+id+'"]');if(nb)nb.focus();$("savedN").textContent=saved.length;});
[q,sp,stt,lt].forEach(function(el){el.addEventListener("input",render);});
document.querySelectorAll(".tab[data-view]").forEach(function(t){t.addEventListener("click",function(){view=t.dataset.view;document.querySelectorAll(".tab[data-view]").forEach(function(x){x.setAttribute("aria-pressed",x===t);});$("filters").hidden=view==="saved";render();});});
$("savedN").textContent=saved.length;render();
})();
