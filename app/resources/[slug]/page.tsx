import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { resources } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
import ChatlingInline from "@/components/chatbot/ChatlingInline";
import { site } from "@/lib/content";
import ResourceGate from "@/components/forms/ResourceGate";
import FormShell from "@/components/forms/FormShell";
export const dynamicParams = false;
export const generateStaticParams = () => resources.map((r) => ({ slug: r.slug }));
export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const r = resources.find((x) => x.slug === params.slug);
  return { title: r?.title, description: r?.summary };
}
export default function ResourcePage({ params }: { params: { slug: string } }) {
  const r = resources.find((x) => x.slug === params.slug);
  if (!r) notFound();
  if (r.slug === "travel-calculator") {
    return (
      <>
        <PageHero eyebrow={`Free resource · ${r.category}`} title={r.title} text="A free interactive tool from Forge. Use it below — no sign-up required." />
        <section className="section">
          <div className="container" style={{ maxWidth: 820 }}>
            <ChatlingInline botId={site.travelCalculatorBotId} />
            <div className="note-box" style={{ marginTop: 16 }}>
              Results are estimates to support planning. Always confirm travel costs and allowable expenses against your award terms, funder guidance and your organization’s travel policy. This tool does not provide legal, accounting or compliance advice. Please don’t enter confidential or sensitive information.
            </div>
          </div>
        </section>
      </>
    );
  }
  return (
    <>
      <PageHero eyebrow={r.category} title={r.title} text={r.summary} />
      <section className="section"><div className="container"><FormShell><ResourceGate slug={r.slug} /></FormShell></div></section>
    </>
  );
}
