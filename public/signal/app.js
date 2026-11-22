(function(){
var $=function(i){return document.getElementById(i);};
var KEY="signalWorkbenchV1";
var SAMPLE={profiles:[
 {id:"p1",name:"Sample PI A (fictional)",dept:"Sample Biology",url:"",status:"Verified",ret:"2026-11-01",areas:["Machine learning methods for rural health access","Community health data analysis"]},
 {id:"p2",name:"Sample PI B (fictional)",dept:"Sample History",url:"",status:"Unverified",ret:"2026-06-01",areas:["Digitization of archival collections","Public access to cultural heritage"]},
 {id:"p3",name:"Sample PI C (fictional)",dept:"Sample Physics",url:"",status:"Verified",ret:"2026-10-15",areas:["Battery materials discovery","Energy storage characterization"]}],
 opps:[
 {id:"o1",title:"Sample: ML for Rural Health Access",sponsor:"Sample Sponsor",url:"",dl:"",elig:"Unclear",notes:"Fictional record",pri:["Data-driven methods that improve access to care in rural communities (Sec. I)"]},
 {id:"o2",title:"Sample: Humanities Collections and Digital Access",sponsor:"Sample Sponsor",url:"",dl:"",elig:"Clear",notes:"Fictional record",pri:["Digitization and public access for cultural collections (Sec. I)"]}]};
var S=load();
function load(){try{var s=JSON.parse(localStorage.getItem(KEY));if(s&&s.profiles&&s.opps)return s;}catch(e){}return JSON.parse(JSON.stringify(SAMPLE));}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S));}catch(e){}}
function uid(){return "x"+Date.now().toString(36)+Math.random().toString(36).slice(2,6);}
function h(tag,attrs,kids){var e=document.createElement(tag);for(var k in (attrs||{}))e.setAttribute(k,attrs[k]);(kids||[]).forEach(function(c){e.appendChild(typeof c==="string"?document.createTextNode(c):c);});return e;}
function clear(n){while(n.firstChild)n.removeChild(n.firstChild);}
function fmt(d){return d?new Date(d+"T00:00:00").toLocaleDateString(undefined,{year:"numeric",month:"short",day:"numeric"}):"Not stated";}

// matching: overlap of stemmed terms; evidence shown, never inferred
var STOP="a an and are as at be by for from in into of on or that the their to with using use via data new based study research approach approaches methods method sec section improve support supports".split(" ");
function terms(arr){var o={};arr.join(" ").toLowerCase().replace(/[^a-z0-9 ]/g," ").split(/\s+/).forEach(function(w){if(w.length<4||STOP.indexOf(w)>-1)return;o[w.replace(/(ing|ed|es|s|ion|al)$/,"")]=w;});return o;}
function match(p,o){
 var a=terms(p.areas),b=terms(o.pri),sh=[];for(var k in a)if(b[k])sh.push(a[k]);
 var r;
 if(o.elig==="Blocked")r="Not eligible";
 else if(sh.length>=2&&p.status==="Verified"&&o.elig==="Clear")r="High";
 else if(sh.length>=2)r="Medium";
 else r="Low";
 var risks=[];
 if(p.status!=="Verified")risks.push("Profile "+p.status+": cannot be High until verified");
 if(o.elig==="Unclear")risks.push("Eligibility unclear: RD to verify");
 if(o.elig==="Blocked")risks.push("Eligibility blocker");
 if(o.notes)risks.push(o.notes);
 if(!o.dl)risks.push("Deadline not stated");
 if(sh.length===1)risks.push("Only one shared term: treated as Low unless RD sees real alignment");
 return {p:p,o:o,r:r,sh:sh,risks:risks};}
var ORD={"High":0,"Medium":1,"Low":2,"Not eligible":3};
function cls(r){return r==="Not eligible"?"r-NE":"r-"+r;}

