import Link from "next/link";
import type { Service } from "@/lib/content";
import CTAButton from "./CTAButton";
export default function ServiceCard({ s }: { s: Service }) {
  return (
    <article className="gcard" id={s.slug}>
      <h3 style={{ marginTop: 0 }}>{s.title}</h3>
      <div className="price">{s.price} <small>indicative</small></div>
      <p style={{ marginTop: 8 }}>{s.purpose}</p>
      <ul>{s.deliverables.map((d) => <li key={d}>{d}</li>)}</ul>
      <div className="cta-row" style={{ marginTop: "auto" }}>
        <CTAButton href={`/book-consultation?interest=${encodeURIComponent(s.title)}`} event="consultation_cta_clicked">{s.cta}</CTAButton>
        <Link href={`/solutions/${s.slug}`} style={{ alignSelf: "center", fontWeight: 600 }}>Details →</Link>
      </div>
    </article>
  );
}
