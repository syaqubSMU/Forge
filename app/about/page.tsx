import type { Metadata } from "next";
import Section, { PageHero, SectionHeading } from "@/components/ui/Section";
import FinalCTA from "@/components/sections/FinalCTA";
import { whyForge } from "@/lib/content";
export const metadata: Metadata = { title: "About", description: "FORGE's mission and operating philosophy: simpler, connected research operations for small research administration teams." };
export default function About() {
  return (
    <>
      <PageHero eyebrow="About FORGE" title="Simpler research operations for the teams who run them." />
      <Section tone="white">
        <div className="split" style={{ alignItems: "start" }}>
          <SectionHeading eyebrow="Mission" title="Make research administration simpler." />
          <div className="stack"><p className="lead">Research administration teams are often small, yet responsible for complex portfolios. They deserve tools that are as capable as the work is demanding, and simple enough to manage without an IT department.</p>
            <p className="lead">FORGE combines a connected workspace, practical consulting, ready-to-use tools and responsible automation to give those teams better visibility and less repetitive work.</p></div>
        </div>
      </Section>
      <Section tone="soft">
        <SectionHeading eyebrow="Operating philosophy" title="How we approach the work." />
        <div className="grid g4">{whyForge.map((w) => (<div key={w.t}><h3 style={{ fontSize: 18, marginBottom: 8 }}>{w.t}</h3><p style={{ color: "var(--muted)" }}>{w.d}</p></div>))}</div>
      </Section>
      <Section tone="white">
        <div className="grid g2">
          <div className="panel"><span className="badge badge--ok">FORGE is</span><ul className="checks"><li>Lightweight and practical</li><li>Designed for small teams</li><li>Integration-oriented</li><li>Specific to research administration</li><li>Automation-enabled, with human review</li></ul></div>
          <div className="panel"><span className="badge badge--coral">FORGE is not</span><ul className="checks"><li>An institutional ERP</li><li>A replacement for official university financial or research administration systems</li><li>A heavy platform requiring a large IT team</li><li>A generic grant-writing consultancy</li></ul></div>
        </div>
      </Section>
      <Section tone="warm">
        <SectionHeading eyebrow="Founder" title="Practical research administration experience." />
        <p className="note">The founder profile and background will be added here once finalized. FORGE does not publish credentials, endorsements or case studies that have not been verified and approved.</p>
      </Section>
      <FinalCTA />
    </>
  );
}
