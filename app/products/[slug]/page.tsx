import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { products, site } from "@/lib/content";
import Section from "@/components/ui/Section";
import Button from "@/components/ui/Button";
import FAQ from "@/components/ui/FAQ";
import ProductVisual from "@/components/ui/ProductVisual";
import ChatlingInline from "@/components/chatbot/ChatlingInline";
import RequestSection from "@/components/sections/RequestSection";

export const dynamicParams = false;
export const generateStaticParams = () => products.map((p) => ({ slug: p.slug }));
export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const p = products.find((x) => x.slug === params.slug);
  return { title: p?.title, description: p?.blurb, openGraph: { title: p?.title, description: p?.blurb } };
}
export default function ProductPage({ params }: { params: { slug: string } }) {
  const p = products.find((x) => x.slug === params.slug);
  if (!p) notFound();
  const isCalc = p.slug === "travel-budget-calculator";
  return (
    <>
      <section className="page-hero"><div className="container">
        <nav aria-label="Breadcrumb" style={{ fontSize: 14, marginBottom: 18 }}><Link href="/products">Products</Link> <span aria-hidden="true">/</span> {p.title}</nav>
        <div className="split split--prod" style={{ alignItems: "center" }}>
          <div>
            <div className="eyebrow">{p.category}</div><h1>{p.title}</h1><p className="lead">{p.description}</p>
            <div style={{ display: "flex", gap: 14, alignItems: "baseline", marginTop: 20 }}><b style={{ fontFamily: "var(--f-head)", fontSize: 30, color: "var(--blue)" }}>{p.price}</b>{!isCalc && <span style={{ color: "var(--muted)", fontSize: 14 }}>indicative price</span>}</div>
            {!isCalc && <div className="btn-row"><Button href="#request" size="lg">Request a Demo</Button></div>}
            {!isCalc && <p className="note" style={{ marginTop: 18 }}>Online checkout is not available yet. Use the demo request form below.</p>}
          </div>
          <ProductVisual kind={p.visual} label={p.title} />
        </div>
      </div></section>
      {isCalc && (
        <Section tone="white">
          <div style={{ maxWidth: 820, margin: "0 auto" }}>
            <h2 style={{ fontSize: 28, marginBottom: 16 }}>Use the calculator</h2>
            <ChatlingInline botId={site.travelCalculatorBotId} />
            <p className="note" style={{ marginTop: 16 }}>Results are planning estimates. Always confirm allowable costs against sponsor terms, award conditions and your institution&apos;s travel policy. This tool does not provide legal, accounting or compliance advice. Please do not enter confidential or sensitive information.</p>
          </div>
        </Section>
      )}
      <Section tone="soft">
        <div className="grid g2">
          <div className="panel"><h3>What&apos;s included</h3><ul className="checks">{p.includes.map((i) => <li key={i}>{i}</li>)}</ul></div>
          <div className="panel"><h3>Who it&apos;s for</h3><p>{p.audience}</p></div>
        </div>
        <h2 style={{ fontSize: 26, margin: "48px 0 16px" }}>Frequently asked questions</h2>
        <div style={{ maxWidth: 820 }}><FAQ items={p.faqs} /></div>
      </Section>
      {!isCalc && <RequestSection product={p.title} />}
    </>
  );
}
