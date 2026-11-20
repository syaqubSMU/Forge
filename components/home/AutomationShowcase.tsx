import { automations, budgetMonitor } from "@/lib/content";
import SectionHeading from "../common/SectionHeading";
import CTAButton from "../common/CTAButton";
export default function AutomationShowcase() {
  const items = [...automations.slice(0, 3), budgetMonitor as { title: string; summary: string; slug?: string }, automations[3]];
  return (
    <section className="section">
      <div className="container">
        <SectionHeading eyebrow="Forge Automation Lab" title="Make Grant Administration More Intelligent."
          text="Automation supports administrative work. Human review remains essential for financial, contractual, and compliance decisions." />
        <div className="card-grid grid-3">
          {items.map((a) => (<article className="gcard" key={a.title}><h3>{a.title}</h3><p>{a.summary}</p></article>))}
        </div>
        <div style={{ marginTop: 28 }}><CTAButton href="/ai-automation" tone="secondary">Explore AI & Automation</CTAButton></div>
      </div>
    </section>
  );
}