// deliverables
var cur=null;
var MS=[["Verify NOFO, deadline, eligibility",70],["Send targeted alerts",60],["PI go/no-go reply",45],["Budget and partner commitments",30],["Draft to internal review",14],["Final package ready",7],["Sponsor deadline",0]];
function mailFor(o,ms){
 var depts=[];ms.forEach(function(m){if(depts.indexOf(m.p.dept)<0)depts.push(m.p.dept);});
 return "Subject: Funding opportunity for your consideration: "+o.title+(o.dl?" (due "+fmt(o.dl)+")":"")+"\n\nDear [Chair, "+(depts.join(" / ")||"Department")+"],\n\nResearch Development is sharing a funding opportunity that may be relevant to faculty in your department: "+o.title+" from "+o.sponsor+". Sponsor page: "+(o.url||"[add link]")+".\n\nDeadline: "+(o.dl?fmt(o.dl):"not stated in the source; please see the sponsor page")+".\nParticipation: "+(o.notes||"[add high-level eligibility, lead vs. partner, required collaborators]")+" Eligibility has "+(o.elig==="Clear"?"been confirmed by Research Development.":"not yet been fully confirmed by Research Development.")+"\n\nThis is a targeted informational alert, not a request or mandate. We are glad to discuss fit, partners, or timelines.\n\n[Research Development signature]\n\n(DRAFT: edit before sending.)";}
function promptFor(o,ms){
 return "ROLE: Research development analyst, SMU Dedman College. You support human decisions; you do not send or commit anyone.\nRULES: Cite sponsor claims by section/page and SMU claims by URL + exact quote + date. Evidence tiers: E1 direct quote, E2 Scholar/ORCID corroboration, E3 your reasoning (caps at Medium). If unsupported write exactly: \"No explicit support found in the provided sources.\" Never state a deadline/award/eligibility rule not in the sponsor text. Only Verified profiles can be High. No Restricted data.\n\nTASK: Check the tool's screening results below against the sources. Confirm, downgrade or reject each rating, add missed matches from Dedman pages, and list eligibility risks and gaps.\n\nOPPORTUNITY: "+o.title+" ("+o.sponsor+") "+(o.url||"")+"\nDeadline: "+fmt(o.dl)+" | Eligibility status: "+o.elig+" | Notes: "+(o.notes||"none")+"\nPriorities (quoted):\n- "+o.pri.join("\n- ")+"\n\nSCREENING RESULTS:\n"+ms.map(function(m){return "- "+m.p.name+" ("+m.p.dept+", "+m.p.status+", retrieved "+(m.p.ret||"n/a")+") "+m.r+"; shared terms: "+(m.sh.join(", ")||"none")+"; areas quoted: "+m.p.areas.join(" | ");}).join("\n");}
function ics(o){
 if(!o.dl)return null;var p=o.dl.split("-"),base=new Date(+p[0],+p[1]-1,+p[2]);
 function pad(n){return (n<10?"0":"")+n;}function ymd(d){return d.getFullYear()+pad(d.getMonth()+1)+pad(d.getDate());}
 function esc(s){return String(s).replace(/\\/g,"\\\\").replace(/;/g,"\;").replace(/,/g,"\\,").replace(/\n/g,"\\n");}
 var st=new Date().toISOString().replace(/[-:]/g,"").replace(/\.\d+/,""),L=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//FORGE SIGNAL//Workbench//EN"];
 MS.forEach(function(m,i){var d=new Date(base);d.setDate(d.getDate()-m[1]);var e=new Date(d);e.setDate(e.getDate()+1);
  L.push("BEGIN:VEVENT","UID:"+o.id+"-"+i+"-"+st+"@forge-signal","DTSTAMP:"+st,"DTSTART;VALUE=DATE:"+ymd(d),"DTEND;VALUE=DATE:"+ymd(e),"SUMMARY:"+esc(o.title+": "+m[0]),"DESCRIPTION:"+esc("Placeholder offset. Verify on sponsor page. "+(o.url||"")),"END:VEVENT");});
 L.push("END:VCALENDAR");return L.join("\r\n");}
function showDeliver(o,ms,head){cur={o:o};$("deliver").hidden=false;$("dh").textContent=head;$("mail").textContent=mailFor(o,ms);$("prm").textContent=promptFor(o,ms);$("ci").disabled=!o.dl;$("ci").title=o.dl?"":"No deadline stated";}
function copy(id){var m=$("msg");(navigator.clipboard?navigator.clipboard.writeText($(id).textContent):Promise.reject()).then(function(){m.textContent="Copied.";},function(){m.textContent="Copy failed; select and copy manually.";});}
$("cm").onclick=function(){copy("mail");};$("cp").onclick=function(){copy("prm");};
$("ci").onclick=function(){var t=ics(cur.o);if(!t)return;var a=h("a",{href:URL.createObjectURL(new Blob([t],{type:"text/calendar"})),download:"signal-"+cur.o.title.toLowerCase().replace(/[^a-z0-9]+/g,"-").slice(0,40)+".ics"});document.body.appendChild(a);a.click();a.remove();};

