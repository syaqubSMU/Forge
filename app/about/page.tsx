import type { Metadata } from "next";
import PageHero from "@/components/common/PageHero";
import FinalCTA from "@/components/common/FinalCTA";
import { whyGos } from "@/lib/content";
export const metadata: Metadata = { title: "About", description: "Our mission and approach to grant operations." };
export default function About() {
  return (
    <>
      <PageHero eyebrow="About Forge" title="Operational infrastructure for grant-funded organizations." />
      <section className="section">
        <div className="container" style={{ maxWidth: 800 }}>
          <p className="lead">Forge was established to help grant-funded organizations build the operational infrastructure needed to manage funding effectively.</p>
          <p className="lead" style={{ marginTop: 16 }}>We believe that strong grant management requires more than tracking deadlines and preparing reports. It requires integrated systems, financial visibility, clear processes, reliable documentation, and informed decision-making.</p>
          <p className="lead" style={{ marginTop: 16 }}>Forge combines practical grant operations expertise with modern technology and responsible AI-enabled automation.</p>
        </div>
      </section>
      <section className="section section--white">
        <div className="container"><div className="card-grid grid-4">{whyGos.map((w) => <div className="gcard" key={w.title}><h3 style={{ marginTop: 0 }}>{w.title}</h3><p>{w.text}</p></div>)}</div></div>
      </section>
      <FinalCTA />
    </>
  );
}
