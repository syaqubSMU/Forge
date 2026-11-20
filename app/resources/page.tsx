import type { Metadata } from "next";
import Link from "next/link";
import { resources, resourceCategories } from "@/lib/content";
import PageHero from "@/components/common/PageHero";
import FinalCTA from "@/components/common/FinalCTA";
export const metadata: Metadata = { title: "Resources", description: "Free grant operations checklists, templates and guides." };
export default function Resources() {
  return (
    <>
      <PageHero eyebrow="Resources" title="Practical resources for grant-funded teams." text="Checklists, templates and guides. Articles and webinars will be added over time." />
      <section className="section">
        <div className="container">
          {resourceCategories.filter((c) => resources.some((r) => r.category === c)).map((c) => (
            <div key={c} style={{ marginBottom: 36 }}>
              <h2 style={{ fontSize: 22, marginBottom: 16 }}>{c}</h2>
              <div className="card-grid grid-3">
                {resources.filter((r) => r.category === c).map((r) => (
                  <article className="gcard" key={r.slug}><h3 style={{ marginTop: 0 }}>{r.title}</h3><p>{r.summary}</p><Link className="more" href={`/resources/${r.slug}`}>View resource →</Link></article>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
      <FinalCTA />
    </>
  );
}