// tables
function matchTable(rows,firstCol){
 var t=h("table"),hd=h("tr");[firstCol,"Rating","Shared terms (evidence)","Notes / risks"].forEach(function(x){hd.appendChild(h("th",{},[x]));});t.appendChild(h("thead",{},[hd]));
 var tb=h("tbody");rows.forEach(function(m){var tr=h("tr");
  var who=firstCol==="Faculty"?[m.p.name+" · "+m.p.dept,h("br"),h("span",{class:"small"},[m.p.areas.join("; ")])]:[m.o.title+" · "+m.o.sponsor,h("br"),h("span",{class:"small"},["Deadline: "+fmt(m.o.dl)+" · "+m.o.pri.join("; ")])];
  tr.appendChild(h("td",{},who));tr.appendChild(h("td",{class:cls(m.r)},[m.r]));
  tr.appendChild(h("td",{},[m.sh.length?m.sh.join(", "):"No explicit support found in the provided sources."]));tr.appendChild(h("td",{},[m.risks.join(" · ")||"None flagged"]));tb.appendChild(tr);});
 t.appendChild(tb);return t;}
function fillSel(sel,items,label){var v=sel.value;clear(sel);items.forEach(function(x){sel.appendChild(h("option",{value:x.id},[label(x)]));});if(items.some(function(x){return x.id===v;}))sel.value=v;}
function runB(){var o=S.opps.filter(function(x){return x.id===$("b_o").value})[0],out=$("b_out");clear(out);$("deliver").hidden=true;
 if(!o){out.appendChild(h("p",{},["Add an opportunity first."]));return;}
 var ms=S.profiles.map(function(p){return match(p,o);}).sort(function(a,b){return ORD[a.r]-ORD[b.r]||b.sh.length-a.sh.length;});
 var shown=ms.filter(function(m){return $("b_low").checked||m.r!=="Low";});
 out.appendChild(h("p",{class:"small"},[shown.length+" of "+ms.length+" profiles shown."]));
 out.appendChild(shown.length?matchTable(shown,"Faculty"):h("p",{},["No Medium or High matches. Low matches hidden."]));
 var alertSet=ms.filter(function(m){return m.r==="High"||m.r==="Medium";});
 if(alertSet.length){var b=h("button",{class:"btn dark",type:"button"},["Prepare alert, prompt and calendar"]);b.onclick=function(){showDeliver(o,alertSet,"Drafts for: "+o.title);$("deliver").scrollIntoView();};out.appendChild(b);}}
function runA(){var p=S.profiles.filter(function(x){return x.id===$("a_p").value})[0],out=$("a_out");clear(out);$("deliver").hidden=true;
 if(!p){out.appendChild(h("p",{},["Add a profile first."]));return;}
 var w=parseInt($("a_w").value,10),now=new Date();now.setHours(0,0,0,0);
 var ms=S.opps.filter(function(o){if(!w)return true;if(!o.dl)return true;var d=(new Date(o.dl+"T00:00:00")-now)/864e5;return d>=0&&d<=w;}).map(function(o){return match(p,o);}).filter(function(m){return m.r==="High"||m.r==="Medium";}).sort(function(a,b){return ORD[a.r]-ORD[b.r]||b.sh.length-a.sh.length;});
 out.appendChild(ms.length?matchTable(ms,"Opportunity"):h("p",{},["No High or Medium matches in this window."]));
 if(p.status!=="Verified")out.appendChild(h("p",{class:"note"},["This profile is "+p.status+". Verify it before relying on these results; it cannot receive High."]));
 ms.forEach(function(m){var b=h("button",{class:"btn dark s",type:"button",style:"margin:4px 6px 4px 0"},["Drafts: "+m.o.title]);b.onclick=function(){showDeliver(m.o,[m],"Drafts for "+p.name+": "+m.o.title);$("deliver").scrollIntoView();};out.appendChild(b);});}

