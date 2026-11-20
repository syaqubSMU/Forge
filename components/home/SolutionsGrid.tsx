import Link from "next/link";
import { pillars } from "@/lib/content";
import SectionHeading from "../common/SectionHeading";
export default function SolutionsGrid() {
  return (
    <section className="section section--white">
      <div className="container">
        <SectionHeading eyebrow="Our solutions" title="A Complete Approach to Grant Operations." />
        <div className="card-grid grid-4">
          {pillars.map((p) => (
            <article className="gcard" key={p.slug}>
              <h3>{p.title}</h3><p>{p.summary}</p>
              <ul>{p.includes.map((i) => <li key={i}>{i}</li>)}</ul>
              <Link className="more" href={p.href} aria-label={`Learn more about ${p.title}`}>Learn more →</Link>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
