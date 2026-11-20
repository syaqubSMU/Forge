import type { Metadata } from "next";
import { services, pillars } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
import ServiceCard from "@/components/common/ServiceCard";
import SectionHeading from "@/components/common/SectionHeading";
import FinalCTA from "@/components/common/FinalCTA";
import CTAButton from "@/components/common/CTAButton";
export const metadata: Metadata = { title: "Solutions", description: "Fixed-price grant operations diagnostics and implementation packages for nonprofits." };
export default function Solutions() {
  return (
    <>
      <PageHero eyebrow="Solutions" title="Professional grant operations services." text="From a diagnostic to a full implementation, choose the level of support that fits your organization's capacity.">
        <CTAButton href="/book-consultation" event="consultation_cta_clicked">Book a Consultation</CTAButton>
      </PageHero>
      <section className="section">
        <div className="container">
          <div className="card-grid grid-2">{services.map((s) => <ServiceCard key={s.slug} s={s} />)}</div>
          <p style={{ marginTop: 20, color: "var(--muted)", fontSize: 14 }}>Prices are indicative and may vary with scope.</p>
        </div>
      </section>
      <section className="section section--white">
        <div className="container">
          <SectionHeading title="What every engagement can draw on" />
          <div className="card-grid grid-4">{pillars.map((p) => <div className="gcard" key={p.slug}><h3>{p.title}</h3><p>{p.summary}</p></div>)}</div>
        </div>
      </section>
      <FinalCTA />
    </>
  );
}
