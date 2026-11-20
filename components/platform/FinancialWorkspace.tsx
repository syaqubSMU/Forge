"use client";
import { useId, useMemo, useState } from "react";
import { awards, derive, totals, money, moneyShort, pct, dateLabel, AS_OF_LABEL, categories, commitmentTypes, splitBy, reconRows, trendMonths, trendPosted, trendProjected, trendProjectedMonths, type Award } from "@/lib/synthetic";
import { site } from "@/lib/content";

const weight = { over: 4, review: 2, ends: 2, under: 1 } as const;
const flagClass = { over: "badge badge--coral", under: "badge badge--blue", ends: "badge", review: "badge badge--coral" } as const;

function Bar({ a }: { a: Award }) {
  const d = derive(a);
  return (
    <div className="sbar" role="img" aria-label={`Posted ${pct(a.actual / a.budget)}, committed ${pct(a.committed / a.budget)}, available ${pct(d.available / a.budget)} of budget`}>
      <i className="act" style={{ width: `${(a.actual / a.budget) * 100}%` }} /><i className="com" style={{ width: `${(a.committed / a.budget) * 100}%` }} />
    </div>
  );
}
const Legend = () => (<div className="legend"><span><i className="act" />Posted expenditures</span><span><i className="com" />Outstanding commitments</span><span><i className="avl" />Available balance</span></div>);

function Kpis({ list, compact }: { list: Award[]; compact?: boolean }) {
  const t = totals(list);
  const items = [
    { l: "Total award budget", v: money(t.budget) }, { l: "Actual expenditures (posted)", v: money(t.actual) }, { l: "Outstanding commitments", v: money(t.committed) },
    { l: "Available balance", v: money(t.available), s: "Budget − actual − commitments", key: true }, { l: "Projected remaining balance", v: money(t.projected), s: "Estimate at award end", proj: true }, { l: "Budget utilization", v: pct(t.utilization), s: "Posted + committed" },
  ].slice(0, compact ? 4 : 6);
  return (
    <div className={`kpis ${compact ? "kpis--compact" : ""}`}>
      {items.map((k) => (<div key={k.l} className={`kpi ${k.key ? "kpi--key" : ""}`}><span>{k.l}</span><b>{k.v}</b>{k.s && <small>{k.s}</small>}</div>))}
    </div>
  );
}

function Trend() {
  const W = 520, H = 170, pad = { l: 34, r: 8, t: 10, b: 24 }, n = trendPosted.length + trendProjected.length, max = 450;
  const bw = (W - pad.l - pad.r) / n, y = (v: number) => pad.t + (H - pad.t - pad.b) * (1 - v / max);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Monthly posted spending for the last 12 months with a 3-month projection" style={{ width: "100%", height: "auto" }}>
      {[0, 150, 300, 450].map((v) => (<g key={v}><line x1={pad.l} x2={W - pad.r} y1={y(v)} y2={y(v)} stroke="#E3EAF0" /><text x={pad.l - 6} y={y(v) + 3} textAnchor="end" fontSize="9" fill="#566878">{v === 0 ? "0" : `$${v}K`}</text></g>))}
      {trendPosted.map((v, i) => (<g key={i}><rect x={pad.l + i * bw + 3} y={y(v)} width={bw - 6} height={y(0) - y(v)} rx="2" fill="#244B70" /><text x={pad.l + i * bw + bw / 2} y={H - 8} textAnchor="middle" fontSize="9" fill="#566878">{trendMonths[i]}</text></g>))}
      {trendProjected.map((v, i) => { const j = trendPosted.length + i; return (<g key={`p${i}`}><rect x={pad.l + j * bw + 3} y={y(v)} width={bw - 6} height={y(0) - y(v)} rx="2" fill="#fff" stroke="#244B70" strokeWidth="1.5" strokeDasharray="3 2" /><text x={pad.l + j * bw + bw / 2} y={H - 8} textAnchor="middle" fontSize="9" fill="#566878">{trendProjectedMonths[i]}</text></g>); })}
    </svg>
  );
}

