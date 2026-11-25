/* Shared rendering for the FORGE SIGNAL interface.
   Reads window.MOCK today; the same functions take the API response once wired.
   All text is inserted as text nodes, never as HTML: opportunity text is sponsor-supplied. */
(function () {
  "use strict";
  var CFG = window.SIGNAL || { live: false, api: "" };
  var LIVE = !!CFG.live;               // true: talk to the API; false: show the fictional sample run
  var M = window.MOCK || {};
  var RUN_KEY = "signal.run";          // the latest run, kept in this browser tab only
  var MODE_KEY = "signal.mode";        // "recorded" once the visitor chose the recorded example (this tab only)
  var RMODE = false;                   // true while a page shows the recorded run
  function isLive() { return LIVE && !RMODE; }
  function recordedChosen() { try { return sessionStorage.getItem(MODE_KEY) === "recorded"; } catch (e) { return false; } }
  function setMode(v) { try { if (v) sessionStorage.setItem(MODE_KEY, v); else sessionStorage.removeItem(MODE_KEY); } catch (e) { /* not remembered */ } }

  function api(path, opts) {
    opts = opts || {};
    return fetch((CFG.api || "") + path, {
      method: opts.method || "GET",
      headers: opts.body ? { "Content-Type": "application/json" } : {},
      body: opts.body ? JSON.stringify(opts.body) : undefined,
      signal: opts.signal
    }).then(function (r) {
      return r.text().then(function (t) {
        var j = null; try { j = t ? JSON.parse(t) : null; } catch (e) { j = null; }
        if (!r.ok) {
          var d = j && j.detail;
          if (Array.isArray(d)) d = d.map(function (x) { return x.msg; }).join("; ");
          else if (d && typeof d === "object") d = d.message || d.code || null;
          if (!d && (r.status === 413 || r.status === 411)) d = "That request is too large. Shorten the research areas or the project description and try again.";
          var er = new Error(d || ("The server answered " + r.status + ".")); er.status = r.status;
          if (j && j.detail && typeof j.detail === "object" && !Array.isArray(j.detail) && typeof j.detail.code === "string") er.code = j.detail.code;
          throw er;
        }
        return j;
      });
    }, function (e) {
      if (e && e.name === "AbortError") throw e;
      throw new Error("We could not reach the server. Your entries are still here. Check your connection and select Find opportunities again.");
    });
  }
  function readRun() { try { return JSON.parse(sessionStorage.getItem(RUN_KEY) || "null"); } catch (e) { return null; } }
  function saveRun(o) { try { sessionStorage.setItem(RUN_KEY, JSON.stringify(o)); } catch (e) { /* private mode: the run just is not remembered */ } }

  function el(tag, attrs, kids) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) {
      if (k === "class") n.className = attrs[k]; else n.setAttribute(k, attrs[k]);
    });
    (kids || []).forEach(function (c) { n.appendChild(typeof c === "string" ? document.createTextNode(c) : c); });
    return n;
  }
  function $(id) { return document.getElementById(id); }
  function clear(n) { while (n && n.firstChild) n.removeChild(n.firstChild); }
  function money(v) { return v == null ? null : "$" + Number(v).toLocaleString("en-US"); }
  function dateLong(iso) {
    if (!iso) return null;
    var p = String(iso).split("-");
    return new Date(+p[0], +p[1] - 1, +p[2]).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
  }
  function pad2(n) { return (n < 10 ? "0" : "") + n; }
  function dayStart(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()); }
  function isoDay(d) { return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()); }
  function parseDay(iso) { var p = String(iso).split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function daysUntil(iso) { return Math.round((parseDay(iso) - dayStart(new Date())) / 864e5); }
  function addDays(iso, k) { var d = parseDay(iso); d.setDate(d.getDate() + k); return isoDay(d); }
  function orNot(v, word) { return v == null || v === "" ? el("span", { class: "nostate" }, [word || "Not specified"]) : document.createTextNode(String(v)); }

  /* badges always carry words, so colour is never the only signal */
  function fitBadge(r) {
    if (!r.fit) return el("span", { class: "badge b-excluded" }, ["Excluded · " + r.tier]);
    return el("span", { class: "badge b-" + r.fit.toLowerCase() }, [r.fit + " · " + r.tier + " fit"]);
  }
  function eligBadge(e) {
    var c = e === "Eligible" ? "b-elig" : e === "Not eligible" ? "b-notelig" : "b-needs";
    return el("span", { class: "badge " + c }, ["Eligibility: " + e]);
  }

  function citationBlock(c, r) {
    var src = c.source_id === "researcher-profile"
      ? el("span", {}, ["Researcher profile, supplied for this run"])
      : el("a", { href: c.source_id, rel: "noopener noreferrer", target: "_blank", "aria-label": "Official source for " + (r && r.number ? r.number : "this opportunity") + " (opens in a new tab)" }, ["Official source"]);
    return el("div", { class: "quote", role: "group", "aria-label": String(c["for"]).replace(/_/g, " ") + " evidence" }, [
      el("span", { class: "for-tag" }, [String(c["for"]).replace(/_/g, " ")]),
      el("q", {}, [c.quote]),
      el("span", { class: "src" }, [src, document.createTextNode(" · retrieved " + (dateLong((M.retrieved_at || "").slice(0, 10)) || "today"))])
    ]);
  }

  function howCalculated(r) {
    var h = r.how_calculated || {}, d = el("details", { class: "calc" });
    d.appendChild(el("summary", {}, ["How this fit was calculated"]));
    var body = el("div", { class: "body" });
    body.appendChild(el("p", { class: "hint" }, ["The model reported these factor values with quotes. The rating itself is calculated from the published rubric, not chosen by the model."]));
    var kv = el("dl", { class: "kv" });
    Object.keys(h.factors || {}).forEach(function (k) {
      kv.appendChild(el("dt", {}, [k.replace(/_/g, " ")]));
      kv.appendChild(el("dd", {}, [String(h.factors[k])]));
    });
    body.appendChild(kv);
    var ul = el("ul", { class: "rule-list" });
    (h.reasons || []).forEach(function (reason, i) {
      ul.appendChild(el("li", {}, [reason + " ", el("span", { class: "pill" }, [(h.rules_fired || [])[i] || "rule"])]));
    });
    body.appendChild(ul);
    (h.adjustments || []).forEach(function (a) { body.appendChild(el("div", { class: "adjust" }, ["Adjusted: " + a])); });
    if (r.failed_citation_count) {
      body.appendChild(el("div", { class: "adjust" }, [r.failed_citation_count +
        " quote(s) could not be found in the source and were discarded. Unsupported claims never raise a rating."]));
    }
    if ((r.prefilter_shared_terms || []).length) {
      body.appendChild(el("p", { class: "hint", style: "margin-top:9px" },
        ["Chosen to be checked because these terms appear in both the research areas and the announcement: " +
         r.prefilter_shared_terms.join(", ") + ". That ranking only decides which announcements are checked; it is not the fit judgment."]));
    }
    d.appendChild(body);
    return d;
  }

  var cardSeq = 0;
  /* fixed wording keyed to the eligibility value and flags; never written by the model */
  function yourCheck(r) {
    var t = r.eligibility === "Eligible"
      ? "Confirm the deadline and the eligibility wording on the sponsor page before any outreach."
      : r.eligibility === "Not eligible"
        ? "A stated restriction may exclude this researcher. Read the quoted sentence and the sponsor page before ruling it out."
        : "The announcement does not clearly say who may apply. Read the eligibility section on the sponsor page, or ask the program officer.";
    var fl = (r.flags || []).join(" ").toLowerCase();
    if (fl.indexOf("limited") >= 0) t += " Limited submission: ask your research office about the internal selection.";
    if (fl.indexOf("invitation") >= 0) t += " Invitation only: contact the program officer.";
    if (r.status === "Rolling") t += " Rolling program: confirm the topic with the program officer.";
    return t;
  }

  function resultCard(r) {
    var tid = "res-" + (++cardSeq);
    var card = el("article", { class: "result r-" + (r.fit || "Excluded"), "aria-labelledby": tid });
    var h = el("h3", { id: tid }, [el("a", { href: r.url, rel: "noopener noreferrer", target: "_blank" }, [r.title])]);
    card.appendChild(h);
    var dl = el("li", {}, ["Sponsor deadline: "]);
    dl.appendChild(orNot(dateLong(r.close_date), "Not stated"));
    if (r.days_to_deadline != null) {
      if (r.passed || r.days_to_deadline < 0) { dl.appendChild(document.createTextNode(" ")); dl.appendChild(el("span", { class: "passed" }, ["(passed)"])); }
      else dl.appendChild(document.createTextNode(r.days_to_deadline === 0 ? " (today)" : " (" + r.days_to_deadline + " day" + (r.days_to_deadline === 1 ? "" : "s") + ")"));
    }
    card.appendChild(el("ul", { class: "meta-list" }, [el("li", {}, [r.sponsor]), el("li", {}, [el("span", { class: "mono" }, [r.number])]), dl]));

    var badges = el("div", { class: "badges" }, [fitBadge(r), eligBadge(r.eligibility)]);
    if (r.status) badges.appendChild(el("span", { class: "flag info" }, ["Status: " + r.status]));
    (r.flags || []).forEach(function (f) { badges.appendChild(el("span", { class: "flag info" }, [f])); });
    (r.currency_flags || []).forEach(function (f) { badges.appendChild(el("span", { class: "flag" }, ["\u26A0 " + f])); });
    card.appendChild(badges);

    card.appendChild(el("p", {}, [r.rationale]));
    if (r.fit === "High" && r.eligibility !== "Eligible")
      card.appendChild(el("p", { class: "hint" }, ["This High rating holds only if the sponsor page confirms that your institution may apply."]));
    card.appendChild(el("div", { class: "yourcheck" }, [el("strong", {}, ["Your check: "]), document.createTextNode(yourCheck(r))]));

    var cites = r.citations || [], n = cites.length, bad = r.failed_citation_count || 0;
    var label = n ? "Evidence: " + n + " quote" + (n === 1 ? "" : "s") + " found in the sources"
                  : "Evidence: no explicit support found in the provided sources";
    if (bad) label += " \u00b7 " + bad + " discarded (not found in the source)";
    var ev = el("details", { class: "evidence" }, [el("summary", {}, [label])]);
    var body = el("div", { class: "body" });
    cites.forEach(function (c) { body.appendChild(citationBlock(c, r)); });
    if (!n) body.appendChild(el("div", { class: "quote" }, [el("q", {}, ["No explicit support found in the provided sources."])]));
    body.appendChild(howCalculated(r));
    ev.appendChild(body);
    card.appendChild(ev);
    return card;
  }

  function counters(c) {
    var t = "Read " + c.opportunities_listed + " announcements. " + c.in_horizon + " fit your deadline window. " +
      c.judged + " checked" + (c.not_judged_due_to_cap ? ", " + c.not_judged_due_to_cap + " not checked because of the limit" : "") + "." +
      (c.no_term_overlap ? " " + c.no_term_overlap + " share no words with the research areas and were not checked." : "") +
      (c.model_call_failures ? " " + c.model_call_failures + " could not be rated because the model failed." : "") +
      (c.source_failures ? " " + c.source_failures + " source" + (c.source_failures === 1 ? "" : "s") + " could not be read." : "");
    return el("p", { class: "countline" }, [t]);
  }

  /* ---------------------------------------------------------------- live mode */
  function liveBanner() {
    var b = document.querySelector(".mock-banner");
    if (b) b.textContent = "Live preview. Opportunity data comes from the public Grants.gov API. Runs are logged.";
    var f = document.querySelector("footer p");      // the footer must not claim sample data when the data is real
    if (f && f.firstChild) f.firstChild.nodeValue = f.firstChild.nodeValue.replace("Preview with sample data only;",
      "Preview using public Grants.gov data;");
  }

  function greeting() {
    var p = M.profile || {};
    if (isLive()) return "Hello,";   // the person who sends this chooses how to address the recipient
    var parts = (p.investigator || "").replace(/\(fictional\)/, "").trim().split(/\s+/);
    return "Dear Dr. " + (parts[parts.length - 1] || "") + ",";
  }

  function provenance() {
    var n = $("provenance"); if (!n) return;
    var s = M.source || (M.recorded_run && M.recorded_run.source);
    if ((!isLive() && !RMODE) || !s) { n.textContent = "Sample data only: no real source was read."; return; }
    var when = s.retrieved_at ? (RMODE ? recStamp(s.retrieved_at) : new Date(s.retrieved_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })) : null;
    n.textContent = "Source: " + s.system + " public API (" + String(s.api).replace(" (public)", "") + "). " +
      (s.mode === "stored copy"
        ? "Read from a stored copy retrieved " + when + (s.records ? " (" + s.records.toLocaleString("en-US") + " records)" : "") + ". Confirm every date on the sponsor page."
        : "Read live from Grants.gov for this run.") +
      (RMODE ? " " + asOfLine() + "." : "");
  }

  function downloads() {
    var h = $("dl-hint");
    if (RMODE) {
      ["dl-xlsx", "dl-ics"].forEach(function (id) { var b = $(id); if (b) b.parentNode.removeChild(b); });
      if (h) h.textContent = "Downloads are not offered on the recorded example. They work on a live run.";
    }
    if (!isLive() || !M.run_id) return;
    [["dl-xlsx", "calendar.xlsx", "Download spreadsheet (.xlsx)", "btn accent"],
     ["dl-ics", "calendar.ics", "Download calendar (.ics)", "btn ghost"]].forEach(function (p) {
      var old = $(p[0]); if (!old) return;
      var a = el("a", { class: p[3], href: (CFG.api || "") + "/api/runs/" + encodeURIComponent(M.run_id) + "/" + p[1], download: "" }, [p[2]]);
      old.parentNode.replaceChild(a, old);
    });
    if (h) h.hidden = true;
  }

  function noRun(message) {
    document.querySelectorAll("main > .wrap").forEach(function (w) { w.hidden = true; });
    document.querySelectorAll(".pagehead .btn-row, #screened, #dl-hint").forEach(function (n) { n.hidden = true; });
    var c = $("count"); if (c) c.textContent = "No run yet.";
    document.querySelector("main").appendChild(el("div", { class: "wrap pt-main" }, [
      el("div", { class: "status none" }, [el("h2", {}, ["There is no run to show yet"]),
        el("p", {}, [message || "Start by finding funding for a researcher. Results, the calendar and the draft alert are built from your latest run in this browser tab."]),
        el("div", { class: "btn-row" }, [el("a", { class: "btn", href: "match.html" }, ["Find funding for a researcher"])])])]));
  }

  var RANKS = { "High only": ["High"], "Medium and above": ["High", "Medium"], "All": ["High", "Medium", "Low"], "Low and above": ["High", "Medium", "Low"] };

  /* the saved run plus the engine's calendar for it, shaped like the sample run the pages were built on */
  function loadLive() {
    var saved = readRun();
    if (!saved || !saved.response) return Promise.resolve(null);
    var resp = saved.response, inp = saved.input || {};
    return api("/api/runs/" + encodeURIComponent(resp.run_id) + "/calendar").then(function (cal) {
      var byUrl = {};
      Object.keys(cal.groups).forEach(function (g) { cal.groups[g].forEach(function (r) { byUrl[r.url] = r; }); });
      var keep = RANKS[inp.minfit] || RANKS["All"];
      var results = resp.results.filter(function (r) { return keep.indexOf(r.fit) >= 0; }).map(function (r) {
        var c = byUrl[r.url] || {};
        ["status", "flags", "internal_deadline", "amount", "next_action"].forEach(function (k) { if (c[k] != null) r[k] = c[k]; });
        return r;
      });
      return { run_id: resp.run_id, profile: { investigator: inp.name || "", lanes: inp.lanes || [], type: inp.type },
               settings: { lead_time_days: cal.lead_days }, retrieved_at: resp.retrieved_at, counters: resp.counters,
               results: results, source_failures: [], source: resp.source, hidden_by_filter: resp.results.length - results.length,
               screened_at: saved.savedAt };
    });
  }

  function lines(id) { return ($(id).value || "").split("\n").map(function (x) { return x.trim(); }).filter(Boolean); }
  function firstNumber(text, fallback) { var m = /(\d+)/.exec(text || ""); return m ? +m[1] : fallback; }

  /* ---------------------------------------------------------------- run status
     Status and errors live in the "This run" card under the button, so they are on screen when the person clicks.
     The server does not report steps, so there are no step ticks: an elapsed timer and an honest range only. */
  function say(msg) { var n = $("runsay"); if (n) n.textContent = msg; }
  function reveal(n) { if (n && n.scrollIntoView) n.scrollIntoView({ block: "center" }); }
  function fmtTime(sec) { var m = Math.floor(sec / 60), r = sec % 60; return m ? m + " min " + r + " s" : r + " s"; }
  var FIELD_HINT = { "pi-name": "pi-name-hint", lanes: "lanes-hint" };
  function clearInvalid() {
    document.querySelectorAll(".field-err").forEach(function (n) { n.parentNode.removeChild(n); });
    document.querySelectorAll("[aria-invalid]").forEach(function (n) {
      n.removeAttribute("aria-invalid");
      if (FIELD_HINT[n.id]) n.setAttribute("aria-describedby", FIELD_HINT[n.id]); else n.removeAttribute("aria-describedby");
    });
  }
  function markInvalid(id, msg) {
    var f = $(id); if (!f) return null;
    f.setAttribute("aria-invalid", "true");
    var eid = id + "-err";
    f.setAttribute("aria-describedby", (FIELD_HINT[id] ? FIELD_HINT[id] + " " : "") + eid);
    var hint = FIELD_HINT[id] && $(FIELD_HINT[id]);
    var p = el("p", { class: "field-err", id: eid }, [msg]);
    if (hint) hint.parentNode.insertBefore(p, hint); else f.parentNode.insertBefore(p, f.nextSibling);
    return f;
  }
  function showError(head, msg) {
    var err = $("runerror"); clear(err);
    err.appendChild(el("h3", {}, [head])); err.appendChild(el("p", {}, [msg]));
    err.hidden = false; $("progress").hidden = true; $("done").hidden = true;
  }
  function showDone(count, note) {
    $("progress").hidden = true; $("runerror").hidden = true;
    var done = $("done");
    $("donecount").textContent = String(count);
    $("donenote").textContent = note || "";
    done.hidden = false; reveal(done); done.focus();
    say("Search finished. " + count + " opportunities rated.");
  }

  function sampleRun() {
    clearInvalid(); $("runerror").hidden = true; $("done").hidden = true;
    var prog = $("progress"), btn = $("runbtn");
    prog.hidden = false; btn.disabled = true; $("stopwait").hidden = true;
    $("runtimer").textContent = "Sample search: nothing is really being checked.";
    say("Sample run started."); reveal(prog);
    setTimeout(function () { btn.disabled = false; showDone(7); }, 1400);
  }

  function liveRun(form) {
    var btn = $("runbtn"), prog = $("progress"), stop = $("stopwait");
    var picked = document.querySelector("[data-panel]:checked"), panel = picked ? picked.getAttribute("data-panel") : "p-pi";
    var body = { options: { horizon_months: firstNumber($("horizon").value, 3), lead_time_days: firstNumber($("lead").value, 14) } };
    var input = { minfit: $("minfit").value, funders: $("funders").value, name: "", lanes: [], type: "" };
    clearInvalid(); $("runerror").hidden = true; $("done").hidden = true;

    var bad = [];
    if (panel === "p-pi") {
      var name = $("pi-name").value.trim(), lanes = lines("lanes");
      if (!name) bad.push(markInvalid("pi-name", "Enter the researcher’s name."));
      if (!lanes.length) bad.push(markInvalid("lanes", "Enter at least one research area, one per line."));
      body.input_type = "pi_name"; body.input_text = name;
      body.profile = { career_stage: $("stage").value, lanes: lanes, positioning_rules: lines("rules") };
      input.name = name; input.lanes = lanes; input.type = "pi_name";
    } else if (panel === "p-project") {
      var abs = $("abstract").value.trim();
      if (!abs) bad.push(markInvalid("abstract", "Paste a project description."));
      body.input_type = "project"; body.input_text = abs; body.profile = { career_stage: "", lanes: [], positioning_rules: [] };
      input.lanes = [abs.slice(0, 160)]; input.type = "project";
    } else if (panel === "p-keywords") {
      var kw = $("kw").value.trim();
      if (!kw) bad.push(markInvalid("kw", "Enter at least one topic."));
      body.input_type = "keywords"; body.input_text = kw; body.profile = { career_stage: "", lanes: [], positioning_rules: [] };
      input.lanes = [kw]; input.type = "keywords";
    } else {
      showError("Not available yet", "Opportunity-and-department matching is coming later. Choose a researcher, a project description or keywords for now.");
      reveal($("runerror")); return;
    }
    bad = bad.filter(Boolean);
    if (bad.length) {
      showError(bad.length === 1 ? "One thing needs fixing" : bad.length + " things need fixing",
                "Fix the highlighted field" + (bad.length === 1 ? "" : "s") + " and select Find opportunities again.");
      bad[0].focus(); return;
    }

    var t0 = Date.now(), ac = window.AbortController ? new AbortController() : null, over = false;
    prog.hidden = false; btn.disabled = true; stop.hidden = !ac; reveal(prog);
    say("Search started. This can take some time.");
    function tick() {
      var sec = Math.round((Date.now() - t0) / 1000);
      $("runtimer").textContent = "Search in progress · " + fmtTime(sec);
      if (sec > 0 && sec % 30 === 0) say("Still searching. " + fmtTime(sec) + " so far.");
    }
    tick(); var iv = setInterval(tick, 1000);
    stop.onclick = function () { over = true; if (ac) ac.abort(); };

    api("/api/runs", { method: "POST", body: body, signal: ac ? ac.signal : undefined }).then(function (resp) {
      saveRun({ input: input, response: resp, savedAt: new Date().toISOString() });
      var keep = RANKS[input.minfit] || RANKS["All"];
      var n = resp.results.filter(function (r) { return keep.indexOf(r.fit) >= 0; }).length;
      var note = n === 0 ? " Nothing was rated at or above your setting; the results page explains why." : "";
      if (input.funders !== "Federal only") note += " State, foundation and other sources are not read in this version; this run used federal opportunities from Grants.gov only.";
      showDone(n, note);
    }, function (e) {
      if (over || (e && e.name === "AbortError")) {
        showError("You stopped waiting", "The run may still finish on the server and appear in the run log. Your entries are still here.");
      } else if (e.status === 413) {
        showError("Request too large", e.message);
      } else if (e.status === 429) {
        showError("Limit reached", e.message);
      } else if (e.status === 502) {
        showError("Nothing could be rated", e.message);      // every model call failed or every answer was unreadable: not the same as "no results"
      } else if (e.status === 503) {
        if (e.code === "budget_reached") { showError("Live searches are paused", e.message); offerInError(); }
        else showError("Service not available", e.message);
      } else {
        showError("Search did not finish", e.message);
      }
    }).then(function () { clearInterval(iv); btn.disabled = false; });
  }


  /* ---------------------------------------------------------------- recorded run
     One real run (fictional researcher, public Grants.gov copy) shown as text. It is the default data on a deploy
     with no backend, and an opt-in on a live deploy. The label bar sits at the top of every page that shows it. */
  function loadRecorded() {
    return new Promise(function (resolve, reject) {
      if (window.MOCK && window.MOCK.recorded_run) { resolve(window.MOCK); return; }
      var sc = document.createElement("script");
      sc.src = "recorded-run.js";
      sc.onload = function () { window.MOCK && window.MOCK.recorded_run ? resolve(window.MOCK) : reject(new Error("The recorded example is not in the expected form.")); };
      sc.onerror = function () { reject(new Error("The recorded example could not be loaded.")); };
      document.head.appendChild(sc);
    });
  }

  function asOfLine() { return "Days counted from today, " + dateLong(isoDay(new Date())) + "; the recording was made as of " + dateLong(M.recorded_run.as_of_date) + ". A deadline earlier than today shows as passed"; }
  function recStamp(iso) { return iso ? new Date(iso).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" }) + " UTC" : "unknown time"; }

  function prepRecorded() {
    var lead = (M.settings && M.settings.lead_time_days) || 14;
    M.screened_at = (M.recorded_run || {}).recorded_at;
    (M.results || []).forEach(function (r) {   // deadlines are counted from today, in code, never taken from the recording
      if (r.close_date) {
        r.days_to_deadline = daysUntil(r.close_date);        // one number per row, counted from today; the page says so
        r.internal_deadline = addDays(r.close_date, -lead);
        r.passed = r.days_to_deadline < 0;
      } else { r.days_to_deadline = null; r.internal_deadline = null; r.passed = false; }
    });
  }

  function recordedBar() {
    var R = M.recorded_run || {}, b = document.querySelector(".mock-banner");
    if (!b) { b = el("p", { class: "mock-banner" }); document.body.insertBefore(b, document.body.firstChild); }
    clear(b); b.className = "mock-banner rec-bar"; b.setAttribute("aria-label", "Recorded example notice");
    var retrieved = (R.source && R.source.retrieved_at) || M.retrieved_at;
    var line1 = [el("strong", {}, ["Recorded example."]),
      document.createTextNode(" A real run made on " + recStamp(R.recorded_at) + ", model " + (R.model || "not stated") +
        ", opportunities as retrieved " + dateLong((retrieved || "").slice(0, 10)) + ", rubric " + (R.rubric_version || "not stated") +
        ". Not live. Not your input. Run ID " + (R.run_id || "not stated") + ".")];
    var line2 = "Researcher: " + ((M.profile || {}).investigator || "fictional researcher") + ". " + asOfLine() + ".";
    b.appendChild(el("span", { class: "rec-line" }, line1));
    var l2 = el("span", { class: "rec-line" }, [line2]);
    if (LIVE) {
      l2.appendChild(document.createTextNode(" "));
      var a = el("a", { href: "match.html" }, ["Leave the recorded example"]);
      a.addEventListener("click", function () { setMode(null); });
      l2.appendChild(a);
    }
    b.appendChild(l2);
  }

  function recordedChrome(page) {
    recordedBar();
    document.querySelectorAll(".live-only").forEach(function (n) { n.parentNode.removeChild(n); });
    document.querySelectorAll("[data-rec]").forEach(function (n) { n.textContent = n.getAttribute("data-rec"); });
    document.querySelectorAll("a.btn").forEach(function (n) { if (n.textContent.trim() === "Change the run") n.textContent = "See the input used"; });
    document.querySelectorAll(".sample-only").forEach(function (n) { n.hidden = false; n.textContent = "See the recorded example"; });
    if (page === "settings") {
      var main = document.querySelector("main");
      main.querySelectorAll(":scope > .wrap, :scope > section:not(.pagehead)").forEach(function (n) { n.parentNode.removeChild(n); });
      var lead = main.querySelector(".pagehead .lead");
      if (lead) lead.textContent = "Settings are for administrators of a running service.";
      main.appendChild(el("div", { class: "wrap pt-main" }, [el("div", { class: "status none" }, [
        el("h2", {}, ["Nothing to set on the recorded example"]),
        el("p", {}, ["Administrator settings apply to a running service. This page shows a recorded example, so there is nothing here to change."]),
        el("div", { class: "btn-row" }, [el("a", { class: "btn", href: "results.html" }, ["See the recorded results"])])])]));
    }
  }

  function homeCard() {
    var fig = $("homecard"); if (!fig) return;
    var r = (M.results || []).filter(function (x) { return x.fit === "High"; })[0] || (M.results || [])[0];
    var c = r && (r.citations || []).filter(function (x) { return x.source_id !== "researcher-profile"; })[0];
    if (!r || !c) return;
    clear(fig);
    fig.appendChild(el("div", { class: "excerpt" }, [
      el("p", { class: "src" }, ["From the announcement \u00b7 " + r.number + " \u00b7 recorded example"]),
      el("p", {}, [el("mark", {}, [c.quote])])]));
    fig.appendChild(el("p", { class: "because", "aria-hidden": "true" }, ["The highlighted sentence is what the rating rests on"]));
    fig.appendChild(el("div", { class: "result r-" + r.fit }, [
      el("p", { class: "h3like" }, [r.title]),
      el("div", { class: "badges" }, [fitBadge(r), eligBadge(r.eligibility)]),
      el("div", { class: "yourcheck" }, [el("strong", {}, ["Your check: "]), document.createTextNode(yourCheck(r))])]));
    fig.appendChild(el("figcaption", {}, ["A real result from the recorded example (fictional researcher). Every result shows its rating, the sentence it rests on, and what a person checks next."]));
    fig.hidden = false;
  }

  function recordedResultsExtras() {
    var anchor = $("shown");
    var elig = (M.results || []).filter(function (r) { return r.eligibility === "Needs verification"; }).length;
    if (elig && elig === (M.results || []).filter(function (r) { return r.fit; }).length && anchor) {
      anchor.parentNode.insertBefore(el("div", { class: "notice mb2" }, [el("strong", {}, ["Why every row says “Needs verification”. "]),
        document.createTextNode("Eligibility shows Needs verification when the notice does not say whether this researcher’s institution qualifies. " +
          "SIGNAL never guesses it; a person checks the sponsor page. Here, the one High rating holds only once that check is done.")]), anchor);
    }
    var c = M.counters || {}, cv = $("counters");
    if (cv && c.in_horizon != null) {
      cv.insertBefore(el("p", { class: "countline" }, [el("strong", {}, ["Coverage. "]), document.createTextNode(c.judged + " of " + c.in_horizon +
        " announcements closing in the window were checked; " + (c.not_judged_due_to_cap || 0) + " more were not checked (cap) and " +
        (c.no_term_overlap || 0) + " share no words with the research areas.")]), cv.firstChild);
    }
    var ex = M.excluded || [], list = $("list");
    if (ex.length && list) {
      var ul = el("ul", { class: "rule-list" });
      ex.forEach(function (x) {
        var t = /^https:\/\/www\.grants\.gov\//.test(x.url || "")
          ? el("a", { href: x.url, rel: "noopener noreferrer", target: "_blank" }, [x.title]) : document.createTextNode(String(x.title));
        var li = el("li", {}, [t, document.createTextNode(" · "), el("span", { class: "mono" }, [x.number || ""])]);
        (x.reasons || []).forEach(function (why) { li.appendChild(el("div", { class: "hint" }, [why])); });
        ul.appendChild(li);
      });
      var d = el("details", { class: "evidence mt2" }, [el("summary", {}, ["Rated Excluded (" + ex.length + ")"]),
        el("div", { class: "body" }, [el("p", { class: "hint" }, ["These were checked and set aside. The rule text is shown with each."]), ul])]);
      list.parentNode.insertBefore(d, list.nextSibling);
    }
  }

  function recordedInputPanel(form) {
    var R = M.recorded_run || {}, inp = R.input_sent || {}, pr = inp.profile || {}, st = M.settings || {};
    var hint = $("runhint"); if (hint) hint.parentNode.removeChild(hint);
    var rest = form.parentNode;
    var lead = document.querySelector(".pagehead .lead");
    if (lead) lead.textContent = "This is the input that produced the recorded example. It is shown read-only and cannot be changed or sent.";
    function list(items) { return el("ul", { class: "rule-list" }, (items || []).map(function (t) { return el("li", {}, [t]); })); }
    var kv = el("dl", { class: "kv" });
    [["Researcher", (M.profile || {}).investigator], ["Institution", (M.profile || {}).institution], ["Career stage", pr.career_stage],
     ["Question put to the model", inp.question], ["Deadline window", st.horizon_months ? "Next " + st.horizon_months + " months" : null],
     ["Funders", (st.funder_types || []).join(", ")], ["Opportunities checked at most", inp.max_judgments]].forEach(function (p) {
      if (p[1] == null || p[1] === "") return;
      kv.appendChild(el("dt", {}, [p[0]])); kv.appendChild(el("dd", {}, [String(p[1])]));
    });
    var card = el("div", { class: "card" }, [el("h2", {}, ["Input used for this recording"]), kv,
      el("h3", { class: "mt2" }, ["Research areas"]), list(pr.lanes), el("h3", { class: "mt2" }, ["Positioning rules"]), list(pr.positioning_rules)]);
    var btns = el("div", { class: "btn-row mt2" }, [el("a", { class: "btn", href: "results.html" }, ["See the recorded results"])]);
    var note;
    if (LIVE) {
      var out = el("a", { class: "btn ghost", href: "match.html" }, ["Leave the recorded example and search live"]);
      out.addEventListener("click", function () { setMode(null); });
      btns.appendChild(out);
      note = "Live searches are limited in this pilot. This example was made earlier by the same engine.";
    } else note = "Live searches are not available on this site. This example was made earlier by the same engine.";
    var panel = el("div", {}, [card, el("p", { class: "hint mt2" }, [note]), btns]);
    rest.insertBefore(panel, form); rest.removeChild(form);   // the live form is removed, not just hidden
  }

  function chooseRecorded() { setMode("recorded"); window.location.href = "results.html"; }
  function offerRecorded() {
    var after = $("runhint"); if (!after) return;
    var b = el("button", { class: "btn ghost s", type: "button" }, ["See the recorded example"]);
    b.addEventListener("click", chooseRecorded);
    after.parentNode.insertBefore(el("div", { class: "mt1" }, [
      el("p", { class: "hint" }, ["Live searches are limited in this pilot. If one is not available, you can look at a recorded example instead."]), b]), after.nextSibling);
  }
  function offerInError() {
    var b = el("button", { class: "btn ghost", type: "button" }, ["See the recorded example"]);
    b.addEventListener("click", chooseRecorded);
    $("runerror").appendChild(el("div", { class: "btn-row" }, [b]));
  }

  /* ---------------------------------------------------------------- pages */
  var pages = {
    results: function () {
      var all = M.results.filter(function (r) { return r.fit; });
      var list = $("list"), chips = $("chips");
      var controls = { q: $("q"), fit: $("f-fit"), elig: $("f-elig"), status: $("f-status"), sponsor: $("f-sponsor") };

      /* fill the selects from the run itself, so a filter never offers a value with no results */
      function fill(sel, values) {
        values.forEach(function (v) { sel.appendChild(el("option", { value: v }, [v])); });
      }
      fill(controls.status, [...new Set(all.map(function (r) { return r.status; }).filter(Boolean))].sort());
      fill(controls.sponsor, [...new Set(all.map(function (r) { return r.sponsor; }).filter(Boolean))].sort());

      $("count").textContent = (all.length && RMODE)
        ? "Recorded example: " + all.length + " opportunities rated, from " + M.counters.judged + " checked. Others were not checked or were rated Excluded; see the counts below."
        : all.length
        ? "Showing " + all.length + " of " + M.counters.judged + " opportunities checked. Others were not checked or were rated Excluded; see the counts below."
        : (M.counters.judged === 0 ? "Nothing was checked in this run." : "Nothing was rated at or above your setting in this run.");
      if (all.length && M.hidden_by_filter) $("count").textContent += " " + M.hidden_by_filter + " more rated below your setting are hidden.";
      if (M.run_id && $("runid")) { $("runid").appendChild(document.createTextNode("Run ID: ")); $("runid").appendChild(el("span", { class: "mono" }, [M.run_id])); }
      var when = M.screened_at || M.retrieved_at;
      if ($("screened") && when) $("screened").textContent = (RMODE ? "Recorded " : isLive() ? "Checked " : "Sample search, checked ") + (RMODE ? recStamp(when) : new Date(when).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" }));
      provenance();
      if (RMODE) recordedResultsExtras();
      $("counters").appendChild(counters(M.counters));
      var f = $("failures");
      (M.source_failures || []).forEach(function (x) { f.appendChild(el("li", {}, [x.source_id + " \u2014 " + x.error])); });
      $("failcount").textContent = (M.source_failures || []).length;

      function matches(r) {
        var term = controls.q.value.trim().toLowerCase();
        if (term) {
          var hay = [r.title, r.sponsor, r.number, r.rationale].join(" ").toLowerCase();
          if (hay.indexOf(term) < 0) return false;
        }
        if (controls.fit.value && r.fit !== controls.fit.value) return false;
        if (controls.elig.value && r.eligibility !== controls.elig.value) return false;
        if (controls.status.value && r.status !== controls.status.value) return false;
        if (controls.sponsor.value && r.sponsor !== controls.sponsor.value) return false;
        return true;
      }

      function chip(label, reset) {
        var c = el("span", { class: "chip" }, [label]);
        var b = el("button", { type: "button", "aria-label": "Remove filter: " + label }, ["\u00d7"]);
        b.onclick = function () { reset(); render(); };
        c.appendChild(b); chips.appendChild(c);
      }

      function render() {
        clear(chips); clear(list);
        if (controls.q.value.trim()) chip('Search: "' + controls.q.value.trim() + '"', function () { controls.q.value = ""; });
        [["fit", "Fit"], ["elig", "Eligibility"], ["status", "Status"], ["sponsor", ""]].forEach(function (p) {
          var c = controls[p[0]];
          if (c.value) chip((p[1] ? p[1] + ": " : "") + c.value, function () { c.value = ""; });
        });
        if (chips.children.length > 1) {
          var b = el("button", { class: "clear-all", type: "button" }, ["Clear all filters"]);
          b.onclick = function () {
            Object.keys(controls).forEach(function (k) { controls[k].value = ""; });
            render(); controls.q.focus();
          };
          chips.appendChild(b);
        }
        if (!all.length) {
          $("shown").textContent = "No results to show.";
          var more = M.hidden_by_filter ? [el("p", {}, [M.hidden_by_filter + " more were rated below your \u201cShow results rated\u201d setting and are hidden. Choose \u201cAll\u201d on the Find funding page to see them."])] : [];
          list.appendChild(el("div", { class: "status none" }, [
            el("h2", {}, [M.counters.judged === 0 ? "Nothing was checked" : "Nothing rated at or above your setting"]),
            el("p", {}, [(M.counters.judged === 0 && M.counters.no_term_overlap) ? "Nothing was checked: " + M.counters.no_term_overlap + " announcements share no words with the research areas. Try the words funders use for this field." : "SIGNAL checked " + M.counters.judged + " opportunities. Each was ruled out (for example by a stated restriction), had no supported connection to the research areas, or was rated below your minimum. Ruled-out items are kept in the run log."])
          ].concat(more).concat([
            el("p", {}, [el("strong", {}, ["You could try:"])]),
            el("ul", {}, [el("li", {}, ["A longer deadline window."]), el("li", {}, ["Research areas written in more detail, in the researcher\u2019s own words."]),
                          el("li", {}, ["A keyword search instead of a researcher."])]),
            el("div", { class: "btn-row" }, [el("a", { class: "btn", href: "match.html" }, ["Change the run"])])])));
          return;
        }
        var shown = all.filter(matches);
        $("shown").textContent = shown.length === all.length
          ? "Showing all " + all.length + " results, highest fit first."
          : "Showing " + shown.length + " of " + all.length + " results.";
        if (!shown.length) {
          list.appendChild(el("div", { class: "empty" }, [
            el("strong", {}, ["No results match these filters"]),
            el("span", {}, ["Every checked opportunity is still in this search. Remove a filter above to see it."])]));
          return;
        }
        shown.forEach(function (r) { list.appendChild(resultCard(r)); });
      }

      Object.keys(controls).forEach(function (k) {
        controls[k].addEventListener(k === "q" ? "input" : "change", render);
      });
      render();
    },

    calendar: function () {
      provenance(); downloads();
      var groups = { Fixed: [], Rolling: [], Watch: [] };
      M.results.filter(function (r) { return r.fit; }).forEach(function (r) {
        (r.status === "Rolling" ? groups.Rolling : r.status === "Watch" ? groups.Watch : groups.Fixed).push(r);
      });
      var lead = (M.settings && M.settings.lead_time_days) || 14;
      var cols = ["Opportunity", "Fit", "Sponsor deadline", "Internal deadline", "Eligibility", "Recommended next action",
                  "Status & conditions", "Sponsor", "NOFO / Call ID", "Days to sponsor deadline", "Amount / scale", "Official source"];
      var host = $("tables");
      if (!groups.Fixed.length && !groups.Rolling.length && !groups.Watch.length) {
        $("scrollhint").hidden = true;
        host.appendChild(el("div", { class: "status none mb3" }, [el("h2", {}, ["Nothing to put on the calendar"]),
          el("p", {}, ["This run produced no rated opportunities, so there are no dates to show."]),
          el("div", { class: "btn-row" }, [el("a", { class: "btn", href: "match.html" }, ["Change the run"])])]));
      }
      Object.keys(groups).forEach(function (g) {
        if (!groups[g].length) return;
        var cap = g === "Fixed" ? "Fixed deadlines" : g === "Rolling" ? "Rolling or anytime (no invented deadline)" : "Watch: dates not yet announced";
        var scroll = el("div", { class: "table-scroll mb3", tabindex: "0", role: "region", "aria-label": cap + " (table, scrolls sideways)" }), t = el("table");
        t.appendChild(el("caption", {}, [cap]));
        var hr = el("tr"); cols.forEach(function (c) { hr.appendChild(el("th", { scope: "col" }, [c])); });
        t.appendChild(el("thead", {}, [hr]));
        var tb = el("tbody");
        groups[g].forEach(function (r) {
          var idl = dateLong(r.internal_deadline);
          var passed = r.internal_deadline && (RMODE ? daysUntil(r.internal_deadline) < 0 : (r.days_to_deadline != null && (r.days_to_deadline - lead) < 0));
          var cells = [
            [r.title], [fitBadge(r)],
            [orNot(dateLong(r.close_date), "Rolling / not stated")],
            [passed ? el("span", {}, [idl + " ", el("span", { class: "passed" }, ["(passed)"])]) : orNot(idl, "Not available: no sponsor date")],
            [el("span", {}, [r.eligibility])],
            [r.next_action || (r.eligibility === "Needs verification" ? "Verify eligibility on the sponsor page before any outreach."
              : r.status === "Rolling" ? "Contact the program officer to confirm topic fit."
              : "Confirm the deadline, then prepare outreach.")],
            [(function () {
              var d = el("span", {}, [r.status || "Open"]);
              (r.flags || []).concat(r.currency_flags || []).forEach(function (f) {
                d.appendChild(document.createTextNode(" ")); d.appendChild(el("span", { class: "flag info" }, [f]));
              });
              return d;
            })()],
            [r.sponsor], [el("span", { class: "mono" }, [r.number])],
            [r.days_to_deadline == null ? el("span", { class: "nostate" }, ["\u2014"]) : (r.passed || r.days_to_deadline < 0) ? el("span", { class: "passed" }, ["Passed"]) : document.createTextNode(String(r.days_to_deadline))],
            [r.amount ? document.createTextNode(r.amount) : orNot(r.award_ceiling ? "up to " + money(r.award_ceiling) : null, "Not specified")],
            [el("a", { href: r.url, rel: "noopener noreferrer", target: "_blank", "aria-label": "Open announcement " + r.number + " (opens in a new tab)" }, ["Open announcement"])]
          ];
          var tr = el("tr");
          cells.forEach(function (c, i) { tr.appendChild(el("td", { "data-label": cols[i] }, c)); });
          tb.appendChild(tr);
        });
        t.appendChild(tb); scroll.appendChild(t); host.appendChild(scroll);
      });

      var decide = M.results.filter(function (r) {
        return (r.fit === "High" || r.fit === "Medium") && r.days_to_deadline != null &&
               !r.passed && r.days_to_deadline >= 0 && r.days_to_deadline < lead && r.status !== "Watch";
      });
      if (decide.length) {
        $("decide").hidden = false;
        var dl = $("decidelist");
        decide.forEach(function (r) {
          dl.appendChild(el("li", {}, [
            el("strong", {}, [r.title]), document.createTextNode(" \u2014 " + r.days_to_deadline +
              " day" + (r.days_to_deadline === 1 ? "" : "s") + " to the sponsor deadline, closer than your " +
              lead + "-day internal deadline. "), fitBadge(r)]));
        });
      }
      var soon = M.results.filter(function (r) { return r.fit && !r.passed && r.days_to_deadline != null && r.days_to_deadline >= 0 && r.days_to_deadline <= 45; });
      var ul = $("soon");
      soon.forEach(function (r) {
        ul.appendChild(el("li", {}, [r.title + " \u2014 ", el("strong", {}, [r.days_to_deadline + " days"]),
          document.createTextNode(" (internal deadline " + (dateLong(r.internal_deadline) || "not set") + ") "), fitBadge(r)]));
      });
      if (!soon.length) ul.appendChild(el("li", { class: "nostate" }, ["Nothing inside 45 days."]));
      var top = $("top5");
      var top5 = M.results.filter(function (r) { return r.fit; }).slice(0, 5);
      top5.forEach(function (r) { top.appendChild(el("li", {}, [r.title + " ", fitBadge(r)])); });
      if (!top5.length) top.appendChild(el("li", { class: "nostate" }, ["Nothing was rated in this run."]));
      else if (top5.length < 5) top.appendChild(el("li", { class: "nostate" }, ["Only " + top5.length + " opportunit" + (top5.length === 1 ? "y was" : "ies were") + " rated in this run."]));
      var watch = $("watchlist");
      groups.Watch.concat(groups.Rolling).forEach(function (r) {
        watch.appendChild(el("li", {}, [r.title + " — " + (r.status === "Rolling" ? "rolling; confirm topic" : "next cycle not announced")]));
      });
      if (!groups.Watch.length && !groups.Rolling.length) watch.appendChild(el("li", { class: "nostate" }, ["Nothing on watch."]));
    },

    review: function () {
      var surfaced = M.results.filter(function (r) { return r.fit === "High" || r.fit === "Medium"; });
      var held = M.results.filter(function (r) { return r.fit === "Low"; });
      var excluded = M.results.filter(function (r) { return !r.fit; });
      function fill(id, rows, note) {
        var ul = $(id);
        rows.forEach(function (r) { ul.appendChild(el("li", {}, [r.title + " ", fitBadge(r)])); });
        if (!rows.length) ul.appendChild(el("li", { class: "nostate" }, [note]));
      }
      fill("surfaced", surfaced, "Nothing would be sent.");
      fill("held", held, "Nothing held back.");
      if (RMODE) {
        var ex = $("excluded");
        (M.excluded || []).forEach(function (x) { ex.appendChild(el("li", {}, [x.title])); });
        if (!(M.excluded || []).length) ex.appendChild(el("li", { class: "nostate" }, ["Nothing excluded."]));
      } else fill("excluded", excluded, LIVE ? "Ruled-out items are kept in the run log, not listed here." : "Nothing excluded.");
      $("draft").value = !surfaced.length ? "" :
        "DRAFT. Review and edit before sending.\n\n" +
        "Subject: [DRAFT] Funding opportunities for your consideration (" + surfaced.length + " to review)\n\n" +
        greeting() + "\n\n" +
        "I checked current federal funding opportunities against your research areas. " +
        surfaced.length + " may be worth a look:\n\n" +
        surfaced.map(function (r) {
          return "• " + r.title + " (" + r.sponsor + ", " + r.number + ")\n" +
                 "  Deadline: " + (dateLong(r.close_date) || "rolling / not stated") +
                 "  |  Internal deadline: " + (dateLong(r.internal_deadline) || "to be set") + "\n" +
                 "  Why it may fit: " + r.rationale + "\n" +
                 "  Eligibility: " + r.eligibility + "\n  " + r.url;
        }).join("\n\n") +
        "\n\nThis is an informational alert, not a recommendation to apply. Please verify every deadline and " +
        "eligibility requirement on the sponsor page before committing time.\n\n[Your name]";

      var tick = $("confirm"), to = $("to"), send = $("send");
      if (!surfaced.length) {
        $("noalert").hidden = false; $("draft").hidden = true; $("sendform").hidden = true; $("draft").disabled = true; $("draft").setAttribute("aria-label", "Draft alert text (empty)");
        tick.disabled = true; to.disabled = true;
      }
      function sync() { send.disabled = !(surfaced.length && tick.checked && /[^@\s]+@[^@\s]+\.[^@\s]+/.test(to.value)); }
      tick.addEventListener("change", sync); to.addEventListener("input", sync); sync();
      $("sendform").addEventListener("submit", function (e) {
        e.preventDefault();
        if (RMODE) {
          $("sent").textContent = "Test mode: nothing was sent and nothing was saved. Recipient " + to.value + " was not contacted.";
          $("sent").hidden = false; return;
        }
        if (isLive()) {
          send.disabled = true;
          api("/api/runs/" + encodeURIComponent(M.run_id) + "/email",
              { method: "POST", body: { draft: $("draft").value, recipient: to.value, confirmed: tick.checked } })
            .then(function (r) { $("sent").textContent = r.message + " Recipient " + to.value + " is recorded in the run log."; },
                  function (err) { $("sent").textContent = "Not sent: " + err.message; })
            .then(function () { $("sent").hidden = false; sync(); });
          return;
        }
        $("sent").textContent = "Logged in test mode at " + new Date().toLocaleTimeString() +
          ". Recipient " + to.value + " recorded in the run log. No email was sent.";
        $("sent").hidden = false;
      });
    },

    match: function () {
      var form = $("runform");
      if (RMODE) { recordedInputPanel(form); return; }
      if (isLive()) offerRecorded();
      if (LIVE) {
        /* real runs start from an empty form: the pre-filled researcher is fictional sample content */
        ["pi-name", "lanes", "rules"].forEach(function (id) { var f = $(id); if (f) f.value = ""; });
        var unit = document.querySelector('[data-panel="p-unit"]');
        if (unit) {
          unit.disabled = true;
          unit.closest("label").appendChild(el("span", { class: "hint" }, [" Coming later."]));
        }
      }
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        if (LIVE) liveRun(form); else sampleRun();
      });
      document.querySelectorAll("[data-panel]").forEach(function (radio) {
        radio.addEventListener("change", function () {
          clearInvalid(); $("runerror").hidden = true;
          document.querySelectorAll(".input-panel").forEach(function (p) { p.hidden = true; });
          var panel = $(radio.getAttribute("data-panel"));
          if (panel) panel.hidden = false;
        });
      });
    }
  };

  function heroVideo() {
    var v = $("hv"), b = $("vb");
    if (!v || !b) return;
    var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function label(playing) {
      b.textContent = playing ? "Pause video" : "Play video";
      b.setAttribute("aria-pressed", playing ? "false" : "true");
    }
    if (!still) { var p = v.play(); if (p && p.catch) p.catch(function () { label(false); }); }
    label(!still);
    b.addEventListener("click", function () {
      if (v.paused) { v.play(); label(true); } else { v.pause(); label(false); }
    });
  }

  /* press / to jump to search on Results */
  document.addEventListener("keydown", function (e) {
    var q = $("q"), t = e.target && e.target.tagName;
    if (e.key === "/" && q && !e.metaKey && !e.ctrlKey && t !== "INPUT" && t !== "TEXTAREA" && t !== "SELECT") { e.preventDefault(); q.focus(); }
  });
  document.addEventListener("DOMContentLoaded", function () {
    heroVideo();
    var p = document.body.getAttribute("data-page");
    function runPage() {
      if (RMODE) { recordedChrome(p); if (p === "home") homeCard(); }
      if (RMODE && p === "settings") return;
      if (pages[p]) pages[p]();
    }
    if (!LIVE || recordedChosen()) {
      /* a deploy without a backend, or a visitor who chose the recorded example: no request to /api/ is made */
      loadRecorded().then(function (m) { M = m; RMODE = true; prepRecorded(); runPage(); },
        function (e) { noRun(e.message + " Reload the page to try again."); });
      return;
    }
    if (LIVE) { liveBanner(); document.querySelectorAll(".sample-only").forEach(function (n) { n.hidden = true; }); }
    if (p === "results" || p === "calendar" || p === "review") {
      loadLive().then(function (m) {
        if (!m) { noRun(); return; }
        M = m; pages[p]();
      }, function (e) { noRun("This run could not be loaded (" + e.message + "). Start a new match."); });
      return;
    }
    runPage();
  });
})();
