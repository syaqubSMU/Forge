import type { Metadata } from "next";
import Link from "next/link";
import { articles, articleCategories } from "@/lib/content";
import Section, { PageHero } from "@/components/ui/Section";
import FinalCTA from "@/components/sections/FinalCTA";
export const metadata: Metadata = { title: "Insights", description: "Practical guides on research administration, grants management, research finance and AI in research administration." };
export default function Insights() {
  return (
    <>
      <PageHero eyebrow="Insights" title="Practical thinking for research administration." text="Short, practical guides for small research administration teams. We publish only what we can stand behind." />
      <Section tone="white">
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 36 }} aria-label="Topics">{articleCategories.map((c) => <span key={c} className="badge badge--blue">{c}</span>)}</div>
        <div className="grid g3">{articles.map((a) => (
          <Link key={a.slug} href={`/insights/${a.slug}`} className="panel panel--link"><span className="num">{a.category}</span><h3 style={{ margin: 0 }}>{a.title}</h3><p style={{ flex: 1 }}>{a.summary}</p><span className="link-arrow">Read guide <span aria-hidden="true">→</span></span></Link>))}</div>
        <p className="note" style={{ marginTop: 36 }}><b>Federal funding developments:</b> we will publish sourced updates here when we can link to primary sources. Nothing is posted until it is verified.</p>
      </Section>
      <FinalCTA title="Want this applied to your team?" text="A discovery call is the fastest way to turn good practice into your own routine." />
    </>
  );
}