function Attention({ list, limit }: { list: Award[]; limit?: number }) {
  const rows = list.map((a) => ({ a, d: derive(a) })).filter((r) => r.d.flags.length).sort((x, y) => y.d.flags.reduce((t, f) => t + weight[f.kind], 0) - x.d.flags.reduce((t, f) => t + weight[f.kind], 0)).slice(0, limit ?? 99);
  return (
    <ul className="alist">
      {rows.map(({ a, d }) => (<li key={a.id}><div><b>{a.title}</b><small>{a.id} · {a.dept}</small></div><div style={{ display: "flex", gap: 6, flexWrap: "wrap", justifyContent: "flex-end" }}>{d.flags.map((f) => <span key={f.text} className={flagClass[f.kind]}>{f.text}</span>)}</div></li>))}
    </ul>
  );
}

function PortfolioView({ onOpen }: { onOpen: (id: string) => void }) {
  const [by, setBy] = useState<"award" | "dept">("award");
  const depts = useMemo(() => Array.from(new Set(awards.map((a) => a.dept))), []);
  const sorted = [...awards].sort((a, b) => daysTo(a) - daysTo(b));
  return (
    <>
      <Kpis list={awards} />
      <div className="dgrid2">
        <div className="dpanel">
          <h4>{by === "award" ? "Awards" : "Departments"}
            <span role="group" aria-label="Group by" style={{ display: "inline-flex", gap: 4 }}>
              {(["award", "dept"] as const).map((k) => (<button key={k} className="dash-tab" aria-pressed={by === k} onClick={() => setBy(k)} style={{ padding: "2px 8px", borderBottom: "none", background: by === k ? "var(--soft)" : "none", borderRadius: 6 }}>{k === "award" ? "By award" : "By department"}</button>))}
            </span></h4>
          <div className="tscroll"><table className="dtable">
            <thead><tr><th>{by === "award" ? "Award" : "Department"}</th><th className="r">Budget</th><th>Posted / committed</th><th className="r">Available</th><th className="r">Projected*</th></tr></thead>
            <tbody>
              {by === "award" ? sorted.map((a) => { const d = derive(a); return (
                <tr key={a.id}><td><button className="rowlink" onClick={() => onOpen(a.id)} aria-label={`Open award view for ${a.title}`}>{a.title}</button><div style={{ fontSize: 11, color: "var(--muted)" }}>{a.id}</div></td>
                  <td className="r">{moneyShort(a.budget)}</td><td><Bar a={a} /></td><td className="r">{moneyShort(d.available)}</td><td className="r" style={{ color: d.projectedRemaining < 0 ? "var(--coral-ink)" : undefined, fontWeight: d.projectedRemaining < 0 ? 700 : 400 }}>{moneyShort(d.projectedRemaining)}</td></tr>); })
              : depts.map((dp) => { const l = awards.filter((a) => a.dept === dp); const t = totals(l); const flags = l.reduce((s, a) => s + derive(a).flags.length, 0); return (
                <tr key={dp}><td><b>{dp}</b><div style={{ fontSize: 11, color: "var(--muted)" }}>{l.length} award{l.length > 1 ? "s" : ""} · {flags} flag{flags === 1 ? "" : "s"}</div></td><td className="r">{moneyShort(t.budget)}</td>
                  <td><div className="sbar"><i className="act" style={{ width: `${(t.actual / t.budget) * 100}%` }} /><i className="com" style={{ width: `${(t.committed / t.budget) * 100}%` }} /></div></td><td className="r">{moneyShort(t.available)}</td><td className="r">{moneyShort(t.projected)}</td></tr>); })}
            </tbody></table></div>
          <div style={{ marginTop: 10 }}><Legend /></div>
        </div>
        <div className="stack">
          <div className="dpanel"><h4>Awards requiring attention</h4><Attention list={awards} limit={4} /></div>
          <div className="dpanel"><h4>Award end dates</h4>
            <ul className="alist">{sorted.slice(0, 4).map((a) => (<li key={a.id}><div><b>{a.title}</b><small>{a.id}</small></div><span className="badge">{dateLabel(a.end)}</span></li>))}</ul></div>
        </div>
      </div>
      <div className="dpanel"><h4>Monthly spending trend <span className="legend"><span><i className="act" />Posted</span><span><i className="prj" />Projected</span></span></h4><Trend /></div>
    </>
  );
}
const daysTo = (a: Award) => derive(a).days;

