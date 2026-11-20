import type { Metadata } from "next";
import { services } from "@/lib/content";
import Section, { PageHero, SectionHeading } from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import FinalCTA from "@/components/sections/FinalCTA";
export const metadata: Metadata = { title: "Solutions", description: "Practical consulting and implementation for research administration teams: assessment, process design, financial oversight, SOPs, implementation and AI readiness." };
export default function Solutions() {
  return (
    <>
      <PageHero eyebrow="Solutions" title="Practical consulting and implementation." text="Right-sized help for small research administration teams, from understanding where you are today to putting simpler operations in place.">
        <Button href="/book-discovery-call" event="consultation_cta_clicked">Book a Discovery Call</Button>
      </PageHero>
      <Section tone="white">
        <div className="ruled">{services.map((s) => (
          <div key={s.slug} id={s.slug} className="item item--cols">
            <div><div className="num">{s.n}</div><h3 style={{ fontSize: 24, margin: "6px 0 10px" }}>{s.t}</h3><p style={{ fontSize: 17 }}>{s.d}</p></div>
            <ul className="checks">{s.items.map((i) => <li key={i}>{i}</li>)}</ul>
          </div>))}</div>
      </Section>
      <Section tone="soft">
        <SectionHeading eyebrow="How we work" title="Start with a conversation." text="Most engagements begin with a discovery call to understand your portfolio, team and systems. Scope and fees are agreed before work begins. Pricing is set per engagement." />
        <Button href="/book-discovery-call" event="consultation_cta_clicked">Book a Discovery Call</Button>
      </Section>
      <FinalCTA />
    </>
  );
}
