import { problems } from "@/lib/content";
import SectionHeading from "../common/SectionHeading";
const dots = ["coral", "tang", "blue", "coral"];
export default function ProblemSection() {
  return (
    <section className="section">
      <div className="container">
        <SectionHeading eyebrow="The problem" title="Winning Grants Is Only the Beginning."
          text="Managing multiple grants can quickly become complicated. Deadlines, budgets, reporting requirements, award conditions, and documentation often end up scattered across spreadsheets, email, and disconnected systems. As organizations grow, these manual processes become increasingly difficult to manage." />
        <div className="card-grid grid-4">
          {problems.map((p, i) => (
            <div className="gcard" key={p.title}><span className={`dot ${dots[i]}`} aria-hidden /><h3>{p.title}</h3><p>{p.text}</p></div>
          ))}
        </div>
      </div>
    </section>
  );
}
