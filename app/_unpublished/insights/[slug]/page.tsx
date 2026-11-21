import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { articles } from "@/lib/content";
import Section from "@/components/ui/Section";
import FinalCTA from "@/components/sections/FinalCTA";
export const dynamicParams = false;
export const generateStaticParams = () => articles.map((a) => ({ slug: a.slug }));
export function generateMetadata({ params }: { params: { slug: string } }): Metadata {
  const a = articles.find((x) => x.slug === params.slug);
  return { title: a?.title, description: a?.summary, openGraph: { title: a?.title, description: a?.summary, type: "article" } };
}
export default function Article({ params }: { params: { slug: string } }) {
  const a = articles.find((x) => x.slug === params.slug);
  if (!a) notFound();
  return (
    <>
      <section className="page-hero"><div className="container"><nav aria-label="Breadcrumb" style={{ fontSize: 14, marginBottom: 18 }}><Link href="/insights">Insights</Link></nav><div className="eyebrow">{a.category}</div><h1>{a.title}</h1><p className="lead">{a.summary}</p></div></section>
      <Section tone="white"><article className="article">
        {a.body.map((b, i) => (<div key={i}>{b.h && <h2>{b.h}</h2>}{b.p && <p>{b.p}</p>}{b.ul && <ul>{b.ul.map((x) => <li key={x}>{x}</li>)}</ul>}</div>))}
        <p className="note">General guidance for orientation only. Always follow your sponsor terms and institutional policies.</p>
      </article></Section>
      <FinalCTA />
    </>
  );
}
