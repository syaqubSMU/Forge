import { steps } from "@/lib/content";
import SectionHeading from "../common/SectionHeading";
/** Horizontal on desktop, vertical timeline on mobile (see .process in globals.css). */
export default function ProcessSteps() {
  return (
    <section className="section">
      <div className="container">
        <SectionHeading eyebrow="How Forge works" title="Five steps from scattered to structured." />
        <ol className="process">
          {steps.map((s) => (<li key={s.title}><h3>{s.title}</h3><p>{s.text}</p></li>))}
        </ol>
      </div>
    </section>
  );
}
