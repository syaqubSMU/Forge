import Link from "next/link";
import { challenges, approach, modules, services, products, aiItems, whyForge, site } from "@/lib/content";
import Section, { SectionHeading } from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import FinancialWorkspace from "@/components/platform/FinancialWorkspace";
import IntegrationDiagram from "@/components/sections/IntegrationDiagram";
import AwardWorkflow from "@/components/sections/AwardWorkflow";
import ShadowTransformation from "@/components/sections/ShadowTransformation";
import ProductCard from "@/components/sections/ProductCard";
import FinalCTA from "@/components/sections/FinalCTA";

export default function Home() {
  const flagship = modules.find((m) => m.flagship)!;
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <div className="eyebrow">{site.descriptor}</div>
            <h1>Research administration, made simpler.</h1>
            <p className="lead">Manage grants, budgets, compliance and research operations in one connected workspace. FORGE brings your information and workflows together, works alongside your university systems and uses intelligent automation to reduce administrative effort.</p>
            <div className="btn-row"><Button href="/platform" size="lg">Explore FORGE</Button><Button href="/#how-it-works" variant="secondary" size="lg">See How It Works</Button></div>
            <p className="tagline-strip">Small teams. Complex research portfolios. Simpler operations.</p>
          </div>
          <FinancialWorkspace compact />
        </div>
      </section>

      <Section tone="white">
        <div className="split split--rev" style={{ alignItems: "start" }}>
          <div>
            <SectionHeading eyebrow="The challenge" title="Small teams carry complex research portfolios." text="Research administration teams are often small but responsible for a lot. They work across disconnected systems, spreadsheets, documents and manual processes, and need a connected, manageable way to coordinate it." />
          </div>
          <div className="ruled">{challenges.map((c, i) => (<div className="item" key={c.t}><h3><span className="num">0{i + 1}</span>{c.t}</h3><p>{c.d}</p></div>))}</div>
        </div>
      </Section>

      <Section tone="warm">
        <SectionHeading eyebrow="The FORGE approach" title="Connect, organize, monitor, automate." text="A practical path from scattered files to a workspace a small team can run." />
        <div className="grid g4">{approach.map((a, i) => (<div key={a.t} className="panel"><span className="num">0{i + 1}</span><h3 style={{ marginTop: 8 }}>{a.t}</h3><p>{a.d}</p></div>))}</div>
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="Platform overview" title="One modular workspace. Start small and grow." text="Begin with the tools you need and add more as your team and portfolio grow. The platform is in development; see what is planned and preview the interface below." />
        <div className="panel" style={{ background: "var(--soft)", borderColor: "#C8D8E6", marginBottom: 24 }}>
          <div className="split split--flag" style={{ alignItems: "center" }}>
            <div><span className="badge badge--coral">Flagship module</span><h3 style={{ margin: "12px 0 8px", fontSize: 26 }}>{flagship.title}</h3><p style={{ color: "var(--muted)" }}>{flagship.text}</p>
              <div className="btn-row"><Button href="/platform#shadow-budget">Beyond the Shadow Budget</Button></div></div>
            <ul className="checks"><li>Award budgets and approved adjustments</li><li>Posted expenditures and commitments, kept separate</li><li>Available balance and projected balance</li><li>Reconciliation with institutional reports</li></ul>
          </div>
        </div>
        <div className="grid g3">{modules.filter((m) => !m.flagship).map((m) => (<div key={m.slug} className="panel"><div style={{ display: "flex", justifyContent: "space-between", gap: 8 }}><h3 style={{ fontSize: 18 }}>{m.title}</h3></div><p>{m.text}</p><span className="badge" style={{ marginTop: 12 }}>In development</span></div>))}</div>
      </Section>

      <Section tone="soft" id="how-it-works">
        <SectionHeading eyebrow="Beyond the shadow budget" title="From fragmented spreadsheets to a connected view." text="FORGE does not replace the official financial system. It replaces the manual departmental tracking layer that sits between those records and the people managing awards." />
        <ShadowTransformation />
        <div style={{ height: 72 }} />
        <SectionHeading eyebrow="How it works" title="From award document to ongoing monitoring." />
        <AwardWorkflow />
      </Section>

      <Section tone="blue">
        <SectionHeading eyebrow="Integration first" title="Built to work alongside your university systems." text="FORGE connects people, information, documents and workflows with the systems your institution already relies on, instead of asking you to replace them." />
        <IntegrationDiagram />
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="Solutions & services" title="Practical help, from assessment to implementation." />
        <div className="grid g2" style={{ columnGap: 56, rowGap: 0 }}>{services.map((s) => (<div className="item" key={s.slug}><h3><span className="num">{s.n}</span>{s.t}</h3><p>{s.d}</p></div>))}</div>
        <div style={{ marginTop: 32 }}><Link href="/solutions" className="link-arrow">Explore solutions <span aria-hidden="true">→</span></Link></div>
      </Section>

      <Section tone="warm">
        <SectionHeading eyebrow="Products & toolkits" title="Practical tools you can use right away." text="Spreadsheet-based tools and templates for award tracking, budget monitoring, compliance and procedures, plus a free travel budget calculator." />
        <div className="grid g3">{products.filter((p) => ["travel-budget-calculator", "budget-monitor", "award-tracker"].includes(p.slug)).map((p) => <ProductCard key={p.slug} p={p} />)}</div>
        <div style={{ marginTop: 32 }}><Link href="/products" className="link-arrow">See all products <span aria-hidden="true">→</span></Link></div>
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="AI & automation" title="Intelligent help, with people in charge." text="Automation prepares drafts, extractions and reminders. Humans review and decide. These capabilities are in development." />
        <div className="grid g3">{aiItems.slice(0, 3).map((a) => (<div key={a.t} className="panel"><h3 style={{ fontSize: 18 }}>{a.t}</h3><p>{a.d}</p></div>))}</div>
        <div style={{ marginTop: 32 }}><Link href="/ai-automation" className="link-arrow">Explore AI & automation <span aria-hidden="true">→</span></Link></div>
      </Section>

      <Section tone="soft">
        <SectionHeading eyebrow="Why FORGE" title="Simple enough for a two-person team." />
        <div className="grid g4">{whyForge.map((w) => (<div key={w.t}><h3 style={{ fontSize: 18, marginBottom: 8 }}>{w.t}</h3><p style={{ color: "var(--muted)" }}>{w.d}</p></div>))}</div>
      </Section>

      <FinalCTA />
    </>
  );
}
