import CTAButton from "../common/CTAButton";

const rows = [
  { n: "Foundation award A", pct: 72, warn: false, v: "72%" },
  { n: "State program B", pct: 91, warn: true, v: "91%" },
  { n: "Federal pass-through C", pct: 38, warn: false, v: "38%" },
];

export default function Hero() {
  return (
    <section className="hero">
      <div className="container hero-grid">
        <div>
          <h1>Better Grant Management Starts with Better Systems.</h1>
          <p className="lead">
            Winning a grant is only the beginning. Forge helps nonprofits build the systems, financial controls, compliance workflows, and technology needed to manage grant-funded programs effectively.
          </p>
          <div className="cta-row">
            <CTAButton href="/book-consultation" event="consultation_cta_clicked">Book a Consultation</CTAButton>
            <CTAButton href="/solutions" tone="ghost-light">Explore Our Solutions</CTAButton>
          </div>
        </div>
        <div className="dash" role="img" aria-label="Illustrative grant portfolio dashboard showing budget spent by award">
          <div className="dash-top">Grant portfolio <span className="pill">Sample data</span></div>
          <div className="dash-stats">
            <div className="dash-stat"><b>6</b><span>Active awards</span></div>
            <div className="dash-stat"><b>4</b><span>Reports due</span></div>
            <div className="dash-stat"><b>2</b><span>Flags</span></div>
          </div>
          {rows.map((r) => (
            <div className="dash-row" key={r.n}>
              <span>{r.n}</span>
              <div className={`bar ${r.warn ? "warn" : ""}`}><i style={{ width: `${r.pct}%` }} /></div>
              <b>{r.v}</b>
            </div>
          ))}
          <div className="dash-note">Illustrative sample — not client data.</div>
        </div>
      </div>
    </section>
  );
}
