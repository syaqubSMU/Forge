import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { resources } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
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
  return (
    <>
      <PageHero eyebrow={r.category} title={r.title} text={r.summary} />
      <section className="section"><div className="container"><FormShell><ResourceGate slug={r.slug} /></FormShell></div></section>
    </>
  );
}
