import { whyGos } from "@/lib/content";
import SectionHeading from "../common/SectionHeading";
export default function WhyGos() {
  return (
    <section className="section section--white">
      <div className="container">
        <SectionHeading eyebrow="Why Forge" title="Built for the way small teams actually work." />
        <div className="card-grid grid-4">
          {whyGos.map((w) => (<div className="gcard" key={w.title}><h3>{w.title}</h3><p>{w.text}</p></div>))}
        </div>
      </div>
    </section>
  );
}
