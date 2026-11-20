import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { automations, awardFields, governance } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
import CTAButton from "@/components/common/CTAButton";
import FinalCTA from "@/components/common/FinalCTA";
export const dynamicParams = false;
export const generateStaticParams = () => automations.map((a) => ({ slug: a.slug }));
export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const a = automations.find((x) => x.slug === params.slug);
  return { title: a?.title, description: a?.summary };
}
export default function AutomationPage({ params }: { params: { slug: string } }) {
  const a = automations.find((x) => x.slug === params.slug);
  if (!a) notFound();
  return (
    <>
      <PageHero eyebrow="AI & Automation" title={a.title} text={a.summary}>
        <CTAButton href="/book-consultation?interest=AI%20%26%20Automation" event="consultation_cta_clicked">Discuss an Automation Project</CTAButton>
        <CTAButton href="/ai-automation" tone="secondary">All automation</CTAButton>
      </PageHero>
      <section className="section">
        <div className="container card-grid grid-2" style={{ alignItems: "start" }}>
          <div><h2 style={{ fontSize: 26, marginBottom: 12 }}>How it helps</h2><p className="lead">{a.detail}</p></div>
          <div className="gcard">
            {a.slug === "award-intelligence" && (<><h3 style={{ marginTop: 0 }}>Fields extracted</h3><ul>{awardFields.map((f) => <li key={f}>{f}</li>)}</ul></>)}
            <h3 style={{ marginTop: a.slug === "award-intelligence" ? 8 : 0 }}>Human review stays essential</h3>
            <ul>{governance.slice(0, 3).map((g) => <li key={g}>{g}</li>)}</ul>
          </div>
        </div>
      </section>
      <FinalCTA />
    </>
  );
}