function AwardView({ a, setId }: { a: Award; setId: (id: string) => void }) {
  const d = derive(a), sid = useId();
  const b = splitBy(a.budget, categories.map((c) => c.b)), ac = splitBy(a.actual, categories.map((c) => c.a)), co = splitBy(a.committed, categories.map((c) => c.c));
  const ct = splitBy(a.committed, commitmentTypes.map((c) => c.s));
  return (
    <>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "end", justifyContent: "space-between" }}>
        <div><label htmlFor={sid} style={{ fontSize: 11, color: "var(--muted)", display: "block" }}>Find an award</label>
          <select id={sid} value={a.id} onChange={(e) => setId(e.target.value)} style={{ font: "inherit", padding: "8px 10px", border: "1px solid var(--border)", borderRadius: 8, minWidth: 260, background: "#fff", color: "var(--slate)" }}>
            {awards.map((x) => <option key={x.id} value={x.id}>{x.id} · {x.title}</option>)}</select></div>
        <div style={{ fontSize: 12, color: "var(--muted)" }}>{a.sponsor} · {a.dept} · {a.pi} · ends {dateLabel(a.end)}</div>
      </div>
      <div className="kpis">
        <div className="kpi"><span>Award budget</span><b>{money(a.budget)}</b><small>{a.budget !== a.originalBudget ? `Revised from ${money(a.originalBudget)} (approved adjustment)` : "Original budget, no adjustments"}</small></div>
        <div className="kpi"><span>Actual expenditures (posted)</span><b>{money(a.actual)}</b></div>
        <div className="kpi"><span>Outstanding commitments</span><b>{money(a.committed)}</b><small>Not yet posted</small></div>
        <div className="kpi kpi--key"><span>Available balance</span><b>{money(d.available)}</b></div>
        <div className="kpi"><span>Projected remaining balance</span><b style={{ color: d.projectedRemaining < 0 ? "var(--coral-ink)" : undefined }}>{money(d.projectedRemaining)}</b><small>Estimate, {d.months} months left</small></div>
        <div className="kpi"><span>Budget utilization</span><b>{pct(d.utilization)}</b><small>Posted + committed</small></div>
      </div>
      <div className="formula">Available balance = {money(a.budget)} budget − {money(a.actual)} actual − {money(a.committed)} commitments = <b>{money(d.available)}</b></div>
      <div className="dgrid2">
        <div className="dpanel"><h4>By budget category</h4><div className="tscroll"><table className="dtable"><thead><tr><th>Category</th><th className="r">Budget</th><th className="r">Actual</th><th className="r">Committed</th><th className="r">Available</th></tr></thead>
          <tbody>{categories.map((c, i) => (<tr key={c.name}><td>{c.name}</td><td className="r">{money(b[i])}</td><td className="r">{money(ac[i])}</td><td className="r">{money(co[i])}</td><td className="r">{money(b[i] - ac[i] - co[i])}</td></tr>))}</tbody></table></div></div>
        <div className="stack">
          <div className="dpanel"><h4>Outstanding commitments</h4><ul className="alist">{commitmentTypes.map((c, i) => (<li key={c.name}><span>{c.name}</span><b style={{ fontVariantNumeric: "tabular-nums" }}>{money(ct[i])}</b></li>))}</ul></div>
          <div className="dpanel"><h4>Attention</h4>{d.flags.length ? <ul className="alist">{d.flags.map((f) => <li key={f.text}><span>{f.text}</span><span className={flagClass[f.kind]}>{f.kind === "over" ? "Risk" : f.kind === "under" ? "Review" : f.kind === "ends" ? "Date" : "Reconcile"}</span></li>)}</ul> : <p style={{ color: "var(--muted)" }}>No items currently flagged.</p>}</div>
        </div>
      </div>
      <div className="dash-foot"><span>Projection method (illustrative): trailing 3-month average spend × months remaining, or commitments if higher.</span></div>
    </>
  );
}

