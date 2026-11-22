(function(){
var $=function(i){return document.getElementById(i);};
var CORE="ROLE\nYou are a research development analyst supporting SMU Dedman College of Humanities and Sciences. You support human decision-making; you do not decide, send, or commit anyone to anything.\n\nSOURCES (use only these)\n- Sponsor text provided below.\n- SMU evidence: pages under https://www.smu.edu/dedman.\n- Corroboration only, label E2: public Google Scholar/ORCID pages for named faculty.\nIf a source cannot be opened, say so; do not reconstruct it from memory.\n\nRULES\n1. Cite every claim: sponsor claims by section header/page; SMU claims by URL + short exact quote + date retrieved.\n2. Evidence tiers: E1 direct quote; E2 public corroboration; E3 your thematic reasoning (label it; caps rating at Medium).\n3. If no support exists, write exactly: \"No explicit support found in the provided sources.\"\n4. Never state a deadline, award amount, or eligibility rule not in the sponsor text. Missing stays \"Not stated.\"\n5. Only profiles marked Verified may be rated High; others are \"possible, needs verification.\"\n6. Do not assume SMU's institutional eligibility, limited-submission status, or cost-share rules; flag them for Research Development to confirm.\n7. No Restricted data (SMU Policy 8.6).\n8. Ratings: High = sponsor priority matched to an E1 quote on the person's/department's page, no unresolved eligibility blocker. Medium = thematic overlap or eligibility/structure uncertainty. Low = indirect. Not eligible = hard blocker (list separately).\n";
var cur="b";
function v(id){return ($(id).value||"").trim()||"[not provided]";}
function build(){
 var t;
 if(cur==="b"){
  t=CORE+"\nMODE: OPPORTUNITY_TO_FACULTY\nFUNDING OPPORTUNITY LINK(S): "+v("b_link")+"\nNOFO TEXT:\n"+v("b_text")+"\nDEPARTMENTS TO CONSIDER: "+v("b_dept")+"\n\nTASKS\nA. Fact Sheet: priorities, supported activities, eligibility (institution/PI/structure), constraints, deadlines, award size, review criteria, each cited.\nB. Eligibility screen: blockers, uncertainties, what Research Development must verify.\nC. Match table for plausible departments/faculty.\nD. Gaps: sponsor priorities with no Dedman support found.\nE. Outreach summary: who to contact (role/unit) and why.\nF. DRAFT department-head alert email: 1-2 sentence description, links, key deadlines, high-level eligibility, and a clear statement that it is a targeted informational alert, not a mandate.\n\nOUTPUT\n1) Fact Sheet 2) Eligibility and risk flags 3) Table: | PI | Dept | Research area (quote + URL) | NOFO priority (quote + cite) | Rating | Evidence tier | Rationale | Risks | 4) Outreach summary 5) Draft email 6) Verify-before-sending checklist";
  $("out_h").textContent="Prompt to run (Opportunity → Faculty)";
 } else if(cur==="a"){
  t=CORE+"\nMODE: FACULTY_TO_OPPORTUNITIES\nPI: "+v("a_pi")+"\nDEPARTMENT: "+v("a_dept")+"\nCAREER STAGE: "+v("a_stage")+"\nPI-CONFIRMED INTERESTS (their words):\n"+v("a_topics")+"\nPREFERRED SPONSORS: "+v("a_sp")+"\nWINDOW: "+$("a_win").value+" from today\n\nTASKS\nA. Restate the profile using quotes from the PI's Dedman page plus the PI-confirmed interests above.\nB. Search official sponsor sources (Grants.gov, NSF, NIH Guide, NEH, DOE, and others relevant) for open AND forecasted opportunities in the window. List each source searched and any that could not be reached.\nC. For each candidate: brief Fact Sheet, eligibility screen, rating.\nD. Return High and Medium only, ranked by fit then deadline, with a note on the internal lead time needed.\nE. DRAFT short PI-facing digest: what, why it fits, deadline, suggested next step.\n\nOUTPUT\n1) Profile 2) Ranked table: | Opportunity | Sponsor | Deadline | Rating | Evidence (quote + cite) | Eligibility flags | Next step | 3) Draft digest 4) Verify-before-sending checklist";
  $("out_h").textContent="Prompt to run (Faculty → Opportunities)";
 } else {
  t="Use the Calendar tab to download the .ics file for the milestones shown above.";
  $("out_h").textContent="Calendar";
 }
 $("prompt").textContent=t;
}
document.querySelectorAll(".tab[data-p]").forEach(function(b){b.addEventListener("click",function(){
 cur=b.dataset.p;
 document.querySelectorAll(".tab[data-p]").forEach(function(x){x.setAttribute("aria-pressed",x===b);});
 $("pa").hidden=cur!=="a";$("pb").hidden=cur!=="b";$("pcal").hidden=cur!=="c";$("out").hidden=cur==="c";
 build();});});
document.querySelectorAll("input,textarea,select").forEach(function(e){e.addEventListener("input",function(){build();cal();});});
$("copy").addEventListener("click",function(){var m=$("msg");
 (navigator.clipboard?navigator.clipboard.writeText($("prompt").textContent):Promise.reject()).then(function(){m.textContent="Copied.";},function(){m.textContent="Copy failed; select the text and copy manually.";});});

// Calendar. Offsets are placeholders, editable here.
var MS=[["Verify NOFO, deadline, eligibility",70],["Send targeted alerts to chairs / PIs",60],["PI intent / go-no-go reply",45],["Budget and partner commitments",30],["Draft to internal review",14],["Final package ready",7],["Sponsor deadline",0]];
var rows=$("c_rows");
MS.forEach(function(m,i){var tr=document.createElement("tr");
 tr.innerHTML='<td>'+m[0]+'</td><td><input type="number" min="0" max="365" value="'+m[1]+'" data-i="'+i+'" aria-label="Days before deadline: '+m[0]+'"></td><td class="d"></td>';rows.appendChild(tr);});
function pad(n){return (n<10?"0":"")+n;}
function ymd(d){return d.getFullYear()+pad(d.getMonth()+1)+pad(d.getDate());}
function dates(){var s=$("c_date").value;if(!s)return null;var p=s.split("-"),base=new Date(+p[0],+p[1]-1,+p[2]);
 return Array.prototype.map.call(rows.querySelectorAll("input"),function(inp,i){var d=new Date(base);d.setDate(d.getDate()-(parseInt(inp.value,10)||0));return {t:MS[i][0],d:d};});}
function cal(){var ds=dates(),cells=rows.querySelectorAll(".d");
 cells.forEach(function(c,i){c.textContent=ds?ds[i].d.toLocaleDateString(undefined,{weekday:"short",year:"numeric",month:"short",day:"numeric"}):"Enter a deadline";});}
function esc(s){return String(s).replace(/\\/g,"\\\\").replace(/;/g,"\;").replace(/,/g,"\\,").replace(/\n/g,"\\n");}
$("c_ics").addEventListener("click",function(){var ds=dates();if(!ds){$("c_date").focus();return;}
 var title=($("c_title").value||"Funding opportunity").trim(),url=$("c_url").value.trim(),stamp=new Date().toISOString().replace(/[-:]/g,"").replace(/\.\d+/,"");
 var L=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//FORGE SIGNAL//Workflow//EN","CALSCALE:GREGORIAN"];
 ds.forEach(function(x,i){var e=new Date(x.d);e.setDate(e.getDate()+1);
  L.push("BEGIN:VEVENT","UID:signal-"+stamp+"-"+i+"@forge-signal","DTSTAMP:"+stamp,"DTSTART;VALUE=DATE:"+ymd(x.d),"DTEND;VALUE=DATE:"+ymd(e),
   "SUMMARY:"+esc(title+": "+x.t),"DESCRIPTION:"+esc("Working-backward milestone (placeholder offset). Verify dates on the sponsor page."+(url?" "+url:"")),"END:VEVENT");});
 L.push("END:VCALENDAR");
 var a=document.createElement("a");a.href=URL.createObjectURL(new Blob([L.join("\r\n")],{type:"text/calendar"}));
 a.download="signal-"+title.toLowerCase().replace(/[^a-z0-9]+/g,"-").slice(0,40)+".ics";document.body.appendChild(a);a.click();a.remove();});
build();cal();
})();
