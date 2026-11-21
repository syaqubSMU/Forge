import type { Metadata } from "next";
import { aiItems, governance } from "@/lib/content";
import Section, { PageHero, SectionHeading } from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import AwardWorkflow from "@/components/sections/AwardWorkflow";
import RequestSection from "@/components/sections/RequestSection";
export const metadata: Metadata = { title: "AI & Automation", description: "Practical, human-reviewed AI for research administration: award document intelligence, extraction, funding discovery, budget intelligence, compliance reminders and reporting assistance." };
export default function AI() {
  return (
    <>
      <PageHero eyebrow="AI & Automation" title="Intelligent help for research administration." text="FORGE applies AI to the routine work of research administration, with people reviewing every result. These capabilities are in development.">
        <Button href="#request">Request a Demo</Button>
      </PageHero>
      <Section tone="white">
        <SectionHeading eyebrow="Featured" title="Award document intelligence" text="Award agreements hold the terms that drive everything else. FORGE is designed to read an agreement and prepare a structured record, with each value tied to its source page and uncertain items flagged for a person to confirm." />
        <AwardWorkflow />
      </Section>
      <Section tone="soft">
        <SectionHeading eyebrow="Capabilities" title="Where automation can help." />
        <div className="grid g3">{aiItems.map((a, i) => (<div className="panel" key={a.t}><span className="num">0{i + 1}</span><h3 style={{ margin: "8px 0" }}>{a.t}</h3><p>{a.d}</p><span className="badge" style={{ marginTop: 12 }}>In development</span></div>))}</div>
      </Section>
      <Section tone="white">
        <SectionHeading eyebrow="Trust and governance" title="Automation supports people. It doesn't replace judgment." />
        <ul className="checks" style={{ maxWidth: 780, fontSize: 17, gap: 12 }}>{governance.map((g) => <li key={g}>{g}</li>)}</ul>
      </Section>
      <RequestSection product="our AI & automation capabilities" />
    </>
  );
}
