/**
 * SYNTHETIC DATA for product demonstrations only. No real awards, sponsors, people or institutions.
 * Definitions (kept explicit so the demo never blurs concepts):
 *   Actual      = posted expenditures (as of the last import date)
 *   Commitments = outstanding, NOT yet posted (open POs, payroll projections, anticipated travel, other)
 *   Available   = Budget − Actual − Commitments
 *   Projection  = estimate, never an actual balance: Budget − Actual − max(Commitments, trailing-3-month average × months remaining)
 */
export const AS_OF = "2026-10-31";
export const AS_OF_LABEL = "Oct 31, 2026";

export type Award = {
  id: string; title: string; dept: string; sponsor: string; pi: string; end: string;
  originalBudget: number; budget: number; actual: number; committed: number; monthlyAvg: number; toReview: number;
};
export const awards: Award[] = [
  { id: "SYN-101", title: "Coastal Resilience Study", dept: "Environmental Science", sponsor: "Federal agency A", pi: "Dr. Sample A.", end: "2027-08-31", originalBudget: 1200000, budget: 1250000, actual: 612400, committed: 148300, monthlyAvg: 41500, toReview: 3 },
  { id: "SYN-102", title: "Community Health Outcomes", dept: "Public Health", sponsor: "Foundation B", pi: "Dr. Sample B.", end: "2027-02-28", originalBudget: 640000, budget: 640000, actual: 421900, committed: 52100, monthlyAvg: 38000, toReview: 0 },
  { id: "SYN-103", title: "Materials Imaging Core", dept: "Engineering", sponsor: "Federal agency C", pi: "Dr. Sample C.", end: "2027-05-31", originalBudget: 2100000, budget: 2100000, actual: 1310500, committed: 395000, monthlyAvg: 74000, toReview: 0 },
  { id: "SYN-104", title: "Rural Education Pilot", dept: "Education", sponsor: "State agency D", pi: "Dr. Sample D.", end: "2028-01-31", originalBudget: 380000, budget: 380000, actual: 118600, committed: 21000, monthlyAvg: 6200, toReview: 0 },
  { id: "SYN-105", title: "Data Methods Training", dept: "Engineering", sponsor: "Foundation E", pi: "Dr. Sample E.", end: "2026-12-31", originalBudget: 275000, budget: 275000, actual: 241800, committed: 30500, monthlyAvg: 14000, toReview: 0 },
  { id: "SYN-106", title: "Watershed Sensor Network", dept: "Environmental Science", sponsor: "Federal agency A", pi: "Dr. Sample F.", end: "2027-10-31", originalBudget: 890000, budget: 890000, actual: 402000, committed: 96000, monthlyAvg: 33500, toReview: 0 },
  { id: "SYN-107", title: "Clinical Outreach Network", dept: "Public Health", sponsor: "Federal agency G", pi: "Dr. Sample G.", end: "2027-03-31", originalBudget: 1480000, budget: 1480000, actual: 905300, committed: 233400, monthlyAvg: 118000, toReview: 0 },
];

const MS = 86400000;
export const daysBetween = (a: string, b: string) => Math.round((new Date(b).getTime() - new Date(a).getTime()) / MS);
export const monthsLeft = (end: string) => Math.max(0, Math.round(daysBetween(AS_OF, end) / 30.4));

export function derive(a: Award) {
  const available = a.budget - a.actual - a.committed;
  const m = monthsLeft(a.end);
  const projectedSpend = Math.max(a.committed, a.monthlyAvg * m);
  const projectedRemaining = a.budget - a.actual - projectedSpend;
  const utilization = (a.actual + a.committed) / a.budget; // spent + committed
  const days = daysBetween(AS_OF, a.end);
  const flags: { kind: "over" | "under" | "ends" | "review"; text: string }[] = [];
  if (projectedRemaining < 0) flags.push({ kind: "over", text: `Projected overspend ${money(-projectedRemaining)}` });
  if (projectedRemaining / a.budget > 0.35) flags.push({ kind: "under", text: "Possible underspending" });
  if (days <= 90) flags.push({ kind: "ends", text: `Ends in ${days} days` });
  if (a.toReview > 0) flags.push({ kind: "review", text: `${a.toReview} items to review` });
  return { available, months: m, projectedSpend, projectedRemaining, utilization, days, flags };
}

