import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { services } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
import CTAButton from "@/components/common/CTAButton";
import FinalCTA from "@/components/common/FinalCTA";

export const dynamicParams = false;
export const generateStaticParams = () => services.map((s) => ({ slug: s.slug }));
export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const s = services.find((x) => x.slug === params.slug);
  return { title: s?.title, description: s?.purpose };
}
export default function ServicePage({ params }: { params: { slug: string } }) {
  const s = services.find((x) => x.slug === params.slug);
  if (!s) notFound();
  return (
    <>
      <PageHero eyebrow="Solution" title={s.title} text={s.purpose}>
        <CTAButton href={`/book-consultation?interest=${encodeURIComponent(s.title)}`} event="consultation_cta_clicked">{s.cta}</CTAButton>
        <CTAButton href="/solutions" tone="secondary">All solutions</CTAButton>
      </PageHero>
      <section className="section">
        <div className="container card-grid grid-2">
          <div className="gcard"><h3 style={{ marginTop: 0 }}>Deliverables</h3><ul>{s.deliverables.map((d) => <li key={d}>{d}</li>)}</ul></div>
          <div className="gcard"><h3 style={{ marginTop: 0 }}>Who it’s for</h3><p>{s.audience}</p><div className="price">{s.price} <small>indicative price</small></div><p style={{ fontSize: 14 }}>Pricing is indicative and confirmed after a short scoping conversation.</p></div>
        </div>
      </section>
      <FinalCTA />
    </>
  );
}
