import type { Metadata } from "next";
import { PageHero } from "@/components/ui/Section";
import Section, { SectionHeading } from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import FAQ from "@/components/ui/FAQ";
import FinancialWorkspace from "@/components/platform/FinancialWorkspace";
import IntegrationDiagram from "@/components/sections/IntegrationDiagram";
import ShadowTransformation from "@/components/sections/ShadowTransformation";
import FinalCTA from "@/components/sections/FinalCTA";

export const metadata: Metadata = { title: "Platform", description: "FORGE is an easy-to-manage research operations workspace: award tracking, financial monitoring, compliance calendar, PI dashboards and documents, working alongside your university systems.", openGraph: { title: "FORGE Platform", description: "A connected research operations workspace for small teams." } };

const capabilities = [
  { t: "Award budget management", items: ["Original award budget", "Revised budget", "Budget categories", "Approved budget adjustments", "Award-level financial records"] },
  { t: "Actual expenditure monitoring", items: ["Posted expenditures", "Payroll charges", "Procurement and purchase orders", "Travel and other expenses", "Transaction dates and source information"] },
  { t: "Commitment tracking", items: ["Payroll projections", "Open purchase orders", "Anticipated travel", "Outstanding commitments", "Other expected costs"] },
  { t: "Available balance", items: ["Budget − actual − commitments", "Committed amounts shown apart from posted expenditures", "Prevents double counting"] },
  { t: "Financial forecasting", items: ["Project future expenditures", "Estimate end-of-award balances", "Identify potential overspending", "Highlight possible underspending", "Surface awards needing attention"] },
  { t: "Financial reconciliation", items: ["Compare against institutional financial reports", "Find missing or mismatched transactions", "Flag discrepancies", "Source and last-updated timestamps", "Administrator review and correction"] },
];
const tasks = ["Find an award", "See its financial position", "Understand what has been spent", "Understand what is committed", "See what remains available", "Identify upcoming financial risks", "Reconcile with the institutional system"];
const others = [
  { t: "Portfolio overview", d: "All awards, sponsors, amounts and end dates in one scannable view." },
  { t: "Award tracking", d: "A structured record per award: terms, dates, contacts, documents and status." },
  { t: "Compliance calendar", d: "Reporting deadlines and award conditions with owners and reminders." },
  { t: "PI dashboards", d: "Plain, role-appropriate views for investigators, with less emailing of spreadsheets." },
  { t: "Document management", d: "Award documents organized with the record they belong to." },
];
const faqs = [
  { q: "Is FORGE an accounting system?", a: "No. FORGE is an operational monitoring and intelligence layer. Official institutional accounting records remain the system of record. FORGE helps departmental teams monitor and reconcile against them." },
  { q: "Does FORGE replace PeopleSoft, Cayuse or other university systems?", a: "No. It is designed to work alongside them through approved integrations, data imports, exports and APIs." },
  { q: "Is the data real time?", a: "Not by default. Institutional data in FORGE reflects the most recent import, and every view shows its source and last-updated date." },
  { q: "Is the platform available today?", a: "The platform is in development. The screens on this site use illustrative synthetic data. Consulting and digital products are available now." },
];

export default function Platform() {
  return (
    <>
      <PageHero eyebrow="Platform" title="An easy-to-manage research operations workspace." text="FORGE sits between your existing university systems and the people managing research every day, connecting award, budget, compliance and document information in one place.">
        <Button href="/book-discovery-call" event="consultation_cta_clicked">Book a Discovery Call</Button><Button href="#try-it" variant="secondary">Try the preview</Button>
      </PageHero>

      <Section tone="white">
        <SectionHeading eyebrow="Operating model" title="Connected to your systems. Built for your people." />
        <IntegrationDiagram />
      </Section>

      <Section tone="soft" id="shadow-budget">
        <SectionHeading eyebrow="FORGE Financial Intelligence" title="Beyond the Shadow Budget." text="Move beyond manually maintained spreadsheets. FORGE brings award budgets, actual expenditures, commitments and projected balances together in one connected workspace, helping departmental research teams maintain better financial visibility and make more informed decisions." />
        <ShadowTransformation />
        <div className="grid g2" style={{ marginTop: 40 }}>
          <div className="panel"><span className="badge badge--blue">Official record</span><h3 style={{ margin: "12px 0 8px" }}>Institutional financial systems</h3><p>The university&apos;s official accounting records remain the system of record. FORGE does not replace them.</p></div>
          <div className="panel" style={{ borderColor: "var(--coral)" }}><span className="badge badge--coral">Departmental monitoring</span><h3 style={{ margin: "12px 0 8px" }}>FORGE Financial Intelligence</h3><p>Replaces the manual departmental tracking layer between official systems and the people who manage awards, working alongside them through approved integrations, imports, exports and APIs.</p></div>
        </div>
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="Capabilities" title="Six capabilities, one financial picture." />
        <div className="grid g3">{capabilities.map((c, i) => (<div className="panel" key={c.t}><span className="num">0{i + 1}</span><h3 style={{ marginTop: 8 }}>{c.t}</h3><ul className="checks">{c.items.map((x) => <li key={x}>{x}</li>)}</ul></div>))}</div>
        <div className="formula" style={{ marginTop: 28, fontSize: 14 }}>Available Balance = Award Budget − Actual Expenditures − Outstanding Commitments</div>
        <p className="note" style={{ marginTop: 14 }}>Commitments are shown separately from posted expenditures so nothing is counted twice. Projections are estimates and are never presented as actual balances.</p>
      </Section>

      <Section tone="warm" id="try-it">
        <SectionHeading eyebrow="Interactive preview" title="See how a small team would use it." text="Switch views, open an award and look at reconciliation. Everything here is illustrative synthetic data." />
        <FinancialWorkspace />
        <div style={{ marginTop: 36 }} className="grid g4">
          {tasks.map((t, i) => (<div key={t} style={{ borderTop: "2px solid var(--coral)", paddingTop: 12 }}><span className="num">0{i + 1}</span><p style={{ fontWeight: 600, color: "var(--blue)" }}>{t}</p></div>))}
        </div>
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="More of the workspace" title="Everything a small team needs, nothing it doesn't." text="Financial Intelligence is the flagship. These modules complete the workspace and are in development." />
        <div className="ruled">{others.map((o) => (<div className="item" key={o.t}><h3>{o.t} <span className="badge">In development</span></h3><p>{o.d}</p></div>))}</div>
      </Section>

      <Section tone="soft">
        <SectionHeading eyebrow="Questions" title="What to know about FORGE" />
        <div style={{ maxWidth: 820 }}><FAQ items={faqs} /></div>
      </Section>
      <FinalCTA />
    </>
  );
}