export function totals(list: Award[]) {
  const t = list.reduce((s, a) => { const d = derive(a); return { budget: s.budget + a.budget, actual: s.actual + a.actual, committed: s.committed + a.committed, available: s.available + d.available, projected: s.projected + d.projectedRemaining }; }, { budget: 0, actual: 0, committed: 0, available: 0, projected: 0 });
  return { ...t, utilization: (t.actual + t.committed) / t.budget };
}

export const money = (n: number) => (n < 0 ? "−" : "") + "$" + Math.abs(Math.round(n)).toLocaleString("en-US");
export const moneyShort = (n: number) => { const a = Math.abs(n); const s = a >= 1e6 ? `$${(a / 1e6).toFixed(2)}M` : a >= 1e3 ? `$${Math.round(a / 1e3)}K` : `$${a}`; return (n < 0 ? "−" : "") + s; };
export const pct = (x: number) => `${Math.round(x * 100)}%`;
export const dateLabel = (iso: string) => new Date(iso + "T00:00:00").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });

/** Posted monthly spending for the whole synthetic portfolio, Nov 2025 – Oct 2026 ($K), plus a simple trailing-average projection. */
export const trendMonths = ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"];
export const trendPosted = [301, 318, 296, 334, 352, 347, 361, 379, 372, 388, 395, 382];
export const trendProjected = (() => { const avg = Math.round(trendPosted.slice(-3).reduce((a, b) => a + b, 0) / 3); return [avg, avg, avg]; })();
export const trendProjectedMonths = ["Nov", "Dec", "Jan"];

/** Category split used for award-level views (shares of budget / actual / committed; each sums to 1). */
export const categories = [
  { name: "Salaries & wages", b: .50, a: .53, c: .62 }, { name: "Fringe benefits", b: .14, a: .15, c: .15 },
  { name: "Equipment", b: .08, a: .09, c: .04 }, { name: "Travel", b: .06, a: .05, c: .06 },
  { name: "Supplies & materials", b: .10, a: .09, c: .06 }, { name: "Subawards", b: .08, a: .07, c: .05 }, { name: "Other direct costs", b: .04, a: .02, c: .02 },
];
export const commitmentTypes = [
  { name: "Payroll projections", s: .56 }, { name: "Open purchase orders", s: .24 }, { name: "Anticipated travel", s: .12 }, { name: "Other expected costs", s: .08 },
];
export function splitBy(total: number, shares: number[]) {
  const out = shares.map((s) => Math.round(total * s)); out[out.length - 1] += total - out.reduce((a, b) => a + b, 0); return out;
}

export type Recon = { date: string; desc: string; source: string; forge: number | null; inst: number | null; status: "Matched" | "Amount differs" | "Missing in institutional report" | "Missing in FORGE" };
export const reconRows: Recon[] = [
  { date: "2026-10-14", desc: "Payroll, October", source: "Payroll import", forge: 18420, inst: 18420, status: "Matched" },
  { date: "2026-10-09", desc: "Lab supplies, PO-5521", source: "Procurement report", forge: 6310, inst: 6310, status: "Matched" },
  { date: "2026-10-03", desc: "Travel reimbursement", source: "Travel report", forge: 1284, inst: 1248, status: "Amount differs" },
  { date: "2026-09-28", desc: "Equipment service agreement", source: "Entered manually", forge: 4900, inst: null, status: "Missing in institutional report" },
  { date: "2026-09-22", desc: "Participant payments", source: "Institutional report", forge: null, inst: 2150, status: "Missing in FORGE" },
  { date: "2026-09-15", desc: "Subaward invoice 3", source: "Institutional report", forge: 12000, inst: 12000, status: "Matched" },
];
