import { products, whyForge, aiItems } from "@/lib/content";
import { withBase } from "@/lib/path";
import Section, { SectionHeading } from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import FinancialWorkspace from "@/components/platform/FinancialWorkspace";
import ShadowTransformation from "@/components/sections/ShadowTransformation";
import ProductCard from "@/components/sections/ProductCard";

export default function Home() {
  const featured = ["travel-budget-calculator", "budget-monitor", "award-tracker", "research-operations-toolkit"];
  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div>
            <div className="eyebrow">Connected research operations</div>
            <h1>Research administration, made simpler.</h1>
            <p className="lead">Practical tools for small research administration teams to manage grants, budgets, deadlines and procedures, and a connected workspace in development that works alongside your university systems.</p>
            <div className="btn-row"><Button href="/products" size="lg">Explore Products</Button><Button href="/products/travel-budget-calculator" variant="secondary" size="lg">Try the free calculator</Button></div>
            <p className="tagline-strip">Small teams. Complex research portfolios. Simpler operations.</p>
          </div>
          <figure className="hero-visual">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={withBase("/images/hero.webp")} width={640} height={360} alt="A monitor showing the FORGE logo with many separate spreadsheet windows being brought together" fetchPriority="high" />
          </figure>
        </div>
      </section>

      <Section tone="white">
        <SectionHeading eyebrow="Products & tools" title="Practical tools you can use right away." text="Spreadsheet-based tools and templates for award tracking, budget monitoring, compliance and procedures, plus a free travel budget calculator." />
        <div className="grid g4">{featured.map((s) => <ProductCard key={s} p={products.find((p) => p.slug === s)!} />)}</div>
        <div className="btn-row"><Button href="/products" variant="secondary">See all products</Button></div>
      </Section>

      <Section tone="warm">
        <div className="split" style={{ marginBottom: 56 }}>
          <SectionHeading eyebrow="Coming next" title="Beyond the Shadow Budget." text="FORGE Financial Intelligence is being designed to replace the manually maintained departmental spreadsheet with a connected view of award budgets, posted expenditures, commitments and projected balances. It works alongside the official institutional systems and does not replace them. It is in development." />
          <FinancialWorkspace compact />
        </div>
        <ShadowTransformation />
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="AI & automation" title="Intelligent help, with people in charge." text="Automation prepares drafts, extractions and reminders. Humans review and decide. These capabilities are in development." />
        <div className="grid g3">{aiItems.slice(0, 3).map((a) => (<div key={a.t} className="panel"><h3 style={{ fontSize: 18 }}>{a.t}</h3><p>{a.d}</p></div>))}</div>
        <div className="btn-row"><Button href="/ai-automation" variant="secondary">Explore AI & Automation</Button></div>
      </Section>

      <Section tone="soft">
        <SectionHeading eyebrow="Why FORGE" title="Simple enough for a two-person team." />
        <div className="grid g4">{whyForge.map((w) => (<div key={w.t}><h3 style={{ fontSize: 18, marginBottom: 8 }}>{w.t}</h3><p style={{ color: "var(--muted)" }}>{w.d}</p></div>))}</div>
      </Section>
    </>
  );
}