function ReconView({ a }: { a: Award }) {
  return (
    <>
      <div className="note note--blue"><b>{a.title}</b> ({a.id}) · FORGE records compared with the institutional report. The institutional record is the system of record.</div>
      <div className="dash-foot"><span><b>Institutional report imported:</b> {AS_OF_LABEL} (manual import)</span><span><b>FORGE records last edited:</b> Oct 31, 2026</span></div>
      <div className="tscroll"><table className="dtable"><thead><tr><th>Date</th><th>Transaction</th><th>Source</th><th className="r">FORGE</th><th className="r">Institutional</th><th>Status</th></tr></thead>
        <tbody>{reconRows.map((r) => (<tr key={r.desc}><td>{dateLabel(r.date)}</td><td>{r.desc}</td><td>{r.source}</td><td className="r">{r.forge === null ? "—" : money(r.forge)}</td><td className="r">{r.inst === null ? "—" : money(r.inst)}</td>
          <td><span className={r.status === "Matched" ? "badge badge--ok" : "badge badge--coral"}>{r.status}</span></td></tr>))}</tbody></table></div>
      <div className="legend"><span>3 items to review: 1 amount difference, 1 missing in the institutional report, 1 missing in FORGE. An administrator reviews and corrects.</span></div>
    </>
  );
}

export default function FinancialWorkspace({ compact = false }: { compact?: boolean }) {
  const [tab, setTab] = useState<"portfolio" | "award" | "recon">("portfolio");
  const [id, setId] = useState("SYN-101");
  const a = awards.find((x) => x.id === id)!;
  const tabs = [{ k: "portfolio", l: "Portfolio" }, { k: "award", l: "Award view" }, { k: "recon", l: "Reconciliation" }] as const;
  const frameBar = (
    <div className="frame-bar"><i /><i /><i /><span className="url">workspace · financial intelligence</span><span className="badge badge--coral">Synthetic data</span></div>
  );
  if (compact) {
    const list = [...awards].sort((x, y) => daysTo(x) - daysTo(y)).slice(0, 4);
    return (
      <div className="frame" role="group" aria-label="FORGE Financial Intelligence preview (illustrative synthetic data)">
        {frameBar}
        <div className="dash">
          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "space-between", gap: 4, alignItems: "baseline" }}><b style={{ fontFamily: "var(--f-head)", color: "var(--blue)", fontSize: 15 }}>Financial Intelligence · Portfolio</b><span style={{ fontSize: 11, color: "var(--muted)" }}>Institutional data imported {AS_OF_LABEL}</span></div>
          <Kpis list={awards} compact />
          <div className="dpanel"><div className="tscroll"><table className="dtable"><thead><tr><th>Award</th><th>Posted / committed</th><th className="r">Available</th></tr></thead>
            <tbody>{list.map((x) => (<tr key={x.id}><td>{x.title}</td><td><Bar a={x} /></td><td className="r">{moneyShort(derive(x).available)}</td></tr>))}</tbody></table></div>
            <div style={{ marginTop: 10 }}><Legend /></div></div>
          <div className="dpanel"><h4>Awards requiring attention</h4><Attention list={awards} limit={2} /></div>
          <div className="dash-foot"><span>{site.syntheticNote}</span></div>
        </div>
      </div>
    );
  }
  return (
    <div className="frame" role="region" aria-label="FORGE Financial Intelligence interactive preview (illustrative synthetic data)">
      {frameBar}
      <div className="dash">
        <div role="tablist" aria-label="Views" className="dash-tabs">
          {tabs.map((t) => (<button key={t.k} role="tab" aria-selected={tab === t.k} className="dash-tab" onClick={() => setTab(t.k)}>{t.l}</button>))}
        </div>
        {tab === "portfolio" && <PortfolioView onOpen={(x) => { setId(x); setTab("award"); }} />}
        {tab === "award" && <AwardView a={a} setId={setId} />}
        {tab === "recon" && (<><div><label htmlFor="rid" style={{ fontSize: 11, color: "var(--muted)", display: "block" }}>Award</label><select id="rid" value={id} disabled style={{ font: "inherit", padding: "8px 10px", border: "1px solid var(--border)", borderRadius: 8, background: "var(--warm)" }}><option>{awards[0].id} · {awards[0].title}</option></select></div><ReconView a={awards[0]} /></>)}
        <div className="dash-foot"><span>{site.syntheticNote}</span><span>* Projected figures are estimates, not actual balances. Institutional data shown as imported {AS_OF_LABEL}, not real time.</span></div>
      </div>
    </div>
  );
}
