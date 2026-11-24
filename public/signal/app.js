/* Shared rendering for the FORGE SIGNAL interface.
   Reads window.MOCK today; the same functions take the API response once wired.
   All text is inserted as text nodes, never as HTML: opportunity text is sponsor-supplied. */
(function () {
  "use strict";
  var M = window.MOCK || {};

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

  function citationBlock(c) {
    var src = c.source_id === "researcher-profile"
      ? el("span", {}, ["Researcher profile, supplied for this run"])
      : el("a", { href: c.source_id, rel: "noopener noreferrer", target: "_blank" }, ["Official source"]);
    return el("div", { class: "quote" }, [
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
        ["Chosen for screening because these terms appear in both the profile and the announcement: " +
         r.prefilter_shared_terms.join(", ") + ". That ranking only controls cost; it is not the fit judgment."]));
    }
    d.appendChild(body);
    return d;
  }

  function resultCard(r) {
    var card = el("article", { class: "result r-" + (r.fit || "Excluded") });
    card.appendChild(el("h3", {}, [el("a", { href: r.url, rel: "noopener noreferrer", target: "_blank" }, [r.title])]));
    var meta = el("div", { class: "meta" }, [r.sponsor, el("span", { class: "sep" }, ["|"]),
      el("span", { class: "mono" }, [r.number]), el("span", { class: "sep" }, ["|"])]);
    meta.appendChild(document.createTextNode("Sponsor deadline: "));
    meta.appendChild(orNot(dateLong(r.close_date), "Not stated"));
    if (r.days_to_deadline != null) meta.appendChild(document.createTextNode(" (" + r.days_to_deadline + " days)"));
    card.appendChild(meta);

    var badges = el("div", { class: "badges" }, [fitBadge(r), eligBadge(r.eligibility)]);
    if (r.status) badges.appendChild(el("span", { class: "flag info" }, ["Status: " + r.status]));
    (r.flags || []).forEach(function (f) { badges.appendChild(el("span", { class: "flag info" }, [f])); });
    (r.currency_flags || []).forEach(function (f) { badges.appendChild(el("span", { class: "flag" }, ["⚠ " + f])); });
    card.appendChild(badges);

    card.appendChild(el("p", {}, [r.rationale]));
    (r.citations || []).forEach(function (c) { card.appendChild(citationBlock(c)); });
    if (!(r.citations || []).length) {
      card.appendChild(el("div", { class: "quote" }, [el("q", {}, ["No explicit support found in the provided sources."])]));
    }
    card.appendChild(howCalculated(r));
    return card;
  }

  function counters(c) {
    var wrap = el("div", { class: "counters" });
    [["Listed", c.opportunities_listed], ["In deadline window", c.in_horizon], ["Full text read", c.details_fetched],
     ["Screened", c.judged], ["Not screened (cap)", c.not_judged_due_to_cap], ["Source failures", c.source_failures]
    ].forEach(function (p) {
      wrap.appendChild(el("div", {}, [el("span", { class: "n" }, [String(p[1])]), el("span", { class: "l" }, [p[0]])]));
    });
    return wrap;
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

      $("count").textContent = all.length + " of " + M.counters.judged +
        " screened opportunities are shown. Excluded items are kept in the run log, not here.";
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
        var shown = all.filter(matches);
        $("shown").textContent = shown.length === all.length
          ? "Showing all " + all.length + " results, highest fit first."
          : "Showing " + shown.length + " of " + all.length + " results.";
        if (!shown.length) {
          list.appendChild(el("div", { class: "empty" }, [
            el("strong", {}, ["No results match these filters"]),
            el("span", {}, ["Every screened opportunity is still in the run. Remove a filter above to see it."])]));
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
      var groups = { Fixed: [], Rolling: [], Watch: [] };
      M.results.filter(function (r) { return r.fit; }).forEach(function (r) {
        (r.status === "Rolling" ? groups.Rolling : r.status === "Watch" ? groups.Watch : groups.Fixed).push(r);
      });
      var cols = ["Opportunity", "Sponsor", "NOFO / Call ID", "Fit", "Status & conditions", "Sponsor deadline",
                  "Internal deadline", "Days left", "Amount / scale", "Eligibility", "Recommended next action", "Official source"];
      var host = $("tables");
      Object.keys(groups).forEach(function (g) {
        if (!groups[g].length) return;
        var scroll = el("div", { class: "table-scroll", style: "margin-bottom:22px" }), t = el("table");
        t.appendChild(el("caption", {}, [g === "Fixed" ? "Fixed deadlines" : g === "Rolling" ? "Rolling or anytime (no invented deadline)" : "Watch: dates not yet announced"]));
        var hr = el("tr"); cols.forEach(function (c) { hr.appendChild(el("th", { scope: "col" }, [c])); });
        t.appendChild(el("thead", {}, [hr]));
        var tb = el("tbody");
        groups[g].forEach(function (r) {
          var cells = [
            [r.title], [r.sponsor], [el("span", { class: "mono" }, [r.number])], [fitBadge(r)],
            [(function () {
              var d = el("span", {}, [r.status || "Open"]);
              (r.flags || []).concat(r.currency_flags || []).forEach(function (f) {
                d.appendChild(document.createTextNode(" ")); d.appendChild(el("span", { class: "flag info" }, [f]));
              });
              return d;
            })()],
            [orNot(dateLong(r.close_date), "Rolling / not stated")],
            [orNot(dateLong(r.internal_deadline), "Set once the sponsor date is known")],
            [r.days_to_deadline == null ? el("span", { class: "nostate" }, ["—"]) : document.createTextNode(String(r.days_to_deadline))],
            [orNot(r.award_ceiling ? "up to " + money(r.award_ceiling) : null, "Not specified")],
            [el("span", {}, [r.eligibility])],
            [r.eligibility === "Needs verification" ? "Verify eligibility on the sponsor page before any outreach."
              : r.status === "Rolling" ? "Contact the program officer to confirm topic fit."
              : "Confirm the deadline, then prepare outreach."],
            [el("a", { href: r.url, rel: "noopener noreferrer", target: "_blank" }, ["Open announcement"])]
          ];
          var tr = el("tr");
          cells.forEach(function (c, i) { tr.appendChild(el("td", { "data-label": cols[i] }, c)); });
          tb.appendChild(tr);
        });
        t.appendChild(tb); scroll.appendChild(t); host.appendChild(scroll);
      });

      var lead = (M.settings && M.settings.lead_time_days) || 14;
      var decide = M.results.filter(function (r) {
        return (r.fit === "High" || r.fit === "Medium") && r.days_to_deadline != null &&
               r.days_to_deadline >= 0 && r.days_to_deadline < lead && r.status !== "Watch";
      });
      if (decide.length) {
        $("decide").hidden = false;
        var dl = $("decidelist");
        decide.forEach(function (r) {
          dl.appendChild(el("li", {}, [
            el("strong", {}, [r.title]), document.createTextNode(" \u2014 " + r.days_to_deadline +
              " day" + (r.days_to_deadline === 1 ? "" : "s") + " to the sponsor deadline, inside the " +
              lead + "-day lead time. "), fitBadge(r)]));
        });
      }
      var soon = M.results.filter(function (r) { return r.fit && r.days_to_deadline != null && r.days_to_deadline <= 45; });
      var ul = $("soon");
      soon.forEach(function (r) {
        ul.appendChild(el("li", {}, [r.title + " — ", el("strong", {}, [r.days_to_deadline + " days"]),
          document.createTextNode(" (internal deadline " + (dateLong(r.internal_deadline) || "not set") + ")")]));
      });
      if (!soon.length) ul.appendChild(el("li", { class: "nostate" }, ["Nothing inside 45 days."]));
      var top = $("top5");
      M.results.filter(function (r) { return r.fit; }).slice(0, 5).forEach(function (r) {
        top.appendChild(el("li", {}, [r.title + " ", fitBadge(r)]));
      });
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
      fill("excluded", excluded, "Nothing excluded.");
      $("draft").value =
        "Subject: Funding opportunities for your consideration (" + surfaced.length + " to review)\n\n" +
        "Dear Dr. " + M.profile.investigator.split(" ")[1] + ",\n\n" +
        "Research Development screened current federal opportunities against your public profile. " +
        surfaced.length + " may be worth a look:\n\n" +
        surfaced.map(function (r) {
          return "• " + r.title + " (" + r.sponsor + ", " + r.number + ")\n" +
                 "  Deadline: " + (dateLong(r.close_date) || "rolling / not stated") +
                 "  |  Internal deadline: " + (dateLong(r.internal_deadline) || "to be set") + "\n" +
                 "  Why it may fit: " + r.rationale + "\n" +
                 "  Eligibility: " + r.eligibility + "\n  " + r.url;
        }).join("\n\n") +
        "\n\nThis is an informational alert, not a recommendation to apply. Please verify every deadline and " +
        "eligibility requirement on the sponsor page before committing time.\n\n[Your name]\nResearch Development";

      var tick = $("confirm"), to = $("to"), send = $("send");
      function sync() { send.disabled = !(tick.checked && /[^@\s]+@[^@\s]+\.[^@\s]+/.test(to.value)); }
      tick.addEventListener("change", sync); to.addEventListener("input", sync); sync();
      $("sendform").addEventListener("submit", function (e) {
        e.preventDefault();
        $("sent").textContent = "Logged in dummy mode at " + new Date().toLocaleTimeString() +
          ". Recipient " + to.value + " recorded in the run log. No email was sent.";
        $("sent").hidden = false;
      });
    },

    match: function () {
      var form = $("runform"), steps = $("progress"), done = $("done");
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        steps.hidden = false; done.hidden = true;
        var items = steps.querySelectorAll("li"), i = 0;
        items.forEach(function (li) { li.className = "todo"; });
        (function tick() {
          if (i > 0) items[i - 1].className = "done";
          if (i < items.length) { items[i].className = "now"; i++; setTimeout(tick, 650); }
          else { done.hidden = false; done.focus(); }
        })();
      });
      document.querySelectorAll("[data-panel]").forEach(function (radio) {
        radio.addEventListener("change", function () {
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

  document.addEventListener("DOMContentLoaded", function () {
    heroVideo();
    var p = document.body.getAttribute("data-page");
    if (pages[p]) pages[p]();
  });
})();