// lists + forms
function renderLists(){
 var pl=$("profList");clear(pl);S.profiles.forEach(function(p){var d=h("div",{class:"item"},[h("div",{},[h("strong",{},[p.name]),h("div",{class:"small"},[p.dept+" · "+p.status+" · retrieved "+(p.ret||"n/a")+(p.url?" · ":"")]),h("div",{class:"small"},[p.areas.join("; ")])]),h("div",{})]);
  if(p.url){d.firstChild.children[1].appendChild(h("a",{href:p.url,rel:"noopener"},["profile"]));}
  var e=h("button",{class:"btn s dark",type:"button"},["Edit"]);e.onclick=function(){$("pf_n").value=p.name;$("pf_d").value=p.dept;$("pf_u").value=p.url;$("pf_s").value=p.status;$("pf_r").value=p.ret;$("pf_a").value=p.areas.join("\n");pf.dataset.id=p.id;$("pfH").textContent="Edit profile";$("pf_n").focus();};
  var x=h("button",{class:"btn s ghost",type:"button",style:"color:var(--blue);border-color:var(--blue)"},["Delete"]);x.onclick=function(){if(confirm("Delete "+p.name+"?")){S.profiles=S.profiles.filter(function(q){return q.id!==p.id;});save();renderAll();}};
  d.lastChild.appendChild(e);d.lastChild.appendChild(document.createTextNode(" "));d.lastChild.appendChild(x);pl.appendChild(d);});
 var ol=$("oppList");clear(ol);S.opps.forEach(function(o){var d=h("div",{class:"item"},[h("div",{},[h("strong",{},[o.title]),h("div",{class:"small"},[o.sponsor+" · Deadline: "+fmt(o.dl)+" · Eligibility: "+o.elig]),h("div",{class:"small"},[o.pri.join("; ")])]),h("div",{})]);
  var x=h("button",{class:"btn s ghost",type:"button",style:"color:var(--blue);border-color:var(--blue)"},["Delete"]);x.onclick=function(){if(confirm("Delete "+o.title+"?")){S.opps=S.opps.filter(function(q){return q.id!==o.id;});save();renderAll();}};d.lastChild.appendChild(x);ol.appendChild(d);});}
function renderAll(){renderLists();fillSel($("b_o"),S.opps,function(o){return o.title;});fillSel($("a_p"),S.profiles,function(p){return p.name+" ("+p.dept+")";});runB();runA();}
var pf=$("pf");
function lines(s){return s.split("\n").map(function(x){return x.trim();}).filter(Boolean);}
function resetPf(){pf.reset();delete pf.dataset.id;$("pfH").textContent="Add profile";}
pf.onsubmit=function(e){e.preventDefault();var rec={id:pf.dataset.id||uid(),name:$("pf_n").value.trim(),dept:$("pf_d").value.trim(),url:$("pf_u").value.trim(),status:$("pf_s").value,ret:$("pf_r").value,areas:lines($("pf_a").value)};
 var i=S.profiles.findIndex(function(p){return p.id===rec.id;});if(i>-1)S.profiles[i]=rec;else S.profiles.push(rec);save();resetPf();renderAll();};
$("pf_c").onclick=resetPf;
$("of").onsubmit=function(e){e.preventDefault();S.opps.push({id:uid(),title:$("of_t").value.trim(),sponsor:$("of_s").value.trim(),url:$("of_u").value.trim(),dl:$("of_d").value,elig:$("of_e").value,notes:$("of_x").value.trim(),pri:lines($("of_p").value)});save();$("of").reset();renderAll();};
$("b_o").onchange=runB;$("b_low").onchange=runB;$("a_p").onchange=runA;$("a_w").onchange=runA;
$("ex").onclick=function(){var a=h("a",{href:URL.createObjectURL(new Blob([JSON.stringify(S,null,1)],{type:"application/json"})),download:"signal-workbench.json"});document.body.appendChild(a);a.click();a.remove();};
$("im").onchange=function(){var f=this.files[0];if(!f)return;var r=new FileReader();r.onload=function(){try{var s=JSON.parse(r.result);if(!Array.isArray(s.profiles)||!Array.isArray(s.opps))throw 0;S=s;save();renderAll();$("dmsg").textContent="Imported.";}catch(e){$("dmsg").textContent="Import failed: not a Workbench file.";}};r.readAsText(f);};
$("reset").onclick=function(){if(confirm("Replace all data with the sample set?")){S=JSON.parse(JSON.stringify(SAMPLE));save();renderAll();}};
document.querySelectorAll(".tab[data-t]").forEach(function(t){t.onclick=function(){document.querySelectorAll(".tab[data-t]").forEach(function(x){x.setAttribute("aria-pressed",x===t);});
 ["prof","opp","b","a","data"].forEach(function(k){$("p-"+k).hidden=k!==t.dataset.t;});$("deliver").hidden=true;};});
renderAll();
})();
