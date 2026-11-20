import type { Metadata } from "next";
import Link from "next/link";
import { automations, awardFields, budgetMonitor, governance } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
import SectionHeading from "@/components/common/SectionHeading";
import CTAButton from "@/components/common/CTAButton";
import FinalCTA from "@/components/common/FinalCTA";
export const metadata: Metadata = { title: "AI & Automation", description: "Practical, human-reviewed AI and workflow automation for grant administration." };
export default function AI() {
  return (
    <>
      <PageHero eyebrow="AI & Automation" title="Practical automation for grant administration." text="Forge uses AI to reduce repetitive administrative work — with people staying in control of every financial, contractual and compliance decision.">
        <CTAButton href="/book-consultation?interest=AI%20%26%20Automation" event="consultation_cta_clicked">Discuss an Automation Project</CTAButton>
      </PageHero>
      <section className="section">
        <div className="container card-grid grid-2" style={{ alignItems: "start" }}>
          <div>
            <div className="eyebrow">Featured automation</div>
            <h2 style={{ fontSize: 32 }}>Award Intelligence Assistant</h2>
            <h3 style={{ fontSize: 17, margin: "18px 0 6px" }}>The problem</h3>
            <p>Award agreements and funding documents contain important information that administrators must manually review and transfer into tracking systems.</p>
            <h3 style={{ fontSize: 17, margin: "18px 0 6px" }}>The solution</h3>
            <p>Upload an award document and extract structured information. The system retains source-page references and flags uncertain extractions for human review.</p>
          </div>
          <div className="gcard"><h3 style={{ marginTop: 0 }}>Fields extracted</h3><ul>{awardFields.map((f) => <li key={f}>{f}</li>)}</ul></div>
        </div>
      </section>
      <section className="section section--white">
        <div className="container">
          <SectionHeading title="More automation solutions" />
          <div className="card-grid grid-3">
            {automations.slice(1).map((a) => (<article className="gcard" key={a.slug}><h3>{a.title}</h3><p>{a.summary}</p><Link className="more" href={`/ai-automation/${a.slug}`}>Learn more →</Link></article>))}
            <article className="gcard"><h3>{budgetMonitor.title}</h3><p>{budgetMonitor.summary}</p></article>
          </div>
        </div>
      </section>
      <section className="section">
        <div className="container">
          <SectionHeading eyebrow="Trust and governance" title="Automation supports your team — it doesn’t replace judgment." />
          <div className="gcard" style={{ maxWidth: 760 }}><ul style={{ lineHeight: 1.9 }}>{governance.map((g) => <li key={g}>{g}</li>)}</ul></div>
        </div>
      </section>
      <FinalCTA title="Curious what automation could do for your team?" text="Let's talk through where it fits, and where it doesn't." cta="Discuss an Automation Project" />
    </>
  );
}
